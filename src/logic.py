import os
import math
from datetime import datetime

from database import Virgin

POINTS_PER_MINUTE = float(os.getenv('POINTS_PER_MINUTE') or 5)
BOT_SCORE_MULTIPLIER = float(os.getenv('BOT_SCORE_MULTIPLIER') or 0.5)


def calc_total_virginity(virgin: Virgin):
  # TODO: implement a curve for virginity
  uncounted_time_in_vc = (datetime.now(
  ) - virgin.vc_connection_start).total_seconds() if virgin.vc_connection_start != None else 0
  virginity_score = (virgin.total_vc_time +
                     uncounted_time_in_vc) / 60 * POINTS_PER_MINUTE
  if virgin.is_bot:
    virginity_score *= BOT_SCORE_MULTIPLIER
  return math.floor(virginity_score)
