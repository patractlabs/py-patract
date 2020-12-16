# Himalia PatractPy

Substrate Contract SDK for Python As a part of Himalia

----------

PatractPy is a contract SDK to support the development of Python scripts that interact with contracts, including automated scripts to support testing. Unlike PatractGo, PatractPy is mainly for script development, so PatractPy mainly completes contract-related RPC interfaces, and completes contract deployment and instantiation-related operations. At the same time, PatractPy will implement PatractGo-based interaction and contract status monitoring support.

PatractPy will be based on [polkascan's Python Substrate Interface](https://github.com/polkascan/py-substrate-interface), which is a Go sdk for Substrate.

Element Group for disscusion: https://app.element.io/#/room/#PatractLabsDev:matrix.org

PatractPy will achieve the following support:

- Complete the secondary packaging of the contract module interface, complete operations such as put_code, call, instantiate, etc.
- Contract-based metadata information and contract interaction
- Based on PatractGo, provide HTTP service for contract-based metadata information and contract interaction
- Based on PatractGo, provide Scanning and monitoring support for contract to do statistics and analysis
- Provide a SDK development example for ERC20 contract
