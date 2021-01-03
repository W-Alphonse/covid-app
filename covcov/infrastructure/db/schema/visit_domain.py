import datetime
from sqlalchemy import Column, Unicode, ForeignKey, DateTime, Integer, Sequence, BigInteger
from sqlalchemy_serializer import SerializerMixin

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema.base_domain import BaseTable

"""--SQL Pour CAS CONTACT--"""
# v1 --> Alias of the infected Visitor / v2 --> Alias of other Visitors
raw_select     = "SELECT (select c.name FROM company c where c.id=v2.company_id) as company, (select r.description FROM room r where r.id=v2.room_id) as room, "\
                 "(select z.description FROM zone z where z.id=v2.zone_id) as zone, " \
                 "to_char(v2.visit_datetime,'YYYY-MM-DD HH24:MI:SS') as visit_datetime, v2.fname, v2.lname, v2.phone_number, v2.visitor_id {}"
summary_select = "SELECT count(distinct(v2.phone_number)) as nb_cases, count(distinct(v2.zone_id)) as nb_zones, (max(v2.visit_datetime)::date - min(v2.visit_datetime)::date) as nb_days {}"
contact_select = "SELECT v2.fname, v2.lname, v2.phone_number, v2.visitor_id, " \
                 "(SELECT count(1) {} and vv2.zone_id = vv1.zone_id and vv2.phone_number = v2.phone_number ) as nb_contacts, "\
                 "count(distinct(v2.zone_id)) as nb_zones, to_char(min(v2.visit_datetime),'YYYY-MM-DD HH24:MI:SS') as min_date, to_char(max(v2.visit_datetime),'YYYY-MM-DD HH24:MI:SS') as max_date {}"
exists_select  = "SELECT exists (SELECT 1 FROM visit as v1 where {})"
#
main_qry = "FROM visit as {}1 inner join public.visit as {}2 on {}1.zone_id = {}2.zone_id where {}"
group_by = " GROUP BY v2.phone_number, v2.visitor_id, v2.fname, v2.lname ORDER BY nb_contacts desc"
#
criteria_phone   = "({}1.phone_number = '{}' and {}2.phone_number <> '{}')"
criteria_visitor = "({}1.visitor_id = '{}' and {}2.visitor_id <> '{}')"
criteria_visit_dt = "({}2.visit_datetime between {}1.visit_datetime - interval '{} hour' and {}1.visit_datetime + interval '{} hour')"
criteria_company  = "({}1.company_id = '{}' and {}2.company_id = '{}')"
#
criteria_phone_exists   = "{}1.phone_number = '{}'"
criteria_visitor_exists = "{}1.visitor_id = '{}'"
criteria_company_exists = "{}1.company_id = '{}'"

company_url_select = "select c.url from company c where c.id='{}' "

