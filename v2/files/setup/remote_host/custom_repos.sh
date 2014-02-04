#!/bin/bash
cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-5-i386-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 5 i386
rhui-client-config/rhel/server/5/i386/os
2
y
rhui-client-config/rhel/server/5/i386/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-5-x86_64-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 5 x86_64
rhui-client-config/rhel/server/5/x86_64/os
2
y
rhui-client-config/rhel/server/5/x86_64/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-6-i386-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 i386
rhui-client-config/rhel/server/6/i386/os
1
y
rhui-client-config/rhel/server/6/i386/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-6-x86_64-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 x86_64
rhui-client-config/rhel/server/6/x86_64/os
1
y
rhui-client-config/rhel/server/6/x86_64/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-5-i386-mrg
Red Hat Update Infrastructure 2.0 Client Configuration Server 5 MRG 2.0 i386
rhui-client-config/rhel/server/5/i386/mrg-g/2.0
2
y
rhui-client-config/rhel/server/5/i386/mrg-g/2.0
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-5-x86_64-mrg
Red Hat Update Infrastructure 2.0 Client Configuration Server 5 MRG 2.0 x86_64
rhui-client-config/rhel/server/5/x86_64/mrg-g/2.0
2
y
rhui-client-config/rhel/server/5/x86_64/mrg-g/2.0
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-6-i386-mrg
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 MRG 2.0 i386
rhui-client-config/rhel/server/6/i386/mrg-g/2.0
1
y
rhui-client-config/rhel/server/6/i386/mrg-g/2.0
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-rhel-server-6-x86_64-mrg
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 MRG 2.0 x86_64
rhui-client-config/rhel/server/6/x86_64/mrg-g/2.0
1
y
rhui-client-config/rhel/server/6/x86_64/mrg-g/2.0
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager --username admin --password admin
r
c
rhui-client-config-server-6-rhs
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 Storage
rhui-client-config/rhel/server/6/x86_64/rhs/6
1
y
rhui-client-config/rhel/server/6/x86_64/rhs/6
y
n
n
y
q
EOQ


