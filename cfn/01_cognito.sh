ARTIFACT_PFIX="01_cognito"
echo $ARTIFACT_PFIX
echo $ARTIFACT_PFIX-out.yml

sam build   -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml &&
sam package -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --output-template-file $ARTIFACT_PFIX-out.yml &&
sam deploy  -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --template-file ./$ARTIFACT_PFIX-out.yml

# sam package --s3-bucket covcov --output-template-file out.yml &&
# sam deploy --no-confirm-changeset --template-file ./out.yml --stack-name test-2


