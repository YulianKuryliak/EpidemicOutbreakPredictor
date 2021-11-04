import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_table as dt
from dash.dependencies import Input, Output, State, MATCH, ALL
import pathlib
from app import app

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
    html.H1('Welcome to analysis', style={"textAlign": "center"}),
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
            ]),
        ])
    ),
    html.Div([
        html.H5("Kind of analysis"),
        dcc.Dropdown(
            #label= "123",
            options=[
                {'label': death_rate, 'value': death_rate} for death_rate in ["Separated analysis of each of the results", "Average values"]
            ],
            #value = "Kind of analysis"
        ),
    ], style = {'margin-left': '1%', 'width':"20%"}),
    dbc.Button("Submit", value="a", id="button_submit_parameters", color="primary", style={"left-margin":'2%'}),

    


])