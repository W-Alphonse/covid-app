import crypt
import json
import logging
import typing
from collections import defaultdict
from contextlib import contextmanager

from sqlalchemy import literal, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker, ColumnProperty, Query

from covcov.infrastructure.db import Base
from covcov.infrastructure.db.connexion import Connexion
import covcov.infrastructure.db.schema.company_domain
import covcov.infrastructure.db.schema.visit_domain

logger = logging.getLogger(__name__)

class Database :

  def __init__(self, database_key:str):
    self.engine = Connexion(database_key).connect()
    self.session = sessionmaker(bind=self.engine)

  def create_missing_tables(self):
    Base.metadata.create_all(self.engine)

  def reset_tables(self):
    logger.info(f'Reset the database.')
    Base.metadata.drop_all(self.engine)
    Base.metadata.create_all(self.engine)

  def insert_value(self, payloads:[typing.Union[dict, str]], tables:[DeclarativeMeta], additionnal_ctx=None):
    with self.session_scope() as session:
      for i, payload in enumerate(payloads) :
        tables[i].execute_before_insert(payload, additionnal_ctx)
        if not isinstance(payload,dict) :
          payload = json.loads(payload)
        insert_stmt = insert(tables[i]).values(payload)
        # logger.info(str(insert_stmt))
        session.execute(insert_stmt)
        #
        cloned_payload= payloads[i].copy()
        tables[i].execute_on_insert(session, id, cloned_payload)


  def upsert_value_with_overwrite(self, datas:[typing.Union[dict, str]], tables:[DeclarativeMeta]):
    with self.session_scope() as session:
      for i, data in enumerate(datas) :
        insert_stmt = insert(tables[i]).values(data if isinstance(data,dict) else json.loads(data) )
        columns_to_exlcude_from_update = [col.name for col in tables[i].__table__.c
                                          if col not in list(tables[i].__table__.primary_key.columns) and col.name not in data.keys()]
        do_upsert_stmt = insert_stmt.on_conflict_do_update(# constraint='pk_my_table'''
                          index_elements=tables[i].__table__.primary_key.columns,
                          set_={k: getattr(insert_stmt.excluded, k) for k in columns_to_exlcude_from_update})
        # logger.info(_compile_query(do_upsert_stmt))
        session.execute(do_upsert_stmt)


  def upsert_value(self, payloads:[typing.Union[dict, str]], tables:[DeclarativeMeta], company_id:str, additionnal_ctx=None):
    with self.session_scope() as session:
      for i, payload in enumerate(payloads) :
        # already_exist = session.query(literal(True)).filter(session.query(tables[i]).filter(tables[i].id == payload['id']).exists()).scalar()
        row_exists, tentative_exceeding_max_zone, current_zone_count = tables[i].check_exists(self, payload, company_id, tables[i])
        if row_exists:
          cloned_payload= payloads[i].copy()
          id = cloned_payload.pop('id')
          session.execute( update(tables[i]).where(tables[i].id == id).values(cloned_payload) )
          tables[i].execute_on_update(session, id, cloned_payload)
        else :
            self.insert_value(payloads, tables, additionnal_ctx)
    # TODO - Use a more generic attribute instead of using : payloads[0].get('company_id'),
    if row_exists :
      ret_as_dict = tables[i].execute_after_update(self, payloads[0].get('company_id'), cloned_payload)
      if (ret_as_dict is not None) and isinstance(ret_as_dict, dict) :
        current_zone_count = ret_as_dict.get("current_zone_count")
    #
    return  {"row_exists": row_exists} if current_zone_count is None \
      else  {"row_exists": row_exists, "tentative_exceeding_max_zone":tentative_exceeding_max_zone, "current_zone_count": current_zone_count }


  def delete_rows(self, payloads:[dict], tables:[DeclarativeMeta]):
    with self.session_scope() as session:
      for i, payload in enumerate(payloads) :
        # delete_stmt = delete(tables[i]).where(id = data.row['id'])
        session.query(tables[i]).filter(tables[i].id == payload['id']).delete()


  def select_rows(self, datas:[Base], tables:[DeclarativeMeta], columns_to_filter:[str]=None) -> [dict] :
    rows = []
    with self.session_scope() as session:
      for i, data in enumerate(datas) :
        for row in session.query(tables[i]).filter(tables[i].id == data.id).all() :
          rows.append( self._remove_dict_keys( self._remove_dict_values(row.to_dict(rules= data.get_serialize_rules()), [None]) , columns_to_filter) )
    return rows

  def native_execute_sqls(self, sql_queries:[str]) -> [int] :
    counts = []
    with self.session_scope() as session:
      for i, sql_query in enumerate(sql_queries) :
        counts.append( self.engine.execute(sql_query).rowcount) # <-- self.engine.execute(sql_query) is of type ResultProxy
    return counts

  """
    sql_queries:[str]  - Array of SQL queries to be executed unconditionally, exception made to the last query in the array.
    master_qry_ndx:int - If equal to -1, Then the last query will be executed unconditionally;
                         Otherwise, the last query will be executed if the related 'master query' result was empty
  """
  def native_select_rows(self, sql_queries:[str], master_qry_ndx=-1, lqry_default_result={"exists":True}) -> [{}] :
    result = []
    master_qry_has_result = False
    for i, sql_query in enumerate(sql_queries) :
      # 1 - Check whether we should execute the last query
      if (sql_query == sql_queries[-1]) and (master_qry_ndx != -1) and master_qry_has_result:
        result.append(lqry_default_result)
        continue
      # 2 - Execute the query ...
      resultProxy = self.engine.execute(sql_query)  # <-- ResultProxy object is made up of RowProxy objects
      # rows = resultProxy.fetchall()
      # 3 - Store the result in dictionnary
      if resultProxy.rowcount != 0 :
        master_qry_has_result = master_qry_has_result or (i == master_qry_ndx)
        dd = defaultdict(list)
        cols_list = resultProxy.keys()
        rows = resultProxy.fetchall() if len(cols_list) != 0 else []
        for row in rows :                      # <-- type(row) == tuple
          for i in range(0, len(cols_list)) :  # <-- extract one row and add it to defaultdict
            dd[cols_list[i]].append(row[i] if row[i] is not None else '')
        result.append(dict(dd))
      else :
        result.append(dict.fromkeys(resultProxy.keys() , {}))
      #
      # list_of_dicts = [{key: value for (key, value) in row.items()} for row in rows]
      # row_as_dict = [dict(row) for row in resultProxy]
    return result


  # def authenticate(self, user_data:dict, user_table:Base):
  #   with self.session_scope() as session:
  #     return  session.query(literal(True)).filter(session.query(user_table).filter(user_table.email == user_data['email'],
  #                                                 user_table.password == self._encrypt(user_data['password'])).exists()).scalar() == True

  def _remove_dict_values(self, dict_to_clean:{}, values_to_remove:[]) -> dict:
    cleaned_dict = {}
    for k, v in dict_to_clean.items():
      if isinstance(v, dict):
        nested = self._remove_dict_values(v, values_to_remove)
        if len(nested.keys()) > 0:
          cleaned_dict[k] = nested
      elif v not in values_to_remove:
        cleaned_dict[k] = v
    return cleaned_dict

  def _remove_dict_keys(self, dict_to_clean:{}, columns_to_filter:[str]) -> dict:
    if columns_to_filter is None or len(columns_to_filter) == 0 :
      return dict_to_clean;
    cleaned_dict = {}
    for k, v in dict_to_clean.items():
      if isinstance(v, dict):
        nested = self._remove_dict_keys(v, columns_to_filter)
        if len(nested.keys()) > 0:
          cleaned_dict[k] = nested
      elif k not in columns_to_filter:
        cleaned_dict[k] = v
    return cleaned_dict

  def _encrypt(self, word: str) -> str :
    # salt = crypt.mksalt(crypt.METHOD_SHA512, rounds=9999)
    return crypt.crypt(word,'$6$rounds=9999$1mtFFonQaqzzg3kh')

  def _compile_query(self, query : Query):
    compiler = query.compile if not hasattr(query, 'statement') else query.statement.compile
    return compiler(dialect=postgresql.dialect())

  @contextmanager
  def session_scope(self):
    """Provide a transactional scope around a series of operations."""
    l_session = self.session()
    try:
      yield l_session
      l_session.commit()
    except Exception as ex:
      l_session.rollback()
      logger.error(f'The following error happened during commit : {ex}')
      raise
    finally:
      l_session.expunge_all()
      l_session.close()

