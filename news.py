from bs4 import BeautifulSoup
import requests
import re
import json


def get_about_info(crypto_name):
    crypto_html = requests.get(f"https://coinmarketcap.com/currencies/{crypto_name}").text
    soup = BeautifulSoup(crypto_html, 'lxml')
    about = soup.find('div', class_="sc-1lt0cju-0 srvSa")

    what_is_heading = about.find(id=re.compile("what-is"))
    possible_text1 = "Who Are"
    possible_text2 = "How Does"

    what_is_content = about.text.split(what_is_heading.text)[1].split(possible_text1)
    if len(what_is_content) == 1:
        what_is_content = about.text.split(what_is_heading.text)[1].split(possible_text2)
    # print(what_is_content)
    # print(len(what_is_content))
    # print(what_is_content[0])
    return what_is_content[0].replace(".", ". ")

def get_news(query_string):
    # https://contextualweb.io/news-api/
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI"

    querystring = {"q":query_string,"pageNumber":"1","pageSize":"10","autoCorrect":"true","fromPublishedDate":"null","toPublishedDate":"null"}

    headers = {
        'x-rapidapi-key': "88e966ea0cmsha786e4c465f62f1p14c61bjsn7b83615c8d96",
        'x-rapidapi-host': "contextualwebsearch-websearch-v1.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    news_data = json.loads(response.text)
    with open('news.log', 'w') as news_file:
        news_file.write(json.dumps(news_data, indent=4))
    
    return news_data['value']

# def get_news(crypto_name):
#     news_html = requests.get(f"https://www.google.com/search?q={crypto_name}&tbm=nws").text
#     soup = BeautifulSoup(news_html, 'lxml')
#     # print(soup.prettify())
#     headings = soup.find_all('div', 'dbsr')
#     print(headings)

# get_news('bitcoin')

# def get_about_info(crypto_name):
#     crypto_html = requests.get(f"https://coinmarketcap.com/currencies/{crypto_name}").text
#     # print(crypto_html)
#     soup = BeautifulSoup(crypto_html, 'lxml')
#     # print(soup.prettify())
#     about = soup.find('div', class_="sc-1lt0cju-0 srvSa")

#     what_is_heading = about.find(id=re.compile("what-is"))
#     founders_heading = about.find(id=re.compile("who-are-the-founders"))
#     unique_heading = about.find(id=re.compile("what-makes"))
#     final_heading = 'Related Pages:'

#     # print(what_is_heading.text)
#     # print(founders_heading.text)
#     # print(unique_heading.text)

#     what_is_content = about.text.split(what_is_heading.text)[1].split(founders_heading.text)[0]
#     founders_content = about.text.split(founders_heading.text)[1].split(unique_heading.text)[0]
#     unique_content = about.text.split(unique_heading.text)[1].split(final_heading)[0]

#     # print(what_is_content)
#     # print(founders_content)
#     # print(unique_content)
#     all_headings_content = [what_is_heading.text, what_is_content, founders_heading.text, founders_content, unique_heading.text, unique_content]
#     return all_headings_content
    