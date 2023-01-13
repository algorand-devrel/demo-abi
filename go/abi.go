package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"strconv"
	"strings"

	"github.com/algorand/go-algorand-sdk/abi"
	"github.com/algorand/go-algorand-sdk/client/v2/algod"
	"github.com/algorand/go-algorand-sdk/future"
	"github.com/algorand/go-algorand-sdk/types"
)

var (
	host  = "http://localhost"
	port  = "4001"
	token = strings.Repeat("a", 64)
)

func main() {
	client, err := algod.MakeClient(fmt.Sprintf("%s:%s", host, port), token)
	if err != nil {
		log.Fatalf("Failed to init client: %+v", err)
	}

	block, err := client.Block(1886).Do(context.Background())
	if err != nil {
		log.Fatalf("FAIL: %+v", err)
	}
	for _, stxn := range block.Payset {
		for _, l := range stxn.EvalDelta.Logs {
			log.Printf("%+v", []byte(l))
		}
	}

	return

	accts, err := GetAccounts()
	if err != nil {
		log.Fatalf("Failed to get accounts: %+v", err)
	}

	acct := accts[0]

	b, err := ioutil.ReadFile("../contract.json")
	if err != nil {
		log.Fatalf("Failed to open contract file: %+v", err)
	}
	contract := &abi.Contract{}
	if err := json.Unmarshal(b, contract); err != nil {
		log.Fatalf("Failed to marshal contract: %+v", err)
	}

	b, err = ioutil.ReadFile("../.app_id")
	if err != nil {
		log.Fatalf("Failed to open app id file: %+v", err)
	}

	// Parse the app id, removing the newline
	app_id, err := strconv.ParseUint(string(b[:len(b)-1]), 10, 64)
	if err != nil {
		log.Fatalf("Failed to parse int: %+v", err)
	}

	sp, err := client.SuggestedParams().Do(context.Background())
	if err != nil {
		log.Fatalf("Failed to get suggeted params: %+v", err)
	}

	signer := future.BasicAccountTransactionSigner{Account: acct}

	mcp := future.AddMethodCallParams{
		AppID:           app_id,
		Sender:          acct.Address,
		SuggestedParams: sp,
		OnComplete:      types.NoOpOC,
		Signer:          signer,
	}

	// Skipping error checks below during AddMethodCall and txn create
	var atc = future.AtomicTransactionComposer{}

	// /// Uint32 args/return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "add"), []interface{}{1, 1}))
	atc.AddMethodCall(combine(mcp, getMethod(contract, "sub"), []interface{}{3, 1}))
	atc.AddMethodCall(combine(mcp, getMethod(contract, "mul"), []interface{}{3, 2}))
	atc.AddMethodCall(combine(mcp, getMethod(contract, "div"), []interface{}{4, 2}))

	// // Uint64 args, (Uint64,Uint64) return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "qrem"), []interface{}{27, 5}))

	// // String arg/return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "reverse"), []interface{}{"desrever yllufsseccus"}))

	// []string arg, string return
	atc.AddMethodCall(combine(mcp, getMethod(contract, "concat_strings"), []interface{}{[]string{"this", "string", "is", "joined"}}))

	// Txn arg, uint return
	txn, _ := future.MakePaymentTxn(acct.Address.String(), acct.Address.String(), 10000, nil, "", sp)
	stxn := future.TransactionWithSigner{Txn: txn, Signer: signer}
	atc.AddMethodCall(combine(mcp, getMethod(contract, "txntest"), []interface{}{10000, stxn, 1000}))

	// >14 args, so they get tuple encoded automatically
	err = atc.AddMethodCall(combine(mcp, getMethod(contract, "manyargs"),
		[]interface{}{
			1, 1, 1, 1, 1,
			1, 1, 1, 1, 1,
			1, 1, 1, 1, 1,
			1, 1, 1, 1, 1,
		}))

	if err != nil {
		log.Fatalf("Failed to add method call: %+v", err)
	}

	ret, err := atc.Execute(client, context.Background(), 2)
	if err != nil {
		log.Fatalf("Failed to execute call: %+v", err)
	}

	for _, r := range ret.MethodResults {
		log.Printf("%+v", r.TransactionInfo.Logs)
		log.Printf("%s returned %+v", r.Method.Name, r.ReturnValue)
	}
}

func getMethod(c *abi.Contract, name string) abi.Method {
	m, err := c.GetMethodByName(name)
	if err != nil {
		log.Fatalf("No method named: %s", name)
	}
	return m
}

func combine(mcp future.AddMethodCallParams, m abi.Method, a []interface{}) future.AddMethodCallParams {
	mcp.Method = m
	mcp.MethodArgs = a
	return mcp
}
