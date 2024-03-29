import datetime

from sqlalchemy import Column, Integer, Unicode, String, ForeignKey, Boolean, DateTime, update
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship, Session
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy_utils import EmailType

from sqlalchemy import BLOB
from covcov.application.BusinessException import BusinessException
from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema.base_domain import BaseTable
from covcov.infrastructure.kmscrypt import crypto

sql_current_zone_count = "select count(*) as current_zone_count from zone where deleted = False and room_id in (select id from room where company_id = '{company_id}' and deleted = False)"
def local_execute_after_select(db, payload_attr:dict, company_id:str) -> dict:
  current_zone_count = db.native_select_rows([sql_current_zone_count.format(company_id=company_id)])[0]
  payload_attr.update({"current_zone_count": current_zone_count["current_zone_count"][0]})
  return payload_attr

# ========
# Company
# ========
class Company(Base, BaseTable, SerializerMixin):
  __tablename__ = 'company'
  __table_args__ = {'extend_existing': True}
  OFFER_FREE    = 'FREE'
  OFFER_DISCOV  = 'DISCOV'
  OFFER_STD     = 'STD'
  OFFER_ENTR    = 'ENTR'
  OFFER_PREM    = 'PREM'
  # OFFER_PREM_PUS = 'PREM_P'
  #
  DISCOV_VISITOR_PM = 10

  id = Column(Unicode(BaseTable.SUB_SIZE), primary_key=True) # cognito:sub
  name = Column(Unicode(50), nullable=False)                 # custom:company_name
  type = Column(Unicode(10))  # ENTRE / ADMIN / REST / ...   # custom:etablissement
  siret    = Column(Unicode(14))
  address  = Column(Unicode(300))
  zip_code = Column(Unicode(10))
  country_code = Column(Unicode(2), default='FR')
  phone_number = Column(Unicode(20))
  email = Column(EmailType(length=64), unique=True, nullable=False)
  contact_fname = Column(Unicode(20))
  contact_lname = Column(Unicode(20))
  url = Column(Unicode(128))
  encrypted_data_key = Column(BLOB)
  iv  = Column(BLOB)
  #
  offer = Column(Unicode(10), default=OFFER_FREE, nullable=False)   # FREE | DISCOV | STD | ENTR | PREM
  contractual_visitor_pmonth = Column(Integer, default=DISCOV_VISITOR_PM, nullable=False)
  visitor_on_last_count   = Column(Integer, default=0, nullable=False)
  visit_on_last_count = Column(Integer, default=0, nullable=False)
  last_count_dt = Column(DateTime, default=datetime.datetime.now, nullable=False)
  #
  # contractual_visit_per_month = Column(Integer, default=VISIT_PM_DISCOV, nullable=False)
  # cumulative_visit_per_month = Column(Integer, default=0, nullable=False)
  # visit_threshold_readched = Column(Boolean(), default=False, nullable=False) # TODO: Remove it
  max_zone = Column(Integer, default=10000, nullable=False)
  #
  deleted = Column(Boolean(), default=False, nullable=False)
  creation_dt    = Column(DateTime, default=datetime.datetime.now, nullable=False)
  activation_dt = Column(DateTime, default=datetime.datetime.now, nullable=False)
  deletion_dt   = Column(DateTime)
  #
  rooms = relationship("Room", cascade="all,delete-orphan", backref="company", primaryjoin="and_(Room.company_id==Company.id, Room.deleted==False)", lazy="select" ) #  https://gist.github.com/davewsmith/ab41cc4c2a189ecd4677c624ee594db3

  @classmethod
  def enhance_payload_with_auth_token(cls, payload_attr:dict, auth_claims:dict):
    payload_attr.update({'email': auth_claims['email']})

  @classmethod
  def execute_after_select(cls, db, payload_attr:dict):
    return local_execute_after_select(db, payload_attr, payload_attr['id'])

  @classmethod
  def execute_before_insert(cls, payload_attr:dict, additionnal_ctx):
    encrypted_data_key, iv = crypto.generate_data_key(additionnal_ctx.kms_clt, additionnal_ctx.kms_key_id, cls.get_encryption_context(payload_attr['id']) )
    payload_attr['encrypted_data_key'] = encrypted_data_key
    payload_attr['iv'] = iv

  @classmethod
  def get_encryption_context(cls, id:str) -> {}:
    return {}
    # return {'company' : id }

  @classmethod
  def get_serialize_rules(cls):
    return  ('-encrypted_data_key', '-iv')

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.name}, {self.address}, {self.zip_code}, {self.country_code})"

