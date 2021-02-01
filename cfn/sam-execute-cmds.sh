echo $ARTIFACT_PFIX  # ARTIFACT_PFIX -> "01_cognito"
echo $STACK_NAME  # STACK_NAME -> "covcov-cognito-DEV"
echo " "


# sam build   -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml CovcovLibsLayer
# TODO: Après le build:
# mkdir -p ./.aws-sam/build/FakeFunction_/python
# mv ./.aws-sam/build/FakeFunction/*  ./.aws-sam/build/FakeFunction_/python
# rmdir ./.aws-sam/build/FakeFunction
#

#cd $TGET_ENV
#rm -r .aws-sam
##sam build -b ./$TGET_ENV/.aws-sam/build  -t $TGET_ENV/$ARTIFACT_PFIX-template.yaml --config-file $TGET_ENV/$ARTIFACT_PFIX-samconfig.toml &&
#sam build -b -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml &&


## Build the layer : https://bryson3gps.wordpress.com/2018/12/06/trick-sam-into-building-your-lambda-layers/
#mkdir -p $TGET_ENV/.aws-sam/build/FakeFunction_/python
#mv $TGET_ENV/.aws-sam/build/FakeFunction/*  $TGET_ENV/.aws-sam/build/FakeFunction_/python
#rmdir $TGET_ENV/.aws-sam/build/FakeFunction
#mv $TGET_ENV/.aws-sam/build/FakeFunction_ $TGET_ENV/.aws-sam/build/FakeFunction


#BUCKET_EXISTS=$(aws s3api head-bucket --bucket $STACK_NAME-$TGET_ENV-1 2>&1 || true)
#if [ -z "$BUCKET_EXISTS" ]; then
#  echo "Bucket exists"
#else
#  echo "Bucket '" $STACK_NAME-$TGET_ENV "' does not exists ==> Bucket creation"
#  aws s3 mb s3://$STACK_NAME-$TGET_ENV-1 --region eu-west-3
#fi

cd $TGET_ENV
rm -r .aws-sam
sam build   -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml &&
sam package -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --output-template-file $ARTIFACT_PFIX-out.yml --force-upload --debug &&
sam deploy  -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --template-file $ARTIFACT_PFIX-out.yml  --stack-name $STACK_NAME-$TGET_ENV
cd ..


#sam package -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --output-template-file $ARTIFACT_PFIX-out.yml --force-upload --s3-bucket covcov-dev &&
#sam deploy  -t $ARTIFACT_PFIX-template.yaml --config-file $ARTIFACT_PFIX-samconfig.toml --template-file ./$ARTIFACT_PFIX-out.yml  --stack-name $STACK_NAME --s3-bucket covcov-dev

# sam package --s3-bucket covcov --output-template-file out.yml &&
# sam deploy --no-confirm-changeset --template-file ./out.yml --stack-name test-2


