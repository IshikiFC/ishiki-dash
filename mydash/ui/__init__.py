import dash_bootstrap_components as dbc
from dash import html

STYLE_DROPBOX = {'width': '100%', 'maxWidth': '250px', 'margin': '3px'}
STYLE_SLIDER = {'width': 500, 'margin': 10}
STYLE_CONTAINER = {'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'wrap', 'justify-content': 'center'}
STYLE_CELL = {'whiteSpace': 'normal', 'height': 'auto'}
STYLE_HEADER = {'fontWeight': 'bold', 'textAlign': 'center'}


def wrap_with_card(content):
    return html.Div([
        dbc.Card(
            dbc.CardBody(content)
        )
    ])
