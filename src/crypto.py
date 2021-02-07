'''
This is the main file for the Cryptocurrency Bot application. 
Run python crypto.py (from within src) to start up the bot.
'''

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

import pymongo
from pymongo import MongoClient

from format_response import (generate_basic_info, generate_extra_info, generate_supply_info, generate_description, generate_crypto_links, 
generate_embed, format_float, format_date, generate_about_embed, generate_news_embed, generate_help_embed)
from crypto_api import (get_total_crypto_data, get_individual_crypto_data, get_total_crypto_metadata, 
get_individual_crypto_metadata, crypto_map)

# # A global list that stores the deserialised JSON data from database.json 
# bot_data = []

# Every command must be prefixed with a !
bot = commands.Bot(command_prefix='!')
bot.remove_command("help")
# Connecting to discord
client = discord.Client()

# bot token is stored in environment variable for security reasons
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

cluster = MongoClient(MONGODB_URI)
db = cluster["CryptoBot"]
collection = db["GuildData"]

'''
Displays when the bot is connected and 
ready on console output, and adds any new servers joined 
to the database
'''
@bot.event
async def on_ready():
    # load data from mongoDB database
    bot_data = collection.find({})
    server_count = collection.count_documents({})

    print(f'{bot.user.name} is connected to the following {server_count} guilds:')
    # for each guild the bot is connected to, 
    for guild in bot.guilds:
        # if that guild_id is not already in the database, add it
        for server_dict in bot_data:
            if guild.id == server_dict['_id']:
                break 
        else:
            collection.insert_one({
                '_id': guild.id, # id number of the guild
                'autopost_channel': guild.text_channels[0].id, # which channel should autoposts go in
                'newsfeed': 'Cryptocurrency',
                'watch_list': [], # which currencies to watch
                'price_pings': [] #pings for particular price drops
            })

        # print each connected guild on console output
        print(f'{guild.name} (id: {guild.id})')
    
    # remove any guilds that the bot isn't connected to anymore
    to_remove = []
    for server_dict in bot_data:
        if bot.get_guild(server_dict['_id']) == None:
            to_remove.append(server_dict['_id'])
    
    for guild_id in to_remove:
        collection.delete_one({'_id': guild_id})
    
    # Start the automatic internal tasks
    crypto_update.start()
    # crypto_news_update.start()

# |-----------------------------------------------------------------------------------|
# |-------------------------------------- TASKS --------------------------------------|
# |-----------------------------------------------------------------------------------|

'''
An update task which provides hourly updates of market data
on chosen cryptocurrencies in a chosen channel. 
It also pings users if certain coins exceed/fall below a chosen price.
'''
@tasks.loop(hours=1)
async def crypto_update():
    total_data = get_total_crypto_data()
    total_metadata = get_total_crypto_metadata()
    bot_data = collection.find({})

    for server_dict in bot_data:
        # for every server, retrieve it's autopost channel and watch list
        channel = bot.get_channel(server_dict['autopost_channel'])
        watch_list = server_dict['watch_list']
        if len(watch_list) > 0:
            await channel.send("*Here's the hourly update for the following coins:*")
        # create and send an embed for each coin in the watch list
        for symbol in watch_list:
            crypto_data = get_individual_crypto_data(total_data, symbol)
            crypto_metadata = get_individual_crypto_metadata(total_metadata, symbol)
            embed_var = generate_embed(crypto_data, crypto_metadata, "-extra")
            await channel.send(embed=embed_var)

        # Gets list of price_pings --> users which have chosen to be notified 
        # when a currency goes over/under a particular price
        price_pings = server_dict['price_pings']
        for ping in price_pings:
            crypto_data = get_individual_crypto_data(total_data, ping['currency'])

            if ping['higher'] == True:
                if crypto_data['quote']['AUD']['price'] > ping['price']:
                    await channel.send(f"<@{ping['user']}>, {ping['currency']} is now greater than ${format_float(ping['price'])}")

            elif ping['higher'] == False:
                if crypto_data['quote']['AUD']['price'] < ping['price']:
                    await channel.send(f"<@{ping['user']}>, {ping['currency']} is now less than ${format_float(ping['price'])}")
        
'''
A news update task which provides automatic updates on the top
trending cryptocurrency news every 8 hours.
'''
@tasks.loop(hours=8)
async def crypto_news_update():
    bot_data = collection.find({})
    for server_dict in bot_data:
        channel = bot.get_channel(server_dict['autopost_channel'])
        await channel.send(embed=generate_news_embed(server_dict['newsfeed']))

