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

# inputed_parameters = {
#     "epidemiological_model" : "",
#     "network_model" : "",
#     "Size" : "",
#     "Infection_rate" : "",
#     "Maximum_simulation_time" : "",
#     "Time_of_data_collection" : "",
#     "start_infected" : "",
#     'number_of_edges' : "",
#     'reconection_coefitient' : "",
#     'Treatment_Period' : "",
#     'Critically_Treatment_Period' : "",
#     'number_of_simulations' : "",
# }

#def start_simulation(amount, size, start_infected, infection_rate, time_step, time_max, 
# network_type, folder, virus_types, death_rate_type, amount_of_edges, 
# prob_reconnection, number_of_threads = 2):

PATH = str(pathlib.Path(__file__).parent.absolute()).replace('scripts', '')


def simulation(inputed_parameters):
	print("PATH", PATH)
	parameters = prepare_parameters(inputed_parameters)
	#print(parameters)
	#print("---------------------\n----------\n------------")
	#print("content : ", os.listdir())
	# start_simulation(
	# 	amount = parameters['number_of_simulations'],
	# 	size = parameters['Size'], 
	# 	start_infected = parameters['start_infected'],
	# 	infection_rate = parameters['Infection_rate'],
	# 	time_step = parameters['Time_of_data_collection'],
	# 	time_max = parameters['Maximum_simulation_time'], 
	# 	virus_types = "1",
	# 	network_type = parameters['network_model'],
	# 	folder = get_folder_name(parameters),
	# 	death_rate_type = parameters['Criticaly_infection_rate'],
	# 	amount_of_edges = parameters['number_of_edges'],
	# 	prob_reconnection = parameters['reconection_coefitient'],
	# 	number_of_threads = 2
	# )
	i = 0.
	print(parameters)
	return Simulation.simulation(
		graph_size = int(parameters['Size']),
		network_type = parameters['network_model'], 
		amount_of_contacts = int(parameters['number_of_edges']), 
		infection_rate = round(float(parameters['Infection_rate']), 6),
		number_of_infications = int(parameters['start_infected']), 
		max_time = int(parameters['Maximum_simulation_time']), 
		time_step = round(float(parameters['Time_of_data_collection']),2), 
		i = int(i), 
		folder = PATH + "/assets/simulations/"
	)



def prepare_parameters(inputed_parameters):
	if inputed_parameters['network_model'] == "Barabasi-Albert":
		inputed_parameters['network_model'] = 'BA'
	return inputed_parameters


# def get_folder_name(parameters):
# 	#folder_name = "test"
# 	folder_name = "output_data/simulations/size {}, start_infected {}, infection_rate {}, time_step {}, time_max {}, network_type {}, amount_of_edges {}, virus_types {} death_rate_type {}, prob_reconnection {}".format(
# 							parameters['Size'], parameters['start_infected'], 
# 							parameters['Infection_rate'], parameters['Time_of_data_collection'],
# 							parameters['Maximum_simulation_time'], parameters['network_model'],
# 							parameters['number_of_edges'],
# 							'1', #virus_types
# 							parameters['Criticaly_infection_rate'],
# 							parameters['reconection_coefitient']
# 		)
# 	return folder_name

# class myThread (threading.Thread):
# 	def __init__(self, i, cmd):
# 		threading.Thread.__init__(self)
# 		self.threadID = i
# 		self.threadCMD = cmd


# 	def run(self):
# 		print("i = ", self.threadID)
# 		run_simulation(self.threadCMD)		


# def run_simulation(cmd):
# 	print("--------------\n\ncmd : ", cmd, "\n\n---------------------")
# 	subprocess.call(cmd, universal_newlines = True)


# def start_simulation(amount, size, start_infected, infection_rate, time_step, time_max, network_type, folder, virus_types, death_rate_type, amount_of_edges, prob_reconnection, number_of_threads = 2):
# 	print(folder)
# 	command = path_to_R
# 	path2script = "scripts\\Simulation.R"
# 	for i in range(0,amount, number_of_threads):
# 		threads = list()
# 		for j in range(0, number_of_threads):
# 			if (i + j >= amount):
# 				break
# 			args = [str(size), str(start_infected), str(time_max), str(infection_rate), str(time_step), str(i + j), folder, str(network_type), virus_types, death_rate_type, str(amount_of_edges), str(prob_reconnection)]
# 			cmd = [command, path2script] + args
# 			thread = myThread(i + j, cmd)
# 			threads.append(thread)
# 			thread.start()

# 		for thread in threads:
# 			thread.join()