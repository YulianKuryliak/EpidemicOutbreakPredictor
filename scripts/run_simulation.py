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

if __name__ == "__main__":
	import Simulation
	import Network
	import Population
	import Network_model	
else:
	from scripts import Simulation
	from scripts import Network
	from scripts import Population
	from scripts import Network_model

import copy

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
	reconnection_rate = round(float(parameters['Reconnection_rate']), 6)
	quorantine_measures = parameters['Quorantine_measures']
	infection_rate = round(float(parameters['Infection_rate']), 6)
	death_rate_type = parameters['Criticaly_infection_rate']
	number_of_nodes_for_immunization = int(parameters['Number_of_nodes_for_immunization'])
	
	last = None

	print("Network creation")
	network = create_network(graph_size, amount_of_contacts, network_type, reconnection_rate = 0, quorantine_measures = "", directed = False, number_of_nodes_for_immunization = 0)
	if(quorantine_measures == 'non-backtracking'):
		network.get_non_backtracking_matrix()
	network = network.better_removing(mode = quorantine_measures, number_of_nodes=int(parameters['Number_of_nodes_for_immunization']))

	path = PATH + "/data/simulations/"
	folder = create_folder(path, graph_size, network_type, amount_of_contacts, infection_rate, death_rate_type, reconnection_rate, quorantine_measures, number_of_nodes_for_immunization)

	infections_by_node = np.zeros(network.size)
	edge_infections = np.zeros(network.graph.ecount())

	for i in range(parameters['number_of_simulations']):
		network_copy = copy.deepcopy(network)
		last = Simulation.simulation(
			network = network_copy,
			infection_rate = round(float(parameters['Infection_rate']), 6),
			number_of_infections = int(parameters['start_infected']), 
			max_time = int(parameters['Maximum_simulation_time']), 
			time_step = round(float(parameters['Time_of_data_collection']),2), 
			i = int(i),
			folder = folder
		)
		infections_by_node = infections_by_node + last[2]
		edge_infections = edge_infections + last[3]
	return last[0], last[1], infections_by_node, edge_infections


def create_network(graph_size, amount_of_contacts, network_type, reconnection_rate = 0, quorantine_measures = "", directed = False, number_of_nodes_for_immunization = 0):
	graph = Network_model.create_network(graph_size, amount_of_contacts, network_type, reconnection_rate)
	graph.es['infections'] = np.array([0 for i in range(graph.ecount())])
	network = Network.Network(graph, Population.get_population(), directed = directed)
	network = network.better_removing(mode = quorantine_measures, number_of_nodes=number_of_nodes_for_immunization)
	return network


def create_graph(graph_size, amount_of_contacts, network_type, reconnection_rate = 0):
	#print("Graph creation")
	graph = Network_model.create_network(graph_size, amount_of_contacts, network_type, reconnection_rate)
	return graph


def prepare_parameters(inputed_parameters):
	if inputed_parameters['network_model'] == "Barabasi-Albert":
		inputed_parameters['network_model'] = 'BA'
	return inputed_parameters


def create_folder(path, graph_size, network_type, amount_of_contacts, infection_rate, death_rate_type, reconnection_rate, quorantine_measures, number_of_nodes_for_immunization):
	if quorantine_measures == 'no':
		number_of_nodes_for_immunization = 0
	folder = path + get_folder_name(graph_size, network_type, amount_of_contacts, infection_rate, death_rate_type, reconnection_rate, quorantine_measures, number_of_nodes_for_immunization)
	if(os.path.exists(folder) == False):
		os.makedirs(folder)
		print("Created!")
	return folder


def get_folder_name(graph_size, network_type, amount_of_contacts, infection_rate, death_rate_type, reconnection_rate=-1, quorantine_measures = -1, number_of_nodes_for_immunization = ""):
	if(reconnection_rate != -1):
		return "size: {}, network: {}, node_contacts: {}, reconnection_rate: {}, infection_rate: {}, death_rate: {}, quorantine: {}_{}/".format(
					graph_size, network_type, amount_of_contacts, np.format_float_positional(reconnection_rate), np.format_float_positional(infection_rate), death_rate_type, quorantine_measures, number_of_nodes_for_immunization)
	return "size: {}, network: {}, node_contacts: {}, infection_rate: {}, death_rate: {}, quorantine: {}_{}/".format(
					graph_size, network_type, amount_of_contacts, np.format_float_positional(infection_rate), death_rate_type, quorantine_measures, number_of_nodes_for_immunization)






if __name__ == "__main__":
	inputed_parameters = {
		"epidemiological_model": "SIR",
		"network_model": "BA",
		"Size": 50,
		"Infection_rate": 0.2,
		"Maximum_simulation_time": 20,
		"Time_of_data_collection": 1,
		"start_infected": 1,
		"number_of_edges": 2,
		"reconection_coefitient": 0,
		"Treatment_Period": 14,
		"Critically_Treatment_Period": 14,
		"number_of_simulations": 5,
		"Criticaly_infection_rate": "different",
		"Reconnection_rate": -1,
		"Quorantine_measures": "no",
		"Directed": False,
		"Number_of_nodes_for_immunization": 3
	}
	run(inputed_parameters)