import igraph
#import numba
#from numba import cuda
#from numba import jit
from scripts import Network_model
from scripts import Population 
import time
import numpy as np
import math
import matplotlib.pyplot as plt
from pprint import pprint
import os
from os import path
from scripts import Network
from memory_profiler import profile
import tracemalloc

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
    #print(sum(contagious_of_contacts))
    return contagious_of_contacts


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
            network.infected_by_nodes[i] += 1
            contact_for_infection = np.random.randint(0, contagious_contacts[i], 1)
            indexes_of_possible_nodes = np.argwhere(np.multiply(network.adjacency_matrix[i], network.susceptible_nodes.T[0]) == 1)
            #print(indexes_of_possible_nodes)
            #print("\n\n\n\nneeded value: ", indexes_of_possible_nodes[contact_for_infection][0][0], type( indexes_of_possible_nodes[contact_for_infection][0][0]), "\n\n\n")
            return  indexes_of_possible_nodes[contact_for_infection][0][0]


def get_time_to_infection(contagious_contacts_concentration, infection_rate):
    if(contagious_contacts_concentration <= 0):
        return math.inf
    return round(np.random.exponential(1/(contagious_contacts_concentration * infection_rate)),12) # expected value - contagious_contacts_concentration.
    #return round(1/contagious_contacts_concentration)


def infection(index_node_for_infection, infection_time, network, death_note):
    prob_of_death = 0.01820518643617639 + 0.2
    network.infected_nodes[index_node_for_infection] = 1
    network.susceptible_nodes[index_node_for_infection][0] = 0
    network.contagious_nodes[index_node_for_infection] = 1
    network.times_node_infection[index_node_for_infection] = infection_time
    network.colors[index_node_for_infection] = "#00FF00"
    if(np.random.uniform(0.0, 1.0) <= network.death_probabilities[index_node_for_infection] + 0.2):
        death_note[index_node_for_infection] = 1 #die with probability
        network.colors[index_node_for_infection] = "#FF0000"


def CTMC(network, death_note, treatment_time, critically_treatment_time, infection_rate = 0.01, time = 0):
    do_actions(time, network, death_note, treatment_time, critically_treatment_time)
    contagious_contacts = get_contagious_contacts(network)
    contagious_contacts_concentration = sum(contagious_contacts)
    if(contagious_contacts_concentration <= 0):
        # what can i do?
        print("No contacts with contagious nodes left")
        return get_time_to_infection(-1, infection_rate)
    index_node_for_infection = infection_roulette_wheel_choise(network, contagious_contacts,contagious_contacts_concentration)
    infection(index_node_for_infection, time, network, death_note)
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
            network.colors[i] = "#9400D3"

        # treatment
        if(network.infected_nodes[i] == 1 and death_note[i] == 0 and time >= network.times_node_infection[i]+treatment_time):
            network.infected_nodes[i] = 0
            network.susceptible_nodes[i][0] = 0
            network.contagious_nodes[i] = 0
            network.colors[i] = "#ADD8E6"
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


def get_folder_name(graph_size, network_type, amount_of_contacts, infection_rate):
    return "size: {}, network: {}, node_contacts: {}, infection_rate: {}/".format(
                    graph_size, network_type, amount_of_contacts, infection_rate)

