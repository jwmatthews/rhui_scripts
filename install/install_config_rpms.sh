#!/bin/sh
source ../hostnames.env
source ./vars

echo "scp config rpm to CDS_01"
ssh -t -t -i ${SSH_PRIV_KEY} ${SSH_USER}@${CDS_01} -x "sudo yum -y --nogpgcheck install /home/${SSH_USER}/rh-cds*.rpm"

echo "scp config rpm to CDS_02"
ssh -t -t -i ${SSH_PRIV_KEY} ${SSH_USER}@${CDS_02} -x "sudo yum -y --nogpgcheck install /home/${SSH_USER}/rh-cds*.rpm"

exit 0

