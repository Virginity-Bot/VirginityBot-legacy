import os
import asyncio
import json
import logging

from dotenv import load_dotenv
from pony.orm import *
import requests

import logger
from database import start_orm, get_biggest_virgin, Guild

logger = logging.getLogger('virginity-bot')


load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))

HOSTNAME = 'discordapp.com'
API_PATH = f'https://{HOSTNAME}/api'


async def award_omega_virgin_roles():
  s = requests.Session()
  s.headers.update({'Authorization': f'Bot {TOKEN}'})

  with db_session:
    guilds = Guild.select()
    for guild in guilds:
      if guild.biggest_virgin_role_id == None:
        continue
      else:
        omega_virgin = get_biggest_virgin(guild.id)
        logger.info(f'{omega_virgin.name} is {guild.name}\'s biggest virgin')

        res = s.delete(
            f'{API_PATH}/guilds/{guild.id}/roles/{guild.biggest_virgin_role_id}')
        if res.status_code == 204:
          logger.info('Deleted old role')

        body = {
            'name': 'Chonkiest Virgin the World Has Ever Seen',
            'color': '15098520',
            'hoist': True,
            'mentionable': True
        }
        res = s.post(f'{API_PATH}/guilds/{guild.id}/roles', json=body)
        new_role = res.json()
        if res.status_code == 200:
          guild.biggest_virgin_role_id = new_role['id']
          commit()
          logger.info('Created new role')
        else:
          logger.error('Failed to create role')
          logger.error(res.status_code)
          logger.error(res.text)
          raise Exception('Failed to create role')

        body = {
            'id': guild.biggest_virgin_role_id,
            'position': 1
        }
        res = s.patch(f'{API_PATH}/guilds/{guild.id}/roles', json=body)
        if res.status_code == 200:
          logger.info('Set role to position 1')

        res = s.put(
            f'{API_PATH}/guilds/{guild.id}/members/{omega_virgin.id}/roles/{guild.biggest_virgin_role_id}')
        if res.status_code == 204:
          logger.info('Added role to biggest virgin')


async def main():
  logger.info('Running daily reset')
  start_orm()
  await award_omega_virgin_roles()


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
