from dash import dcc
from dash import html
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

data_peak_infected1 = dict()
print("i call max_infected")
data_peak_infected1['amounts'], data_peak_infected1['infected_rates'] = analysis.maximum_infected(
    folder="E:\\Managing epidemic outbreak\\task6\\output_data\\simulations", 
    size = 200,
    virus_type1=1,
    network_type1="barabasi", 
    death_rate_type1='same', 
    amount_of_edges=1
)

data_peak_infected2 = dict()
print("i call max_infected")
data_peak_infected2['amounts'], data_peak_infected2['infected_rates'] = analysis.maximum_infected(
    folder="E:\\Managing epidemic outbreak\\task6\\output_data\\simulations", 
    size = 200,
    virus_type1=1,
    network_type1="barabasi", 
    death_rate_type1='same', 
    amount_of_edges=2
)

print("\n\n\n\nhello\n\n\n\n")
print(data_peak_infected1)


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
                {'label': death_rate, 'value': death_rate} for death_rate in ["Separated analysis of each of the results", "Average values", "Analysis of amount of peak values nodes"]
            ],
        ),
    ], style = {'width':"30%", 'margin': 'auto'}),
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
                    html.Div(children="Select type of averaging"),
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
                            {'label': value, 'value': value} for value in ['Average', 'Median']
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
    dbc.Button("Add to plot", value="a", id="button_submit_parameters", color="primary", disabled=False, style={"left-margin":'2%'}),
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
                    html.H2("Peack values plots"),
                    dcc.Graph(id='our_graph', 
                        figure = go.Figure([
                            go.Scatter(
                                x = data_peak_infected1['infected_rates'],
                                y = data_peak_infected1['amounts'],
                                name='parameters 1',
                                line=dict(color='firebrick', width=4),
                                #log_x=True
                            ),
                            go.Scatter(
                                x = data_peak_infected2['infected_rates'],
                                y = data_peak_infected2['amounts'],
                                name='parameters 2',
                                line=dict(color='blue', width=4),
                            ),
                            ], 
                            layout = {
                                'xaxis_title': "Time",
                                'yaxis_title': "Amount of people",
                                'xaxis_type' : 'log'
                            }
                        ),
                    ),
                ], style={"textAlign": "center"}),
            ])
        ])
    ),

])