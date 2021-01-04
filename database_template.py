bot_data = [
    {
       'guild': 1234, # one dictionary (server_dict) for each guild that the bot is in
       'autopost_channel': 1234, # which channel should autoposts go in
       'watch_list': ['BTC', 'ETH', 'XRP'], # which currencies to watch hourly
       'price_pings': [ #pings for particular price drops
            {
                'user': 1234,
                'currency': 'BTC',
                'price': 10000,
                'higher': True,
            },
        ]
    },
]