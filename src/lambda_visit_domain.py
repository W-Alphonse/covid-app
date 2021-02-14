import json
import logging

import boto3

from covcov.application.Ctx import Ctx
from covcov.infrastructure.db.database import Database
from covcov.application import route_dispatcher
from covcov.infrastructure.configuration import config

logger = logging.getLogger(__name__)
db = Database("database")
kms_clt = boto3.client('kms')

def handle(event, context) :
  qry_params = None
  if 'body' in event :
    body = json.loads(event['body'])  # --> Type(event[body]) : <class 'str'>
    qry_params = event['queryStringParameters']
  else :
    body = event # --> Type(event) : <class 'dict'>

  return route_dispatcher.dispatch(Ctx(body, qry_params, None, event['resource'], db, kms_clt, config["kms"]["cmk_id"]))
  # return route_dispatcher.dispatch(body, qry_params, None, event['resource'], db)

