#!/bin/sh
INSTALL_DIR=./install
source ${INSTALL_DIR}/vars
if [ ! -f ${INSTALL_DIR}/${ENT_CERT} ]; then
  echo "Missing a required entitlement certificate: expected it to be at '${INSTALL_DIR}/${ENT_CERT}'"
  echo "Visit access.redhat.com and download a valid certificate and save it to: '${INSTALL_DIR}/${ENT_CERT}'"
  exit 1
fi

if [ ! -f ${SSH_PRIV_KEY} ]; then
  echo "Missing required private ssh key for ec2 instances"
  echo "Please copy the ssh key to: ${SSH_PRIV_KEY}"
  echo "Please also run a chmod 600 ${SSH_PRIV_KEY}"
  exit 1
fi

if [ $(stat -c %a ${SSH_PRIV_KEY}) != 600 ]; then
  echo "Please change the permissions of: ${SSH_PRIV_KEY} to be 600."
  exit 1
fi

pushd .
cd provision
time (./create_instances.sh && ./install_software.sh && ./setup_rhui.sh)
popd
echo ""
echo ""
echo "RHUI has been setup on the below hosts"
echo ""
cat hostnames.env

