# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import math

import dash
import numpy as np
import pandas as pd
from dash import dcc, Output, Input, dash_table
from dash import html

from mydash.figures import do_scatter_plot_play_time, do_bar_plot_player_count, do_scatter_plot_avg_play_time, \
    do_histogram_play_time
from mydash.utils.categorize import TeamCategory

app = dash.Dash(__name__)

rookie_df = pd.read_csv('./data/rookie.csv')
rookie_df = rookie_df.rename(
    columns=dict([(col, f'joined_{col}') for col in ['year', 'league_id', 'team_name']])
)
rookie_df['joined_league'] = rookie_df['joined_league_id'].map(lambda x: f'J{x}')
rookie_df['player_label'] = rookie_df.apply(lambda x: '{0}({1})<br>{2}<br>{3}'.format(
    x['player_name'], x['joined_year'], x['joined_team_name'], x['prev_team_name']), axis=1)
rookie_df['cur_rookie_year'] = 2021 - rookie_df['joined_year'] + 1

stats_df = pd.read_csv('./data/stats_rookie.csv')
stats_df['league'] = stats_df['league_id'].map(lambda x: f'J{x}')
stats_df = pd.merge(stats_df, rookie_df[['player_name', 'joined_year']], on='player_name')
stats_df['rookie_year'] = stats_df['year'] - stats_df['joined_year'] + 1
stats_df['stats_label'] = stats_df.apply(lambda x: '{0}({1})'.format(x['team_name'], x['year']), axis=1)

joined_team_options = [{'label': x, 'value': x} for x in rookie_df['joined_team_name'].unique()]
prev_team_options = [{'label': x, 'value': x} for x in rookie_df['prev_team_name'].unique()]
league_options = [{'label': f'J{x}', 'value': x} for x in [1, 2, 3]]
position_options = [{'label': x, 'value': x} for x in ['GK', 'DF', 'MF', 'FW']]
category_options = [[{'label': x.value, 'value': x.name} for x in TeamCategory]]

app.layout = html.Div([
    html.Div(
        id='selector-container',
        children=[
            dcc.Dropdown(id='joined-team-dropdown', placeholder='加入チームを選択', options=joined_team_options,
                         multi=True, style={'width': 250, 'margin': 10}),
            dcc.Dropdown(id='prev-team-dropdown', placeholder='前所属チームを選択', options=prev_team_options,
                         multi=True, style={'width': 250, 'margin': 10}),
            dcc.Dropdown(id='joined-league-dropdown', placeholder='加入リーグを選択', options=league_options,
                         multi=True, style={'width': 250, 'margin': 10}),
            dcc.Dropdown(id='prev-category-dropdown', placeholder='全所属カテゴリを選択', options=category_options,
                         multi=True, style={'width': 250, 'margin': 10}),
            dcc.Dropdown(id='position-dropdown', placeholder='加入時ポジションを選択', options=position_options,
                         multi=True, style={'width': 250, 'margin': 10}),
            dcc.Input(id='page-size-input', type='number', min=1, max=100, value=5,
                      style={'width': 100, 'height': 30, 'marginLeft': 10, 'marginTop': 'auto',
                             'marginBottom': 'auto'}),
            dcc.Input(id='rookie-year-input', type='number', min=1, max=7, value=1,
                      style={'width': 100, 'height': 30, 'marginLeft': 10, 'marginTop': 'auto', 'marginBottom': 'auto'})
        ],
        style={'display': 'flex', 'flex-direction': 'row'}
    ),

    html.Div(
        id='two-pane-container',
        children=[
            html.Div(
                id='player-container',
                children=[
                    html.Div(
                        id='player-table-container',
                        children=[dash_table.DataTable(
                            id='player-table',
                            columns=[
                                {'name': i, 'id': i} for i in
                                ['player_name', 'joined_year', 'joined_league_id', 'joined_team_name', 'prev_team_name']
                            ],
                            page_current=0,
                            page_action='custom'
                        )],
                        style={'width': 600}
                    ),
                    html.Div(id='player-graph-container'),
                ],
                style={'width': 800, 'margin': 50}
            ),
            html.Div(
                id='agg-container',
                children=[
                    html.Div(id='player-count-graph-container'),
                    html.Div(id='avg-player-graph-container'),
                    html.Div(id='play-time-histogram-container')
                ],
                style={'width': 800, 'margin': 50}
            ),
        ],
        style={'display': 'flex', 'flex-direction': 'row'}
    )
])


def filter_rookie_df(df, joined_teams=None, prev_teams=None, player_names=None,
                     joined_league_ids=None, positions=None, prev_categories=None):
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
    return df[mask]


@app.callback(
    Output('player-table', 'data'),
    Output('player-table', 'page_count'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value'),
    Input('joined-league-dropdown', 'value'),
    Input('prev-category-dropdown', 'value'),
    Input('position-dropdown', 'value'),
    Input('player-table', 'page_current'),
    Input('page-size-input', 'value'),
)
def update_player_table(joined_teams, prev_teams, joined_league_ids, prev_categories, positions,
                        page_current, page_size):
    f_rookie_df = filter_rookie_df(rookie_df, joined_teams=joined_teams, prev_teams=prev_teams,
                                   joined_league_ids=joined_league_ids,
                                   prev_categories=prev_categories, positions=positions)
    records = f_rookie_df.iloc[page_current * page_size:(page_current + 1) * page_size].to_dict('records')
    page_count = math.ceil(len(f_rookie_df) / page_size)

    return [records, page_count]


@app.callback(
    Output('player-graph-container', 'children'),
    Input('player-table', 'data'),
)
def update_player_graph(rows):
    player_names = [row['player_name'] for row in rows]
    f_rookie_df = filter_rookie_df(rookie_df, player_names=player_names)
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')

    fig = do_scatter_plot_play_time(
        f_rookie_df,
        f_stats_df,
        hover_name='stats_label',
        hover_data={'minutes': True, 'apps': True, 'goals': True,
                    'rookie_year': False, 'y': False, 'league': False}
    )
    return [dcc.Graph(id='player-graph', figure=fig)]


@app.callback(
    Output('player-count-graph-container', 'children'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value')
)
def update_player_count_graph(selected_joined_teams, selected_prev_teams):
    f_rookie_df = filter_rookie_df(rookie_df, selected_joined_teams, selected_prev_teams)
    fig = do_bar_plot_player_count(f_rookie_df)
    return [dcc.Graph(id='player-count-graph', figure=fig)]


@app.callback(
    Output('avg-player-graph-container', 'children'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value')
)
def update_avg_player_graph(selected_joined_teams, selected_prev_teams):
    f_rookie_df = filter_rookie_df(rookie_df, selected_joined_teams, selected_prev_teams)
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')
    fig = do_scatter_plot_avg_play_time(f_rookie_df, f_stats_df)
    return [dcc.Graph(id='avg-player-graph', figure=fig)]


@app.callback(
    Output('play-time-histogram-container', 'children'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value'),
    Input('rookie-year-input', 'value'),
)
def update_play_time_histogram(selected_joined_teams, selected_prev_teams, rookie_year):
    f_rookie_df = filter_rookie_df(rookie_df, selected_joined_teams, selected_prev_teams)
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')
    f_stats_df = f_stats_df[f_stats_df['rookie_year'] == rookie_year]
    fig = do_histogram_play_time(f_stats_df)
    return [dcc.Graph(id='avg-player-graph', figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
