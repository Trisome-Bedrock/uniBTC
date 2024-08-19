from brownie import Vault, accounts

# Execution Command Format:
# `brownie run scripts/vault_impl_deploy.py main "owner" "ethereum" --network=mainnet-public`

def main(owner="owner", network="ethereum"):
    owner = accounts.load(owner)

    vault_impl = Vault.deploy({'from': owner})

    print("Network: ", network)
    print("  Deployed Vault implementation address: ", vault_impl)

    # Deployed Vault implementation addresses:
    # Ethereum: 0xC0c9E78BfC3996E8b68D872b29340816495D7e89                # https://etherscan.io/address/0xC0c9E78BfC3996E8b68D872b29340816495D7e89
    # Mantle: 0xC0c9E78BfC3996E8b68D872b29340816495D7e89                  # https://explorer.mantle.xyz/address/0xC0c9E78BfC3996E8b68D872b29340816495D7e89




