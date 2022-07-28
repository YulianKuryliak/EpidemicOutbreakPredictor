#folder title - ./version of simulation/(parameters).csv
#format of parameters - population 20, start_infected 2, treatment_time = 10, time_max = 20000, infection_rate = 0.01, time_step = 1 
#file title - number of simulation	
import sys
import os, os.path
import time
import subprocess
import numpy as np
import threading
import datetime
import pathlib
from scripts import Simulation
from scripts import Network
from scripts import Population
from scripts import Network_model

# inputed_parameters = {
#     "epidemiological_model": "SIR",
#     "network_model": "BA",
#     "Size": 100,
#     "Infection_rate": 0.1,
#     "Maximum_simulation_time": 100,
#     "Time_of_data_collection": 1,
#     "start_infected": 1,
#     "number_of_edges": 2,
#     "reconection_coefitient": 0,
#     "Treatment_Period": 10,
#     "Critically_Treatment_Period": 14,
#     "number_of_simulations": 1,
#     "Criticaly_infection_rate": "different",
# }

PATH = str(pathlib.Path(__file__).parent.absolute()).replace('scripts', '')


def run(inputed_parameters):
	parameters = prepare_parameters(inputed_parameters)
	print(parameters)

	graph_size = int(parameters['Size'])
	network_type = parameters['network_model']
	amount_of_contacts = int(parameters['number_of_edges'])
	reconnection_rate = 0
	
	graph = create_graph(graph_size, amount_of_contacts, network_type, reconnection_rate)
	last = None

	for i in range(parameters['number_of_simulations']):
		last = Simulation.simulation(
			graph = graph,
			graph_size = int(parameters['Size']),
			network_type = parameters['network_model'], 
			amount_of_contacts = int(parameters['number_of_edges']), 
			infection_rate = round(float(parameters['Infection_rate']), 6),
			number_of_infections = int(parameters['start_infected']), 
			death_rate_type = parameters['Criticaly_infection_rate'],
			max_time = int(parameters['Maximum_simulation_time']), 
			time_step = round(float(parameters['Time_of_data_collection']),2), 
			i = int(i), 
			folder = PATH + "/data/simulations/"
		)
	return last
# def simulation(graph, graph_size, network_type, 
# amount_of_contacts, infection_rate, number_of_infections, 
# death_rate_type,  max_time, time_step, 
# i, folder, reconnection_rate = -1, quorantine_measures = ""):

def create_graph(graph_size, amount_of_contacts, network_type, reconnection_rate = 0):
	#print("Graph creation")
	graph = Network_model.create_network(graph_size, amount_of_contacts, network_type, reconnection_rate)
	graph.vs['infections'] = np.array([0 for i in range(graph.vcount())])
	graph.es['infections'] = np.array([0 for i in range(graph.ecount())])
	return graph


def prepare_parameters(inputed_parameters):
	if inputed_parameters['network_model'] == "Barabasi-Albert":
		inputed_parameters['network_model'] = 'BA'
	return inputed_parameters
