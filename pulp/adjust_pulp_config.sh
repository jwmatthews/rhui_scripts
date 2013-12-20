#!/bin/sh
HOSTNAME=`hostname`
#sed "s/localhost/${HOSTNAME}/" -i /etc/pulp/server.conf
sed "s/host = localhost.localdomain/host\ =\ ${HOSTNAME}/" -i /etc/pulp/server.conf
