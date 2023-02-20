import igraph
#import numba
#from numba import cuda
#from numba import jit

# if __name__ == "__main__":
# 	import Network_model
# 	import Population 
# 	import Network
# else:
from scripts import Network_model
from scripts import Population 
from scripts import Network

# import Network_model
# import Population 
# import Network

import time
import numpy as np
import math
#import matplotlib.pyplot as plt
from pprint import pprint
import os
from os import path
import pathlib
import copy
import json


'''
arrays:
	infected
	susceptible
	contagiousprint

	adjacency matrix - np [n][n]
'''

#@jit(nopython=True)
def get_contagious_contacts(network):
	contagious_of_contacts = (
		network.adjacency_matrix.dot(
			network.susceptibility_of_nodes * network.susceptible_nodes
			)).T[0] * (network.contagiousness_of_nodes * network.contagious_nodes)
		
	#
	# print(sum(contagious_of_contacts))
	return contagious_of_contacts
	# return numba_get_contagious_contacts(network.adjacency_matrix, network.susceptibility_of_nodes, 
	# network.susceptible_nodes, network.contagiousness_of_nodes, network.contagious_nodes)


# @jit(nopython=True)
# def numba_get_contagious_contacts(adjacency_matrix, susceptibility_of_nodes, susceptible_nodes, contagiousness_of_nodes, contagious_nodes):
#	 contagious_of_contacts = (
#		 adjacency_matrix.dot(
#			 susceptibility_of_nodes * susceptible_nodes
#			 )).T[0] * (contagiousness_of_nodes * contagious_nodes)
#	 #print(sum(contagious_of_contacts))
#	 return contagious_of_contacts

def infection_roulette_wheel_choise(network, contagious_contacts, contagious_contacts_concentration):
	probabilities = contagious_contacts / contagious_contacts_concentration
	if(contagious_contacts_concentration <= 0):
		print("ERROR: Contagious_contacts_concentration <= 0")
		return -1

	sumprob = 0.0
	infect = np.random.uniform(0.0, 1.0) # [0, 1)
	for i in range(len(contagious_contacts)):
		previous_sumprob = sumprob
		sumprob += probabilities[i]
		if(previous_sumprob <= infect and infect < sumprob):
			
			contact_for_infection = np.random.randint(0, contagious_contacts[i], 1)	
			indexes_of_possible_nodes = np.argwhere(np.multiply(network.adjacency_matrix[i], network.susceptible_nodes.T[0]) == 1)
			#print(indexes_of_possible_nodes)
			#print("\n\n\n\nneeded value: ", indexes_of_possible_nodes[contact_for_infection][0][0], type( indexes_of_possible_nodes[contact_for_infection][0][0]), "\n\n\n")
			return  i, indexes_of_possible_nodes[contact_for_infection][0][0]


def get_time_to_infection(contagious_contacts_concentration, infection_rate):
	#check with R rexp(1,qii)
	if(contagious_contacts_concentration <= 0):
		return math.inf
	return round(np.random.exponential(1/(contagious_contacts_concentration * infection_rate)),12) # expected value - contagious_contacts_concentration.
	#return round(1/contagious_contacts_concentration)


def infection(index_node_for_infection, infection_time, network, death_note, index_infector = -1):
	prob_of_death = 0.01820518643617639 + 0.2

	network.infected_nodes[index_node_for_infection] = 1
	network.susceptible_nodes[index_node_for_infection][0] = 0
	network.contagious_nodes[index_node_for_infection] = 1
	network.times_node_infection[index_node_for_infection] = infection_time
	network.graph.vs[index_node_for_infection]['color'] = "#00FF00"
	# network.graph.vs[index_node_for_infection]['infections'] += 1
	print("index_node_for_infection = ", index_node_for_infection)
	if(np.random.uniform(0.0, 1.0) <= network.death_probabilities[index_node_for_infection]):
		death_note[index_node_for_infection] = 1 #die with probability
		network.graph.vs[index_node_for_infection]['color'] = "#FFB000"

	if index_infector >=0:
		network.infected_by_nodes[index_infector] += 1
		if (index_infector, index_node_for_infection) in network.edges_list:
			network.graph.es[network.graph.get_eid(index_infector, index_node_for_infection)]['color'] = "#FF0000"
			network.graph.es[network.graph.get_eid(index_infector, index_node_for_infection)]['infections'] += 1
		elif (index_node_for_infection, index_infector) in network.edges_list:
			network.graph.es[network.graph.get_eid(index_node_for_infection, index_infector)]['color'] = "#FF0000"
			network.graph.es[network.graph.get_eid(index_node_for_infection, index_infector)]['infections'] += 1
		# if(index_infector != -1):
		# 	edge = network.graph.es.select(_between=([index_infector], [index_node_for_infection]))[0]
		# 	# print('infector: ', index_infector, ';  infected:', index_node_for_infection)
		# 	# print(edge)
		# 	edge['color'] = "#FF0000"
		# 	edge['infections'] += 1


