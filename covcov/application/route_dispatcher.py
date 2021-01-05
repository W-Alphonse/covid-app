import json
import logging
import traceback

import covcov.infrastructure.db.schema.company_domain as cd
import covcov.infrastructure.db.schema.visit_domain as vd
from covcov.infrastructure.db.database import Database

logger = logging.getLogger(__name__)
#
# Attributes and flags used in the endpoint api response
STATUS_CODE = "statusCode"
OK_200 = "200"
OK_302 = "302"
#
KO_401 = "401"
KO_500 = "500"
#
HEADERS = "headers"
BODY    = "body"
#
STACK_TRACE = "stackTrace"
ERROR_TYPE = "errorType"
ERROR_MESSAGE = "errorMessage"

#
HEADERS_VALUES = {
  "Content-Type" : "application/json",
  "Access-Control-Allow-Headers": "*",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}


def check_route_consistency(method : str, tablename:str, route:str) :
  msg_err = f"Action interdite '{method} / {tablename}' pour '{route}'."
  if route == "/visit_domain" :
    if method == "GET" or method == "DELETE" or tablename != vd.Visit.__tablename__ :
      raise Exception(msg_err)
    else :
      return
  #
  if route == "/company_domain" :
    if tablename == vd.Visit.__tablename__ or method == "DELETE" :
      raise Exception(msg_err)
    else :
      return
  #
  if route == "/c_ccontact" or route == "/a_ccontact":
    if method != "" :
      raise Exception(msg_err)
    else :
      return


def dispatch(payload:dict, qry_params:dict, auth_claims:dict, route:str, db:Database) -> dict:
  try :
    method = payload.pop('method') if bool(payload.get('method'))  else '' # 1 - Extract 'method type' = POST | GET | DELETE + Payload type + Payload
    type = next(iter(payload))          # 1.a - type values : [company, room, zone, visit]
    table = vd.Visit   if type == vd.Visit.__tablename__ else \
            cd.Company if type == cd.Company.__tablename__ else \
            cd.Room    if type == cd.Room.__tablename__ else \
            cd.Zone    if type == cd.Zone.__tablename__ else None
    check_route_consistency(method, type, route)
    if bool(qry_params):
      payload[type].update(qry_params)  # 1.b - Add 'qry_params' to 'payload data'
    if table == cd.Company :            # 1.c - Set the 'id' for "Company/Ars" by extracting 'sub' from the Authentication-token
    # if (table == cd.Company) and ( payload[type].get('id') is None) : # <-- Over Flask, it allows to bypass Cognito by injecting the 'id' in the payload
      payload[type].update({'id': auth_claims['sub']})
    #
    # 2 - According to method type, decide how to route the Payload
    method_result="Success :-)"
    if method.upper() == 'POST' or method.upper() == 'PUT' :
      table.enhance_payload_with_auth_token(payload[type], auth_claims)
      table.check_business_rules_for_upsert(payload[type])
      table.preprocess_before_upsert(payload[type])
      if table == vd.Visit :
        db.insert_value([payload[type]],[table])
        method_result = {"redirect":f"{select_company_url(payload[type]['company_id'], db)}"}
      else :
        db.upsert_value([payload[type]],[table])
    elif method.upper() == 'GET' :
      method_result =  db.select_rows( [table(**payload[type])] , [table])
    elif (route == '/a_ccontact') or (route == '/c_ccontact') :
      if route == '/c_ccontact' :
        payload[type].update({'company_id': auth_claims['sub']})
      sql_stmts_kv = vd.Visit.compose_ccontact_sqls(payload[type])
      result_list = db.native_select_rows(list(sql_stmts_kv.values()), 0)
      method_result = vd.Visit.compose_ccontact_result(list(sql_stmts_kv.keys()), result_list)
    elif method.upper() == 'DELETE' :
      db.delete_rows([payload[type]],[table])
    elif method.upper() == 'RESET_TABLES' :
      db.reset_tables()
    elif method.upper() == 'FILL_TABLES' :
      cd.create_company( payload[type]["company_id"], payload[type]["company_name"], payload[type]["company_email"] )
      vd.create_visit(payload[type]["company_id"])
    else :
      raise Exception(f"Unrecognized 'method' value '{method}' or table '{str(type)}'. Value should be one of [POST, PUT, DELETE, GET, CONNECT]")
    return compose_success_response(method_result)
  except Exception as ex:
    return _compose_error_response(ex)
    # raise Exception(str(_compose_error_response(ex) ))

def select_company_url(comp_id:str, db:Database) -> str :
  result_as_dict = db.native_select_rows( [vd.Visit.select_company_url(comp_id)] ) [0]
  return result_as_dict['url'][0]


def _compose_error_response(ex: Exception) -> dict:
  logger.exception(ex)
  headers = HEADERS_VALUES.copy()
  headers.update({"X-Amzn-ErrorType":"Exception"})
  return {
    STATUS_CODE: KO_500,
    HEADERS : headers,
    # BODY: json.dumps({"errorMessage" : "Error of type [{}] occured : {}".format(type(ex), str(ex).replace('"', "'").replace('\n', '').strip("' ")) \
    BODY: json.dumps({"errorMessage" : "Error of type [{}] occured : {}.".format(type(ex), str(ex).replace('"', "'").replace('\n', '')) \
                                       + "   --> ".join( [elmt.replace('"', "'").replace('\n','').strip("' ") for elmt in traceback.format_tb(ex.__traceback__)] )})
  }

# def _compose_error_response(ex: Exception) -> dict:
#   logger.exception(ex)
#   return {
#     STATUS_CODE: KO_500,
#     ERROR_MESSAGE: "Error of type [{}] occured : {}".format( type(ex), str(ex).replace('"', "'").replace('\n','').strip("' ") ),
#     STACK_TRACE: "   --> ".join( [elmt.replace('"', "'").replace('\n','').strip("' ") for elmt in traceback.format_tb(ex.__traceback__)] )
#   }

# def _compose_error_unauthorized(user_id: str) -> dict:
#   logger.exception(f"Unauthorized user '{user_id}' error")
#   return {
#     STATUS_CODE: KO_401,
#     HEADERS: HEADERS_VALUES,
#     BODY: "Unauthorized user error",
#   }

def compose_success_response(result) -> dict:
  return {
    STATUS_CODE: OK_200,
    HEADERS: HEADERS_VALUES,
    BODY: json.dumps(result)
  }

# def compose_redirect_response(location:str) -> dict:
#   headers = HEADERS_VALUES.copy()
#   d_location = {"Location":f"{location}"}
#   headers.update(d_location)
#   return {
#     STATUS_CODE: OK_302,
#     HEADERS: headers,
#     BODY: json.dumps(d_location)
#   }
