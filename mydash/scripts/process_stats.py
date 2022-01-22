import argparse
from logging import getLogger

import pandas as pd

from mydash.utils.log import init_logger

LOGGER = getLogger(__name__)


def filter_rookie(stats_df, rookie_df):
    p_stats_df = pd.merge(stats_df, rookie_df[['player_name']], on='player_name')
    LOGGER.info('filtered rookie stats: {} -> {}'.format(len(stats_df), len(p_stats_df)))
    return p_stats_df


def drop_stats(stats_df, drop_df):
    drop_df['drop'] = True
    p_stats_df = pd.merge(stats_df, drop_df, on=['player_name', 'year', 'team_name'], how='left')
    p_stats_df['drop'] = p_stats_df['drop'].fillna(False)
    p_stats_df = p_stats_df[~p_stats_df['drop']]
    p_stats_df = p_stats_df.drop(['drop'], axis=1)
    assert len(drop_df) == len(stats_df) - len(p_stats_df)
    LOGGER.info('dropped stats: {} -> {}'.format(len(stats_df), len(p_stats_df)))
    return p_stats_df


def merge_stats(stats_df):
    p_stats_df = stats_df.groupby(['year', 'league_id', 'team_name', 'player_name']).sum().reset_index()
    LOGGER.info('merged separated stats: {} -> {}'.format(len(stats_df), len(p_stats_df)))
    return p_stats_df


def main():
    stats_df = pd.read_csv(args.stats)
    rookie_df = pd.read_csv(args.rookie)
    drop_df = pd.read_csv(args.drop)

    stats_df = filter_rookie(stats_df, rookie_df)
    stats_df = drop_stats(stats_df, drop_df)
    stats_df = merge_stats(stats_df)

    stats_df.to_csv(args.out, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ダウンロードした出場記録の前処理を行う')
    parser.add_argument('-s', '--stats', help='fetch_stats.pyで取得したstatsファイル', default='./data/stats.csv')
    parser.add_argument('-r', '--rookie', help='fetch_rookie.pyで取得したrookieファイル', default='./data/rookie.csv')
    parser.add_argument('-d', '--drop', help='除くべきstatsを定義したファイル（同姓同名など）', default='./data/drop.csv')
    parser.add_argument('-o', '--out', help='出力ファイル', default='./data/stats_processed.csv')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    init_logger(args.verbose)
    main()
