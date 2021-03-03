import logging
from covcov.infrastructure.db.database import Database
from covcov.infrastructure.db.schema import stat_domain

logger = logging.getLogger(__name__)
db = Database("database")

def handle(event, context):
  stat_domain.CompanyVisit.update_visisit_stat(db)
  return event