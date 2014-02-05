#!/bin/bash
source vars

# First time we run rhui-manager it prompts us for:
# 1) Entitlement CA Certificate
# 2) Entitlement CA Key
# The entitlement CA is used to sign the entitlement certificates rhui-manager generates for allowing a yum client access to content from a CDS
#

cat <<EOQ | rhui-manager --username admin --password admin
${RHUI_CERTS_DIR}/entitlement-ca.crt
${RHUI_CERTS_DIR}/entitlement-ca-key.pem
3650
q
EOQ

