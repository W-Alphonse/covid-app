"""
Upsert gist
Requires at least postgres 9.5 and sqlalchemy 1.1
Initial state:
[]
Initial upsert:
[['2016-08-02', '2016-08-01', 1000, 10], ['2016-08-02', '2016-08-02', 2000, 20]]
INSERT INTO digital_spend (report_date, day, impressions, conversions) VALUES (%(report_date_0)s, %(day_0)s, %(impressions_0)s, %(conversions_0)s), (%(report_date_1)s, %(day_1)s, %(impressions_1)s, %(conversions_1)s) ON CONFLICT (day) WHERE report_date < report_date DO UPDATE SET report_date = excluded.report_date, impressions = excluded.impressions
State after upsert:
[[datetime.date(2016, 8, 2), datetime.date(2016, 8, 1), 1000, 10], [datetime.date(2016, 8, 2), datetime.date(2016, 8, 2), 2000, 20]]
First real upsert:
[['2016-08-03', '2016-08-02', 2050, 100], ['2016-08-03', '2016-08-03', 3000, 30]]
INSERT INTO digital_spend (report_date, day, impressions, conversions) VALUES (%(report_date_0)s, %(day_0)s, %(impressions_0)s, %(conversions_0)s), (%(report_date_1)s, %(day_1)s, %(impressions_1)s, %(conversions_1)s) ON CONFLICT (day) WHERE report_date < report_date DO UPDATE SET report_date = excluded.report_date, impressions = excluded.impressions
Note that 8/2 impressions change and conversions do not:
[[datetime.date(2016, 8, 2), datetime.date(2016, 8, 1), 1000, 10], [datetime.date(2016, 8, 3), datetime.date(2016, 8, 2), 2050, 20], [datetime.date(2016, 8, 3), datetime.date(2016, 8, 3), 3000, 30]]
"""

import os

from sqlalchemy import Column, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql

Base = declarative_base()

def start_session():
  engine = create_engine('postgresql+psycopg2://haa:haa@127.0.0.1:5432/postgres?client_encoding=utf8', echo=True)
  session = sessionmaker()
  session.configure(bind=engine)
  Base.metadata.create_all(engine)
  return session()

class DigitalSpend(Base):
  __tablename__ = 'digital_spend'
  report_date = Column(Date, nullable=False)
  day = Column(Date, nullable=False, primary_key=True)
  impressions = Column(Integer)
  conversions = Column(Integer)

  def __repr__(self):
    return str([getattr(self, c.name, None) for c in self.__table__.c])


def compile_query(query):
  """Via http://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries"""
  compiler = query.compile if not hasattr(query, 'statement') else query.statement.compile
  return compiler(dialect=postgresql.dialect())


def upsert(session, model, rows, as_of_date_col='report_date', no_update_cols=[]):
  table = model.__table__

  stmt = insert(table).values(rows)

  update_cols = [c.name for c in table.c
                 if c not in list(table.primary_key.columns)
                 and c.name not in no_update_cols]

  on_conflict_stmt = stmt.on_conflict_do_update(
    index_elements=table.primary_key.columns,
    set_={k: getattr(stmt.excluded, k) for k in update_cols},
    index_where=(getattr(model, as_of_date_col) < getattr(stmt.excluded, as_of_date_col))
  )

  print(compile_query(on_conflict_stmt))
  session.execute(on_conflict_stmt)
  session.commit()


if __name__ == '__main__':
  session = start_session()

  headers = ['report_date', 'impressions', 'conversions']

  initial_rows = [
    ['2016-08-02', '2016-08-01', 1000, 10],
    ['2016-08-02', '2016-08-02', 2000, 20]
  ]

  next_rows = [
    ['2016-08-03', '2016-08-02', 2050, 100],
    ['2016-08-03', '2016-08-03', 3000, 30]
  ]

  print('Initial state:\n')
  print(session.query(DigitalSpend).all())

  print('Initial upsert:\n')
  print(initial_rows)
  upsert(session, DigitalSpend, initial_rows, no_update_cols=['conversions'])
  print('State after upsert:\n')
  print(session.query(DigitalSpend).all())

  print('First real upsert:\n')
  print(next_rows)
  upsert(session, DigitalSpend, next_rows, no_update_cols=['conversions'])
  print('Note that 8/2 impressions change and conversions do not:\n')
  print(session.query(DigitalSpend).all())