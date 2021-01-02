
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

