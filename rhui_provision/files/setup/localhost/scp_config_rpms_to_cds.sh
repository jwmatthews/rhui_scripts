#!/bin/sh
source ../../../vars
source ${HOSTNAMES_ENV}

if [ ! -d ${GEN_CONFIG_RPM_DIR} ]; then
  echo "Missing required directory: ${GEN_CONFIG_RPM_DIR}"
  echo "Please run 'gather_config_rpms_from_rhua.sh' first"
  exit 1
fi

echo "scp config rpm to CDS_01"
scp -i ${EC2_SSH_PRIV_KEY} ${GEN_CONFIG_RPM_DIR}/rh-cds1*.rpm ${EC2_SSH_USER}@${CDS_01}:~

echo "scp config rpm to CDS_02"
scp -i ${EC2_SSH_PRIV_KEY} ${GEN_CONFIG_RPM_DIR}/rh-cds2*.rpm ${EC2_SSH_USER}@${CDS_02}:~
