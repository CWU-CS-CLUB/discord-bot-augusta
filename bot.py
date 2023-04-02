#!/usr/bin/env python
"""bot.py: Runs Discord API bot 'Augusta'"""

import discord

__author__: 'Alice Williams'
__version__: '0.0.0'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg == '$hello':
        await message.channel.send('Hello!')
    elif msg.startswith('$echo'):
        await message.channel.send(message.content)
    elif msg.startswith('$help'):
        await message.channel.send('Current commands:\n$help - shows this message\n$hello - says hello back\n$echo <msg> - echos a msg string')


token_file = open('token.txt', 'r')
token = token_file.readline()
client.run(token)
