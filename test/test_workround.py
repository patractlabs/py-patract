import unittest
import os
import logging

from substrateinterface import SubstrateInterface, Keypair
from patractinterface.contract import ContractAPI, ContractFactory
from patractinterface.observer import ContractObserver
from patractinterface.unittest.env import SubstrateTestEnv

class ContractNormalTestCase(unittest.TestCase):
    def tearDown(cls):
        cls.env.stop_node()

    @classmethod
    def setUpClass(cls):
        # types = {'types': {'LookupSource': 'MultiAddress'}}
        # this test is for [europa](https://github.com/patractlabs/europa) node
        cls.env = SubstrateTestEnv.create_europa(port=39944)
        cls.env.start_node()
        substrate=SubstrateInterface(url=cls.env.url(), type_registry_preset=cls.env.typ(), type_registry=cls.env.types())

        # setup substrate api endpoint
        cls.substrate = substrate
        # setup keypair
        cls.alice = Keypair.create_from_uri('//Alice')
        cls.bob = Keypair.create_from_uri('//Bob')

    def test_erc20_workround(self):
        # 1. create a Factory to generate contract instance later.
        contract = ContractFactory.create_from_file(
            substrate= self.substrate, 
            code_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.wasm'),
            metadata_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json')
        )

        # 2. after put code, developer could deploy the contract
        erc20_ins = contract.new(self.alice, 1000000 * (10 ** 15), endowment=2*10**10, gas_limit=20000000000, deployment_salt="0x12")

        logging.info(f"erc20 addr: {erc20_ins.contract_address}")

        observer = ContractObserver(erc20_ins.contract_address, erc20_ins.metadata, self.substrate)
        # 3. do a transfer call for this contract
        res = erc20_ins.transfer(self.alice, self.bob.ss58_address, 100000, gas_limit=20000000000)
        logging.info(f'transfer res {res.error_message}')
        self.assertTrue(res.is_success)

        # 4 define callback for events
        def on_transfer(num, evt):
            logging.info("on_transfer in {} : {} {} {}".format(num, evt['from'], evt['to'], evt['value']))

        def on_approval(num, evt):
            logging.info("on_approval in {} : {} {} {}".format(num, evt['owner'], evt['spender'], evt['value']))

        # 5. listen event for this erc20 contract instance
        observer.scanEvents(handlers={
            'Transfer': on_transfer,
            'Approve': on_approval
        }, to_num=2)

