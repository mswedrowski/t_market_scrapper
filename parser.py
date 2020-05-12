from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os

import constants as c


class Node:
    def __init__(self, uid: int, name: str, group: str = "", start: str = "", end: str = "", lat: float = 0, lng: float = 0, notes: str = ""):
        self.uid = uid
        self.name = name
        self.group = group
        self.start = start
        self.end = end
        self.lat = lat
        self.lng = lng
        self.notes = notes

    def __str__(self):
        return self.name


class Edge:
    def __init__(self, source: int, target: int, weight: float, start: str = "", end: str = "", notes: str = ""):
        self.source = source
        self.target = target
        self.weight = weight
        self.start = start
        self.end = end
        self.notes = notes

    def __str__(self):
        return f"{self.source}-{self.target}:{self.weight}"


def get_next_node_id():
    global nodes_next_id
    id = nodes_next_id
    nodes_next_id += 1
    return id


def load_page(path):
    with open(path, 'r') as f:
        return f.read()


def convert_time(year) -> str:
    # return f"{year}-01-01"
    return str(year)


def convert_fee(fee: str) -> int:
    if fee == "Free transfer":
        return 0
    elif "m" in fee:
        fee_split = fee[1:-1].split(sep=".")
        big = int(fee_split[0])
        smoke = int(fee_split[1])
        return big * 1_000_000 + smoke * 1_000
    elif "Th." in fee:
        return int(fee[1:-3]) * 1_000
    else:
        raise ValueError()


def parse_page(page, league_name, league_initials, transfer_season, year):
    soup = BeautifulSoup(page, 'html.parser')

    club_table_headers = soup.find_all("div", {"class": "table-header"})[1:]
    for club_table_header in club_table_headers:
        to_club_name = club_table_header.text
        if to_club_name in NODES:
            to_club_node = NODES[to_club_name]
        else:
            to_club_node = Node(
                get_next_node_id(),
                to_club_name,
            )
            NODES[to_club_node.uid] = to_club_node

        to_club_node.group = league_name  # also for already existing nodes, which were created below with missing group label

        club_table = club_table_header.parent
        players = club_table.find("table").find_all("tr")[1:]
        for player in players:
            player_features = player.find_all("td")
            player_name = player_features[0].find("a", {"class": "spielprofil_tooltip"}).text
            player_age = player_features[1].text
            player_nationality = player_features[2].find('img')['alt']
            player_position = player_features[3].text
            player_market_value = player_features[5].text
            from_club_name = player_features[7].text.lstrip()
            fee = player_features[8].text
            if "€" not in fee and 'Free transfer' not in fee or "Loan fee" in fee:
                continue

            if from_club_name in NODES:
                from_club_node = NODES[from_club_name]
            else:
                from_club_node = Node(
                    get_next_node_id(),
                    from_club_name,
                )
                NODES[from_club_node.uid] = from_club_node

            transfer1992 = Edge(from_club_node.uid, to_club_node.uid, convert_fee(fee), start=convert_time(year), end=convert_time(2020), notes=player_name)
            EDGES.append(transfer1992)


if __name__ == "__main__":
    # leagues = c.LEAGUES
    # years = c.YEARS
    transfer_seasons = c.TRANSFER_SEASONS

    leagues = [c.LEAGUES[0]]
    years = [2019]
    # transfer_seasons = [c.SUMMER_TRANSFER_SEASON]

    NODES = {}
    EDGES = []
    nodes_next_id = 0

    print("PARSING...")
    for league_name, league_initials in leagues:
        for year in years:
            for transfer_season in transfer_seasons:
                print(f"{league_initials}_{year}_{transfer_season}")
                path = os.path.join(c.PAGES_PATH, league_name, f"{league_initials}_{year}_{transfer_season}.html")
                page = load_page(path)
                parse_page(page, league_name, league_initials, transfer_season, year)

    print()