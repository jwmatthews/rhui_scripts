#!/bin/sh

source ./hostnames
source ./vars

cp -R /usr/share/rh-rhua/rhui_certs /home/ec2-user
cd /home/ec2-user/rhui_certs
echo "Will generate certs for: "
echo "  RHUA   = ${RHUA}"
echo "  CDS_01 = ${CDS_01}"
echo "  CDS_02 = ${CDS_02}"
ENCRYPT_KEYS=0 ./create_rhui_ssl_certs.sh ${RHUA} ${CDS_01} ${CDS_02}

