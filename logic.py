import math

def calc_total_virginity(virgin):
  # TODO: implement a curve for virginity
  # TODO: implement a score multiplier for bots
  return math.floor(virgin.total_vc_time / 60 * 5)