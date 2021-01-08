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
  print("** event ** :" + str(event))
  user_attrs =  event ['request']['userAttributes']

  # https://docs.aws.amazon.com/fr_fr/cognito/latest/developerguide/cognito-user-pool-managing-errors.html / SignUp: UsernameExistsException
  # https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-attributes.html#user-pool-settings-aliases
  if db.native_execute_sqls([f"select 1 from company where email = '{user_attrs ['email']}'" ])[0] != 0 :
    raise Exception(f"Used email '{user_attrs ['email']}' already exist")

  return event

# if __name__ == '__main__':
#   handle(None,None)
  # email = 'wharouny.tp@gmail.comz'
  # if db.native_execute_sqls([f"select 1 from company where email = '{email}'" ])[0] != 0 :
  #   print(f"Email {email} exists")
  # else :
  #   print(f"Email {email} does not exist")

# {
#   "version":"1",
#   "region":"eu-west-3",
#   "userPoolId":"eu-west-3_05HzIk4Qk",
#   "userName":"wharouny",
#   "callerContext":{
#     "awsSdkVersion":"aws-sdk-unknown-unknown",
#     "clientId":"6o8cf2djai5dg5btns5iqaf13r"
#   },
#   "triggerSource":"PostConfirmation_ConfirmSignUp",
#   "request":{
#     "userAttributes":{
#       "sub":"4e7c9c03-46e2-41a9-b1f8-6aa97df1e9a5",
#       "cognito:user_status":"CONFIRMED",
#       "email_verified":"true",
#       "cognito:email_alias":"wharouny@gmail.com",
#       "email":"wharouny@gmail.com"
#     }
#   },
#   "response":{
#   }
# }
