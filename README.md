Algorand AVM ABI
-----------------

**This is a Work In Progress**
Some functionality is not yet supported by all the SDKs. Expect errors for now.

Demo of implementation for contract and client code that conforms to the ARC4 spec.

https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0004.md


ARC-004 or the Algorand ABI is a specification for encoding and decoding of data types and a standard for handling method calls.


## Contents
contract.py - A PyTEAL contract that generates a set of methods that can be called as ABI methods
contract.json - A JSON file describing the interface of the contract to be read by SDK clients
js/ - Directory containing a TypeScript client to read in the contract.json file and call methods
py/ - Directory containing a Python client to read in the contract.json file and call methods

