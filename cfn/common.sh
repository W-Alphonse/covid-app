#ARTIFACT_PFIX="01_cognito"
#STACK_NAME="covcov-cognito-DEV"
echo $1
echo $2
echo "-------------"

rm -r ./.aws-sam
sam build   -t $1-template.yaml --config-file $1-samconfig.toml &&
sam package -t $1-template.yaml --config-file $1-samconfig.toml --output-template-file $1-out.yml &&
sam deploy  -t $1-template.yaml --config-file $1-samconfig.toml --template-file ./$1-out.yml  --stack-name $2

# sam package --s3-bucket covcov --output-template-file out.yml &&
# sam deploy --no-confirm-changeset --template-file ./out.yml --stack-name test-2


