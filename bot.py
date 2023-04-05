#!/usr/bin/env python
"""bot.py: Runs Discord API bot 'Augusta'"""

import discord
import requests

__author__: 'Alice Williams'
__version__: '0.0.0'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
api = 'https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,religious,political,racist,sexist,explicit'

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
    elif msg == '$joke':
        joke = requests.get(api)
        if "joke" in joke:
            await message.channel.send(joke["joke"])
        else:
            await message.channel.send('joke error occurred')


token_file = open('token.txt', 'r')
token = token_file.readline()
client.run(token)
