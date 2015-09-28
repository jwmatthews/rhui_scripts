#!/bin/bash

cat <<EOQ | rhui-manager --username admin --password admin
n
u
$1
y
q
EOQ
