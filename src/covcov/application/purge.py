import logging
import datetime

import covcov.infrastructure.db.schema.visit_domain as vd
from covcov.infrastructure.db.database import Database

logger = logging.getLogger(__name__)

SUCCES_CODE = 0
ERROR_CODE  = 1
def archive_visit(db:Database, days_count=15, chunk_size=300) -> int:
  t1 = datetime.datetime.now()
  counts = [chunk_size]
  cumul = 0
  try :
    while counts[0] == chunk_size :
      counts = db.native_execute_sqls( vd.Visit.compose_purge_sqls(days_count, chunk_size) )
      cumul += counts[0]
    return SUCCES_CODE
  except Exception as ex:
    logger.exception("Exception in batch 'archive_visit(days_count=%s,chunk_size=%s)':\n", days_count, chunk_size, exc_info=1)
    return ERROR_CODE
  finally :
    logger.info(f"Batch 'archive_visit(days_count={days_count},chunk_size={chunk_size})' finished after {(datetime.datetime.now() -t1).seconds} seconds.\nIt archived {cumul} Visit(s)" )


# if __name__ == '__main__':
#   from covcov.infrastructure.db.database import Database
#   db = Database("database")
#   archive_visit(db)
#
#   db.create_missing_tables()
#   archive_visit(db, 0.2, 10)