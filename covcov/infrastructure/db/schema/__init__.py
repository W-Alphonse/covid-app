class BaseTable :
  EMAIL_SIZE = 64

  @classmethod
  def check_business_rules_for_upsert(cls, attr:dict):
    pass

  @classmethod
  def check_business_rules_for_select(cls, attr:dict):
    pass