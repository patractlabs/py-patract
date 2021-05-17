import os
from substrateinterface import SubstrateInterface, Keypair
from patractinterface.contract import ContractAPI, ContractFactory
from patractinterface.observer import ContractObserver

def main():
    # use [europa](https://github.com/patractlabs/europa) as test node endpoint, notice `type_registry` should set correctly.
    substrate=SubstrateInterface(url='ws://127.0.0.1:9944', type_registry_preset="default", type_registry={'types': {'LookupSource': 'MultiAddress'}})
    # load deployer key
    alice = Keypair.create_from_uri('//Alice')
    bob = Keypair.create_from_uri('//Bob')

    factory = ContractFactory.create_from_file(
        substrate=substrate, 
        code_file=os.path.join(os.path.dirname(__file__), 'contract', 'erc20.wasm'),
        metadata_file=os.path.join(os.path.dirname(__file__), 'contract', 'erc20.json')
    )

    auto_api = factory.new(alice, 1000000 * (10 ** 15), endowment=10**15, gas_limit=1000000000000)

    # api will auto generate caller for contract from metadata
    # this api is for test
    api = ContractAPI(auto_api.contract_address, factory.metadata, substrate)
    alice_balance_old = api.balance_of(bob, alice.ss58_address) # bob is the keypair for `//Bob`

    res = api.transfer(alice, bob.ss58_address, 100000, gas_limit=20000000000)
    print(f'transfer res {res.error_message}')
    print(res.is_success)

    alice_balance = api.balance_of(bob, alice.ss58_address)
    print(f'transfer alice_balance from {alice_balance_old} to {alice_balance}')

    bob_balance = api.balance_of(bob, bob.ss58_address)
    print(f'transfer bob_balance {bob_balance}')

if __name__ == "__main__":
    main()
    pass