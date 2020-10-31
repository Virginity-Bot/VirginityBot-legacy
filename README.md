# VirginityBot

A discord bot for the biggest virgins.

[Invite the official Virginity Bot to your Server](https://discordapp.com/api/oauth2/authorize?client_id=688470281320267800&permissions=472991744&scope=bot)

## Supported Commands

- `/myvirginity` - check your own virginity
- `/checkvirginity {Discord.User}` - check virginity of other users in the server
- `/biggestvirgin` - biggest Virgin in the server
- `/topvirgin` - biggest Virgin in the server
- `/smolestvirgin` - smolest Virgin in the server
- `/leaderboard` - list top 10 virgins in the server
- `/resetvirginity` - Reset your virginity

## How to Increase Your Virginity

1. Virginity counter starts on initial voice channel join
2. Virgins must not be muted of deafened
3. Virgins may not be in the AFK channel

### Potential Improvements

- Alpha virgin role - rename to Ω Virgin?
- Extra points for streaming with viewers?

## Run your own Virginity Bot

1. (Create a new Discord Application](https://discord.com/developers/applications/]
   1. Retrive your Bot Token from the bot tab
1. Use to host your own instance with Docker [/docker-compose.yaml](/docker-compose.yaml)
   1. `$ docker-compose up -d`
   1. Make sure to set the [/virginity-bot.env](/virginity-bot.env) variables appropriately.

## Permissions

- Manage Roles
  - Required to create and move the biggest virgin role.
- Manage Nickname
- Change Nickname
- Send Messages
  - Required to respond to commands.
- Embed Links
  - Required to respond to commands.
- Read Message History
  - Required to respond to commands.
- Connect
  - Required for playing the biggest virgin's intro theme.
- Speak
  - Required for playing the biggest virgin's intro theme.
