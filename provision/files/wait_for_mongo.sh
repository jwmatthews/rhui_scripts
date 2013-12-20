#!/bin/bash
RETVAL=1
while [ $RETVAL -ne 0 ]; do
  mongo test --eval "printjson(db.getCollectionNames())"
  RETVAL=$?
  if [ $RETVAL -ne 0 ]; then
    echo "Will sleep 10 seconds, waiting for mongo to come up.  Last retval = ${RETVAL}"
    sleep 10
  fi
done
