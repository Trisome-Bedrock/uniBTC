import pytest
from web3 import Web3
from pathlib import Path
from brownie import FBTC, WBTC, WBTC18, XBTC, Vault, uniBTC, Peer, MessageBus, accounts, Contract, project, config, network

# Web3 client
@pytest.fixture(scope="session", autouse=True)
def w3():
    return Web3(Web3.HTTPProvider('http://localhost:8545'))

# Roles
@pytest.fixture(scope="session", autouse=True)
def roles(w3):
    pauser_role = w3.keccak(text='PAUSER_ROLE')  # index = 0
    minter_role = w3.keccak(text='MINTER_ROLE')  # index = 1
    manager_role = w3.keccak(text='MANAGER_ROLE')  # index = 2
    default_admin_role = w3.toBytes(hexstr="0x00")  # index = 5
    return [pauser_role, minter_role, manager_role, default_admin_role]

# Predefined Accounts
@pytest.fixture(scope="session", autouse=True)
def owner():
    return accounts[0]

@pytest.fixture(scope="session", autouse=True)
def deployer():
    return accounts[1]

@pytest.fixture(scope="session", autouse=True)
def alice():
    return accounts[2]

@pytest.fixture(scope="session", autouse=True)
def bob():
    return accounts[3]

@pytest.fixture(scope="session", autouse=True)
def executor():
    return accounts[3]

@pytest.fixture(scope="session", autouse=True)
def zero_address():
    return accounts.at("0x0000000000000000000000000000000000000000", True)

@pytest.fixture(scope="session", autouse=True)
def chain_id(w3):
    return w3.eth.chain_id

@pytest.fixture(scope="session", autouse=True)
def proxy():
    # Reference: https://docs.openzeppelin.com/contracts/4.x/api/proxy#TransparentUpgradeableProxy
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    return deps.TransparentUpgradeableProxy

# Contracts
@pytest.fixture()
def contracts(w3, proxy, chain_id, roles, owner, deployer):
    # Deploy contracts
    message_bus_sender = MessageBus.deploy({'from': owner})
    message_bus_receiver = MessageBus.deploy({'from': owner})
    fbtc = FBTC.deploy({'from': owner})
    wbtc = WBTC.deploy({'from': owner})
    wbtc18 = WBTC18.deploy({'from': owner})
    xbtc = XBTC.deploy({'from': owner})

    uni_btc = uniBTC.deploy({'from': deployer})
    uni_btc_proxy = proxy.deploy(uni_btc, deployer, b'', {'from': deployer})
    uni_btc_transparent = Contract.from_abi("uniBTC", uni_btc_proxy.address, uniBTC.abi)

    vault_eth = Vault.deploy({'from': deployer})
    vault_eth_proxy = proxy.deploy(vault_eth, deployer, b'', {'from': deployer})
    vault_eth_transparent = Contract.from_abi("Vault", vault_eth_proxy.address, Vault.abi)

    vault_btc = Vault.deploy({'from': deployer})
    vault_btc_proxy = proxy.deploy(vault_btc, deployer, b'', {'from': deployer})
    vault_btc_transparent = Contract.from_abi("Vault", vault_btc_proxy.address, Vault.abi)

    peer_sender = Peer.deploy(message_bus_sender, uni_btc_transparent, {'from': owner})
    peer_receiver = Peer.deploy(message_bus_receiver, uni_btc_transparent, {'from': owner})
    peers = [peer_sender, peer_receiver]

    vaults = [vault_eth_transparent, vault_btc_transparent]

    # Configure contracts
    uni_btc_transparent.initialize(owner, owner, {'from': owner})
    for peer in peers:
        uni_btc_transparent.grantRole(roles[1], peer, {'from': owner})
        peer.configurePeers([chain_id, chain_id + 1], [peer_sender, peer_receiver], {'from': owner})

    vault_eth_transparent.initialize(owner, uni_btc_transparent, False, {'from': owner})
    vault_btc_transparent.initialize(owner, uni_btc_transparent, True, {'from': owner})
    for vault in vaults:
        uni_btc_transparent.grantRole(roles[1], vault, {'from': owner})

    return [uni_btc_transparent,
            peer_sender,
            peer_receiver,
            message_bus_sender,
            message_bus_receiver,
            wbtc,
            vault_eth_transparent,
            fbtc,
            xbtc,
            vault_btc_transparent,
            wbtc18]
