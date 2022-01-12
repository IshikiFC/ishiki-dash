# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import math

import dash
import pandas as pd
from dash import dcc, Output, Input, dash_table
from dash import html

from mydash.figures import do_scatter_plot_play_time, do_bar_plot_player_count, do_scatter_plot_avg_play_time, \
    do_histogram_play_time

app = dash.Dash(__name__)

rookie_df = pd.read_csv('./data/rookies.csv')
rookie_df = rookie_df.rename(
    columns={'year': 'joined_year', 'league': 'joined_league_id', 'team_name': 'joined_team_name'})
rookie_df['joined_league'] = rookie_df['joined_league_id'].map(lambda x: f'J{x}')
rookie_df['player_label'] = rookie_df.apply(lambda x: '{0}({1})<br>{2}<br>{3}'.format(
    x['player_name'], x['joined_year'], x['joined_team_name'], x['prev_team_name']), axis=1)
rookie_df['current_year'] = 2021 - rookie_df['joined_year'] + 1

stats_df = pd.read_csv('./data/stats.csv')
stats_df['league'] = stats_df['league_id'].map(lambda x: f'J{x}')
stats_df = pd.merge(stats_df, rookie_df[['player_name', 'joined_year']], on='player_name')
stats_df['rookie_year'] = stats_df['year'] - stats_df['joined_year'] + 1
stats_df['stats_label'] = stats_df.apply(lambda x: '{0}({1})'.format(x['team_name'], x['year']), axis=1)

joined_teams = list(rookie_df['joined_team_name'].unique())
prev_teams = list(rookie_df['prev_team_name'].unique())

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
            ),
            dcc.Input(
                id='rookie-year-input',
                type='number',
                min=1,
                max=7,
                value=1,
                style={'width': 100, 'height': 30, 'marginLeft': 10, 'marginTop': 'auto', 'marginBottom': 'auto'}
            )
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
                    html.Div(
                        id='player-graph-container'
                    ),
                ],
                style={'width': 800, 'margin': 50}
            ),
            html.Div(
                id='agg-container',
                children=[
                    html.Div(
                        id='player-count-graph-container',
                    ),
                    html.Div(
                        id='avg-player-graph-container'
                    ),
                    html.Div(
                        id='play-time-histogram-container'
                    )
                ],
                style={'width': 800, 'margin': 50}
            ),
        ],
        style={'display': 'flex', 'flex-direction': 'row'}
    )
])


def filter_rookie_df(df, selected_joined_teams=None, selected_prev_teams=None, player_names=None):
    if selected_joined_teams:
        df = df[df['joined_team_name'].isin(selected_joined_teams)]
    if selected_prev_teams:
        df = df[df['prev_team_name'].isin(selected_prev_teams)]
    if player_names:
        df = df[df['player_name'].isin(player_names)]
    return df


@app.callback(
    Output('player-table', 'data'),
    Output('player-table', 'page_count'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value'),
    Input('player-table', 'page_current'),
    Input('page-size-input', 'value'),
)
def update_player_table(selected_joined_teams, selected_prev_teams, page_current, page_size):
    f_rookie_df = filter_rookie_df(rookie_df, selected_joined_teams, selected_prev_teams)
    records = f_rookie_df.iloc[page_current * page_size:(page_current + 1) * page_size] \
        .to_dict('records')
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
    return [
        dcc.Graph(
            id='player-graph',
            figure=fig
        ),
    ]


@app.callback(
    Output('player-count-graph-container', 'children'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value')
)
def update_player_count_graph(selected_joined_teams, selected_prev_teams):
    f_rookie_df = filter_rookie_df(rookie_df, selected_joined_teams, selected_prev_teams)
    fig = do_bar_plot_player_count(f_rookie_df)
    return [
        dcc.Graph(
            id='player-count-graph',
            figure=fig
        )
    ]


@app.callback(
    Output('avg-player-graph-container', 'children'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value')
)
def update_avg_player_graph(selected_joined_teams, selected_prev_teams):
    f_rookie_df = filter_rookie_df(rookie_df, selected_joined_teams, selected_prev_teams)
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')
    fig = do_scatter_plot_avg_play_time(f_rookie_df, f_stats_df)
    return [
        dcc.Graph(
            id='avg-player-graph',
            figure=fig
        )
    ]


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
    return [
        dcc.Graph(
            id='avg-player-graph',
            figure=fig
        )
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
