from cProfile import label
from webbrowser import get
from numpy import NaN, genfromtxt
import numpy as np
import matplotlib.pyplot as plt
from os import path
import os
import pandas as pd
import operator
import Network_properties_data
import json


parent_path = "/home/data/projects/ManagingEpidemicOutbreak/EpidemicOutbreakPredictor/scripts/simulations/"
mean_type = 'average'
np.set_printoptions(formatter={'float_kind':'{:f}'.format})


def get_data(directory, amount_of_files, extension):
    data = []
    #print(os.listdir(directory))
    files = [os.path.join(directory, file_name) for file_name in os.listdir(directory) if os.path.isfile(os.path.join(directory, file_name)) and 'R.txt' not in file_name and 'properties' not in file_name]

    for file in files:
        #print(file)
        #print(os.path.isfile(file))
        new_data = genfromtxt(file, delimiter=',')[1:101]
        new_data = np.insert(new_data, 0, [0,1,0,0,0,0], 0)
        data.append(new_data)
    return np.array(data, dtype=int)


def get_R(dir):
    data = np.array([])
    # with open(path+"R.txt") as file:
    #     for line in file:
    #         print(line)
    data = np.append(data,np.array(genfromtxt(dir+ "R.txt", delimiter=';')))
    data = np.delete(data,-1)
    data = np.reshape(data, (-1, 2))
    return data.T


def get_mean(data, mean_type='average'):
    if(mean_type == 'average'):
        mean = np.mean(data, axis=0)
    if(mean_type == 'median'):
        mean = np.median(data, axis = 0)
    return mean


def plot(data, language, label, mode = "I", marker = ".", color = 'black', size = 6.0):
    if(language == 'python' or language == 'Python'):
        index_1 = 0
        index_2 = 1
        index_3 = 4
    if(language == 'r' or language == 'R'):
        index_1 = 1
        index_2 = 2
    if(mode == "I"):
        plt.plot(data.T[index_1], data.T[index_2], label = label, color = color, marker = marker, markersize = size)
    if(mode == "CI"):
        plt.plot(data.T[index_1], data.T[index_3], label = label+" CI", color = color, marker = marker, markersize = size)


def get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, recconection_rate="", quorantine = "", number_of_nodes_for_immunzation = ""):
    #Python only
    path_to_data = parent_path + "size: {}, network: {}, node_contacts: {}, infection_rate: {}, death_rate: {}/".format(
    network_size, network_type, amount_of_contacts, np.format_float_positional(infection_rate), death_rate_type)
    if(recconection_rate != ""):
        path_to_data = parent_path + "size: {}, network: {}, node_contacts: {}, reconnection_rate: {}, infection_rate: {}, death_rate: {}/".format(
    network_size, network_type, amount_of_contacts, recconection_rate, np.format_float_positional(infection_rate), death_rate_type)
    if(quorantine != "" and number_of_nodes_for_immunzation != ""):
        path_to_data = path_to_data[:-1] + ", quorantine: {}_{}/".format(quorantine, number_of_nodes_for_immunzation)
    if(quorantine != "" and number_of_nodes_for_immunzation == ""):
        path_to_data = path_to_data[:-1] + ", quorantine: {}/".format(quorantine)
    
    return path_to_data


def get_amount_of_files(path):
    amount_of_files = 0
    for base, dirs, files in os.walk(path):
        for Files in files:
            amount_of_files += 1
    return amount_of_files - 1


def get_mean_values(dataset, mean_type='median', time = 50):
    mean_values = pd.DataFrame(dataset[0][:time], columns=['time','amount_of_infected','amount_of_susceptible','amount_of_contagious','amount_of_critically_infected','amount_of_dead'])
    for i in mean_values.columns:
        mean_values[i] = mean_values[i].astype(float)
    for j in range(len(mean_values)):
        for k in range(len(mean_values.columns)):
            values = []
            for i in range(len(dataset)):
                #print(k)
                values.append(dataset[i][j][k])
            if(mean_type == 'average'):
                mean_values.iat[j, k] = np.average(values)
            mean_values.iat[j, k] = np.median(values)
    return mean_values


