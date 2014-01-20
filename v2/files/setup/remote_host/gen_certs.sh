#!/bin/sh
source ./hostnames.env
source ./desired_hostnames.env
source ./vars

echo "Will generate certs for: "
echo "  RHUA   = ${DESIRED_RHUA}"
echo "  CDS_01 = ${DESIRED_CDS_01}"
echo "  CDS_02 = ${DESIRED_CDS_02}"
/usr/share/rh-rhua/rhui_certs/create_rhui_ssl_certs.sh --noencrypt ${DESIRED_RHUA} ${DESIRED_CDS_01} ${DESIRED_CDS_02}
