from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from time import sleep
import json

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
    print(json.dumps(data, indent=4))
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
    # sleep(10)

query = input("Which currency would you like to view? : ")
for obj in data['data']:
    if obj['symbol'] == query:
        print(obj['name'])
        print("--------------------------------")
        print(json.dumps(obj['quote'], indent=4))
        break
else:
    print("Requested cryptocurrency not found")
