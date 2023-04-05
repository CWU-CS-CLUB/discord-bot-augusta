#!/usr/bin/env python
"""bot.py: Runs Discord API bot 'Augusta'"""

import discord
import requests
from requests import Response

__author__: 'Alice Williams'
__version__: '0.0.0'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
api = 'https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,religious,political,racist,sexist,explicit'

help_text = 'Current commands:\n$help - shows this message\n$hello - says hello back\n$echo <msg> - echos a msg string\n$joke - prints a programmer joke'

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
        await message.channel.send(help_text)
    elif msg == '$joke':
        joke = requests.get(api).json()
        joke = joke  # hacky fix
        await message.channel.send(joke["joke"])


token_file = open('token.txt', 'r')
token = token_file.readline()
token_file.close()
client.run(token)
