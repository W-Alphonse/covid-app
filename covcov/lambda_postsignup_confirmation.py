from covcov.infrastructure.db.database import Database
from covcov.application import misc_utils as create_user

db = Database("database")

def handle(event, context):
  create_user(event, db)
  return event
