import datetime

from sqlalchemy import Column, Integer, Unicode, BigInteger, String, ForeignKey, Boolean, DateTime, update, Date
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship, Session
from sqlalchemy_serializer import SerializerMixin

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.schema.base_domain import BaseTable

sql_drop_tmp_tbl = "drop table if exists tmp_tbl"
sql1_compute_stat =  "CREATE TEMP TABLE tmp_tbl AS " \
                     "select vh.company_id, DATE_TRUNC('month',vh.visit_datetime) as start_period_dt, 'M' as period_type, "\
                     "count(*) FILTER (where 1=1) as visit_count, " \
                     "count(distinct vh.phone_number) FILTER (where 1=1) + " \
                     "count(distinct vh.visitor_id) FILTER (where vh.phone_number is null ) as visitor_count " \
                     "from visit_histo vh inner join company c on vh.company_id = c.id " \
                     "where vh.visit_datetime >= DATE_TRUNC('month',c.last_count_dt) and vh.visit_datetime <  DATE_TRUNC('day',now()) " \
                     "group by vh.company_id, start_period_dt"
sql2_create_stat_entry   = "insert into company_visit(company_id, start_period_dt, period_type, visit_count, visitor_count, last_count_dt, creation_dt ) " \
                           "select t.company_id, t.start_period_dt, t.period_type, t.visit_count, t.visitor_count, now(), now() from tmp_tbl t " \
                           "where not exists (select 1 from company_visit c where c.company_id = t.company_id and c.start_period_dt = t.start_period_dt and c.period_type = t.period_type)"
sql3_update_stat = "update company_visit SET company_id = qry.company_id, start_period_dt =qry.start_period_dt, " \
                   "period_type = qry.period_type, visit_count = qry.visit_count, visitor_count = qry.visitor_count, last_count_dt = now() " \
                   "FROM ( select company_id, start_period_dt, period_type, visit_count, visitor_count from tmp_tbl ) AS qry " \
                   "WHERE company_visit.company_id = qry.company_id and company_visit.start_period_dt = qry.start_period_dt and company_visit.period_type = 'M'"
sql4_update_company_stat = "update company c set last_count_dt = DATE_TRUNC('day',now()), visitor_on_last_count = cv.visitor_count, " \
                           "visit_on_last_count = cv.visit_count from company_visit cv " \
                           "where c.id = cv.company_id and cv.start_period_dt = DATE_TRUNC('month',now())"

# ===============
# Company Visit
# ===============
class CompanyVisit(Base, BaseTable, SerializerMixin):
  __tablename__ = 'company_visit'
  __table_args__ = {'extend_existing': True}

  # id = Column(BigInteger, primary_key=True)
  # company_id  = Column(Unicode(BaseTable.SUB_SIZE), ForeignKey("company.id"), nullable=False)
  company_id = Column(Unicode(BaseTable.SUB_SIZE), primary_key=True)   # pk1
  start_period_dt = Column(DateTime, nullable=False, primary_key=True) # pk2
  period_type = Column(Unicode(3), nullable=False, primary_key=True)   # pk3 - [Y, M, W, 2W, ...]
  # end_period_dt = Column(DateTime, nullable=False)
  #
  visitor_count   = Column(Integer, default=0, nullable=False)
  visit_count     = Column(Integer, default=0, nullable=False)
  last_count_dt = Column(DateTime, default=datetime.datetime.now, nullable=False)
  creation_dt    = Column(DateTime, default=datetime.datetime.now, nullable=False)

  #
  # rooms = relationship("Room", cascade="all,delete-orphan", backref="company", primaryjoin="and_(Room.company_id==Company.id, Room.deleted==False)", lazy="select" ) #  https://gist.github.com/davewsmith/ab41cc4c2a189ecd4677c624ee594db3

  @classmethod
  def update_visisit_stat(cls, db) -> [{}] :
    # db.native_select_rows
    return db.native_execute_sqls([sql_drop_tmp_tbl, sql1_compute_stat, sql2_create_stat_entry, sql3_update_stat, sql4_update_company_stat])

if __name__ == '__main__' :
  pass
  # from covcov.infrastructure.db.database import Database
  # db = Database("database")
  # db.create_missing_tables()