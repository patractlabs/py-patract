import os
import logging
import json

from scalecodec.block import EventRecord, EventsDecoder, LogDigest, MetadataDecoder
from scalecodec.metadata import MetadataV12Decoder
from scalecodec.base import ScaleDecoder
from scalecodec import ScaleBytes, ScaleType, GenericContractExecResult
from substrateinterface import SubstrateInterface, ContractMetadata, ContractInstance, Keypair
from substrateinterface.exceptions import SubstrateRequestException
from patractinterface.base import *
from substrateinterface.constants import *

class ContractMessageArgError(ValueError):
    pass


class contractExecutor:
    def __init__(self, name, data, contract_address: str, metadata: ContractMetadata = None, substrate: SubstrateInterface = None):
        self.substrate = substrate
        self.contract_address = contract_address
        self.metadata = metadata
        self.name = name
        self.data = data
        self.instance = ContractInstance(contract_address, metadata, substrate)

    def __call__(self, *args, **kwargs):
        logging.debug(f'args {args}')
        
        if (len(self.data['args']) + 1) != len(args):
            raise ContractMessageArgError(f'exec args num error: export {len(self.data.args)}, got {len(args) - 1}')

        call_args = {}
        for i in range(0, len(self.data['args'])):
            arg_name = self.data['args'][i]['name']
            call_args[arg_name] = args[i + 1]

        gas_limit = 200000
        if 'gas_limit' in kwargs:
            gas_limit = kwargs['gas_limit']
        
        value = 0
        if 'value' in kwargs:
            value = kwargs['value']

        logging.debug(f'args to call {call_args} {gas_limit}')
        res = self.instance.exec(keypair=args[0], method=self.name, args=call_args, gas_limit=gas_limit, value=value)

        return res

class contractReader:
    def __init__(self, name, data, contract_address: str, metadata: ContractMetadata = None, substrate: SubstrateInterface = None):
        self.substrate = substrate
        self.contract_address = contract_address
        self.metadata = metadata
        self.name = name
        self.data = data
        self.instance = ContractInstance(contract_address, metadata, substrate)

    def __call__(self, *args, **kwargs):
        logging.debug(f'args {args}')
        
        if (len(self.data['args']) + 1) != len(args):
            raise ContractMessageArgError(f'exec args num error: export {len(self.data.args)}, got {len(args) - 1}')

        call_args = {}
        for i in range(0, len(self.data['args'])):
            arg_name = self.data['args'][i]['name']
            call_args[arg_name] = args[i + 1]

        logging.debug(f'args to call {self.name} {call_args}')
        res = self.instance.read(keypair=args[0], method=self.name, args=call_args)

        logging.debug(f'args to call {res.value}')

        if res.value['result']['Ok']['data'] != None:
            return res.value['result']['Ok']['data']
        else:
            return res

class ContractAPI:
    def __init__(self, contract_address: str, metadata: ContractMetadata = None, substrate: SubstrateInterface = None):
        self.substrate = substrate
        self.contract_address = contract_address
        self.metadata = metadata
        self.event_decoder_typ = get_contract_event_type(metadata)

        self.caller = {}
        self._constructors_data = {}
        self._execs_data = {}
        self._reads_data = {}
        self._make_messages()

    @classmethod
    def create_from_address(cls, contract_address: str, metadata_file: str,
                            substrate: SubstrateInterface = None):
        metadata = ContractMetadata.create_from_file(metadata_file, substrate=substrate)
        return cls(contract_address=contract_address, metadata=metadata, substrate=substrate)

    def _make_exec_caller(self, name, data):
        logging.debug(f'exec {name} --> {data}')
        self.__dict__[name] = contractExecutor(name, data, self.contract_address, self.metadata, self.substrate)


    def _make_read_caller(self, name, data):
        logging.debug(f'read {name} --> {data}')
        self.__dict__[name] = contractReader(name, data, self.contract_address, self.metadata, self.substrate)

    def _make_messages(self):
        constructors = self.metadata.metadata_dict['spec']['constructors']
        messages = self.metadata.metadata_dict['spec']['messages']

        for m in messages:
            if m['mutates'] is True:
                # TODO: for multiple path
                if len(m['name']) == 1:
                    self._execs_data[m['name'][0]] = m
            else:
                if len(m['name']) == 1:
                    self._reads_data[m['name'][0]] = m

        for n in self._execs_data:
            self._make_exec_caller(n, self._execs_data[n])
        
        for n in self._reads_data:
            self._make_read_caller(n, self._reads_data[n])