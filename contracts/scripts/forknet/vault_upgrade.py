from brownie import interface, FBTCProxy, LockedFBTC, uniBTC, Vault, accounts, project, config, Contract
from pathlib import Path

# Execution Command Format:
# `brownie run scripts/forknet/vault_upgrade.py main "ethereum" --network=mainnet-public-fork`

contracts = {
    "ethereum": {
        "proxy_admin": "0x029E4FbDAa31DE075dD74B2238222A08233978f6",      # https://etherscan.io/address/0x029E4FbDAa31DE075dD74B2238222A08233978f6
        "uni_btc": "0x004E9C3EF86bc1ca1f0bB5C7662861Ee93350568",          # https://etherscan.io/address/0x004E9C3EF86bc1ca1f0bB5C7662861Ee93350568
        "vault": "0x047D41F2544B7F63A8e991aF2068a363d210d6Da",            # https://etherscan.io/address/0x047D41F2544B7F63A8e991aF2068a363d210d6Da
        "fbtc_proxy": "0x56c3024eB229Ca0570479644c78Af9D53472B3e4",       # https://etherscan.io/address/0x56c3024eB229Ca0570479644c78Af9D53472B3e4
        "locked_fbtc": "0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c",      # https://etherscan.io/address/0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c
        "fbtc": "0xC96dE26018A54D51c097160568752c4E3BD6C364",             # https://etherscan.io/address/0xC96dE26018A54D51c097160568752c4E3BD6C364
    },
    "mantle": {
        "proxy_admin": "0x0A3f2582FF649Fcaf67D03483a8ED1A82745Ea19",      # https://explorer.mantle.xyz/address/0x0A3f2582FF649Fcaf67D03483a8ED1A82745Ea19
        "uni_btc": "0x93919784C523f39CACaa98Ee0a9d96c3F32b593e",          # https://explorer.mantle.xyz/address/0x93919784C523f39CACaa98Ee0a9d96c3F32b593e
        "vault": "0xF9775085d726E782E83585033B58606f7731AB18",            # https://explorer.mantle.xyz/address/0xF9775085d726E782E83585033B58606f7731AB18
        "fbtc_proxy": "0x56c3024eB229Ca0570479644c78Af9D53472B3e4",       # https://explorer.mantle.xyz/address/0x56c3024eB229Ca0570479644c78Af9D53472B3e4
        "locked_fbtc": "0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c",      # https://explorer.mantle.xyz/address/0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c
        "fbtc": "0xC96dE26018A54D51c097160568752c4E3BD6C364",             # https://explorer.mantle.xyz/address/0xC96dE26018A54D51c097160568752c4E3BD6C364
    },
}

def main(network="ethereum"):
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy
    ProxyAdmin = deps.ProxyAdmin

    # Load accounts
    owner = accounts.at('0x9251fd3D79522bB2243a58FFf1dB43E25A495aaB', True)
    owner_zealy = accounts.at('0xbFdDf5e269C74157b157c7DaC5E416d44afB790d', True)
    deployer = accounts.at('0x899c284A89E113056a72dC9ade5b60E80DD3c94f', True)
    multisig = accounts.at('0xC9dA980fFABbE2bbe15d4734FDae5761B86b5Fc3', True)

    # Upgrade Vault
    proxyAdmin = ProxyAdmin.at(contracts[network]['proxy_admin'])

    vault_impl = Vault.deploy({'from': deployer})
    vault_proxy = TransparentUpgradeableProxy.at(contracts[network]['vault'])
    proxyAdmin.upgrade(vault_proxy, vault_impl.address, {'from': multisig})

    # Build objects
    uni_btc = uniBTC.at(contracts[network]['uni_btc'])
    vault = Contract.from_abi("Vault",vault_proxy.address, Vault.abi)
    fbtc_proxy = FBTCProxy.at(contracts[network]['fbtc_proxy'])
    locked_fbtc = interface.ILockedFBTC(contracts[network]['locked_fbtc'])
    fbtc = deps.ERC20.at(contracts[network]['fbtc'])

    # Grant OperatorRole to FBTCProxy
    vault.grantRole(vault.OPERATOR_ROLE(), fbtc_proxy, {'from': owner})
    assert vault.hasRole(vault.OPERATOR_ROLE(), fbtc_proxy)



