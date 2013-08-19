export HOSTS_FILE=./builder_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs

if [ ! -f ${HOSTS_FILE} ]; then
  echo "Unable to find ansible hosts file: ${HOSTS_FILE}"
  exit
fi

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

time ansible-playbook setup_instance.yml -i ${HOSTS_FILE} -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/setup_instance.log
