# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import math

import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc, Output, Input, dash_table
from dash import html

app = dash.Dash(__name__)

rookie_df = pd.read_csv('./data/rookies.csv')
rookie_df = rookie_df.rename(
    columns={'year': 'joined_year', 'league': 'joined_league', 'team_name': 'joined_team_name'})
joined_teams = list(rookie_df['joined_team_name'].unique())
prev_teams = list(rookie_df['prev_team_name'].unique())

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
    df['size'] = df['minutes'] ** (1 / 2)

    fig = px.scatter(df, x='rookie_year', y='y', size='size',
                     color='league',
                     category_orders={'league': ['J1', 'J2', 'J3']},
                     hover_data=['team_name', 'minutes', 'apps', 'goals'])
    fig.update_yaxes(range=[4 * len(name2index) + 1, 0])
    fig.update_xaxes(range=[0.5, 7.5])

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


def get_mask(df, years=None, leagues=None, teams=None, players=None):
    mask = np.ones(len(df)).astype(bool)
    if years:
        mask &= df['joined_year'].isin(years)
    if leagues:
        mask &= df['joined_league'].isin(leagues)
    if teams:
        mask &= df['joined_team_name'].isin(teams)
    if players:
        mask &= df['player_name'].isin(players)
    return mask


app.layout = html.Div([
    html.Div(
        id='selector-container',
        children=[
            dcc.Dropdown(
                id='joined-team-dropdown',
                placeholder='加入チームを選択',
                options=[{'label': t, 'value': t} for t in joined_teams],
                multi=True,
                style={'width': 250, 'margin': 10}
            ),
            dcc.Dropdown(
                id='prev-team-dropdown',
                placeholder='前所属チームを選択',
                options=[{'label': t, 'value': t} for t in prev_teams],
                multi=True,
                style={'width': 250, 'margin': 10}
            ),
            dcc.Input(
                id='page-size-input',
                type='number',
                min=1,
                max=100,
                value=5,
                style={'width': 100, 'height': 30, 'marginLeft': 10, 'marginTop': 'auto', 'marginBottom': 'auto'}
            )
        ],
        style={'display': 'flex', 'flex-direction': 'row'}),

    html.Div(
        id='player-table-container',
        children=[dash_table.DataTable(
            id='player-table',
            columns=[
                {"name": i, "id": i} for i in
                ['player_name', 'joined_year', 'joined_league', 'joined_team_name', 'prev_team_name']
            ],
            page_current=0,
            page_action='custom'
        )],
        style={'width': 800}
    ),

    html.Div(
        id='player-graph-container'
    ),
])


@app.callback(
    Output('player-table', "data"),
    Output('player-table', 'page_count'),
    Input('joined-team-dropdown', 'value'),
    Input('player-table', "page_current"),
    Input('page-size-input', "value"),
)
def update_player_table(selected_joined_teams, page_current, page_size):
    if selected_joined_teams:
        df = rookie_df[rookie_df['joined_team_name'].isin(selected_joined_teams)]
    else:
        df = rookie_df

    records = df.iloc[page_current * page_size:(page_current + 1) * page_size] \
        .to_dict('records')
    page_count = math.ceil(len(df) / page_size)

    return [records, page_count]


@app.callback(
    Output('player-graph-container', 'children'),
    Input('player-table', "data"),
)
def update_player_graph(rows):
    player_names = [row['player_name'] for row in rows]
    mask = get_mask(plot_df, players=player_names)
    return [
        dcc.Graph(
            id='player-graph',
            figure=do_plot(plot_df[mask])
        ),
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
