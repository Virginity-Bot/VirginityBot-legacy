import os
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
  name = Required(str)
  discriminator = Required(str)
  total_vc_time = Required(float, default=0)
  total_vc_time_ever = Required(float, default=0)
  virginity_score = Required(int, default=0, index=True)

  PrimaryKey(name, discriminator)
  # SecondaryKey(virginity_score)

  def is_user(name, disc):
    return this.name == name and this.discriminator == disc


db.generate_mapping(create_tables=True)


@db_session
def get_biggest_virgin():
  return Virgin.select().sort_by(desc(Virgin.virginity_score)).limit(1)


@db_session
def get_users_virginity(name: str, disc: str):
  return Virgin.get(name=name, discriminator=disc)


with db_session:
  # print(select(p for p in Virgin))
  v = Virgin.get(name='DudeOfAwesome')
  print(v)
  print(get_biggest_virgin())
  # print(vars(Virgin))
