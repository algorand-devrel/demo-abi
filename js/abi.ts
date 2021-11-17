import algosdk from 'algosdk'

(async function(){
    const m = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

    const client = new algosdk.Algodv2(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 
        "http://127.0.0.1", 
        "4001"
    )

    const acct = algosdk.mnemonicToSecretKey(m)
    const appId = 27

    const sp = await client.getTransactionParams().do()

    const sum = new algosdk.ABIMethod({
        name:"add", args:[{type:"uint64"}, {type:"uint64"}], returns:{type:"uint64"}
    })
    const sub = new algosdk.ABIMethod({
        name:"sub", args:[{type:"uint64"}, {type:"uint64"}], returns:{type:"uint64"}
    })
    const mul = new algosdk.ABIMethod({
        name:"mul", args:[{type:"uint64"}, {type:"uint64"}], returns:{type:"uint64"}
    })

    const div = new algosdk.ABIMethod({
        name:"div", args:[{type:"uint64"}, {type:"uint64"}], returns:{type:"uint64"}
    })

    const qrem = new algosdk.ABIMethod({
        name:"qrem", args:[{type:"uint64"}, {type:"uint64"}], returns:{type:"(uint64,uint64)"}
    })

    const commonParams = {
        appID:appId,
        sender:acct.addr,
        suggestedParams:sp,
        signer: algosdk.makeBasicAccountTransactionSigner(acct)
    }

    const comp = new algosdk.AtomicTransactionComposer()

    comp.addMethodCall({
        method: sum, methodArgs: [1,1], ...commonParams
    })
    comp.addMethodCall({
        method: sub, methodArgs: [3,1], ...commonParams
    })
    comp.addMethodCall({
        method: div, methodArgs: [4,2], ...commonParams
    })
    comp.addMethodCall({
        method: mul, methodArgs: [3,3], ...commonParams
    })

    comp.addMethodCall({
        method: qrem, methodArgs: [27,5], ...commonParams
    })

    const result = await comp.execute(client, 2)

    for(const idx in result.methodResults){
        const r = result.methodResults[idx]
        console.log(r)
    }
})()
