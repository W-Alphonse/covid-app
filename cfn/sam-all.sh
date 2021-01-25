sam build && 
sam package --output-template-file out.yml &&
sam deploy --no-confirm-changeset --template-file ./out.yml

# sam package --s3-bucket covcov --output-template-file out.yml &&
# sam deploy --no-confirm-changeset --template-file ./out.yml --stack-name test-2

# https://stackoverflow.com/questions/62536095/how-to-set-a-stage-name-in-a-sam-template
# https://medium.com/@rokaso/cloudformation-gotchas-and-lessons-learned-22a671556b6b
# https://labrlearning.medium.com/a-detailed-look-at-aws-cognito-da19b1dd0fba
# https://www.learncoderetain.com/aws-kms-cognito-and-security-refresher/
# https://lumigo.io/aws-serverless-ecosystem/aws-serverless-application-model/