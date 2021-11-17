import algosdk from 'algosdk'

(async function a(){
    const m = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

    const client = new algosdk.Algodv2(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 
        "http://127.0.0.1", 
        "4001"
    )

    const acct = algosdk.mnemonicToSecretKey(m)
    const appId = 1

    const sp = await client.getTransactionParams().do()

    const addMethod = new algosdk.ABIMethod({
        name:"add", 
        args:[{type:"uint64"}, {type:"uint64"}], 
        returns:{type:"uint64"}
    })

    const comp = new algosdk.AtomicTransactionComposer()
    comp.addMethodCall({
        appID:appId,
        method: addMethod,
        methodArgs: [1,1],
        sender:acct.addr,
        suggestedParams:sp,
        signer: algosdk.makeBasicAccountTransactionSigner(acct)
    })

    const result = await comp.execute(client, 2)
    console.log(result)
})()
