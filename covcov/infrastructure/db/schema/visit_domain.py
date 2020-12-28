import datetime
from sqlalchemy import Column, Unicode, ForeignKey, DateTime, Integer, Sequence, BigInteger
from sqlalchemy_serializer import SerializerMixin

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema.base_domain import BaseTable

# v1 --> Alias of the infected Visitor / v2 --> Alias of other Visitors
raw_select     = "SELECT v2.company_id, v2.room_id, v2.zone_id, v2.phone_number, v2.visit_datetime, v2.visitor_id, v2.fname, v2.lname {}"
summary_select = "SELECT count(distinct(v2.phone_number)) as nb_cases, count(distinct(v2.zone_id)) as nb_zones, max(v2.visit_datetime) - min(v2.visit_datetime) nb_days {}"
contact_select = "SELECT v2.fname, v2.lname, v2.phone_number, v2.visitor_id, count(distinct(v2.zone_id)) as nb_zones, " \
                 "(SELECT count(1) {} and vv2.zone_id = vv1.zone_id and vv2.phone_number = v2.phone_number ) as nb_contacts, "\
                 "min(v2.visit_datetime) as min_date, max(v2.visit_datetime) as max_date {}"
              #  select v2.fname, v2.lname, v2.phone_number, v2.visitor_id, count(distinct(v2.zone_id)) as nb_zones,
# nb_cases = "select count(1) FROM public.visit as vv1 inner join public.visit as vv2 on vv1.zone_id = vv2.zone_id
# where
# vv1.phone_number = '3262_' and vv2.phone_number <> '3262_' and
# vv2.zone_id = vv1.zone_id and vv2.phone_number = v2.phone_number"
#
main_qry = "FROM public.visit as {}1 inner join public.visit as {}2 on {}1.zone_id = {}2.zone_id where {}"
group_by = " GROUP BY v2.phone_number, v2.visitor_id, v2.fname, v2.lname"
#
criteria_phone   = "({}1.phone_number = '{}' and {}2.phone_number <> '{}')"
criteria_visitor = "({}1.visitor_id = '{}' and {}2.visitor_id <> '{}') "
criteria_visit_dt = "({}2.visit_datetime between {}1.visit_datetime - interval '{} hour' and {}1.visit_datetime + interval '{} hour')"
criteria_company  = "({}1.company_id = '{}' and {}2.company_id = '{}')"
# TODO: TEST Scoped search to Company => Add 'company_id' as selection criteria



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
  visit_datetime = Column(DateTime, default=datetime.datetime.now())

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.company.description}, {self.room.description}, {self.zone.description}, {self.visit_datetime})"

  @classmethod
  def compose_ccontact_sql(cls, criteria:dict) -> [str] :
    sqls = []
    # sqls.append(cls.compose_ccontact_sql_raw(criteria))
    return cls.compose_ccontact_sql_raw(criteria)

  @classmethod
  def compose_ccontact_sql_raw(cls, criteria:dict) -> str :
    # phone = criteria.get('phone_number')
    # vid =  criteria.get('visitor_id')
    # hbv = 1 if criteria.get('h_before_visit') is None else criteria.get('h_before_visit')
    # hav = 1 if criteria.get('h_after_visit') is None else criteria.get('h_after_visit')
    # #
    # def _compose_criteria_sql(cls, v_alias:str) -> str :
    #   criteria_sql = criteria_visitor.format(v_alias, vid, v_alias, vid)   if phone == None else \
    #                  criteria_phone.format(v_alias, phone, v_alias, phone) if vid == None else \
    #                  '{} or {}'.format(criteria_visitor.format(v_alias, vid, v_alias, vid)  , criteria_phone.format(v_alias, phone, v_alias, phone))
    #   criteria_sql = '{} and {}'.format(criteria_sql, criteria_visit_dt.format(v_alias, v_alias, hbv, v_alias, hav) )
    #   if criteria.get('company_id') is not None :  # criteria_company  = "({}1.company_id = '{}' and {}2.company_id = '{}')"
    #     criteria_sql = '{} and {}'.format(criteria_company.format(v_alias, v_alias, criteria.get('company_id')), criteria_sql)
    #   return criteria_sql
    #
    # qry_from = main_qry.format(criteria_sql)  # main_qry -> "FROM visit as v where v.id in (select v2.id FROM visit as v1 inner join visit as v2 on v1.zone_id = v2.zone_id where {})"
    qry_from = cls._compose_criteria_sql(criteria=criteria, v_alias='v')   # main_qry -> "FROM visit as v where v.id in (select v2.id FROM visit as v1 inner join visit as v2 on v1.zone_id = v2.zone_id where {})"
    inner_qry_from = cls._compose_criteria_sql(criteria=criteria, v_alias='vv')   # main_qry -> "FROM visit as v where v.id in (select v2.id FROM visit as v1 inner join visit as v2 on v1.zone_id = v2.zone_id where {})"
    #
    # GARDER
    # return raw_select.format(qry_from)
    # return summary_select.format(qry_from)
    return contact_select.format(inner_qry_from, qry_from) + group_by
