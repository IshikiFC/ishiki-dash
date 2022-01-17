import math

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, Output, Input, dash_table, html

from mydash.figures import do_scatter_plot_play_time, do_bar_plot_player_count, do_scatter_plot_avg_play_time, \
    do_histogram_play_time
from mydash.utils.categorize import TeamCategory

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

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
category_options = [{'label': x.value, 'value': x.name} for x in TeamCategory]
position_options = [{'label': x, 'value': x} for x in ['GK', 'DF', 'MF', 'FW']]

dropbox_style = {'width': '100%', 'maxWidth': '250px', 'margin': '3px'}
input_style = {'width': 100, 'marginLeft': 10, 'marginRight': 10, 'marginTop': 'auto', 'marginBottom': 'auto'}
slider_style = {'width': 500, 'margin': 10}


def wrap_with_card(content):
    return html.Div([
        dbc.Card(
            dbc.CardBody(content)
        )
    ])


selector_container = dbc.Row(
    id='selector-container',
    children=[
        dcc.Dropdown(id='joined-team-dropdown', placeholder='加入チーム', options=joined_team_options,
                     multi=True, style=dropbox_style),
        dcc.Dropdown(id='prev-team-dropdown', placeholder='前所属チーム', options=prev_team_options,
                     multi=True, style=dropbox_style),
        dcc.Dropdown(id='joined-league-dropdown', placeholder='加入リーグ', options=league_options,
                     multi=True, style=dropbox_style),
        dcc.Dropdown(id='prev-category-dropdown', placeholder='前所属カテゴリ', options=category_options,
                     multi=True, style=dropbox_style),
        dcc.Dropdown(id='position-dropdown', placeholder='ポジション', options=position_options,
                     multi=True, style=dropbox_style),
        html.Div(
            id='joined-year-range-slider-container',
            children=[
                dcc.RangeSlider(
                    id='joined-year-range-slider', min=2015, max=2021, value=[2015, 2021],
                    marks={i: str(i) for i in range(2015, 2022)})],
            style=slider_style
        ),
    ],
    style={'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'wrap', 'justify-content': 'center'}
)

col2label = {
    'player_name': 'Name',
    'joined_year': 'Year',
    'joined_league': 'League',
    'joined_team_name': 'Team',
    'prev_team_name': 'Prev.',
    'position': 'Position',
}

player_container = html.Div(
    id='player-container',
    children=[
        html.Div(
            id='player-table-container',
            children=dash_table.DataTable(
                id='player-table',
                columns=[{'name': label, 'id': col} for col, label in col2label.items()],
                page_current=0,
                page_size=5,
                page_action='custom',
                style_cell={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                }
            ),
        ),
        html.Div(id='player-graph-container'),
    ]
)

agg_container = html.Div(
    id='agg-container',
    children=[
        html.Div(id='player-count-graph-container'),
        html.Div(id='avg-player-graph-container'),
        html.Div(id='play-time-histogram-container')
    ]
)

app.layout = dbc.Container(
    [
        html.Div(selector_container, className='bg-light'),
        dbc.Row(
            [
                html.Div(player_container, className='col-xl-6'),
                html.Div(agg_container, className='col-xl-6')
            ]
        ),
        dcc.Store(id='filtered-rookie-json')
    ],
    fluid=True
)


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


@app.callback(
    Output('filtered-rookie-json', 'data'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value'),
    Input('joined-league-dropdown', 'value'),
    Input('prev-category-dropdown', 'value'),
    Input('position-dropdown', 'value'),
    Input('joined-year-range-slider', 'value')
)
def update_matched_rookie_df(joined_teams, prev_teams, joined_league_ids, prev_categories, positions,
                             joined_year_range):
    f_rookie_df = filter_rookie_df(rookie_df, joined_teams=joined_teams, prev_teams=prev_teams,
                                   joined_league_ids=joined_league_ids,
                                   prev_categories=prev_categories, positions=positions,
                                   joined_year_range=joined_year_range)
    return f_rookie_df.to_json(orient='split')


@app.callback(
    Output('player-table', 'data'),
    Output('player-table', 'page_count'),
    Input('filtered-rookie-json', 'data'),
    Input('player-table', 'page_current'),
    Input('player-table', 'page_size'),
    prevent_initial_call=True
)
def update_player_table(filtered_rookie_json, page_current, page_size):
    f_rookie_df = pd.read_json(filtered_rookie_json, orient='split')
    records = f_rookie_df.iloc[page_current * page_size:(page_current + 1) * page_size].to_dict('records')
    page_count = math.ceil(len(f_rookie_df) / page_size)
    return [records, page_count]


@app.callback(
    Output('player-graph-container', 'children'),
    Input('player-table', 'data'),
    prevent_initial_call=True
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
    return wrap_with_card(dcc.Graph(id='player-graph', figure=fig))


@app.callback(
    Output('player-count-graph-container', 'children'),
    Input('filtered-rookie-json', 'data'),
    prevent_initial_call=True
)
def update_player_count_graph(filtered_rookie_json):
    f_rookie_df = pd.read_json(filtered_rookie_json, orient='split')
    fig = do_bar_plot_player_count(f_rookie_df)
    return wrap_with_card(dcc.Graph(id='player-count-graph', figure=fig))


@app.callback(
    Output('avg-player-graph-container', 'children'),
    Input('filtered-rookie-json', 'data'),
    prevent_initial_call=True
)
def update_avg_player_graph(filtered_rookie_json):
    f_rookie_df = pd.read_json(filtered_rookie_json, orient='split')
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')
    fig = do_scatter_plot_avg_play_time(f_rookie_df, f_stats_df)
    return wrap_with_card(dcc.Graph(id='avg-player-graph', figure=fig))


@app.callback(
    Output('play-time-histogram-container', 'children'),
    Input('filtered-rookie-json', 'data'),
    prevent_initial_call=True
)
def update_play_time_histogram(filtered_rookie_json):
    rookie_year = 1
    f_rookie_df = pd.read_json(filtered_rookie_json, orient='split')
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')
    f_stats_df = f_stats_df[f_stats_df['rookie_year'] == rookie_year]
    fig = do_histogram_play_time(f_stats_df)
    return wrap_with_card(dcc.Graph(id='avg-player-graph', figure=fig))


if __name__ == '__main__':
    app.run_server(debug=True)
