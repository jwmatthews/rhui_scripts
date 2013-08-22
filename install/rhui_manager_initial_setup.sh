#!/bin/bash
cat <<EOQ | rhui-manager --username admin --password admin
/tmp/rhui_certs/ca.crt
/tmp/rhui_certs/ca.key
3650
q
EOQ

