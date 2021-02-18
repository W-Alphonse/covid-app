#!/bin/sh

mkdir -p $TGET_ENV
cat > $TGET_ENV/$ARTIFACT_PFIX.config << EOF
s/¤stack-name¤/$STACK_NAME/
s/¤cognito-stack-name¤/$COGNITO_STACK_NAME/
s/¤prj-name¤/$PRJ_NAME/
s/¤env¤/$TGET_ENV/
s/¤sg-id¤/00f6c4428099b89d3/
s/¤subnet-id_1¤/001de14caa7e5fab5/
s/¤subnet-id_2¤/0542da4ff26acc598/
s/¤relative-path-src¤/..\/..\/src/
s/¤cmk_id¤/arn:aws:kms:eu-west-3:030307376673:key\/a52945d5-81ce-4cb8-899b-c05f88da4285/
s/¤COG_APP_CLIENT_ID¤/6td9c7nhclpvvav057544go5u6/
s/¤COG_USER_POOL_ID¤/eu-west-3_asaRuXKE9/
s/¤LOG_LEVEL¤/INFO/
s/¤DB_URL¤/postgresql+psycopg2:\/\/covcov_admin:>?sTd)2\`ae(_L8z)@covcov-dev.cluster-cauvhk884vjr.eu-west-3.rds.amazonaws.com:5432\/covcov_dev?client_encoding=utf8/
s/¤DB_ECHO¤/True/
EOF