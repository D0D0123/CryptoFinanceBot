from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from time import sleep
import json

import os
import discord
from discord import Embed
from discord.ext import tasks, commands
from dotenv import load_dotenv

from format_response import generate_basic_info, generate_extra_info, generate_supply_info, generate_crypto_link, generate_all_embed
# from database import bot_data

# Maps every symbol to it's corresponding currency name
crypto_map = {}
bot_data = []

'''
Gets the entirety of cryptocurrency data from CoinMarketCap API
as JSON, converts to a python dictionary and returns this
'''
def get_total_crypto_data():
    # https://coinmarketcap.com/api/documentation/v1/#
    global crypto_map

    #defining parameters for API request
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'10',
    'convert':'AUD'
    }
    headers = {
    'Accepts': 'application/json',
    'Accept-Encoding': 'deflate, gzip',
    'X-CMC_PRO_API_KEY': '971768f9-fc4a-4166-9a71-249e89d36138',
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
    
    print(output)
    return output

'''
updates database.json with new bot_data information
by serialising bot_data as json and rewriting it to the file
'''
def update_database():
    with open('database.json', 'w') as out:
        out.write(json.dumps(bot_data, indent=4))

# Connecting to discord
# bot token is stored in environment variable for security reasons
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# every command must be prefixed with a !
bot = commands.Bot(command_prefix='!')
client = discord.Client()

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

    for server_dict in bot_data:
        channel = bot.get_channel(server_dict['autopost_channel'])
        watch_list = server_dict['watch_list']
        await channel.send("*Here's the hourly update for the following coins:*")
        # create and send an embed for each coin in the watch list
        for symbol in watch_list:
            crypto_data = get_individual_crypto_data(total_data, symbol)
            embed_var = generate_all_embed(crypto_data)
            await channel.send(embed=embed_var)

        # Gets list of price_pings --> users which have chosen to be notified 
        # when a currency goes over a particular price
        price_pings = server_dict['price_pings']
        for ping in price_pings:
            crypto_data = get_individual_crypto_data(total_data, ping['currency'])

            if ping['higher'] == True:
                if crypto_data['quote']['AUD']['price'] > ping['price']:
                    await channel.send(f"<@{ping['user']}>, {ping['currency']} is now greater than ${ping['price']}")

            elif ping['higher'] == False:
                if crypto_data['quote']['AUD']['price'] < ping['price']:
                    await channel.send(f"<@{ping['user']}>, {ping['currency']} is now less than ${ping['price']}")
        


# |--------------------------------------------------------------------------------------|
# |-------------------------------------- COMMANDS --------------------------------------|
# |--------------------------------------------------------------------------------------|

'''
The !crypto [symbol] [param] command,
which calls crypto_send() to send 
information about a particular 
cryptocurrency to the channel
'''
@bot.command(name="crypto")
async def crypto_display(ctx, *args):
    if len(args) == 0:
        await ctx.send("Please input a cryptocurrency code")
    else:
        total_data = get_total_crypto_data()
        crypto_data = get_individual_crypto_data(total_data, args[0])
        if len(args) > 1:
            await crypto_send(ctx, crypto_data, args[1])
        else:
            await crypto_send(ctx, crypto_data)

'''
Sends cryptocurrency information 
to the server, with the depth of information 
depending on the parameter given
(None, -extra, -supply, -link, -all)
'''
async def crypto_send(ctx, crypto_data, param=None):
    embed_var = Embed(title=crypto_data['name'], description=generate_basic_info(crypto_data), color=3447003)
    # embed_var.set_thumbnail(url="https://cdn-images-1.medium.com/max/1024/1*o4pm4QDu0cwR1XEpLdFCSw.jpeg")
    # embed_var.set_image(url="https://static.blockgeeks.com/wp-content/uploads/2019/03/image18.png")

    if param != None:
        if param == "-extra" or param == "-all":
            embed_var.add_field(name="Extra", value=generate_extra_info(crypto_data), inline=False)

        if param == "-supply" or param == "-all":
            embed_var.add_field(name="Supply", value=generate_supply_info(crypto_data), inline=True)
        
        if param == "-link" or param == "-all":
            embed_var.add_field(name="Link", value=generate_crypto_link(crypto_data), inline=True)
    
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
                    embed_var = Embed(title="Currency Watch List", description=watch_list_str)
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
                continue

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
    
    embed_var = Embed(title="Top 10 Cryptocurrencies", 
                      description=crypto_list, 
                      color=3447003)
    await ctx.send(embed=embed_var)

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

    