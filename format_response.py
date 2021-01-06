from discord import Embed
from datetime import datetime
from webscraper import get_about_info

'''
The following functions generate and return formatted strings 
for different chunks of cryptocurrency information
'''

def format_float(number, dp=2):
    if dp == 2:
        return str('{:,.2f}'.format(number))
    elif dp == 0:
        return str('{:,.0f}'.format(number))

def format_date(given_date):
    given_date_split = given_date.split(".")
    dt_object = datetime.strptime(given_date_split[0], "%Y-%m-%dT%H:%M:%S")
    dt_string = dt_object.strftime("%d/%m/%Y | %H:%M:%S")
    return dt_string

def get_individual_crypto_metadata(total_crypto_metadata, symb):
    return total_crypto_metadata['data'][symb]

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

    supply_info = f"""
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

def generate_embed(crypto_data, crypto_metadata, param=None):
    embed_var = Embed(title=f"{crypto_data['name']} ({crypto_data['symbol']})", description=generate_basic_info(crypto_data), color=16736330)
    embed_var.set_footer(text=f"{format_date(crypto_data['last_updated'])} GMT")
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

def generate_about_embed(crypto_name):
    about_info = get_about_info(crypto_name)
    embed_var = Embed(title=f"About {crypto_name}", description=about_info, color=16736330)
    return embed_var
