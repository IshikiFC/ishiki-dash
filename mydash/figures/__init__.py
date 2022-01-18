from logging import getLogger

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from mydash.utils.common import assert_columns
from mydash.utils.df import get_avg_stats_df

LOGGER = getLogger(__name__)


def do_scatter_plot_play_time(rookie_df, stats_df, **kwargs):
    assert_columns(rookie_df, ['player_name', 'player_label'])
    assert_columns(stats_df, ['player_name', 'rookie_year', 'league_id', 'league', 'minutes'])

    rookie_df = rookie_df.reset_index(drop=True) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'player_index'})
    stats_df = pd.merge(stats_df, rookie_df[['player_name', 'player_index']], on='player_name')
    stats_df['y'] = 4 * stats_df['player_index'] + stats_df['league_id']

    for _ in range(2):
        # Plotly randomly fails. We can retry plotting, a hack found in the following discussion forum
        # https://community.plotly.com/t/valueerror-invalid-value-in-basedatatypes-py/55993
        try:
            fig = px.scatter(stats_df, x='rookie_year', y='y', size='minutes',
                             color='league',
                             category_orders={'league': ['J1', 'J2', 'J3']},
                             height=max(230, (len(rookie_df) + 1) * 80),
                             **kwargs)
            break
        except Exception as e:
            if _ == 0:
                continue
            LOGGER.exception(f'failed to scatter plot: {stats_df}')
            raise e
    fig.update_yaxes(range=[4 * len(rookie_df), 0])
    fig.update_xaxes(range=[0.5, 7.5])
    fig.update_traces(
        marker=dict(
            sizemode='area',
            sizeref=2. * 3600 / (30. ** 2)  # https://plotly.com/python/bubble-charts/
        )
    )
    fig.update_layout(
        yaxis=dict(
            title_text='',
            ticktext=rookie_df['player_label'],
            tickvals=rookie_df['player_index'] * 4 + 2
        ),
        xaxis=dict(
            title_text='rookie year'
        )
    )
    return fig


def do_scatter_plot_avg_play_time(rookie_df, stats_df):
    assert_columns(rookie_df, ['cur_rookie_year'])
    assert_columns(stats_df, ['rookie_year', 'league_id', 'league', 'minutes', 'apps', 'goals'])

    avg_stats_df = get_avg_stats_df(rookie_df, stats_df)

    # build dummy DataFrames for scatter_plot
    player_name = 'Avg.'
    d_rookie_df = pd.DataFrame([{'player_name': player_name, 'player_label': player_name}])
    d_stats_df = avg_stats_df
    d_stats_df['player_name'] = player_name
    d_stats_df['league'] = d_stats_df['league_id'].map(lambda x: f'J{x}')
    d_stats_df = d_stats_df.rename(columns={'player_count': '#players'})

    return do_scatter_plot_play_time(
        d_rookie_df,
        d_stats_df,
        hover_data={'minutes': ':.1f', 'apps': ':.1f', 'goals': ':.1f', '#players': True,
                    'rookie_year': False, 'y': False, 'league': False}
    )


def do_histogram_play_time(stats_df):
    LOGGER.info(f'do_histogram_play_time: #stats={len(stats_df)}')
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
    LOGGER.info(f'do_bar_plot_player_count: #players={len(rookie_df)}')
    count_df = rookie_df.groupby(['joined_year', 'joined_league']).size() \
        .reset_index().rename(columns={0: 'player_count'})
    fig = px.bar(count_df, x="joined_year", y="player_count", color="joined_league",
                 category_orders={'joined_league': ['J1', 'J2', 'J3']},
                 range_x=[2014.5, 2021.5])
    fig.update_layout(
        xaxis_title_text='year',
        yaxis_title_text='#player',
        legend_title_text='league'
    )
    return fig
