from algosdk import mnemonic
from algosdk.v2client.algod import *
from algosdk.future.atomic_transaction_composer import *
from algosdk.future.transaction import *
from algosdk.abi import * 
from algosdk.mnemonic import *
from algosdk.account import *

client = AlgodClient("a"*64, "http://localhost:4001")

with open("../contract.json") as f:
    js = f.read()

c = Contract.from_json(js)

def get_method(c: Contract, name: str)->Method:
    for m in c.methods:
        if m.name == name:
            return m
    raise Exception("No method with that name")



mnemonic = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

sk   = to_private_key(mnemonic)
addr = to_public_key(mnemonic)

sum     = get_method(c, "add")
sub     = get_method(c, "sub")
div     = get_method(c, "div")
mul     = get_method(c, "mul")
qrem    = get_method(c, "qrem")
reverse = get_method(c, "reverse")
txntest = get_method(c, "txntest")


signer = AccountTransactionSigner(sk)

sp = client.suggested_params()

comp = AtomicTransactionComposer()
comp.add_method_call(c.app_id, sum, addr, sp, signer, method_args=[1,1])
comp.add_method_call(c.app_id, sub, addr, sp, signer, method_args=[3,1])
comp.add_method_call(c.app_id, div, addr, sp, signer, method_args=[4,2])
comp.add_method_call(c.app_id, mul, addr, sp, signer, method_args=[3,2])
comp.add_method_call(c.app_id, qrem, addr, sp, signer, method_args=[27,5])
comp.add_method_call(c.app_id, reverse, addr, sp, signer, method_args=["desrever yllufsseccus"])

txn = TransactionWithSigner(PaymentTxn(addr, sp, addr, 10000), signer)
comp.add_method_call(c.app_id, txntest, addr, sp, signer, method_args=[10000, txn, 1000])

resp = comp.execute(client, 2)

for result in resp.abi_results:
    print(result.return_value)

#    const sp = await client.getTransactionParams().do()
#    const commonParams = {
#        appId:contract.appId,
#        sender:acct.addr,
#        suggestedParams:sp,
#        signer: algosdk.makeBasicAccountTransactionSigner(acct)
#    }
#
#    const comp = new algosdk.AtomicTransactionComposer()
#
#    comp.addMethodCall({
#        method: sum, methodArgs: [1,1], ...commonParams
#    })
#    comp.addMethodCall({
#        method: sub, methodArgs: [3,1], ...commonParams
#    })
#    comp.addMethodCall({
#        method: div, methodArgs: [4,2], ...commonParams
#    })
#    comp.addMethodCall({
#        method: mul, methodArgs: [3,3], ...commonParams
#    })
#    comp.addMethodCall({
#        method: qrem, methodArgs: [27,5], ...commonParams
#    })
#
#    comp.addMethodCall({
#        method: reverse, 
#        methodArgs: [
#            Buffer.from("desrever yllufsseccus")
#        ], 
#        ...commonParams
#    })
#
#    comp.addMethodCall({
#        method: txntest, 
#        methodArgs: [
#            10000,
#            {
#                txn: new Transaction({
#                    from: acct.addr,
#                    to: acct.addr,
#                    amount: 10000,
#                    ...sp
#                }),
#                signer: algosdk.makeBasicAccountTransactionSigner(acct)
#            },
#            1000
#        ], 
#        ...commonParams
#    })
#
#
#print(comp)