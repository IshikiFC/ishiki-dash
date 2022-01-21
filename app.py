import math
from logging import getLogger

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, Output, Input, dash_table, html

from mydash.figures import do_scatter_plot_play_time, do_bar_plot_player_count, do_histogram_play_time
from mydash.ui import wrap_with_card, STYLE_CELL, STYLE_HEADER, STYLE_DROPBOX, STYLE_SLIDER, STYLE_CONTAINER
from mydash.utils.categorize import TeamCategory
from mydash.utils.constants import FIRST_YEAR, LAST_YEAR
from mydash.utils.df import filter_rookie_df, get_avg_stats_df, load_rookie_df, load_stats_df

LOGGER = getLogger(__name__)

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

rookie_df = load_rookie_df()
stats_df = load_stats_df(rookie_df)

joined_team_options = [{'label': x, 'value': x} for x in rookie_df['joined_team_name'].unique()]
prev_team_options = [{'label': x, 'value': x} for x in rookie_df['prev_team_name'].unique()]
league_options = [{'label': f'J{x}', 'value': x} for x in [1, 2, 3]]
category_options = [{'label': x.value, 'value': x.name} for x in TeamCategory]
position_options = [{'label': x, 'value': x} for x in ['GK', 'DF', 'MF', 'FW']]

table_columns = {
    'player_name': 'Name',
    'joined_year': 'Year',
    'joined_league': 'League',
    'joined_team_name': 'Team',
    'prev_team_name': 'Prev.',
    'position': 'Position',
}
table_columns = [{'id': col, 'name': label} for col, label in table_columns.items()]

selector_container = dbc.Row(
    children=[
        dcc.Dropdown(id='joined-team-dropdown', placeholder='加入チーム', options=joined_team_options,
                     multi=True, style=STYLE_DROPBOX),
        dcc.Dropdown(id='prev-team-dropdown', placeholder='前所属チーム', options=prev_team_options,
                     multi=True, style=STYLE_DROPBOX),
        dcc.Dropdown(id='joined-league-dropdown', placeholder='加入リーグ', options=league_options,
                     multi=True, style=STYLE_DROPBOX),
        dcc.Dropdown(id='prev-category-dropdown', placeholder='前所属カテゴリ', options=category_options,
                     multi=True, style=STYLE_DROPBOX),
        dcc.Dropdown(id='position-dropdown', placeholder='ポジション', options=position_options,
                     multi=True, style=STYLE_DROPBOX),
        html.Div(
            dcc.RangeSlider(
                id='joined-year-range-slider', min=FIRST_YEAR, max=LAST_YEAR, value=[FIRST_YEAR, LAST_YEAR],
                marks={i: str(i) for i in range(FIRST_YEAR, LAST_YEAR + 1)}
            ),
            style=STYLE_SLIDER
        ),
    ],
    style=STYLE_CONTAINER
)

player_container = html.Div([
    html.Div(wrap_with_card(dash_table.DataTable(
        id='player-table',
        columns=table_columns,
        page_current=0,
        page_size=5,
        page_action='custom',
        style_cell=STYLE_CELL,
        style_header=STYLE_HEADER
    ))),
    html.Div(wrap_with_card(dcc.Graph(
        id='play-time-plot',
        hoverData=None
    ))),
])

summary_container = html.Div([
    html.Div(wrap_with_card(dcc.Graph(
        id='player-count-plot'
    ))),
    html.Div(wrap_with_card(dcc.Graph(
        id='play-time-histogram'
    )))
])

app.layout = dbc.Container(
    children=[
        html.Div(selector_container, className='bg-light'),
        dbc.Row([
            html.Div(player_container, className='col-lg-6'),
            html.Div(summary_container, className='col-lg-6')
        ]),
        dcc.Store(id='filtered-rookie-json')
    ],
    fluid=True
)


@app.callback(
    Output('filtered-rookie-json', 'data'),
    Input('joined-team-dropdown', 'value'),
    Input('prev-team-dropdown', 'value'),
    Input('joined-league-dropdown', 'value'),
    Input('prev-category-dropdown', 'value'),
    Input('position-dropdown', 'value'),
    Input('joined-year-range-slider', 'value')
)
def update_filtered_rookie_json(joined_teams, prev_teams, joined_league_ids, prev_categories, positions,
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
    Output('play-time-plot', 'figure'),
    Input('filtered-rookie-json', 'data'),
    Input('player-table', 'data'),
    prevent_initial_call=True
)
def update_play_time_plot(filtered_rookie_json, table_records):
    # calculate AVG stats
    f_rookie_df = pd.read_json(filtered_rookie_json, orient='split')
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')
    avg_stats_df = get_avg_stats_df(f_rookie_df, f_stats_df)

    # build data frames for AVG player
    player_name = 'Avg.'
    d_rookie_df = pd.DataFrame([{'player_name': player_name, 'player_label': player_name}])
    d_stats_df = avg_stats_df
    d_stats_df['player_name'] = player_name
    d_stats_df['stats_label'] = player_name
    d_stats_df['league'] = d_stats_df['league_id'].map(lambda x: f'J{x}')

    # build data frames for table records
    player_names = [record['player_name'] for record in table_records]
    t_rookie_df = filter_rookie_df(f_rookie_df, player_names=player_names)
    t_stats_df = pd.merge(stats_df, t_rookie_df['player_name'], on='player_name')

    # concat data frames for plotting
    p_rookie_df = d_rookie_df.append(t_rookie_df)
    p_stats_df = d_stats_df.append(t_stats_df)

    fig = do_scatter_plot_play_time(
        p_rookie_df,
        p_stats_df,
        hover_name='stats_label',
        hover_data={'minutes': ':.1f', 'apps': ':.1f', 'goals': ':.1f',
                    'rookie_year': False, 'y': False, 'league': False}
    )
    return fig


@app.callback(
    Output('player-count-plot', 'figure'),
    Input('filtered-rookie-json', 'data'),
    prevent_initial_call=True
)
def update_player_count_plot(filtered_rookie_json):
    f_rookie_df = pd.read_json(filtered_rookie_json, orient='split')
    fig = do_bar_plot_player_count(f_rookie_df)
    return fig


@app.callback(
    Output('play-time-histogram', 'figure'),
    Input('filtered-rookie-json', 'data'),
    Input('play-time-plot', 'hoverData'),
    prevent_initial_call=True
)
def update_play_time_histogram(filtered_rookie_json, hover_data):
    if hover_data:
        point = hover_data['points'][0]
        rookie_year = point['x']
        league_id = point['y'] % 4
    else:
        rookie_year = 1
        league_id = 1

    f_rookie_df = pd.read_json(filtered_rookie_json, orient='split')
    f_stats_df = pd.merge(stats_df, f_rookie_df['player_name'], on='player_name')
    f_stats_df = f_stats_df[f_stats_df['rookie_year'] == rookie_year]
    f_stats_df = f_stats_df[f_stats_df['league_id'] == league_id]
    fig = do_histogram_play_time(f_stats_df)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
