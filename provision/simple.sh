export ANSIBLE_HOSTS=~/ansible_hosts
export ANSIBLE_HOST_KEY_CHECKING=False
export SSH_PRIV_KEY=~/.ssh/splice_rsa
export LOG_DIR=./logs

grep "localhost" $ANSIBLE_HOSTS &> /dev/null || echo "localhost" > ~/ansible_hosts

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

time ansible-playbook simple.yml -vv --private-key=${SSH_PRIV_KEY} | tee ${LOG_DIR}/simple.log
