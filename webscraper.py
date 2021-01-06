from bs4 import BeautifulSoup
import requests
import re

def get_about_info(crypto_name):
    crypto_html = requests.get(f"https://coinmarketcap.com/currencies/{crypto_name}").text
    # print(crypto_html)
    soup = BeautifulSoup(crypto_html, 'lxml')
    # print(soup.prettify())
    about = soup.find('div', class_="sc-1lt0cju-0 srvSa")

    what_is_heading = about.find(id=re.compile("what-is"))
    founders_heading = about.find(id=re.compile("who-are-the-founders"))
    unique_heading = about.find(id=re.compile("what-makes"))
    final_heading = 'Related Pages:'

    # print(what_is_heading.text)
    # print(founders_heading.text)
    # print(unique_heading.text)

    what_is_content = about.text.split(what_is_heading.text)[1].split(founders_heading.text)[0]
    founders_content = about.text.split(founders_heading.text)[1].split(unique_heading.text)[0]
    unique_content = about.text.split(unique_heading.text)[1].split(final_heading)[0]

    # print(what_is_content)
    # print(founders_content)
    # print(unique_content)
    all_headings_content = [what_is_heading.text, what_is_content, founders_heading.text, founders_content, unique_heading.text, unique_content]
    return all_headings_content
    