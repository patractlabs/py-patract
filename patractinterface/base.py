import os
import json
import requests

from substrateinterface import SubstrateInterface, ContractMetadata, ContractCode, Keypair
from substrateinterface.exceptions import SubstrateRequestException, ConfigurationError


class SubstrateSubscriber:
    def __init__(self, substrate: SubstrateInterface = None):
        self.substrate = substrate

    @classmethod
    def create_from_address(cls, substrate: SubstrateInterface = None):
        return cls(substrate=substrate)

    def subscribe(self, handler, namespace, method_suffix, args):
        method = namespace + '_' + method_suffix
        return self.substrate.rpc_request(method=method, params=args, result_handler=handler)

    def unsubscribe(self, handler, namespace, unsubscribe_method_suffix):
        method = namespace + '_' + unsubscribe_method_suffix
        return self.substrate.rpc_request(method=method)