if __name__ == '__main__':
  pass
  # db = Database("database")
  # db.create_missing_tables()
  # **db.reset_tables()**
  # db.insert_value([dict({"id":"comp_1", "address":"24 Avenue Frayce", "zip_code":"93400"}),
  #                 dict({"id":"room_1.1", "description":"ROOM_1.1", "comp_id":"comp_1"}),
  #                 dict({"id":"zone_1.1.1", "description":"ZONE_1.1.1", "room_id":"room_1.1"}),
  #                 dict({"id":"zone_1.1.2", "description":"ZONE_1.1.2", "room_id":"room_1.1"})], [Company, Room, Zone, Zone])

  # db.insert_value(['{"id":"comp_1", "address":"24 Avenue Frayce", "zip_code":"93400"}',
  #                  '{"id":"room_1.1", "description":"ROOM_1.1", "company_id":"comp_1"}',
  #                  '{"id":"zone_1.1.1", "description":"ZONE_1.1.1", "room_id":"room_1.1"}',
  #                  '{"id":"zone_1.1.2", "description":"ZONE_1.1.2", "room_id":"room_1.1"}' ], [Company, Room, Zone, Zone])

  # db.nsert_value(['{"id":"comp_1", "address":"24 Avenue Frayce", "zip_code":"93400"}'], [Company])

