import os
import unittest
import logging
import threading
import time

from substrateinterface import SubstrateInterface, ContractMetadata, Keypair
from substrateinterface.utils.ss58 import ss58_encode
from patractinterface.unittest.env import SubstrateTestEnv
from patractinterface.contracts.erc20 import ERC20, ERC20Observer


class ERC20ObserverTestCase(unittest.TestCase):
    @classmethod
    def tearDown(cls):
        cls.env.stop_node()

    @classmethod
    def setUpClass(cls):
        logging.info("init deplay")

        cls.env = SubstrateTestEnv.create_europa(port=39944)
        cls.env.start_node()
        cls.substrate=SubstrateInterface(url=cls.env.url(), type_registry_preset=cls.env.typ(), type_registry=cls.env.types())

        cls.contract_metadata = ContractMetadata.create_from_file(
            metadata_file=os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json'),
            substrate=cls.substrate
        )

        cls.erc20 = ERC20.create_from_contracts(
            substrate= cls.substrate, 
            contract_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.wasm'),
            metadata_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json')
        )
        cls.alice = Keypair.create_from_uri('//Alice')
        cls.bob = Keypair.create_from_uri('//Bob')

        cls.erc20.instantiate_with_code(cls.alice, 1000000 * (10 ** 15))

        cls.observer = ERC20Observer.create_from_address(
            substrate = cls.substrate, 
            contract_address = cls.erc20.contract_address,
            metadata_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json')
        )

    def test_watch(self):
        self.erc20.transfer(self.alice, self.bob.ss58_address, 10000)
        self.erc20.transfer_from(self.alice,
            from_acc=self.alice.ss58_address, 
            to_acc=self.bob.ss58_address, 
            amt=10000)
        self.erc20.approve(self.alice, spender=self.bob.ss58_address, amt=10000)
        self.erc20.transfer(self.alice, self.bob.ss58_address, 100000)

        logging.info("start scan")

        def on_transfer(num, evt):
            logging.info("on_transfer in {} : {} {} {}".format(num, evt['from'], evt['to'], evt['value']))

        def on_approval(num, evt):
            logging.info("on_approval in {} : {} {} {}".format(num, evt['owner'], evt['spender'], evt['value']))

        self.observer.scanEvents(to_num = 5, on_transfer = on_transfer, on_approval = on_approval)

if __name__ == '__main__':
    unittest.main()
