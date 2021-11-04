import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


# Connect to main app.py file
from app import app
from app import server


# Connect to your app pages
from tabs import simulation_tab#, analysis_tab, home_tab
path_to_R = "C:\\Program Files\\R\\R-4.0.3\\bin\\Rscript.exe"
simulation_tab.path_to_R = path_to_R


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Simulation", href="/tabs/simulation")),
            dbc.NavItem(dbc.NavLink("Analysis", href="/tabs/analysis")),
        ],
        brand="Epidemic Outbreak Predictor",
        brand_href="/tab/home",
        color="primary",
        dark=True,
    ),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/tabs/simulation':
        return simulation_tab.layout
    if pathname == '/tabs/analysis':
        return analysis_tab.layout
    else:
        return "404 Page Error! Please choose a link"


if __name__ == '__main__':
    app.run_server(debug=True)
