from logging import getLogger

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from mydash.utils import assert_columns

LOGGER = getLogger(__name__)


def do_scatter_plot_play_time(rookie_df, stats_df, **kwargs):
    assert_columns(rookie_df, ['player_name', 'player_label'])
    assert_columns(stats_df, ['player_name', 'rookie_year', 'league_id', 'league', 'minutes'])

    rookie_df = rookie_df.reset_index(drop=True) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'player_index'})
    stats_df = pd.merge(stats_df, rookie_df[['player_name', 'player_index']], on='player_name')
    stats_df['y'] = 4 * stats_df['player_index'] + stats_df['league_id']

    fig = px.scatter(stats_df, x='rookie_year', y='y', size='minutes',
                     color='league',
                     category_orders={'league': ['J1', 'J2', 'J3']},
                     **kwargs)
    fig.update_yaxes(range=[4 * len(rookie_df), 0])
    fig.update_xaxes(range=[0.5, 7.5])
    fig.update_traces(marker=dict(
        sizemode='area',
        sizeref=2. * 3600 / (30. ** 2)  # https://plotly.com/python/bubble-charts/
    ))

    fig.update_layout(
        autosize=False,
        width=800,
        height=max(250, (len(rookie_df) + 1) * 100),
        yaxis=dict(
            title_text='',
            ticktext=rookie_df['player_label'],
            tickvals=rookie_df['player_index'] * 4 + 2
        )
    )
    return fig


def do_scatter_plot_avg_play_time(rookie_df, stats_df):
    assert_columns(rookie_df, ['current_year'])
    assert_columns(stats_df, ['rookie_year', 'league_id', 'league', 'minutes', 'apps', 'goals'])

    agg_rookie_df = rookie_df.groupby('current_year').size().reset_index() \
        .rename(columns={'current_year': 'rookie_year', 0: 'player_count'})
    count_df = pd.DataFrame({'rookie_year': range(1, 8)})
    count_df = pd.merge(count_df, agg_rookie_df, on='rookie_year', how='left')
    count_df['player_count'] = count_df['player_count'].fillna(0).astype(int)
    count_df['player_count'] = count_df['player_count'][::-1].cumsum()[::-1]

    agg_stats_df = stats_df.groupby(['rookie_year', 'league_id', 'league'])[['minutes', 'apps', 'goals']].sum() \
        .reset_index()
    agg_stats_df = pd.merge(agg_stats_df, count_df, on='rookie_year')
    for field in ['minutes', 'apps', 'goals']:
        agg_stats_df[field] = agg_stats_df[field] / agg_stats_df['player_count']

    # build dummy DataFrames for scatter_plot
    d_rookie_df = pd.DataFrame([{'player_name': 'avg', 'player_label': 'avg'}])
    d_stats_df = agg_stats_df
    d_stats_df['player_name'] = 'avg'

    return do_scatter_plot_play_time(
        d_rookie_df,
        d_stats_df,
        hover_data={'minutes': ':.1f', 'apps': ':.1f', 'goals': ':.1f', 'player_count': True,
                    'rookie_year': False, 'y': False, 'league': False}
    )


def do_histogram_play_time(stats_df):
    assert_columns(stats_df, ['league_id', 'minutes'])

    fig = go.Figure()
    for league_id, color in zip(range(1, 4), DEFAULT_PLOTLY_COLORS):
        fig.add_trace(go.Histogram(
            x=stats_df[stats_df['league_id'] == league_id]['minutes'],
            name=f'J{league_id}',
            marker_color=color,
            xbins=dict(start=0, end=3600, size=100)
        ))
    fig.update_xaxes(range=[0, 3600])
    fig.update_layout(
        xaxis_title_text='minutes',
        yaxis_title_text='#players',
        bargap=0.2,
        bargroupgap=0.1
    )
    return fig


def do_bar_plot_player_count(rookie_df):
    count_df = rookie_df.groupby(['joined_year', 'joined_league']).size() \
        .reset_index().rename(columns={0: 'player_count'})
    fig = px.bar(count_df, x="joined_year", y="player_count", color="joined_league",
                 category_orders={'joined_league': ['J1', 'J2', 'J3']},
                 range_x=[2014.5, 2021.5])
    fig.update_traces(width=0.8)
    return fig
