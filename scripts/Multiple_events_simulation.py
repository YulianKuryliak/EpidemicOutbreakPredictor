from cmath import nan
import numpy as np
from sklearn import neighbors
import Multiple_events_network as Network
import Population
import Network_model
from colorama import Fore, Back, Style
import copy
import pandas as pd
import os
from os import path

list_infected = []

# values and rates are dictionaries
def CTMC(network, rates, time):
    values = get_probabilities(network, time) # dict of np.arrays {'infection': np.array, 'threatment': , 'adding_edge': , 'removing_edge':}
    event_probs = np.array([sum(value) * rates[key] for key, value in values.items() if key in rates]) # sum(event_value) * rate
    a = 0
    sum_prob = np.sum(event_probs)
    if(sum_prob <= 0 or len(event_probs) == 0):
        return network, np.inf
    print('event_probs: ', event_probs)
    event = roulette_wheel(event_probs) # !!! NOTHING
    print(Fore.RED + 'time:' + Fore.WHITE, time)
    match event:
        case 0:
            do_infection(network, values['infection'], time)
        case 1:
            do_threatment(network, values['threatment'])
        case 2:
            do_adding_edge(network, values['adding_edge'])
        case 3:
            do_removing_edge(network, values['removing_edge'])
    
    event_probs = np.array([sum(value) * rates[key] for key, value in get_probabilities(network, time).items() if key in rates])
    if(np.sum(event_probs) <= 0 or len(event_probs) == 0):
        return network, np.inf
    return network, get_time_to_new_event(event_probs)


# prob_list - numpy.array
def roulette_wheel(prob_list, network = nan, one = nan, two = nan):
    print("prob_list", prob_list)
    sum_prob = np.sum(prob_list)
    normalized_probs = np.array(prob_list) / sum_prob
    cum_probs = np.cumsum(normalized_probs)
    print("cum_probs len", len(cum_probs))
    rand_value = np.random.uniform(0,1,1)
    return np.where(cum_probs > rand_value)[0][0] #index 0 is out of bounds for axis 0 with size 0


def get_probabilities(network, time):
    return {'infection': get_infection_probabilities(network), 
            'threatment': get_treatment_probabilities(network, time), 
            'adding_edge': get_edge_adding_probabilities(network),
            'removing_edge': get_edge_removing_probabilities(network)
            }


def get_infection_probabilities(network):
    #return network.infected_neighbors * (1 - network.network.infection_state)
    if (any(network.infection_state  * network.susceptible_neighbors < 0)):
        a = 0
    return network.infection_state * network.susceptible_neighbors


#time of infication should be taken into account
def get_treatment_probabilities(network, time):
    return np.nan_to_num((time - network.time_infection) * network.infection_state)
    # (time - min(time, network.time_infection)) * network.infection_state

def get_edge_adding_probabilities(network):
    probs = copy.deepcopy(network.degrees)
    probs[np.where(probs >= network.size - 1)] = 0
    probs[np.where(probs == 0)] = 1
    return probs


def get_edge_removing_probabilities(network):
    probs = copy.deepcopy(network.degrees)
    return probs


def do_infection(network, prob_list, time):
    print(Fore.RED + 'i am infection'+ Fore.WHITE)
    # choose which node will infect # prob_list = network.infection_state * network.susceptible_neighbors
    infects = roulette_wheel(prob_list)
    # get neighbors of a node
    susceptible_neighbors = get_susceptible_neighbors(network, infects)
    if(len(susceptible_neighbors) < 1):
        a = 0
    get_infected = susceptible_neighbors[roulette_wheel(np.ones(len(susceptible_neighbors)))]
    network = infection(network, time, get_infected, infects)
    return network


def get_susceptible_neighbors(network, node):
    neighbors = np.array(network.graph.get_adjlist()[node])
    neighbors_states = np.take(network.susceptible_state, neighbors)
    return neighbors[neighbors_states == 1]


def infection(network, time, get_infected, infects = -1):
    network.infection_state[get_infected] = 1
    network.susceptible_state[get_infected] = 0
    network.time_infection = time
    # Counting the number of infections caused by the node
    if(infects != -1) : network.infected_by_node[infects] += 1
    # update network.susceptible_neighbors for all neighbors
    list_infected.append(get_infected)
    for neighbor in network.graph.get_adjlist()[get_infected]: # probably, something wrong with network.graph.get_adjlist()
        network.susceptible_neighbors[neighbor] -= 1 #incorrect?
    return network


