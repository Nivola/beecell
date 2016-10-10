#!/bin/bash

if [ -z "$1" ]; then 
    echo usage: $0 prod/test home/office
    exit
fi

from=$1

if [ "$from" = "home" ]; then
    HOST='172.16.0.19'
    PORT='10022'
    REFPATH='/home/io/workspace/git/cloudstack/plugins/hypervisors/kvm/target'
    FILE='cloud-plugin-hypervisor-kvm-4.3.1.jar'
    echo "Sync environment: (host:$HOST, port:$PORT) from: $from"
    #rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 10022' $REFPATH/beecell/beecell root@$HOST:/usr/local/lib/gibbon
    scp -P $PORT $REFPATH/$FILE root@$HOST:/usr/share/cloudstack-agent/lib
elif [ "$from" = "office" ]; then
    # prod from office
    HOST='10.102.86.4'
    PORT='22'
    REFPATH='/root/workspace/git'
fi
