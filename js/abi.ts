import algosdk, { decodeAddress, Transaction } from 'algosdk'
import * as fs from 'fs' 
import {Buffer} from 'buffer'

(async function(){
    const m = "train pause genre sound energy sorry ketchup purse urban lobster until engage ordinary furnace media clown sure goddess genuine pioneer nephew maximum vivid absorb silk"
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
            throw Error("Method undefined: "+name)
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

    comp.addMethodCall({
        method: getMethodByName("add"), methodArgs: [1,1], ...commonParams
    })
    comp.addMethodCall({
        method: getMethodByName("sub"), methodArgs: [3,1], ...commonParams
    })

    comp.addMethodCall({
        method: getMethodByName("div"), methodArgs: [4,2], ...commonParams
    })
    comp.addMethodCall({
        method: getMethodByName("mul"), methodArgs: [3,3], ...commonParams
    })
    //comp.addMethodCall({
    //    method: getMethodByName("qrem"), methodArgs: [27,5], ...commonParams
    //})

    comp.addMethodCall({
        method: getMethodByName("reverse"), 
        methodArgs: [ Buffer.from("desrever yllufsseccus") ], 
        ...commonParams
    })

    comp.addMethodCall({
        method: getMethodByName("txntest"), 
        methodArgs: [
            10000,
            {
                txn: new Transaction({
                    from: acct.addr,
                    to: acct.addr,
                    amount: 10000,
                    ...sp
                }),
                signer: algosdk.makeBasicAccountTransactionSigner(acct)
            },
            1000
        ], 
        ...commonParams
    })

    comp.addMethodCall({
        method: getMethodByName("manyargs"),
        methodArgs:[
            1,1,1,1,1,
            1,1,1,1,1,
            1,1,1,1,1,
            1,1,1,1,1
        ],
        ...commonParams
    })

    //comp.addMethodCall({
    //    method:getMethodByName("min_bal"),
    //    methodArgs:["FHWVNNZOALOSBKYFKEUIZC56SGPLLAREZFFWLXCPBBVVISXDLPTRFR7EIQ"],
    //    ...commonParams
    //})

    //comp.addMethodCall({
    //    method: getMethodByName("concat_strings"),
    //    methodArgs: [["this", "string", "is", "joined"]],
    //    ...commonParams
    //})
    
    const g = comp.buildGroup()
    console.log(g)
    for(const x in g){
        console.log(g[x].txn.appArgs)
    }


    const result = await comp.execute(client, 2)

    for(const idx in result.methodResults){
        const r = result.methodResults[idx]
        console.log(r)
    }

})()
