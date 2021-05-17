import json
import unittest
import logging
import os

from scalecodec import ScaleBytes, ScaleDecoder
from substrateinterface import SubstrateInterface, ContractMetadata, ContractInstance, Keypair
from substrateinterface.utils.ss58 import ss58_encode
from patractinterface.base import SubstrateSubscriber, get_contract_event_type
from patractinterface.unittest.env import SubstrateTestEnv

evt_getted = 0

class ContractSubscriberTestCase(unittest.TestCase):
    @classmethod
    def tearDown(cls):
        cls.env.stop_node()

    @classmethod
    def setUpClass(cls):
        cls.env = SubstrateTestEnv.create_europa(port=39944)
        cls.env.start_node()
        substrate=SubstrateInterface(url=cls.env.url(), type_registry_preset=cls.env.typ(), type_registry=cls.env.types())

        cls.subscriber = SubstrateSubscriber(substrate)
        cls.substrate = substrate

    #def setUp(self) -> None:

    def subscriber(self):
        def result_handler(result, update_nr, subscription_id):
            # Check if extrinsic is included and finalized
            logging.info("get res: {}".format(json.dumps(result)))
            global evt_getted 
            
            evt_getted = evt_getted + 1
            if evt_getted > 5:
                return True
            else :
                return None


        keys = [self.subscriber.substrate.generate_storage_hash(storage_module = "System", storage_function = "Events")]

        self.subscriber.subscribe(result_handler, "state", "subscribeStorage", [keys])

    def test_get_contract_event_type(self):
        contract_metadata = ContractMetadata.create_from_file(
            metadata_file=os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json'),
            substrate=self.substrate
        )

        typ15 = contract_metadata.get_type_string_for_metadata_type(15)
        logging.debug("typ15 {}".format(typ15))
        decoder = ScaleDecoder.get_decoder_class(typ15, 
            ScaleBytes("0x01d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d"),
            self.substrate.runtime_config)
        evtTransferArgs = decoder.decode()
        logging.debug("evtTransfer {}".format(evtTransferArgs))
        self.assertEqual(evtTransferArgs, '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY')

        type_data = get_contract_event_type(contract_metadata)
        logging.debug("type_event_data {}".format(type_data))

        decoder = ScaleDecoder.get_decoder_class(type_data, 
            ScaleBytes("0x000001d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d0000a0dec5adc9353600000000000000"),
            self.substrate.runtime_config)
        evtTransfer1 = decoder.decode()
        self.assertEqual(evtTransfer1['Transfer']['from'], None)
        self.assertEqual(evtTransfer1['Transfer']['to'], '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY')
        self.assertEqual(evtTransfer1['Transfer']['value'], 1000000000000000000000)

        logging.debug("evtTransfer {}".format(evtTransfer1))

        decoder = ScaleDecoder.get_decoder_class(type_data, 
            ScaleBytes("0x0001d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d018eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a4810270000000000000000000000000000"),
            self.substrate.runtime_config)
        evtTransfer2 = decoder.decode()
        self.assertEqual(evtTransfer2['Transfer']['from'], '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY')
        self.assertEqual(evtTransfer2['Transfer']['to'], '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty')
        self.assertEqual(evtTransfer2['Transfer']['value'], 10000)

        logging.debug("evtTransfer2 {}".format(evtTransfer2))

        decoder = ScaleDecoder.get_decoder_class(type_data, 
            ScaleBytes("0x01d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a4810270000000000000000000000000000"),
            self.substrate.runtime_config)
        evtApprove1 = decoder.decode()

        self.assertEqual(evtApprove1['Approval']['owner'], '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY')
        self.assertEqual(evtApprove1['Approval']['spender'], '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty')
        self.assertEqual(evtApprove1['Approval']['value'], 10000)
        logging.debug("evtApprove1 {}".format(evtApprove1))

if __name__ == '__main__':
    unittest.main()
