# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from logging import getLogger

import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html

LOGGER = getLogger(__name__)

app = dash.Dash(__name__)

rookie_df = pd.read_csv('./data/rookies.csv')
rookie_df = rookie_df.rename(
    columns={'year': 'joined_year', 'league': 'joined_league', 'team_name': 'joined_team_name'})

stats_df = pd.read_csv('./data/stats.csv')
stats_df['league'] = stats_df['league_id'].map(lambda x: f'J{x}')

plot_df = pd.merge(
    rookie_df[['player_name', 'joined_year', 'joined_team_name', 'joined_league', 'prev_team_name', 'birth']],
    stats_df[['player_name', 'year', 'league_id', 'league', 'team_name', 'apps', 'minutes', 'goals']],
    on='player_name'
)
plot_df['rookie_year'] = plot_df['year'] - plot_df['joined_year'] + 1


def do_plot(df):
    name2label = dict()
    name2index = dict()
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
    app.logger.debug(f'plot {len(player_df)} players')

    df = df.copy()
    df['name_index'] = df['player_name'].map(lambda x: name2index[x])
    df['y'] = df['name_index'] + df['league_id']

    fig = px.scatter(df, x='rookie_year', y='y', size='minutes',
                     color='league',
                     category_orders={'league': ['J1', 'J2', 'J3']},
                     hover_data=['team_name', 'apps', 'goals'])
    fig.update_yaxes(range=[4 * len(name2index) + 1, 0])
    fig.update_xaxes(range=[0.5, 7.5])

    tick_texts = []
    tick_vals = []
    for name in name2index:
        tick_texts.append(name2label[name])
        tick_vals.append(name2index[name] + 2)

    fig.update_layout(
        autosize=False,
        width=500,
        height=max(500, len(name2index) * 100),
        yaxis=dict(
            title_text='',
            ticktext=tick_texts,
            tickvals=tick_vals
        )
    )
    return fig


def get_mask(df, years=None, leagues=None, teams=None):
    mask = np.ones(len(df)).astype(bool)
    if years:
        mask &= df['joined_year'].isin(years)
    if leagues:
        mask &= df['joined_league'].isin(leagues)
    if teams:
        mask &= df['joined_team_name'].isin(teams)
    return mask


app.layout = html.Div([
    dcc.Graph(
        id='example-graph',
        figure=do_plot(plot_df[get_mask(plot_df, years=[2015])])
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
