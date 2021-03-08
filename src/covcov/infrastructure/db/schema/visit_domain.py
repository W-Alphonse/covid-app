import datetime
import hashlib

import dateutil
from sqlalchemy import Column, Unicode, ForeignKey, DateTime, BigInteger, SmallInteger, insert
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Session
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import BLOB

from covcov.application.BusinessException import BusinessException
from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema import company_domain
from covcov.infrastructure.db.schema.base_domain import BaseTable
from covcov.infrastructure.kmscrypt import crypto

"""--SQL Pour CAS CONTACT--"""
# v1 --> Alias of the infected Visitor / v2 --> Alias of other Visitors
raw_select     = "SELECT (select c.name FROM company c where c.id=v2.company_id) as company, (select r.description FROM room r where r.id=v2.room_id) as room, "\
                 "(select z.description FROM zone z where z.id=v2.zone_id) as zone, " \
                 "to_char(v2.visit_datetime,'YYYY-MM-DD HH24:MI:SS') as visit_datetime, v2.fname, v2.lname, v2.phone_number, v2.visitor_id {}"
summary_select = "SELECT count(distinct(v2.phone_number)) as nb_cases, count(distinct(v2.zone_id)) as nb_zones, (max(v2.visit_datetime)::date - min(v2.visit_datetime)::date) as nb_days {}"
contact_select_for_short_report = "SELECT v2.fname, v2.lname, v2.phone_number, v2.visitor_id {}"
contact_select = "SELECT v2.fname, v2.lname, v2.phone_number, v2.visitor_id, " \
                 "(SELECT count(1) {} and vv2.zone_id = vv1.zone_id and vv2.phone_number = v2.phone_number ) as nb_contacts, "\
                 "count(distinct(v2.zone_id)) as nb_zones, to_char(min(v2.visit_datetime),'YYYY-MM-DD HH24:MI:SS') as min_date, to_char(max(v2.visit_datetime),'YYYY-MM-DD HH24:MI:SS') as max_date {}"
exists_select  = "SELECT exists (SELECT 1 FROM visit as v1 where {})"
#
main_qry = "FROM visit as {}1 inner join public.visit as {}2 on {}1.zone_id = {}2.zone_id where {}"
group_by_for_short_report = " GROUP BY v2.phone_number, v2.visitor_id, v2.fname, v2.lname"
group_by = group_by_for_short_report + " ORDER BY nb_contacts desc"
#
criteria_phone   = "({}1.phone_number = {} and {}2.phone_number <> {})"
criteria_visitor = "({}1.visitor_id = {} and {}2.visitor_id <> {})"
# criteria_visit_dt = "({}2.visit_datetime between {}1.visit_datetime - interval '{} minute' and {}1.visit_datetime + interval '{} minute')"
# https://stackoverflow.com/questions/325933/determine-whether-two-date-ranges-overlap
criteria_visit_dt = "({0}1.visit_s_datetime <= {0}1.visit_e_datetime)"
criteria_company  = "({}1.company_id = '{}' and {}2.company_id = '{}')"
#
criteria_phone_exists   = "{}1.phone_number = {}"
criteria_visitor_exists = "{}1.visitor_id = {}"
criteria_company_exists = "{}1.company_id = '{}'"

company_attributes_select = "select c.url, c.offer, (c.visitor_on_last_count > c.contractual_visitor_pmonth) as allowed_visitor_count_exceeded, encode(c.encrypted_data_key,'hex') as encrypted_data_key, encode(c.iv,'hex') as iv from company c where c.id='{}' "

