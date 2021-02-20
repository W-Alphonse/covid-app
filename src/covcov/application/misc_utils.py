import random

from covcov.application import route_dispatcher
from covcov.application.Ctx import Ctx
from covcov.infrastructure.db.database import Database
from covcov.application.templates import *
from covcov.infrastructure.configuration import config

ROUTE = '/company_domain'

region         = config["cognito"]["COG_REGION"]
user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]

def make_id(k=10):
  chars = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
  return ''.join(random.choices(chars, k=10))

def gen_room(description:str, auth_claim:dict, db: Database, kms_clt ) -> dict :
  room_id = make_id()
  room = {'id':room_id, 'description':f'{description}', 'company_id':f'{auth_claim["sub"]}'}
  body = { 'method' : 'POST', 'room': room }
  route_dispatcher.dispatch(Ctx(body, None, auth_claim , ROUTE, db, kms_clt, config["kms"]["cmk_id"]))
  return room_id

def gen_zone(room_id: str, description:str, auth_claim:dict, db: Database, kms_clt ) -> dict :
  zone = {'id':make_id(), 'description':f'{description}', 'room_id':f'{room_id}'}
  body = { 'method' : 'POST', 'zone': zone }
  route_dispatcher.dispatch(Ctx(body, None, auth_claim , ROUTE, db, kms_clt, config["kms"]["cmk_id"]))
  return

def populate_spaces(event, db, kms_clt) -> None:
  user_attrs = event ['request']['userAttributes']
  auth_claim = {'sub': user_attrs ['sub'],  'email': user_attrs['email'] }
  type_etablissement = user_attrs.get('custom:etablissement')
  rooms = TEMPLATES[type_etablissement].copy() if bool(TEMPLATES.get(type_etablissement)) else TEMPLATES[AUTRE].copy()
  for room in rooms:
    room_id = gen_room(room["room"], auth_claim, db, kms_clt)
    for zone in room['zones']:
      gen_zone(room_id, zone['zone'], auth_claim, db, kms_clt)

def populate_user(event, db, kms_clt):
  user_attrs = event ['request']['userAttributes']
  auth_claim = {'sub': user_attrs ['sub'],  'email': user_attrs['email'] }
  body = { 'method' : 'POST',
           'company': {"name": f"{user_attrs['custom:company_name']}" ,
                       "type": f"{user_attrs['custom:etablissement']}" if bool(user_attrs.get('custom:etablissement')) else None } }
  route_dispatcher.dispatch(Ctx(body, None, auth_claim , ROUTE, db, kms_clt, config["kms"]["cmk_id"]))

def should_create_user(event):
  user_attrs = event ['request']['userAttributes']
  is_valid_user_pool = event['region'] == region and event['userPoolId'] == user_pool_id
  is_valid_trigger = event['triggerSource'] == 'PostConfirmation_ConfirmSignUp'
  is_valid_user = user_attrs ['email_verified'] == 'true' and user_attrs['cognito:user_status'] == 'CONFIRMED'
  return is_valid_user_pool & is_valid_trigger & is_valid_user

def create_user(event, db, kms_clt):
  if should_create_user(event):
    populate_user(event, db, kms_clt)
    # populate_spaces(event, db, kms_clt)


# if __name__ == '__main__':
#   from covcov.infrastructure.db.database import Database
#   import datetime
#   import boto3
#   from botocore.config import Config
#   #
#   db = Database("database")
#   kms_clt = boto3.client('kms', config=Config(connect_timeout=10, read_timeout=10, retries={'max_attempts': 3}))
#
#
#   event = {}
#   _sub = '¤' + str(datetime.datetime.now())
#   event['request'] = { 'userAttributes' : { 'sub': _sub, 'email': _sub + '@gmail.com',
#                                             'email_verified' : 'true', 'cognito:user_status': 'CONFIRMED',
#                                             'custom:etablissement': MEDIC,  'custom:company_name': _sub   } }
#   event['userName'] = _sub + '_name'
#   event['region'] = region
#   event['userPoolId'] = user_pool_id
#   event['triggerSource'] = 'PostConfirmation_ConfirmSignUp'
#   create_user(event, db, kms_clt)





  # event = {'version': '1', 'region': 'eu-west-3', 'userPoolId': 'eu-west-3_asaRuXKE9', 'userName': 'wharouny.tp',
  # 'callerContext': {'awsSdkVersion': 'aws-sdk-unknown-unknown', 'clientId': '6td9c7nhclpvvav057544go5u6'},
  # 'triggerSource': 'PostConfirmation_ConfirmSignUp',
  # 'request': {'userAttributes':
  #     {'sub': '96082fa1-3e42-458f-ada3-296e7b72d04b',
  #       'custom:company_name': 'wharouny.tp',
  #       'custom:etablissement': 'RESTO',
  #       'cognito:user_status': 'CONFIRMED',
  #       'email_verified': 'true', 'cognito:email_alias': 'wharouny.tp@gmail.com',
  #       'phone_number_verified': 'false',
  #       'email': 'wharouny.tp@gmail.com'}},
  # 'response': {}}