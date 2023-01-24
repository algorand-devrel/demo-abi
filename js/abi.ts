import algosdk, {
  decodeAddress,
  makePaymentTxnWithSuggestedParamsFromObject,
  Transaction,
} from "algosdk";
import * as fs from "fs";
import { Buffer } from "buffer";
import { getAccounts } from "./sandbox";

const algod_token =
  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const algod_host = "http://127.0.0.1";
const algod_port = "4001";

(async function () {
  // Create a client to communicate with local node
  const client = new algosdk.Algodv2(algod_token, algod_host, algod_port);

  // Get account from sandbox
  const accounts = await getAccounts();
  const acct = accounts[0];

  // Read in the local contract.json file
  const buff = fs.readFileSync("../contract.json");

  // Parse the json file into an object, pass it to create an ABIContract object
  const contract = new algosdk.ABIContract(JSON.parse(buff.toString()));

  // Get the app id for the app we created with `./manage.sh` earlier
  const appId = parseInt(fs.readFileSync("../.app_id").toString());

  // Get sp once, we'll reuse it
  const sp = await client.getTransactionParams().do();

  // Fund the app address so it can create boxes
  const ptxn = makePaymentTxnWithSuggestedParamsFromObject({
    from: acct.addr,
    suggestedParams: sp,
    to: algosdk.getApplicationAddress(appId),
    amount: 1_000_000_000,
  }).signTxn(acct.sk);
  await client.sendRawTransaction(ptxn).do();

  // We initialize the common parameters here, they'll be passed to all the transactions
  // since they happen to be the same
  const commonParams = {
    appID: appId,
    sender: acct.addr,
    suggestedParams: sp,
    signer: algosdk.makeBasicAccountTransactionSigner(acct),
  };

  // Write then read a box
  const boxComp = new algosdk.AtomicTransactionComposer();
  const boxName = new Uint8Array(Buffer.from("cool_box"));
  boxComp.addMethodCall({
    method: contract.getMethodByName("box_write"),
    methodArgs: [boxName, [123, 456]],
    boxes: [{ appIndex: 0, name: boxName }],
    ...commonParams,
  });
  boxComp.addMethodCall({
    method: contract.getMethodByName("box_read"),
    methodArgs: [boxName],
    boxes: [{ appIndex: 0, name: boxName }],
    ...commonParams,
  });
  const boxResult = await boxComp.execute(client, 4);
  console.log("Box contents: ", boxResult.methodResults[1].returnValue);

  // Simple ABI Calls with standard arguments, return type
  const comp = new algosdk.AtomicTransactionComposer();
  comp.addMethodCall({
    method: contract.getMethodByName("add"),
    methodArgs: [1, 1],
    ...commonParams,
  });
  comp.addMethodCall({
    method: contract.getMethodByName("sub"),
    methodArgs: [3, 1],
    ...commonParams,
  });
  comp.addMethodCall({
    method: contract.getMethodByName("div"),
    methodArgs: [4, 2],
    ...commonParams,
  });
  comp.addMethodCall({
    method: contract.getMethodByName("mul"),
    methodArgs: [3, 3],
    ...commonParams,
  });

  //Tuple return type
  comp.addMethodCall({
    method: contract.getMethodByName("qrem"),
    methodArgs: [27, 5],
    ...commonParams,
  });

  // String return type
  comp.addMethodCall({
    method: contract.getMethodByName("reverse"),
    methodArgs: [Buffer.from("desrever yllufsseccus")],
    ...commonParams,
  });

  // Transaction being passed as an argument, this removes the transaction from the
  // args list, but includes it in the atomic grouped transaction
  comp.addMethodCall({
    method: contract.getMethodByName("txntest"),
    methodArgs: [
      10000,
      {
        txn: new Transaction({
          from: acct.addr,
          to: acct.addr,
          amount: 10000,
          ...sp,
        }),
        signer: algosdk.makeBasicAccountTransactionSigner(acct),
      },
      1000,
    ],
    ...commonParams,
  });

  // Here we call with 20 arguments to demonstrate Tuple encoding of any arguments past index 14
  comp.addMethodCall({
    method: contract.getMethodByName("manyargs"),
    methodArgs: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ...commonParams,
  });

  // Pass in an account by address, the atc will take care of mapping this correctly
  comp.addMethodCall({
    method: contract.getMethodByName("min_bal"),
    methodArgs: ["FHWVNNZOALOSBKYFKEUIZC56SGPLLAREZFFWLXCPBBVVISXDLPTRFR7EIQ"],
    ...commonParams,
  });

  // Dynamic argument types are supported (undefined length array)
  comp.addMethodCall({
    method: contract.getMethodByName("concat_strings"),
    methodArgs: [["this", "string", "is", "joined"]],
    ...commonParams,
  });

  // This is not necessary to call but it is helpful for debugging
  // to see what is being sent to the network
  //for(const gtxn of comp.buildGroup()){ console.log(gtxn.txn.appArgs) }

  // We can also dryrun the group
  // const res = await comp.dryrun(client)
  // for(const tx of res.methodResults){ console.log(tx.returnValue) }

  // Finally, execute the composed group and print out the results
  const results = await comp.execute(client, 2);
  for (const result of results.methodResults) {
    console.log(`${result.method.name} => ${result.returnValue}`);
  }
})();
