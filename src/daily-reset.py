import os
import asyncio
import json
import logging
import functools

from dotenv import load_dotenv
from pony.orm import *
from discord import Color
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
      omega_virgin = get_biggest_virgin(guild.id)
      logger.info(f'{omega_virgin.name} is {guild.name}\'s biggest virgin')

      if guild.biggest_virgin_role_id != None:
        res = s.delete(
            f'{API_PATH}/guilds/{guild.id}/roles/{guild.biggest_virgin_role_id}')
        if res.status_code == 204:
          logger.info('Deleted old role')
        else:
          logger.error(f'Error deleting old role for {guild.name}')

      # create new role
      res = s.post(f'{API_PATH}/guilds/{guild.id}/roles', json={
          'name': 'Chonkiest Virgin the World Has Ever Seen',
          'color': Color.from_rgb(230, 98, 152).value,
          'hoist': True,
          'mentionable': True
      })
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

      res = s.put(
          f'{API_PATH}/guilds/{guild.id}/members/{omega_virgin.id}/roles/{guild.biggest_virgin_role_id}')
      if res.status_code == 204:
        logger.info('Added role to biggest virgin')

      # get current user's highest role
      # get current user
      res = s.get(f'{API_PATH}/users/@me')
      if res.status_code != 200:
        logger.error('Failed to get bot user')
        logger.error(res.text)
        raise Exception('Failed to get bot user')
      bot_user = res.json()
      bot_user_id = bot_user['id']

      # get user in the guild
      res = s.get(f'{API_PATH}/guilds/{guild.id}/members/{bot_user_id}')
      if res.status_code != 200:
        logger.error(res.text)
        logger.info('Failed to retrieve guild bot member')
      guild_bot_user = res.json()
      guild_bot_user['roles']

      # get guild's roles
      res = s.get(f'{API_PATH}/guilds/{guild.id}/roles')
      if res.status_code != 200:
        logger.error(res.text)
        logger.info('Failed to retrieve guild roles')
      guild_roles = res.json()

      # find bot's highest role in the guild
      def reducer(highest_role, curr):
        for guild_role in guild_roles:
          if guild_role['id'] == curr:
            if highest_role == None:
              return guild_role
            if guild_role['position'] > highest_role['position']:
              return guild_role
        return highest_role
      highest_role = functools.reduce(reducer, guild_bot_user['roles'], None)
      target_role_pos = highest_role['position'] - 1

      logger.info(f'Moving role to {target_role_pos}')

      # set role's position to one below the bot's highest role
      res = s.patch(f'{API_PATH}/guilds/{guild.id}/roles', json=[{
          'id': guild.biggest_virgin_role_id,
          'position': target_role_pos
      }])
      if res.status_code == 200:
        logger.info('Moved role position up')
      else:
        logger.error(res.text)


async def main():
  logger.info('Running daily reset')
  start_orm()
  await award_omega_virgin_roles()


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
