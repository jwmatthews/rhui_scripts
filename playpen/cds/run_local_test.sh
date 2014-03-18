TEST_DIR="testdir/published/repo_a"
OUTPUT_FILE="rsync_testdir.txt"

time ./generate_rsync_list.py -s ${TEST_DIR} -o ${OUTPUT_FILE}