def get_deviations(dataset, mean_values, deviation_value = 0.3):
    mean_values = mean_values.assign(dl_infected = 0, du_infected = 0, dl_critically_infected = 0, du_critically_infected = 0, dl_dead = 0, du_dead = 0, sd_infected = 0)
    #print("\n\n\\n\n", mean_values, "\n\n\n\\n\n")

    for j in range(len(mean_values)):
        infecteds = []
        critically_infecteds = []
        deads = []
        for i in range(len(dataset)):
            infecteds.append(dataset[i][j][1])
            critically_infecteds.append(dataset[i][j][4])
            deads.append(dataset[i][j][5])
        infecteds.sort()
        #print("j: ", j, " infecteds : ", infecteds)
        
        mean_values.at[j, 'dl_infected'], mean_values.at[j, 'du_infected'] = deviation(infecteds, deviation_value, mean_values.at[j, 'amount_of_infected'])
        mean_values.at[j, 'sd_infected'] = np.std(infecteds)
        mean_values.at[j, 'dl_critically_infected'], mean_values.at[j, 'du_critically_infected'] = deviation(critically_infecteds, deviation_value, mean_values.at[j, 'amount_of_critically_infected'])
        mean_values.at[j, 'dl_dead'], mean_values.at[j, 'du_dead'] = deviation(deads, deviation_value, mean_values.at[j, 'amount_of_dead'])
    return mean_values


def deviation(values, deviation, mean):
    values.sort()
    return mean - values[int(len(values) * (0.5 - deviation))], values[int(len(values) * (0.5 + deviation)) - 1] - mean


def find_error_deviations(dataset, folder, time_max = 100, time_step = 1, deviation = 0.3, mean_type='median'):    
    pd.set_option('display.max_rows', None)
    mean_values = get_mean_values(dataset, mean_type)
    #print(mean_values)
    mean_values = get_deviations(dataset, mean_values, deviation_value=deviation)
    # #mean_values = mean_values.sort_index()
    # #mean_values = mean_values.reset_index()
    # #print(mean_values)
    if(not path.exists(folder)):
        os.makedirs(folder.replace("simulations","simulations/Analysis"))
    mean_values.to_csv(folder.replace("simulations","simulations/Analysis") + "mean_data.csv", index=True)
    #mean_values.to_excel(folder_title.replace("simulations","analysis") + "mean_data.xlsx", index=True)
    return mean_values


def plot_error_deviations(data, markers, colors, labels, shifts, markersize = 6.0):
    plt.errorbar(data.time - shifts[0], data.amount_of_infected, yerr=[data.dl_infected, data.du_infected], fmt=markers[0], color = colors[0], label=labels[0], markersize=markersize)
    plt.plot(data.time, data.amount_of_infected, color=colors[0], markersize=markersize)
    plt.errorbar(data.time - shifts[1], data.amount_of_critically_infected, yerr=[data.dl_critically_infected, data.du_critically_infected], fmt=markers[1], color = colors[1], label=labels[1], markersize=markersize)
    plt.plot(data.time, data.amount_of_critically_infected, color=colors[1])
    plt.xlabel('Time(days)', fontsize=20)
    plt.ylabel('Amount of nodes', fontsize=20)


def correlation_analysis(data, min_time, max_time):
    #print("Data on range [{} ; {}]".format(min_time, max_time))
    infected = data.amount_of_infected[min_time:max_time]
    critically_infected = data.amount_of_critically_infected[min_time:max_time]
    correlation = critically_infected.corr(infected)
    #print("Correlation coefitient : {}".format(correlation))

    dependency = data.amount_of_critically_infected[min_time:max_time] / data.amount_of_infected[min_time:max_time]
    #print(dependency)
    #print("median = ", np.median(dependency), " avg = ", np.average(dependency), " sd = ", np.std(dependency))
    print("{}-{} & {} & {} & {} \\\\".format(min_time, max_time, round(np.median(dependency), 3), round(np.average(dependency), 3), round(correlation, 3)))




