import algosdk from 'algosdk'
import * as fs from 'fs' 
import {Buffer} from 'buffer'

(async function(){
    const m = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

    const client = new algosdk.Algodv2(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 
        "http://127.0.0.1", 
        "4001"
    )
    
    const acct = algosdk.mnemonicToSecretKey(m)

    const buff = fs.readFileSync("../interface.json")
    const contract = new algosdk.ABIContract( JSON.parse(buff.toString()))

    function getMethodByName(name: string): algosdk.ABIMethod  {
        const m = contract.methods.find((mt: algosdk.ABIMethod)=>{ return mt.name==name })
        if(m === undefined)
            throw Error("Method undefined")
        return m
    }

    const sum   = getMethodByName("add")
    const sub   = getMethodByName("sub")
    const mul   = getMethodByName("mul")
    const div   = getMethodByName("div")
    const qrem  = getMethodByName("qrem")

    const reverse  = getMethodByName("reverse")


    const sp = await client.getTransactionParams().do()
    const commonParams = {
        appID:contract.appId,
        sender:acct.addr,
        suggestedParams:sp,
        signer: algosdk.makeBasicAccountTransactionSigner(acct)
    }

    const comp = new algosdk.AtomicTransactionComposer()

    //comp.addMethodCall({
    //    method: sum, methodArgs: [1,1], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: sub, methodArgs: [3,1], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: div, methodArgs: [4,2], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: mul, methodArgs: [3,3], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: qrem, methodArgs: [27,5], ...commonParams
    //})

    comp.addMethodCall({
        method: reverse, 
        methodArgs: [
            Buffer.from("reverse me please")
        ], 
        ...commonParams
    })

    const gtxn = comp.buildGroup()
    for(const idx in gtxn){
        const t =gtxn[idx]
        console.log(t.txn.appArgs)
    }

    const result = await comp.execute(client, 2)

    for(const idx in result.methodResults){
        const r = result.methodResults[idx]
        console.log(r)
    }

})()
