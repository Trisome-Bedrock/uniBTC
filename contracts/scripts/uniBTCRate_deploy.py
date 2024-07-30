from brownie import uniBTCRate, accounts, Contract, project, config

# Execution Command Format:
# `brownie run scripts/uniBTCRate_deploy.py main "owner" --network=optimism-main`


def main(owner="owner"):
    owner = accounts.load(owner)

    # Deploy contracts
    uni_btc_rate = uniBTCRate.deploy({'from': owner})

    # Check status
    assert uni_btc_rate.getRate() == 1e8

    print("Deployed uniBTCRate address: ", uni_btc_rate)

    # Deployed contract on OP mainnet: 0x56c3024eB229Ca0570479644c78Af9D53472B3e4
