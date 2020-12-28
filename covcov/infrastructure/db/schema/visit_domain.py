import datetime
from sqlalchemy import Column, Unicode, ForeignKey, DateTime, Integer, Sequence, BigInteger
from sqlalchemy_serializer import SerializerMixin

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema.base_domain import BaseTable


raw_select = "SELECT v.company_id, v.room_id, v.zone_id, v.phone_number, v.visit_datetime, v.visitor_id, v.fname, v.lname {}"
summary_select = "SELECT count(distinct(v.phone_number)) as nb_cases, count(distinct(v.zone_id)) as nb_zones, max(v.visit_datetime) - min(v.visit_datetime) nb_days {}"
contact_select = "SELECT v.fname, v.lname, v.phone_number, v.visitor_id, count(distinct(v.zone_id)) as nb_zones, min(v.visit_datetime) as min_date, max(v.visit_datetime) as max_date {}"
#
sub_qry = "FROM visit as v where v.id in (select v2.id FROM visit as v1 inner join visit as v2 on v1.zone_id = v2.zone_id where {})"
group_by = " GROUP BY v.phone_number, v.visitor_id, v.fname, v.lname"
#
criteria_phone   = "(v1.phone_number = '{}' and v2.phone_number <> '{}')"
criteria_visitor = "(v1.visitor_id = '{}' and v2.visitor_id <> '{}') "
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
    phone = criteria.phone_number
    vid =  criteria.visitor_id
    criteria_sql = criteria_visitor.format(vid, vid)   if phone == None else \
                   criteria_phone.format(phone, phone) if vid == None else \
                   '{} or {}'.format(criteria_visitor.format(vid, vid)  , criteria_phone.format(phone, phone))
    if criteria.company_id is not None :
      criteria_sql = '{} and {}'.format(criteria.company_id, criteria_sql)
    sub_select = sub_qry.format(criteria_sql)
    #
    # raw_select = "SELECT v.company_id, v.room_id, v.zone_id, v.phone_number, v.visit_datetime, v.visitor_id, v.fname, v.lname {}"
    # sub_select = " FROM visit as v where v.id in (select v2.id FROM visit as v1 inner join visit as v2 on v1.zone_id = v2.zone_id where {})"

    # return raw_select.format(sub_select)
    # return summary_select.format(sub_select)
    return contact_select.format(sub_select) + group_by

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
