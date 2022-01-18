import argparse
import time
from dataclasses import dataclass, asdict
from logging import getLogger

import pandas as pd
import requests

from mydash.utils.common import build_url, clean_name
from mydash.utils.log import init_logger

LOG_DATE_FORMAT = "%Y-%m-%d %I:%M:%S"
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

LOGGER = getLogger(__name__)


@dataclass
class Competition:
    comp_id: int
    comp_name: str
    year: int
    frame_id: int


@dataclass
class Team:
    team_id: int
    team_name: str


@dataclass
class Stats:
    player_name: str
    apps: int
    minutes: int
    goals: int


def build_stats_url(year, frame_id, comp_id, team_id):
    """
    e.g.) https://data.j-league.or.jp/SFPR01/search?competition_year=2021&competition_frame_id=1&competition_id=492&team_id=14

    :param year:
    :param frame_id: 1-3 for J1-3, 11 for cup
    :param comp_id: unique competition ID. use `fetch_competitions(year)` to get available IDs
    :param team_id: unique team ID. use `fetch_teams(comp_id)` to get available IDs
    """

    url = 'https://data.j-league.or.jp/SFPR01/search'
    query = {
        'competition_year': year,
        'competition_frame_id': frame_id,
        'competition_id': comp_id,
        'team_id': team_id
    }
    return build_url(url, query)


def fetch_stats(comp: Competition, team: Team):
    stats_url = build_stats_url(comp.year, comp.frame_id, comp.comp_id, team.team_id)
    LOGGER.info(f'fetch stats from {stats_url}')
    dfs = pd.read_html(stats_url)
    assert len(dfs) == 2
    df = dfs[0]
    time.sleep(1)

    records = []
    for _, row in df.iterrows():
        records.append(Stats(
            player_name=clean_name(row[1]),
            apps=int(row[2]),
            minutes=int(row[3]),
            goals=int(row[4])
        ))
    LOGGER.info(f'fetched {len(records)} stats')
    return records


def fetch_teams(comp: Competition):
    url = 'https://data.j-league.or.jp/SFPR01/createTeams'
    payload = {'competition_id': comp.comp_id}
    LOGGER.info(f'fetch teams from {url} : {payload}')
    response = requests.post(url, payload)
    data = response.json()
    time.sleep(1)

    records = []
    for item in data['teamList']:
        records.append(Team(
            team_id=int(item['selectValue']),
            team_name=item['displayName']
        ))
    LOGGER.info(f'fetched {len(records)} teams')
    return records


def fetch_competitions(year):
    records = []
    for frame_id in [1, 2, 3]:
        url = 'https://data.j-league.or.jp/SFPR01/createCompetitions'
        payload = {'competition_year': year, 'competition_frame_id': frame_id}
        LOGGER.info(f'fetch competitions from {url}: {payload}')
        response = requests.post(url, payload)
        data = response.json()
        time.sleep(1)

        for item in data['competitionList']:
            records.append(Competition(
                comp_id=int(item['selectValue']),
                comp_name=item['displayName'],
                year=year,
                frame_id=frame_id
            ))
        LOGGER.info(f'fetched {len(records)} competitions')
    return records


def main():
    records = []
    for year in range(2015, 2022):
        for comp in fetch_competitions(year):
            for team in fetch_teams(comp):
                for stat in fetch_stats(comp, team):
                    record = dict()
                    record.update(asdict(comp))
                    record.update(asdict(team))
                    record.update(asdict(stat))
                    records.append(record)
    out_df = pd.DataFrame(records)
    out_df = out_df[['year', 'frame_id', 'team_name', 'player_name', 'apps', 'minutes', 'goals']]
    out_df = out_df.rename(columns={'frame_id': 'league_id'})
    out_df.to_csv(args.out, index=False)
    LOGGER.info(f'saved stats in {args.out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='J.LEAGUE Data Siteから出場記録を取得する')
    parser.add_argument('-o', '--out', help='出力ファイル名', default='./data/stats.csv')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    init_logger(args.verbose)
    main()
