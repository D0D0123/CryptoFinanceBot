# CryptoBot

<p align="center">
  <!-- <img src="media/proper-logo-3-filled.png" /> -->
  <img src="media/CryptoLogov2Filled.svg" />
</p>

## Introduction

CryptoBot is an open source cryptocurrency bot for Discord. It automates much of the process of researching financial and background
information about cryptocurrencies and the economy surrounding them, as well as tracking their individual market performance. 
It was initially created as a side project to make cryptocurrency investment and learning more convenient, whilst furthering my knowledge of
API integration, database management, and system design. See the *Setting up your own Cryptocurrency Bot* section below to host your own
discord bot using this code.

### Features
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

<div align=center style="font-weight:bold;"> !crypto BTC -all </div>

## !list

Provides a list of the top 20 cryptocurrencies (ranked by market cap)

### Example:

<div align=center style="font-weight:bold;"> !list </div>

## !watch [param] [symbols...]

Add/Remove cryptocurrencies to/from a watch list.
The bot will provide hourly updates on the currencies in this watch list.
* Use '-add' [symbols...] to add symbols to the watch list
* Use '-remove' [symbols...] to remove symbols from the watch list
* Use '-show' to show the watch list

### Example:
 
<div align=center style="font-weight:bold;"> !watch -add BTC ETH </div>

<div align=center style="font-weight:bold;"> !watch -show </div>

## !ping [symbol] [> OR <] [price]

Add/Remove cryptocurrencies to/from a notification list, 
as well as specifying a price and a higher/lower comparison parameter.
The bot will notify you if the price of a chosen cryptocurrency
exceeds/falls below your chosen price.
* Use '>' if you want to be notified if the currency exceeds a price
* Use '<' if you want to be notified if the currency falls below a price
  
### Example:

<div align=center style="font-weight:bold;"> !ping BTC < 10000 </div>

## !news [symbol/phrase] [-general]

Provides the top 9 trending news articles surrounding 
either a specified cryptocurrency, or a general phrase.
* Use '-general' at the end of any word/phrase that isn't a cryptocurrency symbol

### Example:

<div align=center style="font-weight:bold;"> !news BTC </div>

<div align=center style="font-weight:bold;"> !news Australia -general </div>

## !newsfeed [symbol/phrase] [-general]

Sets the tri-daily automated news feed to provide news about a cryptocurrency
or custom phrase (the default is 'Cryptocurrency').

### Example:

<div align=center style="font-weight:bold;"> !newsfeed BTC </div>

## !about [symbol]

Displays information about a specified cryptocurrency, as well as a link to read more, and other relevant links.

### Example:

<div align=center style="font-weight:bold;"> !about ETH </div>

</br>
</br>
<p align="center" >
  <img style="border-radius:30px 30px 30px 30px" src="media/CryptoLogov2Banner.svg" />
</p>
</br>

## APIs 

* [CoinMarketCap API](https://coinmarketcap.com/api/documentation/v1/)
* [Google Knowledge Graph API](https://developers.google.com/knowledge-graph/?hl=en_US)
* [ContextualWeb News API](https://contextualweb.io/news-api/) 

## Setting up your own Cryptocurrency Bot

### Requirements


## How it works

