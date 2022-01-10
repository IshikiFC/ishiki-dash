from collections import defaultdict
from logging import getLogger

import pandas as pd
import plotly.express as px

LOGGER = getLogger(__name__)


def scatter_plot_play_time(df):
    name2label, name2index = dict(), dict()
    player_df = df[['player_name', 'joined_year', 'joined_team_name', 'prev_team_name']] \
        .drop_duplicates(keep='first') \
        .reset_index(drop=True)
    for i, row in player_df.iterrows():
        name = row['player_name']
        label = '{0}({1})<br>{2}<br>{3}'.format(name, row['joined_year'], row['joined_team_name'],
                                                row['prev_team_name'])
        index = 4 * i
        name2label[name] = label
        name2index[name] = index
    LOGGER.debug(f'plot {len(player_df)} players')

    df = df.copy()
    df['name_index'] = df['player_name'].map(lambda x: name2index[x])
    df['y'] = df['name_index'] + df['league_id']

    fig = px.scatter(df, x='rookie_year', y='y', size='minutes',
                     color='league',
                     category_orders={'league': ['J1', 'J2', 'J3']},
                     hover_data=['team_name', 'minutes', 'apps', 'goals'])
    fig.update_yaxes(range=[4 * len(name2index) + 1, 0])
    fig.update_xaxes(range=[0.5, 7.5])
    fig.update_traces(marker=dict(
        sizemode='area',
        sizeref=2. * 90 * 40 / (30. ** 2)  # https://plotly.com/python/bubble-charts/
    ))

    tick_texts = []
    tick_vals = []
    for name in name2index:
        tick_texts.append(name2label[name])
        tick_vals.append(name2index[name] + 2)

    fig.update_layout(
        autosize=False,
        width=800,
        height=max(500, len(name2index) * 100),
        yaxis=dict(
            title_text='',
            ticktext=tick_texts,
            tickvals=tick_vals
        )
    )
    return fig


def bar_plot_player_count(df):
    player_count = defaultdict(int)  # key: (year, league_id)
    for _, row in df.iterrows():
        key = (row['joined_year'], row['joined_league_id'])
        player_count[key] += 1
    records = []
    for year in range(2015, 2022):
        for league_id in range(1, 4):
            records.append({
                'year': year,
                'league': f'J{league_id}',
                'player_count': player_count[(year, league_id)]
            })

    count_df = pd.DataFrame(records)
    fig = px.bar(count_df, x="year", y="player_count", color="league",
                 category_orders={'league': ['J1', 'J2', 'J3']})
    return fig
