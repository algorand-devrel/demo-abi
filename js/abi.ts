import algosdk, { decodeAddress, Transaction } from 'algosdk'
import * as fs from 'fs' 
import {Buffer} from 'buffer'
import {getAccounts} from './sandbox'
import { isConstructorDeclaration } from 'typescript';

const algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const algod_host = "http://127.0.0.1";
const algod_port = "4001";

(async function(){

    // Create a client to communicate with local node
    const client = new algosdk.Algodv2(algod_token, algod_host, algod_port)
    
    // Get account from sandbox 
    const accounts = await getAccounts()
    const acct = accounts[0]

    // Read in the local contract.json file
    const buff = fs.readFileSync("../contract.json")

    // Parse the json file into an object, pass it to create an ABIContract object
    const contract = new algosdk.ABIContract(JSON.parse(buff.toString()))

    // Utility function to return an ABIMethod by its name
    function getMethodByName(name: string): algosdk.ABIMethod  {
        const m = contract.methods.find((mt: algosdk.ABIMethod)=>{ return mt.name==name })
        if(m === undefined)
            throw Error("Method undefined: "+name)
        return m
    }

    // We initialize the common parameters here, they'll be passed to all the transactions 
    // since they happen to be the same
    const sp = await client.getTransactionParams().do()
    const commonParams = {
        appID:contract.networks["default"].appID,
        sender:acct.addr,
        suggestedParams:sp,
        signer: algosdk.makeBasicAccountTransactionSigner(acct)
    }

    const comp = new algosdk.AtomicTransactionComposer()

    // Simple ABI Calls with standard arguments, return type
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

    //Tuple return type
    comp.addMethodCall({
        method: getMethodByName("qrem"), methodArgs: [27,5], ...commonParams
    })

    // String return type
    comp.addMethodCall({
        method: getMethodByName("reverse"), 
        methodArgs: [ Buffer.from("desrever yllufsseccus") ], 
        ...commonParams
    })

    // Transaction being passed as an argument, this removes the transaction from the 
    // args list, but includes it in the atomic grouped transaction
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

    // Here we call with 20 arguments to demonstrate Tuple encoding of any arguments past index 14
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

    // Pass in an account by address, the atc will take care of mapping this correctly
    comp.addMethodCall({
        method:getMethodByName("min_bal"),
        methodArgs:["FHWVNNZOALOSBKYFKEUIZC56SGPLLAREZFFWLXCPBBVVISXDLPTRFR7EIQ"],
        ...commonParams
    })

    // Dynamic argument types are supported (undefined length array)
    comp.addMethodCall({
        method: getMethodByName("concat_strings"),
        methodArgs: [["this", "string", "is", "joined"]],
        ...commonParams
    })
    
    // This is not necessary to call but it is helpful for debugging
    // to see what is being sent to the network
    const g = comp.buildGroup()
    console.log(g)
    for(const x in g){
        console.log(g[x].txn.appArgs)
    }

    const result = await comp.execute(client, 2)
    for(const idx in result.methodResults){
        console.log(result.methodResults[idx])
    }

})()
