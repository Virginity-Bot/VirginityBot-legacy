# bot.py
import os
import random
import functools
import re
import array

from datetime import datetime, timedelta
import asyncio
import logging

import discord
from discord import *
from discord.ext import commands
from dotenv import load_dotenv
from pony.orm import *

from database import *

load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))

logger = logging.getLogger('virginity-bot')

bot = commands.Bot(command_prefix=('/'))
bot.remove_command('help')

voice_client: VoiceClient = None


@bot.event
async def on_connect():
  logger.info(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_ready():
  logger.info(f'{bot.user.name} is ready!')

  with db_session:
    for guild in bot.guilds:
      for channel in guild.channels:
        if channel.type == discord.ChannelType.voice and channel != guild.afk_channel:
          for virgin in channel.members:
            if Virgin.exists(guild_id=str(guild.id), id=str(virgin.id)):
              virgin = Virgin.get(
                  guild_id=str(guild.id), id=str(virgin.id))
              virgin.vc_connection_start = datetime.now()
              commit()
            else:
              Virgin(guild_id=str(guild.id), id=str(virgin.id), name=virgin.name,
                     discriminator=virgin.discriminator,
                     vc_connection_start=datetime.now(), is_bot=virgin.bot)


@bot.event
async def on_disconnect():
  logger.warn(f'{bot.user.name} has disconnected from Discord!')
  # TODO: wrap up all open transactions
  if voice_client != None:
    await voice_client.disconnect()

# /help
@bot.command(name='help')
async def help(ctx):
  if ctx.message.author == bot.user:
    return

  msg = Embed(title='Virginity Bot - Help', url='https://discordapp.com/api/oauth2/authorize?client_id=688470281320267800&permissions=472991744&scope=bot')
  msg.add_field(name='/myvirginity', value='Check your own virginity.', inline=False)
  msg.add_field(name='/checkvirginity {user}', value='Check the virginity of a user.', inline=False)
  msg.add_field(name='/biggestvirgin', value='Find the biggest virgin in the server.', inline=False)
  msg.add_field(name='/topvirgin', value='Find the biggest virgin in the server.', inline=False)
  msg.add_field(name='/smolestvirgin', value='Find the smolest virgin in the server.', inline=False)
  msg.add_field(name='/leaderboard', value='List the biggest virgins in the server.', inline=False)
  msg.add_field(name='/resetvirginity', value='Undo your virginity.', inline=False)
  
  await ctx.message.author.send(embed=msg)

# /myvirginity
@bot.command(name='myvirginity')
async def myvirginity(ctx):
  if ctx.message.author == bot.user:
    return
  await ctx.trigger_typing()
  with db_session:
    virgin = Virgin.get(guild_id=str(ctx.message.guild.id),
                        id=str(ctx.message.author.id))
    if virgin is None:
      virgin = Virgin(id=str(ctx.message.author.id), guild_id=str(ctx.message.guild.id),
                      name=ctx.message.author.name, discriminator=ctx.message.author.discriminator,
                      is_bot=ctx.message.author.bot)
      return await ctx.send(f'{virgin.name} ain\'t no virgin. (at least not yet)')
    virginity_score = calc_total_virginity(virgin)
    commit()
    return await ctx.send(virginity_score)

# /checkvirgininty
@bot.command(name='checkvirginity')
async def checkvirginity(ctx):
  if ctx.message.author == bot.user:
    return
  await ctx.trigger_typing()

  match = re.match(r'^\/checkvirginity <@(&?[0-9]+)>\W*$', ctx.message.content)
  if not match:
    return await ctx.send('User specification failed')
  else:
    with db_session:
      virgin = Virgin.get(guild_id=str(ctx.message.guild.id),
                          id=match.group(1))
      if not virgin:
        return await ctx.send('Virgin not found')
      else:
        virginity_score = calc_total_virginity(virgin)
        commit()
        return await ctx.send(virginity_score)

# /biggestvirgin
@bot.command(name='biggestvirgin')
async def biggestvirgin(ctx):
  if ctx.message.author == bot.user:
    return
  await ctx.trigger_typing()
  await handlebiggestvirgin(ctx)

# /topvirgin
@bot.command(name='topvirgin')
async def topvirgin(ctx):
  if ctx.message.author == bot.user:
    return
  await ctx.trigger_typing()
  await handlebiggestvirgin(ctx)

# /smolestvirgin
@bot.command(name='smolestvirgin')
async def smolestvirgi_n(ctx):
  if ctx.message.author == bot.user:
    return
  await ctx.trigger_typing()
  await handlesmolestvirgin(ctx)


# /leaderboard
@bot.command(name='leaderboard')
async def leaderboard(ctx: commands.Context):
  if ctx.message.author == bot.user:
    return
  await ctx.trigger_typing()

  calculatedVCVirgs = []
  combinedTop = []
  topVirgins = get_top_virgins(str(ctx.guild.id))
  vcVirgins = get_active_virgins(str(ctx.guild.id))
  
  with db_session:
    for vcVirg in vcVirgins:
      virgScore = calc_total_virginity(vcVirg)
      calculatedVCVirgs.append((vcVirg.id, vcVirg.name, virgScore))

    for topVirg in topVirgins:
      isAdded = False
      for calcVirg in calculatedVCVirgs:
        if topVirg.id == calcVirg[0]:
          isAdded = True
          combinedTop.append(calcVirg)
          break
      if not isAdded:
        combinedTop.append((topVirg.id, topVirg.name, topVirg.virginity_score))

  combinedTop = sorted(combinedTop, key=lambda x: x[2], reverse=True)
  logger.info(combinedTop)

  msg = Embed(
      title=f'Biggest Virgins of {ctx.guild.name}', description='')
  # msg.color(Colour.from_rgb(255, 41, 255))
  # msg.add_field(name='field 1', value='value 1')
  for i, tVirgin in enumerate(combinedTop):
    msg.description += f'**{i + 1}.** {tVirgin[1]} - {tVirgin[2]}\n'
  await ctx.send(embed=msg)


# /resetvirginity
@bot.command(name='resetvirginity')
async def resetvirginity(ctx):
  if ctx.message.author == bot.user:
    return
  return await ctx.send(f'🔴 I\'m sorry {ctx.message.author.name}, I\'m afraid I can\'t do that.')

# /add
@bot.command(name='add')
async def add(ctx):
  if ctx.message.author == bot.user:
    return
  return await ctx.send(f'Please send 1₿ to 1F1tAaz5-1HUXrLMAOMDqcw69xGNn4xqX')


@bot.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
  # Virgin connects to VC
  with db_session:
    if before.channel is None and after.channel is not None:
      logger.info(f'{member.name} connected')
      start_adding_virginity(member, after)
    elif before.channel is not None and after.channel is None:
      logger.info(f'{member.name} disconnected')
      virgin = member_to_virgin(member)
      if virgin != None and virgin.vc_connection_start != None:
        stop_adding_virginity(virgin)
    elif after.afk:
      logger.info(f'{member.name} went AFK')
      virgin = member_to_virgin(member)
      if virgin != None and virgin.vc_connection_start != None:
        stop_adding_virginity(virgin)
    elif before.afk and after.channel is not None:
      logger.info(f'{member.name} is not AFK')
      start_adding_virginity(member, after)
    elif (
        (before.self_mute == False or before.mute == False) and
        (after.self_mute == True or after.mute == True)) or (
        (before.self_deaf == False or before.deaf == False) and
            (after.self_deaf == True or after.mute == True)):
      logger.info(f'{member.name} muted')
      virgin = member_to_virgin(member)
      if virgin != None and virgin.vc_connection_start != None:
        stop_adding_virginity(virgin)
    elif (
        (before.self_mute == True or before.mute == True) and
        (after.self_mute == False or after.mute == False)) or (
        (before.self_deaf == True or before.deaf == True) and
            (after.self_deaf == False or after.mute == False)):
      logger.info(f'{member.name} unmuted')
      start_adding_virginity(member, after)

    # Play entrance music
    if not after.afk and (
        (before.channel is None and after.channel is not None) or
        (after.channel is not None and
            (before.self_mute == after.self_mute and
             before.self_deaf == after.self_deaf and
             before.self_stream == after.self_stream)
         )
    ):
      # TODO: figure out a way to cache this
      guild = Guild.get(id=str(member.guild.id))

      if len(list(filter(lambda role: str(role.id) == guild.biggest_virgin_role_id, member.roles))) >= 1:
        logger.info(f'biggest virgin has connected')
        await play_entrance_theme(after.channel)


@db_session
def member_to_virgin(member: Member):
  if Virgin.exists(guild_id=str(member.guild.id), id=str(member.id)):
    return Virgin.get(guild_id=str(member.guild.id), id=str(member.id))


@db_session
def start_adding_virginity(virgin: Member, voice_state: VoiceState):
  if not voice_state.afk:
    if voice_state.self_mute == False and voice_state.self_deaf == False:
      if Virgin.exists(guild_id=str(virgin.guild.id), id=str(virgin.id)):
        real_virgin = Virgin.get(guild_id=str(virgin.guild.id),
                                 id=str(virgin.id))
        # TODO: be more thoughtful about overriding start times
        real_virgin.vc_connection_start = datetime.now()
        real_virgin.vc_connection_end = None
        commit()
      else:
        Virgin(guild_id=str(virgin.guild.id), id=str(virgin.id), name=virgin.name,
               discriminator=virgin.discriminator,
               vc_connection_start=datetime.now(), is_bot=virgin.bot)


@db_session
def stop_adding_virginity(virgin: Virgin, finish_transaction=True):
  virgin.vc_connection_end = datetime.now()
  vc_conn_end = virgin.vc_connection_end
  vc_conn_start = virgin.vc_connection_start
  latest_vc_time = calc_time_difference(vc_conn_start, vc_conn_end)
  if (latest_vc_time < 0):
    logger.error(f'🚨🚨🚨 OH SHIT {virgin.name} has NEGATIVE VIRGINITY 🚨🚨🚨')

  virgin.total_vc_time += latest_vc_time
  virgin.total_vc_time_ever += latest_vc_time

  print(f'{virgin.name} spent {timedelta(seconds=latest_vc_time)} in VC')

  virgin.virginity_score = calc_total_virginity(virgin)

  virgin.vc_connection_start = None
  virgin.vc_connection_end = None
  if finish_transaction:
    commit()


async def handlebiggestvirgin(ctx):
  calculatedVCVirgs = []
  combinedTop = []
  topVirgins = get_top_virgins(str(ctx.guild.id))
  vcVirgins = get_active_virgins(str(ctx.guild.id))
  
  with db_session:
    for vcVirg in vcVirgins:
      virgScore = calc_total_virginity(vcVirg)
      calculatedVCVirgs.append((vcVirg.id, vcVirg.name, virgScore))

    for topVirg in topVirgins:
      isAdded = False
      for calcVirg in calculatedVCVirgs:
        if topVirg.id == calcVirg[0]:
          isAdded = True
          combinedTop.append(calcVirg)
          break
      if not isAdded:
        combinedTop.append((topVirg.id, topVirg.name, topVirg.virginity_score))

  combinedTop = sorted(combinedTop, key=lambda x: x[2], reverse=True)
  logger.info(combinedTop)

  msg = Embed(
      title=f'Biggest Virgin of {ctx.guild.name}', description='')
  # msg.color(Colour.from_rgb(255, 41, 255))
  # msg.add_field(name='field 1', value='value 1')
  for i, tVirgin in enumerate(combinedTop):
    if i < 1:
      msg.description += f'{tVirgin[1]} with {tVirgin[2]} {pluralize("points", tVirgin[2])} 💦'
  await ctx.send(embed=msg)


async def handlesmolestvirgin(ctx):
  calculatedVCVirgs = []
  combinedBot = []
  botVirgins = get_bot_virgins(str(ctx.guild.id))
  vcVirgins = get_active_virgins(str(ctx.guild.id))
  
  with db_session:
    for vcVirg in vcVirgins:
      virgScore = calc_total_virginity(vcVirg)
      calculatedVCVirgs.append((vcVirg.id, vcVirg.name, virgScore))

    for botVirg in botVirgins:
      isAdded = False
      for calcVirg in calculatedVCVirgs:
        if botVirg.id == calcVirg[0]:
          isAdded = True
          combinedBot.append(calcVirg)
          break
      if not isAdded:
        combinedBot.append((botVirg.id, botVirg.name, botVirg.virginity_score))

  combinedBot = sorted(combinedBot, key=lambda x: x[2])
  logger.info(combinedBot)

  msg = Embed(
      title=f'Smolest Virgin of {ctx.guild.name}', description='')
  # msg.color(Colour.from_rgb(255, 41, 255))
  # msg.add_field(name='field 1', value='value 1')
  for i, tVirgin in enumerate(combinedBot):
    if i < 1:
      msg.description += f'{tVirgin[1]} with {tVirgin[2]} {pluralize("points", tVirgin[2])} 🌈'
  await ctx.send(embed=msg)

async def play_entrance_theme(channel):
  voice_client = await channel.connect()
  greeting = FFmpegPCMAudio('./assets/entrance_theme.opus')
  logger.info('starting entrance theme')
  voice_client.play(
      greeting, after=lambda e: logger.info(f'🚨 finished entrance theme'))
  while voice_client.is_playing():
    await asyncio.sleep(1)
  await voice_client.disconnect()


def pluralize(non_plural: str, val: int):
  return non_plural + ('s' if val != 1 else '')


def start_bot():
  bot.run(TOKEN)


def stop_bot():
  with db_session:
    for virgin in select(v for v in Virgin if v.vc_connection_start != None)[:]:
      stop_adding_virginity(virgin, finish_transaction=False)
    commit()
  if voice_client != None:
    voice_client.disconnect()
  bot.close()
