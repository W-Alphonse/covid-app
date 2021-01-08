import random

from covcov.application import route_dispatcher
from covcov.infrastructure.db.database import Database
from covcov.application.templates import TEMPLATES
from covcov.infrastructure.configuration import config

ROUTE = '/company_domain'

region         = config["cognito"]["COG_REGION"]
user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]

def purge_visit(nbr_days:int) -> int:
  pass

def make_id(k=10):
  chars = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
  return ''.join(random.choices(chars, k=10))

def gen_room(description:str, auth_claim:dict, db: Database ) -> dict :
    room_id = make_id()
    room = {'id':room_id, 'description':f'{description}', 'company_id':f'{auth_claim["sub"]}'}
    body = { 'method' : 'POST', 'room': room }
    route_dispatcher.dispatch(body, None, auth_claim , ROUTE, db)
    return room_id

def gen_zone(room_id: str, description:str, auth_claim:dict, db: Database ) -> dict :
  zone = {'id':make_id(), 'description':f'{description}', 'room_id':f'{room_id}'}
  body = { 'method' : 'POST', 'zone': zone }
  route_dispatcher.dispatch(body, None, auth_claim , ROUTE, db)
  return

def populate_spaces(event, db) -> None:
    type_etablissement = ""
    auth_claim = {'sub': user_attrs ['sub'],  'email': user_attrs['email'] }
    rooms = TEMPLATES[type_etablissement].copy()
    for room in rooms:
        room_id = gen_room(room["room"], auth_claim, db)
        for zone in room['zones']:
            gen_zone(room_id, zone['zone'], auth_claim, db)

def populate_user(event, db):
    user_attrs = event ['request']['userAttributes']
    auth_claim = {'sub': user_attrs ['sub'],  'email': user_attrs['email'] }
    body = { 'method' : 'POST',
             'company': {"name": f"{event['userName']}" } }
    route_dispatcher.dispatch(body, None,  auth_claim, ROUTE, db)

def should_create_user(event):
  user_attrs = event ['request']['userAttributes']
  is_valid_user_pool = event['region'] == region and event['userPoolId'] == user_pool_id
  is_valid_trigger = event['triggerSource'] == 'PostConfirmation_ConfirmSignUp'
  is_valid_user = user_attrs ['email_verified'] == 'true' and user_attrs['cognito:user_status'] == 'CONFIRMED'
  return is_valid_user_pool & is_valid_trigger & is_valid_user

def create_user(event, db):
  if should_create_user(event):
    populate_user(event, db)
    populate_spaces(event, db)
