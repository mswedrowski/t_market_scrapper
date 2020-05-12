from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os
from easymoney.money import EasyPeasy
from typing import Tuple

import constants as c

ep = EasyPeasy()

class Node:
    def __init__(self, uid: int, name: str, year: int, season: str, country: str, group: str = "", lat: float = 0, lng: float = 0, notes: str = ""):
        self.uid = uid
        self.name = name
        self.group = group
        self.country = country
        self.year = year
        self.season = season
        self.start = convert_time(year, season)
        self.end = convert_time(2020, c.SUMMER_TRANSFER_SEASON)
        self.lat = lat
        self.lng = lng
        self.notes = notes

    def __str__(self):
        return self.name


class Edge:
    def __init__(self, source: int, target: int, weight: float, weight_norm: float, year: int, season: str, notes: str = ""):
        self.source = source
        self.target = target
        self.weight = weight
        self.weight_norm = weight_norm
        self.year = year
        self.season = season
        self.start = convert_time(year, season)
        self.end = convert_time(2020, c.SUMMER_TRANSFER_SEASON)
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


def convert_time(year, season) -> str:
    if season == c.WINTER_TRANSFER_SEASON:
        return f"{year}-01-01"
    elif season == c.SUMMER_TRANSFER_SEASON:
        return f"{year}-06-01"
    else:
        raise ValueError()


def convert_fee(fee: str, year) -> Tuple[int, int]:
    if fee == "Free transfer":
        fee_transformed = 0
    elif "m" in fee:
        fee_split = fee[1:-1].split(sep=".")
        big = int(fee_split[0])
        small = int(fee_split[1])
        fee_transformed = big * 1_000_000 + small * 10_000
    elif "Th." in fee:
        fee_transformed = int(fee[1:-3]) * 1_000
    elif len(fee) == 4:  # e.g. '€500'
        fee_transformed = int(fee[1:])
    else:
        raise ValueError()

    return fee_transformed, int(ep.normalize(amount=fee_transformed, region="DEU", from_year=year))
    # return fee_transformed

def parse_page(page, league_name, league_initials, transfer_season, year):
    soup = BeautifulSoup(page, 'html.parser')
    league_country = soup.find("div", {"class": "flagge"}).find('img')['alt'].strip()

    club_table_headers = soup.find_all("div", {"class": "table-header"})[1:]
    for club_table_header in club_table_headers:
        to_club_name = club_table_header.text.strip()
        if to_club_name in NODES:
            to_club_node = NODES[to_club_name]
        else:
            to_club_node = Node(
                uid=get_next_node_id(),
                name=to_club_name,
                year=year,
                season=transfer_season,
                country=league_country
            )
            NODES[to_club_node.name] = to_club_node

        to_club_node.group = league_name  # also for already existing nodes, which were created below with missing group label

        club_table = club_table_header.parent
        players = club_table.find("table").find_all("tr")[1:]
        for player in players:
            player_features = player.find_all("td")
            if "No new arrivals" in player_features[0].text:
                continue

            fee = player_features[8].text
            if "€" not in fee and 'Free transfer' not in fee or "Loan fee" in fee or "?" in fee or "-" in fee:
                continue
            from_club_name = player_features[6].find('img')['alt'].strip()
            if from_club_name == "Unknown":
                continue
            player_name = player_features[0].find("a", {"class": "spielprofil_tooltip"}).text
            player_age = player_features[1].text
            player_nationality = player_features[2].find('img')['alt']
            player_position = player_features[3].text
            player_market_value = player_features[5].text
            if from_club_name == "Career break" or from_club_name == "Without Club":
                from_club_country = "NA"
            else:
                from_club_country = player_features[7].find('img')['alt'].strip()
                if from_club_country == "Korea, South":
                    from_club_country = "South Korea"

            if from_club_name in NODES:
                from_club_node = NODES[from_club_name]
            else:
                from_club_node = Node(
                    uid=get_next_node_id(),
                    name=from_club_name,
                    year=year,
                    season=transfer_season,
                    country=from_club_country
                )
                NODES[from_club_node.name] = from_club_node

            fee, fee_normalized = convert_fee(fee, year)
            transfer = Edge(from_club_node.uid, to_club_node.uid, fee, fee_normalized, year, transfer_season, notes=player_name)
            EDGES.append(transfer)


def save_nodes_and_edges(nodes, edges):
    with open(os.path.join(c.RESULTS_PATH, "nodes.csv"), 'w') as f:
        f.write("id,label,group,country,year,season,start,end,lat,lng,notes\n")
        for n in nodes.values():
            f.write(f"{n.uid},{n.name},{n.group},{n.country},{n.year},{n.season},{n.start},{n.end},{n.lat},{n.lng},{n.notes}\n")

    with open(os.path.join(c.RESULTS_PATH, "edges.csv"), 'w') as f:
        f.write("source,target,weight_not_norm,weight,year,season,start,end,label\n")
        for e in edges:
            f.write(f"{e.source},{e.target},{e.weight},{e.weight_norm},{e.year},{e.season},{e.start},{e.end},{e.notes}\n")


if __name__ == "__main__":
    leagues = c.LEAGUES
    years = c.YEARS
    transfer_seasons = c.TRANSFER_SEASONS

    NODES = {}
    EDGES = []
    nodes_next_id = 0

    print("PARSING...")
    for year in years:
        for transfer_season in transfer_seasons:
            for league_name, league_initials in leagues:
                print(f"{league_initials}_{year}_{transfer_season}")
                path = os.path.join(c.PAGES_PATH, league_name, f"{league_initials}_{year}_{transfer_season}.html")
                page = load_page(path)
                parse_page(page, league_name, league_initials, transfer_season, year)

    print("Nodes:", len(NODES))
    print("Edges:", len(EDGES))
    save_nodes_and_edges(NODES, EDGES)


