
from covcov.infrastructure.db.database import Database
db = Database("database")

def handle(event, context):
  db.native_execute_sqls(["select 1"])
  return {
    "statusCode": 200,
    "headers" : {
      "Content-Type" : "application/json",
      "Access-Control-Allow-Headers": "*",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    },
    "body" : str({})
  }