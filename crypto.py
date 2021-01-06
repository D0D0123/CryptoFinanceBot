from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from time import sleep
import json
from datetime import datetime

import os
import discord
from discord import Embed
from discord.ext import tasks, commands
from dotenv import load_dotenv

from format_response import (generate_basic_info, generate_extra_info, generate_supply_info, generate_description, generate_crypto_links, 
generate_embed, format_float, format_date, get_individual_crypto_metadata)
# from database import bot_data

# Maps every symbol to it's corresponding currency name
crypto_map = {}
bot_data = []

# bot token is stored in environment variable for security reasons
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CMC_API_KEY = os.getenv('CMC_API_KEY')

# every command must be prefixed with a !
bot = commands.Bot(command_prefix='!')
# Connecting to discord
client = discord.Client()
# GUILD = os.getenv('DISCORD_GUILD')

'''
Gets the entirety of cryptocurrency data from CoinMarketCap API
as JSON, converts to a python dictionary and returns this
'''
def get_total_crypto_data():
    # https://coinmarketcap.com/api/documentation/v1/#
    global crypto_map

    #defining parameters for first API request - listings/latest
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'20',
    'convert':'AUD'
    }
    headers = {
    'Accepts': 'application/json',
    'Accept-Encoding': 'deflate, gzip',
    'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    # receiving data
    try:
        response = session.get(url, params=parameters)
        total_data = json.loads(response.text)
        with open('output.log', 'w') as out:    # logs the entirety of each request in a file
            out.write(json.dumps(total_data, indent=4))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    # filling in crypto_map
    for obj in total_data['data']:
        crypto_map[obj["symbol"]] = obj["name"]
    print(crypto_map)
    # get_total_crypto_metadata()
    return total_data

'''
Parses the total data returned from the API request 
for the data of an individual coin
'''
def get_individual_crypto_data(total_data, query):
    for obj in total_data['data']:
        if obj['symbol'] == query:
            output = obj
            break
    else:
        print("Requested cryptocurrency not found")
    
    # print(output)
    return output

def get_total_crypto_metadata():
    #defining parameters for metadata request
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'

    param_symbols = []
    for symb in crypto_map:
        param_symbols.append(symb)
    symbols_string = ','.join(param_symbols)

    parameters = {
    'symbol': symbols_string,
    }
    headers = {
    'Accepts': 'application/json',
    'Accept-Encoding': 'deflate, gzip',
    'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    # receiving data
    try:
        response = session.get(url, params=parameters)
        total_metadata = json.loads(response.text)
        with open('metadata.log', 'w') as out:    # logs the entirety of each request in a file
            out.write(json.dumps(total_metadata, indent=4))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    return total_metadata

'''
updates database.json with new bot_data information
by serialising bot_data as json and rewriting it to the file
'''
def update_database():
    with open('database.json', 'w') as out:
        out.write(json.dumps(bot_data, indent=4))

'''
Displays when the bot is connected and 
ready on console output
'''
@bot.event
async def on_ready():
    # loads (deserialises) existing database.json file into bot_data
    global bot_data
    with open('database.json', 'r') as data_file:
        bot_data = json.load(data_file)

    print(f'{bot.user.name} is connected to the following guilds:')
    for guild in bot.guilds:
        for server_dict in bot_data:
            if guild.id == server_dict['guild']:
                break
        else:
            bot_data.append({
                'guild': guild.id, # one dictionary for each guild that the bot is in
                'autopost_channel': guild.text_channels[0].id, # which channel should autoposts go in
                'watch_list': [], # which currencies to watch
                'price_pings': [] #pings for particular price drops
            })

        print(f'{guild.name} (id: {guild.id})')
    
    update_database()
    crypto_update.start()

# |-----------------------------------------------------------------------------------|
# |-------------------------------------- TASKS --------------------------------------|
# |-----------------------------------------------------------------------------------|

'''
Defines an 'update' task which provides hourly updates 
on chosen cryptocurrencies in a chosen channel, set by a user
'''
@tasks.loop(hours=1)
async def crypto_update():
    total_data = get_total_crypto_data()
    total_metadata = get_total_crypto_metadata()

    for server_dict in bot_data:
        channel = bot.get_channel(server_dict['autopost_channel'])
        watch_list = server_dict['watch_list']
        await channel.send("*Here's the hourly update for the following coins:*")
        # create and send an embed for each coin in the watch list
        for symbol in watch_list:
            crypto_data = get_individual_crypto_data(total_data, symbol)
            crypto_metadata = get_individual_crypto_metadata(total_metadata, symbol)
            embed_var = generate_embed(crypto_data, crypto_metadata, "-extra")
            await channel.send(embed=embed_var)

        # Gets list of price_pings --> users which have chosen to be notified 
        # when a currency goes over a particular price
        price_pings = server_dict['price_pings']
        for ping in price_pings:
            crypto_data = get_individual_crypto_data(total_data, ping['currency'])

            if ping['higher'] == True:
                if crypto_data['quote']['AUD']['price'] > ping['price']:
                    await channel.send(f"<@{ping['user']}>, {ping['currency']} is now greater than ${format_float(ping['price'])}")

            elif ping['higher'] == False:
                if crypto_data['quote']['AUD']['price'] < ping['price']:
                    await channel.send(f"<@{ping['user']}>, {ping['currency']} is now less than ${format_float(ping['price'])}")
        


# |--------------------------------------------------------------------------------------|
# |-------------------------------------- COMMANDS --------------------------------------|
# |--------------------------------------------------------------------------------------|

'''
The !crypto [symbol] [param] command,
which sends cryptocurrency information 
to the server, with the depth of information 
depending on the parameter given
(None, -extra, -supply, -link, -all)
'''
@bot.command(name="crypto")
async def crypto_display(ctx, *args):
    if len(args) == 0:
        await ctx.send("Please input a cryptocurrency code")
    else:
        total_data = get_total_crypto_data()
        total_metadata = get_total_crypto_metadata()
        crypto_data = get_individual_crypto_data(total_data, args[0])
        crypto_metadata = get_individual_crypto_metadata(total_metadata, args[0])
        if len(args) > 1:
            # await crypto_send(ctx, crypto_data, args[1])
            embed_var = generate_embed(crypto_data, crypto_metadata, args[1])
            await ctx.send(embed=embed_var)
        else:
            # await crypto_send(ctx, crypto_data)
            embed_var = generate_embed(crypto_data, crypto_metadata)
            await ctx.send(embed=embed_var)

@bot.command(name="watch")
async def crypto_watch(ctx, *args):
    global crypto_map
    global bot_data
    for symb in args:
        if symb not in crypto_map and args[0] != "-show":
            continue
        for server_dict in bot_data:
            # add the symbol to the watch list of a specific guild (or remove it)
            if server_dict['guild'] == ctx.message.guild.id:

                if args[0] == "-show":
                    watch_list_str = ''
                    for symb in server_dict['watch_list']:
                        watch_list_str = watch_list_str + "\n" + f"**{symb}** " + f"({crypto_map[symb]})"
                    embed_var = Embed(title="Currency Watch List", description=watch_list_str, color=16736330)
                    await ctx.send(embed=embed_var)

                elif args[0] == "-add":
                    if symb not in server_dict['watch_list']:
                        server_dict['watch_list'].append(symb)
                    await ctx.send(f"{symb} is now being watched hourly")

                elif args[0] == "-remove":
                    server_dict['watch_list'].remove(symb)
                    await ctx.send(f"{symb} has been removed from the watchlist")
    
    update_database()


'''
!ping [currency] [>] [price]
'''
@bot.command(name="ping")
async def crypto_ping(ctx, *args):
    global bot_data
    
    for server_dict in bot_data:
        # get the guild that this command was sent from, locate it's dict in bot_data 
        # (maybe turn this into a function)
        if server_dict['guild'] == ctx.message.guild.id:
            if args[0] == "-cancel":
                for item in server_dict['price_pings']:
                    if item['user'] == ctx.message.author.id:
                        server_dict['price_pings'].remove(item)
                update_database()
                break
            
            if args[0] == "-show":
                ping_list = ''
                for ping in server_dict['price_pings']:
                    if ping['user'] == ctx.message.author.id:
                        if ping['higher'] == True:
                            equality = '>'
                        elif ping['higher'] == False:
                            equality = '<'
                        ping_list = ping_list + "\n" + f"**{crypto_map[ping['currency']]}** {equality} ${format_float(ping['price'])}"
                
                embed_var = Embed(title="Your watched currencies", description=ping_list, color=16736330)
                await ctx.send(embed=embed_var)
                break

            symb = args[0]
            compare_bool = args[1]
            price = args[2]
            if symb not in crypto_map:
                return
            
            if compare_bool == '>':
                compare_bool = True 
            elif compare_bool == '<':
                compare_bool = False 
            # generate a dict, append this to 'price_pings'
            ping = {
                'user': ctx.message.author.id, # the user who wants to be notified
                'currency': symb, # the cryptocurrency symbol
                'price': float(price), # the value of the price
                'higher': compare_bool, # notify if the currency price is higher/lower than the chosen price
            }
            server_dict['price_pings'].append(ping)

    update_database()


@bot.command(name="list")
async def send_crypto_list(ctx):
    crypto_list = ""
    for i, key in enumerate(crypto_map):
        crypto_list = crypto_list + f"{i + 1}: " + f"**{key}** ({crypto_map[key]})" + "\n\n"
    
    embed_var = Embed(title="Top 20 Cryptocurrencies", 
                      description=crypto_list, 
                      color=16736330)
    await ctx.send(embed=embed_var)

@bot.command(name="post")
async def change_autopost_channel(ctx, arg):
    global bot_data
    # navigate to the guild the message was sent from,
    # change it's autopost channel
    for server_dict in bot_data:
        if server_dict['guild'] == ctx.message.guild.id:
            for channel in ctx.message.guild.text_channels:
                if arg == str(channel.id):
                    await ctx.send(f"Automated posts will now go in **{bot.get_channel(channel.id).name}**")
                    server_dict['autopost_channel'] = channel.id
                    break
            # if given channel id does not match any existing channel id
            else:
                await ctx.send(ctx.message.guild.text_channels)
                await ctx.send("Not a valid channel ID")
    
    update_database()

@bot.command(name="raw")
async def send_raw_data(ctx):
    await ctx.send(file=discord.File('output.log'))

@bot.command(name="debug")
async def crypto_debug(ctx):
    await ctx.send(bot_data)

# Error Handling
@bot.event
async def on_error(event, *args, **kwargs):
    # output error to err.log file
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise Exception

bot.run(TOKEN)

    