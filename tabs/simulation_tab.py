import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import dash_table as dt
from dash.dependencies import Input, Output, State, MATCH, ALL
import pathlib
import time
import pandas as pd
from pandas.core.frame import DataFrame
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import *
import igraph
from dash.exceptions import PreventUpdate
from scripts import Network_model, run_simulation
import numpy as np

from app import app
from scripts import Simulation

# get relative data folder
path_to_R = ""
PATH = pathlib.Path(__file__).parent.parent

log_df = pd.read_csv(
    "/home/data/projects/ManagingEpidemicOutbreak/EpidemicOutbreakPredictor/assets/data/data_actions_0.csv"
)
log_df = log_df.drop([log_df.columns[0], "virus_type"], 1)
data_df = pd.read_csv(
    "/home/data/projects/ManagingEpidemicOutbreak/EpidemicOutbreakPredictor/assets/data/data_0.csv"
)
new_data_df = pd.melt(
    data_df,
    id_vars=["time"],
    value_vars=["infected", "dead", "critically_infected", "susceptible"],
)


epidemiological_models = ["SIR", "SI", "SIS", "SEIR"]
chosen_epidemiological_model = epidemiological_models[0]
network_models = ["Complete", "Barabasi-Albert", "Erdos-Renyi", "Watts-Strogatz"]
chosen_network_model = network_models[0]

graph_states = []
dinamics_data = []

# parameters for simmulation
epidemiological_parameters = []
network_parameters = []
other_parameters = [
    "Size",
    "Infection_rate",
    "Maximum_simulation_time",
    "Time_of_data_collection",
    "start_infected",
    "number_of_simulations",
]
total_fields = []
inputed_parameters = {
    "epidemiological_model": "SIR",
    "network_model": "BA",
    "Size": 500,
    "Infection_rate": 0.5,
    "Maximum_simulation_time": 100,
    "Time_of_data_collection": 1,
    "start_infected": 1,
    "number_of_edges": 2,
    "reconection_coefitient": 0,
    "Treatment_Period": 10,
    "Critically_Treatment_Period": 14,
    "number_of_simulations": 1,
    "Criticaly_infection_rate": "different",
}

s_time = -1

