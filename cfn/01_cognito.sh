
export ARTIFACT_PFIX=01_cognito
export STACK_NAME=covcov-cognito
export ENV=$1

echo ENV $ENV

. sam-prepare-config.sh  $ARTIFACT_PFIX $ENV
#. sam-execute-cmds.sh $ARTIFACT_PFIX $STACK_NAME-$ENV


#. sam-execute-cmds.sh '01_cognito' 'covcov-cognito-DEV'

