#!/bin/bash
cat <<EOQ | rhui-manager
r
c
rhui-client-config-beta-rhel-server-7-i386-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 7 i386 Beta
rhui-client-config/beta/rhel/server/7/i386/os
1
y
rhui-client-config/beta/rhel/server/7/i386/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager
r
c
rhui-client-config-beta-rhel-server-7-x86_64-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 7 x86_64 Beta
rhui-client-config/beta/rhel/server/7/x86_64/os
1
y
rhui-client-config/beta/rhel/server/7/x86_64/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager
r
c
rhui-client-config-beta-rhel-server-6-i386-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 i386 Beta
rhui-client-config/beta/rhel/server/6/i386/os
1
y
rhui-client-config/beta/rhel/server/6/i386/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager
r
c
rhui-client-config-beta-rhel-server-6-x86_64-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 6 x86_64 Beta
rhui-client-config/beta/rhel/server/6/x86_64/os
1
y
rhui-client-config/beta/rhel/server/6/x86_64/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager
r
c
rhui-client-config-beta-rhel-server-5-i386-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 5 i386 Beta
rhui-client-config/beta/rhel/server/5/i386/os
2
y
rhui-client-config/beta/rhel/server/5/i386/os
y
n
n
y
q
EOQ

cat <<EOQ | rhui-manager
r
c
rhui-client-config-beta-rhel-server-5-x86_64-os
Red Hat Update Infrastructure 2.0 Client Configuration Server 5 x86_64 Beta
rhui-client-config/beta/rhel/server/5/x86_64/os
2
y
rhui-client-config/beta/rhel/server/5/x86_64/os
y
n
n
y
q
EOQ
