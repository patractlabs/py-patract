import os
import unittest
import logging

from substrateinterface import SubstrateInterface, ContractMetadata, Keypair
from substrateinterface.utils.ss58 import ss58_encode
from patractinterface.unittest.env import SubstrateTestEnv
from patractinterface.contracts.erc20 import ERC20


class ERC20TestCase(unittest.TestCase):

    @classmethod
    def tearDown(cls):
        cls.env.stopNode()

    @classmethod
    def setUpClass(cls):
        logging.info("init deplay")
        cls.env = SubstrateTestEnv.create_europa(port=39944)
        cls.env.startNode()
        cls.substrate=SubstrateInterface(url=cls.env.url(), type_registry_preset=cls.env.typ())

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

    def transfer(self):
        supply = self.erc20.totalSupply()
        self.assertEqual(supply, 1000000 * (10 ** 15))

        res = self.erc20.transfer(self.alice, self.bob.ss58_address, 10000)
        self.assertTrue(res.is_succes)
        self.check_balance_of(self.bob.ss58_address, 10000)

    def transferFrom(self):
        res = self.erc20.transferFrom(self.alice,
            fromAcc=self.alice.ss58_address, 
            toAcc=self.bob.ss58_address, 
            amt=10000)
        self.assertTrue(res.is_succes)

    def approve(self):
        res = self.erc20.approve(self.alice, spender=self.bob.ss58_address, amt=10000)
        self.assertTrue(res.is_succes)
        allowance = self.erc20.allowance(self.alice.ss58_address, self.bob.ss58_address)
        self.assertEqual(allowance, 10000)

    def check_balance_of(self, acc, value):
        res = self.erc20.balanceOf(acc)
        self.assertEqual(res, value)

    def test_exec_and_read(self):
        self.transfer()
        self.approve()
        self.transferFrom()

if __name__ == '__main__':
    unittest.main()
