import algosdk from 'algosdk'
import * as fs from 'fs'

(async function(){
    const m = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

    const client = new algosdk.Algodv2(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 
        "http://127.0.0.1", 
        "4001"
    )

    
    const acct = algosdk.mnemonicToSecretKey(m)

    const buff = await fs.readFileSync("../interface.json")
    const contract = new algosdk.ABIContract( JSON.parse(buff.toString()))

    function getMethodByName(name: string): algosdk.ABIMethod  {
        const m = contract.methods.find((m)=>{ return m.name==name })
        if(m === undefined){
            return new algosdk.ABIMethod({name:"", args:[], returns:{type:"void"}})
        }
        return m
    }

    const sp = await client.getTransactionParams().do()

    const sum = getMethodByName("add")
    const sub = getMethodByName("sub")
    const mul = getMethodByName("mul")
    const div = getMethodByName("div")
    const qrem = getMethodByName("qrem")

    const commonParams = {
        appID:contract.appId,
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
