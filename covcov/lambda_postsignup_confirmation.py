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
  # print("** event ** :" + str(event))
  user_attrs = event ['request']['userAttributes']
  if event['region'] == region and event['userPoolId'] == user_pool_id  and event['triggerSource'] == 'PostConfirmation_ConfirmSignUp' and \
     user_attrs ['email_verified'] == 'true' and user_attrs['cognito:user_status'] == 'CONFIRMED' :
    body = { 'method' : 'POST',
             'company': {"name": f"{event['userName']}" } }
    auth_claim = {'sub': user_attrs ['sub'],  'email': user_attrs['email'] }
    route_dispatcher.dispatch(body, None,  auth_claim, '/company_domain', db)
    #
    s1 = util.gen_room('Salle 1', auth_claim, db)
    s2 = util.gen_room('Salle de réunion', auth_claim, db)
    #
    util.gen_zone(s1['room']['id'], 'Table 1', auth_claim)
    util.gen_zone(s1['room']['id'], 'Table 2', auth_claim)
    util.gen_zone(s1['room']['id'], 'Table 3', auth_claim)
    #
    util.gen_zone(s2['room']['id'], 'Salle 1', auth_claim)
    util.gen_zone(s2['room']['id'], 'Salle 2', auth_claim)

  return event


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
