#!/bin/sh
source ../hostnames.env
source ./vars

if [ ! -d ${GEN_CONFIG_RPM_DIR} ]; then
  mkdir -p ${GEN_CONFIG_RPM_DIR}
fi

rm -f ${GEN_CONFIG_RPM_DIR}/*.rpm

echo "scp files from RHUA"
scp -i ${SSH_PRIV_KEY} ${SSH_USER}@${RHUA}:/etc/rhui/*.rpm ${GEN_CONFIG_RPM_DIR}