# ========
#  Visit
# ========
class Visit(Base, BaseTable, SerializerMixin):
  __tablename__ = 'visit'
  __table_args__ = {'extend_existing': True}
  ciphered_flds = ['phone_number', 'visitor_id', 'fname', 'lname']

  #
  id = Column(BigInteger, primary_key=True)
  company_id  = Column(Unicode(BaseTable.SUB_SIZE), ForeignKey("company.id"), nullable=False)
  room_id     = Column(Unicode(10), ForeignKey("room.id"), nullable=False)
  zone_id     = Column(Unicode(10), ForeignKey("zone.id"), nullable=False)
  #
  visitor_id  = Column(BLOB)
  phone_number = Column(BLOB)
  fname = Column(BLOB)
  lname = Column(BLOB)
  visit_datetime = Column(DateTime, default=datetime.datetime.now, nullable=False)
  visit_s_datetime = Column(DateTime, default=datetime.datetime.now, nullable=False)
  visit_e_datetime = Column(DateTime, default=datetime.datetime.now, nullable=False)
  # minutes_bfore_visit_dt = Column(SmallInteger, default=0, nullable=False)
  # minutes_after_visit_dt = Column(SmallInteger, default=0, nullable=False)
  #
  # _visitor_id  = Column(Unicode(15))
  # _phone_number = Column(Unicode(20))
  # _fname = Column(Unicode(30))
  # _lname = Column(Unicode(30))

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.company.description}, {self.room.description}, {self.zone.description}, {self.visit_datetime})"

  @classmethod
  def select_company_attributes(cls, comp_id:str) -> str :
    return company_attributes_select.format(comp_id)

  @classmethod
  def decrypt_result(cls, result_to_decrypt:dict, c) -> {} :
    result_to_decrypt['fname'] = cls.decrypt(result_to_decrypt, 'fname', c)
    result_to_decrypt['lname'] = cls.decrypt(result_to_decrypt, 'lname', c)
    result_to_decrypt['phone_number'] = cls.decrypt(result_to_decrypt, 'phone_number', c)
    result_to_decrypt['visitor_id']   = cls.decrypt(result_to_decrypt, 'visitor_id', c)
    return result_to_decrypt

  @classmethod
  def decrypt(cls, contact:dict, attr_name:str, c):
    return crypto.decrypt([attr_value for attr_value in contact[attr_name]], c.kms_clt, c.encrypted_data_key, c.iv, encryption_context={})

  @classmethod
  def execute_on_insert(cls, session:Session, id: str, cloned_payload:dict):
    cloned_payload.pop('fname', None)
    cloned_payload.pop('lname', None)
    #
    cls.sha256_att_payload(cloned_payload, 'phone_number')
    cls.sha256_att_payload(cloned_payload, 'visitor_id')
    session.execute(insert(VisitHist).values(cloned_payload) )

  @classmethod
  def sha256_att_payload(cls, payload:dict, att_name:str):
    att_value = payload.pop(att_name, None)
    if att_value is not None:
      payload[att_name] = hashlib.sha256(att_value).digest()

  @classmethod
  def compose_ccontact_result(cls, result_keys:[], result_list:[dict], c) -> {} :
    data = {}
    if not c.is_short_report() :
      data[cls.RAW_DATA] = cls.decrypt_result(result_list[result_keys.index(cls.RAW_DATA)], c)
      data[cls.SUMMARY]  = result_list[result_keys.index(cls.SUMMARY)]
    data[cls.CONTACTS] = cls.decrypt_result( result_list[result_keys.index(cls.CONTACTS)], c)
    exists             = result_list[result_keys.index(cls.EXISTS)]
    #
    result = {}
    # result['code'] = 0 if len(data[cls.RAW_DATA]['company']) > 0 else \
    result['code'] = 0 if (len(data[cls.CONTACTS]['phone_number']) > 0) or (len(data[cls.CONTACTS]['visitor_id']) > 0) else \
                     1 if exists['exists'][0] == True else 2
    result['description'] =  'Données disponibles' if result['code'] == 0 else \
                             'Aucun cas contact trouvé' if result['code'] == 1 else "L identificateur saisi n existe pas en base"
    result['data'] = data
    return result

    sql_stmts_kv = vd.Visit.compose_ccontact_sqls(payload[type])
    result_list = db.native_select_rows(sql_stmts_kv.values())

  RAW_DATA = 'raw_data'
  SUMMARY  = 'summary'
  CONTACTS = 'contacts'
  EXISTS   = 'exists'
  @classmethod
  def compose_ccontact_sqls(cls, criteria:dict, c) -> {} :
    cls.visit_encrypt_data(criteria, c, True)
    qry_from  = cls._compose_criteria_sql(criteria, 'v')
    inner_qry_from = cls._compose_criteria_sql(criteria, 'vv')
    #
    sqls = {}
    if not c.is_short_report() :
      sqls[cls.RAW_DATA] = raw_select.format(qry_from)
      sqls[cls.SUMMARY]  = summary_select.format(qry_from)
    sqls[cls.CONTACTS] =  contact_select_for_short_report.format(qry_from)  + group_by_for_short_report \
                          if c.is_short_report() else contact_select.format(inner_qry_from, qry_from) + group_by
    sqls[cls.EXISTS]   = cls._compose_criteria_exists(criteria, 'v')
    return sqls

  def _compose_criteria_sql(criteria:dict, v_alias:str) -> str :
    # b = s.strip() if s and s.strip() else 'None'
    phone = criteria.get('phone_number')
    phone = phone.strip() if phone and phone.strip() else None
    #
    vid =  criteria.get('visitor_id')
    vid =  vid.strip() if vid and vid.strip() else None
    #
    # mbv = criteria.get('m_before_visit')
    # mbv = mbv.strip() if mbv and mbv.strip() else 1
    #
    # mav = criteria.get('m_after_visit')
    # mav = mbv.strip() if mav and mav.strip() else 1
    # mbv = 0 if criteria.get('m_before_visit') is None else criteria.get('m_before_visit')
    # mav = 0 if criteria.get('m_after_visit') is None else criteria.get('m_after_visit')
    # 1 - Add phone_number + visitor_id Criteria
    criteria_sql = criteria_visitor.format(v_alias, vid, v_alias, vid)   if phone == None else \
                   criteria_phone.format(v_alias, phone, v_alias, phone) if vid   == None else \
                   '({} or {})'.format(criteria_visitor.format(v_alias, vid, v_alias, vid)  , criteria_phone.format(v_alias, phone, v_alias, phone))
    # 2 - Add company_id Criteria
    if criteria.get('company_id') is not None :
      criteria_sql = '{} and {}'.format( criteria_company.format(v_alias, criteria.get('company_id'), v_alias, criteria.get('company_id')), criteria_sql)
    # 3 - Add visit_datetime Criteria
    # criteria_sql = '{} and {}'.format(criteria_sql, criteria_visit_dt.format(v_alias, v_alias, mbv, v_alias, mav) )
    criteria_sql = '{} and {}'.format(criteria_sql, criteria_visit_dt.format(v_alias) )
    #
    return main_qry.format(v_alias, v_alias, v_alias, v_alias, criteria_sql)

  def _compose_criteria_exists(criteria:dict, v_alias:str) -> str :
    phone = criteria.get('phone_number')
    vid =  criteria.get('visitor_id')
    # mbv = 0 if criteria.get('m_before_visit') is None else criteria.get('m_before_visit')
    # mav = 0 if criteria.get('m_after_visit') is None else criteria.get('m_after_visit')
    # 1 - Add phone_number + visitor_id Criteria
    criteria_sql = criteria_visitor_exists.format(v_alias, vid) \
                   if phone == None else criteria_phone_exists.format(v_alias, phone) \
                   if vid   == None else '({} or {})'.format(criteria_visitor_exists.format(v_alias, vid)  , criteria_phone_exists.format(v_alias, phone))
    # 2 - Add company_id Criteria
    if criteria.get('company_id') is not None :
      criteria_sql = '{} and {}'.format( criteria_company_exists.format(v_alias, criteria.get('company_id')), criteria_sql)
    # 3 - Add exists visitor Check
    return exists_select.format(criteria_sql)

  @classmethod
  def execute_before_upsert(cls, attr:dict):
    if ('visitor_id' in attr) and (not bool(attr.get('visitor_id'))) :
       attr.pop('visitor_id')
    if ('phone_number' in attr) and (not bool(attr.get('phone_number'))) :
      attr.pop('phone_number')

  @classmethod
  def execute_before_insert(cls, payload_attr:dict, additionnal_ctx):
    cls.visit_encrypt_data(payload_attr, additionnal_ctx)
    payload_attr['visit_datetime'] = datetime.datetime.now()
    #
    minutes_bfore_visit_dt = dateutil.relativedelta.relativedelta(minutes=payload_attr.get('minutes_bfore_visit_dt',0))
    minutes_after_visit_dt = dateutil.relativedelta.relativedelta(minutes=payload_attr.get('minutes_after_visit_dt',0))
    payload_attr['visit_s_datetime'] = payload_attr['visit_datetime'] - minutes_bfore_visit_dt
    payload_attr['visit_e_datetime'] = payload_attr['visit_datetime'] + minutes_after_visit_dt
    payload_attr.pop("minutes_bfore_visit_dt",None)
    payload_attr.pop("minutes_after_visit_dt",None)

  @classmethod
  def visit_encrypt_data(cls, payload_attr:dict, additionnal_ctx, b64_encode=False):
    b64_enc_data, binary_enc_data = cls.get_visit_encrypted_data(payload_attr, additionnal_ctx)
    i = 0
    for id in Visit.ciphered_flds :
      if bool(payload_attr.get(id)) :
        # payload_attr[f'_{id}']  = payload_attr[id]
        payload_attr[id] = binary_enc_data[i] if not b64_encode else f"decode('{b64_enc_data[i]}', 'base64')"
        i +=1

  @classmethod
  def get_visit_encrypted_data(cls, payload_attr:dict, additionnal_ctx) -> (str, bytes):  # b64_enc_data, binary_enc_data
    datas = [ payload_attr.get(ciphered_fld)  for ciphered_fld in Visit.ciphered_flds if bool(payload_attr.get(ciphered_fld))]
    return crypto.encrypt(datas, additionnal_ctx.kms_clt, additionnal_ctx.encrypted_data_key, additionnal_ctx.iv,
                          company_domain.Company.get_encryption_context(payload_attr['company_id']) )


  @classmethod
  def check_business_rules_for_upsert(cls, attr:dict):
    if (attr.get('company_id') is None) or (attr.get('room_id') is None) or (attr.get('zone_id') is None)  :
      raise ValueError(f"'Visit' entity instance should reference a well identified location => Indicate 'company_id, room_id and zone_id' ")
    #
    if ( (attr.get('phone_number') is None)  and (attr.get('visitor_id') is None)  ):
      raise ValueError(f"'Visit' entity instance should reference a well identified client => Either indicate 'phone_number' or 'visitor_id' ")

  @classmethod
  def check_business_rules_for_insert(cls, payload_attr:dict, additionnal_ctx=None):
    if datetime.datetime.now().day != 1 :
      if (additionnal_ctx.offer == 'FREE') and (additionnal_ctx.allowed_visitor_count_exceeded == True) :
        raise BusinessException( {"offer" : additionnal_ctx.offer, "allowed_visitor_count_exceeded" : additionnal_ctx.allowed_visitor_count_exceeded,
                                  "error" : "Excessive use of Covcov: The 'count of user' exceeds the 'contracted allowed user'"})
      # sql = "select offer, contractual_visitor_pmonth, visitor_on_last_count, visit_on_last_count, last_count_dt from company where id = '{0}' and visitor_on_last_count > contractual_visitor_pmonth"
      # # sql = "select offer, contractual_visitor_pmonth, visitor_on_last_count, visit_on_last_count, last_count_dt from company where id = '{0}' "
      # companies = db.native_select_rows([sql.format(attr.get('company_id')) ])[0]
      # if len(companies["contractual_visitor_pmonth"]) != 0 :
      #   if companies["visitor_on_last_count"][0] > companies["contractual_visitor_pmonth"][0] :
      #     raise BusinessException( {"offer" : companies["offer"][0], "contractual_visitor_pmonth" : companies["contractual_visitor_pmonth"][0],
      #           "visitor_on_last_count" : companies["visitor_on_last_count"][0], "last_count_dt" : companies["last_count_dt"][0].strftime("%Y-%m-%d %H:%M:%S"),
      #           "error" : "Excessive use of Covcov: The 'count of user' exceeds the 'contracted allowed user'"})

  @classmethod
  def check_business_rules_for_select(cls, attr:dict):
    location_criteria_is_missing = (attr.get('company.address') is None) or (attr.get('company.zip_code') is None) or (attr.get('company.country_code') is None)
    visiting_date_criteria_is_missing = attr.get('visit_date') is None
    visitor_identification_criteria_is_missing = attr.get('visitor_phone_number') is None
    # visitor_identification_criteria_is_missing = ( (attr.get('visitor_fname') is None) or (attr.get('visitor_lname') is None) or (attr.get('visitor_phone_number') is None) ) and (attr.get('visitor_id') is None)
    #
    if location_criteria_is_missing and visitor_identification_criteria_is_missing :
      raise ValueError(f"Either should indicate a 'location of interest' or a 'person of interest'")
    #
    if visiting_date_criteria_is_missing :
      raise ValueError(f"Please indicate 'visiting date' before search")

  # @classmethod
  # def compose_purge_sqls(cls, days_count:float, chunk_size:int):
  #   dt = datetime.datetime.now() - datetime.timedelta(days=days_count)
  #   str_now = datetime.datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")
  #   sql = []
  #   sql.append(insert_hist.format(str_now, chunk_size))
  #   sql.append(delete_visit.format(str_now, chunk_size))
  #   return sql

