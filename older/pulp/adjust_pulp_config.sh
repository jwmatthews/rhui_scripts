#!/bin/sh
HOSTNAME=`hostname`
sed "s/host = localhost.localdomain/host\ =\ ${HOSTNAME}/" -i /etc/pulp/admin/admin.conf
