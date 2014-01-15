#!/bin/sh
source ./vars

if [ ! -f ${ANSIBLE_INVENTORY} ]; then
  echo "Unable to find ansible hosts file: ${ANSIBLE_INVENTORY}"
  exit
fi

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

if [ ! -z "$1" ]; then
  ISO_PATH=`realpath $1`
fi

ansible-playbook install_software.yml -i ${ANSIBLE_INVENTORY} -vv --private-key=${SSH_PRIV_KEY} --extra-vars "iso_path=$ISO_PATH" | tee ${LOG_DIR}/install_software.log
