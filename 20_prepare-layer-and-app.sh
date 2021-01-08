# 0 - Assemble the dependencies
 rm -r ./build; mkdir ./build
pip install -r ./covcov/requirements-aws.txt -t ./build/python --upgrade

# 1 - Create the Zip of all dependencies
mkdir -p ./build_zipped
cd ./build; rm covcov-libs.zip; zip -r ../build_zipped/covcov-libs.zip .; cd ..

# 2 - Create the Zip of the application
rm covcov-app.zip; zip -g -r ./build_zipped/covcov-app.zip ./covcov

# 3 - Add lambda(s) at the root of the zip
cd covcov; zip -g ../build_zipped/covcov-app.zip ./lambda_company_domain.py
zip -g ../build_zipped/covcov-app.zip ./lambda_visit_domain.py
zip -g ../build_zipped/covcov-app.zip ./lambda_cas_contact.py
zip -g ../build_zipped/covcov-app.zip ./lambda_postsignup_confirmation.py
zip -g ../build_zipped/covcov-app.zip ./lambda_histo_visit.py
zip -g ../build_zipped/covcov-app.zip ./lambda_presignup.py; cd ..

# 4 - Delete the unrequired artifacts
zip -d ./build_zipped/covcov-app.zip covcov/lambda_company_domain.py
zip -d ./build_zipped/covcov-app.zip covcov/lambda_visit_domain.py
zip -d ./build_zipped/covcov-app.zip covcov/lambda_cas_contact.py
zip -d ./build_zipped/covcov-app.zip covcov/lambda_postsignup_confirmation.py
zip -d ./build_zipped/covcov-app.zip covcov/lambda_histo_visit.py
zip -d ./build_zipped/covcov-app.zip covcov/lambda_presignup.py

zip -d ./build_zipped/covcov-app.zip covcov/application/server.py
zip -d ./build_zipped/covcov-app.zip covcov/requirements-flask.txt