layout = html.Div(
    [
        html.H1("Welcome to simulation", style={"textAlign": "center"}),
        dbc.Table(
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                html.Div(children="Select epidemiological model"),
                            ),
                            html.Td(
                                html.Div(children="Select network model"),
                            ),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td(
                                dcc.Dropdown(
                                    id="dropdown_epidemiological_model",
                                    # label=chosen_epidemiological_model,
                                    options=[
                                        {
                                            "label": epidemiological_model,
                                            "value": epidemiological_model,
                                        }
                                        for epidemiological_model in epidemiological_models
                                    ],
                                    # value = "chosen_epidemiological_model"
                                ),
                            ),
                            html.Td(
                                dcc.Dropdown(
                                    id="dropdown_network_model",
                                    # label=chosen_epidemiological_model,
                                    options=[
                                        {"label": network_model, "value": network_model}
                                        for network_model in network_models
                                    ],
                                    # value = "chosen_epidemiological_model"
                                ),
                            ),
                        ]
                    ),
                ]
            )
        ),
        html.Div(id="parameters", children=[]),
        # dbc.Checklist(
        #     options=[
        #         {"label": "Same criticaly infication rate", "value": "same"},
        #     ],
        #     value=["different"],
        #     id="death_rate_input",
        #     switch=True,
        # ),
        dbc.Button(
            "Submit",
            value="a",
            id="button_submit_parameters",
            color="primary",
        ),
        html.Div(
            id="output",
            children=[
                html.Div(
                    id="simulation_output",
                    children=[
                        dcc.Interval(id="interval1", interval=1 * 1000, n_intervals=0, max_intervals = 100, disabled=True),
                        html.H1(
                            id="test_clock",
                            children=["no data"],
                            style={"textAlign": "center"},
                        ),
                        html.Div([
                            dcc.Graph(
                                id="graph_visualization",
                                figure=go.Figure(data=None, layout = go.Layout(
                                    font= dict(size=12),
                                    showlegend=False,
                                    autosize=False,
                                    width=800,
                                    height=800,
                                    xaxis=go.layout.XAxis(),
                                    yaxis=go.layout.YAxis(),
                                    # margin=go.layout.Margin(
                                    #     l=40,
                                    #     r=40,
                                    #     b=85,
                                    #     t=100,
                                    # ),
                                    #align='center',
                                    hovermode='closest',
                                    annotations=[
                                        dict(
                                        showarrow=False,
                                            xref='paper',
                                            yref='paper',
                                            x=0,
                                            y=-0.1,
                                            xanchor='left',
                                            yanchor='bottom',
                                            font=dict(
                                            size=14
                                            )
                                        )
                                    ]
                                )),
                            )
                            ],
                            style={
                                "width": "100%",
                                "height": "100%",
                            },
                        ),

                        # style={'height':'50%', 'width':'50%'}
                        html.Div(
                            [
                                dcc.Slider(
                                    id="my-slider",
                                    min=0,
                                    max=inputed_parameters["Maximum_simulation_time"],
                                    step=inputed_parameters["Time_of_data_collection"],
                                    value=0,
                                )
                            ],
                            style={
                                "width": "750px",
                                "margin-left": str((100 - 850 / 1920 * 100) / 2) + "%",
                            },
                        ),
                    ],
                    style={"textAlign": "center"},
                ),
                
                html.H1(
                    id="dynamics", children=["Dynamics"], style={"textAlign": "center"}
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="our_graph",
                            figure=px.line(
                                new_data_df,
                                x="time",
                                y="value",
                                color="variable",
                                labels={
                                    "time": "Time",
                                    "value": "Amount of people",
                                    "variable": "Curves:",
                                },
                            ),
                        ),
                    ],
                    style={"width": "90%", "margin-left": "5%"},
                ),
                # html.Div([
                #     dcc.Checklist(
                #         id="checklist",
                #         options=[{"label": x, "value": x}
                #                 for x in all_continents],
                #         value=all_continents[3:],
                #         labelStyle={'display': 'inline-block'}
                #     ),
                #     dcc.Graph(id="line-chart"),
                # ]),
                # html.H1(id = "Actions_log", children = ["Log of actions"], style={"textAlign": "center"}),
                # html.Div([
                #     dt.DataTable(
                #         id='log_actions_table',
                #         columns=[{"name": i, "id": i} for i in log_df.columns],
                #         data=log_df.to_dict('records'),
                #     ),
                # ],style={'width':'90%', 'margin-left':'5%'})
            ],
            style={"display": "contents"},
        ),
        dcc.Store(id="intermediate-value"),
    ]
)


# @app.callback(
#     Output("death_rate_input", "value"),
#     Input("death_rate_input", "value"),
# )
# def death_rate_switch(value):
#     print("i am death_rate_switch")
#     if "same" in value:
#         value = ["same"]
#     else:
#         value = ["different"]
#     inputed_parameters["Criticaly_infection_rate"] = value[0]
#     return value


@app.callback(
    Output(component_id="parameters", component_property="children"),
    Input(component_id="dropdown_epidemiological_model", component_property="value"),
    Input(component_id="dropdown_network_model", component_property="value"),
)
def create_inputs(chosen_epidemiological_model_value, chosen_network_model_value):
    print("i am create inputs")
    # time.sleep(10)
    set_epidemiological_model(chosen_epidemiological_model_value)
    set_network_model(chosen_network_model_value)
    global total_fields
    total_fields = epidemiological_parameters + network_parameters + other_parameters
    return [
        dcc.Input(
            id={"type": "input_parameters", "index": field},
            type="number",
            placeholder="insert {}".format(
                field
            ),  # A hint to the user of what can be entered in the control
            debounce=True,  # Changes to input are sent to Dash server only on enter or losing focus
            # min=2015, max=2019, step=1,         # Ranges of numeric value. Step refers to increments
            minLength=0,
            maxLength=50,  # Ranges for character length inside input box
            autoComplete="on",
            disabled=False,  # Disable input box
            readOnly=False,  # Make input box read only
            required=False,  # Require user to insert something into input box
            size="20",  # Number of characters that will be visible inside box
            # persistence='',                   # Stores user's dropdown changes in memory (Dropdown video: 16:20)
            # persistence_type='',              # Stores user's dropdown changes in memory (Dropdown video: 16:20)
            # value = 1,
        )
        for field in total_fields
    ]


def set_epidemiological_model(chosen_value):
    chosen_epidemiological_model = chosen_value
    global epidemiological_parameters

    if chosen_epidemiological_model == "SIR":
        epidemiological_parameters = ["Treatment_Period", "Critically_Treatment_Period"]
    if chosen_epidemiological_model == "SI":
        epidemiological_parameters = []


