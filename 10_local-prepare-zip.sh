# 0 - Assemble the dependencies
# rm -r ./build; mkdir ./build
pip install -r ./covcov/requirements-aws.txt -t ./build --upgrade

# 1 - Create the Zip with all dependencies
mkdir -p ./build_zipped
cd ./build; rm covcov-aws.zip; zip -r ../build_zipped/covcov-aws.zip .; cd ..

# 2 - Add the <project:covcov> to the zip
zip -g -r ./build_zipped/covcov-aws.zip ./covcov

# 3 - Add lambda(s) at the root of the zip
cd covcov; zip -g ../build_zipped/covcov-aws.zip ./lambda_company_domain.py; cd ..

# 4 - Delete the unrequired artifacts
zip -d ./build_zipped/covcov-aws.zip covcov/lambda_company_domain.py
zip -d ./build_zipped/covcov-aws.zip covcov/application/server.py
zip -d ./build_zipped/covcov-aws.zip covcov/requirements-flask.txt