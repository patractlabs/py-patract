import os
import logging
import json

from scalecodec.block import EventRecord, EventsDecoder, LogDigest, MetadataDecoder
from scalecodec.metadata import MetadataV12Decoder
from scalecodec.base import ScaleDecoder
from scalecodec import ScaleBytes, ScaleType, GenericContractExecResult
from substrateinterface import SubstrateInterface, ContractMetadata, ContractCode, Keypair
from substrateinterface.exceptions import SubstrateRequestException
from patractinterface.base import *
from substrateinterface.constants import *


class ContractObserver:
    def __init__(self, contract_address: str, metadata: ContractMetadata = None, substrate: SubstrateInterface = None):
        self.substrate = substrate
        self.contract_address = contract_address
        self.metadata = metadata
        self.subscriber = SubstrateSubscriber(substrate)

    @classmethod
    def create_from_address(cls, contract_address: str, metadata_file: str,
                            substrate: SubstrateInterface = None):
        """
        Create a ContractObserver object that already exists on-chain providing a SS58-address and the path to the
        metadata JSON of that contract

        Parameters
        ----------
        contract_address
        metadata_file
        substrate

        Returns
        -------
        ContractObserver
        """

        metadata = ContractMetadata.create_from_file(metadata_file, substrate=substrate)

        return cls(contract_address=contract_address, metadata=metadata, substrate=substrate)

    def decode_event(self, metadata_decoder, data):
        events_decoder = EventsDecoder(
            data=ScaleBytes(data),
            metadata=metadata_decoder,
            runtime_config=self.substrate.runtime_config
        )
        events_decoder.decode()

        return events_decoder

    def get_block_events(self, block_hash, metadata_decoder=None):
        """
        A convenience method to fetch the undecoded events from storage

        Parameters
        ----------
        block_hash
        metadata_decoder

        Returns
        -------

        """

        key = self.subscriber.substrate.generate_storage_hash(storage_module = "System", storage_function = "Events")
        response = self.substrate.rpc_request(method = "state_getStorage", params = [key, block_hash])

        if response.get('result'):
            return self.decode_event(metadata_decoder, response.get('result'))
        else:
            raise SubstrateRequestException("Error occurred during retrieval of events")

    def scanEvents(self, from_num = None):
        def result_handler(res):
            # Check if extrinsic is included and finalized
            if 'params' in res:
                if res['method'] != 'state_storage':
                    return
                
                hash = res['params']['result']['block']
                blk_number = self.substrate.get_block_number(hash)

                for c in res['params']['result']['changes']:
                    evt = self.decode_event(metadata_decoder, c[1])
                    logging.info("event: {} data {}".format(blk_number, evt))


        chain_head = self.substrate.get_chain_head()
        blk_number = self.substrate.get_block_number(chain_head)

        metadata_decoder = self.substrate.get_block_metadata(block_hash = chain_head)

        logging.debug("get head {} {}".format(blk_number, json.dumps(chain_head)))

        if from_num == None:
            from_num = 1

        while from_num < blk_number:
            for num in range(from_num, blk_number + 1):
                hash = self.substrate.get_block_hash(num)
                blk_events = self.get_block_events(block_hash = hash, metadata_decoder = metadata_decoder)
                for evt in blk_events.elements:
                    logging.info("get event {} to {}".format(num, evt))

            from_num = blk_number + 1
            blk_number = self.substrate.get_block_number(self.substrate.get_chain_head())

        keys = [self.subscriber.substrate.generate_storage_hash(storage_module = "System", storage_function = "Events")]
        self.subscriber.subscribe(result_handler, "state", "subscribeStorage", [keys])