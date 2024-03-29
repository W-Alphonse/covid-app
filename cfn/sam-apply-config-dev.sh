#!/bin/sh

mkdir -p $TGET_ENV
cat > $TGET_ENV/$ARTIFACT_PFIX.config << EOF
s/¤stack-name¤/$STACK_NAME/
s/¤cognito-stack-name¤/$COGNITO_STACK_NAME/
s/¤prj-name¤/$PRJ_NAME/
s/¤env¤/$TGET_ENV/
s/¤sg-id¤/****/
s/¤subnet-id_1¤/****/
s/¤subnet-id_2¤/****/
s/¤relative-path-src¤/..\/..\/src/
s/¤cmk_id¤/arn:aws:kms:****-****-****:****:key\/****-81ce-4cb8-899b-****/
s/¤PostConfirmationFunctionRoleId¤/1M01I9Q8IU748/
s/¤CompanyDomainFunctionRoleId¤/19PZGC0U7JTNM/
s/¤VisitDomainFunctionRoleId¤/1IPKCCY08YIWR/
s/¤CompanyCasContactFunctionRoleId¤/H9BD91I8M82K/
s/¤COG_APP_CLIENT_ID¤/****/
s/¤COG_USER_POOL_ID¤/****-****-****/
s/¤LOG_LEVEL¤/INFO/
s/¤DB_URL¤/******/
s/¤DB_ECHO¤/True/
EOF