import numpy as np

#population_data {"age_range", "gender", "probability", "cumulative"}

class Network:

    def __init__(self, adjacency_matrix, population_data):
        self.adjacency_matrix = adjacency_matrix
        self.size = len(adjacency_matrix)
        self.__init_disease_info()
        self.__init_population_info(population_data)


    def __init_disease_info(self):
        self.infected_nodes = [0 for i in range(self.size)]
        self.susceptible_nodes = np.array([1 for i in range(self.size)])
        self.contagious_nodes = np.array([[0] for i in range(self.size)])
        self.times_node_infication = [-1] * self.size
        self.ages = [-1 for i in range(self.size)]
        self.genders = ['U' for i in range(self.size)]
        self.death_probabilities = [0 for i in range(self.size)]
        self.contagiousness_of_nodes = np.array([1 for i in range(self.size)])
        self.susceptibility_of_nodes = np.array([[1] for i in range(self.size)])
        self.infected_by_nodes = np.array([0 for i in range(self.size)])


# canon [{???'method': , 'influence_susceptibility': , 'influence_contagiousness': , 'amount': }, ...]
    def do_random_quarantine(self, quarantine_measure):
        rng = np.random.default_rng(12345)
        people_in_quarantine = rng.integers(low=0, high=self.size, size=int(quarantine_measure['amount']))
        #people_in_quarantine = np.random.randint(low=0, high=self.size, size=int(quarantine_measure['amount']))
        for person in people_in_quarantine:
            self.contagiousness_of_nodes[person][0] = self.contagiousness_of_nodes[person][0] * (1 - quarantine_measure['influence_contagiousness'])
            self.susceptibility_of_nodes[person] = self.susceptibility_of_nodes[person] * (1 - quarantine_measure['influence_susceptibility'])


    def __init_population_info(self, data):
        for i in range(self.size):
            self.ages[i], self.genders[i], self.death_probabilities[i] = self.__searching_data(data, np.random.uniform(0.0, 1.0))
            

    def __searching_data(self, data, probability):
        for i in range(1,len(data)):
            if(probability < data[i]["cumulative"]):
                return data[i]["age_range"], data[i]["gender"], data[i]["p_death"]


    def print(self):
        for i in range(self.size):
            print("node: %5d, age: %7s, gender: %2c, infected: %2d, susceprible: %2d, contagious: %2d, time_node_infication: %6f, prbability of death: %6f" % (
                i, self.ages[i], self.genders[i], self.infected_nodes[i], self.susceptible_nodes[i], self.contagious_nodes[i][0], self.times_node_infication[i], self.death_probabilities[i]))