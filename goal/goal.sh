#!/bin/bash

SB="$HOME/sandbox/sandbox"
GOAL="$SB goal"

accts=(`$GOAL account list | awk '{print $3}'`)
creator=${accts[0]}

app_id=`cat ../.app_id`

$GOAL app method --app-id $app_id \
 --method "add(uint64,uint64)uint64" \
 --arg 1 --arg 1 --from ${accts[1]}

$GOAL app method --app-id $app_id \
 --method "sub(uint64,uint64)uint64" \
 --arg 3 --arg 1 --from ${accts[1]}

$GOAL app method --app-id $app_id \
 --method "div(uint64,uint64)uint64" \
 --arg 4 --arg 2 --from ${accts[1]}

$GOAL app method --app-id $app_id \
 --method "mul(uint64,uint64)uint64" \
 --arg 3 --arg 2 --from ${accts[1]}
