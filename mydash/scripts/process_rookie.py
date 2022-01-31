import argparse
from logging import getLogger

import pandas as pd

from mydash.utils.canonicalize import canonicalize_player, canonicalize_team
from mydash.utils.categorize import categorize_team
from mydash.utils.common import clean_name, clean_text
from mydash.utils.log import init_logger

LOGGER = getLogger(__name__)


def update_columns(rookie_df):
    p_rookie_df = rookie_df.copy()

    for col in ['player_name']:
        p_rookie_df[col] = p_rookie_df[col].apply(lambda x: canonicalize_player(clean_name(x)))
        LOGGER.info(f'updated \"{col}\" column')

    for col in ['team_name', 'prev_team_name']:
        p_rookie_df[col] = p_rookie_df[col].apply(lambda x: canonicalize_team(clean_text(x)))
        LOGGER.info(f'updated \"{col}\" column')

    p_rookie_df['prev_team_category'] = p_rookie_df['prev_team_name'].apply(lambda x: categorize_team(x).name)
    LOGGER.info('added \"prev_team_category\" column')

    return p_rookie_df


def main():
    rookie_df = pd.read_csv(args.rookie)

    rookie_df = update_columns(rookie_df)
    rookie_df = rookie_df[['year', 'league_id', 'player_name', 'team_name', 'prev_team_name', 'prev_team_category',
                           'birth', 'position']]

    rookie_df.to_csv(args.out, index=False)
    LOGGER.info(f'saved {args.out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ダウンロードした新卒選手一覧の前処理を行う')
    parser.add_argument('-r', '--rookie', help='fetch_rookie.pyで取得したrookieファイル', default='./data/rookie_raw.csv')
    parser.add_argument('-o', '--out', help='出力ファイル', default='./data/rookie.csv')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    init_logger(args.verbose)
    main()
