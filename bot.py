#!/usr/bin/env python
""" bot.py: Entrypoint script that runs Discord API bot 'Augusta' """

from time import sleep
import pytz
from datetime import datetime
import discord
import requests
import constants
from boto3.dynamodb.conditions import Key
import DBManagement
import boto3 as boto3
from discord.ext import tasks

discord_token = constants.discord_token
joke_api = constants.joke_api
aws_access_key_id = constants.aws_access_key_id
aws_secret_access_key = constants.aws_secret_access_key

tz_utc = pytz.timezone('UTC')
tz_la = pytz.timezone('America/Los_Angeles')

region_name = 'us-west-2'

__author__ = 'CWU CS CLUB'
__version__ = '0.1-alpha'

intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)

help_text = 'Current commands:\n' \
            "$help - shows the help for this bot\n" \
            '$hello - says hello back\n' \
            '$echo <msg> - echos a msg string\n' \
            '$joke - prints a programmer joke\n' \
            '$points - prints your current points balance\n' \
            '$users - lists all users seen\n' \
            '$userNum - prints number of users seen\n' \
            '$version - prints the running bot version\n' \
            '$time - prints the current time'


# Runs function every minute. Adds new users and gives out points.
@tasks.loop(minutes=1)
async def refreshMembers():
    await client.wait_until_ready()

    guilds = client.guilds

    for guild in guilds:
        members = guild.members
        for member in members:
            DBManagement.add_user(user_id=member.id, guild_id=member.guild.id, aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key, region_name=region_name)
            incrementPoints(user_id=member.id, guild_id=member.guild.id)

    print('Refreshed users for all servers.')


# Event called when bot authenticates with Discord gateway.
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    refreshMembers.start()


# Event called on message seen by bot.
@client.event
async def on_message(message):
    # Does not respond to self
    if message.author == client.user:
        return

    msg = message.content

    # Hardcoded command routing
    if msg == '$hello':
        await say_hello(message)
    elif msg.startswith('$echo'):
        await echo(message)
    elif msg == '$help':
        await say_help(message)
    elif msg == '$joke':
        await say_joke(message)
    elif msg == '$users':
        await list_users(message)
    elif msg == '$userNum':
        await member_count(message)
    elif msg == '$points':
        await get_points(message)
    elif msg == '$version':
        await print_version(message)
    elif msg == '$time':
        await time(message)
    elif msg.startswith('$'):
        await cmd_error(message)


# Prints the current time
async def time(message):
    await message.channel.send(f"The local time is {datetime.now(tz_la).strftime('%H:%M:%S')}")


# Command not found error
async def cmd_error(message):
    await message.channel.send('Error command not known')

    print("Printed command error.")


# Prints the current script version
async def print_version(message):
    await message.channel.send(f'Current version: v{__version__}')

    print("Printed version.")


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
    joke = requests.get(joke_api).json()

    if joke["type"] == "single":
        await message.channel.send(joke["joke"])
    else:
        await message.channel.send(joke["setup"])
        sleep(3)
        await message.channel.send(joke["delivery"])

    print("Told a joke.")


# Prints all members or to the limit in the server by their usernames.
async def list_users(message, limit=-1):
    # List of all members in the server.
    members = message.guild.members

    # Shuffles the order of members in the list
    # random.shuffle(members)

    # If there is no limit then print all users.
    if limit <= 0:
        for member in members:
            await message.channel.send(f"{member.display_name}#{member.discriminator}")
    # Print the specified number of members in the server.
    else:
        if limit > len(members):
            limit = len(members)

        for index in range(limit):
            await message.channel.send(f"{members[index].display_name}#{members[index].discriminator}")

    print("Printed a list of server members.")


# Prints number of members in server.
async def member_count(message):
    await message.channel.send('Server member count: {}'.format(message.guild.member_count))

    print('Printed member count.')


# Displays user's points.
async def get_points(message):
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name
                              )

    table = dynamodb.Table('Users')

    response = table.query(
        KeyConditionExpression=Key('user_id').eq(message.author.id) & Key('guild_id').eq(message.guild.id))

    await message.channel.send('You have {} points.'.format(response['Items'][0]['info']['user_points']))

    print('Displayed a user\'s points.')


# Increments a user's points based on the incrementalValue.
def incrementPoints(user_id, guild_id, incrementalValue=1):
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name
                              )

    table = dynamodb.Table('Users')

    response = table.update_item(
        Key={
            'user_id': user_id,
            'guild_id': guild_id
        },

        UpdateExpression='set info.user_points = info.user_points + :N',
        ExpressionAttributeValues={
            ':N': incrementalValue
        },
        ReturnValues='UPDATED_NEW'
    )


client.run(discord_token)
