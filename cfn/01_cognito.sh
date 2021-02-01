export ARTIFACT_PFIX=01_cognito
export STACK_NAME=covcov-cognit
export PRJ_NAME=covcov
export TGET_ENV=$1

. sam-prepare-config.sh  $ARTIFACT_PFIX $TGET_ENV $PRJ_NAME
. sam-execute-cmds.sh    $ARTIFACT_PFIX $TGET_ENV $STACK_NAME


