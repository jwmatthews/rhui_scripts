export RHUI_HOSTS_FILE=../rhui_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs
export ISO_PATH=`realpath $1`

if [ ! -f ${RHUI_HOSTS_FILE} ]; then
  echo "Unable to find ansible hosts file: ${RHUI_HOSTS_FILE}"
  exit
fi

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

ansible-playbook rhui_dev_install_software.yml -i ${RHUI_HOSTS_FILE} -vv --private-key=${SSH_PRIV_KEY} --extra-vars "iso_path=$ISO_PATH" | tee ${LOG_DIR}/rhui_dev_install_software.log
