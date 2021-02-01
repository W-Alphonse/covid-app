echo $ARTIFACT_PFIX
echo $STACK_NAME
echo $TGET_ENV
echo " "

# 1 - Sam build
cd $TGET_ENV
rm -r .aws-sam-$STACK_NAME
sam build -b .aws-sam-$STACK_NAME/build  -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml

# 2 - Build the layer : https://bryson3gps.wordpress.com/2018/12/06/trick-sam-into-building-your-lambda-layers/
mkdir -p .aws-sam-$STACK_NAME/build/FakeFunction_/python
mv .aws-sam-$STACK_NAME/build/FakeFunction/*  .aws-sam-$STACK_NAME/build/FakeFunction_/python
rmdir .aws-sam-$STACK_NAME/build/FakeFunction
mv .aws-sam-$STACK_NAME/build/FakeFunction_ .aws-sam-$STACK_NAME/build/FakeFunction

# 3 - Sam package & deploy
sam package -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --output-template-file $ARTIFACT_PFIX-out.yml --force-upload --debug &&
sam deploy  -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --template-file $ARTIFACT_PFIX-out.yml  --stack-name $STACK_NAME-$TGET_ENV
cd ..

# 4 - Get back the initial config.yml
mv $PATH_CFG_YML/config_.yml $PATH_CFG_YML/config.yml


#BUCKET_EXISTS=$(aws s3api head-bucket --bucket $STACK_NAME-$TGET_ENV-1 2>&1 || true)
#if [ -z "$BUCKET_EXISTS" ]; then
#  echo "Bucket exists"
#else
#  echo "Bucket '" $STACK_NAME-$TGET_ENV "' does not exists ==> Bucket creation"
#  aws s3 mb s3://$STACK_NAME-$TGET_ENV-1 --region eu-west-3
#fi