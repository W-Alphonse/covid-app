echo $1  # ARTIFACT_PFIX -> "01_cognito"
echo $2  # STACK_NAME -> "covcov-cognito-DEV"
echo " "

rm -r ./.aws-sam
# sam build   -t $1-template.yaml --config-file $1-samconfig.toml CovcovLibsLayer
# TODO: Après le build:
# mkdir -p ./.aws-sam/build/FakeFunction_/python
# mv ./.aws-sam/build/FakeFunction/*  ./.aws-sam/build/FakeFunction_/python
# rmdir ./.aws-sam/build/FakeFunction
#
sam build   -t $1-template.yaml --config-file $1-samconfig.toml

# Build the layer : https://bryson3gps.wordpress.com/2018/12/06/trick-sam-into-building-your-lambda-layers/
mkdir -p ./.aws-sam/build/FakeFunction_/python
mv ./.aws-sam/build/FakeFunction/*  ./.aws-sam/build/FakeFunction_/python
rmdir ./.aws-sam/build/FakeFunction
mv ./.aws-sam/build/FakeFunction_ ./.aws-sam/build/FakeFunction

sam package -t $1-template.yaml --config-file $1-samconfig.toml --output-template-file $1-out.yml --force-upload &&
sam deploy  -t $1-template.yaml --config-file $1-samconfig.toml --template-file ./$1-out.yml  --stack-name $2
#sam package -t $1-template.yaml --config-file $1-samconfig.toml --output-template-file $1-out.yml --force-upload --s3-bucket covcov-dev &&
#sam deploy  -t $1-template.yaml --config-file $1-samconfig.toml --template-file ./$1-out.yml  --stack-name $2 --s3-bucket covcov-dev

# sam package --s3-bucket covcov --output-template-file out.yml &&
# sam deploy --no-confirm-changeset --template-file ./out.yml --stack-name test-2


