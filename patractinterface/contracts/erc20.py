import os
import logging
import json

from substrateinterface import SubstrateInterface, ContractInstance, ContractMetadata, ContractCode
from substrateinterface.exceptions import SubstrateRequestException, DeployContractFailedException
from substrateinterface import ContractCode, Keypair
from scalecodec import ScaleBytes, ScaleDecoder
from patractinterface.observer import ContractObserver
from patractinterface.base import get_contract_event_type

class ContractAddressFailedException(Exception):
    pass

class ERC20:
    def __init__(self, address: str, substrate: SubstrateInterface, metadata: ContractMetadata, code: ContractCode = None):
        self.substrate = substrate
        self.contract_address = address
        self.metadata = metadata
        self.code = code
        self.instance = None
        if address != "":
            self.instance = ContractInstance(address, metadata, substrate)


    @classmethod
    def create_from_address(cls, contract_address: str, metadata_file: str, substrate: SubstrateInterface):
        metadata = ContractMetadata.create_from_file(metadata_file, substrate=substrate)
        return cls(address=contract_address, metadata=metadata, substrate=substrate)

    @classmethod
    def create_from_contracts(cls, contract_file: str, metadata_file: str, substrate: SubstrateInterface):
        code = ContractCode.create_from_contract_files(
            metadata_file=metadata_file,
            wasm_file=contract_file,
            substrate=substrate
        )

        metadata = ContractMetadata.create_from_file(metadata_file, substrate=substrate)
        return cls(address="", metadata=metadata, substrate=substrate, code=code)

    def put_and_deploy(self, keypair: Keypair, initial_supply, endowment=10**15, gas_limit=1000000000000):
        receipt = self.code.upload_wasm(keypair)
        if receipt.is_success:
            logging.debug("erc20 code deploy success")

            for event in receipt.triggered_events:
                logging.debug("events triggered: {}".format(event.value))

            # Deploy contract
            contract = self.code.deploy(
                keypair=keypair, endowment=endowment, gas_limit=gas_limit,
                constructor="new",
                args={'initial_supply': initial_supply}
            )

            self.contract_address = contract.contract_address
            logging.debug("deploy erc20 token {}".format(self.contract_address))

            self.instance = ContractInstance(self.contract_address, self.metadata, self.substrate)
        else:
            logging.error("deploy erc20 token error {}".format(receipt.error_message))
            raise DeployContractFailedException(receipt.error_message)

    def instantiate_with_code(self, keypair: Keypair, initial_supply, salt: str=None, endowment=10**15, gas_limit=1000000000000):
        # Deploy contract
        contract = self.code.deploy(
            keypair=keypair, endowment=endowment, gas_limit=gas_limit,
            constructor="new",
            args={'initial_supply': initial_supply},
            deployment_salt=salt, upload_code=True,
        )

        self.contract_address = contract.contract_address
        logging.debug("deploy erc20 token {}".format(self.contract_address))

        self.instance = ContractInstance(self.contract_address, self.metadata, self.substrate)

    def check_address(self):
        if self.contract_address == "":
            raise ContractAddressFailedException("contract_address is empty need address or deplay")

    def transfer(self, keypair: Keypair, to, amt, value = 0, gas_limit = 100000000000):
        self.check_address()
        args = {
            "to" : to,
            "value" : amt,
        }
        return self.instance.exec(keypair, "transfer", args, value=value, gas_limit=gas_limit)

    def transfer_from(self, keypair: Keypair, from_acc, to_acc, amt, value = 0, gas_limit = 100000000000):
        self.check_address()
        args = {
            "from" : from_acc,
            "to" : to_acc,
            "value" : amt,
        }
        return self.instance.exec(keypair, "transfer_from", args, value=value, gas_limit=gas_limit)

    def approve(self, keypair: Keypair, spender, amt, value = 0, gas_limit = 100000000000):
        self.check_address()
        args = {
            "spender" : spender,
            "value" : amt,
        }
        return self.instance.exec(keypair, "approve", args, value=value, gas_limit=gas_limit)

    def balance_of(self, owner: str):
        self.check_address()
        args = {
            "owner" : owner
        }
        res = self.instance.read(keypair=Keypair(ss58_address = owner), method="balance_of", args=args)
        return res.value['result']['Ok']['data']

    def allowance(self, owner: str, spender: str):
        self.check_address()
        args = {
            "owner" : owner,
            "spender" : spender
        }
        res = self.instance.read(keypair=Keypair(ss58_address = owner), method="allowance", args=args)

        return res.value['result']['Ok']['data']

    def totalSupply(self):
        self.check_address()
        k = Keypair.create_from_uri('//Alice')
        args = {}
        res = self.instance.read(keypair=k, method="total_supply", args=args)

        logging.debug("results {}".format(res.value))

        return res.value['result']['Ok']['data']

class ERC20Observer:
    def __init__(self, address: str, substrate: SubstrateInterface, metadata: ContractMetadata, observer: ContractObserver):
        self.substrate = substrate
        self.contract_address = address
        self.metadata = metadata
        self.observer = observer

    @classmethod
    def create_from_address(cls, contract_address: str, metadata_file: str, substrate: SubstrateInterface):
        metadata = ContractMetadata.create_from_file(metadata_file, substrate=substrate)
        observer = ContractObserver(contract_address, metadata, substrate)
        return cls(address=contract_address, metadata=metadata, substrate=substrate, observer=observer)

    def scanEvents(self, from_num = None, to_num = None, on_transfer = None, on_approval = None):
        self.observer.scanEvents(from_num, to_num, {
            'Transfer': on_transfer,
            'Approve': on_approval
        })
