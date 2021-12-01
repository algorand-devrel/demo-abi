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

	atc := future.MakeAtomicTransactionComposer()
	_ = atc.AddMethodCall(future.AddMethodCallParams{
		AppID:           contract.AppId,
		Method:          getMethod(contract, "add"),
		MethodArgs:      []interface{}{1, 1},
		Sender:          acct.Address,
		SuggestedParams: sp,
		OnComplete:      types.NoOpOC,
	}, signer)

	_ = atc.AddMethodCall(future.AddMethodCallParams{
		AppID:           contract.AppId,
		Method:          getMethod(contract, "sub"),
		MethodArgs:      []interface{}{3, 1},
		Sender:          acct.Address,
		SuggestedParams: sp,
		OnComplete:      types.NoOpOC,
	}, signer)

	_ = atc.AddMethodCall(future.AddMethodCallParams{
		AppID:           contract.AppId,
		Method:          getMethod(contract, "mul"),
		MethodArgs:      []interface{}{3, 2},
		Sender:          acct.Address,
		SuggestedParams: sp,
		OnComplete:      types.NoOpOC,
	}, signer)

	_ = atc.AddMethodCall(future.AddMethodCallParams{
		AppID:           contract.AppId,
		Method:          getMethod(contract, "div"),
		MethodArgs:      []interface{}{4, 2},
		Sender:          acct.Address,
		SuggestedParams: sp,
		OnComplete:      types.NoOpOC,
	}, signer)

	_ = atc.AddMethodCall(future.AddMethodCallParams{
		AppID:           contract.AppId,
		Method:          getMethod(contract, "qrem"),
		MethodArgs:      []interface{}{27, 5},
		Sender:          acct.Address,
		SuggestedParams: sp,
		OnComplete:      types.NoOpOC,
	}, signer)

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
