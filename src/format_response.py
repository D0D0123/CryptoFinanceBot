'''
The following functions generate and return formatted strings 
for different chunks of cryptocurrency information.
'''

from discord import Embed
from datetime import datetime
from news import get_about_info, get_news

'''
Formats floating point numbers to have commas, 
to either 2 decimal places or none
'''
def format_float(number, dp=2):
    if dp == 2:
        return str('{:,.2f}'.format(number))
    elif dp == 0:
        return str('{:,.0f}'.format(number))

'''
Formats the date recieved from an API request
(given in the form yyyy-mm-ddThh:mm:ss.???Z)
'''
def format_date(given_date):
    given_date_split = given_date.split(".")
    dt_object = datetime.strptime(given_date_split[0], "%Y-%m-%dT%H:%M:%S")
    dt_string = dt_object.strftime("%d/%m/%Y | %H:%M:%S")
    return dt_string

def generate_basic_info(crypto_data):
    if crypto_data['platform'] == None:
        platform = "None"
    else:
        platform = crypto_data['platform']['name']
    
    basic_info = ( "**Current Price**: " + f"${format_float(crypto_data['quote']['AUD']['price'])}" + "\n" 
    + "**CoinMarketCap Rank**: " + str(crypto_data['cmc_rank']) + "\n"
    + "**Platform**: " + platform )

    return basic_info

def generate_extra_info(crypto_data):
    volume_24h = format_float(crypto_data['quote']['AUD']['volume_24h'])
    change_1h = format_float(crypto_data['quote']['AUD']['percent_change_1h']) 
    change_24h = format_float(crypto_data['quote']['AUD']['percent_change_24h']) 
    change_7d = format_float(crypto_data['quote']['AUD']['percent_change_7d'])
    
    extra_info = f"""
**Volume Traded Last 24 Hours**: ${volume_24h}
**Percent Change Last 1 Hour**: {change_1h}% 
**Percent Change Last 24 Hours**: {change_24h}%
**Percent Change Last 7 Days**: {change_7d}%
""" 
    return extra_info

def generate_supply_info(crypto_data):
    if crypto_data['max_supply'] == None:
        max_supply = None
    else:
        max_supply = format_float(crypto_data['max_supply'], 0)
    circulating_supply = format_float(crypto_data['circulating_supply'], 0)
    total_supply = format_float(crypto_data['total_supply'], 0)
    market_cap = format_float(crypto_data['quote']['AUD']['market_cap'], 0)

    supply_info = f"""
**Market Cap**: ${market_cap}
**Max Supply**: {max_supply}
**Circulating Supply**: {circulating_supply}
**Total Supply**: {total_supply}
"""
    return supply_info

def generate_description(crypto_metadata):
    return crypto_metadata['description']

def generate_crypto_links(crypto_metadata):
    links_data = crypto_metadata['urls']
    website, twitter, reddit, tech_doc, src_code = None, None, None, None, None
    # if any of these strings don't exist, default them to None
    if links_data['website']:
        website = links_data['website'][0]
    if links_data['twitter']:
        twitter = links_data['twitter'][0]
    if links_data['reddit']:
        reddit = links_data['reddit'][0]
    if links_data['technical_doc']:
        tech_doc = links_data['technical_doc'][0]
    if links_data['source_code']:
        src_code = links_data['source_code'][0]
    
    links_string = f"""
 » **Website:** {website}
 » **Twitter:** {twitter}
 » **Reddit:** {reddit}
 » **Technical Document:** {tech_doc}
 » **Source Code:** {src_code}
 » **CMC:** https://coinmarketcap.com/currencies/{crypto_metadata['name'].replace(" ", "-")}
"""
    return links_string

'''
Generates and returns the embed containing the overall economic information for a particular cryptocurrency.
It takes in one of a few parameters (None, -extra, -supply, -links, -all) and adds certain fields accordingly.
'''
def generate_embed(crypto_data, crypto_metadata, param=None):
    embed_var = Embed(title=f"{crypto_data['name']} ({crypto_data['symbol']})", description=generate_basic_info(crypto_data), color=16736330)
    embed_var.set_footer(text=f"{format_date(crypto_data['last_updated'])} GMT • From CoinMarketCap")
    embed_var.set_thumbnail(url=crypto_metadata['logo'])
    # embed_var.set_image(url="https://static.blockgeeks.com/wp-content/uploads/2019/03/image18.png")

    if param != None:
        if param == "-extra" or param == "-all":
            embed_var.add_field(name="Extra", value=generate_extra_info(crypto_data), inline=False)

        if param == "-supply" or param == "-all":
            embed_var.add_field(name="Supply", value=generate_supply_info(crypto_data), inline=False)
        
        if param == "-links" or param == "-all":
            embed_var.add_field(name="Links", value=generate_crypto_links(crypto_metadata), inline=False)

    return embed_var

