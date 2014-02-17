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
echo "Options"
echo " -d      Directory containing existing certificates to user for this install"
echo " -r      RH Repo Data file"
echo " -c      Client RPMs directory"
echo " -h      Help"
exit 2
}

while getopts ":d:,:r:,:c:,:h" opt; do
    case $opt in
        h)     usage;;
        d)     EXISTING_CERT_DIR=$OPTARG;;
        r)     REPO_DATA_FILE=$OPTARG;;
        c)     CLIENT_RPM_DIR=$OPTARG;;
        \?)    break;; # end of options
    esac
done

if [ ! -z "$EXISTING_CERT_DIR" ]; then
  EXISTING_CERT_DIR=`readlink -f $EXISTING_CERT_DIR`
  echo "Will provision RHUI setup using information from: ${EXISTING_CERT_DIR}"
fi

if [ ! -z "$REPO_DATA_FILE" ]; then
  REPO_DATA_FILE=`readlink -f $REPO_DATA_FILE`
  REPO_DATA_FILENAME=`echo $REPO_DATA_FILE | rev | cut -f1 -d'/' | rev`
fi

if [ ! -z "$CLIENT_RPM_DIR" ]; then
  CLIENT_RPM_DIR=`readlink -f $CLIENT_RPM_DIR`
fi

ansible-playbook setup_rhui.yml -i ${ANSIBLE_INVENTORY} -vv --private-key=${SSH_PRIV_KEY} --extra-vars "existing_cert_dir=${EXISTING_CERT_DIR} rh_repo_data=${REPO_DATA_FILE} rh_repo_data_filename=${REPO_DATA_FILENAME} custom_client_rpm_dir=${CLIENT_RPM_DIR}" | tee ${LOG_DIR}/setup_rhui.log