def experiment_1(mean_type = 'median', markersize=6.0):

    #python data
    network_size = 10000
    network_type = 'Complete'
    amount_of_contacts = 0
    infection_rate = 0.00005
    death_rate_type = 'different'
    parent_path = "/home/data/projects/ManagingEpidemicOutbreak/Python-v.0.1/simulations/"
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    #print(path.exists(data_path))
    #print(data_path)
    amount_of_files = get_amount_of_files(data_path)
    #print(amount_of_files)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)
    #plot(mean, 'Python', 'DR: Different')
    error_deviations = find_error_deviations(data, data_path)
    print("death_rate_type = ", death_rate_type)
    print("PIN: ", get_max_values(mean, "I"))
    print("PCIN: ", get_max_values(mean, "CI"))

    #print("\n\n\n\n\n\\n", data, "\n\n\n\\n")

    markers = ['s','o']
    colors = ['black', 'black']
    labels = ['IU, same CIP', 'CIU, same CIP']
    shifts = [0.25, 0.2]

    plot_error_deviations(error_deviations, markers, colors, labels, shifts, markersize=markersize)

    correlation_analysis(error_deviations, min_time=0, max_time = len(error_deviations))
    correlation_analysis(error_deviations, min_time=10, max_time = len(error_deviations)-10)
    correlation_analysis(error_deviations, min_time=15, max_time = len(error_deviations)-15)
    correlation_analysis(error_deviations, min_time=0, max_time = 24)
    correlation_analysis(error_deviations, min_time=10, max_time = 24)
    correlation_analysis(error_deviations, min_time=24, max_time = 50)
    correlation_analysis(error_deviations, min_time=24, max_time = 40)

    print("\n\n\nSAME")

    death_rate_type = 'same'
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    #print(path.exists(data_path))
    #print(data_path)
    amount_of_files = get_amount_of_files(data_path)
    #print(amount_of_files)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)
    #plot(mean, 'Python', 'DR: Same')
    print("death rate type: ",death_rate_type)
    print("PIN: ", get_max_values(mean, "I"))
    print("PCIN: ", get_max_values(mean, "CI"))

    error_deviations = find_error_deviations(data, data_path)

    markers = ['v','^']
    colors = ['black', 'black']
    labels = ['IU, weighted CIP', 'CIU, weighted CIP']
    shifts = [-0.15, -0.2]

    plot_error_deviations(error_deviations, markers, colors, labels, shifts, markersize=markersize)

    correlation_analysis(error_deviations, min_time=0, max_time = len(error_deviations))
    correlation_analysis(error_deviations, min_time=10, max_time = len(error_deviations)-10)
    correlation_analysis(error_deviations, min_time=15, max_time = len(error_deviations)-15)
    correlation_analysis(error_deviations, min_time=0, max_time = 24)
    correlation_analysis(error_deviations, min_time=10, max_time = 24)
    correlation_analysis(error_deviations, min_time=24, max_time = 50)
    correlation_analysis(error_deviations, min_time=24, max_time = 40)


