import os

from substrateinterface import SubstrateInterface, ContractMetadata, ContractCode, Keypair
from substrateinterface.exceptions import SubstrateRequestException


class ContractObserver:
    def __init__(self, contract_address: str, metadata: ContractMetadata = None, substrate: SubstrateInterface = None):
        self.substrate = substrate
        self.contract_address = contract_address
        self.metadata = metadata

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