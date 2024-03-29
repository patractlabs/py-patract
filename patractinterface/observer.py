import os
import logging
import json

from scalecodec.base import ScaleDecoder, RuntimeConfigurationObject
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
        self.event_decoder_typ = get_contract_event_type(metadata)

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

    def process_handler(self, handler, num, evt):
        if handler == None:
            return
        
        logging.debug("event: {} data {}".format(num, evt))

        if evt['module_id'] != 'Contracts':
            return
        
        logging.debug("event: {} data {}".format(num, evt))
        return handler(num, evt)

    def scanEvents(self, from_num = None, to_num = None, handlers = None):
        def handlerContracts(num, evt):
            if evt['event_id'] != 'ContractEmitted':
                return

            # for p in evt['params']:
            for p in evt['event']['attributes']:
                typ = p['type']
                if typ == 'Vec<u8>':
                    decoder = ScaleDecoder.get_decoder_class(self.event_decoder_typ, 
                        ScaleBytes(p['value']),
                        self.substrate.runtime_config)
                    evtDecoded = decoder.decode()
                    keys = list(evtDecoded.keys())
                    if len(keys) == 1:
                        h = handlers.get(keys[0], None)
                        if h is not None:
                            h(num, evtDecoded[keys[0]])

            if to_num != None and num >= to_num:
                logging.info("return by to_num")
                return True

        return self.scanChainEvents(from_num, handlerContracts)

    def scanChainEvents(self, from_num = None, handler = None):
        def result_handler(res, update_nr, subscription_id):
            # Check if extrinsic is included and finalized
            if 'params' in res:
                if res['method'] != 'state_storage':
                    return
                
                hash = res['params']['result']['block']
                blk_number = self.substrate.get_block_number(hash)

                for c in res['params']['result']['changes']:
                    # evt = self.decode_event(event_metadata_decoder, c[1])
                    evt = blk_events
                    for e in evt.value:
                        return self.process_handler(handler, blk_number, e)


        chain_head = self.substrate.get_chain_head()
        blk_number = self.substrate.get_block_number(chain_head)

        # metadata_decoder = self.substrate.get_block_metadata(block_hash = chain_head)


        logging.debug("get head {} {}".format(blk_number, json.dumps(chain_head)))

        if from_num == None:
            from_num = 1

        while from_num < blk_number:
            for num in range(from_num, blk_number + 1):
                hash = self.substrate.get_block_hash(num)
                self.substrate.init_runtime()
                blk_events = self.substrate.query("System", "Events", block_hash=hash)
                for evt in blk_events.elements:
                    res = self.process_handler(handler, num, evt.value)
                    if not res == None:
                        return

            from_num = blk_number + 1
            blk_number = self.substrate.get_block_number(self.substrate.get_chain_head())

        keys = [self.subscriber.substrate.generate_storage_hash(storage_module = "System", storage_function = "Events")]
        self.subscriber.subscribe(result_handler, "state", "subscribeStorage", [keys])