def set_network_model(chosen_value):
    chosen_network_model = chosen_value
    global network_parameters
    if chosen_network_model == "Complete":
        network_parameters = []
    if chosen_network_model == "Barabasi-Albert":
        network_parameters = ["number_of_edges"]  # ["initial_number_of_adges_for_node"]

    if chosen_network_model == "Erdos-Renyi":
        network_parameters = ["number_of_edges"]  # ["number_of_adges_in_network"]
    if chosen_network_model == "Watts-Strogatz":
        network_parameters = [
            "number_of_edges",
            "reconection_coefitient",
        ]  # ["initial_number_of_adges_for_node",  "Reconection_coefitient"]


@app.callback(
    Output("our_graph", "figure"),
    Output("interval1", "disabled"),
    #Output("interval1", "max_intervals"),
    Input("button_submit_parameters", "n_clicks"),
    # State("dropdown_epidemiological_model", "value"),
    # State("dropdown_network_model", "value"),
    # [
    #     State(
    #         component_id={"type": "input_parameters", "index": ALL},
    #         component_property="value",
    #     )
    # ],
)
def button_submit_clicked(click)#, epidemiological_model, network_model, *parameters):
    if click is None:
        raise PreventUpdate
    print("i am button_submit_clicked")
    print("\033[92m" + "click : ", click)
    print("\033[0m")
    global inputed_parameters
    global s_time
    global graph_states
    print("----------")
    inputed_parameters["epidemiological_model"] = epidemiological_model if epidemiological_model is not None else inputed_parameters["epidemiological_model"]
    inputed_parameters["network_model"] = network_model if network_model is not None else inputed_parameters["network_model"]
    if len(parameters[0]) != 0 and parameters[0][0] != None:
        for i in range(0, len(parameters[0])):
            inputed_parameters[total_fields[i]] = parameters[0][i] if parameters[0][i] is not None else inputed_parameters[total_fields[i]]
    s_time = 0
    graph_states, dinamics_data = run_simulation.run(inputed_parameters)
    
    print("----------")
    print("type of returned state: ",type(graph_states[0]))
    print("lenght", len(graph_states))
    # print('inputed_parameters : ', inputed_parameters)
    # return {'display': 'none'}
    return update_dinamics(dinamics_data), False#, int(inputed_parameters['Maximum_simulation_time'])+1


# @app.callback(
#     Output("our_graph", "figure"), 
#     Input("intermediate-value", "data"))
def update_dinamics(dinamics_data):
    print("i am update_dinamics")
    # px.line(new_data_df, x="time")
    temp = pd.DataFrame(dinamics_data[1:], columns=dinamics_data[0])
    temp = pd.melt(
        temp,
        id_vars=["time"],
        value_vars=[
            "amount_of_infected",
            "amount_of_susceptible",
            "amount_of_contagious",
            "amount_of_critically_infected",
            "amount_of_dead",
        ],
    )
    return px.line(
        temp,
        x="time",
        y="value",
        color="variable",
        labels={"time": "Time", "value": "Amount of people", "variable": "Curves:"},
    )

@app.callback(
    Output("test_clock", "children"),
    Input("interval1", "n_intervals"),
)
def test(n_intervals):
    print(n_intervals)
    return n_intervals

# @app.callback(
#     Output("test_clock", "children"),
#     # Output("test_clock", "children"),
#     #Output("image1", "src"),
#     Output("my-slider", "value"),
#     Output("graph_visualization", "figure"),
#     Input("interval1", "n_intervals"),
# )
# def graph_updating(n_step):
#     if n_step is None:
#         raise PreventUpdate
#     print("i am graph_updating")
#     # print(app.get_asset_url())
#     global s_time
#     global inputed_parameters
#     if s_time >= 0 and s_time < inputed_parameters['Maximum_simulation_time'] + 1:
#         print("graph states: ", len(graph_states))
#         s_time += 1
#         return (
#             "Time : " + str(s_time - 1),
#             #app.get_asset_url("plots\\" + str(s_time - 1) + ".png"),
#             s_time - 1,
#             get_graph(s_time-1)
#         )
#     return "Not started", 0, px.scatter()#, None


