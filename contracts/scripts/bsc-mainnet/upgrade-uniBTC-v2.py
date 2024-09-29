from brownie import uniBTC, accounts, Contract, project, config
from pathlib import Path

# Execution Command Format:
# `brownie run scripts/bsc-mainnet/upgrade-uniBTC-v2.py main "uniBTCMainnetDeployer" "uniBTCMainnetAdmin" --network=bsc-main -I`

def main(deployer="deployer", default_admin="default_admin", ):
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    ProxyAdmin = deps.ProxyAdmin

    deployer = accounts.load(deployer)
    default_admin = accounts.load(default_admin)

    vault_proxy_address = "0x84E5C854A7fF9F49c888d69DECa578D406C26800"

    # Deployed contracts
    proxy_admin = ProxyAdmin.at("0xb3f925B430C60bA467F7729975D5151c8DE26698")
    uni_btc = uniBTC.at("0x6B2a01A5f79dEb4c2f3c0eDa7b01DF456FbD726a")

    # Check permissions before upgrade
    assert uni_btc.hasRole(uni_btc.DEFAULT_ADMIN_ROLE(), default_admin)
    assert  uni_btc.hasRole(uni_btc.MINTER_ROLE(), vault_proxy_address)

    # Upgrade uniBTC
    frozen_users = ["0x3Ff8788f9172d77A9688939bc00442C7be9042bF",
                    "0xe676708EA7611c93Ee106b1D7a2c6F721Fc10c18",
                    "0x994b28cC5dF7591ee77b0Bc882dbC600fe11940d",
                    "0x1A907D828Af47423b22cf384A699223e06EeB349",
                    "0xa865ba66C140B704562a02CEeDCb4AB1baF46C27",
                    "0xD7435aEB02f7299ab539E0946450F91e7dA066B8",
                    "0xbC0842230c10066C47711342608ffeed26661884",
                    "0x7A505dF95aAc78f142CA98CeCd771d3c398b4b71",
                    "0x16bF14f25910231Ad328d9d21aF44f0d64C37BF1",
                    "0xC476267c64C2a0f383Fb14cE77eCeF555071dd36",
                    "0x0c31cfa27e53FCDF5392a15aba41963ebc8223A8",
                    "0x767f42B9A127F80180CB1F699a690dc2edC9cD03",
                    "0xDeAF42D4a2CC1Dc14505Ce4E4f59629aeC253d75",
                    "0xf1809f69E33A81796651D3DD14abDb3652d9625b"
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

    print("Deployed uniBTC implementation: ", uniBTC_impl)  # 0x9203ce1bcded1a20f697e1780bc47d5b6d718031

