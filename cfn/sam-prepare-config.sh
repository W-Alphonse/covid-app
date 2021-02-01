#!/bin/sh

if [ -z $TGET_ENV ]
then
  echo "\$TGET_ENV is mandatory and has no value. Valid value should be one from [dev, demo, prod]"
  return 1
fi
if  [ $TGET_ENV != "dev" ] && [ $TGET_ENV != "prod" ] && [ $TGET_ENV != "demo" ]
then
  echo "\$TGET_ENV value has invalid value of '$TGET_ENV'. Valid value should be one from [dev, demo, prod]"
  return 1
fi

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
EOF


sed -f $TGET_ENV/$ARTIFACT_PFIX.config $ARTIFACT_PFIX-template.yaml-tpl > ./$TGET_ENV/$ARTIFACT_PFIX-template.yaml
sed -f $TGET_ENV/$ARTIFACT_PFIX.config $ARTIFACT_PFIX-samconfig.toml-tpl > ./$TGET_ENV/$ARTIFACT_PFIX-samconfig.toml

#sed 's/$PORT/portyyyy/;s/$DOMAIN/domainnnn/' t.template
#sed 's/$PORT/portyyyy/;s/$DOMAIN/domainnnn/' t.template