'''
Generates and returns the embed containing descriptive information about 
a particular cryptocurrency, as well as links
'''
def generate_about_embed(crypto_name, crypto_metadata):
    about_info = get_about_info(crypto_name)
    embed_var = Embed(title=f"About {crypto_name}", description=about_info['articleBody'], color=16736330)
    embed_var.add_field(name='Read More:', value=about_info['url'], inline=False)
    embed_var.add_field(name='Links', value=generate_crypto_links(crypto_metadata), inline=False)
    embed_var.set_footer(text="From Google Knowledge Graph")

    return embed_var

'''
Generates and returns the embed containing news for a particular topic
'''
def generate_news_embed(query_string):
    total_news_data = get_news(query_string)
    embed_var = Embed(title=f"{query_string} News", color=16736330)
    for i, news in enumerate(total_news_data[:-1]):
        # only include the first sentence of the article for brevity
        description = news['description'].split(".")[0]
        provider_date = f"*{news['provider']['name']} | {format_date(news['datePublished'])}*"
        embed_var.add_field(name=f"{i + 1}. **{news['title']}**",  
                            value=f"[{description}]({news['url']})" + '\n' + '\n' + provider_date + '\n' + '\n',
                            inline=True)
    embed_var.set_footer(text="From ContextualWeb News")

    return embed_var

def generate_help_embed(command_name=None):
    embed = Embed(title="Help", color=16736330)
    if command_name == None:
        command_list = """
!help
!about
!crypto
!list
!news
!newsfeed
!ping
!post
!raw
!watch
"""
        embed.add_field(name="Command List", value=f"{command_list} \n Use !help [command name] to get info about a specific command.")
    
    if command_name == "about":
        about_string = """
    » e.g. !about BTC

Displays information about a specified cryptocurrency,
as well as a link to read more, and other relevant links
"""
        embed.add_field(name="!about [symbol]", value=about_string)
    
    if command_name == "crypto":
        crypto_string = """
    » e.g. !crypto BTC -supply

Sends cryptocurrency information to the server, 
with the depth of information depending on the parameter given
(None, -extra, -supply, -links, -all)
    » With no parameter, only price, rank, platform will be shown
    » Use '-extra' to show daily volume traded, and percentage changes
    » Use '-supply' to show market cap and supply info
    » Use '-links' to show relevant links
    » Use '-all' to show all the above information
"""
        embed.add_field(name="!crypto [symbol] [param]", value=crypto_string)
    
    if command_name == "list":
        list_string = """
Provides a list of the top 20 cryptocurrencies
(ranked by market cap), in the format 'rank. symbol (name)'
"""
        embed.add_field(name="!list", value=list_string)
    
    if command_name == "news":
        news_string = """
    » e.g. !news BTC
    » e.g. !news Coronavirus -general   

Provides the top 9 trending news articles surrounding 
either a specified cryptocurrency, or a general phrase
    » Use '-general' at the end of any word/phrase that isn't a cryptocurrency symbol
"""
        embed.add_field(name="!news [symbol] OR !news [phrase] -general", value=news_string)
    
    if command_name == "newsfeed":
        newsfeed_string = """
» e.g. !newsfeed Australia -general

Sets the tridaily news feed to something other than the default 
'Cryptocurrency'
"""
        embed.add_field(name="!newsfeed [symbol/phrase] [-general]", value=newsfeed_string)
    
    if command_name == "ping":
        ping_string = """
    » e.g. !ping BTC < 10000

Add/Remove cryptocurrencies to/from a ping list, 
as well as specifying a price and a higher/lower comparison parameter.
The bot will notify you if the price of a chosen cryptocurrency
exceeds/falls below your chosen price.
    » Use '>' if you want to be notified if the currency exceeds a price
    » Use '<' if you want to be notified if the currency falls below a price
"""
        embed.add_field(name="!ping [currency] [> OR <] [price]", value=ping_string)

    if command_name == "post":
        post_string = """
Change which channel the bot will send it's automatic posts to
"""
        embed.add_field(name="!post [channel name]", value=post_string)
    
    if command_name == "raw":
        raw_string = """
Sends the raw market data and metadata for the last !crypto call
"""
        embed.add_field(name="!raw", value=raw_string)
    
    if command_name == "watch":
        watch_string = """
    » e.g. !watch -add BTC ETH

Add/Remove cryptocurrencies to/from a watch list.
The bot will provide hourly updates on the currencies in this watch list.
    » Use '-add' [symbols...] to add symbols to the watch list
    » Use '-remove' [symbols...] to remove symbols from the watch list
    » Use '-show' to show the watch list
"""
        embed.add_field(name="!watch [param] [symbol] [symbol] ...", value=watch_string)
    
    return embed