# |--------------------------------------------------------------------------------------|
# |-------------------------------------- COMMANDS --------------------------------------|
# |--------------------------------------------------------------------------------------|
'''
Provides information about each command
'''
@bot.command(name="help")
async def help(ctx, *args):
    if len(args) == 0:
        command_name = None
    else:
        command_name = args[0]
    await ctx.send(embed=generate_help_embed(command_name))


'''
!crypto [symbol] [param]
    » e.g. !crypto BTC -supply

Sends cryptocurrency information to the server, 
with the depth of information depending on the parameter given
(None, -extra, -supply, -links, -all)
    » With no parameter, only price, rank, platform will be shown
    » Use '-extra' to show daily volume traded, and percentage changes
    » Use '-supply' to show market cap and supply info
    » Use '-links' to show relevant links
    » Use '-all' to show all the above information
'''
@bot.command(name="crypto")
async def crypto_display(ctx, *args):
    global crypto_map
    if len(args) == 0:
        await ctx.send("Please input a cryptocurrency code")
        return
    
    symbol = args[0]
    if symbol not in crypto_map:
        await ctx.send("Please input a valid cryptocurrency code")
        return
    
    total_data = get_total_crypto_data()
    total_metadata = get_total_crypto_metadata()
    crypto_data = get_individual_crypto_data(total_data, symbol)
    crypto_metadata = get_individual_crypto_metadata(total_metadata, symbol)

    # if a parameter is given
    if len(args) > 1:
        param = args[1]
        embed_var = generate_embed(crypto_data, crypto_metadata, param)
        await ctx.send(embed=embed_var)
    else:
        embed_var = generate_embed(crypto_data, crypto_metadata)
        await ctx.send(embed=embed_var)

'''
!watch [param] [symbol] [symbol] ...
    » e.g. !watch -add BTC ETH

Add/Remove cryptocurrencies to/from a watch list.
The bot will provide hourly updates on the currencies in this watch list.
    » Use '-add' [symbols...] to add symbols to the watch list
    » Use '-remove' [symbols...] to remove symbols from the watch list
    » Use '-show' to show the watch list
'''
@bot.command(name="watch")
async def crypto_watch(ctx, *args):
    global crypto_map

    for symbol in args:
        # skip over symbols that aren't in the crypto_map
        if symbol not in crypto_map and args[0] != "-show":
            continue
        
        server_dict = collection.find_one({'_id': ctx.message.guild.id})

        if args[0] == "-show":
            watch_list_str = ''
            for symbol in server_dict['watch_list']:
                watch_list_str = watch_list_str + "\n" + f"**{symbol}** " + f"({crypto_map[symbol]})"
            embed_var = Embed(title="Cryptocurrency Watch List", description=watch_list_str, color=16736330)
            await ctx.send(embed=embed_var)

        elif args[0] == "-add":
            if symbol not in server_dict['watch_list']:
                collection.update_one(
                    {'_id': ctx.message.guild.id}, 
                    {"$addToSet": {'watch_list': symbol}}
                )
            await ctx.send(f"{symbol} is now being watched hourly")

        elif args[0] == "-remove":
            collection.update_one(
                {'_id': ctx.message.guild.id}, 
                {"$pull": {'watch_list': symbol}}
            )
            await ctx.send(f"{symbol} has been removed from the watchlist")


'''
!ping [currency] [> OR <] [price]
    » e.g. !ping BTC < 10000

Add/Remove cryptocurrencies to/from a ping list, 
as well as specifying a price and a higher/lower comparison parameter.
The bot will notify you if the price of a chosen cryptocurrency
exceeds/falls below your chosen price.
    » Use '>' if you want to be notified if the currency exceeds a price
    » Use '<' if you want to be notified if the currency falls below a price
'''
@bot.command(name="ping")
async def crypto_ping(ctx, *args):
    
    server_dict = collection.find_one({'_id': ctx.message.guild.id})

    if args[0] == "-cancel":
        # $pull removes all instances of an element from a mongoDB array
        collection.update_one(
            {'_id': ctx.message.guild.id}, 
            {"$pull": {'price_pings': {'user': ctx.message.author.id} }}
        )
        return
    
    if args[0] == "-show":
        ping_list = ''
        # generate a formatted list of pings to display
        for ping in server_dict['price_pings']:
            if ping['user'] == ctx.message.author.id:
                if ping['higher'] == True:
                    equality = '>'
                elif ping['higher'] == False:
                    equality = '<'
                ping_list = ping_list + "\n" + f"**{crypto_map[ping['currency']]}** {equality} ${format_float(ping['price'])}"
        
        embed_var = Embed(title="Your watched cryptocurrencies", description=ping_list, color=16736330)
        await ctx.send(embed=embed_var)
        return
        
    symbol = args[0]
    compare_bool = args[1]
    price = args[2]
    if symbol not in crypto_map:
        return
    
    if compare_bool == '>':
        compare_bool = True 
    elif compare_bool == '<':
        compare_bool = False 
    # generate a dict, append this to 'price_pings'
    ping = {
        'user': ctx.message.author.id, # the user who wants to be notified
        'currency': symbol, # the cryptocurrency symbol
        'price': float(price), # the value of the price
        'higher': compare_bool, # notify if the currency price is higher/lower than the chosen price
    }

    collection.update_one(
        {'_id': ctx.message.guild.id},
        {"$addToSet": {'price_pings': ping}}
    )
    
    await ctx.send("Notification list updated successfully")


