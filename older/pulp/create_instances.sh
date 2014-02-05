export PULP_HOSTS_FILE=../pulp_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs

# Remove prior rhui_hosts file if it exists
if [ -f ${PULP_HOSTS_FILE} ]; then
    rm -f ${PULP_HOSTS_FILE}
fi

grep "localhost" $PULP_HOSTS_FILE &> /dev/null || echo "localhost" > ${PULP_HOSTS_FILE}

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

ansible-playbook pulp_setup.yml -i ${PULP_HOSTS_FILE} -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/pulp_setup.log