def experiment_2_1(mode = 'I'):

    network_type = 'ER'
    base_amount_of_contacts = 4
    amount_of_contacts = base_amount_of_contacts

    network_size = 10000
    biggest = 10000
    if(network_type == 'ER'):
        amount_of_contacts = base_amount_of_contacts * network_size
    infection_rate = 0.1
    death_rate_type = 'different'
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    print(path.exists(data_path))
    print(data_path)
    amount_of_files = get_amount_of_files(data_path)
    print(amount_of_files)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)
    mean[:,1] /= network_size
    mean[:,4] /= network_size
    marker = "s"
    color = 'black'
    plot(mean, 'Python', network_type + str(network_size), mode, marker, color)

    # network_size = 5000
    # if(network_type == 'ER'):
    #     amount_of_contacts = base_amount_of_contacts * network_size
    # data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    # print(path.exists(data_path))
    # print(data_path)
    # amount_of_files = get_amount_of_files(data_path)
    # print(amount_of_files)
    # data = get_data(data_path, amount_of_files, 'txt')
    # mean = get_mean(data, mean_type)
    # mean[:,1] /= network_size
    # mean[:,4] /= network_size
    # marker = "*"
    # color = 'black'
    # plot(mean, 'Python', network_type + str(network_size), mode, marker, color)

    network_size = 2000
    if(network_type == 'ER'):
        amount_of_contacts = base_amount_of_contacts * network_size
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    print(path.exists(data_path))
    print(data_path)
    amount_of_files = get_amount_of_files(data_path)
    print(amount_of_files)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)
    mean[:,1] /= network_size
    mean[:,4] /= network_size
    marker = "X"
    color = 'black'
    plot(mean, 'Python', network_type + str(network_size), mode, marker, color)


    network_size = 1000
    if(network_type == 'ER'):
        amount_of_contacts = base_amount_of_contacts * network_size
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    print(path.exists(data_path))
    print(data_path)
    amount_of_files = get_amount_of_files(data_path)
    print(amount_of_files)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)
    mean[:,1] /= network_size
    mean[:,4] /= network_size
    marker = "o"
    color = 'black'
    plot(mean, 'Python', network_type + str(network_size), mode, marker, color)


    network_size = 500
    if(network_type == 'ER'):
        amount_of_contacts = base_amount_of_contacts * network_size
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    print(path.exists(data_path))
    print(data_path)
    amount_of_files = get_amount_of_files(data_path)
    print(amount_of_files)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)
    mean[:,1] /= network_size
    mean[:,4] /= network_size
    marker = "+"
    color = 'black'
    plot(mean, 'Python', network_type + str(network_size), mode, marker, color)

    plt.xlabel("Day", fontsize=16)
    plt.ylabel("Part of infected", fontsize=16)

    network_size = 200
    if(network_type == 'ER'):
        amount_of_contacts = base_amount_of_contacts * network_size
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type)
    print(path.exists(data_path))
    print(data_path)
    amount_of_files = get_amount_of_files(data_path)
    print(amount_of_files)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)
    mean[:,1] /= network_size
    mean[:,4] /= network_size
    marker = "P"
    color = 'black'
    plot(mean, 'Python', network_type + str(network_size), mode, marker, color)

    plt.xlabel("Day", fontsize=16)
    plt.ylabel("Part of infected", fontsize=16)


def exp_2_plot(network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, label, color = 'black', marker = "s", mode = "I", recconection_rate = "", quorantine = "", number_of_nodes_for_immunzation = ""):
    data_path = get_path(parent_path, network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, recconection_rate, quorantine, number_of_nodes_for_immunzation)
    properties = get_network_properties(data_path)
    #         {Network model} &
    #     {CCG} & % Clustering coefficient (global)
    #     {NACC} & % Network average clustering coefficient
    #     {ADN} & % Average degree of node
    #     {MDN} & %Median degree of node
    #     {D} & % Diameter of network 
    #     {ASPL} % Average shortest path length
    print(data_path)
    if(properties is not None):
        print("{} {} & {} & {} & {} & {} & {} & {} \\\\".format(properties['Network model'], properties['Reconnection probability'], round(properties['Global clustering coefitient'],3), round(properties['Network average clustering coefficient'],3), round(properties['Average degree'],3), round(properties['Median degree'],3), round(properties['Diameter of network'],3), round(properties['Average shortest path length'],3)))
    amount_of_files = get_amount_of_files(data_path)
    data = get_data(data_path, amount_of_files, 'txt')
    mean = get_mean(data, mean_type)[:41]
    plot(mean, 'Python', label, mode, marker, color, size = 5)
    

