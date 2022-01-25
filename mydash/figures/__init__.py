from dataclasses import dataclass
from logging import getLogger

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS

from mydash.utils.constants import FIRST_YEAR, LAST_YEAR
from mydash.utils.df import assert_columns

LOGGER = getLogger(__name__)


def do_scatter_plot_play_time(rookie_df, stats_df, **kwargs):
    assert_columns(rookie_df, ['player_name', 'player_label'])
    assert_columns(stats_df, ['player_name', 'rookie_year', 'league_id', 'league', 'minutes'])

    rookie_df = rookie_df.reset_index(drop=True) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'player_index'})
    stats_df = pd.merge(stats_df, rookie_df[['player_name', 'player_index']], on='player_name')
    stats_df['y'] = 4 * stats_df['player_index'] + stats_df['league_id']

    fig = None
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
    assert fig is not None
    fig.update_yaxes(range=[4 * len(rookie_df), 0])
    fig.update_xaxes(range=[0.5, LAST_YEAR - FIRST_YEAR + 1.5])
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


@dataclass
class HistogramConfig:
    rookie_year: int = 1
    league_id: int = 1


def do_histogram_play_time(stats_df, config: HistogramConfig):
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
        title=dict(
            text=f'league=J{config.league_id}, rookie year={config.rookie_year}, #stats={len(stats_df)}',
            x=0.5
        ),
        xaxis_title_text='minutes',
        yaxis_title_text='#players',
        bargap=0.2,
        bargroupgap=0.1
    )
    return fig


def do_bar_plot_player_count(rookie_df, color_column='league'):
    if color_column == 'league':
        color_column_full = 'joined_league'
    elif color_column == 'category':
        color_column_full = 'prev_team_category'
    elif color_column == 'position':
        color_column_full = 'position'
    else:
        raise ValueError(f'unknown color column = {color_column}')

    assert_columns(rookie_df, ['joined_year', color_column_full])
    count_df = rookie_df.groupby(['joined_year', color_column_full]).size() \
        .reset_index().rename(columns={0: '#players',
                                       'joined_year': 'year',
                                       color_column_full: color_column})
    fig = px.bar(count_df, x='year', y='#players', color=color_column,
                 category_orders={
                     'league': ['J1', 'J2', 'J3'],
                     'category': ['HIGH', 'YOUTH', 'UNIV'],
                     'position': ['GK', 'DF', 'MF', 'FW']
                 },
                 range_x=[FIRST_YEAR - 0.5, LAST_YEAR + 0.5])
    fig.update_traces(width=0.8)
    fig.update_layout(
        title=dict(
            text=f'#players={len(rookie_df)}',
            x=0.5
        )
    )
    return fig
