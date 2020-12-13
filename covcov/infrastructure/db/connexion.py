from sqlalchemy import create_engine
from covcov.infrastructure.configuration.config import config

class Connexion(object):
  def __init__(self, database_key:str):
    self.url  = config[database_key]["connection_string"]
    self.echo = config[database_key]["echo"]

  def connect(self):
    return create_engine(self.url, echo=self.echo)
