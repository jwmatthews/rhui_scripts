#!/bin/bash

if [ "$#" -eq "0" ] 
then
    exit 1
fi

cat <<EOQ | rhui-manager --username admin --password admin
c
a
$1
root
/root/.ssh/cds.rsa
y
q
EOQ
