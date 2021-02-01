import json
import logging
import traceback

import covcov.infrastructure.db.schema.company_domain as cd
import covcov.infrastructure.db.schema.visit_domain as vd
from covcov.application.BusinessException import BusinessException
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
    # _sub = '¤ii4e4rv3s'
    # auth_claims = {'sub': _sub,  'email': _sub + '@gmail.com' }
    method = payload.pop('method') if bool(payload.get('method'))  else '' # 1 - Extract 'method type' = POST | GET | DELETE + Payload type + Payload
    tbl_name   = next(iter(payload))                                       # 1.a - type values : [company, room, zone, visit]
    tbl_object = vd.Visit   if tbl_name == vd.Visit.__tablename__ else \
                 cd.Company if tbl_name == cd.Company.__tablename__ else \
                 cd.Room    if tbl_name == cd.Room.__tablename__ else \
                 cd.Zone    if tbl_name == cd.Zone.__tablename__ else None
    check_route_consistency(method, tbl_name, route)
    if bool(qry_params):
      payload[tbl_name].update(qry_params)  # 1.b - Add 'qry_params' to 'payload data'
    if tbl_object == cd.Company :           # 1.c - Set the 'id' for "Company/Ars" by extracting 'sub' from the Authentication-token
    # if (table == cd.Company) and ( payload[type].get('id') is None) : # <-- Over Flask, it allows to bypass Cognito by injecting the 'id' in the payload
      payload[tbl_name].update({'id': auth_claims['sub']})
    #
    # 2 - According to method type, decide how to route the Payload
    method_result="Success :-)"
    if method.upper() == 'POST' or method.upper() == 'PUT' :
      tbl_object.enhance_payload_with_auth_token(payload[tbl_name], auth_claims)
      tbl_object.check_business_rules_for_upsert(payload[tbl_name])
      tbl_object.preprocess_before_upsert(payload[tbl_name])
      if tbl_object == vd.Visit :
        db.insert_value([payload[tbl_name]],[tbl_object])
        method_result = {"redirect":f"{select_company_url(payload[tbl_name]['company_id'], db)}"}
      else :
        method_result = db.upsert_value([payload[tbl_name]],[tbl_object], auth_claims['sub'])
    elif method.upper() == 'GET' :
      method_result =  db.select_rows( [tbl_object(**payload[tbl_name])] , [tbl_object])
      tbl_object.execute_after_select(db, method_result[0])
    elif (route == '/a_ccontact') or (route == '/c_ccontact') :
      if route == '/c_ccontact' :
        payload[tbl_name].update({'company_id': auth_claims['sub']})
      sql_stmts_kv = vd.Visit.compose_ccontact_sqls(payload[tbl_name])
      result_list = db.native_select_rows(list(sql_stmts_kv.values()), 0)
      method_result = vd.Visit.compose_ccontact_result(list(sql_stmts_kv.keys()), result_list)
    elif method.upper() == 'DELETE' :
      db.delete_rows([payload[tbl_name]],[tbl_object])
    elif method.upper() == 'RESET_TABLES' :
      db.reset_tables()
    elif method.upper() == 'FILL_TABLES' :
      cd.create_company( payload[tbl_name]["company_id"], payload[tbl_name]["company_name"], payload[tbl_name]["company_email"], payload[tbl_name]["url"], payload[tbl_name]["pfix"]  )
      vd.create_visit(payload[tbl_name]["company_id"])
    else :
      raise Exception(f"Unrecognized 'method' value '{method}' or table '{str(tbl_name)}'. Value should be one of [POST, PUT, DELETE, GET, CONNECT]")
    return compose_success_response(method_result)
  except BusinessException as ex:
    return compose_success_response(ex.context)
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

def compose_redirect_response(location:str) -> dict:
  headers = HEADERS_VALUES.copy()
  d_location = {"Location":f"{location}"}
  headers.update(d_location)
  return {
    STATUS_CODE: OK_302,
    HEADERS: headers,
    BODY: json.dumps(d_location)
  }
