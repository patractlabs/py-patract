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

    # 1. load a contract from WASM file and metadata.json file (Those files is complied by [ink!](https://github.com/paritytech/ink))
    # in this example, we use `ink/example/erc20` contract as example.
    factory = ContractFactory.create_from_file(
        substrate=substrate, 
        code_file=os.path.join(os.path.dirname(__file__), 'contract', 'erc20.wasm'),
        metadata_file=os.path.join(os.path.dirname(__file__), 'contract', 'erc20.json')
    )

    # this api is `ContractAPI`
    api = factory.new(alice, 1000000 * (10 ** 15), endowment=10**15, gas_limit=1000000000000)
    print(api.contract_address) # contract_address is the deployed contract

if __name__ == "__main__":
    main()
    pass