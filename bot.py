# bot.py
import os
import random
import functools
import numpy as np
import re

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

  for guild in client.guilds:
    show(guild)
    for channel in guild.channels:
      print(f'{channel},{channel.type}')
      if channel.type == discord.ChannelType.voice and channel != guild.afk_channel:
        # virgins.append(channel.members)
        for virgin in channel.members:
          with db_session:
            Virgin(id=str(virgin.id), guild=str(guild.id), name=virgin.name,
                   discriminator=virgin.discriminator)


@db_session
@client.event
# /myvirginity
async def on_message(message):
  show(message)
  if message.author == client.user:
    return
  if message.content.startswith('/myvirginity'):
    await message.channel.send(get_users_virginity_by_id(str(message.guild.id), str(message.author.id)).virginity_score)
  if message.content.startswith('/checkvirginity'):
    print(message.content)
    match = re.match('^\/checkvirginity <@([0-9]+)>\W*$', message.content)
    if not match:
      await message.channel.send('User specification failed')
    else:
      virgin = get_users_virginity_by_id(str(message.guild.id), match.group(1))
      if not virgin:
        await message.channel.send('Virgin not found')
      else:
        await message.channel.send(virgin.virginity_score)
  if message.content.startswith('/biggestvirgin'):
    bigun = get_biggest_virgin(str(message.guild.id))
    await message.channel.send(f'{bigun.name}')
  if message.content.startswith('/smolestvirgin'):
    smol = get_smolest_virgin(str(message.guild.id))
    await message.channel.send(f'{smol.name}')
  if message.content.startswith('/resetvirginity'):
    await message.channel.send(f'I\'m sorry {message.author.name}, I\'m afraid I can\'t do that.')

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
