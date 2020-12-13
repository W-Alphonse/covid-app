import json
import logging
from covcov.infrastructure.db.database import Database
from covcov.application import route_dispatcher

import sys

logger = logging.getLogger(__name__)

# https://www.postgresql.org/message-id/AANLkTim6p8vp0+h48-sC1Cu1govjQqi+WKsC_QnWdrwE@mail.gmail.com
# https://github.com/jkehler/awslambda-psycopg2
# https://github.com/jkehler/awslambda-psycopg2/issues/47
# https://stackoverflow.com/questions/44855531/no-module-named-psycopg2-psycopg-modulenotfounderror-in-aws-lambda

# print(f"sys.path: {sys.path}")
db = Database("database")

def handle(event, context) :

  # from psycopg2 import __version__ as pv
  # print(f"xxx: {pv}")
  # print( help('modules'))
      # import importlib
      # f, filename, description = importlib.find_module('psycopg2')
      # print(f"psycopg2 file location: {filename} - description : {description}")

  print("** Event **\n" + str(event))
  #
  if isinstance(event,dict) :
    for k,v in event.items() :
      print(f'key:{k} - value:{v}')
    # body = event['body']
    # for k,v in body.items() :
    #   print(f'body.key:{k} - body.value:{v}')
  #
  if 'body' in event :
    print("** Contains Tag 'body' **")
    body = event['body']
  else :
    print("** Does not contain Tag 'body' **")
    body = event
  #
  ret = route_dispatcher.dispatch(body,db)
  print(f'** route_dispatcher.dispatch ({type(ret)}) ** : {str(ret)}')
  return ret
  # return {"body" : "super" }

