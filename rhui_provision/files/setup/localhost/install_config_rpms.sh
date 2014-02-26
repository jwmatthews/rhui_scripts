#!/bin/sh
source ../../../vars
source ${HOSTNAMES_ENV}

echo "yum install config rpm on CDS_01: ${CDS_O1}"
ssh -t -t -i ${EC2_SSH_PRIV_KEY} ${EC2_SSH_USER}@${CDS_01} -x "sudo yum -y --nogpgcheck --disableplugin=rhui-lb --disablerepo='*' install /home/${EC2_SSH_USER}/rh-cds*.rpm"

echo "yum install config rpm on CDS_02: ${CDS_02}"
ssh -t -t -i ${EC2_SSH_PRIV_KEY} ${EC2_SSH_USER}@${CDS_02} -x "sudo yum -y --nogpgcheck --disableplugin=rhui-lb --disablerepo='*' install /home/${EC2_SSH_USER}/rh-cds*.rpm"

exit 0

