export RHUI_HOSTS_FILE=./rhui_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs

# Remove prior rhui_hosts file if it exists
if [ -f ${RHUI_HOSTS_FILE} ]; then
    rm -f ${RHUI_HOSTS_FILE}
fi

grep "localhost" $RHUI_HOSTS_FILE &> /dev/null || echo "localhost" > ${RHUI_HOSTS_FILE}

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

time ansible-playbook rhui_dev_create_instances.yml -i ${RHUI_HOSTS_FILE} -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/rhui_dev_create_instances.log