def experiment_2(infection_mode = "I", value_mode = 'amount'):
    # value_mode = 'amount' / 'time'

    network_size = 10000
    network_type = 'BA'
    amount_of_contacts = 4
    infection_rate = 0.1
    death_rate_type = 'different'
    marker = "s"
    color = 'black'
    label = "BA"
    exp_2_plot(network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, label, color, marker, infection_mode)
    
    network_type = 'WS'
    recconection_rate = 0.1
    marker = "o"
    color = 'black'
    label = 'WS {}'.format(recconection_rate)
    exp_2_plot(network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, label, color, marker, infection_mode, recconection_rate)
    
    recconection_rate = 0.2
    marker = "x"
    color = 'black'
    label = 'WS {}'.format(recconection_rate)
    exp_2_plot(network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, label, color, marker, infection_mode, recconection_rate)
    
    recconection_rate = 0.5
    marker = "v"
    color = 'black'
    label = 'WS {}'.format(recconection_rate)
    exp_2_plot(network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, label, color, marker, infection_mode, recconection_rate)

    network_type = 'ER'
    amount_of_contacts = network_size * amount_of_contacts
    marker = "P"
    color = 'black'
    label = 'ER'
    exp_2_plot(network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, label, color, marker, infection_mode)

    # network_type = 'Complete'
    # amount_of_contacts = 0
    # infection_rate = 0.002
    # marker = "o"
    # color = 'black'
    # label = 'Complete'
    # exp_2_plot(network_size, network_type, amount_of_contacts, infection_rate, death_rate_type, label, color, marker, mode)

    #max(mean, key=operator.itemgetter(column))[column]


def get_max_values(mean_data, mode='I'):
    if(mode == 'I'):
        column = 1
    if(mode == 'CI'):
        column = 4
    print(type(mean_data))
    max_day = max(mean_data, key=operator.itemgetter(column))
    return {'day':max_day[0], 'value':max_day[column]}


def get_folder_names(parent_path, network_size, network_type, amount_of_contacts, death_rate, recconection_rate = -1, infection_rate = -1):
    all_dirs = os.listdir(parent_path)
    if(infection_rate == -1):

        if(network_type != 'WS'):
            params_dirs = [parent_path + dir + "/" for dir in all_dirs if("size: {}, network: {}, node_contacts: {},".format(network_size, network_type, amount_of_contacts) in dir and 
                                                    "death_rate: {}".format(death_rate) in dir)]
        else:
            params_dirs = [parent_path + dir for dir in all_dirs if("size: {}, network: {}, node_contacts: {}, reconnection_rate: {},".format(network_size, network_type, amount_of_contacts, recconection_rate) in dir and 
                                                    "death_rate: {}".format(death_rate) in dir)]
        for name in params_dirs: print(name) 
        return params_dirs
    elif(network_type == 'all'):
        # network_size = 10000
        # network_type = 'all'
        # infection_rate = 0.1
        # amount_of_contacts = 'all'
        # recconection_rate = 'all'
        params_dirs = []
        if(amount_of_contacts == 'all'):
            if(recconection_rate == 'all'):
                params_dirs = [parent_path + dir for dir in all_dirs if("size: {},".format(network_size) in dir and 
                                                                        "death_rate: {}".format(death_rate) in dir and
                                                                        "infection_rate: {},".format(infection_rate) in dir
                                                                        ) 
                                ]
        else:
            if(recconection_rate == 'all'):
                params_dirs = [parent_path + dir for dir in all_dirs if("size: {},".format(network_size) in dir and 
                                                                            "node_contacts: {},".format(amount_of_contacts) in dir and
                                                                            "death_rate: {}".format(death_rate) in dir and
                                                                            "infection_rate: {},".format(infection_rate) in dir 
                                                                            )
                                ]
            params_dirs.extend([parent_path + dir for dir in all_dirs if("size: {},".format(network_size) in dir and
                                                                        "network: {}".format("ER") in dir and
                                                                        "node_contacts: {},".format(amount_of_contacts * network_size) in dir and
                                                                        "death_rate: {}".format(death_rate) in dir and
                                                                        "infection_rate: {},".format(infection_rate) in dir
                                                                        )
                                ])

        
        return params_dirs

    else:
        path_to_data = parent_path + "size: {}, network: {}, node_contacts: {}, infection_rate: {}, death_rate: {}/".format(
        network_size, network_type, amount_of_contacts, np.format_float_positional(infection_rate), death_rate)
        if(recconection_rate != -1):
            path_to_data = parent_path + "size: {}, network: {}, node_contacts: {}, reconnection_rate: {}, infection_rate: {}, death_rate: {}/".format(
        network_size, network_type, amount_of_contacts, recconection_rate, np.format_float_positional(infection_rate), death_rate)
        # if(quorantine != ""):
        #     path_to_data = path_to_data[:-1] + ", quorantine_measure: {}/".format(quorantine)
        return path_to_data    


