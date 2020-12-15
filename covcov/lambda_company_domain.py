import json
import logging
from covcov.infrastructure.db.database import Database
from covcov.application import route_dispatcher

logger = logging.getLogger(__name__)
db = Database("database")

def handle(event, context) :
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
  ret = route_dispatcher.dispatch(body,qry_params, db)
  # print(f'** route_dispatcher.dispatch ({type(ret)}) ** : {str(ret)}')
  return ret

