# Himalia PatractPy

Substrate Contract SDK for Python As a part of Himalia

----------

PatractPy is a contract SDK to support the development of Python scripts that interact with contracts, including automated scripts to support testing. Unlike PatractGo, PatractPy is mainly for script development, so PatractPy mainly completes contract-related RPC interfaces, and completes contract deployment and instantiation-related operations. At the same time, PatractPy will implement PatractGo-based interaction and contract status monitoring support.

PatractPy will be based on [polkascan's Python Substrate Interface](https://github.com/polkascan/py-substrate-interface), which is a Go sdk for Substrate.

Element Group for disscusion: https://app.element.io/#/room/#PatractLabsDev:matrix.org

PatractPy will achieve the following support:

- Some support that missing in [polkascan's Python Substrate Interface](https://github.com/polkascan/py-substrate-interface), which is needed for contracts
- Provide Scanning and monitoring support for contract to do statistics and analysis
- Provide a SDK development example for ERC20 contract
- Support For unittest to canvas or [europa](https://github.com/patractlabs/europa) env.

## Basic Apis For Contracts

As [polkascan's Python Substrate Interface](https://github.com/polkascan/py-substrate-interface) has provide some support to contract api, so we not need to important the api for contract calls, but there is some api to add:

- `SubstrateSubscriber` is a subscriber support to subscribe data changes in chain, for example, the events in chain.
- `get_contract_event_type` add event decode support for contracts.

## ContractObserver

ContractObserver can observer events for a contract:

```python
substrate=SubstrateInterface(url="ws://127.0.0.1:9944", type_registry_preset='canvas')
contract_metadata = ContractMetadata.create_from_file(
    metadata_file=os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json'),
    substrate=substrate
)
observer = ContractObserver("0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48", contract_metadata, substrate)

# for some handlers
observer.scanEvents()
```

The handler function can take the erc20 support as a example.

## ERC20 API

ERC20 api provide a wapper to erc20 contract exec, read and observer events, it can be a example for contracts api calling.

```python

# init api
substrate=SubstrateInterface(url="ws://127.0.0.1:9944", type_registry_preset='canvas')

contract_metadata = ContractMetadata.create_from_file(
    metadata_file=os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json'),
    substrate=substrate
)

alice = Keypair.create_from_uri('//Alice')
bob = Keypair.create_from_uri('//Bob')

# erc20 api
erc20 = ERC20.create_from_contracts(
    substrate= substrate, 
    contract_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.wasm'),
    metadata_file= os.path.join(os.path.dirname(__file__), 'constracts', 'ink', 'erc20.json')
)

# deplay a erc20 contract
erc20.putAndDeploy(alice, 1000000 * (10 ** 15))

# read total supply
total_supply = erc20.totalSupply()

# transfer
erc20.transferFrom(alice,
    fromAcc=alice.ss58_address, 
    toAcc=bob.ss58_address, 
    amt=10000)

erc20.transfer(alice, bob.ss58_address, 10000)

# get balance
alice_balance = erc20.balanceOf(alice.ss58_address)

# approve
erc20.approve(alice, spender=bob.ss58_address, amt=10000)

# get allowance
alice_allowance = erc20.allowance(alice.ss58_address, bob.ss58_address)

```
