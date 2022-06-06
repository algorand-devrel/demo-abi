Algorand AVM ABI
-----------------

Demo of implementation for contract and client code that conforms to the ARC4 spec.

https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0004.md


ARC-004 or the Algorand ABI is a specification for encoding and decoding of data types and a standard for handling method calls.

## Contents
    contract.py - A PyTEAL contract that generates a set of methods that can be called as ABI methods
    contract.json - A JSON file describing the interface of the contract to be read by SDK clients
    js/ - Directory containing a TypeScript client to read in the contract.json file and call methods
    py/ - Directory containing a Python client to read in the contract.json file and call methods
    go/ - Directory containing a Go client to read in the contract.json file and call methods
    goal/ - Directory containing goal commands to call methods directly from the commandline

## Development

Install the [sandbox](https://github.com/algorand/sandbox) to start a local private node and start it with the `dev` configuration.

If you're in the sandbox directory run:
```
./sandbox up dev
```

First make sure you have the correct version of [PyTEAL](https://github.com/algorand/pyteal) package installed.

This currently requires the `feature/abi` branch, you can run `pip install requirements.txt` to pull it down

Next, clone this repository and cd to the root directory.

Create the application:
Run `./manage.sh create` 
    This will create the teal source files in approval.teal and clear.teal, copy them to the sandbox, and call the create app transaction.
    It will print the newly created app id and cache it in a local file `.app_id` 
    you may have to modify the path to the sandbox shell script you've installed)

If you update the PyTEAL source:
Run `./manage.sh update`
    This will recreate the teal source files, copy them to the sandbox, and call the update app transaction.
    It will use the cached app id from `.app_id` 


Update the `contract.json` file by swapping in your new app id, then check the Language specific README files to see how to call the methods.

You'll also need to tweak the hostnames/ports for the algod client in their respective directories depending on how your local sandbox is configured.
