import logging
import traceback

import covcov.infrastructure.db.schema.company_domain as cd
import covcov.infrastructure.db.schema.visit_domain as vd
from covcov.infrastructure.db.database import Database

logger = logging.getLogger(__name__)
#
# Attributes and flags used in the endpoint api response
STATUS_CODE = "statusCode"
OK_200 = 200
KO_401 = 401
KO_500 = 500
#
HEADERS = "headers"
BODY    = "body"
ERROR   = "error"
ERROR_DETAIL = "error_detail"
#
HEADERS_VALUES = {
  "Content-Type" : "application/json",
  "Access-Control-Allow-Headers": "*",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}


def dispatch(payload : dict, qry_params:dict, auth_claims:dict, db:Database) -> str:
  try :
    # 1 - Extract 'method type' = POST | GET | DELETE + Payload type + Payload
    method = payload.pop('method')
    # 1.a - type values : [company, room, zone, visit]
    type = next(iter(payload))
    table = vd.Visit   if type == vd.Visit.__tablename__ else \
            cd.Company if type == cd.Company.__tablename__ else \
            cd.Room    if type == cd.Room.__tablename__ else \
            cd.Zone    if type == cd.Zone.__tablename__ else None
    # 1.b - Add 'qry_params' to 'payload data'
    if bool(qry_params):
      payload[type].update(qry_params)
    # 1.c - Compute "Company/Ars" ID by extracting 'sub' from the Authentication-token
    if table == cd.Company :
      payload[type].update({'id': auth_claims['sub']})

    # 2 - According to method type, decide how to route the Payload
    method_result="Success :-)"
    if method.upper() == 'POST' or method.upper() == 'PUT' :
      table.enhance_payload_with_auth_token(payload[type], auth_claims)
      table.check_business_rules_for_upsert(payload[type])
      db.insert_value([payload[type]],[table]) if table == vd.Visit else db.upsert_value([payload[type]],[table])
    elif method.upper() == 'GET' :
      method_result =  db.select_rows( [table(**payload[type])] , [table])
    elif method.upper() == 'DELETE' :
      db.delete_rows([payload[type]],[table])
    # elif method.upper() == 'CONNECT' : # Authenticate over a database
    #   if not db.authenticate(payload[type],table) :
    #     return _compose_error_unauthorized(payload[type]['email'])
    elif method.upper() == 'RESET_TABLES' :
      db.reset_tables()
    else :
      raise Exception(f"Unrecognized 'method' value '{method}' or table '{str(type)}'. Value should be one of [POST, PUT, DELETE, GET, CONNECT]")
    return compose_success_response(method_result)
  except Exception as ex:
    return _compose_error_response(ex)


def _compose_error_response(ex: Exception) -> dict:
  logger.exception(ex)
  return {
    STATUS_CODE: KO_500,
    HEADERS : HEADERS_VALUES,
    ERROR: "Error of type [{}] occured : {}".format( type(ex), str(ex).replace('"', "'").replace('\n','').strip("' ") ),
    ERROR_DETAIL: "   --> ".join( [elmt.replace('"', "'").replace('\n','').strip("' ") for elmt in traceback.format_tb(ex.__traceback__)] )
  }

# def _compose_error_unauthorized(user_id: str) -> dict:
#   logger.exception(f"Unauthorized user '{user_id}' error")
#   return {
#     STATUS_CODE: KO_401,
#     HEADERS: HEADERS_VALUES,
#     ERROR: "Unauthorized user error",
#   }

def compose_success_response(result) -> dict:
  return {
    STATUS_CODE: OK_200,
    HEADERS: HEADERS_VALUES,
    BODY: str(result).replace("'",'"')
  }
