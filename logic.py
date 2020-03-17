import os
import math

from database import Virgin

POINTS_PER_MINUTE = float(os.getenv('POINTS_PER_MINUTE') or 5)
BOT_SCORE_MULTIPLIER = float(os.getenv('BOT_SCORE_MULTIPLIER') or 0.5)


def calc_total_virginity(virgin: Virgin):
  # TODO: implement a curve for virginity
  # TODO: implement a score multiplier for bots
  virginity_score = virgin.total_vc_time / 60 * POINTS_PER_MINUTE
  if virgin.is_bot:
    virginity_score *= BOT_SCORE_MULTIPLIER
  return math.floor(virginity_score)
