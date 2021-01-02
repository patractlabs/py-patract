import os
import json
import logging

from substrateinterface import SubstrateInterface, ContractMetadata, ContractCode, Keypair
from substrateinterface.exceptions import SubstrateRequestException, ConfigurationError
from scalecodec.base import RuntimeConfiguration
from scalecodec.types import Enum, Struct

class SubstrateSubscriber:
    def __init__(self, substrate: SubstrateInterface = None):
        self.substrate = substrate

    @classmethod
    def create_from_address(cls, substrate: SubstrateInterface = None):
        return cls(substrate=substrate)

    def subscribe(self, handler, namespace, method_suffix, args):
        method = namespace + '_' + method_suffix
        return self.substrate.rpc_request(method=method, params=args, result_handler=handler)

    def unsubscribe(self, namespace, unsubscribe_method_suffix):
        method = namespace + '_' + unsubscribe_method_suffix
        return self.substrate.rpc_request(method=method)

def get_contract_event_type(metadata: ContractMetadata):
    # TODO: use a way to fix this event_id, now just append to types
    event_id = len(metadata.metadata_dict['types']) + 1

    type_definition = {
      "type": "enum",
      "type_mapping": []
    }

    logging.debug("metadata {}".format(json.dumps(metadata.metadata_dict['spec']['events'])))

    for evtNum in range(0, len(metadata.metadata_dict['spec']['events'])):
        evt = metadata.metadata_dict['spec']['events'][evtNum]
        logging.debug("evt {} {}".format(evtNum, evt['name']))

        if 'args' in evt and len(evt['args']) > 1:
            evt_args_def = {
                "type": "struct",
                "type_mapping": []
            }

            for fieldNum in range(0, len(evt['args'])):
                field = evt['args'][fieldNum]
                logging.debug("Field {}/{} {}".format(evtNum, fieldNum, field))

                evt_args_def['type_mapping'].append(
                    [field['name'], metadata.get_type_string_for_metadata_type(field['type']['type'])]
                )

            type_id = event_id + 1 + evtNum
            type_str = f'{metadata.type_string_prefix}.{type_id}'
            # Add to type registry
            metadata.substrate.runtime_config.update_type_registry_types(
                {type_str: evt_args_def}
            )

            # Generate unique type string
            metadata.type_registry[type_id] = type_str

            logging.debug("args {} {} {}".format(evtNum, type_str, json.dumps(evt_args_def)))

            enum_value = f'{metadata.type_string_prefix}.{type_id}'
        else:
            enum_value = 'Null'

        type_definition['type_mapping'].append(
            [evt['name'], enum_value]
        )

    # Add to type registry
    metadata.substrate.runtime_config.update_type_registry_types(
        {f'{metadata.type_string_prefix}.{event_id}': type_definition}
    )
    # Generate unique type string
    metadata.type_registry[event_id] = f'{metadata.type_string_prefix}.{event_id}'

    return f'{metadata.type_string_prefix}.{event_id}'
