from sqlalchemy import Column, Integer, Sequence, Unicode, String, ForeignKey, event
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy_utils import EmailType, PhoneNumber, CountryType

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema.base_domain import BaseTable


# ========
# Company
# ========

class Company(Base, BaseTable, SerializerMixin):
  __tablename__ = 'company'
  id = Column(Unicode(BaseTable.SUB_SIZE), primary_key=True)
  # password = Column(Unicode(128), nullable=False)
  siret    = Column(Unicode(14))
  address  = Column(Unicode(300), nullable=False)
  zip_code = Column(Unicode(10), nullable=False)
  country_code = Column(Unicode(2), default='FR', nullable=False)
  phone_number = Column(Unicode(20))
  email = Column(EmailType(length=64), unique=True)
  contact_fname = Column(Unicode(20))
  contact_lname = Column(Unicode(20))
  url = Column(Unicode(128))
  #
  rooms = relationship("Room", cascade="all,delete-orphan", backref="company")  #  https://gist.github.com/davewsmith/ab41cc4c2a189ecd4677c624ee594db3

  @classmethod
  def enhance_payload_with_auth_token(cls, payload_attr:dict, auth_claims:dict):
    # payload_attr.update({'id': auth_claims['sub']})
    payload_attr.update({'email': auth_claims['email']})


  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.address}, {self.zip_code}, {self.country_code})"

#======
# ROOM
#======
class Room(Base, BaseTable, SerializerMixin):
  __tablename__ = 'room'
  id = Column(String(10), primary_key=True)
  description = Column(String(30))
  company_id  = Column(Unicode(BaseTable.SUB_SIZE), ForeignKey("company.id", ondelete='CASCADE'), nullable=False)
  #
  zones   = relationship("Zone", cascade="all, delete-orphan", backref="room")
  # company = relationship("Company", backref=backref("rooms", cascade="all, delete-orphan"))
  serialize_rules = ('-company',)

  # def __init__(self, row:dict):
  #   self.__dict__ = row

  @classmethod
  def enhance_payload_with_auth_token(cls, payload_attr:dict, auth_claims:dict):
    payload_attr.update({'company_id': auth_claims['sub']})


  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.description}, FK.company_id={self.company_id})"

#======
# ZONE
#======
class Zone(Base, BaseTable, SerializerMixin):
  __tablename__ = 'zone'
  id = Column(String(10), primary_key=True)
  description = Column(String(30))
  room_id = Column(Unicode(10), ForeignKey("room.id", ondelete='CASCADE'), nullable=False)
  serialize_rules = ('-room',)

  # def __init__(self, row:dict):
  #   self.__dict__ = row

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.description}, FK.room_id={self.room_id})"

if __name__ == '__main__':
  pass
  # Populate a few tables
  # db.insert_value(['{"id":"comp_2", "address": "24 Avenue Frayce", "zip_code":"93400"}'], [Company])
  # session = sessionmaker(bind=engine)
  # session = Session(engine)
  # session.add(Company('{"id":"comp_1", "address": "24 Avenue Frayce", "zip_code":"93400"}'))
  # session.add(Room("room_1.1", "ROOM_1.1", "comp_1"))
  # session.add(Room("zone_1.1.1", "ZONE_1.1.1", "room_1.1"))
  # session.add(Room("zone_1.1.2", "ZONE_1.1.2", "room_1.1"))
  # --
  # session.add(Room("room_1.2", "ROOM_1.2", "comp_1"))
  # session.add(Room("zone_1.2.1", "ZONE_1.2.1", "room_1.2"))
  #--
  # session.add(Company("Id_2", "34 Avenue Frayce", "93400"))
  #--
  # session.commit()