from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from time import sleep
import json

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

def get_crypto_data(query):
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

    # while True:
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        with open('output.log', 'w') as out:
            out.write(json.dumps(data, indent=4))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
        # sleep(10)

    output_dict = {}
    for obj in data['data']:
        if obj['symbol'] == query:
            # output_dict = {}
            # output_dict['name'] = obj['name']
            # output_dict['']
            # output_dict['info'] = obj['quote']
            output = obj
            # print(json.dumps(obj['quote'], indent=4))
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

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user.name} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

# @bot.command(name="crypto")
# async def crypto_view(ctx):
#     await ctx.send("Fetching Cryptocurrency Data...")

@bot.event
async def on_message(message):
    if message.content.startswith("!crypto"):
        query_list = message.content.split(" ")
    
    if len(query_list) == 1:
        await message.channel.send("Please input a cryptocurrency code")
    else:
        crypto_data = get_crypto_data(query_list[1])
        await message.channel.send("**Name:** " + crypto_data['name'])
        await message.channel.send("------------------")
        await message.channel.send("**Current Price**: " + str( '{:,.2f}'.format(crypto_data['quote']['AUD']['price']) ))
        await message.channel.send("**CoinMarketCap Rank**: " + str(crypto_data['cmc_rank']))
        # await message.channel.send(crypto_data['quote'])


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

    