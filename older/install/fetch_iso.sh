#!/bin/bash

source ./vars

URL="https://cdn.redhat.com/content/dist/rhel/rhui/server/6/6Server/x86_64/rhui/2/iso/RHEL-6-RHUI-2-LATEST-Server-x86_64-DVD.iso"

wget --certificate=${ENT_CERT} --ca-certificate=${REDHAT_CA_CERT} ${URL}