# ============
#  VisitHisto   sha256(c.name::bytea)
# ============
# delete_visit = "delete from visit where id = any (array(SELECT id FROM visit where visit_datetime < TIMESTAMP '{}' limit {})) "
# insert_hist = "insert into visit_histo(id, company_id, room_id, zone_id, visitor_id, phone_number, visit_datetime, creation_dt) " \
#               "select id, company_id, room_id, zone_id, sha256(visitor_id::bytea) as visitor_id, sha256(phone_number::bytea) as phone_number, visit_datetime, now() from visit where visit_datetime < TIMESTAMP '{}' limit {} "

class VisitHist(Base, BaseTable, SerializerMixin):
  __tablename__ = 'visit_histo'
  __table_args__ = {'extend_existing': True}
  #
  id = Column(BigInteger, primary_key=True)
  company_id  = Column(Unicode(BaseTable.SUB_SIZE), ForeignKey("company.id"), nullable=False)
  room_id     = Column(Unicode(10), ForeignKey("room.id"), nullable=False)
  zone_id     = Column(Unicode(10), ForeignKey("zone.id"), nullable=False)
  #
  # visitor_id  = Column(BYTEA(32))
  # phone_number = Column(BYTEA(32))
  visitor_id  = Column(BLOB)
  phone_number = Column(BLOB)
  visit_datetime = Column(DateTime, nullable=False)
  visit_s_datetime = Column(DateTime, nullable=False)
  visit_e_datetime = Column(DateTime, nullable=False)
  creation_dt    = Column(DateTime, default=datetime.datetime.now, nullable=False)

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.company.description}, {self.room.description}, {self.zone.description}, {self.visit_datetime})"



