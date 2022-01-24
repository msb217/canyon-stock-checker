import argparse
import os
import re
import time

import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Sends a Discord notification if specified Canyon models in specified sizes are in stock.')
parser.add_argument('--sizes',
                    help='A list of sizes to check',
                    nargs='+', default=['XS', 'S', 'M', 'L', 'XL', 'XXL'])

args = vars(parser.parse_args())

sizes = set(map(str.upper, args.get('sizes')))

def post_to_discord(message):
    url = os.environ.get("DISCORD_WEBHOOK")
    requests.post(url=url, json={"content": message})

    # avoid throttle
    time.sleep(1)


urls_file = open('bikes.txt', 'r')
urls = urls_file.read().splitlines()

for url in urls:
    try:
        get = requests.get(url)
        soup = BeautifulSoup(get.text)
        bikes = soup.find_all("li", {"class": "productConfiguration__optionListItem"})
        for bike in bikes:
            try:
                size_div = bike.find("div", attrs={"class": "productConfiguration__variantType js-productConfigurationVariantType"})
                size = size_div.text.strip().upper()

                available_div = bike.find("div", attrs={"class": "productConfiguration__availabilityMessage"})
                available = available_div.text.strip().upper()
                available = re.sub(r'([^A-Za-z0-9]+)|\s', '', available)

                if 'INSTOCK' in available and size in sizes:
                    post_to_discord(
                        "url: {url}\nsize: {size}\navailable: {available}".format(url=url, size=size,
                                                                                  available=available))
            except:
                post_to_discord("broken url {url}".format(url=url))
    except:
        post_to_discord("broken url {url}").format(url=url)

    # avoid throttle
    time.sleep(5)
