#!/bin/bash

# Sets up dependencies to run RHUI provisioning automation
# Tailored to a RHEL 7.3 box inside of AWS

hostname ansible-runner
yum -y install wget tmux
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum -y install epel-release-latest-7.noarch.rpm
yum -y install gcc libffi-devel python-devel openssl-devel
yum -y install python-pip
pip install ansible==2.2.1.0
pip install boto3

echo DONE!
echo Ensure that RHUI provisioning environment variables are set correctly before proceeding.

