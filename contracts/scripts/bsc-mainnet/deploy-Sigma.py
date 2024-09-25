from brownie import Sigma, accounts, Contract, project, config
from pathlib import Path
from web3 import Web3


# Execution Command Format:
# `brownie run scripts/bsc-mainnet/deploy-Sigma.py main "uniBTCMainnetDeployer" "uniBTCMainnetAdmin" --network=bsc-main -I`


def main(deployer="deployer", owner="owner"):
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    default_admin_role = w3.to_bytes(hexstr="0x00")

    deployer = accounts.load(deployer)
    owner = accounts.load(owner)

    # Deployed core contracts
    proxy_admin = "0xb3f925B430C60bA467F7729975D5151c8DE26698"
    vault = "0x84E5C854A7fF9F49c888d69DECa578D406C26800"

    # Deploy and initialize Sigma
    sigma_impl = Sigma.deploy({'from': deployer})
    initialize_data = sigma_impl.initialize.encode_input(owner)
    sigma_proxy = TransparentUpgradeableProxy.deploy(sigma_impl, proxy_admin, initialize_data, {'from': deployer})

    # Check initial status
    sigma_transparent = Contract.from_abi("Sigma", sigma_proxy, Sigma.abi)
    assert sigma_transparent.hasRole(default_admin_role, owner)

    print("Deployed Sigma proxy address: ", sigma_proxy)  # 0x8Cc6D6135C7088fdb3eBFB39B11e7CB2F9853915
    print("")
    print("Deployed Sigma implementation address: ", sigma_impl)  # 0x1F6C2e81F09174D076aA19AFd7C9c67D0e257B5a


    # --------- Set holders of FBTC, which have 8 decimals. ---------
    fbtc = "0xC96dE26018A54D51c097160568752c4E3BD6C364"
    fbtc_pools = [
        (fbtc, (vault,))
    ]
    tx = sigma_transparent.setTokenHolders(fbtc, fbtc_pools, {'from': owner})
    assert "TokenHoldersSet" in tx.events
    assert sigma_transparent.getTokenHolders(fbtc) == fbtc_pools
    assert len(sigma_transparent.ListLeadingTokens()) == 1

    # Check supply of FBTC
    FBTC = deps.ERC20.at(fbtc)
    assert sigma_transparent.totalSupply(fbtc) == FBTC.balanceOf(vault)

    # ---------- Set holders of BTCB, which have 18 decimals. ---------
    btcb = "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"
    btcb_pools = [
        (btcb, (vault,))
    ]
    tx = sigma_transparent.setTokenHolders(btcb, btcb_pools, {'from': owner})
    assert "TokenHoldersSet" in tx.events
    assert sigma_transparent.getTokenHolders(btcb) == btcb_pools
    assert len(sigma_transparent.ListLeadingTokens()) == 2

    # Check supply of BTCB
    BTCB = deps.ERC20.at(btcb)
    assert sigma_transparent.totalSupply(btcb) == BTCB.balanceOf(vault)




