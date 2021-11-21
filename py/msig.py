from algosdk.v2client.algod import AlgodClient
from algosdk.future.transaction import Multisig, MultisigTransaction
from algosdk.account import generate_account
from algosdk.future.transaction import PaymentTxn
from algosdk.atomic_transaction_composer import (
    MultisigTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)

client = AlgodClient("a" * 64, "http://localhost:4001")

sk1, addr1 = generate_account()
sk2, addr2 = generate_account()

msig = Multisig(1, 2, [addr1, addr2])

sp = client.suggested_params()

comp = AtomicTransactionComposer()
comp.add_transaction(
    TransactionWithSigner(
        PaymentTxn(msig.address(), sp, addr1, 100000),
        MultisigTransactionSigner(msig, [sk1, sk2]),
    )
)

print(comp.execute(client, 2))
