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


class Virgin(db.Entity):
  id = Required(str, index=True)
  guild_id = Required(str, index=True)
  name = Required(str)
  discriminator = Required(str)
  is_bot = Required(bool, default=False)
  total_vc_time = Required(float, default=0)
  total_vc_time_ever = Required(float, default=0)
  virginity_score = Required(int, default=0, index=True)
  vc_connection_start = Optional(datetime)

  PrimaryKey(guild_id, id)


class Guild(db.Entity):
  id = PrimaryKey(str)
  name = Required(str)
  # virgins = Set(Virgin)



def start_orm():
  db.bind(provider='postgres', host=POSTGRES_HOST, port=POSTGRES_PORT,
          user=POSTGRES_USER, password=POSTGRES_PASS)

  db.generate_mapping(create_tables=True)


@db_session
def get_biggest_virgin(guild: str):
  return Virgin.select(lambda v: v.guild_id == guild).sort_by(desc(Virgin.virginity_score)).limit(1)[0]


@db_session
def get_top_virgins(guild: str, limit=5, exclude_bots=True):
  # TODO: actually respect exclude_bots
  return Virgin.select(lambda v: v.guild_id == guild and v.is_bot == False).sort_by(desc(Virgin.virginity_score)).limit(limit)


@db_session
def get_smolest_virgin(guild: str):
  return Virgin.select(lambda v: v.guild_id == guild).sort_by(Virgin.virginity_score).limit(1)[0]


@db_session
def get_users_virginity_by_id(guild: str, ID: str):
  return Virgin.get(guild_id=guild, id=ID)


@db_session
def calculate_time_difference(virgin: Virgin):
  vc_conn_end = datetime.now()
  vc_conn_start = virgin.vc_connection_start
  secdiff = float(db.get(f'SELECT DateDiff (\'s\',\'{vc_conn_start}\',\'{vc_conn_end}\');'))
  return secdiff