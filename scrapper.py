import requests
import os

import constants as c


def build_url(basic_url, league, league_initials, transfer_season, year):
    return f"{basic_url}/{league}/{transfer_season}/wettbewerb/{league_initials}/plus/?saison_id={year}$leihe=0"  # leihe=0 means that we don't consider lending


def fetch_page(url):
    tree = requests.get(url, headers=c.headers)
    page = tree.content
    return page


def save_page(path, page):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode='wb') as file:
        file.write(page)


def fetch_and_save_page_for_league(league_name, league_initials, transfer_season, year):
    url = build_url(c.BASIC_URL, league_name, league_initials, transfer_season, year)
    page = fetch_page(url)
    path = os.path.join(c.PAGES_PATH, league_name, f"{league_initials}_{transfer_season}_{year}.html")
    save_page(path, page)


if __name__ == "__main__":
    # leagues = c.LEAGUES
    # years = c.YEARS
    # transfer_seasons = c.TRANSFER_SEASONS

    leagues = [c.LEAGUES[0]]
    years = [2018, 2019]
    transfer_seasons = c.TRANSFER_SEASONS

    print("SCRAPING...")
    for league_name, league_initials in leagues:
        for year in years:
            for transfer_season in transfer_seasons:
                print(f"{league_initials}_{transfer_season}_{year}")
                fetch_and_save_page_for_league(league_name, league_initials, transfer_season, year)
