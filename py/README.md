Python ABI Demo
-------------------

This directory contains a single code file, `abi.py`.

In it is a demonstration of the use of the SDK methods used to interact with the Algorand ABI.

Make sure you've run the items mentioned in the root README

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

TODO: provide methods to pull funded accts 
Change the hardcoded mnemonic to a funded account in your sandbox (`sandbox goal account export -a $ADDR`)

run `python3 abi.py`

This should print out some logs about what its doing.  

Happy hacking :)