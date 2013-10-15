#!/bin/bash
cat <<EOQ | rhui-manager --username admin --password admin
/home/ec2-user/rhui_certs/certs/client-ca-chain.pem
/home/ec2-user/rhui_certs/certs/client-ca-key.pem
3650
q
EOQ

