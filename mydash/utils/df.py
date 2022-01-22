import numpy as np
import pandas as pd

from mydash.utils.constants import LAST_YEAR


def assert_columns(df, columns):
    for col in columns:
        assert col in df.columns, f'column does not exist: \'{col}\' not in  {list(df.columns)}'


def load_rookie_df():
    rookie_df = pd.read_csv('./data/rookie.csv')
    rookie_df = rookie_df.rename(
        columns=dict([(col, f'joined_{col}') for col in ['year', 'league_id', 'team_name']])
    )
    rookie_df['joined_league'] = rookie_df['joined_league_id'].map(lambda x: f'J{x}')
    rookie_df['player_label'] = rookie_df.apply(lambda x: '{0}({1})<br>{2}<br>{3}'.format(
        x['player_name'], x['joined_year'], x['joined_team_name'], x['prev_team_name']), axis=1)
    rookie_df['cur_rookie_year'] = LAST_YEAR - rookie_df['joined_year'] + 1
    return rookie_df


def load_stats_df(rookie_df):
    stats_df = pd.read_csv('./data/stats_processed.csv')
    stats_df['league'] = stats_df['league_id'].map(lambda x: f'J{x}')
    stats_df = pd.merge(stats_df, rookie_df[['player_name', 'joined_year']], on='player_name')
    stats_df['rookie_year'] = stats_df['year'] - stats_df['joined_year'] + 1
    stats_df['stats_label'] = stats_df.apply(lambda x: '{0}({1})'.format(x['team_name'], x['year']), axis=1)
    return stats_df


def filter_rookie_df(df, joined_teams=None, prev_teams=None, player_names=None,
                     joined_league_ids=None, prev_categories=None, positions=None, joined_year_range=None):
    mask = np.ones(len(df)).astype(bool)
    if joined_teams:
        mask &= df['joined_team_name'].isin(joined_teams)
    if prev_teams:
        mask &= df['prev_team_name'].isin(prev_teams)
    if player_names:
        mask &= df['player_name'].isin(player_names)
    if joined_league_ids:
        mask &= df['joined_league_id'].isin(joined_league_ids)
    if positions:
        mask &= df['position'].isin(positions)
    if prev_categories:
        mask &= df['prev_team_category'].isin(prev_categories)
    if joined_year_range:
        mask &= df['joined_year'] >= joined_year_range[0]
        mask &= df['joined_year'] <= joined_year_range[1]
    return df[mask]


def filter_stats_df(df, rookie_year=None, league_id=None, minutes_range=None, player_names=None):
    mask = np.ones(len(df)).astype(bool)
    if rookie_year:
        mask &= df['rookie_year'] == rookie_year
    if league_id:
        mask &= df['league_id'] == league_id
    if minutes_range:
        mask &= df['minutes'] >= minutes_range[0]
        mask &= df['minutes'] <= minutes_range[1]
    if player_names:
        mask &= df['player_name'].isin(player_names)
    return df[mask]


def get_avg_stats_df(rookie_df, stats_df, stats_cols=None):
    if stats_cols is None:
        stats_cols = ['minutes', 'apps', 'goals']
    assert_columns(rookie_df, ['cur_rookie_year'])
    assert_columns(stats_df, ['rookie_year', 'league_id'] + stats_cols)

    # calculate player_count for each rookie_year
    agg_rookie_df = rookie_df.groupby('cur_rookie_year').size().reset_index() \
        .rename(columns={'cur_rookie_year': 'rookie_year', 0: 'player_count'})
    count_df = pd.DataFrame({'rookie_year': range(1, 8)})  # max 7 as of 2021
    count_df = pd.merge(count_df, agg_rookie_df, on='rookie_year', how='left').fillna(0).astype(int)
    # reverse cumsum here to make players with cur_rookie_year=3 available for rookie_year=[1,2,3], for example
    count_df['player_count'] = count_df['player_count'][::-1].cumsum()[::-1]
    count_df = count_df[count_df['player_count'] > 0]
    assert_columns(count_df, ['rookie_year', 'player_count'])

    # calculate avg stats
    agg_stats_df = stats_df.groupby(['rookie_year', 'league_id'])[stats_cols].sum() \
        .reset_index()
    agg_stats_df = pd.merge(agg_stats_df, count_df, on='rookie_year')
    for col in stats_cols:
        agg_stats_df[col] = agg_stats_df[col] / agg_stats_df['player_count']
    assert_columns(agg_stats_df, ['rookie_year', 'league_id'] + stats_cols)

    return agg_stats_df
