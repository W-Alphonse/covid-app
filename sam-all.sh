sam build && 
sam package --output-template-file out.yml &&
sam deploy --no-confirm-changeset --template-file ./out.yml

# sam package --s3-bucket covcov --output-template-file out.yml &&
# sam deploy --no-confirm-changeset --template-file ./out.yml --stack-name test-2

#https://stackoverflow.com/questions/62536095/how-to-set-a-stage-name-in-a-sam-template