'''
!about [symbol]
    » e.g. !about BTC

Displays information about a specified cryptocurrency,
as well as a link to read more, and other relevant links
'''
@bot.command(name="about")
async def send_about_info(ctx, arg):
    global crypto_map
    symbol = arg
    if symbol not in crypto_map:
        await ctx.send("Please input a valid cryptocurrency code")
        return
    
    total_metadata = get_total_crypto_metadata()
    crypto_metadata = get_individual_crypto_metadata(total_metadata, symbol)
    await ctx.send(embed=generate_about_embed(crypto_map[symbol], crypto_metadata))
    
'''
!news [symbol]
OR
!news [phrase] -general
    » e.g. !news BTC
    » e.g. !news Coronavirus -general   

Provides the top 9 trending news articles surrounding 
either a specified cryptocurrency, or a general phrase
    » Use '-general' at the end of any word/phrase that isn't a cryptocurrency symbol
'''      
@bot.command(name="news")
async def send_news_info(ctx, *args):
    global crypto_map
    if len(args) == 1:
        await ctx.send(embed=generate_news_embed(crypto_map[args[0]]))
    elif len(args) == 0:
        await ctx.send("Please input a query")
    
    if args[-1] == "-general":
        query_string = " ".join(args[:-1])
        await ctx.send(embed=generate_news_embed(query_string))


'''
!newsfeed [symbol/phrase] [-general]
» e.g. !newsfeed Australia -general

Sets the tridaily news feed to something other than the default 
'Cryptocurrency'
'''
@bot.command(name="newsfeed")
async def set_newsfeed(ctx, *args):
    global crypto_map
    if len(args) == 1:
        query_string = crypto_map[args[0]]
    else:
        query_string = " ".join(args[:-1])

    collection.update_one(
        {'_id': ctx.message.guild.id},
        {"$set" : {'newsfeed': query_string}}
    )

    await ctx.send(f"Newsfeed updated to provide automatic news about **{query_string}**")

'''
!list

Provides a list of the top 20 cryptocurrencies
(ranked by market cap), in the format 'rank. symbol (name)'
'''
@bot.command(name="list")
async def send_crypto_list(ctx):
    global crypto_map
    crypto_list = ""
    for i, key in enumerate(crypto_map):
        crypto_list = crypto_list + f"{i + 1}: " + f"**{key}** ({crypto_map[key]})" + "\n\n"
    
    embed_var = Embed(title="Top 20 Cryptocurrencies", 
                      description=crypto_list, 
                      color=16736330)
    embed_var.set_footer(text="From CoinMarketCap")
    await ctx.send(embed=embed_var)

'''
!post [channel name]

Change which channel the bot will send it's automatic posts to
'''
@bot.command(name="post")
async def change_autopost_channel(ctx, arg):
    # verify that given channel id matches an existing channel id in that guild
    for channel in ctx.message.guild.text_channels:
        if arg == channel.name:
            await ctx.send(f"Automated posts will now go in **#{channel.name}**")
            collection.update_one(
                {'_id': ctx.message.guild.id}, 
                { "$set" : {'autopost_channel' : channel.id}}
            )
            break
    else:
        # await ctx.send(ctx.message.guild.text_channels)
        await ctx.send("Not a valid channel name")


'''
!raw
Sends the raw market data and metadata for the last !crypto call
'''
@bot.command(name="raw")
async def send_raw_data(ctx):
    await ctx.send(file=discord.File('../logs/market.log'))
    await ctx.send(file=discord.File('../logs/metadata.log'))

@bot.command(name="debug")
async def crypto_debug(ctx):
    await ctx.send(collection.find({}))

# Error Handling
@bot.event
async def on_error(event, *args, **kwargs):
    print("should have used rust")
    # output error to err.log file
    with open('../logs/err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise Exception

bot.run(TOKEN)

    