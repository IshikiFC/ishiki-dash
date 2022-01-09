import argparse
import time
from logging import getLogger

import pandas as pd
import requests
from bs4 import BeautifulSoup

from mydash.utils import init_logger, clean_text, clean_name, canonicalize_team

LOGGER = getLogger(__name__)


def build_rookie_url(year: int, league_id: int):
    """
    e.g. https://soccer-db.net/contents/2015_j_newcomers.php
    """

    league = 'j' if league_id == 1 else f'j{league_id}'
    return f'https://soccer-db.net/contents/{year}_{league}_newcomers.php'


def contains_class(div, class_name):
    return class_name in div.attrs.get('class', [])


def extract_text(div):
    if contains_class(div, 'group_title'):
        return div.find(class_='gt_j').text
    return div.text


def extract_player_meta(div):
    cells = div.find('table').find_all('td')
    meta = {
        'birth': cells[2].text,
        'prev_team_name': canonicalize_team(clean_text(cells[3].text))
    }
    return meta


def fetch_players(year, league_id):
    url = build_rookie_url(year, league_id)
    LOGGER.info(f'fetch players from {url}')
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    time.sleep(1)

    if soup.find(class_='main_contents'):
        main_tag, team_tag, player_tag = 'main_contents', 'group_title', 'mini_jpn_title'
    elif soup.find(class_='full_contents'):  # after 2017
        main_tag, team_tag, player_tag = 'full_contents', 'cp_middletitle', 'group_title'
    else:
        raise ValueError(f'failed to find main/full_contents in {url}')

    records = []
    team_name = None
    divs = soup.find(class_=main_tag).find_all('div')
    for i, div in enumerate(divs):
        if contains_class(div, team_tag):
            team_name = canonicalize_team(clean_text(extract_text(div)))
        if contains_class(div, player_tag):
            assert team_name
            record = {
                'year': year,
                'league': league_id,
                'team_name': team_name,
                'player_name': clean_name(extract_text(div))
            }
            record.update(extract_player_meta(divs[i + 1]))
            records.append(record)

    LOGGER.info(f'fetched {len(records)} players')
    return records


def main():
    records = []
    for year in range(2015, 2022):
        for league in range(1, 4):
            records += fetch_players(year, league)
    out_df = pd.DataFrame(records)
    out_df = out_df[['year', 'league', 'player_name', 'team_name', 'prev_team_name', 'birth']]
    out_df.to_csv(args.out, index=False)
    LOGGER.info(f'saved rookies in {args.out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Soccer D.B.から新卒選手を取得する')
    parser.add_argument('-o', '--out', help='出力ファイル名', default='./data/rookies.csv')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    init_logger(args)
    main()