#size: 10000, network: WS, node_contacts: 4, reconnection_rate: 0.1, infection_rate: 0.1, death_rate: different?
def get_infection_rates(params_dirs):
    infection_rates = [float((params.split("infection_rate: ",1)[1]).split(',', 1)[0]) for params in params_dirs]
    print(infection_rates)
    
    return infection_rates


def experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, recconection_rate = -1, mode = 'I', marker = "s", value_mode='value'):
    #value_mode= 'value' / 'day'

    folder_names = get_folder_names(parent_path, network_size, network_type, amount_of_contacts, death_rate_type, recconection_rate)
    infection_rates = get_infection_rates(folder_names)
    peack_infected_nodes_list = []

    for data_path in folder_names:
        print(path.exists(data_path))
        print(data_path)
        amount_of_files = get_amount_of_files(data_path)
        print(amount_of_files)
        if(amount_of_files != -1):
            data = get_data(data_path, amount_of_files, 'txt')
            mean = get_mean(data, mean_type)
            #print(mean)
            peack_infected_nodes_list.append(get_max_values(mean, mode)[value_mode])
    
    print(parent_path)

    color = 'black'
    #plot(mean, 'Python', 'BA', mode, marker, color)

    print(infection_rates)
    print(peack_infected_nodes_list)
    infection_rates, peack_infected_nodes_list = zip(*sorted(zip(infection_rates, peack_infected_nodes_list)))

    plt.plot(infection_rates, peack_infected_nodes_list, label = get_label(network_type, amount_of_contacts, recconection_rate), color = color, marker = marker)


def get_label(network_type, amount_of_contacts, recconection_rate):
        if(network_type != "WS"):
            return "{} {}".format(network_type, amount_of_contacts)
        return "{}({}) {}".format(network_type, recconection_rate, amount_of_contacts)


def get_value(fn,parameter):
    if(parameter not in fn):
        return 0
    return (fn.split(parameter,1)[1]).split(',', 1)[0]


def get_params_from_folder_name(folder_name):
    size = int(get_value(folder_name, parameter='size: '))
    network_model = get_value(folder_name, parameter='network: ')
    amount_of_contacts = int(get_value(folder_name, parameter='node_contacts: '))
    reconnection_rate = float(get_value(folder_name, parameter='reconnection_rate: '))
    return {
        "Network model" : network_model,
        "Size" :  size,
        "Initial number of edges for node" :  amount_of_contacts,
        "Reconnection probability" :  reconnection_rate,
    }


def get_network_properties(folder_name):
    parameters = get_params_from_folder_name(folder_name)
    for properties in Network_properties_data.network_properties:
        check = True
        for parameter in parameters.keys():
            if parameters[parameter] != properties[parameter]:
                #print(parameter)
                check = False
                break
                #print('check = false')
        if(check):
            #print(properties)
            return properties


#correlation betwean network topology (mode_1) and peak infected nodes / time of peak (mode_2)
#aspl - average shortest path lenght, cc - clastering coefitient
def experiment_4(network_size, amount_of_contacts, infection_rate, mode_1 = 'aspl'):
    network_type = 'all'
    recconection_rate = 'all'
    death_rate_type = 'different'

    folder_names = get_folder_names(parent_path, network_size, network_type, amount_of_contacts, death_rate_type, recconection_rate, infection_rate)
    #for folder_name in folder_names: print(folder_name)
    #peack_infected_nodes_list = []

    df = pd.DataFrame(columns=list(Network_properties_data.network_properties[0].keys()) + ['peak_infected_nodes', 'peak_critically_infected_nodes', 'time_of_PIN', 'time_of_PCIN'])
    for data_path in folder_names:
        if(not path.exists(data_path)):
            print('path not exist')
            continue
        values = get_network_properties(data_path)
        
        print(data_path)
        amount_of_files = get_amount_of_files(data_path)
        print(amount_of_files)
        pd.DataFrame(columns=['A','B','C','D','E','F','G'])
        if(amount_of_files != -1):
            data = get_data(data_path, amount_of_files, 'txt')
            mean = get_mean(data, mean_type)
            #print(mean)
            values['peak_infected_nodes'] = get_max_values(mean, "I")['value']
            values['peak_critically_infected_nodes'] = get_max_values(mean, "CI")['value']
            values['time_of_PIN'] = get_max_values(mean, "I")['day']
            values['time_of_PCIN'] = get_max_values(mean, "CI")['day']
            print(values)

        df = df.append(values, ignore_index=True)

    
    df = df.sort_values(by=['Average shortest path length'])
    df_corr = df.corr()
    df_corr = df_corr.round(3)
    df_corr.to_csv("output.csv")

    
    # print(parent_path)

    # color = 'black'
    # #plot(mean, 'Python', 'BA', mode, marker, color)

    # print(infection_rates)
    # print(peack_infected_nodes_list)
    # infection_rates, peack_infected_nodes_list = zip(*sorted(zip(infection_rates, peack_infected_nodes_list)))

    plt.plot(df['Average shortest path length'], df['time_of_PIN'], label = "", color = 'black', marker = 's')

