#!/bin/sh

INPUT_FILE="rsync_testdir.txt"
REMOTE_USER="fedora"
REMOTE_HOST="ec2-54-204-152-124.compute-1.amazonaws.com"

rsync -avz --files-from ${INPUT_FILE} / ${REMOTE_USER}@${REMOTE_HOST}:~