def create_visit(comp_id:str, pfix='X') :
  from covcov.infrastructure.db.database import Database
  db = Database("database")
        # db.insert_value(['{"id":"visit_1", "company_id": comp_id, "room_id": "room_100.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De La Fontaine", "visitor_phone_number": "0661794641" }'], [Visit])
  # Visit on ROOM_1 / z_0.1.1                                                                                               +33611123262
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.1", "phone_number": "+33611223262" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.1", "phone_number": "+33611223263" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.1", "phone_number": "+33611223264" }}'], [Visit])
  # Visit on ROOM_1 / z_0.1.3
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.3", "phone_number": "+33611223262" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.3", "phone_number": "+33611223271" }}'], [Visit])
  # Visit on ROOM_2 / z_0.2.1
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.1", "phone_number": "+33611223262" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.1", "phone_number": "+33611223281" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.1", "phone_number": "+33611223264" }}'], [Visit])
  # Visit on ROOM_2 / z_0.2.2
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.2", "phone_number": "+33611223291" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.2", "phone_number": "+33611223292" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.2", "phone_number": "+33611223263" }}'], [Visit])


if __name__ == '__main__':
  pass
  # create_visit("7c791fa9-5774-46d4-88f3-1134d08ef212", "")
  # create_visit("57976c93-cd46-44c4-82c1-6271abc0c319", "Y")
  #
  # sess = db.session()
  # sess.add(Visit({"id":"visit_3", "company_id": "comp_1", "room_id": "room_1.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De Lafontaine" }))
