import json
import logging
from covcov.infrastructure.db.database import Database
from covcov.application import route_dispatcher
from covcov.infrastructure.configuration import config
from covcov.infrastructure.cognito.idp_connexion import IdpConnexion

logger = logging.getLogger(__name__)
db = Database("database")
#
region         = config["cognito"]["COG_REGION"]
user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]
app_client_id  = config["cognito"]["COG_APP_CLIENT_ID"]
cognito_idp = IdpConnexion(region, user_pool_id, app_client_id)

def handle(event, context):
  print('Ds Lambda CompanyCasContactFunction')
  # return {
  #     'statusCode': 200,
  #     'body': json.dumps('Hello from Lambda!')
  # }

  # return {
  #   "statusCode": 200,
  #   "headers" : {
  #     "Content-Type" : "application/json",
  #     "Access-Control-Allow-Headers": "*",
  #     "Access-Control-Allow-Origin": "*",
  #     "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
  #   },
  #   "body" : str({
  #     "code":0,
  #     "description" : "data available :-) !!",
  #     "data" : {
  #       "col_1" : "XXXX",
  #       "col_2" : "YYYY"
  #     }
  #   }).replace("'",'"')
  # }

  qry_params = None
  if 'body' in event :
    body = json.loads(event['body'])  # --> Type(event[body]) : <class 'str'>
    qry_params = event['queryStringParameters']
  else :
    body = event # --> Type(event) : <class 'dict'>
  return route_dispatcher.dispatch(body, qry_params, None, db)