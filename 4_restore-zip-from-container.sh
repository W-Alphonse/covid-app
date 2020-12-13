# 5 - Send back the ZIP to the local host -> $1 : Container ID
docker cp $1:/root/covcov-app/build_zipped/covcov-aws.zip  .