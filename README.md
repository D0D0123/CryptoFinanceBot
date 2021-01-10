
</br>
</br>
<p align="center" >
  <img src="media/CryptoLogov2Banner.svg" />
</p>
</br>

# CryptoBot

CryptoBot is an open source cryptocurrency bot for Discord, which automates the process of obtaining economic
information about cryptocurrencies, as well as tracking their individual market performance. 
It was initially created as a side project to make cryptocurrency investment and learning more convenient, whilst furthering my knowledge of
API integration, database management, and system design. See the *Setting up your own Cryptocurrency Bot* section below to host your own
discord bot using this code.

## Features
CryptoBot is able to:
* Retrieve and display real-time financial information for individual cryptocurrencies, including:
    - Price
    - Rank
    - Platform
    - Daily Volume Traded
    - Percentage Changes (Hourly, 7 Hourly, Daily)
    - Market Cap
    - Max, Circulating and Total Supply
* Display background information about each cryptocurrency, as well as providing relevant links to 
official websites, financial information websites, social media pages, and technical documents 
* Retrieve and display the top nine trending news articles for a specified cryptocurrency, or any general economic news
    - Includes a tri-daily news feed to remain updated on the latest general cryptocurrency news
* Track multiple chosen cryptocurrencies and provide hourly updates on their performance
* Be set to notify individual users when chosen cryptocurrencies exceed/fall below a specified price

## Commands

### Command List

| Command       | Arguments         
| ------------- |:-------------:   
| !crypto       | [symbol] [param]  
| !list         |      N/A            
| !watch        | [param] [symbols...] 
| !ping         | [symbol] [> OR <] [price]
| !news         | [symbol/phrase] [-general]
| !newsfeed     | [symbol/phrase] [-general]
| !about        | [symbol]
| !post         | [channel ID]
| !raw          |      N/A
</br>

### Descriptions
</br>

## !crypto [symbol] [param]

Displays financial information surrounding a cryptocurrency, 
with the depth of information depending on the parameter given
(None, -extra, -supply, -links, -all)
* With no parameter, only price, rank and platform will be shown
* Use '-extra' to show daily volume traded, and percentage changes
* Use '-supply' to show market cap and supply information
* Use '-links' to show relevant links
* Use '-all' to show all the above information

### Example:

**!crypto BTC -all**

## !list

Provides a list of the top 20 cryptocurrencies (ranked by market cap)

### Example:

**!list**

## !watch [param] [symbols...]

Add/Remove cryptocurrencies to/from a watch list.
The bot will provide hourly updates on the currencies in this watch list.
* Use '-add' [symbols...] to add symbols to the watch list
* Use '-remove' [symbols...] to remove symbols from the watch list
* Use '-show' to show the watch list

### Example:
 
**!watch -add BTC ETH**

**!watch -show**

## !ping [symbol] [> OR <] [price]

Add/Remove cryptocurrencies to/from a notification list, 
as well as specifying a price and a higher/lower comparison parameter.
The bot will notify you if the price of a chosen cryptocurrency
exceeds/falls below your chosen price.
* Use '>' if you want to be notified if the currency exceeds a price
* Use '<' if you want to be notified if the currency falls below a price
  
### Example:

**!ping BTC < 10000**

## !news [symbol/phrase] [-general]

Provides the top 9 trending news articles surrounding 
either a specified cryptocurrency, or a general phrase.
* Use '-general' at the end of any word/phrase that isn't a cryptocurrency symbol

### Example:

**!news BTC**

**!news Australia -general**

## !newsfeed [symbol/phrase] [-general]

Sets the tri-daily automated news feed to provide news about a cryptocurrency
or custom phrase (the default is 'Cryptocurrency').

### Example:

**!newsfeed BTC**

## !about [symbol]

Displays information about a specified cryptocurrency, as well as a link to read more, and other relevant links.

### Example:

**!about ETH**

</br>
<p align="center">
  <!-- <img src="media/proper-logo-3-filled.png" /> -->
  <img height="200" src="media/CryptoLogov2Triad.svg" />
</p>
</br>

## APIs 

* [CoinMarketCap API](https://coinmarketcap.com/api/documentation/v1/)
* [Google Knowledge Graph API](https://developers.google.com/knowledge-graph/?hl=en_US)
* [ContextualWeb News API](https://contextualweb.io/news-api/) 

## Setting up your own Cryptocurrency Bot

*Discord Developer Portal Steps Here*

*API Setup Steps Here*

*Fill in .env file*

*Install required packages*

*Navigate into /src and run python crypto.py*

### Requirements


## How it works

