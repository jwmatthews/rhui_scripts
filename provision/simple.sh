export RHUI_HOSTS_FILE=./rhui_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs

grep "localhost" $RHUI_HOSTS_FILE &> /dev/null || echo "localhost" > ${RHUI_HOSTS_FILE}

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

time ansible-playbook simple.yml -i ${RHUI_HOSTS_FILE} -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/simple.log
