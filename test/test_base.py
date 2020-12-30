import json
import unittest
import logging

from scalecodec import ScaleBytes
from substrateinterface import SubstrateInterface, ContractMetadata, ContractInstance, Keypair
from substrateinterface.utils.ss58 import ss58_encode
from patractinterface.base import SubstrateSubscriber

evt_getted = 0

class ContractSubscriberTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        substrate=SubstrateInterface(url="ws://127.0.0.1:9944", type_registry_preset='canvas')
        cls.subscriber = SubstrateSubscriber(substrate)

    #def setUp(self) -> None:

    def test_subscriber(self):
        def result_handler(result):
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

if __name__ == '__main__':
    unittest.main()
