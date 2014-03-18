TEST_DIR="/var/lib/pulp/published/yum/https/repos/content/beta/rhs/rhui/vsa/2.0/x86_64/os"
OUTPUT_FILE="rsync_vsa.txt"

time ./generate_rsync_list.py -s ${TEST_DIR} -o ${OUTPUT_FILE}


