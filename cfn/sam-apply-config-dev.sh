#!/bin/sh

mkdir -p $TGET_ENV
cat > $TGET_ENV/$ARTIFACT_PFIX.config << EOF
s/¤stack-name¤/$STACK_NAME/
s/¤cognito-stack-name¤/$COGNITO_STACK_NAME/
s/¤prj-name¤/$PRJ_NAME/
s/¤env¤/$TGET_ENV/
s/¤sg-id¤/00f6c4428099b89d3/
s/¤subnet-id_1¤/****/
s/¤subnet-id_2¤/****/
s/¤relative-path-src¤/..\/..\/src/
s/¤cmk_id¤/arn:aws:kms:eu-west-3:030307376673:key\/a52945d5-81ce-4cb8-899b-c05f88da4285/
s/¤PostConfirmationFunctionRoleId¤/1M01I9Q8IU748/
s/¤CompanyDomainFunctionRoleId¤/19PZGC0U7JTNM/
s/¤VisitDomainFunctionRoleId¤/1IPKCCY08YIWR/
s/¤CompanyCasContactFunctionRoleId¤/H9BD91I8M82K/
s/¤COG_APP_CLIENT_ID¤/****/
s/¤COG_USER_POOL_ID¤/eu-west-****/
s/¤LOG_LEVEL¤/INFO/
s/¤DB_URL¤/******/
s/¤DB_ECHO¤/True/
EOF