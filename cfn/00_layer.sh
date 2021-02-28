export ARTIFACT_PFIX=00_layer
export STACK_NAME=covcov-layer
export PRJ_NAME=covcovio # PRJ_NAME gives uniques "name" for resources requiring unicity all over AWS. Ex: S3 Bucket, Cognito Domain Name
export TGET_ENV=$1

. sam-prepare-config.sh
. sam-execute-cmds.sh


