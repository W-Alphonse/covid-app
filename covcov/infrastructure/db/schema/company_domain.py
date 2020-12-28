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
  # __table_args__ = {'extend_existing': True}

  id = Column(Unicode(BaseTable.SUB_SIZE), primary_key=True)
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
  # __table_args__ = {'extend_existing': True}

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
  # __table_args__ = {'extend_existing': True}

  id = Column(String(10), primary_key=True)
  description = Column(String(30))
  room_id = Column(Unicode(10), ForeignKey("room.id", ondelete='CASCADE'), nullable=False)
  serialize_rules = ('-room',)

  # def __init__(self, row:dict):
  #   self.__dict__ = row

  def __repr__(self):
    return f"{self.__tablename__}({self.id}, {self.description}, FK.room_id={self.room_id})"

# "company sub": "caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e" | "...f" | "...g"
if __name__ == '__main__':
  pass

  # from covcov.infrastructure.db.database import Database
  # db = Database("database")
  # # Creation Company_1
  # db.insert_value(['{"id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e", "address": "0 - 24 Avenue Frayce", "zip_code":"93401", "phone_number":"0661794641"}'], [Company])
  # db.insert_value(['{"id":"room_0.1", "description":"ROOM_0.1_", "company_id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e"}'], [Room])
  # db.insert_value(['{"id":"z_0.1.1", "description":"Z_0.1.1", "room_id":"room_0.1"}'], [Zone])
  # db.insert_value(['{"id":"z_0.1.2", "description":"Z_0.1.2", "room_id":"room_0.1"}'], [Zone])
  # db.insert_value(['{"id":"z_0.1.3", "description":"Z_0.1.3", "room_id":"room_0.1"}'], [Zone])
  # #
  # db.insert_value(['{"id":"room_0.2", "description":"ROOM_0.2_", "company_id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e"}'], [Room])
  # db.insert_value(['{"id":"z_0.2.1", "description":"Z_0.2.1", "room_id":"room_0.2"}'], [Zone])
  # db.insert_value(['{"id":"z_0.2.2", "description":"Z_0.2.2", "room_id":"room_0.2"}'], [Zone])
  # #
  # db.insert_value(['{"id":"room_0.3", "description":"ROOM_0.3_", "company_id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1e"}'], [Room])
  # db.insert_value(['{"id":"z_0.3.1", "description":"Z_0.3.1", "room_id":"room_0.3"}'], [Zone])
  #
  # # Creation Company_2
  # db.insert_value(['{"id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1f", "address": "2 - 24 Avenue Frayce", "zip_code":"93402", "phone_number":"0661794641-2"}'], [Company])
  # db.insert_value(['{"id":"room_2.1", "description":"ROOM_2.1_", "company_id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1f"}'], [Room])
  # db.insert_value(['{"id":"z_2.1.1", "description":"Z_2.1.1", "room_id":"room_2.1"}'], [Zone])
  # db.insert_value(['{"id":"z_2.1.2", "description":"Z_2.1.2", "room_id":"room_2.1"}'], [Zone])
  # db.insert_value(['{"id":"z_2.1.3", "description":"Z_2.1.3", "room_id":"room_2.1"}'], [Zone])
  # #
  # db.insert_value(['{"id":"room_2.2", "description":"ROOM_2.2_", "company_id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1f"}'], [Room])
  # db.insert_value(['{"id":"z_2.2.1", "description":"Z_2.2.1", "room_id":"room_2.2"}'], [Zone])
  # db.insert_value(['{"id":"z_2.2.2", "description":"Z_2.2.2", "room_id":"room_2.2"}'], [Zone])
  #
  # # Creation Company_3
  # db.insert_value(['{"id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1g", "address": "3 - 24 Avenue Frayce", "zip_code":"93403", "phone_number":"0661794641-3"}'], [Company])
  # db.insert_value(['{"id":"room_3.1", "description":"ROOM_3.1_", "company_id":"caf13bd0-6a7d-4c7b-aa87-6b6f3833fe1g"}'], [Room])
  # db.insert_value(['{"id":"z_3.1.1", "description":"Z_3.1.1", "room_id":"room_3.1"}'], [Zone])
  # db.insert_value(['{"id":"z_3.1.2", "description":"Z_3.1.2", "room_id":"room_3.1"}'], [Zone])



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