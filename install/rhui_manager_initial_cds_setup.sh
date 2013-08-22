#!/bin/bash
source ./hostnames
cat <<EOQ | rhui-manager --username admin --password admin
c
a
${CDS_01}
${CDS_01}
${CDS_01}
cluster1
y
a
${CDS_02}
${CDS_02}
${CDS_02}
2
y
q
EOQ

