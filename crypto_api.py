'''
The following functions call the CoinMarketCap API
for market data and metadata on cryptocurrencies.
'''

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os
from dotenv import load_dotenv

# API Key is stored in environment variable for security reasons
load_dotenv()
CMC_API_KEY = os.getenv('CMC_API_KEY')

# Maps every symbol to it's corresponding currency name
crypto_map = {}

'''
Gets the entirety of cryptocurrency data from CoinMarketCap API
as JSON, deserialises JSON to python dictionaries and returns this
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
        with open('logs/market.log', 'w') as out:    # logs the entirety of each request in a file
            out.write(json.dumps(total_data, indent=4))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    # filling in crypto_map
    for obj in total_data['data']:
        crypto_map[obj["symbol"]] = obj["name"]
    # print(crypto_map)
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

'''
Gets the entirety of cryptocurrency metadata from CoinMarketCap API
as JSON, deserialises JSON to python dictionaries and returns this
'''
def get_total_crypto_metadata():
    #defining parameters for metadata request
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'

    # makes a list of symbols from the ones in crypto_map
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
        with open('logs/metadata.log', 'w') as out:    # logs the entirety of each request in a file
            out.write(json.dumps(total_metadata, indent=4))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    return total_metadata

'''
Parses the total metadata returned from the API request 
for the metadata of an individual coin
'''
def get_individual_crypto_metadata(total_crypto_metadata, symb):
    return total_crypto_metadata['data'][symb]