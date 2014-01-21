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
  ISO_FILENAME=`echo $1 | rev | cut -f1 -d'/' | rev`
fi

ansible-playbook install_software.yml -i ${ANSIBLE_INVENTORY} -vv --private-key=${SSH_PRIV_KEY} --extra-vars "iso_path=$ISO_PATH rhui_iso_filename=$ISO_FILENAME" | tee ${LOG_DIR}/install_software.log
