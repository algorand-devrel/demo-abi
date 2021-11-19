import algosdk, { decodeAddress, Transaction } from 'algosdk'
import * as fs from 'fs' 
import {Buffer} from 'buffer'

(async function(){
    const m = "hobby other dilemma add wool nurse insane cinnamon doctor swarm fan same usage sock mirror clever mention situate reason subject curtain tired flat able hunt"

    const client = new algosdk.Algodv2(
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 
        "http://127.0.0.1", 
        "4002"
    )
    
    const acct = algosdk.mnemonicToSecretKey(m)

    const buff = fs.readFileSync("../contract.json")
    const contract = new algosdk.ABIContract( JSON.parse(buff.toString()))

    function getMethodByName(name: string): algosdk.ABIMethod  {
        const m = contract.methods.find((mt: algosdk.ABIMethod)=>{ return mt.name==name })
        if(m === undefined)
            throw Error("Method undefined")
        return m
    }

    const sp = await client.getTransactionParams().do()
    const commonParams = {
        appId:contract.appId,
        sender:acct.addr,
        suggestedParams:sp,
        signer: algosdk.makeBasicAccountTransactionSigner(acct)
    }

    const comp = new algosdk.AtomicTransactionComposer()

    //comp.addMethodCall({
    //    method: getMethodByName("add"), methodArgs: [1,1], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: getMethodByName("sub"), methodArgs: [3,1], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: getMethodByName("div"), methodArgs: [4,2], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: getMethodByName("mul"), methodArgs: [3,3], ...commonParams
    //})
    //comp.addMethodCall({
    //    method: getMethodByName("qrem"), methodArgs: [27,5], ...commonParams
    //})

    //comp.addMethodCall({
    //    method: getMethodByName("reverse"), 
    //    methodArgs: [ Buffer.from("desrever yllufsseccus") ], 
    //    ...commonParams
    //})

    //comp.addMethodCall({
    //    method: txntest, 
    //    methodArgs: [
    //        10000,
    //        {
    //            txn: new Transaction({
    //                from: acct.addr,
    //                to: acct.addr,
    //                amount: 10000,
    //                ...sp
    //            }),
    //            signer: algosdk.makeBasicAccountTransactionSigner(acct)
    //        },
    //        1000
    //    ], 
    //    ...commonParams
    //})

    //comp.addMethodCall({
    //    method: getMethodByName("manyargs"),
    //    methodArgs:[
    //        1,1,1,1,1,
    //        1,1,1,1,1,
    //        1,1,1,1,1,
    //        1,1,1,1,1
    //    ],
    //    ...commonParams
    //})

    //comp.addMethodCall({
    //    method: getMethodByName("_closeOut"),
    //    methodArgs: [1], 
    //    onComplete: algosdk.OnApplicationComplete.CloseOutOC,
    //    ...commonParams
    //})

    //comp.addMethodCall({
    //    method: getMethodByName("_optIn"),
    //    methodArgs: [1], 
    //    onComplete: algosdk.OnApplicationComplete.OptInOC,
    //    ...commonParams
    //})

    //comp.addMethodCall({
    //    method:getMethodByName("min_bal"),
    //    methodArgs:["FHWVNNZOALOSBKYFKEUIZC56SGPLLAREZFFWLXCPBBVVISXDLPTRFR7EIQ"],
    //    ...commonParams
    //})

    const group = comp.buildGroup()
    for(const idx in group){
        console.log(group[idx].txn)
    }

    const result = await comp.execute(client, 2)

    for(const idx in result.methodResults){
        const r = result.methodResults[idx]
        console.log(r)
    }

})()
