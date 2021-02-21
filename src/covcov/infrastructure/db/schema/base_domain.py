from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session


class BaseTable:
  SUB_SIZE = 36

  @classmethod
  def check_business_rules_for_upsert(cls, payload_attr:dict):
    pass

  @classmethod
  def check_business_rules_for_select(cls, payload_attr:dict):
    pass

  @classmethod
  def enhance_payload_with_auth_token(cls, payload_attr:dict, auth_claims:dict):
    pass

  @classmethod
  def execute_before_upsert(cls, payload_attr:dict):
    pass

  @classmethod
  def execute_before_insert(cls, payload_attr:dict, additionnal_ctx=None):
    pass

  @classmethod
  def execute_on_insert(cls, session:Session, id: str, payload_attr:dict):
    pass

  @classmethod
  def execute_on_update(cls, session:Session, id: str, payload_attr:dict):
    pass

  @classmethod
  def execute_after_update(cls, db, id: str, payload_attr:dict):
    pass

  @classmethod
  def execute_after_select(cls, db, payload_attr:dict):
    pass

  @classmethod
  def get_serialize_rules(cls):
    return ()

  @classmethod
  def check_exists(cls, db, payload:dict, company_id:str, table:DeclarativeMeta) -> (bool, int): # row_exists, tentative_exceeding_max_zone, current_zone_count
    return ( db.native_execute_sqls([f"select 1 from {table.__name__} where id = '{payload['id']}'" ])[0] != 0, False, None)