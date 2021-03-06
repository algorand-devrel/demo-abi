from algosdk import mnemonic
from algosdk.v2client.algod import *
from algosdk.atomic_transaction_composer import *
from algosdk.future.transaction import *
from algosdk.abi import *
from algosdk.mnemonic import *
from algosdk.account import *

from sandbox import get_accounts

client = AlgodClient("a" * 64, "http://localhost:4001")

with open("../contract.json") as f:
    js = f.read()

with open("../.app_id") as f:
    app_id = int(f.read())

c = Contract.from_json(js)

addr, sk = get_accounts()[0]
signer = AccountTransactionSigner(sk)

comp = AtomicTransactionComposer()

sp = client.suggested_params()
comp.add_method_call(
    app_id, c.get_method_by_name("add"), addr, sp, signer, method_args=[1, 1]
)
comp.add_method_call(
    app_id, c.get_method_by_name("sub"), addr, sp, signer, method_args=[3, 1]
)
comp.add_method_call(
    app_id, c.get_method_by_name("div"), addr, sp, signer, method_args=[4, 2]
)
comp.add_method_call(
    app_id, c.get_method_by_name("mul"), addr, sp, signer, method_args=[3, 2]
)
comp.add_method_call(
    app_id, c.get_method_by_name("qrem"), addr, sp, signer, method_args=[27, 5]
)

comp.add_method_call(
    app_id,
    c.get_method_by_name("reverse"),
    addr,
    sp,
    signer,
    method_args=["desrever yllufsseccus"],
)

ptxn = TransactionWithSigner(PaymentTxn(addr, sp, addr, 10000), signer)
comp.add_method_call(
    app_id,
    c.get_method_by_name("txntest"),
    addr,
    sp,
    signer,
    method_args=[10000, ptxn, 1000],
)

comp.add_method_call(
    app_id, c.get_method_by_name("manyargs"), addr, sp, signer, method_args=[2] * 20
)


comp.add_method_call(
    app_id,
    c.get_method_by_name("min_bal"),
    addr,
    sp,
    signer,
    method_args=["SKCBRBKPIGY5LI2OU63IE5LMNQ5BVVOKPHWTPPWFQOI4NG4TI35SLAA3JQ"],
)

comp.add_method_call(
    app_id,
    c.get_method_by_name("concat_strings"),
    addr,
    sp,
    signer,
    method_args=[["this", "string", "is", "joined"]],
)

# drr = comp.dryrun(client)
# for txn in drr.trace.txns:
#    if txn.app_call_rejected():
#        print(txn.app_trace())

resp = comp.execute(client, 2)
for result in resp.abi_results:
    print(f"{result.method.name} => {result.return_value}")
