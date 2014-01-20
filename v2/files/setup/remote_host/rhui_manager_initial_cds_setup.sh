#!/bin/bash
source ./hostnames.env
source ./desired_hostnames.env
cat <<EOQ | rhui-manager --username admin --password admin
c
a
${DESIRED_CDS_01}
${DESIRED_CDS_01}
${DESIRED_CDS_01}
cluster1
y
a
${DESIRED_CDS_02}
${DESIRED_CDS_02}
${DESIRED_CDS_02}
2
y
q
EOQ

