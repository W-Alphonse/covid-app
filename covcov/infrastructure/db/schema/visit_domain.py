import datetime
from sqlalchemy import Column, Unicode, ForeignKey, DateTime
from sqlalchemy_serializer import SerializerMixin

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema import BaseTable


# ========
#  Visit
# ========

class Visit(Base, BaseTable, SerializerMixin):
  __tablename__ = 'visit'
  #
  id = Column(Unicode(10), primary_key=True)
  company_id  = Column(Unicode(10), ForeignKey("company.id"), nullable=False)
  room_id     = Column(Unicode(10), ForeignKey("room.id"), nullable=False)
  zone_id     = Column(Unicode(10), ForeignKey("zone.id"), nullable=False)
  #
  visitor_id  = Column(Unicode(15))
  visitor_phone_number = Column(Unicode(20), nullable=False)
  visitor_fname = Column(Unicode(20))
  visitor_lname = Column(Unicode(20))
  visit_datetime = Column(DateTime, default=datetime.datetime.now(), nullable=False)

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.company.description}, {self.room.description}, {self.zone.description}, {self.visit_datetime})"

  @classmethod
  def check_business_rules_for_upsert(cls, attr:dict):
    if (attr.get('company_id') is None) or (attr.get('room_id') is None) or (attr.get('zone_id') is None)  :
      raise ValueError(f"'Visit' entity instance should reference a well identified location => Indicate 'company_id, room_id and zone_id' ")
    #
    if attr.get('visitor_phone_number') is None or  \
       (    (attr.get('visitor_fname') is None or attr.get('visitor_lname') is None) \
         and (attr.get('visitor_id') is None)  ):
      raise ValueError(f"'Visit' entity instance should reference a well identified client => Either indicate ('first name, last name, phone_number') or ('visitor_id, phone_number') ")


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


if __name__ == '__main__':
  pass
  # from covcov.infrastructure.db.database import Database
  # db = Database("database")
  # Base.metadata.create_all(db.engine)
  # db.insert_value(['{"id":"visit_1", "company_id": "comp_100", "room_id": "room_100.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De La Fontaine", "visitor_phone_number": "0661794641" }'], [Visit])
  #
  # sess = db.session()
  # sess.add(Visit({"id":"visit_3", "company_id": "comp_1", "room_id": "room_1.1", "zone_id": "z_100.1.1", "visitor_fname":"Jean", "visitor_lname": "De Lafontaine" }))
