from botocore.client import BaseClient

from covcov.infrastructure.db.database import Database


class Ctx:
  payload : dict
  qry_params : dict
  auth_claims:dict
  #
  route:str
  #
  db : Database
  kms_clt : BaseClient
  kms_key_id : str
  #
  encrypted_data_key : bytes
  iv : bytes


  def __init__(self, payload: dict, qry_params:dict, auth_claims:dict, route:str, db:Database, kms_clt:BaseClient, kms_key_id:str) :
    self.payload = payload
    self.qry_params = qry_params
    self.auth_claims = auth_claims
    #
    self.route = route
    #
    self.db = db
    self.kms_clt = kms_clt
    self.kms_key_id = kms_key_id

  def is_short_report(self) -> bool :
    return True