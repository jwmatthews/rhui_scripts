#!/bin/sh
source ./hostnames
source ./vars

echo "Will generate certs for: "
echo "  RHUA   = ${RHUA}"
echo "  CDS_01 = ${CDS_01}"
echo "  CDS_02 = ${CDS_02}"
/usr/share/rh-rhua/rhui_certs/create_rhui_ssl_certs.sh --noencrypt ${RHUA} ${CDS_01} ${CDS_02}
