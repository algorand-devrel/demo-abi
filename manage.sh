#!/bin/bash

SB="$HOME/sandbox/sandbox"
GOAL="$SB goal"

accts=(`$GOAL account list | awk '{print $3}'`)
creator=${accts[0]}

app_name=approval.teal
clear_name=clear.teal


creator=''
initAcct(){
    accts=(`$GOAL account list | awk '{print $3}'`)
    creator=${accts[0]}
}

makeTeal() {
    #python3 contract.py
    $SB copyTo $app_name
    $SB copyTo $clear_name 
}


case $1 in 

    create)
        echo "Creating application"
        initAcct
        makeTeal
        app_id=`$GOAL app create --creator $creator \
            --approval-prog $app_name \
            --clear-prog $clear_name \
            --global-byteslices 0 \
            --global-ints 0 \
            --local-ints 0 \
            --extra-pages 1 \
            --local-byteslices 0  | grep 'Created app' |awk '{print $6}' | tr -d '\r'`

        echo $app_id > .app_id
        echo "App ID: $app_id"
        ;;

    update)
        echo "Updating application"
        initAcct
        makeTeal
        app_id=`cat .app_id`
        $GOAL app update --app-id $app_id \
            --from $creator \
            --approval-prog $app_name \
            --clear-prog $clear_name 
        ;;

    *)
        echo "You must specify create or update"
esac