#======
# ROOM
#======
class Room(Base, BaseTable, SerializerMixin):
  __tablename__ = 'room'
  __table_args__ = {'extend_existing': True}

  id = Column(String(10), primary_key=True)
  description = Column(String(30), nullable=False)
  company_id  = Column(Unicode(BaseTable.SUB_SIZE), ForeignKey("company.id", ondelete='CASCADE'), nullable=False)
  deleted = Column(Boolean(), default=False, nullable=False)
  creation_dt   = Column(DateTime, default=datetime.datetime.now, nullable=False)
  activation_dt = Column(DateTime, default=datetime.datetime.now, nullable=False)
  deletion_dt   = Column(DateTime)
  #
  zones = relationship("Zone", cascade="all, delete-orphan", backref="room", primaryjoin="and_( and_(Zone.room_id==Room.id, Room.deleted==False) , Zone.deleted==False)", lazy="joined")  # select=>lazy | joined=>eager
  serialize_rules = ('-company',)

  @classmethod
  def enhance_payload_with_auth_token(cls, payload_attr:dict, auth_claims:dict):
    payload_attr.update({'company_id': auth_claims['sub']})

  @classmethod
  def execute_before_upsert(cls, payload_attr:dict):
    handle_delete_flag(payload_attr)

  @classmethod
  def execute_on_update(cls, session:Session, id:str, cloned_payload:dict):
    if 'deleted' in cloned_payload :
      company_id = cloned_payload.pop('company_id')
      session.execute( update(Zone).where(Zone.room_id == id).values(cloned_payload) )

  @classmethod
  def execute_after_update(cls, db, company_id:str, cloned_payload:dict):
    if 'deleted' in cloned_payload :
      return local_execute_after_select(db, cloned_payload, company_id)

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.description}, FK.company_id={self.company_id})"


def handle_delete_flag(payload_attr:dict):
  if 'deleted' in payload_attr :
    if payload_attr.get('deleted') :
      payload_attr['deletion_dt'] = datetime.datetime.now()
    else :
      payload_attr['deletion_dt'] = None
      payload_attr['activation_dt'] = datetime.datetime.now()

#======
# ZONE
#======
''' result can be 1 or 2 values dataset; It interpretation follow the folowing priorities:
    dataset == 2 rows => Max Zone not reached yet
    dataset == 1 row  => Max Zone reached and tentative to excced max_zone '''
max_zone_sql = "select false as tentative_exceeding_max_zone, " \
               "(select count(*) from zone where deleted = False and room_id in (select id from room where company_id = '{company_id}' and deleted = False)) as current_zone_count " \
               " from company c where c.id = '{company_id}' and ( c.max_zone = -1 or c.max_zone > " \
               "(select count(*) from zone where deleted = False and room_id in (select id from room where company_id = '{company_id}' and deleted = False)) - {p_is_row} ) " \
               "union select true as tentative_exceeding_max_zone, max_zone as current_zone_count from company c where c.id = '{company_id}' " \
               "order by tentative_exceeding_max_zone"

class Zone(Base, BaseTable, SerializerMixin):
  __tablename__ = 'zone'
  __table_args__ = {'extend_existing': True}

  id = Column(String(10), primary_key=True)
  description = Column(String(30), nullable=False)
  room_id = Column(Unicode(10), ForeignKey("room.id", ondelete='CASCADE'), nullable=False)
  deleted = Column(Boolean(), default=False, nullable=False)
  creation_dt   = Column(DateTime, default=datetime.datetime.now, nullable=False)
  activation_dt = Column(DateTime, default=datetime.datetime.now, nullable=False)
  deletion_dt = Column(DateTime)
  #
  serialize_rules = ('-room',)

  @classmethod
  def execute_before_upsert(cls, payload_attr:dict):
    handle_delete_flag(payload_attr)

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.description}, FK.room_id={self.room_id})"

  @classmethod
  def is_max_zone_contract(cls, db, payload: dict, company_id:str, table:DeclarativeMeta) -> bool:
    return False;


  @classmethod
  def check_exists(cls, db, payload: dict, company_id:str, table:DeclarativeMeta) -> (bool, bool, int): # (row_exists, tentative_exceeding_max_zone, current_zone_count)
    row_exists = super().check_exists(db, payload, company_id, table)[0]
    is_delete_zone = payload.get("deleted") == True
    max_zone_list = db.native_select_rows([max_zone_sql.format(company_id=company_id, p_is_row= 1 if row_exists else 0)])[0] \
                    if cls.is_max_zone_contract(db, payload, company_id, table) else \
                    { "tentative_exceeding_max_zone":[False,None], "current_zone_count": [1,None] }
    if (len(max_zone_list["tentative_exceeding_max_zone"]) == 2) or is_delete_zone : # <-- => max_zone not reached yet
      return row_exists, max_zone_list["tentative_exceeding_max_zone"][0], \
             max_zone_list["current_zone_count"][0] -1 if is_delete_zone else max_zone_list["current_zone_count"][0] \
             if row_exists else max_zone_list["current_zone_count"][0] + 1
    else :  # <-- len(max_zone_list) == 1 => max_zone reached
      raise BusinessException( {"row_exists": row_exists, "tentative_exceeding_max_zone":
             max_zone_list["tentative_exceeding_max_zone"][0], "current_zone_count": max_zone_list["current_zone_count"][0] } )

