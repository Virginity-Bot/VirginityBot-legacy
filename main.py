import atexit

from database import start_orm
from bot import start_bot, stop_bot
from healthcheck import start_server


def main():
  start_orm()
  # start_server()
  start_bot()


if __name__ == '__main__':
  main()


def on_exit():
  print('\nExitting')
  stop_bot()


atexit.register(on_exit)
