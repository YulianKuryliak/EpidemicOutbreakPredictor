import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_daq as daq
import dash_table as dt
from dash.dependencies import Input, Output, State, MATCH, ALL
import pathlib
import pandas as pd
import plotly
import plotly.express as px
from app import app

from scripts import analysis

data_simulation1 = analysis.mean("E:\\Managing epidemic outbreak\\task6\\output_data\\simulations\\size 200, start_infected 1, infection_rates 0.15, time_step 1, time_max 100, network_type barabasi, amount_of_edges 2, virus_types 1 death_rate_type same, prob_reconnection 0")
data_simulation2 = analysis.mean("E:\\Managing epidemic outbreak\\task6\\output_data\\simulations\\size 200, start_infected 1, infection_rates 0.2, time_step 1, time_max 100, network_type barabasi, amount_of_edges 2, virus_types 1 death_rate_type same, prob_reconnection 0")
print("\n\n\n\nhello\n\n\n\n")
print(data_simulation1)


log_df = pd.read_csv('E:/PreRelease/assets/data/data_actions_0.csv')
log_df = log_df.drop([log_df.columns[0], 'virus_type'],1)
data_df = pd.read_csv('E:/PreRelease/assets/data/data_0.csv')
new_data_df = pd.melt(data_df, id_vars=['time'], value_vars=["infected","dead","critically_infected","susceptible"])

epidemiological_models = ["SIR", "SI", "SIS", "SEIR"]
chosen_epidemiological_model = epidemiological_models[0]
network_models = ["Complete", "Barabasi-Albert", "Erdos-Renyi", "Watts-Strogatz"]
chosen_network_model = network_models[0]

#parameters for simmulation
epidemiological_parameters = []
network_parameters = []
other_parameters = ["Size", "Infection_rate", "Maximum_simulation_time", "Time_of_data_collection", "start_infected", "number_of_simulations"]
total_fields = []
inputed_parameters = {
    "epidemiological_model" : "",
    "network_model" : "",
    "Size" : "",
    "Infection_rate" : "",
    "Maximum_simulation_time" : "",
    "Time_of_data_collection" : "",
    "start_infected" : "",
    'number_of_edges' : 0,
    'reconection_coefitient' : 0,
    'Treatment_Period' : "",
    'Critically_Treatment_Period' : "",
    'number_of_simulations' : 1,
    'Criticaly_infection_rate' : "different",
}

amounts_of_nodes = [50, 100, 200, 500]
death_rates = ["different", "same"]

threatment_times = [10]
critically_threatment_times = [14]
initial_amounts_of_edges = [1,2,4,5,10]


# get relative data folder
PATH = pathlib.Path(__file__).parent


