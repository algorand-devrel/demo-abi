JavaScript ABI Demo
-------------------

This directory contains a single code file, `abi.ts`.

In it is a demonstration of the use of the SDK methods used to interact with the Algorand ABI.

Make sure you've run the items mentioned in the root README

Install dependencies for this demo
```sh
npm install
```

TODO: provide methods to pull funded accts 
Change the hardcoded mnemonic to a funded account in your sandbox (`sandbox goal account export -a $ADDR`)

run `npx ts-node abi.ts`

This should print out some logs about what its doing.  

Currently (12/1/21) the JS SDK does not support foreign types in ABI method calls.

Happy Hacking :)