# # # make 2 inputs https://dash.plotly.com/duplicate-callback-outputs
# # @app.callback(
# #     Output("test_clock", "children"),
# #     Output("my-slider", "value"),
# #     Output("graph_visualization", "figure"),
# #     Input("interval1", "n_intervals"),
# # )
# # def interval_graph_updating(n_step):
# #     return ("Time : " + str(n_step * inputed_parameters['Time_of_data_collection']),
# #             str(n_step * inputed_parameters['Time_of_data_collection']),
# #             graph_updating(n_step)
# #     )


# # @app.callback(
# #     Output("test_clock", "children"),
# #     Output("interval1", "n_intervals"),
# #     Output("graph_visualization", "figure"),
# #     Input("my-slider", "value"), 
# # )
# # def slider_graph_updating(value):
# #     return("Time : " + str(value),
# #         int(value / inputed_parameters['Time_of_data_collection']),
# #         graph_updating(value / inputed_parameters['Time_of_data_collection'])
# #     )


# # def graph_updating(time):
# #     if time is None:
# #         raise PreventUpdate
# #     print("i am graph_updating")
# #     global inputed_parameters
# #     if time >= 0 and time < inputed_parameters['Maximum_simulation_time'] + 1:
# #         return (
# #             # "Time : " + str(time * inputed_parameters['Time_of_data_collection']),
# #             # #app.get_asset_url("plots\\" + str(s_time - 1) + ".png"),
# #             # str(time * inputed_parameters['Time_of_data_collection']),
# #             get_graph(time)
# #         )
# #     return px.scatter()



# def get_graph(index):
#     print("getting graph ", index)
#     print("index : ", index)
#     G = graph_states[index]
#     #igraph.plot(G)
#     #G=igraph.Graph.Tree(127,2)
#     labels= [i for i in range(G.vcount())] #list(G.vs['label'])
#     G.vs['name'] = ["name_" + str(i) for i in labels]
#     N=len(labels)
#     E=[e.tuple for e in G.es]# list of edges # represintation (start node, end node)
#     layt=G.layout('kk', dim=3) #kamada-kawai layout
#     type(layt)
#     v_colors = G.vs['color']
#     v_sizes = G.vs['infections']
#     e_colors = G.es['color']
#     e_sizes = G.es['infections']


#     Xn=[layt[k][0] for k in range(N)]
#     Yn=[layt[k][1] for k in range(N)]
#     Zn=[layt[k][2] for k in range(N)]

#     Xe=[]
#     Ye=[]
#     Ze=[]

#     for e in E:
#         Xe+=[layt[e[0]][0], layt[e[1]][0]] #coordinates of edge e(start, end)
#         Ye+=[layt[e[0]][1], layt[e[1]][1]] 
#         Ze+=[layt[e[0]][2], layt[e[1]][2]] 

#     trace1=[go.Scatter3d(
#                 x=Xe[i:i+2],
#                 y=Ye[i:i+2],
#                 z=Ze[i:i+2],
#                 mode='lines',
#                 line= dict(color=e_colors[int(i/2)], width=1 + 3 * e_sizes[int(i/2)]),
#                 hoverinfo='none'
#     ) for i in range(0, len(e_colors)*2, 2)]

#     trace2=go.Scatter3d(x=Xn,
#                 y=Yn,
#                 z=Zn,
#                 mode='markers',
#                 name='ntw',
#                 marker=dict(symbol='circle',
#                                             size=12,
#                                             color=v_colors,
#                                             line=dict(color='rgb(50,50,50)', width=1)
#                                             ),
#                 text=labels,
#                 hoverinfo='none'
#     )

#     axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
#             zeroline=False,
#             showgrid=False,
#             showticklabels=False,
#             title=''
#             )

#     width=1800
#     height=900
#     layout=go.Layout(
#         font= dict(size=12),
#         showlegend=False,
#         autosize=False,
#         width=width,
#         height=height,
#         xaxis=go.layout.XAxis(axis),
#         yaxis=go.layout.YAxis(axis),
#         # margin=go.layout.Margin(
#         #     l=40,
#         #     r=40,
#         #     b=85,
#         #     t=100,
#         # ),
#         #align='center',
#         hovermode='closest',
#         annotations=[
#             dict(
#             showarrow=False,
#                 xref='paper',
#                 yref='paper',
#                 x=0,
#                 y=-0.1,
#                 xanchor='left',
#                 yanchor='bottom',
#                 font=dict(
#                 size=14
#                 )
#             )
#         ]
#     )

#     data=[*trace1, trace2]
#     fig=go.Figure(data=data, layout=layout)
#     #fig.show()
#     return fig