# contact_select = "SELECT v2.fname, v2.lname, v2.phone_number, v2.visitor_id, count(distinct(v2.zone_id)) as nb_zones, " \
#                  "(SELECT count(1) {} and vv2.zone_id = vv1.zone_id and vv2.phone_number = v2.phone_number ) as nb_contacts, " \
#                  "min(v2.visit_datetime) as min_date, max(v2.visit_datetime) as max_date {}"

  def _compose_criteria_sql(criteria:dict, v_alias:str) -> str :
    phone = criteria.get('phone_number')
    vid =  criteria.get('visitor_id')
    hbv = 1 if criteria.get('h_before_visit') is None else criteria.get('h_before_visit')
    hav = 1 if criteria.get('h_after_visit') is None else criteria.get('h_after_visit')
    #
    criteria_sql = criteria_visitor.format(v_alias, vid, v_alias, vid)   \
                   if phone == None else criteria_phone.format(v_alias, phone, v_alias, phone) \
                   if vid   == None else '{} or {}'.format(criteria_visitor.format(v_alias, vid, v_alias, vid)  , criteria_phone.format(v_alias, phone, v_alias, phone))
    criteria_sql = '{} and {}'.format(criteria_sql, criteria_visit_dt.format(v_alias, v_alias, hbv, v_alias, hav) )
    if criteria.get('company_id') is not None :  # criteria_company  = "({}1.company_id = '{}' and {}2.company_id = '{}')"
      criteria_sql = '{} and {}'.format( criteria_company.format(v_alias, criteria.get('company_id'), v_alias, criteria.get('company_id')), criteria_sql)
    return main_qry.format(v_alias, v_alias, v_alias, v_alias, criteria_sql)


  @classmethod
  def check_business_rules_for_upsert(cls, attr:dict):
    if (attr.get('company_id') is None) or (attr.get('room_id') is None) or (attr.get('zone_id') is None)  :
      raise ValueError(f"'Visit' entity instance should reference a well identified location => Indicate 'company_id, room_id and zone_id' ")
    #
    if ( (attr.get('visitor_phone_number') is None)  and (attr.get('visitor_id') is None)  ):
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

# room_0.1
# room_0.2
# room_0.3
#
# room_2.1
# room_2.2
#
# z_0.1.1
# z_0.1.2
# z_0.1.3
# z_0.2.1
# z_0.2.2
# z_0.3.1
# z_2.1.1
# "company sub": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e" | "...f" | "...g"
if __name__ == '__main__':
  pass
  # from covcov.infrastructure.db.database import Database
  # db = Database("database")
  # db.insert_value(['{"id":"visit_1", "company_id": "comp_100", "room_id": "room_100.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De La Fontaine", "visitor_phone_number": "0661794641" }'], [Visit])

  # # Visit on ROOM_1 / z_0.1.1
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.1", "zone_id": "z_0.1.1", "phone_number": "3262_" }'], [Visit])
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.1", "zone_id": "z_0.1.1", "phone_number": "3263" }'], [Visit])
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.1", "zone_id": "z_0.1.1", "phone_number": "3264" }'], [Visit])

  # # Visit on ROOM_1 / z_0.1.3
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.1", "zone_id": "z_0.1.3", "phone_number": "3262_" }'], [Visit])
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.1", "zone_id": "z_0.1.3", "phone_number": "3271" }'], [Visit])
  #
  # # Visit on ROOM_2 / z_0.2.1
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.2", "zone_id": "z_0.2.1", "phone_number": "3262_" }'], [Visit])
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.2", "zone_id": "z_0.2.1", "phone_number": "3281" }'], [Visit])
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.2", "zone_id": "z_0.2.1", "phone_number": "3264" }'], [Visit])
  #
  # # Visit on ROOM_2 / z_0.2.2
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.2", "zone_id": "z_0.2.2", "phone_number": "3291" }'], [Visit])
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.2", "zone_id": "z_0.2.2", "phone_number": "3292" }'], [Visit])
  # db.insert_value(['{"company_id": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "room_id": "room_0.2", "zone_id": "z_0.2.2", "phone_number": "3263" }'], [Visit])

  #
  # sess = db.session()
  # sess.add(Visit({"id":"visit_3", "company_id": "comp_1", "room_id": "room_1.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De Lafontaine" }))
