#!/bin/bash

source hostnames.env
source desired_hostnames.env
HOSTNAME=${DESIRED_CDS_02}

hostname ${HOSTNAME}
sed -i "s/^HOSTNAME.*/HOSTNAME=${HOSTNAME}/" /etc/sysconfig/network


RHUA_IP=`dig +short ${RHUA}`
CDS1_IP=`dig +short ${CDS_01}`
CDS2_IP=`dig +short ${CDS_02}`

grep "${RHUA_IP}" /etc/hosts
if [ "$?" -eq "1" ]; then
	echo "${RHUA_IP} ${DESIRED_RHUA}" >> /etc/hosts
else
	sed -i "s/^${RHUA_IP}.*/${RHUA_IP} ${DESIRED_RHUA}/" /etc/hosts
fi 

grep "${CDS1_IP}" /etc/hosts
if [ "$?" -eq "1" ]; then
	echo "${CDS1_IP} ${DESIRED_CDS_01}" >> /etc/hosts
else
	sed -i "s/^${CDS1_IP}.*/${CDS1_IP} ${DESIRED_CDS_01}/" /etc/hosts
fi 

grep "${CDS2_IP}" /etc/hosts
if [ "$?" -eq "1" ]; then
	echo "${CDS2_IP} ${DESIRED_CDS_02}" >> /etc/hosts
else
	sed -i "s/^${CDS2_IP}.*/${CDS2_IP} ${DESIRED_CDS_02}/" /etc/hosts
fi 

