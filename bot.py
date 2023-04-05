#!/usr/bin/env python
"""bot.py: Runs Discord API bot 'Augusta'"""

from time import sleep
import discord
import requests

__author__: 'Alice Williams'
__version__: '0.0.0'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
api = 'https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,religious,political,racist,sexist,explicit'

help_text = 'Current commands:\n$help - shows this message\n$hello - says hello back\n$echo <msg> - echos a msg ' \
            'string\n$joke - prints a programmer joke '


# Logs in bot.
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    
# Bot does something based on command.
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    # Determines what command to execute.
    if msg == '$hello':
        await say_hello(message)
    elif msg.startswith('$echo'):
        await echo(message)
    elif msg.startswith('$help'):
        await say_help(message)
    elif msg == '$joke':
        await say_joke(message)


# Greets a user with "Hello!".
async def say_hello(message):
    await message.channel.send('Hello!')

    print("User greeted.")


# Echoes a message from another user.
async def echo(message):
    await message.channel.send(message.content)

    print("echoed \"{}\"", message.content)


# Prints the help message that lists all commands and how to use them.
async def say_help(message):
    await message.channel.send(help_text)

    print("Printed help information.")


# Tells a joke based on the settings in JokeAPI URL.
async def say_joke(message):
    joke = requests.get(api).json()

    if joke["type"] == "single":
        await message.channel.send(joke["joke"])
    else:
        await message.channel.send(joke["setup"])
        sleep(3)
        await message.channel.send(joke["delivery"])

    print("Told a joke.")


token_file = open('token.txt', 'r')
token = token_file.readline()
token_file.close()
client.run(token)
