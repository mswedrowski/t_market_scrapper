import math
import requests
from bs4 import BeautifulSoup
import numpy as np

import constants as c


def fetch_page(page):
    tree = requests.get(page, headers=c.headers)
    soup = BeautifulSoup(tree.content, 'html.parser')
    return soup


def build_url(league, transfer_season, league_initials, season):
    return "%s/%s/%s/wettbewerb/%s/saison_id/%d" % (c.BASIC_URL, league, transfer_season, league_initials, season)


def get_transfers(soup):
    for club_table_header in soup.find_all("div", {"class": "table-header"})[1:2]:
        to_club_name = club_table_header.text
        club_table = club_table_header.parent

        players = club_table.find("table").find_all("tr")[1:]
        for player in players:
            print(player)
            features = player.find_all("td")
            name = features[0].find("a", {"class": "spielprofil_tooltip"}).text
            age = features[1].text
            nationality = features[2].find('img')['alt']
            position = features[3].text
            market_value = features[5].text
            from_club_name = features[7].text.lstrip()
            fee = features[8].text

            print(name)
            print(nationality)
            print(from_club_name)
            print(fee)
    #return (club_table['id'])


if __name__ == "__main__":
    url = build_url(c.PREMIER_LEAGUE, c.SUMMER_TRANSFER_SEASON, c.PREMIER_LEAGUE_INITIALS, 2017)
    print(url)
    soup = fetch_page(url)
    print(get_transfers(soup))
