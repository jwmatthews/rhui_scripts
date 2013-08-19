export HOSTS_FILE=./builder_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs

# Remove prior rhui_hosts file if it exists
if [ -f ${HOSTS_FILE} ]; then
    rm -f ${HOSTS_FILE}
fi

grep "localhost" $HOSTS_FILE &> /dev/null || echo "localhost" > ${HOSTS_FILE}

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

time ansible-playbook create_instance.yml -i ${HOSTS_FILE} -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/create_instance.log
