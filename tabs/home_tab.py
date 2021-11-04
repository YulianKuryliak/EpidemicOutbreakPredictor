import dash_html_components as html
from dash.dependencies import Input, Output
import pathlib

from app import app

# get relative data folder
PATH = pathlib.Path(__file__).parent

layout = html.Div([
    html.H1('Welcome to home', style={"textAlign": "center"}),
])


