#. common.sh '03_api' 'covcov-api-DEV'

export ARTIFACT_PFIX=03_api
export STACK_NAME=covcov-api
export COGNITO_STACK_NAME=covcov-cognit
export PRJ_NAME=covcov
export TGET_ENV=$1

. sam-prepare-config.sh  # $ARTIFACT_PFIX $TGET_ENV $PRJ_NAME
. sam-execute-cmds.sh    # $ARTIFACT_PFIX $TGET_ENV $STACK_NAME



# https://stackoverflow.com/questions/62536095/how-to-set-a-stage-name-in-a-sam-template
# https://medium.com/@rokaso/cloudformation-gotchas-and-lessons-learned-22a671556b6b
# https://labrlearning.medium.com/a-detailed-look-at-aws-cognito-da19b1dd0fba
# https://www.learncoderetain.com/aws-kms-cognito-and-security-refresher/
# https://lumigo.io/aws-serverless-ecosystem/aws-serverless-application-model/