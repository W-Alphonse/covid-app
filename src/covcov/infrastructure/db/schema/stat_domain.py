import datetime

from sqlalchemy import Column, Integer, Unicode, DateTime
from sqlalchemy_serializer import SerializerMixin

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema.base_domain import BaseTable

sql_drop_tmp_tbl = "drop table if exists tmp_tbl"
#
sql1_compute_stat =  "CREATE TEMP TABLE tmp_tbl AS " \
                     "select vh.company_id, DATE_TRUNC('month',vh.visit_datetime) as start_period_dt, 'M' as period_type, "\
                     "count(*) FILTER (where 1=1) as visit_count, " \
                     "count(distinct vh.phone_number) FILTER (where 1=1) + " \
                     "count(distinct vh.visitor_id) FILTER (where vh.phone_number is null ) as visitor_count " \
                     "from visit_histo vh inner join company c on vh.company_id = c.id {}" \
                     "group by vh.company_id, start_period_dt"
sql1_compute_stat_bom = "where vh.visit_datetime >= DATE_TRUNC('month',c.last_count_dt) and vh.visit_datetime <  DATE_TRUNC('day',now() {}) "
sql1_compute_stat_bod = "where vh.visit_datetime >= DATE_TRUNC('day',c.last_count_dt) and vh.visit_datetime <  DATE_TRUNC('day',now() {}) "
#
sql2_create_stat_entry   = "insert into company_visit(company_id, start_period_dt, period_type, visit_count, visitor_count, last_count_dt, creation_dt ) " \
                           "select t.company_id, t.start_period_dt, t.period_type, 0, 0, now(), now() from tmp_tbl t " \
                           "where not exists (select 1 from company_visit c where c.company_id = t.company_id and c.start_period_dt = t.start_period_dt and c.period_type = t.period_type)"
#
sql3_update_stat = "update company_visit SET company_id = qry.company_id, start_period_dt =qry.start_period_dt, " \
                   "period_type = qry.period_type, last_count_dt = now(), {} " \
                   "FROM ( select company_id, start_period_dt, period_type, visit_count, visitor_count from tmp_tbl ) AS qry " \
                   "WHERE company_visit.company_id = qry.company_id and company_visit.start_period_dt = qry.start_period_dt and company_visit.period_type = 'M'"
sql3_update_stat_bom = "visit_count = qry.visit_count, visitor_count = qry.visitor_count"
sql3_update_stat_bod = "visit_count = company_visit.visit_count + qry.visit_count, visitor_count = company_visit.visitor_count + qry.visitor_count"
#
sql4_update_company_stat = "update company c set last_count_dt = DATE_TRUNC('day',now() {}), visitor_on_last_count = cv.visitor_count, " \
                           "visit_on_last_count = cv.visit_count from company_visit cv " \
                           "where c.id = cv.company_id and cv.start_period_dt = DATE_TRUNC('month',now())"

# ===============
# Company Visit
# ===============
class CompanyVisit(Base, BaseTable, SerializerMixin):
  __tablename__ = 'company_visit'
  __table_args__ = {'extend_existing': True}
  #
  company_id = Column(Unicode(BaseTable.SUB_SIZE), primary_key=True)   # pk1
  start_period_dt = Column(DateTime, nullable=False, primary_key=True) # pk2
  period_type = Column(Unicode(3), nullable=False, primary_key=True)   # pk3 - [Y, M, W, 2W, ...]
  #
  visitor_count   = Column(Integer, default=0, nullable=False)
  visit_count     = Column(Integer, default=0, nullable=False)
  last_count_dt = Column(DateTime, default=datetime.datetime.now, nullable=False)
  creation_dt    = Column(DateTime, default=datetime.datetime.now, nullable=False)

  @classmethod
  def update_visisit_stat(cls, db) -> [{}] :
    bom = True    # Should be True
    noint = True  # Should be True
    #
    noffset =  "" if noint else "+ INTERVAL '1 day'"
    _sql1_compute_stat = sql1_compute_stat.format( sql1_compute_stat_bom.format(noffset)  if bom else sql1_compute_stat_bod.format(noffset) )
    _sql3_update_stat  = sql3_update_stat.format( sql3_update_stat_bom.format(noffset) if bom else sql3_update_stat_bod.format(noffset) )
    _sql4_update_company_stat = sql4_update_company_stat.format(noffset)
    #
    return db.native_execute_sqls([sql_drop_tmp_tbl, _sql1_compute_stat, sql2_create_stat_entry, _sql3_update_stat, _sql4_update_company_stat])

if __name__ == '__main__' :
  pass
  # from covcov.infrastructure.db.database import Database
  # db = Database("database")
  # db.create_missing_tables()