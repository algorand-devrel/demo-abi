#!/bin/bash

set -euo pipefail

SB="$HOME/sandbox/sandbox"
GOAL="$SB goal"

accts=(`$GOAL account list | awk '{print $3}'`)
creator=${accts[0]}

app_id=`cat ../.app_id`

echo "Funding app account"
app_addr=`$GOAL app info --app-id $app_id | grep 'Application account' | awk '{print $3}' | tr -d '\r'`
$GOAL clerk send -f $creator -t $app_addr -a 1000000000

box_name="cool_box"
# use b64 to pass named box
b64_box_name=`echo -n $box_name | base64 -w0`
# Convert to byte array
encoded_box_name=`echo -n $box_name | od -td1 -An | tr -s [:space:] ',' | sed 's/^,//g' | sed 's/,$//g'`
echo "Calling box_write(byte[],(uint64,uint64))void with $box_name and '(123,456)'"
$GOAL app method --app-id $app_id \
    --method "box_write(byte[],(uint64,uint64))void" \
    --arg "[$encoded_box_name]" --arg [123,456] --from ${accts[1]} \
    --box "0,b64:$b64_box_name" 
echo ""

echo "Calling box_read(byte[])(uint64,uint64) with $box_name"
$GOAL app method --app-id $app_id \
    --method "box_read(byte[])(uint64,uint64)" \
    --arg "[$encoded_box_name]" --from ${accts[1]} \
    --box "0,b64:$b64_box_name" 
echo ""

echo "Calling add(uint64,uint64)uint64) with 2 and 3."
$GOAL app method --app-id $app_id \
    --method "add(uint64,uint64)uint64" \
    --arg 2 --arg 3 --from ${accts[1]}
echo ""

echo "Calling sub(uint64,uint64)uint64 with 5 and 1."
$GOAL app method --app-id $app_id \
    --method "sub(uint64,uint64)uint64" \
    --arg 5 --arg 1 --from ${accts[1]}
echo ""

echo "Calling div(uint64,uint64)uint64 with 8 and 2."
$GOAL app method --app-id $app_id \
    --method "div(uint64,uint64)uint64" \
    --arg 8 --arg 2 --from ${accts[1]}
echo ""

echo "Calling mul(uint64,uint64)uint64 with 4 and 2."
$GOAL app method --app-id $app_id \
    --method "mul(uint64,uint64)uint64" \
    --arg 4 --arg 2 --from ${accts[1]}
echo ""

echo "Calling qrem(uint64,uint64)(uint64,uint64) with 5 and 2."
$GOAL app method --app-id $app_id \
    --method "qrem(uint64,uint64)(uint64,uint64)" \
    --arg 5 --arg 2 --from ${accts[1]}
echo ""

echo "Calling reverse(string)string with \"My Message\"."
$GOAL app method --app-id $app_id \
    --method "reverse(string)string" \
    --arg '"My Message"' --from ${accts[1]}
echo ""


echo "Calling concat_strings(string[])string with [\"My\",\"Message\"]."
$GOAL app method --app-id $app_id \
    --method "concat_strings(string[])string" \
    --arg '["My","Message"]' --from ${accts[1]}
echo ""

echo "Calling manyargs(uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64)uint64 with 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, and 20."
$GOAL app method --app-id $app_id \
    --method "manyargs(uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64)uint64" \
    --arg 1 --arg 2 --arg 3 --arg 4 --arg 5 \
    --arg 6 --arg 7 --arg 8 --arg 9 --arg 10 \
    --arg 11 --arg 12 --arg 13 --arg 14 --arg 15 \
    --arg 16 --arg 17 --arg 18 --arg 19 --arg 20 \
    --from ${accts[1]}
echo ""

echo "Calling min_bal(account)uint64 with Senders Address."
$GOAL app method --app-id $app_id \
    --method "min_bal(account)uint64" \
    --arg ${accts[1]} --from ${accts[1]}
echo ""

echo "Calling txntest(uint64,pay,uint64)uint64 with 2, Payment Transaction, and 1000."
$GOAL clerk send --amount 2 --from ${accts[1]} \
    --to ${accts[1]} -o txntest_pay.txn
$GOAL app method --app-id $app_id \
    --method "txntest(uint64,pay,uint64)uint64" \
    --arg 2 --arg txntest_pay.txn --arg 1000 --from ${accts[1]}
echo ""


#echo "Calling tupler((string,uint64,string))uint64 with (\"My\",42,\"Message\")."
#$GOAL app method --app-id $app_id \
#    --method "tupler((string,uint64,string))uint64" \
#    --arg ['"My"',42,'"Message"'] --from ${accts[1]}
#echo ""