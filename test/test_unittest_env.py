import os
import json
import unittest
import logging

from scalecodec import ScaleBytes
from substrateinterface.utils.ss58 import ss58_encode
from substrateinterface import SubstrateInterface, ContractMetadata, Keypair
from patractinterface.contracts.erc20 import ERC20
from patractinterface.unittest.env import SubstrateTestEnv

class UnittestEnvTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.env = SubstrateTestEnv.create_europa(port=39944)
        cls.env.start_node()
        return

    def tearDown(cls):
        cls.env.stop_node()

    def test_env_canvas(self):
        # init api
        substrate=SubstrateInterface(url=self.env.url(), type_registry_preset=self.env.typ(), type_registry=self.env.types())

        alice = Keypair.create_from_uri('//Alice')
        bob = Keypair.create_from_uri('//Bob')

        # erc20 api
        erc20 = ERC20.create_from_contracts(
            substrate= substrate, 
            contract_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.wasm'),
            metadata_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json')
        )

        # deplay a erc20 contract
        erc20.instantiate_with_code(alice, 1000000 * (10 ** 15))

        erc20.transfer_from(alice,
            from_acc=alice.ss58_address, 
            to_acc=bob.ss58_address, 
            amt=10000)

        erc20.transfer(alice, bob.ss58_address, 10000)

if __name__ == '__main__':
    unittest.main()
