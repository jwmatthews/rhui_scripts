#!/bin/sh
source ./vars

if [ ! -f ${ANSIBLE_INVENTORY} ]; then
  echo "Unable to find ansible hosts file: ${ANSIBLE_INVENTORY}"
  exit
fi

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

EXISTING_CERT_DIR=""
if [ ! -z "$1" ]; then
  EXISTING_CERT_DIR=`realpath $1`
fi

ansible-playbook setup_rhui.yml -i ${ANSIBLE_INVENTORY} -vv --private-key=${SSH_PRIV_KEY} --extra-vars "existing_cert_dir=${EXISTING_CERT_DIR}" | tee ${LOG_DIR}/rhui_dev_setup.log
