from numpy import genfromtxt
import numpy as np
import matplotlib.pyplot as plt
from os import path

import numpy


def get_data(directory, amount_of_files, extension):
    data = []
    for i in range(0,amount_of_files):
        data.append(genfromtxt(directory+ str(i) + '.' + extension, delimiter=',')[1:100])
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


def plot(data, language, label):
    if(language == 'python' or language == 'Python'):
        index_1 = 0
        index_2 = 1
    if(language == 'r' or language == 'R'):
        index_1 = 1
        index_2 = 2
    plt.plot(data.T[index_1], data.T[index_2], label = label)


def get_path(parent_path, graph_size, network_type, amount_of_contacts, infection_rate, quarantine = ""):
    #Python only
    path_to_data = parent_path + "size: {}, network: {}, node_contacts: {}, infection_rate: {}/".format(
    graph_size, network_type, amount_of_contacts, infection_rate)
    if(quarantine != ""):
        path_to_data = path_to_data[:-1] + ", quarantine_measure: {}/".format(quarantine)
    return path_to_data

mean_type = 'average'

np.set_printoptions(formatter={'float_kind':'{:f}'.format})

#python data
amount_of_files = 100
graph_size = 1000
network_type = 'Barabasi'
amount_of_contacts = 10
infection_rate = 0.02
quarantine = "no_10"
# parent_path = "/run/media/fedora_user/31614d99-e16f-45e1-8be5-e21723cf8199/projects/ManagingEpidemicOutbreak/Python-v.0.1/simulations/(new)"
# data_path = get_path(parent_path, graph_size, network_type, amount_of_contacts, infection_rate, quarantine)
# print(path.exists(data_path))
# data = get_data(data_path, amount_of_files, 'txt')
# mean = get_mean(data, mean_type)
# plot(mean, 'Python', 'Node inficates another')

quarantine = "no_10"
parent_path = "/home/data/projects/ManagingEpidemicOutbreak/Python-v.0.1/simulations/"
data_path = get_path(parent_path, graph_size, network_type, amount_of_contacts, infection_rate, quarantine)
print(path.exists(data_path))
data = get_data(data_path, amount_of_files, 'txt')
mean = get_mean(data, mean_type)


data_R = []
avg_R = []
infection_rate_range = [0.02, 0.019, 0.018, 0.017, 0.016, 0.015, 0.012, 0.01, 0.009,0.008,0.007,0.006, 0.005, 0.004]
for infection_rate in infection_rate_range:
    print("\nhello\n")
    data_path = get_path(parent_path, graph_size, network_type, amount_of_contacts, infection_rate, quarantine)
    data = get_R(data_path)[0]
    print(data)
    data_R.append(data)
    avg_R.append(np.average(data))

#avg_R = np.average(data_R)

#print(data_R)
base_index = 0
print("infection rates: ", np.array(infection_rate_range)/infection_rate_range[base_index])
print("average R: ", avg_R/avg_R[base_index])

#plot(mean, 'Python', 'Node inficated')


# data_R = get_data(parent_path + 'size 200, start_infected 1, infection_rates 0.002, time_step 1, time_max 100, network_type compleet_same, amount_of_edges 0, virus_types 1 death_rate_type same, prob_reconnection 0/data_', 36, 'csv')
# mean_R = get_mean(data_R, mean_type)
# plot(mean_R, 'R', 'R(newer)')

# data_R1 = get_data(parent_path + 'size 200, start_infected 1, infection_rates 0.002, time_step 1, time_max 100, network_type compleet, virus_types 1 death_rate_type same/data_', 32, 'csv')
# mean_R1 = get_mean(data_R1, mean_type)
# plot(mean_R1, 'R', 'R (older)')

# data_R2 = get_data(parent_path + 'size 200, start_infected 1, infection_rates 0.002, time_step 1, time_max 100, network_type compleet, amount_of_edges 0, virus_types 1 death_rate_type same, prob_reconnection 0/data_', 24, 'csv')
# mean_R2 = get_mean(data_R2, mean_type)
# plot(mean_R2, 'R', 'R(the newest)')

# plt.xlabel("day")
# plt.ylabel("amount of people")

# plt.title("Infected people (counting was provided ones per each \"day\")\n (average values)")

# plt.legend()
# plt.show()