def CTMC(network, death_note, treatment_time, critically_treatment_time, infection_rate = 0.01, time = 0):
	do_actions(time, network, death_note, treatment_time, critically_treatment_time)
	contagious_contacts = get_contagious_contacts(network)
	contagious_contacts_concentration = sum(contagious_contacts)
	if(contagious_contacts_concentration <= 0):
		# what can i do?
		print("No contacts with contagious nodes left")
		return get_time_to_infection(-1, infection_rate)
	index_infector, index_node_for_infection = infection_roulette_wheel_choise(network, contagious_contacts,contagious_contacts_concentration)
	infection(index_node_for_infection, time, network, death_note, index_infector = index_infector)
	return get_time_to_infection(sum(get_contagious_contacts(network)), infection_rate)


def start_infection(number_of_infections, network, death_note):
	infection_time = 0
	for _ in range(number_of_infections):
		index_node_for_infection = np.random.randint(0, len(network.infected_nodes))
		infection(index_node_for_infection, infection_time, network, death_note)


def get_time_to_action(current_time, time_to_next_infection, time_step):
	new_time = min(current_time + time_to_next_infection, current_time + time_step - current_time % time_step)
	return round(new_time, 12), round(time_to_next_infection -  (new_time - current_time), 12)


def do_actions(time, network, death_note, treatment_time, critically_treatment_time):
	for i in range(len(network.infected_nodes)):
		# death
		if(network.infected_nodes[i] == 1 and death_note[i] == 1 and time >= network.times_node_infection[i]+critically_treatment_time):
			network.infected_nodes[i] = 0
			network.susceptible_nodes[i][0] = 0
			network.contagious_nodes[i] = 0
			network.graph.vs[i]['color'] = "#9400D3"

		# treatment
		if(network.infected_nodes[i] == 1 and death_note[i] == 0 and time >= network.times_node_infection[i]+treatment_time):
			network.infected_nodes[i] = 0
			network.susceptible_nodes[i][0] = 0
			network.contagious_nodes[i] = 0
			network.graph.vs[i]['color'] = "#ADD8E6"
	#print("infected_nodes: ", infected_nodes)
	#print(treatment_time)


def get_states_info(network, death_note):
	amount_of_infected = sum(network.infected_nodes)
	amount_of_susceptible = sum(network.susceptible_nodes.T[0])
	amount_of_contagious = sum(network.contagious_nodes)
	amount_of_critically_infected = sum([1 for have_to_die, infected in zip(death_note, network.infected_nodes) if(have_to_die == 1 and infected == 1)])
	amount_of_dead = sum([1 for have_to_die, infected in zip(death_note, network.infected_nodes) if(have_to_die == 1 and infected == 0)])
	return amount_of_infected, amount_of_susceptible, amount_of_contagious, amount_of_critically_infected, amount_of_dead


def provide_quorantine_measures(network, current_time, quorantine_measures):
	for measure in quorantine_measures:
		if(current_time == measure['time']):
			network.do_random_quarantine(measure)


def append_data_to_json(filename, newdata):
	if(os.path.exists(filename)):
		data = json.load(open(filename))
	else :
		data = []
	data.append(newdata)

	with open(filename, "w") as outfile:
		json.dump(data, outfile)


