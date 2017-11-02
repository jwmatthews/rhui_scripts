#!/bin/bash
cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-6-i386-sap-hana
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 SAP Hana i386
rhui-client-config/rhel/server/6/i386/sap-hana
2
y
rhui-client-config/rhel/server/6/\$basearch/sap-hana
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-6-x86_64-sap-hana
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 SAP Hana x86_64
rhui-client-config/rhel/server/6/x86_64/sap-hana/
2
y
rhui-client-config/rhel/server/6/\$basearch/sap-hana
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-7-x86_64-sap-hana
Red Hat Update Infrastructure 2.0 Client Configuration Server 7 SAP Hana x86_64
rhui-client-config/rhel/server/7/x86_64/sap-hana/
2
y
rhui-client-config/rhel/server/7/\$basearch/sap-hana
y
n
n
y
q
EOQ
