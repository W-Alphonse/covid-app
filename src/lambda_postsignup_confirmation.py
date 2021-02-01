from covcov.infrastructure.db.database import Database
from covcov.application import misc_utils as util

db = Database("database")

def handle(event, context):
  util.create_user(event, db)
  return event


# {
#   "version":"1",
#   "region":"eu-west-3",                           <-- ${region}
#   "userPoolId":"eu-west-3_05HzIk4Qk",
#   "userName":"wharouny",                          <-- ${userName}
#   "callerContext":{
#     "awsSdkVersion":"aws-sdk-unknown-unknown",
#     "clientId":"6o8cf2djai5dg5btns5iqaf13r"       <-- ${clientId}
#   },
#   "triggerSource":"PostConfirmation_ConfirmSignUp",
#   "request":{
#     "userAttributes":{
#       "sub":"4e7c9c03-46e2-41a9-b1f8-6aa97df1e9a5",
#       "cognito:user_status":"CONFIRMED",
#       "email_verified":"true",
#       "cognito:email_alias":"wharouny@gmail.com",
#       "email":"wharouny@gmail.com"                <-- ${email}
#     }
#     "codeParameter": {.....}                      <-- ${codeParameter}
#   },
#   "response":{
#   }
# }
