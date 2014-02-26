#!/bin/sh
source ../../../vars
source ${HOSTNAMES_ENV}

if [ ! -d ${GEN_CONFIG_RPM_DIR} ]; then
  mkdir -p ${GEN_CONFIG_RPM_DIR}
fi

rm -f ${GEN_CONFIG_RPM_DIR}/*.rpm

echo "scp files from RHUA"
scp -i ${EC2_SSH_PRIV_KEY} ${EC2_SSH_USER}@${RHUA}:/etc/rhui/*.rpm ${GEN_CONFIG_RPM_DIR}

