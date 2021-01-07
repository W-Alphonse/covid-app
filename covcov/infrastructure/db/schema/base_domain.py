from sqlalchemy.orm import Session


class BaseTable :
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
  def preprocess_before_upsert(cls, payload_attr:dict):
    pass

  @classmethod
  def execute_on_update(cls, session:Session, id: str, payload_attr:dict):
    pass

