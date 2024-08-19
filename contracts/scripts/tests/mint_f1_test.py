from brownie import interface, FBTCProxy, LockedFBTC, uniBTC, Vault, accounts, project, config, Contract
from pathlib import Path

# Execution Command Format:
# `brownie run scripts/tests/mint_f1_test.py main "fbtc_proxy_owner" ethereum" --network=mainnet-public -I`

contracts = {
    "ethereum": {
        "uni_btc": "0x004E9C3EF86bc1ca1f0bB5C7662861Ee93350568",          # https://etherscan.io/address/0x004E9C3EF86bc1ca1f0bB5C7662861Ee93350568
        "vault": "0x047D41F2544B7F63A8e991aF2068a363d210d6Da",            # https://etherscan.io/address/0x047D41F2544B7F63A8e991aF2068a363d210d6Da
        "fbtc_proxy": "0x56c3024eB229Ca0570479644c78Af9D53472B3e4",       # https://etherscan.io/address/0x56c3024eB229Ca0570479644c78Af9D53472B3e4
        "locked_fbtc": "0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c",      # https://etherscan.io/address/0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c
        "fbtc": "0xC96dE26018A54D51c097160568752c4E3BD6C364",             # https://etherscan.io/address/0xC96dE26018A54D51c097160568752c4E3BD6C364
    },
    "mantle": {
        "uni_btc": "0x93919784C523f39CACaa98Ee0a9d96c3F32b593e",          # https://explorer.mantle.xyz/address/0x93919784C523f39CACaa98Ee0a9d96c3F32b593e
        "vault": "0xF9775085d726E782E83585033B58606f7731AB18",            # https://explorer.mantle.xyz/address/0xF9775085d726E782E83585033B58606f7731AB18
        "fbtc_proxy": "0x56c3024eB229Ca0570479644c78Af9D53472B3e4",       # https://explorer.mantle.xyz/address/0x56c3024eB229Ca0570479644c78Af9D53472B3e4
        "locked_fbtc": "0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c",      # https://explorer.mantle.xyz/address/0xd681C5574b7F4E387B608ed9AF5F5Fc88662b37c
        "fbtc": "0xC96dE26018A54D51c097160568752c4E3BD6C364",             # https://explorer.mantle.xyz/address/0xC96dE26018A54D51c097160568752c4E3BD6C364
    },
}

def main(fbtc_proxy_owner="fbtc_proxy_owner", network="ethereum"):
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])

    # Load accounts
    owner_zealy = accounts.load(fbtc_proxy_owner)

    # Build objects
    uni_btc = uniBTC.at(contracts[network]['uni_btc'])
    vault = Vault.at(contracts[network]['vault'])
    fbtc_proxy = FBTCProxy.at(contracts[network]['fbtc_proxy'])
    locked_fbtc = interface.ILockedFBTC(contracts[network]['locked_fbtc'])
    fbtc = deps.ERC20.at(contracts[network]['fbtc'])

    # Test minting LockedFBTC
    fbtc_bal_before = fbtc.balanceOf(vault)

    amt = 0.0001 * 1e8

    tx = fbtc_proxy.mintLockedFbtcRequest(amt, {'from': owner_zealy})
    assert tx.status == 1
    assert len(tx.events) > 0
    assert 'MintLockedFbtcRequest' in tx.events

    receive_amount = tx.events['MintLockedFbtcRequest']['receivedAmount']
    fee = tx.events['MintLockedFbtcRequest']['fee']
    assert receive_amount > 0
    assert locked_fbtc.balanceOf(vault) == receive_amount
    assert fbtc.balanceOf(vault) == fbtc_bal_before - amt

    print("Network: ", network)
    print(" Burned FBTC amount: ", amt)
    print(" Minted LockedFBTC amount: ", receive_amount)
    print(" Fee: ", fee)


