#!/usr/bin/env python
""" bot.py: Entrypoint script that runs Discord API bot 'Augusta' """

import random
from time import sleep
import pytz
from datetime import datetime
import discord
import requests
import constants
from boto3.dynamodb.conditions import Key
import DBManagement
import boto3 as boto3
from discord.ext import tasks, commands
import randfacts

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

bot = commands.Bot(command_prefix='$', intents=intents)


# Adds new members to the database.
@bot.event
async def on_member_join(member):
    DBManagement.add_user(user_id=member.id, guild_id=member.guild.id, aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    print('Added new member to the database.')


# Runs function every minute. Gives out points.
@tasks.loop(minutes=1)
async def give_points():
    await bot.wait_until_ready()

    guilds = bot.guilds

    for guild in guilds:
        for member in guild.members:
            incrementPoints(user_id=member.id, guild_id=member.guild.id)

    print('Gave points to all users for all servers.')


# Event called when bot authenticates with Discord gateway.
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    give_points.start()


# Prints the current time
@bot.command()
async def time(message):
    await message.channel.send(f"The local time is {datetime.now(tz_la).strftime('%H:%M:%S')}")


# Prints the current script version
@bot.command()
async def print_version(message):
    await message.channel.send(f'Current version: v{__version__}')

    print("Printed version.")


# Greets a user with "Hello!".
@bot.command(name='hello')
async def say_hello(message):
    await message.channel.send('Hello!')

    print("User greeted.")


# Echoes a message from another user.
@bot.command()
async def echo(message, *args):
    arg = ' '.join(args)
    await message.channel.send(arg)

    print("echoed \"{}\"", arg)


# Tells a joke based on the settings in JokeAPI URL.
@bot.command(name='joke')
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
@bot.command()
async def list_users(message, limit=-1):
    # List of all members in the server.
    members = message.guild.members

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
@bot.command()
async def member_count(message):
    await message.channel.send('Server member count: {}'.format(message.guild.member_count))

    print('Printed member count.')


# Displays user's points.
@bot.command(name='points')
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

    table.update_item(
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


# Gambles a user's points. 50/50 odds with a double return of bet on win.
@bot.command()
async def gamble(message, *arg):
    if len(arg) != 1:
        await message.channel.send('Invalid parameters. There needs to be an amount.')
        print("Attempted gambling.")
        return
    elif not arg[0].isdigit() or int(arg[0]) <= 0:
        await message.channel.send('Invalid parameters. Amount must be a positive integer.')
        print("Attempted gambling.")
        return

    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name
                              )

    table = dynamodb.Table('Users')

    response = table.query(
        KeyConditionExpression=Key('user_id').eq(message.author.id) & Key('guild_id').eq(message.guild.id))

    funds = int(response['Items'][0]['info']['user_points'])

    if funds < int(arg[0]):
        await message.channel.send('You do not have {} points.'.format(arg[0]))
        print("Attempted gambling.")
        return

    if random.randint(1, 2) == 1:
        await message.channel.send('Congratulations! You won {} points and now have {} points.'.format(arg[0],
                                                                                                       int(arg[
                                                                                                               0]) + funds))
        incrementPoints(message.author.id, message.guild.id, incrementalValue=int(arg[0]))
    else:
        await message.channel.send(
            'You lost {} points and now have {} points.'.format(arg[1], funds - int(arg[0])))
        incrementPoints(message.author.id, message.guild.id, incrementalValue=(-1 * int(arg[0])))

    print('Successfully gambled.')


# Tells a fact.
@bot.command(name='fact')
async def get_fact(message):
    try:
        await message.channel.send(randfacts.get_fact())
        print('Told a fact.')
    except Exception as e:
        print("Something went really bad in get_fact().")

bot.run(discord_token)
