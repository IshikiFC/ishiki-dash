import pandas as pd
import numpy as np

from mydash.utils.common import assert_columns


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