# ========
#  Visit
# ========
class Visit(Base, BaseTable, SerializerMixin):
  __tablename__ = 'visit'
  __table_args__ = {'extend_existing': True}

  #
  id = Column(BigInteger, primary_key=True)
  company_id  = Column(Unicode(BaseTable.SUB_SIZE), ForeignKey("company.id"), nullable=False)
  room_id     = Column(Unicode(10), ForeignKey("room.id"), nullable=False)
  zone_id     = Column(Unicode(10), ForeignKey("zone.id"), nullable=False)
  #
  visitor_id  = Column(Unicode(15))
  phone_number = Column(Unicode(20))
  fname = Column(Unicode(20))
  lname = Column(Unicode(20))
  visit_datetime = Column(DateTime, default=datetime.datetime.now(), nullable=False)

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.company.description}, {self.room.description}, {self.zone.description}, {self.visit_datetime})"

  @classmethod
  def select_company_url(cls, comp_id:str) -> str :
    return company_url_select.format(comp_id)


  @classmethod
  def compose_ccontact_result(cls, result_keys:[], result_list:[dict]) -> {} :
    data = {}
    data[cls.RAW_DATA] = result_list[result_keys.index(cls.RAW_DATA)]
    data[cls.SUMMARY]  = result_list[result_keys.index(cls.SUMMARY)]
    data[cls.CONTACTS] = result_list[result_keys.index(cls.CONTACTS)]
    exists             = result_list[result_keys.index(cls.EXISTS)]
    #
    result = {}
    result['code'] = 0 if len(data[cls.RAW_DATA]['company']) > 0 else \
                     1 if exists['exists'] else 2
    result['description'] =  'Données disponibles' if result['code'] == 0 else \
                             'Aucun cas contact trouvé' if result['code'] == 0 else "L identificateur saisi n existe pas en base"
    result['data'] = data
    return result

    sql_stmts_kv = vd.Visit.compose_ccontact_sqls(payload[type])
    result_list = db.native_select_rows(sql_stmts_kv.values())

  RAW_DATA = 'raw_data'
  SUMMARY  = 'summary'
  CONTACTS = 'contacts'
  EXISTS   = 'exists'
  @classmethod
  def compose_ccontact_sqls(cls, criteria:dict) -> {} :
    qry_from  = cls._compose_criteria_sql(criteria, 'v')
    inner_qry_from = cls._compose_criteria_sql(criteria, 'vv')
    #
    sqls = {}
    sqls[cls.RAW_DATA] = raw_select.format(qry_from)
    sqls[cls.SUMMARY]  = summary_select.format(qry_from)
    sqls[cls.CONTACTS] = contact_select.format(inner_qry_from, qry_from) + group_by
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
    # hbv = criteria.get('h_before_visit')
    # hbv = hbv.strip() if hbv and hbv.strip() else 1
    #
    # hav = criteria.get('h_after_visit')
    # hav = hbv.strip() if hav and hav.strip() else 1
    hbv = 1 if criteria.get('h_before_visit') is None else criteria.get('h_before_visit')
    hav = 1 if criteria.get('h_after_visit') is None else criteria.get('h_after_visit')
    # 1 - Add phone_number + visitor_id Criteria
    criteria_sql = criteria_visitor.format(v_alias, vid, v_alias, vid)   if phone == None else \
                   criteria_phone.format(v_alias, phone, v_alias, phone) if vid   == None else \
                   '({} or {})'.format(criteria_visitor.format(v_alias, vid, v_alias, vid)  , criteria_phone.format(v_alias, phone, v_alias, phone))
    # 2 - Add company_id Criteria
    if criteria.get('company_id') is not None :
      criteria_sql = '{} and {}'.format( criteria_company.format(v_alias, criteria.get('company_id'), v_alias, criteria.get('company_id')), criteria_sql)
    # 3 - Add visit_datetime Criteria
    criteria_sql = '{} and {}'.format(criteria_sql, criteria_visit_dt.format(v_alias, v_alias, hbv, v_alias, hav) )
    #
    return main_qry.format(v_alias, v_alias, v_alias, v_alias, criteria_sql)

  def _compose_criteria_exists(criteria:dict, v_alias:str) -> str :
    phone = criteria.get('phone_number')
    vid =  criteria.get('visitor_id')
    hbv = 1 if criteria.get('h_before_visit') is None else criteria.get('h_before_visit')
    hav = 1 if criteria.get('h_after_visit') is None else criteria.get('h_after_visit')
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
  def check_business_rules_for_upsert(cls, attr:dict):
    if (attr.get('company_id') is None) or (attr.get('room_id') is None) or (attr.get('zone_id') is None)  :
      raise ValueError(f"'Visit' entity instance should reference a well identified location => Indicate 'company_id, room_id and zone_id' ")
    #
    if ( (attr.get('phone_number') is None)  and (attr.get('visitor_id') is None)  ):
      raise ValueError(f"'Visit' entity instance should reference a well identified client => Either indicate 'phone_number' or 'visitor_id' ")


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


def create_visit(comp_id:str, pfix='X') :
  from covcov.infrastructure.db.database import Database
  db = Database("database")
        # db.insert_value(['{"id":"visit_1", "company_id": comp_id, "room_id": "room_100.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De La Fontaine", "visitor_phone_number": "0661794641" }'], [Visit])

  # Visit on ROOM_1 / z_0.1.1
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.1", "phone_number": "3262_" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.1", "phone_number": "3263" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.1", "phone_number": "3264" }}'], [Visit])

  # Visit on ROOM_1 / z_0.1.3
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.3", "phone_number": "3262_" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.1", "zone_id": "{pfix}z_0.1.3", "phone_number": "3271" }}'], [Visit])

  # Visit on ROOM_2 / z_0.2.1
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.1", "phone_number": "3262_" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.1", "phone_number": "3281" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.1", "phone_number": "3264" }}'], [Visit])

  # Visit on ROOM_2 / z_0.2.2
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.2", "phone_number": "3291" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.2", "phone_number": "3292" }}'], [Visit])
  db.insert_value([f'{{"company_id": "{comp_id}", "room_id": "{pfix}room_0.2", "zone_id": "{pfix}z_0.2.2", "phone_number": "3263" }}'], [Visit])


if __name__ == '__main__':
  pass
  # create_visit("57976c93-cd46-44c4-82c1-6271abc0c319", "Y")
  #
  # sess = db.session()
  # sess.add(Visit({"id":"visit_3", "company_id": "comp_1", "room_id": "room_1.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De Lafontaine" }))