layout = html.Div([
    #html.H1('Welcome to analysis', style={"textAlign": "center"}),
    html.P(),
    html.Div([
        html.H5("Select kind of analysis", style={"textAlign": "center"}),
        dcc.Dropdown(
            options=[
                {'label': death_rate, 'value': death_rate} for death_rate in ["Separated analysis of each of the results", "Average values", "Analysis of amount of peak infected nodes"]
            ],
        ),
    ], style = {'width':"25%", 'margin': 'auto'}),
    html.P(),

    
    dbc.Table(
        html.Tbody([
            html.Tr([
                html.Td(
                    html.Div(children="Select epidemiological model"),
                ),
                html.Td(
                    html.Div(children="Select network model"),
                ),
                html.Td(
                    html.Div(children="Select amount of nodes"),
                ),
                html.Td(
                    html.Div(children="Select critically infection rate"),
                ),
            ]),

            #first parameters
            html.Tr([
                html.Td(
                    dcc.Dropdown(
                        id="dropdown_epidemiological_model",
                        #label=chosen_epidemiological_model,
                        options=[
                            {'label': epidemiological_model, 'value': epidemiological_model} for epidemiological_model in epidemiological_models
                        ],
                        #value = "chosen_epidemiological_model"
                    ),
                ), 
                html.Td(
                    dcc.Dropdown(
                        id="dropdown_network_model",
                        #label=chosen_epidemiological_model,
                        options=[
                            {'label': network_model, 'value': network_model} for network_model in network_models
                        ],
                        #value = "chosen_epidemiological_model"
                    ),
                ),
                html.Td(
                    dcc.Dropdown(
                        id="dropdown_epidemiological_model",
                        #label=chosen_epidemiological_model,
                        options=[
                            {'label': a_nodes, 'value': a_nodes} for a_nodes in amounts_of_nodes
                        ],
                        #value = "chosen_epidemiological_model"
                    ),
                ), 
                html.Td(
                    dcc.Dropdown(
                        id="dropdown_epidemiological_model",
                        #label=chosen_epidemiological_model,
                        options=[
                            {'label': death_rate, 'value': death_rate} for death_rate in death_rates
                        ],
                        #value = "chosen_epidemiological_model"
                    ),
                ),
            ]),

            html.Tr([
                html.Td(
                    html.Div(children="Select threatment time"),
                ),
                html.Td(
                    html.Div(children="Select critically threatment time"),
                ),
                html.Td(
                    html.Div(children="Select initial amount of nodes"),
                ),
                html.Td(
                    html.Div(children="Select infection rate"),
                ),
            ]),

            #second parameters
            html.Tr([
                html.Td(
                    dcc.Dropdown(
                        options=[
                            {'label': threatment_time, 'value': threatment_time} for threatment_time in threatment_times
                        ],
                    ),
                ), 
                html.Td(
                    dcc.Dropdown(
                        options=[
                            {'label': critically_threatment_time, 'value': critically_threatment_time} for critically_threatment_time in critically_threatment_times
                        ],
                    ),
                ),    
                html.Td(
                    dcc.Dropdown(
                        options=[
                            {'label': initial_amount_of_edges, 'value': initial_amount_of_edges} for initial_amount_of_edges in initial_amounts_of_edges
                        ],
                    ),
                ),    
                html.Td(
                    dcc.Dropdown(
                        options=[
                            {'label': value, 'value': value} for value in [0.01, 0.015, 0.02]
                        ],
                    ),
                ),              
            ]),
            html.Tr([
                html.Td(
                    html.Div(children="Select state"),
                ),
            ]),
            html.Tr([
                html.Td(
                    dcc.Dropdown(
                        options=[
                            {'label': value, 'value': value} for value in ['infected', 'dead', 'critically infected']
                        ],
                    ),
                ),  
            ]),
         ]),
    ),
    html.P(),

    html.Div([
        dbc.Checklist(
            options=[
                {"label": "error bar", "value": "same"},
            ],
            value=['different'],
            id="death_rate_input",
            switch=True,
        ),

        html.P(),
        "Enter the deviation",
        html.P(),

        dcc.Input(
            #id=
            type="number",
            placeholder="insert of error from 0 to 0.5",  # A hint to the user of what can be entered in the control
            #debounce=True,                      # Changes to input are sent to Dash server only on enter or losing focus
            #min=2015, max=2019, step=1,         # Ranges of numeric value. Step refers to increments
            #minLength=0, maxLength=50,          # Ranges for character length inside input box
            #autoComplete='on',
            size="50",                          # Number of characters that will be visible inside box
            # persistence='',                   # Stores user's dropdown changes in memory (Dropdown video: 16:20)
            # persistence_type='',              # Stores user's dropdown changes in memory (Dropdown video: 16:20)
            # value = 1,
        )
    ]),
    
    html.P(),
    dbc.Button("Add to plot", value="a", id="button_submit_parameters", color="primary", disabled=True, style={"left-margin":'2%'}),
    dbc.Button("Clean plot", value="a", id="button_submit_parameters", color="primary", disabled=False, style={"left-margin":'10px'}),
    html.P(),

    dbc.Table(
        html.Tbody([
            html.Tr([
                html.Td(
                    children=[
                        "Scale for x-axis",
                        dcc.Dropdown(
                            options=[
                                {'label': scale, 'value': scale} for scale in ['linear', 'logarithmic']
                            ],
                        ),
                        "Scale for y-axis",
                        dcc.Dropdown(
                            options=[
                                {'label': scale, 'value': scale} for scale in ['linear', 'logarithmic']
                            ],
                        ),
                    ]
                    ,style={'width': '20%'}),
                html.Td(children=[
                    html.H2("Average plots"),
                    dcc.Graph(id='our_graph', 
                        figure = go.Figure([
                            go.Scatter(
                                x=data_simulation1['time'], 
                                y=data_simulation1['infected'], 
                                name='infected 1',
                                line=dict(color='firebrick', width=4),
                            ),
                            go.Scatter(
                                x=data_simulation1['time'], 
                                y=data_simulation1['dl_infected'], 
                                name='low_infected 1',
                                line=dict(color='firebrick', width=4, dash='dash'),
                            ),
                            go.Scatter(
                                x=data_simulation1['time'], 
                                y=data_simulation1['du_infected'], 
                                name='up_infected 1',
                                line=dict(color='firebrick', width=4, dash='dot'),
                            ),


                            #line two
                            go.Scatter(
                                x=data_simulation2['time'], 
                                y=data_simulation2['infected'], 
                                name='infected 2',
                                line=dict(color='blue', width=4),
                            ),
                            # go.Scatter(
                            #     x=data_simulation2['time'], 
                            #     y=data_simulation2['dl_infected'], 
                            #     name='low_infected 2',
                            #     line=dict(color='blue', width=4, dash='dash'),
                            # ),
                            # go.Scatter(
                            #     x=data_simulation2['time'], 
                            #     y=data_simulation2['du_infected'], 
                            #     name='up_infected 2',
                            #     line=dict(color='blue', width=4, dash='dot'),
                            # ),
                        ], 
                        layout = {
                            'xaxis_title': "Time",
                            'yaxis_title': "Amount of people",
                        }
                        ),
                    ),
                ], style={"textAlign": "center"}),
            ])
        ])
    ),

])