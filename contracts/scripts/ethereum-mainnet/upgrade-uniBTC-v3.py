from brownie import uniBTC, accounts, Contract, project, config
from pathlib import Path

# Execution Command Format:
# `brownie run scripts/ethereum-mainnet/upgrade-uniBTC-v3.py main "uniBTCMainnetDeployer" "uniBTCMainnetAdmin" --network=eth-mainnet -I`

def main(deployer="deployer", default_admin="default_admin", ):
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    ProxyAdmin = deps.ProxyAdmin

    deployer = accounts.load(deployer)
    default_admin = accounts.load(default_admin)

    vault_proxy_address = "0x047d41f2544b7f63a8e991af2068a363d210d6da"

    # Deployed contracts
    proxy_admin = ProxyAdmin.at("0x029E4FbDAa31DE075dD74B2238222A08233978f6")
    uni_btc = uniBTC.at("0x004e9c3ef86bc1ca1f0bb5c7662861ee93350568")

    # Check permissions before upgrade
    assert uni_btc.hasRole(uni_btc.DEFAULT_ADMIN_ROLE(), default_admin)
    assert  uni_btc.hasRole(uni_btc.MINTER_ROLE(), vault_proxy_address)

    # Upgrade uniBTC
    frozen_users= ["0x893411580e590D62dDBca8a703d61Cc4A8c7b2b9",
                   "0x1E1d02D663228e5D47f1De64030B39632A3B787D",
                   "0x0000000000004F3D8AAf9175fD824CB00aD4bf80",
                   "0xCAfc58De1E6A071790eFbB6B83b35397023E1544",
                   "0x2c87fD92DA54Ab1af3683B5E70E6Dc065F5Df490",
                   "0x4d0f57689843C32A53668C8D69ddD65f7A490965",
                   "0x708b1bDdA2d9274De42303cE1979b58D1660C499",
                   "0xdA83eA6CDa19ce430816b565750F692F15E89ded",
                   "0xbC0842230c10066C47711342608ffeed26661884",
                   "0x1A907D828Af47423b22cf384A699223e06EeB349",
                   "0xaDDA48a3F790664e01b4DF7029041dA58C5E6c24",
                   "0x3Ff8788f9172d77A9688939bc00442C7be9042bF",
                   "0x581404553d7dD49cdc458B117D765CF0D9a118f8",
                   "0xeF15b99D9d748bd7021906429565027Eb5FB5169",
                   "0x7d522f67268F1C46D888fe083aAa86f784B9d082",
                   "0xDeAF42D4a2CC1Dc14505Ce4E4f59629aeC253d75",
                   "0xf1809f69E33A81796651D3DD14abDb3652d9625b",
                   "0x959A90a6B88D19184ac7c46Dfe43ff2968b12bd2",
                   "0xD6095f91A366eAb359bfE54143e151700d32476d",
                   "0x0290445D5F6F78452D4d70B49C267bD856fDa636",
                   "0xe676708EA7611c93Ee106b1D7a2c6F721Fc10c18",
                   "0x5f2f99f21181D8668EC6E2e761704d9C383f989A",
                   "0x39E856863e5F6f0654a0b87B12bc921DA23D06BB",
                   "0xFd2B5F20Ed3B3d9EAb62dEF32188725A4415DD36",
                   "0xAc68803BE3ca28299BF09571945d4cd8e867E7f2"
                   ]

    uniBTC_impl = uniBTC.deploy({'from': deployer})
    reinitialize_data = uniBTC_impl.initialize.encode_input(default_admin, vault_proxy_address, frozen_users)
    proxy_admin.upgradeAndCall(uni_btc.address, uniBTC_impl.address, reinitialize_data, {'from': default_admin})

    # Check contract status after upgrade
    assert uni_btc.hasRole(uni_btc.DEFAULT_ADMIN_ROLE(), default_admin)
    assert uni_btc.hasRole(uni_btc.MINTER_ROLE(), vault_proxy_address)

    assert uni_btc.decimals() == 8
    assert uni_btc.symbol() == "uniBTC"
    assert uni_btc.name() == "uniBTC"

    assert uni_btc.freezeToRecipient() == "0x899c284A89E113056a72dC9ade5b60E80DD3c94f"
    for user in frozen_users:
        assert uni_btc.frozenUsers(user)

    print("Deployed uniBTC implementation: ", uniBTC_impl)  # 0x780a6913885988d8f1290da6abccf8d5faf375c5

