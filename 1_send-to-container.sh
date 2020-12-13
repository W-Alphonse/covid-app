# $1 : Container ID
# docker cp /home/haa/pydev/aws-lambda/covid-app/covcov $1:/root/covcov-app
docker cp ./covcov $1:/root/covcov-app
docker cp ./2_pip-install-on-container.sh           $1:/root/covcov-app
docker cp ./3_assemble-zip-and-get-back-to-host.sh  $1:/root/covcov-app
docker cp ./setup.py                                $1:/root/covcov-app