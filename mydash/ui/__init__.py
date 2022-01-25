import dash_bootstrap_components as dbc

STYLE_DROPBOX = {'width': '100%', 'maxWidth': '250px', 'margin': '3px'}
STYLE_SLIDER = {'width': 500, 'margin': 10}
STYLE_CONTAINER = {'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'wrap', 'justify-content': 'center'}
STYLE_RADIO_LABEL = {'padding': '10px', 'margin': 'auto'}
STYLE_RADIO_INPUT = {'margin': '3px'}
STYLE_CELL = {'whiteSpace': 'normal', 'height': 'auto'}
STYLE_HEADER = {'fontWeight': 'bold', 'textAlign': 'center'}


def wrap_with_card(content):
    return dbc.Card(
        dbc.CardBody(content)
    )
