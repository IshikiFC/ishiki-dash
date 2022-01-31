import dash_bootstrap_components as dbc

STYLE_DROPBOX = {'width': '100%', 'maxWidth': '250px', 'margin': '3px'}
STYLE_SLIDER = {'width': 500, 'margin': 10}
STYLE_CONTAINER = {'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'wrap', 'justify-content': 'center'}
STYLE_RADIO_LABEL = {'padding': '10px', 'margin': 'auto'}
STYLE_RADIO_INPUT = {'margin': '3px'}
STYLE_CELL = {'whiteSpace': 'normal', 'height': 'auto'}
STYLE_HEADER = {'fontWeight': 'bold', 'textAlign': 'center'}

TITLE = 'J.LEAGUE Rookie Stats Viewer'
DESCRIPTION = 'Jリーグの新人選手の出場記録をインタラクティブに可視化するダッシュボードです。'
IMAGE = 'https://ishiki-dash.s3.ap-northeast-1.amazonaws.com/dashboard.png'

META_TAGS = [
    {'name': 'description', 'content': DESCRIPTION},
    {'property': 'og:type', 'content': 'website'},
    {'property': 'og:title', 'content': TITLE},
    {'property': 'og:description', 'content': DESCRIPTION},
    {'property': 'og:image', 'content': IMAGE},
    {'name': 'twitter:card', 'content': 'summary'},
    {'name': 'twitter:title', 'content': TITLE},
    {'name': 'twitter:description', 'content': DESCRIPTION}
]


def wrap_with_card(content):
    return dbc.Card(
        dbc.CardBody(content)
    )
