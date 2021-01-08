from covcov.infrastructure.db.database import Database
from covcov.application import misc_utils as util

db = Database("database")

def handle(event, context):
  util.create_user(event, db)
  return event
