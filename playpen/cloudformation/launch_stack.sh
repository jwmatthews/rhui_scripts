KEY_NAME="splice"
OWNER_NAME=`whoami`
TEMPLATE_NAME="file://`pwd`/simple_rhui_setup.template"
STACK_NAME="RHUISimpleStack"
REGION="us-east-1"

aws cloudformation create-stack --stack-name ${STACK_NAME} --region ${REGION} --parameters ParameterKey=KeyName,ParameterValue=${KEY_NAME} ParameterKey=OwnerName,ParameterValue=${OWNER_NAME} --template-body ${TEMPLATE_NAME}
