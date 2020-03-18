import os
import asyncio
import logging

from pony.orm import *

import logger
from database import start_orm, get_biggest_virgin, Guild

logger = logging.getLogger('virginity-bot')


async def reset_weekly_virginity():
  with db_session:
    virgins = Virgin.select()
    for virgin in virgins:
      virgin.total_vc_time = 0
      virgin.virginity_score = 0
      commit()


async def main():
  logger.info('Running weekly reset')
  start_orm()
  await reset_weekly_virginity()


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