#@profile
def simulation(network, infection_rate, number_of_infections, max_time, time_step, i, folder):
	
	death_note = [0 for i in range(network.size)]
	treatment_time = 10
	critically_treatment_time = 10
	current_time = 0
	network_states = []
	states_info = [["time", "amount_of_infected", "amount_of_susceptible", "amount_of_contagious", "amount_of_critically_infected", "amount_of_dead"]]

	all_time = time.time()

	start_infection(number_of_infections, network, death_note)
	time_to_next_infection = get_time_to_infection(np.sum(get_contagious_contacts(network)), infection_rate)

	states_info = [["time", "amount_of_infected", "amount_of_susceptible", "amount_of_contagious", "amount_of_critically_infected", "amount_of_dead"]]
		
	print("current_time: ", current_time)

	while(current_time < max_time):
		current_time, time_to_next_infection = get_time_to_action(current_time, time_to_next_infection, time_step)
		#print("current_time: ", current_time, "\t time to next infection: ", time_to_next_infection)
		if(time_to_next_infection == 0):
			time_to_next_infection = CTMC(network, death_note, treatment_time, critically_treatment_time, infection_rate, current_time)
			#times_to_infections.append(time_to_next_infection)
			#print("new time_to_next_infection: ", time_to_next_infection)
		if(current_time % time_step == 0):
			do_actions(current_time, network, death_note, treatment_time, critically_treatment_time)
			states_info.append([current_time] + list(get_states_info(network, death_note)))
			#provide_quorantine_measures(network, current_time, quorantine_measures)
			g = copy.deepcopy(network.graph)
			network_states.append(g)
	network_states.append(copy.deepcopy(network.graph))
	print("all time: ", time.time() - all_time)

	# print(network.infected_by_nodes)

	with open(folder+'R.txt','a+') as file:
		file.write(str(np.average(network.infected_by_nodes))+";"+str(np.median(network.infected_by_nodes))+";")

	with open(folder + str(i) + '.txt', 'w') as file:
		for row in states_info:
			file.write(','.join([str(a) for a in row]) + '\n')

	return network_states, states_info, network.infected_by_nodes, network.graph.es['infections']


def create_graph(graph_size, amount_of_contacts, network_type, reconnection_rate = 0, network_name = None):
	#print("Graph creation")
	graph = Network_model.create_network(graph_size, amount_of_contacts, network_type, reconnection_rate)
	graph.es['infections'] = np.array([0 for i in range(graph.ecount())])
	return graph
	

if __name__ == "__main__":
	graph_size = 200
	network_type_range =  ['WS']#'Complete'#, "WS", "BA"
	amount_of_contacts_set = [2]

	reconnection_rate_set = [0.3]
	infection_rate_set = [0.15] #, 0.018, 0.016, 0.015, 0.012, 0.01, 0.005]#, 0.05, 0.1, 0.5]
	number_of_infections = 1
	max_time = 100
	time_step = 1
	amount_of_simulations = 50
	amount_of_nodes_for_imunization_set = [int(graph_size * fraction) for fraction in [0.01]]#, 0.05, 0.1, 0.2]]
	death_rate_type = 'different'
	quorantine_measures = ['no', 'adjacency', 'aspl', 'degree', 'non-backtracking']
	quorantine_measures = ['aspl']
	directed = False
	if(network_type_range == ['US']):
		graph_size = 235
		directed = True

	number_of_nodes_for_immunization = 1

	#0.63 * infection_rate
	#R (!!!infection_rate!!!, contagious, suceptibility, network(number of contacts))

	#quorantine_measures = [{'method':'masks', 'influence_susceptibility':0.1, 'influence_contagiousness':0.3, 'amount': graph_size*0.75, 'time':0}]
	#quorantine_measures = [{'method':'no', 'influence_susceptibility':0.1, 'influence_contagiousness':0.3, 'amount': graph_size*0.75, 'time':-1}]

	times = []

	for network_type in network_type_range:
		if network_type == 'Complete':
			amount_of_contacts_set = [0]
		if network_type == 'ER':
			amount_of_contacts_set = [i*graph_size for i in amount_of_contacts_set]
		if network_type != 'WS':
			reconnection_rate_set = [-1]
		start = time.time()
		folder_path = str(pathlib.Path(__file__).parent.absolute()) + "/simulations/"
		print(folder_path)
		for amount_of_nodes_for_imunization in amount_of_nodes_for_imunization_set:
			#quorantine_measures = [{'method':'betweenness_imunization', 'amount': amount_of_nodes_for_imunization}]
			for quorantine_measure in quorantine_measures:
				for amount_of_contacts in amount_of_contacts_set:
					for reconnection_rate in reconnection_rate_set:
						for infection_rate in infection_rate_set:
							for i in range(0, amount_of_simulations):
								#adjacency_matrix = np.array(list(Network_model.create_network(graph_size, amount_of_contacts, network_type, reconnection_rate).get_adjacency()))
								graph = create_graph(graph_size, amount_of_contacts, network_type, reconnection_rate)
								simulation(graph, graph_size, network_type, amount_of_contacts, infection_rate, number_of_infections, death_rate_type, max_time, time_step, i, folder_path, reconnection_rate, quorantine_measure, directed, number_of_nodes_for_immunization)
		times.append(time.time() - start)
	print(sum(times)/amount_of_simulations)

								#simulation(graph, graph_size, network_type, amount_of_contacts, infection_rate, number_of_infections, death_rate_type, max_time, time_step, i, folder, reconnection_rate = -1, quorantine_measures = "")
