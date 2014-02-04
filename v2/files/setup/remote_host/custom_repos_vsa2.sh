#!/bin/bash
cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-beta-server-6-vsa2
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 Beta VSA 2.0
rhui-client-config/beta/rhel/server/6/x86_64/vsa/2.0
2
y
rhui-client-config/beta/rhel/server/6/\$basearch/vsa/2.0
y
n
n
y
q
EOQ
