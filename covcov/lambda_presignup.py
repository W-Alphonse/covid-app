import logging

from covcov.infrastructure.db.database import Database
from covcov.application import route_dispatcher
from covcov.application import misc_utils as util
from covcov.infrastructure.configuration import config

logger = logging.getLogger(__name__)
db = Database("database")
#
region         = config["cognito"]["COG_REGION"]
user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]
app_client_id  = config["cognito"]["COG_APP_CLIENT_ID"]

def handle(event, context):
  user_attrs =  event ['request']['userAttributes']

  # https://docs.aws.amazon.com/fr_fr/cognito/latest/developerguide/cognito-user-pool-managing-errors.html / SignUp: UsernameExistsException
  # https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-attributes.html#user-pool-settings-aliases
  if db.native_execute_sqls([f"select 1 from company where email = '{user_attrs ['email']}'" ])[0] != 0 :
    raise Exception(f": [Email '{user_attrs ['email']}' déjà utilisé. Merci d'en saisir un autre]")

  if db.native_execute_sqls([f"select 1 from company where name = '{event ['userName']}'" ])[0] != 0 :
    raise Exception(f": [Nom d'établissement '{event ['userName']}' déjà utilisé. Merci d'en saisir un autre]")

  return event
