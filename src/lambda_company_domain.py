import json
import logging

import boto3

from covcov.application.Ctx import Ctx
from covcov.infrastructure.db.database import Database
from covcov.application import route_dispatcher
from covcov.infrastructure.configuration import config
from covcov.infrastructure.cognito.idp_connexion import IdpConnexion

logger = logging.getLogger(__name__)
db = Database("database")
kms_clt = boto3.client('kms')
#
region         = config["cognito"]["COG_REGION"]
user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]
app_client_id  = config["cognito"]["COG_APP_CLIENT_ID"]
cognito_idp = IdpConnexion(region, user_pool_id, app_client_id)


def handle(event, context) :

  # print('**Loading function**')
  # with urllib.request.urlopen(urllib.request.Request(
  #   url='https://cognito-idp.eu-west-3.amazonaws.com/eu-west-3_bAiEm44uF/.well-known/jwks.json',
  #   headers={'Accept': 'application/json'},
  #   method='GET'),
  #   timeout=5) as f :
  #   response = f.read()

  # print(f"idp_connexion - After f.read()")
  # print(f"idp_connexion - response.decode('utf-8'):{response.decode('utf-8')}")
  # print(f"json.loads(response.decode('utf-8'))['keys']: {json.loads(response.decode('utf-8'))['keys']} ")


  # print("** Event **\n" + str(event))
  # #
  # if isinstance(event,dict) :
  #   for k,v in event.items() :
  #     print(f'key:{k} - type(value):{type(v)} - value:{v} ')

  #
  qry_params = None
  if 'body' in event :
    # print(f"** Event contains tag Body - Type(event[body]):{type(event['body'])} **")
    body = json.loads(event['body'])  # --> Type(event[body]) : <class 'str'>
    qry_params = event['queryStringParameters']
  else :
    # print(f"** Event does not contain tag Body - Type(event):{type(event)} **")
    body = event # --> Type(event) : <class 'dict'>
  # print(f"** Après transformation, Body(type) ** : {type(body)}")
  # print("** Body **\n" + str(body))
  #
  # if isinstance(event['headers'],dict) :
  #   for k,v in event['headers'].items() :
  #     print(f'HEADER -> key:{k} - type(value):{type(v)} - value:{v} ')
  # print(f'** event[headers] ** ->  type(value):{type(event["headers"])} - value:{str(event["headers"])} ')

  ret = route_dispatcher.dispatch(Ctx(body, qry_params, cognito_idp.get_claims(event['headers']['auth-id-token'], 'id'), event['resource'], db, kms_clt, config["kms"]["cmk_id"]))
  # print(f'** route_dispatcher.dispatch ({type(ret)}) ** : {str(ret)}')
  return ret

