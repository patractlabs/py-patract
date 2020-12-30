import os
import json
import unittest
import logging

from scalecodec import ScaleBytes
from substrateinterface import SubstrateInterface, ContractMetadata, ContractInstance, Keypair
from substrateinterface.utils.ss58 import ss58_encode

from patractinterface.observer import ContractObserver


class ContractObserverTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.substrate=SubstrateInterface(url="ws://127.0.0.1:9944")
        cls.contract_metadata = ContractMetadata.create_from_file(
            metadata_file=os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json'),
            substrate=cls.substrate
        )
        cls.observer = ContractObserver("0x", cls.contract_metadata, cls.substrate)

    def test_eventScan(self):
        self.observer.scanEvents()

if __name__ == '__main__':
    unittest.main()
