import json
import logging
from covcov.infrastructure.db.database import Database
from covcov.application import purge

logger = logging.getLogger(__name__)
db = Database("database")

def handle(event, context) :
  qry_params = None
  if 'body' in event :
    body = json.loads(event['body'])  # --> Type(event[body]) : <class 'str'>
    qry_params = event['queryStringParameters']
  else :
    body = event # --> Type(event) : <class 'dict'>
  purge.archive_visit(db)
  # return route_dispatcher.dispatch(body, qry_params, None, event['resource'], db)

