from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from time import sleep
import json

import os
import discord
from discord import Embed
from discord.ext import tasks, commands
from dotenv import load_dotenv

'''
Gets the entirety of cryptocurrency data from CoinMarketCap API
as JSON, converts to a python dictionary and returns this
'''
def get_total_crypto_data():
    # https://coinmarketcap.com/api/documentation/v1/#

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

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        with open('output.log', 'w') as out:    # logs the entirety of each request in a file
            out.write(json.dumps(data, indent=4))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    return data

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


# Connecting to discord
# bot token is stored in environment variable for security reasons
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# every command must be prefixed with a !
bot = commands.Bot(command_prefix='!')
client = discord.Client()

'''
Defines a 'watch' task which provides hourly updates 
on chosen cryptocurrencies in a chosen channel, set by a user
'''
@tasks.loop(hours=1)
async def crypto_update():
    channel = bot.get_channel(793053168304783440)
    await channel.send("*Here's the hourly update for the following coins:*")
    total_data = get_total_crypto_data()
    watched = ["BTC", "ETH"]
    for symbol in watched:
        crypto_data = get_individual_crypto_data(total_data, symbol)
        embed_var = Embed(title=crypto_data['name'], 
                          description=generate_basic_info(crypto_data), 
                          color=3447003)
        embed_var.add_field(name="Extra", 
                            value=generate_extra_info(crypto_data), 
                            inline=False)
        embed_var.add_field(name="Supply", 
                            value=generate_supply_info(crypto_data), 
                            inline=True)
        embed_var.add_field(name="Link", 
                            value=generate_crypto_link(crypto_data), 
                            inline=True)

        await channel.send(embed=embed_var)


'''
Displays when the bot is connected and 
ready on console output
'''
@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user.name} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )

    # crypto_update.start()

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
'''
The following functions generate and return formatted strings 
for different chunks of cryptocurrency information
'''
def generate_basic_info(crypto_data):
    if crypto_data['platform'] == None:
        platform = "None"
    else:
        platform = crypto_data['platform']['name']
    
    basic_info = ( "**Current Price**: " + str( '{:,.2f}'.format(crypto_data['quote']['AUD']['price']) + "\n" 
    + "**CoinMarketCap Rank**: " + str(crypto_data['cmc_rank'])) + "\n"
    + "**Platform**: " + platform )

    return basic_info


def generate_extra_info(crypto_data):
    volume_24h = str( '{:,.2f}'.format(crypto_data['quote']['AUD']['volume_24h']) )
    change_1h = str( '{:,.2f}'.format(crypto_data['quote']['AUD']['percent_change_1h']) )
    change_24h = str( '{:,.2f}'.format(crypto_data['quote']['AUD']['percent_change_24h']) )
    change_7d = str( '{:,.2f}'.format(crypto_data['quote']['AUD']['percent_change_7d']) )
    
    extra_info = f"""
**Volume Traded Last 24 Hours**: {volume_24h}
**Percent Change Last 1 Hour**: {change_1h}% 
**Percent Change Last 24 Hours**: {change_24h}%
**Percent Change Last 7 Days**: {change_7d}%
""" 
    return extra_info

def generate_supply_info(crypto_data):
    if crypto_data['max_supply'] == None:
        max_supply = None
    else:
        max_supply = str( '{:,.0f}'.format(crypto_data['max_supply']) )
    circulating_supply = str( '{:,.0f}'.format(crypto_data['circulating_supply']) )
    total_supply = str( '{:,.0f}'.format(crypto_data['total_supply']) )

    supply_info = f"""
**Max Supply**: {max_supply}
**Circulating Supply**: {circulating_supply}
**Total Supply**: {total_supply}
"""
    return supply_info

def generate_crypto_link(crypto_data):
    return f"https://coinmarketcap.com/currencies/{crypto_data['name']}"


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

    