def do_threatment(network, prob_list, epid_model = 'SIR'):
    print(Fore.GREEN + 'i am treatment'+ Fore.WHITE)
    get_threated = roulette_wheel(prob_list)
    network.infection_state[get_threated] = 0
    return network


def do_adding_edge(network, prob_list):
    print(Fore.GREEN + 'i am adding an edge'+ Fore.WHITE)    
    #node_one = np.random.randint(0, network.size)
    node_one = roulette_wheel(prob_list)
    copy_probs = copy.deepcopy(prob_list)
    adj_list = network.graph.get_adjlist()
    adjecent_nodes = network.graph.get_adjlist()[node_one]
    prob_list[adjecent_nodes] = 0
    copy1_probs = copy.deepcopy(prob_list)
    prob_list[node_one] = 0
    if(sum(prob_list) <= 0):
        a = 0
    #print('degrees: ', network.degrees)
    node_two = roulette_wheel(prob_list, network, node_one)
    #print("node one:", node_one, " degree one: ", network.degrees[node_one], "node two:", node_two, "degree two: ", network.degrees[node_two])
    network.graph.add_edge(node_one, node_two)
    network = uptate_states(network, node_one, node_two, mode = 'add')
    network = update_edges_list(network, node_one, node_two)
    #print("node one:", node_one, " degree one: ", network.degrees[node_one], "node two:", node_two, "degree two: ", network.degrees[node_two])
    return network


def do_removing_edge(network, prob_list):
    print(Fore.GREEN + 'i am removing an edge' + Fore.WHITE)
    node_one = roulette_wheel(prob_list)
    neighbors_probs = np.ones(len(network.graph.get_adjlist()[node_one]))
    #print("neighbors_probs: ", neighbors_probs)
    #print('neighbors: ', network.graph.get_adjlist()[node_one])
    #print('degrees: ', network.degrees)
    #if len(network.graph.get_adjlist()[node_one]) <= 0:
        #print('no neighbors')
        #print('neighbors: ', network.graph.get_adjlist()[node_one])
        #print('prob:', prob_list[node_one])
    node_two = network.graph.get_adjlist()[node_one][roulette_wheel(neighbors_probs)]
    #print("node one:", node_one, " degree one: ", network.degrees[node_one], "node two:", node_two, "degree two: ", network.degrees[node_two])
    network.graph.delete_edges([(node_one, node_two)]) #check if (node_two, node_one) is also deleted
    network = uptate_states(network, node_one, node_two, mode = 'remove')
    network = update_edges_list(network, node_one, node_two)
    #print("node one:", node_one, " degree one: ", network.degrees[node_one], "node two:", node_two, "degree two: ", network.degrees[node_two])
    return network


def uptate_states(network, node_one, node_two, mode):
    value = 0
    if mode == 'add':
        value = 1
    elif mode == 'remove':
        value = -1
    else:
        return nan

    print("degrees: ", network.degrees)
    network.degrees[node_one] += value
    network.degrees[node_two] += value
    print("degrees: ", network.degrees)

    if network.susceptible_state[node_one] == 1:
        network.susceptible_neighbors[node_two] += value
    if network.susceptible_state[node_two] == 1:
        network.susceptible_neighbors[node_one] += value

    return network


def update_edges_list(network, node_one, node_two):
    return network


def get_time_to_new_event(prob_list):
    # time to a new event should be like:
    #   exp(1 / (infection + threatment + edge_adding + edge_removing)
    return round(np.random.exponential(1/(np.sum(prob_list))),12)


def initial_infection(network, number_to_infect = 1, list_of_indexes_to_infect = []):
    if list_of_indexes_to_infect == []:
        list_of_indexes_to_infect = np.random.randint(network.size, size=number_to_infect)
    for index_to_infect in list_of_indexes_to_infect:
        infection(network, time = 0, get_infected = index_to_infect)
    

def get_node_states(network, time):
    node_states = {
        'time': [time],
        'infected': [np.sum(network.infection_state)],
        'susceptible': [network.size - np.sum(network.susceptible_state)]
    }
    return node_states


