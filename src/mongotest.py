# mongodb+srv://dbUser0:<password>@cluster0.ijvyk.mongodb.net/<dbname>?retryWrites=true&w=majority

import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')

cluster = MongoClient(MONGODB_URI)
db = cluster["CryptoBot"]
collection = db["GuildData"]

doc0 = {"_id": 0,
        "guild": 793053167842754580,
        "autopost_channel": 793442420959346698,
        "newsfeed": "Cryptocurrency",
        "watch_list": [
            "ETH",
            "USDT"
        ],
        "price_pings": [
            {
                "user": 270100069682905090,
                "currency": "BTC",
                "price": 40000.0,
                "higher": False
            },
            {
                "user": 270100069682905090,
                "currency": "BTC",
                "price": 50000.0,
                "higher": True
            }
        ]
    }

doc1 = {"_id": 1,
        "guild": 797406310580355082,
        "autopost_channel": 797406310580355085,
        "newsfeed": "Cryptocurrency",
        "watch_list": [],
        "price_pings": [
            {
                "user": 797404797526867978,
                "currency": "BTC",
                "price": 45000.0,
                "higher": False
            },
            {
                "user": 270100069682905090,
                "currency": "BTC",
                "price": 25000.0,
                "higher": True
            }
        ]
    }

# collection.insert_many([doc0, doc1])

# server_count = collection.count_documents({})
# print(server_count)

results = collection.find({})
for result in results:
    print(result)
    # for ping in result["price_pings"]:
    #     print(ping)
