import os
from datetime import datetime

from pony.orm import *
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = str(os.getenv('POSTGRES_HOST'))
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT'))
POSTGRES_USER = str(os.getenv('POSTGRES_USER'))
POSTGRES_PASS = str(os.getenv('POSTGRES_PASS'))

db = Database()
db.bind(provider='postgres', host=POSTGRES_HOST, port=POSTGRES_PORT,
        user=POSTGRES_USER, password=POSTGRES_PASS)


class Virgin(db.Entity):
  guild = Required(str, index=True)
  id = Required(str, index=True, unique=True)
  name = Required(str)
  discriminator = Required(str)
  total_vc_time = Required(float, default=0)
  total_vc_time_ever = Required(float, default=0)
  virginity_score = Required(int, default=0, index=True)
  vc_connection_start = Optional(datetime)

  PrimaryKey(guild, id)

  def is_user(name, disc):
    return this.name == name and this.discriminator == disc


db.generate_mapping(create_tables=True)


@db_session
def get_biggest_virgin(guild: str):
  return Virgin.select().sort_by(desc(Virgin.virginity_score)).limit(1)[0]


@db_session
def get_smolest_virgin(guild: str):
  return Virgin.select().sort_by(Virgin.virginity_score).limit(1)[0]


@db_session
def get_users_virginity_by_id(guild: str, ID: str):
  return Virgin.get(guild=guild, id=ID)
