#!/bin/bash
source vars

cat <<EOQ | rhui-manager --username admin --password admin
${RHUI_CERTS_DIR}/client-ca-chain.pem
${RHUI_CERTS_DIR}/client-ca-key.pem
3650
q
EOQ

