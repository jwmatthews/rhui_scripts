#!/bin/sh
source ./vars
CLOUD_FORMATION_TEMPLATE=./rhui_cloud_formation.template

ENT_CERT="./ent_cert.pem"
if [ ! -f ${ENT_CERT} ]; then
  echo "Missing a required entitlement certificate: expected it to be at '${ENT_CERT}'"
  echo "Visit access.redhat.com and download a valid certificate and save it to: '${ENT_CERT}'"
  exit 1
fi

if [ ! -f ${SSH_PRIV_KEY} ]; then
  echo "Missing required private ssh key for ec2 instances"
  echo "Please copy the ssh key to: ${SSH_PRIV_KEY}"
  echo "Please also run a chmod 600 ${SSH_PRIV_KEY}"
  exit 1
fi

if [ $(stat -c %a ${SSH_PRIV_KEY}) != 600 ]; then
  echo "Please change the permissions of: ${SSH_PRIV_KEY} to be 600."
  exit 1
fi

if [ ! -d ${LOG_DIR} ]; then
  mkdir ${LOG_DIR}
fi

pushd .

usage() {
echo "$0 [options] ISO_FILE (optional) ..."
echo
echo "Options"
echo " -p      Optional packages to install on RHUA/CDS (default: $PACKAGES)"
echo " -i      Install RHUA/CDS software from ISO (default: $ISO_PATH)"
echo " -d      Directory containing existing certificates to user for this install"
echo " -r      RH Repo Data file"
echo " -c      Client RPMs directory"
echo " -h      Help"
exit 2
}

while getopts ":p:,:i:,:d:,:r:,:c:,:h" opt; do
    case $opt in
        h)     usage;;
        p)     PACKAGES=$OPTARG;;
        i)     ISO_PATH=$OPTARG;;
        d)     EXISTING_CERT_DIR=$OPTARG;;
        r)     REPO_DATA_FILE=$OPTARG;;
        c)     CLIENT_RPM_DIR=$OPTARG;;
        \?)    break;; # end of options
    esac
done

./launch_stack.py --template ${CLOUD_FORMATION_TEMPLATE} --bash_out_file ${HOSTNAMES_ENV} --ans_out_file ${ANSIBLE_INVENTORY}
if [ "$?" -ne "0" ]; then
	echo "Failed to run launch_stack.py"
	exit 1
fi

### Install Software Block ###
if [ ! -z "$ISO_PATH" ] && [ ! -z "$PACKAGES" ]; then
  ./install_software.sh -i ${ISO_PATH} -p ${PACKAGES}
elif [ ! -z "$ISO_PATH" ]; then
  ./install_software.sh -i ${ISO_PATH}
elif [ ! -z "$PACKAGES" ]; then
  ./install_software.sh -p ${PACKAGES}
else
  ./install_software.sh
fi

if [ "$?" -ne "0" ]; then
	echo "Failed to run install_software.sh"
	exit 1
fi

### Setup RHUI Block ###
if [ ! -z "$EXISTING_CERT_DIR" ] && [ ! -z "$REPO_DATA_FILE" ] && [ ! -z "$CLIENT_RPM_DIR" ]; then
  ./setup_rhui.sh -d ${EXISTING_CERT_DIR} -r ${REPO_DATA_FILE} -c ${CLIENT_RPM_DIR}
elif [ ! -z "$EXISTING_CERT_DIR" ] && [ ! -z "$CLIENT_RPM_DIR" ]; then
  ./setup_rhui.sh -d ${EXISTING_CERT_DIR} -c ${CLIENT_RPM_DIR}
elif [ ! -z "$REPO_DATA_FILE" ] && [ ! -z "$CLIENT_RPM_DIR" ]; then
  ./setup_rhui.sh -r ${REPO_DATA_FILE} -c ${CLIENT_RPM_DIR}
elif [ ! -z "$REPO_DATA_FILE" ] && [ ! -z "$EXISTING_CERT_DIR" ]; then
  ./setup_rhui.sh -r ${REPO_DATA_FILE} -d ${EXISTING_CERT_DIR}
elif [ ! -z "$EXISTING_CERT_DIR" ]; then
  ./setup_rhui.sh -d ${EXISTING_CERT_DIR}
elif [ ! -z "$REPO_DATA_FILE" ]; then
  ./setup_rhui.sh -r ${REPO_DATA_FILE}
elif [ ! -z "$CLIENT_RPM_DIR" ]; then
  ./setup_rhui.sh -c ${CLIENT_RPM_DIR}
else
  ./setup_rhui.sh
fi

if [ "$?" -ne "0" ]; then
	echo "Failed to run setup_rhui.sh"
	exit 1
fi

echo "RHUI has been setup on the below hosts"
echo ""
cat hostnames.env

