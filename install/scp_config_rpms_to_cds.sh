#!/bin/sh
source ../hostnames.env
source ./vars

if [ ! -d ${GEN_CONFIG_RPM_DIR} ]; then
  echo "Missing required directory: ${GEN_CONFIG_RPM_DIR}"
  echo "Please run 'gather_config_rpms_from_rhua.sh' first"
  exit 1
fi

echo "scp config rpm to CDS_01"
scp -i ${SSH_PRIV_KEY} ${GEN_CONFIG_RPM_DIR}/rh-cds1*.rpm ${SSH_USER}@${CDS_01}:~

echo "scp config rpm to CDS_02"
scp -i ${SSH_PRIV_KEY} ${GEN_CONFIG_RPM_DIR}/rh-cds2*.rpm ${SSH_USER}@${CDS_02}:~
