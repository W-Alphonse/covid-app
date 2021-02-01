#!/bin/sh

mkdir -p $TGET_ENV
cat > $TGET_ENV/$ARTIFACT_PFIX.config << EOF
s/¤stack-name¤/$STACK_NAME/
s/¤cognito-stack-name¤/$COGNITO_STACK_NAME/
s/¤prj-name¤/$PRJ_NAME/
s/¤env¤/$TGET_ENV/
s/¤sg-id¤/07e556a0646210968/
s/¤subnet-id_1¤/08c8be7b7bc3d5b17/
s/¤subnet-id_2¤/02f8d18bfc7567152/
s/¤subnet-id_3¤/04221ccadea52a084/
s/¤relative-path-src¤/..\/..\/src/
s/¤COG_APP_CLIENT_ID¤/2s8lcr08p3mb453ofcqvtde9r6/
s/¤COG_USER_POOL_ID¤/eu-west-3_KbhRKJfVX/
s/¤LOG_LEVEL¤/INFO/
s/¤DB_URL¤/***/
s/¤DB_ECHO¤/True/
EOF