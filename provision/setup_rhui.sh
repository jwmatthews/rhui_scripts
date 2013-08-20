export RHUI_HOSTS_FILE=../rhui_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

time ansible-playbook rhui_dev_setup.yml -i ${RHUI_HOSTS_FILE} -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/rhui_dev_setup.log
