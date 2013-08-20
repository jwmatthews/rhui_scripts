#!/bin/sh
source ../hostnames.env
source vars

if [ ! -d ${GEN_CONFIG_RPM_DIR} ]; then
  mkdir -p ${GEN_CONFIG_RPM_DIR}
fi

echo "scp files from RHUA"
scp -i ${SSH_PRIV_KEY} ${SSH_USER}@${RHUA}:/tmp/rhui/*.rpm ${GEN_CONFIG_RPM_DIR}