def collect_states_data(network, time, timestep, time_to_event, max_time):
    print("time_to_event: ", time_to_event)
    first_time = time - (time % timestep) + timestep
    temp_time = first_time

    some_df = pd.DataFrame()
    node_states = pd.DataFrame(get_node_states(network, time))

    while temp_time < min(time + time_to_event, max_time):
        some_df = some_df.append(node_states)
        temp_time += timestep
    return some_df


def initialize_network(graph_size, amount_of_contacts, network_type, reconnection_rate):
    graph = Network_model.create_network(graph_size, amount_of_contacts, network_type, reconnection_rate)
    return Network.Network(graph, Population.get_population())
    

def get_folder_name(graph_size, network_type, amount_of_contacts, rates):
    folder_name = "temporal network/size: {}, network: {}, node_contacts: {}, infection_rate: {}, threatment_rate: {}, adding_edge_rate: {}, removing_edge_rate: {}/".format(
        graph_size, network_type, amount_of_contacts, np.format_float_positional(rates['infection']), np.format_float_positional(rates['threatment']), np.format_float_positional(rates['adding_edge']), np.format_float_positional(rates['removing_edge']))
    return folder_name
    
# def get_folder_name(graph_size, network_type, amount_of_contacts, infection_rate, death_rate_type, reconnection_rate=-1, quorantine_measures = -1, number_of_nodes_for_immunization = ""):
#     if(reconnection_rate != -1):
#         return "size: {}, network: {}, node_contacts: {}, reconnection_rate: {}, infection_rate: {}, death_rate: {}, quorantine: {}_{}/".format(
#                     graph_size, network_type, amount_of_contacts, np.format_float_positional(reconnection_rate), np.format_float_positional(infection_rate), death_rate_type, quorantine_measures, number_of_nodes_for_immunization)
#     return "size: {}, network: {}, node_contacts: {}, infection_rate: {}, death_rate: {}, quorantine: {}_{}/".format(
#                     graph_size, network_type, amount_of_contacts, np.format_float_positional(infection_rate), death_rate_type, quorantine_measures, number_of_nodes_for_immunization)


def create_folder(folder):
    print(folder)
    if(path.exists(folder) == False):
        os.makedirs(folder)
        print("Created!")


def write_data(graph_size, network_type, amount_of_contacts, event_rates, node_states_history, simulation_id, path):
    folder_name = get_folder_name(graph_size, network_type, amount_of_contacts, event_rates)
    create_folder(path + folder_name)
    print(node_states_history)
    with open(folder_name + str(simulation_id) + '.txt', 'w') as file:
        node_states_history.to_csv(file)


def simulation(graph_size, amount_of_contacts, network_type, reconnection_rate, timestep, max_time, event_rates, simulation_id = 0, path = '/home/data/projects/ManagingEpidemicOutbreak/EpidemicOutbreakPredictor/scripts/simulations/'):
    network = initialize_network(graph_size, amount_of_contacts, network_type, reconnection_rate)
    initial_infection(network)

    time = 0
    node_states_history = pd.DataFrame(get_node_states(network, time))

    while time < max_time:
        network, time_to_event = CTMC(network, event_rates, time)
        node_states_history = node_states_history.append(collect_states_data(network, time, timestep, time_to_event, max_time))
        time += time_to_event
    a = 0
    #write_data(graph_size, network_type, amount_of_contacts, event_rates, node_states_history, simulation_id, path)
    print(np.array(network.graph.get_adjacency().data))
    return network


def run():
    graph_size = 10
    amount_of_contacts = 2
    network_type = 'BA'
    reconnection_rate = 0
    timestep = 1
    max_time = 100
    event_rates = {'infection': 0.2, 
        'threatment': 0.1, 
        'adding_edge': 0.01,
        'removing_edge': 0.01
        }

    simulation(graph_size, amount_of_contacts, network_type, reconnection_rate, timestep, max_time, event_rates)



if __name__ == '__main__':
    run()
    


# передавати ліст івентів і ліст дискретний операцій.
# На фронті можна поробити свічі з визначенням дискретного часу для операції чи зробити її івентом

# ! проблема, якщо видалити останнє ребро вузла, він більше не під'єднається
# Пропоноване вирішення: Встановити вагу приєдення для вузліть 0 степеня 1 або меншу

# ? . Якщо кількість івентів на видалення переважає чи буде кількість цих івентів збільшувати перевагу з часом?