#-- "company sub": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e" | "...f" | "...g" --#  {pfix}
def create_company(comp_id:str, comp_name:str, comp_email:str, url:str, pfix='X'):
  from covcov.infrastructure.db.database import Database
  db = Database("database")
  # Creation Company_1
  db.insert_value([f'{{"id":"{comp_id}", "name": "{comp_name}", "address": "1 - 24 Avenue Frayce", "zip_code":"93401", "phone_number":"+33661794641", "email":"{comp_email}", "url":"{url}" }}'], [Company])
  db.insert_value([f'{{"id":"{pfix}room_0.1", "description":"ROOM_0.1_", "company_id":"{comp_id}" }}'], [Room])
  db.insert_value([f'{{"id":"{pfix}z_0.1.1", "description":"Z_0.1.1", "room_id":"{pfix}room_0.1"}}'], [Zone])
  db.insert_value([f'{{"id":"{pfix}z_0.1.2", "description":"Z_0.1.2", "room_id":"{pfix}room_0.1"}}'], [Zone])
  db.insert_value([f'{{"id":"{pfix}z_0.1.3", "description":"Z_0.1.3", "room_id":"{pfix}room_0.1"}}'], [Zone])
  #
  db.insert_value([f'{{"id":"{pfix}room_0.2", "description":"ROOM_0.2_", "company_id":"{comp_id}" }}'], [Room])
  db.insert_value([f'{{"id":"{pfix}z_0.2.1", "description":"Z_0.2.1", "room_id":"{pfix}room_0.2"}}'], [Zone])
  db.insert_value([f'{{"id":"{pfix}z_0.2.2", "description":"Z_0.2.2", "room_id":"{pfix}room_0.2"}}'], [Zone])
  #
  db.insert_value([f'{{"id":"{pfix}room_0.3", "description":"ROOM_0.3_", "company_id":"{comp_id}" }}'], [Room])
  db.insert_value([f'{{"id":"{pfix}z_0.3.1", "description":"Z_0.3.1", "room_id":"{pfix}room_0.3"}}'], [Zone])

  # Creation Company_2
  db.insert_value([f'{{"id":"{comp_id[:-1]}+", "name": "2_{comp_name}", "address": "2 - 24 Avenue Frayce", "zip_code":"93402", "phone_number":"+33661794642", "email":"2_{comp_email}" }}'], [Company])
  db.insert_value([f'{{"id":"{pfix}room_2.1", "description":"ROOM_2.1_", "company_id":"{comp_id[:-1]}+" }}'], [Room])
  db.insert_value([f'{{"id":"{pfix}z_2.1.1", "description":"Z_2.1.1", "room_id":"{pfix}room_2.1"}}'], [Zone])
  db.insert_value([f'{{"id":"{pfix}z_2.1.2", "description":"Z_2.1.2", "room_id":"{pfix}room_2.1"}}'], [Zone])
  db.insert_value([f'{{"id":"{pfix}z_2.1.3", "description":"Z_2.1.3", "room_id":"{pfix}room_2.1"}}'], [Zone])
  #
  db.insert_value([f'{{"id":"{pfix}room_2.2", "description":"ROOM_2.2_", "company_id":"{comp_id[:-1]}+" }}'], [Room])
  db.insert_value([f'{{"id":"{pfix}z_2.2.1", "description":"Z_2.2.1", "room_id":"{pfix}room_2.2"}}'], [Zone])
  db.insert_value([f'{{"id":"{pfix}z_2.2.2", "description":"Z_2.2.2", "room_id":"{pfix}room_2.2"}}'], [Zone])

  # Creation Company_3
  db.insert_value([f'{{"id":"{comp_id[:-2]}-", "name": "3_{comp_name}", "address": "3 - 24 Avenue Frayce", "zip_code":"93403", "phone_number":"+33661794643", "email":"3_{comp_email}"}}'], [Company])
  db.insert_value([f'{{"id":"{pfix}room_3.1", "description":"ROOM_3.1_", "company_id":"{comp_id[:-2]}-" }}'], [Room])
  db.insert_value([f'{{"id":"{pfix}z_3.1.1", "description":"Z_3.1.1", "room_id":"{pfix}room_3.1"}}'], [Zone])
  db.insert_value([f'{{"id":"{pfix}z_3.1.2", "description":"Z_3.1.2", "room_id":"{pfix}room_3.1"}}'], [Zone])


if __name__ == '__main__':
  pass
  # create_company("7c791fa9-5774-46d4-88f3-1134d08ef212", "alf", "wharouny.tp@gmail.com", "https://www.lemonde.fr/", "")
  # create_company("57976c93-cd46-44c4-82c1-6271abc0c319", "covcov", "yohan.obadia@gmail.com", "https://www.mcdonalds.fr/", "Y")
  #
  # db.insert_value([f'{{"id":"comp_2", "address": "24 Avenue Frayce", "zip_code":"93400"}}'], [Company])
  # session = sessionmaker(bind=engine)
  # session = Session(engine)
  # session.add(Company(f'{{"id":"comp_1", "address": "24 Avenue Frayce", "zip_code":"93400"}}'))
  # session.commit()