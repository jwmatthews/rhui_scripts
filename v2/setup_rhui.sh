#!/bin/sh
source ./vars

if [ ! -f ${ANSIBLE_INVENTORY} ]; then
  echo "Unable to find ansible hosts file: ${ANSIBLE_INVENTORY}"
  exit
fi

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

ansible-playbook setup_rhui.yml -i ${ANSIBLE_INVENTORY} -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/rhui_dev_setup.log
