from math import degrees
import numpy as np
import igraph

class Network:

    def __init__(self, graph, population_data):
        self.graph = graph
        self.adjacency_matrix = np.array(graph.get_adjacency().data)
        self.egdes_list = graph.get_edgelist()
        self.size = len(self.adjacency_matrix)
        self.__init_disease_info()
        print(self.adjacency_matrix)
        print("degrees: ", self.degrees)
        #self.__init_population_info(population_data)


    def __init_disease_info(self):
        self.infection_state = np.zeros(self.size)
        self.susceptible_state = np.ones(self.size)
        self.infected_by_node = np.zeros(self.size)
        self.susceptible_neighbors = np.array(self.graph.indegree())
        self.time_infection = np.full(shape=self.size, fill_value=-np.inf)
        self.degrees = np.array(self.graph.degree()) 


    def __init_population_info(self, data):
        for i in range(self.size):
            self.ages[i], self.genders[i], self.death_probabilities[i] = self.__searching_data(data, np.random.uniform(0.0, 1.0))
            self.death_probabilities[i] += 0.2
            

    def __searching_data(self, data, probability):
        for i in range(1,len(data)):
            if(probability < data[i]["cumulative"]):
                return data[i]["age_range"], data[i]["gender"], data[i]["p_death"]





