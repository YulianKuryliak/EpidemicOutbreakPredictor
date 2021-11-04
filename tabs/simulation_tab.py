import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_table as dt
from dash.dependencies import Input, Output, State, MATCH, ALL
import pathlib
import time
import pandas as pd
import plotly
import plotly.express as px


from app import app
from scripts import run_simulation

# get relative data folder
path_to_R = ""
PATH = pathlib.Path(__file__).parent.parent

log_df = pd.read_csv('/media/user/90D2F44FD2F43AD4/data backup/PreRelease/assets/data/data_actions_0.csv')
log_df = log_df.drop([log_df.columns[0], 'virus_type'],1)
data_df = pd.read_csv('/media/user/90D2F44FD2F43AD4/data backup/PreRelease/assets/data/data_0.csv')
new_data_df = pd.melt(data_df, id_vars=['time'], value_vars=["infected","dead","critically_infected","susceptible"])
#print(new_data_df)

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

s_time = -1

layout = html.Div([
    html.H1('Welcome to simulation', style={"textAlign": "center"}),

    # html.Div(children="Chose epidemiological model"),
    # dbc.DropdownMenu(
    #     id="dropdown_epidemiological_model",
    #     label=chosen_epidemiological_model,
    #     children=[
    #         dbc.DropdownMenuItem(
    #             id = "dropdown_item_epidemiological_model_{}".format(epidemiological_model),
    #             epidemiological_model) for epidemiological_model in epidemiological_models
    #     ],
    # ),

    dbc.Table(
        html.Tbody([
            html.Tr([
                html.Td(
                    html.Div(children="Select epidemiological model"),
                ),
                html.Td(
                    html.Div(children="Select network model"),
                ),
            ]),
    
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
                )
            ])
        ])
    ),
    html.Div(id = "parameters", children = []), 

    dbc.Checklist(
        options=[
            {"label": "Same criticaly infication rate", "value": "same"},
        ],
        value=['different'],
        id="death_rate_input",
        switch=True,
    ),

    dbc.Button("Submit", value="a", id="button_submit_parameters", color="primary", ),
    
    html.Div(id="output", children=[
        html.Div(id = "simulation_output", 
            children = [
                dcc.Interval(id='interval1', interval=1 * 1000, n_intervals=0),
                html.H1(id = "test_clock", children = ["123"], style={"textAlign": "center"}),
                #html.Img(id = "image1", src='data:image/png;base64,{}'.format(encoded_image))
                html.Img(id = "image1", src=app.get_asset_url('0.png'), style={'height':'700px', 'width':'700px', 'textAlign': 'center'}),
                #style={'height':'50%', 'width':'50%'}
                html.Div([
                    dcc.Slider(
                        id='my-slider',
                        min=0,
                        max=100,
                        step=1,
                        value=17,
                    )],style={'width':'750px', 'margin-left' : str((100 -850/1920*100)/2) + "%"}
                )
            ], 
            style={'textAlign': 'center'}
        ), 
        
        html.H1(id = "dynamics", children = ["Dynamics"], style={"textAlign": "center"}),

        html.Div([
            dcc.Graph(id='our_graph', figure = px.line(new_data_df, x="time", y="value",color='variable', labels={
                        "time": "Time",
                        "value": "Amount of people",
                        "variable": "Curves:"
                    },)),
        ], style={'width':'90%', 'margin-left':'5%'}),

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
        html.H1(id = "Actions_log", children = ["Log of actions"], style={"textAlign": "center"}),
        html.Div([
            dt.DataTable(
                id='log_actions_table',
                columns=[{"name": i, "id": i} for i in log_df.columns],
                data=log_df.to_dict('records'),
            ), 
        ],style={'width':'90%', 'margin-left':'5%'})
    ], style={'display': 'none'})
])