#experiment_4(10000, 0.1)

# network_size=10000
# infection_rate = 0.2
# number_of_contacts = 4
# experiment_4(network_size, number_of_contacts, infection_rate)




# experiment_1()
# plt.xlabel("Day", fontsize=16)
# plt.ylabel("Number of infected people", fontsize=16)


# mode = 'I'
# experiment_2(mode)

# plt.xlabel("Day", fontsize=16)
# if(mode == 'CI'):
#     plt.ylabel("Number of critically infected people", fontsize=16)
# else:
#     plt.ylabel("Number of infected people", fontsize=16)


#print(mean)

# value_mode='value'

# network_size = 10000
# death_rate_type = 'different'
# network_type = 'ER'
# amount_of_contacts = 4 * 10000
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, marker = "v", value_mode=value_mode)

# network_type = 'BA'
# amount_of_contacts = 4
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, marker = "o", value_mode=value_mode)

# network_type = 'WS'
# recconection_rate = 0.1
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, recconection_rate, marker = "s", value_mode=value_mode)

# recconection_rate = 0.2
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, recconection_rate, marker = "P", value_mode=value_mode)

# recconection_rate = 0.5
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, recconection_rate, marker = "x", value_mode=value_mode)

# plt.xlabel("Infection rate", fontsize=16)
# plt.ylabel("Day of the peak", fontsize=16)


# experiment_2_1("I")


#exp 3
# network_type = 'BA'
# amount_of_contacts = 1
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, marker = "o")

# amount_of_contacts = 2
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, marker = "o")

# amount_of_contacts = 4
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, marker = "o")

# amount_of_contacts = 10
# experiment_2_peak(network_size, network_type, amount_of_contacts, death_rate_type, marker = "o")


# plt.xlabel("Day", fontsize=16)
# plt.ylabel("Number of infected people", fontsize=16)

# plt.title("Infected people (counting was provided ones per each \"day\")\n (average values)")

def new_exp(parameters):
    markers = ['s', 'o','D', 'P', 'v']
    colors = ['black', 'blue', 'red', 'purple', 'green']
    quorantines = ['no', 'adjacency', 'non-backtracking', 'aspl', 'degree']
    labels = ['No', 'EAM', 'ENBM' ,'ASPL','HD']

    for color, quorantine, marker, label in list(zip(colors, quorantines, markers, labels)):
        if(quorantine == 'no'):
            temp_number_of_nodes_for_immunzation = 0
        else:
            temp_number_of_nodes_for_immunzation = parameters.number_of_nodes_for_immunzation
        exp_2_plot(parameters.network_size, parameters.network_type, parameters.amount_of_contacts, \
                    parameters.infection_rate, parameters.death_rate_type, label, color, marker, \
                    parameters.infection_mode, quorantine = quorantine, recconection_rate=parameters.recconection_rate, \
                    number_of_nodes_for_immunzation = temp_number_of_nodes_for_immunzation)


