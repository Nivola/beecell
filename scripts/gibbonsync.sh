#!/bin/bash

if [ -z "$1" ]; then 
    echo usage: $0 prod/test home/office
    exit
fi

RSA='.ssh/id_rsa'
env=$1
from=$2
pkg=$3

if [ "$env" = "prod" ]; then
    if [ "$from" = "home" ]; then
        # prod from home
        HOST='172.16.0.19'
        PORT='5022'
        REFPATH='/home/io/workspace/git'
		echo "Sync environment: $env (host:$HOST, port:$PORT) from: $from"
        if [ "$pkg" = "beecell" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 5022 -i .ssh/id_rsa' $REFPATH/beecell/beecell root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloud" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 5022 -i .ssh/id_rsa' $REFPATH/gibboncloud/gibboncloud root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibbonportal" -o "$pkg" = "all" ]; then        
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 5022 -i .ssh/id_rsa' $REFPATH/gibbonportal/gibbonportal root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloudapi" -o "$pkg" = "all" ]; then            
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 5022 -i .ssh/id_rsa' $REFPATH/gibboncloudapi/gibboncloudapi root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "portal-stage" ]; then
            SYNC_PATH='/usr/local/lib/gibbon/portal-02/lib/python2.7/site-packages/'
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 5022 -i .ssh/id_rsa' $REFPATH/beecell/beecell root@$HOST:$SYNC_PATH
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 5022 -i .ssh/id_rsa' $REFPATH/gibboncloud/gibboncloud root@$HOST:$SYNC_PATH
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 5022 -i .ssh/id_rsa' $REFPATH/gibbonportal/gibbonportal root@$HOST:$SYNC_PATH
        fi        
        
    elif [ "$from" = "office" ]; then
        # prod from office
        HOST='10.102.86.4'
        PORT='22'
        REFPATH='/home/io/workspace/git'
        echo "Sync environment: $env (host:$HOST, port:$PORT) from: $from"
        if [ "$pkg" = "beecell" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/beecell/beecell root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloud" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibboncloud/gibboncloud root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibbonportal" -o "$pkg" = "all" ]; then        
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibbonportal/gibbonportal root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloudapi" -o "$pkg" = "all" ]; then            
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibboncloudapi/gibboncloudapi root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "portal-stage" ]; then
            SYNC_PATH='/usr/local/lib/gibbon/portal-02/lib/python2.7/site-packages/'
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/beecell/beecell root@$HOST:$SYNC_PATH
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibboncloud/gibboncloud root@$HOST:$SYNC_PATH
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibbonportal/gibbonportal root@$HOST:$SYNC_PATH
        fi
    fi
elif [ "$env" = "test" ]; then
    if [ "$from" = "home" ]; then
        # test from home
        HOST='172.16.0.19'
        PORT='4022'
        REFPATH='/home/io/workspace/git'
        echo "Sync environment: $env (host:$HOST, port:$PORT) from: $from"
        if [ "$pkg" = "beecell" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 4022 -i .ssh/id_rsa' $REFPATH/beecell/beecell root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloud" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 4022 -i .ssh/id_rsa' $REFPATH/gibboncloud/gibboncloud root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibbonportal" -o "$pkg" = "all" ]; then        
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 4022 -i .ssh/id_rsa' $REFPATH/gibbonportal/gibbonportal root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloudapi" -o "$pkg" = "all" ]; then            
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 4022 -i .ssh/id_rsa' $REFPATH/gibboncloudapi/gibboncloudapi root@$HOST:/usr/local/lib/gibbon
        fi            
    elif [ "$from" = "office" ]; then
        # test from office
        HOST='10.102.47.208'
        PORT='22'
        REFPATH='/root/workspace/git'
        echo "Sync environment: $env (host:$HOST, port:$PORT) from: $from"
        if [ "$pkg" = "beecell" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/beecell/beecell root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloud" -o "$pkg" = "all" ]; then
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibboncloud/gibboncloud root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibbonportal" -o "$pkg" = "all" ]; then        
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibbonportal/gibbonportal root@$HOST:/usr/local/lib/gibbon
        fi
        if [ "$pkg" = "gibboncloudapi" -o "$pkg" = "all" ]; then            
            rsync -avzPr --exclude-from 'exclude-list' -e 'ssh -p 22 -i .ssh/id_rsa' $REFPATH/gibboncloudapi/gibboncloudapi root@$HOST:/usr/local/lib/gibbon
        fi    
    fi
fi