#@profile
def simulation(graph_size, network_type, amount_of_contacts, infection_rate, number_of_infections, max_time, time_step, i, folder, quorantine_measures = ""):
    folder = folder + get_folder_name(graph_size, network_type, amount_of_contacts, infection_rate)
    if(path.exists(folder) == False):
        os.makedirs(folder)
        print("Created!")
    print(network_type)
    death_note = [0 for i in range(graph_size)]
    treatment_time = 10
    critically_treatment_time = 14
    current_time = 0
    network_states = []

    all_time = time.time()
    print("Network was created")
    #print(list(graph.get_adjacency()))
    #graph = Network_model.imunize(graph, quorantine_measures[0]['method'], quorantine_measures[0]['amount'])
    network = Network.Network(np.array(list(Network_model.create_network(graph_size, amount_of_contacts, network_type).get_adjacency())), Population.get_population())
    print("adjecency matrix was got")
    #provide_quorantine_measures(network, current_time, quorantine_measures)

    start_infection(number_of_infections, network, death_note)
    time_to_next_infection = get_time_to_infection(np.sum(get_contagious_contacts(network)), infection_rate)
    
    #times_to_infections = [time_to_next_infection]

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
            graph = igraph.Graph.Adjacency(network.adjacency_matrix, mode = "undirected")
            graph.vs['color'] = network.colors
            network_states.append(graph)
            #igraph.plot(graph, " /run/media/fedora_user/31614d99-e16f-45e1-8be5-e21723cf8199/projects/ManagingEpidemicOutbreak/Python-v.0.1/test.png")
    network_states.append(graph)
    print("all time: ", time.time() - all_time)

    #print(network.infected_by_nodes)
    with open(folder+'R.txt','a+') as file:
        file.write(str(np.average(network.infected_by_nodes))+";"+str(np.median(network.infected_by_nodes))+";")

    with open(folder + str(i) + '.txt', 'w') as file:
        for row in states_info:
            file.write(','.join([str(a) for a in row]) + '\n')

    return network_states, states_info

# graph_size = (10 ** 3) * 1
# network_type = 'WS' #'Barabasi', 'Complete'
# amount_of_contacts_set = [10]#,2,4,10]
# if network_type == 'Complete':
#     amount_of_contacts_set = [0]
# infection_rate_set = [0.02, 0.018, 0.016, 0.015, 0.012, 0.01, 0.005]#, 0.05, 0.1, 0.5]
# number_of_infections = 1
# max_time = 100
# time_step = 1
# amount_of_simulations = 100
# amount_of_nodes_for_imunization_set = [int(graph_size * fraction) for fraction in [0.01]]#, 0.05, 0.1, 0.2]]


# #0.63 * infection_rate
# #R (!!!infection_rate!!!, contagious, suceptibility, network(number of contacts))

# #quorantine_measures = [{'method':'masks', 'influence_susceptibility':0.1, 'influence_contagiousness':0.3, 'amount': graph_size*0.75, 'time':0}]
# #quorantine_measures = [{'method':'no', 'influence_susceptibility':0.1, 'influence_contagiousness':0.3, 'amount': graph_size*0.75, 'time':-1}]
# times = []
# am = 1
# for i in range(am):
#     start = time.time()
#     folder_path = "/home/data/projects/ManagingEpidemicOutbreak/Python-v.0.1/simulations/"
#     for amount_of_nodes_for_imunization in amount_of_nodes_for_imunization_set:
#         #quorantine_measures = [{'method':'betweenness_imunization', 'amount': amount_of_nodes_for_imunization}]
#         quorantine_measures = [{'method':'no', 'amount': amount_of_nodes_for_imunization}]
#         for amount_of_contacts in amount_of_contacts_set:
#             for infection_rate in infection_rate_set:
#                 folder_name = "size: {}, network: {}, node_contacts: {}, infection_rate: {}/".format(
#                     graph_size, network_type, amount_of_contacts, infection_rate)

#                 data_path = folder_path + folder_name
#                 if(path.exists(data_path) == False):
#                     os.makedirs(data_path)
#                     print("Created!")
#                 if(os.path.exists(data_path+"R.txt")):
#                     os.remove(data_path+"R.txt")
                
#                 for i in range(0, amount_of_simulations):
#                     file_name = ""
#                     simulation(graph_size, network_type, amount_of_contacts, infection_rate, number_of_infections, max_time, time_step, i, data_path, quorantine_measures)
#     times.append(time.time() - start)
# print(sum(times)/am)