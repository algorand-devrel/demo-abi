from algosdk import mnemonic
from algosdk.v2client.algod import *
from algosdk.atomic_transaction_composer import *
from algosdk.future.transaction import *
from algosdk.abi import *
from algosdk.mnemonic import *
from algosdk.account import *

client = AlgodClient("a" * 64, "http://localhost:4002")

with open("../contract.json") as f:
    js = f.read()

c = Contract.from_json(js)


def get_method(name: str) -> Method:
    for m in c.methods:
        if m.name == name:
            return m
    raise Exception("No method with that name")


mnemonic = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

sk = to_private_key(mnemonic)
addr = to_public_key(mnemonic)

signer = AccountTransactionSigner(sk)

sp = client.suggested_params()

comp = AtomicTransactionComposer()

# comp.add_method_call(c.app_id, get_method("add"), addr, sp, signer, method_args=[1,1])
# comp.add_method_call(c.app_id, get_method("sub"), addr, sp, signer, method_args=[3,1])
# comp.add_method_call(c.app_id, get_method("div"), addr, sp, signer, method_args=[4,2])
# comp.add_method_call(c.app_id, get_method("mul"), addr, sp, signer, method_args=[3,2])
# comp.add_method_call(c.app_id, get_method("qrem"), addr, sp, signer, method_args=[27,5])
# comp.add_method_call(c.app_id, get_method("reverse"), addr, sp, signer, method_args=["desrever yllufsseccus"])

# txn = TransactionWithSigner(PaymentTxn(addr, sp, addr, 10000), signer)
# comp.add_method_call(c.app_id, get_method("txntest"), addr, sp, signer, method_args=[10000, txn, 1000])

# comp.add_method_call(c.app_id, get_method("manyargs"), addr, sp, signer, method_args=[2]*20)

# comp.add_method_call(c.app_id, get_method("_closeOut"), addr, sp, signer, method_args=[1])
# comp.add_method_call(c.app_id, get_method("_optIn"), addr, sp, signer, method_args=[1])

comp.add_method_call(
    c.app_id,
    get_method("min_bal"),
    addr,
    sp,
    signer,
    method_args=["SKCBRBKPIGY5LI2OU63IE5LMNQ5BVVOKPHWTPPWFQOI4NG4TI35SLAA3JQ"],
)

# comp.add_method_call(
#    c.app_id,
#    get_method("concat_strings"),
#    addr,
#    sp,
#    signer,
#    method_args=[["this", "string", "is", "joined"]]
# )


txns = comp.build_group()

write_to_file([t.txn for t in txns], "tmp.txns")

resp = comp.execute(client, 2)

print(client.pending_transaction_info(resp.tx_ids[0]))

for result in resp.abi_results:
    print(result.return_value)
