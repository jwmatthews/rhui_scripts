#!/bin/sh
source ./vars

if [ ! -f ${ANSIBLE_INVENTORY} ]; then
  echo "Unable to find ansible hosts file: ${ANSIBLE_INVENTORY}"
  exit
fi

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

usage() {
echo "$0 -r /path/to/hostnames.env -f /path/to/desired_hostnames.env"
echo
echo "Options"
echo " -r      Real hostnames, this a path to hostnames.env, contains actual DNS hostnames of provisioned instances"
echo " -f      Fake hostnames, this is a path to desired_hostnames.env, contains the desired (perhaps fake) hostnames we want to simulate"
echo " -?      Help"
exit 2
}

while getopts ":r:,:f:,:h" opt; do
    case $opt in
        h)     usage;;
        r)     HOSTNAMES_ENV=$OPTARG;;
        f)     DESIRED_HOSTNAMES_ENV=$OPTARG;;
        \?)    break;; # end of options
    esac
done

if [ -z "$HOSTNAMES_ENV" ]; then
  echo "Please re-run with the path to hostnames.env"
  usage
fi

if [ -z "$DESIRED_HOSTNAMES_ENV" ]; then
  echo "Please re-run with the path to hostnames.env"
  usage
fi

echo "Will create a new client that uses:"
echo "  Real hostnames:  HOSTNAMES_ENV = '${HOSTNAMES_ENV}'"
echo "  Fake hostnames:  DESIRED_HOSTNAMES_ENV = '${DESIRED_HOSTNAMES_ENV}'"

ansible-playbook create_client.yml -i ${ANSIBLE_INVENTORY} -vv --private-key=${EC2_SSH_PRIV_KEY} --extra-vars "hostnames_env=${HOSTNAMES_ENV} desired_hostnames_env=${DESIRED_HOSTNAMES_ENV}" | tee ${LOG_DIR}/create_client.log
