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

bot = commands.Bot(command_prefix=('/'))

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')

  guilds = bot.guilds
  voice_channels = []

  with db_session:
    for guild in bot.guilds:
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

# /myvirginity
@bot.command(name='myvirginity')
async def myvirginity(ctx):
    if ctx.message.author == bot.user:
      return
    with db_session:
      virgin = Virgin.get(guild=str(ctx.message.guild.id),
                          id=str(ctx.message.author.id))
      virgin.virginity_score = calc_total_virginity(virgin)
      commit()
      await ctx.send(virgin.virginity_score)

# /checkvirgininty
@bot.command(name='checkvirginity')
async def checkvirginity(ctx):
    if ctx.message.author == bot.user:
      return
    match = re.match('^\/checkvirginity <@([0-9]+)>\W*$', ctx.message.content)
    if not match:
      await ctx.send('User specification failed')
    else:
      virgin = Virgin.get(guild=str(ctx.message.guild.id), id=match.group(1))
      if not virgin:
        await ctx.send('Virgin not found')
      else:
        virgin.virginity_score = calc_total_virginity(virgin)
        commit()
        await ctx.send(virgin.virginity_score)

# /biggestvirgin
@bot.command(name='biggestvirgin')
async def biggestvirgin(ctx):
    if ctx.message.author == bot.user:
      return
    # TODO: update virginity_score for all connected users before display
    await handlebiggestvirgin(ctx)

# /topvirgin
@bot.command(name='topvirgin')
async def topvirgin(ctx):
    if ctx.message.author == bot.user:
      return
    # TODO: update virginity_score for all connected users before display
    await handlebiggestvirgin(ctx)

# /smolestvirgin
@bot.command(name='smolestvirgin')
async def smolestvirgin(ctx):
    if ctx.message.author == bot.user:
      return
    # smol = get_smolest_virgin(str(ctx.message.guild.id))
    # await ctx.send(f'🏩 {smol.name} 💦')
    await handlesmolestvirgin(ctx)

# /resetvirginity
@bot.command(name='resetvirginity')
async def resetvirginity(ctx):
    if ctx.message.author == bot.user:
      return
    await ctx.send(f'🔴 I\'m sorry {ctx.message.author.name}, I\'m afraid I can\'t do that.')

# /add
@bot.command(name='add')
async def add(ctx):
    if ctx.message.author == bot.user:
      return
    await ctx.send(f'Please send 1₿ to 1F1tAaz5-1HUXrLMAOMDqcw69xGNn4xqX')


@bot.event
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

async def handlebiggestvirgin(ctx):
  bigun = get_biggest_virgin(str(ctx.message.guild.id))
  await ctx.send(f'🎉 {bigun.name} :nun:')

async def handlesmolestvirgin(ctx):
  smol = get_smolest_virgin(str(ctx.message.guild.id))
  await ctx.send(f'🏩 {smol.name} 💦')


bot.run(TOKEN)