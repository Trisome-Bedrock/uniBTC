from brownie import uniBTC, accounts, Contract, project, config
from pathlib import Path

# Execution Command Format:
# `brownie run scripts/optimism-mainnet/upgrade-uniBTC-v3.py main "uniBTCMainnetDeployer" "uniBTCMainnetAdmin" --network=optimism-main -I`

def main(deployer="deployer", default_admin="default_admin", ):
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    ProxyAdmin = deps.ProxyAdmin

    deployer = accounts.load(deployer)
    default_admin = accounts.load(default_admin)

    vault_proxy_address = "0xF9775085d726E782E83585033B58606f7731AB18"

    # Deployed contracts
    proxy_admin = ProxyAdmin.at("0x0A3f2582FF649Fcaf67D03483a8ED1A82745Ea19")
    uni_btc = uniBTC.at("0x93919784C523f39CACaa98Ee0a9d96c3F32b593e")

    # Check permissions before upgrade
    assert uni_btc.hasRole(uni_btc.DEFAULT_ADMIN_ROLE(), default_admin)
    assert  uni_btc.hasRole(uni_btc.MINTER_ROLE(), vault_proxy_address)

    # Upgrade uniBTC
    frozen_users = ["0xaDDA48a3F790664e01b4DF7029041dA58C5E6c24",
                    "0xe676708EA7611c93Ee106b1D7a2c6F721Fc10c18",
                    "0xAc68803BE3ca28299BF09571945d4cd8e867E7f2",
                    "0x40A1448A7F6243CD7aF514048bc9770F874d0733"
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

    print("Deployed uniBTC implementation: ", uniBTC_impl)  # 0x89b2c722Abf9E1C8DD215E4E8352e0f293740Aeb

