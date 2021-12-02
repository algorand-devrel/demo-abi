package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"

	"github.com/algorand/go-algorand-sdk/client/v2/algod"
	"github.com/algorand/go-algorand-sdk/crypto"
	"github.com/algorand/go-algorand-sdk/future"
	"github.com/algorand/go-algorand-sdk/mnemonic"
	"github.com/algorand/go-algorand-sdk/types"
)

var (
	host  = "http://localhost"
	port  = "4002"
	token = strings.Repeat("a", 64)

	m = "train pause genre sound energy sorry ketchup purse urban lobster until engage ordinary furnace media clown sure goddess genuine pioneer nephew maximum vivid absorb silk"
)

func main() {
	client, err := algod.MakeClient(fmt.Sprintf("%s:%s", host, port), token)
	if err != nil {
		log.Fatalf("Failed to init client: %+v", err)
	}

	sk, err := mnemonic.ToPrivateKey(m)
	if err != nil {
		log.Fatalf("Failed to get pk from mnemonic: %+v", err)
	}

	acct, err := crypto.AccountFromPrivateKey(sk)
	if err != nil {
		log.Fatalf("Failed to generate acct from sk: %+v", err)
	}

	f, err := os.Open("../contract.json")
	if err != nil {
		log.Fatalf("Failed to open contract file: %+v", err)
	}

	b, err := ioutil.ReadAll(f)
	if err != nil {
		log.Fatalf("Failed to read file: %+v", err)
	}

	contract := &future.Contract{}
	if err := json.Unmarshal(b, contract); err != nil {
		log.Fatalf("Failed to marshal contract: %+v", err)
	}

	sp, err := client.SuggestedParams().Do(context.Background())
	if err != nil {
		log.Fatalf("Failed to get suggeted params: %+v", err)
	}

	signer := future.BasicAccountTransactionSigner{Account: acct}

	mcp := future.AddMethodCallParams{
		AppID:           contract.AppId,
		Sender:          acct.Address,
		SuggestedParams: sp,
		OnComplete:      types.NoOpOC,
	}

	// Skipping error checks below during AddMethodCall and txn create
	atc := future.MakeAtomicTransactionComposer()

	// Uint32 args/return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "add"), []interface{}{1, 1}), signer)
	atc.AddMethodCall(combine(mcp, getMethod(contract, "sub"), []interface{}{3, 1}), signer)
	atc.AddMethodCall(combine(mcp, getMethod(contract, "mul"), []interface{}{3, 2}), signer)
	atc.AddMethodCall(combine(mcp, getMethod(contract, "div"), []interface{}{4, 2}), signer)

	// Uint64 args, (Uint64,Uint64) return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "qrem"), []interface{}{27, 5}), signer)

	// String arg/return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "reverse"),
		[]interface{}{"desrever yllufsseccus"}), signer)

	// []string arg, string return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "concat_strings"),
		[]interface{}{[]string{"this", "string", "is", "joined"}}), signer)

	// Txn arg, uint return
	txn, _ := future.MakePaymentTxn(acct.Address.String(), acct.Address.String(), 10000, nil, "", sp)
	stxn := future.TransactionWithSigner{
		Txn:    txn,
		Signer: signer,
	}
	atc.AddMethodCall(combine(mcp, getMethod(contract, "txntest"),
		[]interface{}{10000, stxn, 1000}), signer)

	// >14 args, so they get tuple encoded automatically
	err = atc.AddMethodCall(combine(mcp, getMethod(contract, "manyargs"),
		[]interface{}{
			1, 1, 1, 1, 1,
			1, 1, 1, 1, 1,
			1, 1, 1, 1, 1,
			1, 1, 1, 1, 1,
		}), signer)

	if err != nil {
		log.Fatalf("Failed to add method call: %+v", err)
	}

	_, _, ret, err := atc.Execute(client, context.Background(), 2)
	if err != nil {
		log.Fatalf("Failed to execute call: %+v", err)
	}

	for _, r := range ret {
		log.Printf("%s returned %+v", r.TxID, r.ReturnValue)
	}
}

func getMethod(c *future.Contract, name string) (m future.Method) {
	for _, m = range c.Methods {
		if m.Name == name {
			return
		}
	}
	log.Fatalf("No method named: %s", name)
	return
}

func combine(mcp future.AddMethodCallParams, m future.Method, a []interface{}) future.AddMethodCallParams {
	mcp.Method = m
	mcp.MethodArgs = a
	return mcp
}