def get_averaged_network_parameters(parameters, quorantine = 'no', number_of_nodes_for_immunzation = ""):
    data_path = get_path(parent_path, parameters.network_size, parameters.network_type,\
        parameters.amount_of_contacts, parameters.infection_rate, parameters.death_rate_type,\
        parameters.recconection_rate, quorantine, number_of_nodes_for_immunzation)
    file = open(data_path+'initialized_network_properties.json') if(quorantine == 'no') else open(data_path + 'imunized_network_properties.json')
    data = json.load(file)
    df = pd.DataFrame.from_dict(data)
    mean_data = df.mean().round(decimals = 3)
    #print(mean_data)
    if quorantine == 'no':
        return mean_data.values
    elif quorantine == 'aspl':
        return mean_data['ASPL']
    elif quorantine == 'adjacency':
        return mean_data['adjacency eigenvalue']
    elif quorantine == 'non-backtracking':
        return mean_data['non-backtracking eigenvalue']
    elif quorantine == 'degree':
        return mean_data['highest degree']
    elif quorantine == 'diameter':
        return mean_data['diameter']
    else:
        return None


def get_number_of_failed_outbreaks(parameters):
    data_path = get_path(parent_path, parameters.network_size, parameters.network_type,\
        parameters.amount_of_contacts, parameters.infection_rate, parameters.death_rate_type,\
        parameters.recconection_rate, parameters.quorantine, parameters.number_of_nodes_for_immunzation)
    amount_of_files = get_amount_of_files(data_path)
    data = get_data(data_path, amount_of_files, 'txt')
    percent_of_outbreaks = np.sum(data[:, 100, 2] > 0.2 * parameters.network_size)
    return percent_of_outbreaks / len(data)


class Parameters():
    def __init__(self, network_type, network_size, amount_of_contacts, death_rate_type,\
         infection_rate, number_of_nodes_for_immunzation,  recconection_rate = "", \
         infection_mode = 'I', quorantine = ""):
        self.network_type = network_type
        self.network_size = network_size
        self.amount_of_contacts = amount_of_contacts
        if network_type == 'ER':
            self.amount_of_contacts = amount_of_contacts * network_size
        self.death_rate_type = death_rate_type
        self.infection_rate = infection_rate
        self.number_of_nodes_for_immunzation = number_of_nodes_for_immunzation
        self.infection_mode = infection_mode
        self.quorantine = quorantine
        self.recconection_rate = recconection_rate if self.network_type == 'WS' else ''
        

parameters = Parameters(network_type = 'ER', \
                        network_size = 200, \
                        amount_of_contacts=2, \
                        death_rate_type = 'different', \
                        infection_rate = 0.15, \
                        number_of_nodes_for_immunzation = 5, \
                        # quorantine = 'aspl', \
                        recconection_rate = 0.3)

#new_exp(parameters)


quorantines = ['no', 'aspl', 'adjacency', 'non-backtracking' , 'degree']
quorantines = ['aspl', 'adjacency', 'non-backtracking' , 'degree']
list_of_numbers_of_nodes_for_immunzation = ["", 5]


# for number_of_nodes_for_immunzation in list_of_numbers_of_nodes_for_immunzation:
#     lst = []
#     print(number_of_nodes_for_immunzation)
#     for quorantine in quorantines:
#         parameters.quorantine = quorantine
#         parameters.number_of_nodes_for_immunzation = number_of_nodes_for_immunzation if quorantine != 'no' or number_of_nodes_for_immunzation == '' else 0
#         lst.append(get_number_of_failed_outbreaks(parameters))
#     print(*lst, sep=' & ')



data = [get_averaged_network_parameters(parameters, number_of_nodes_for_immunzation=parameters.number_of_nodes_for_immunzation, quorantine = quorantine) for quorantine in quorantines]
for i in range(len(data)):
    if data[i] is not None:
        data[i] = np.round(data[i], 3)
print(*data, sep = " & ")

# get_number_of_failed_outbreaks(parameters)

# print('\n')

new_exp(parameters)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.legend(prop={'size': 16})
plt.xlabel('Time', fontsize=16)
plt.ylabel('Infected nodes', fontsize=16)
#plt.title(parameters.network_type, fontsize= 20)
#plt.figure(num=None,figsize=(400,400),dpi=100,facecolor='w',edgecolor='k')
plt.show()
