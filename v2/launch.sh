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
#if [ ! -z "$1" ]; then
#  ISO_PATH=`realpath $1`
#fi

usage() {
echo "$0 [options] ISO_FILE (optional) ..."
echo
echo "Options"
echo " -p      Optional packages to install on RHUA/CDS (default: $PACKAGES)"
echo " -i      Install RHUA/CDS software from ISO (default: $ISO_PATH)"
echo " -h      Help"
exit 2
}

while getopts ":p:,:i:,:h" opt; do
    case $opt in
        h)     usage;;
        p)     PACKAGES=$OPTARG;;
        i)     ISO_PATH=$OPTARG;;
        \?)    break;; # end of options
    esac
done

if [ ! -z "$2" ]; then
  EXISTING_CERT_DIR=`realpath $2`
fi

./launch_stack.py --template ${CLOUD_FORMATION_TEMPLATE} --bash_out_file ${HOSTNAMES_ENV} --ans_out_file ${ANSIBLE_INVENTORY}
if [ "$?" -ne "0" ]; then
	echo "Failed to run launch_stack.py"
	exit 1
fi

./install_software.sh -i ${ISO_PATH} -p ${PACKAGES}
if [ "$?" -ne "0" ]; then
	echo "Failed to run install_software.sh"
	exit 1
fi

./setup_rhui.sh ${EXISTING_CERT_DIR}
if [ "$?" -ne "0" ]; then
	echo "Failed to run setup_rhui.sh"
	exit 1
fi

echo "RHUI has been setup on the below hosts"
echo ""
cat hostnames.env

