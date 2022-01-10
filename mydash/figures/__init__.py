from logging import getLogger

import pandas as pd
import plotly.express as px

LOGGER = getLogger(__name__)


def do_scatter_plot_play_time(rookie_df, stats_df):
    rookie_df = rookie_df.reset_index(drop=True) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'player_index'})
    stats_df = pd.merge(stats_df, rookie_df[['player_name', 'player_index']], on='player_name')
    stats_df['y'] = 4 * stats_df['player_index'] + stats_df['league_id']

    fig = px.scatter(stats_df, x='rookie_year', y='y', size='minutes',
                     color='league',
                     category_orders={'league': ['J1', 'J2', 'J3']},
                     hover_data=['team_name', 'minutes', 'apps', 'goals'])
    fig.update_yaxes(range=[4 * len(rookie_df) + 1, 0])
    fig.update_xaxes(range=[0.5, 7.5])
    fig.update_traces(marker=dict(
        sizemode='area',
        sizeref=2. * 3600 / (30. ** 2)  # https://plotly.com/python/bubble-charts/
    ))

    fig.update_layout(
        autosize=False,
        width=800,
        height=max(500, len(rookie_df) * 100),
        yaxis=dict(
            title_text='',
            ticktext=rookie_df['player_label'],
            tickvals=rookie_df['player_index'] * 4 + 2
        )
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
