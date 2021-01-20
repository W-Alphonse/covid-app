sam build && 
sam package --s3-bucket covcov --output-template-file out.yml &&
sam deploy --no-confirm-changeset --template-file ./out.yml

# sam package --s3-bucket covcov --output-template-file out.yml &&
# sam deploy --no-confirm-changeset --template-file ./out.yml --stack-name test-2

