BUILD_LOG=./build_log
echo "Build Starting: `date`" &> ${BUILD_LOG}
time python bos.py --config ./bos.cfg | tee -a ${BUILD_LOG}
echo "Build Finished: `date`" &>> ${BUILD_LOG}
