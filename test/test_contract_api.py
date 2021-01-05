import json
import unittest
import logging
import os

from scalecodec import ScaleBytes, ScaleDecoder
from substrateinterface import SubstrateInterface, ContractMetadata, ContractInstance, Keypair
from substrateinterface.utils.ss58 import ss58_encode
from patractinterface.base import SubstrateSubscriber, get_contract_event_type
from patractinterface.unittest.env import SubstrateTestEnv
from patractinterface.contracts.erc20 import ERC20
from patractinterface.contract import ContractAPI

class ContractSubscriberTestCase(unittest.TestCase):
    @classmethod
    def tearDown(cls):
        cls.env.stopNode()

    @classmethod
    def setUpClass(cls):
        cls.env = SubstrateTestEnv.create_europa(port=39944)
        cls.env.startNode()
        substrate=SubstrateInterface(url=cls.env.url(), type_registry_preset=cls.env.typ())

        cls.subscriber = SubstrateSubscriber(substrate)
        cls.substrate = substrate

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

        cls.erc20.putAndDeploy(cls.alice, 1000000 * (10 ** 15))

    def test_contract_api_erc20(self):
        api = ContractAPI(self.erc20.contract_address, self.contract_metadata, self.substrate)
        alice_balance_old = api.balance_of(self.bob, self.alice.ss58_address)

        res = api.transfer(self.alice, self.bob.ss58_address, 100000, gas_limit=20000000000)
        logging.info(f'transfer res {res.error_message}')
        self.assertTrue(res.is_succes)

        alice_balance = api.balance_of(self.bob, self.alice.ss58_address)
        logging.info(f'transfer alice_balance {alice_balance}')

        bob_balance = api.balance_of(self.bob, self.bob.ss58_address)
        logging.info(f'transfer bob_balance {bob_balance}')

        self.assertEqual(alice_balance, alice_balance_old - 100000)
        self.assertEqual(bob_balance,   100000)