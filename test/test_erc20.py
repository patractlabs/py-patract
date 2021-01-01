import os
import json
import unittest
import logging

from scalecodec import ScaleBytes
from substrateinterface import SubstrateInterface, ContractMetadata, ContractInstance, Keypair
from substrateinterface.utils.ss58 import ss58_encode

from patractinterface.contracts.erc20 import ERC20


class ERC20TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.substrate=SubstrateInterface(url="ws://127.0.0.1:9944", type_registry_preset='canvas')

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

    def setUp(self) -> None:
        self.erc20.putAndDeploy(self.alice, 1000000 * (10 ** 15))

    def test_transfer(self):
        res = self.erc20.transfer(self.alice, self.bob.ss58_address, 10000)
        is_succes = res.is_succes
        self.assertTrue(is_succes)

if __name__ == '__main__':
    unittest.main()