@app.callback(
    Output(component_id="parameters", component_property="children"),
    Input(component_id="dropdown_epidemiological_model", component_property="value"),
    Input(component_id="dropdown_network_model", component_property="value")
)
def create_inputs(chosen_epidemiological_model_value, chosen_network_model_value):
    #time.sleep(10)
    set_epidemiological_model(chosen_epidemiological_model_value)
    set_network_model(chosen_network_model_value)
    global total_fields 
    total_fields = epidemiological_parameters + network_parameters + other_parameters
    return [
        dcc.Input(
            id={
                "type" : "input_parameters",
                'index' : field
            },
            type="number",
            placeholder="insert {}".format(field),  # A hint to the user of what can be entered in the control
            debounce=True,                      # Changes to input are sent to Dash server only on enter or losing focus
            #min=2015, max=2019, step=1,         # Ranges of numeric value. Step refers to increments
            minLength=0, maxLength=50,          # Ranges for character length inside input box
            autoComplete='on',
            disabled=False,                     # Disable input box
            readOnly=False,                     # Make input box read only
            required=False,                     # Require user to insert something into input box
            size="20",                          # Number of characters that will be visible inside box
            # persistence='',                   # Stores user's dropdown changes in memory (Dropdown video: 16:20)
            # persistence_type='',              # Stores user's dropdown changes in memory (Dropdown video: 16:20)
            # value = 1,
        ) for field in total_fields
    ]


def set_epidemiological_model(chosen_value):
    chosen_epidemiological_model = chosen_value
    global epidemiological_parameters

    if(chosen_epidemiological_model == "SIR"):
        epidemiological_parameters = ["Treatment_Period", "Critically_Treatment_Period"]
    if(chosen_epidemiological_model == "SI"):
        epidemiological_parameters = []
    

def set_network_model(chosen_value):
    chosen_network_model = chosen_value
    global network_parameters
    if(chosen_network_model == "Complete"):
        network_parameters = []
    if(chosen_network_model == "Barabasi-Albert"):
        network_parameters = ['number_of_edges'] #["initial_number_of_adges_for_node"]

    if(chosen_network_model == "Erdos-Renyi"):
        network_parameters = ['number_of_edges'] #["number_of_adges_in_network"]
    if(chosen_network_model == "Watts-Strogatz"):
        network_parameters = ['number_of_edges', 'reconection_coefitient']#["initial_number_of_adges_for_node",  "Reconection_coefitient"]


@app.callback(
    #Output("button_submit_parameters", "value"),
    Output("output", "style"),
    #Input("interval1","n_intervals"),
    Input("button_submit_parameters","n_clicks"),
    State('dropdown_epidemiological_model', 'value'),
    State('dropdown_network_model', 'value'),
    [State(component_id={'type' : "input_parameters", 'index' : ALL}, component_property="value")]
)
def button_submit_clicked(click, epidemiological_model, network_model, *parameters):
    print('\033[92m' + "click")
    print('\033[0m')
    global inputed_parameters
    global s_time
    # print("two type : ", type(parameters))
    # print("two : ", parameters[0])
    # print("two len : ", len(parameters[0]))
    # print('total_fields len: ', len(total_fields))
    # print('total fields :', total_fields)
    print('----------')
    inputed_parameters['epidemiological_model'] = epidemiological_model
    inputed_parameters['network_model'] = network_model
    if(len(parameters[0]) != 0 and parameters[0][0] != None):
        for i in range(0, len(parameters[0])):
            inputed_parameters[total_fields[i]] = parameters[0][i]
        #run_simulation.path_to_R = path_to_R
        #run_simulation.simulation(inputed_parameters)
        s_time = 0
        return {}
    #print('inputed_parameters : ', inputed_parameters)
    return {'display': 'none'}


@app.callback(
    Output("test_clock", "children"),
    #Output("test_clock", "children"),
    Output("image1", "src"),
    Output("my-slider", "value"),
    Input("interval1","n_intervals")
)
def test_button(n_step):
    #print(app.get_asset_url())
    global s_time
    if(s_time >= 0 & s_time < 101):
        s_time += 1
        return "Time : " + str(s_time - 1), app.get_asset_url("plots\\" +  str(s_time - 1) + '.png'), s_time - 1
    return 0, app.get_asset_url('0.png'), 0


@app.callback(
    Output("death_rate_input", 'value'),
    Input("death_rate_input", 'value'),
)
def death_rate_switch(value):
    if('same' in value):
        value = ['same']
    else:
        value = ['different']
    inputed_parameters['Criticaly_infection_rate'] = value[0]
    return value
