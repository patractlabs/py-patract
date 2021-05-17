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
    contract = ContractFactory.create_from_file(
            substrate=substrate, # should provide a subtrate endpoint
            code_file= os.path.join(os.path.dirname(__file__), 'contract', 'erc20.wasm'),
            metadata_file= os.path.join(os.path.dirname(__file__), 'contract', 'erc20.json')
        )

    # 2. instantiate the uploaded code as a contract instance
    erc20_ins = contract.new(alice, 1000000 * (10 ** 15), endowment=2*10**10, gas_limit=20000000000, deployment_salt="0x12")

    # 2.1 create a observer to listen event
    observer = ContractObserver(erc20_ins.contract_address, erc20_ins.metadata, substrate)

    # 3. send a transfer call for this contract
    res = erc20_ins.transfer(alice, bob.ss58_address, 100000, gas_limit=20000000000)
    print('transfer res', res.is_success)

    def on_transfer(num, evt):
        print("on_transfer in {} : {} {} {}".format(num, evt['from'], evt['to'], evt['value']))

    def on_approval(num, evt):
        print("on_approval in {} : {} {} {}".format(num, evt['owner'], evt['spender'], evt['value']))

    # 4 set event callback 
    observer.scanEvents(to_num=2, handlers={
        'Transfer': on_transfer,
        'Approve': on_approval
    })

if __name__ == "__main__":
    main()
    pass