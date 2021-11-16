import algosdk from 'algosdk'
import { makeBasicAccountTransactionSigner } from 'algosdk/dist/types/src/signer'


(async function(){
    const client = new algosdk.Algodv2({
        token:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 
        baseServer:"http://localhost", 
        port:"4001"
    })

    const acct = algosdk.generateAccount()

    const sp = await client.getTransactionParams().do()

    const addMethod = new algosdk.ABIMethod({
        name:"add", 
        args:[{type:"uint64"}, {type:"uint64"}], 
        returns:{type:"uint64"}
    })

    const appId = 0
    const comp = new algosdk.AtomicTransactionComposer()
    comp.addMethodCall({
        appID:appId,
        method: addMethod,
        methodArgs: [1,1],
        sender:acct.addr,
        suggestedParams:sp,
        signer: makeBasicAccountTransactionSigner(acct)
    })

    const result = await comp.execute(client, 2)
    console.log(result)
})()