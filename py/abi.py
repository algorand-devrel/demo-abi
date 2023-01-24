from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk.transaction import PaymentTxn, AssetCreateTxn
from algosdk.abi import Contract
from algosdk.logic import get_application_address

from sandbox import get_accounts

client = AlgodClient("a" * 64, "http://localhost:4001")


addr, sk = get_accounts()[0]

with open("../contract.json") as f:
    js = f.read()

with open("../.app_id") as f:
    app_id = int(f.read())

app_addr = get_application_address(app_id)

c = Contract.from_json(js)

signer = AccountTransactionSigner(sk)
sp = client.suggested_params()


box_comp = AtomicTransactionComposer()
box_name = b"cool_box"
box_comp.add_transaction(
    TransactionWithSigner(PaymentTxn(addr, sp, app_addr, 1_000_000_000), signer=signer),
)
box_comp.add_method_call(
    app_id,
    c.get_method_by_name("box_write"),
    addr,
    sp,
    signer,
    method_args=[box_name, (123, 456)],
    boxes=[(0, box_name)],
)
box_comp.add_method_call(
    app_id,
    c.get_method_by_name("box_read"),
    addr,
    sp,
    signer,
    method_args=[box_name],
    # technically not needed since we already ref it in
    # the previous txn in the same group
    boxes=[(0, box_name)],
)
result = box_comp.execute(client, 4)
print(f"box_read returned: {result.abi_results[-1].return_value}")


comp = AtomicTransactionComposer()

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

# Useable with abi_types.py contract
# comp.add_method_call(
#     app_id,
#     c.get_method_by_name("concat_dynamic_arrays"),
#     addr,
#     sp,
#     signer,
#     method_args=[[1, 2, 3], [4, 5, 6]],
# )
#
# comp.add_method_call(
#     app_id,
#     c.get_method_by_name("concat_static_arrays"),
#     addr,
#     sp,
#     signer,
#     method_args=[[1, 2, 3], [4, 5, 6]],
# )
#
#
# comp.add_method_call(
#     app_id,
#     c.get_method_by_name("concat_dynamic_string_arrays"),
#     addr,
#     sp,
#     signer,
#     method_args=[["a", "b", "c"], ["d", "e", "f"]],
# )


# drr = comp.dryrun(client)
# for txn in drr.trace.txns:
#    if txn.app_call_rejected():
#        print(txn.app_trace())

resp = comp.execute(client, 2)
for result in resp.abi_results:
    # print(result.decode_error)
    # print(result.raw_value.hex())
    print(f"{result.method.name} => {result.return_value}")
