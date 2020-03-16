# bot.py
import os
import random
import functools
import numpy as np
import re
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pony.orm import *

from database import *
from logic import *

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

  with db_session:
    for guild in client.guilds:
      for channel in guild.channels:
        # print(f'{channel},{channel.type}')
        if channel.type == discord.ChannelType.voice and channel != guild.afk_channel:
          # virgins.append(channel.members)
          for virgin in channel.members:
            if Virgin.exists(guild=str(guild.id), id=str(virgin.id)):
              print('User already registered')
              virgin = Virgin.get(
                  guild=str(guild.id), id=str(virgin.id))
              virgin.vc_connection_start = datetime.now()
              commit()
            else:
              Virgin(guild=str(guild.id), id=str(virgin.id), name=virgin.name,
                     discriminator=virgin.discriminator)


@db_session
@client.event
# /myvirginity
async def on_message(message):
  with db_session:
    show(message)
    if message.author == client.user:
      return
    if message.content.startswith('/myvirginity'):
      virgin = Virgin.get(guild=str(message.guild.id),
                          id=str(message.author.id))
      virgin.virginity_score = calc_total_virginity(virgin)
      commit()
      await message.channel.send(virgin.virginity_score)
    if message.content.startswith('/checkvirginity'):
      print(message.content)
      match = re.match('^\/checkvirginity <@([0-9]+)>\W*$', message.content)
      if not match:
        await message.channel.send('User specification failed')
      else:
        virgin = Virgin.get(guild=str(message.guild.id), id=match.group(1))
        if not virgin:
          await message.channel.send('Virgin not found')
        else:
          virgin.virginity_score = calc_total_virginity(virgin)
          commit()
          await message.channel.send(virgin.virginity_score)
    if message.content.startswith('/biggestvirgin') or message.content.startswith('/topvirgin'):
      # TODO: update virginity_score for all connected users before display
      bigun = get_biggest_virgin(str(message.guild.id))
      await message.channel.send(f'🎉 {bigun.name} :nun:')
    if message.content.startswith('/smolestvirgin'):
      smol = get_smolest_virgin(str(message.guild.id))
      await message.channel.send(f'🏩 {smol.name} 💦')
    if message.content.startswith('/resetvirginity'):
      await message.channel.send(f'🔴 I\'m sorry {message.author.name}, I\'m afraid I can\'t do that.')
    if message.content.startswith('/add'):
      await message.channel.send(f'Please send 1₿ to 1F1tAaz5-1HUXrLMAOMDqcw69xGNn4xqX')


@db_session
@client.event
async def on_voice_state_update(member, before, after):
  with db_session:
    # Virgin connects to VC
    if before.channel == None and after.channel != None:
      # if after.channel != afk
      if Virgin.exists(guild=str(member.guild.id), id=str(member.id)):
        print('User connected')
        virgin = Virgin.get(
            guild=str(member.guild.id), id=str(member.id))
        # TODO: be more thoughtful about overriding start times
        virgin.vc_connection_start = datetime.now()
        commit()
      else:
        Virgin(guild=str(member.guild.id), id=str(member.id), name=member.name,
               discriminator=member.discriminator)
    elif before.channel != None and after.channel == None:
      # if after.channel != afk
      if Virgin.exists(guild=str(member.guild.id), id=str(member.id)):
        print('User disconnected')
        virgin = Virgin.get(
            guild=str(member.guild.id), id=str(member.id))
        time_spent = datetime.now() - virgin.vc_connection_start
        print('time_spent')
        print(time_spent)
        virgin.total_vc_time += time_spent.total_seconds()
        virgin.total_vc_time_ever += time_spent.total_seconds()
        virgin.virginity_score = calc_total_virginity(virgin)
        virgin.vc_connection_start = None
        commit()

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
