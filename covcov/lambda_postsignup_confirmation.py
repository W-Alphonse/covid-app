import logging

from covcov.infrastructure.db.database import Database
from covcov.application import route_dispatcher
from covcov.application import misc_utils as create_user
from covcov.infrastructure.configuration import config

logger = logging.getLogger(__name__)
db = Database("database")
#
region         = config["cognito"]["COG_REGION"]
user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]
app_client_id  = config["cognito"]["COG_APP_CLIENT_ID"]

def handle(event, context):
  create_user(event, db)

  return event
