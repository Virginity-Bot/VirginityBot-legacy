# bot.py
import os
import random
import functools
import numpy as np

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pony.orm import *

from database import *

load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))

# print(TOKEN)

client = discord.Client()


@db_session
@client.event
async def on_ready():
  print(f'{client.user.name} has connected to Discord!')

  guilds = client.guilds
  voice_channels = []
  virgins = []

  for guild in client.guilds:
    for channel in guild.channels:
      print(f'{channel},{channel.type}')
      if channel.type == discord.ChannelType.voice and channel != guild.afk_channel:
        virgins.append(channel.members)

  print(virgins)


@db_session
@client.event
# /myvirginity
async def on_message(message):
  print(message)
  if message.author == client.user:
    return
  if message.content.startswith('/myvirginity'):
    await message.channel.send(get_users_virginity(message.author.name, message.author.discriminator).virginity_score)

# @bot.command(name='biggestvirgin')
# async def biggestvirgin(ctx):
#     if message.author == client.user:
#         return

#     response =
#     await ctx.send(response)


# @bot.commd(name='sizedoesntmatter')
# async def sizedoesntmatter(ctx):
#     if message.author == client.user:
#         return

#     response =
#     await ctx.send(response)


client.run(TOKEN)
