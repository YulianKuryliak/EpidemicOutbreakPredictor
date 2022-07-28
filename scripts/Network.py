import numpy as np
from numpy.linalg import eig
import random

#population_data {"age_range", "gender", "probability", "cumulative"}

class Network:

    def __init__(self, graph, population_data):
        self.graph = graph
        self.adjacency_matrix = np.array(graph.get_adjacency().data)
        self.egdes_list = graph.get_edgelist()
        self.size = len(self.adjacency_matrix)
        self.__init_disease_info()
        self.__init_population_info(population_data)


    def __init_disease_info(self):
        self.infected_nodes = [0 for i in range(self.size)]
        self.susceptible_nodes = np.array([[1] for i in range(self.size)])
        self.contagious_nodes = np.array([0 for i in range(self.size)])
        self.times_node_infection = [-1] * self.size
        self.ages = [-1 for i in range(self.size)]
        self.genders = ['U' for i in range(self.size)]
        self.death_probabilities = [0 for i in range(self.size)]
        self.contagiousness_of_nodes = np.array([1 for i in range(self.size)])
        self.susceptibility_of_nodes = np.array([[1] for i in range(self.size)])
        self.infected_by_nodes = np.array([0 for i in range(self.size)])
        self.graph.vs['color'] = np.array(['#FFFFFF' for i in range(self.size)])
        self.graph.es['color'] = np.array(['#000000' for i in range(len(self.egdes_list))])


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
            self.death_probabilities[i] += 0.2
            

    def __searching_data(self, data, probability):
        for i in range(1,len(data)):
            if(probability < data[i]["cumulative"]):
                return data[i]["age_range"], data[i]["gender"], data[i]["p_death"]


    def print(self):
        for i in range(self.size):
            print("node: %5d, age: %7s, gender: %2c, infected: %2d, susceprible: %2d, contagious: %2d, time_node_infection: %6f, prbability of death: %6f" % (
                i, self.ages[i], self.genders[i], self.infected_nodes[i], self.susceptible_nodes[i], self.contagious_nodes[i][0], self.times_node_infection[i], self.death_probabilities[i]))


    def get_eigenvalue(self):
        return eig(self.adjacency_matrix)[0]
    

    def get_eigenvector(self):
        return eig(self.adjacency_matrix)[1] #incorrect

    
    def test(self):
        print('hello')


    def netShield(self, k):
        # https://chenannie45.github.io/netshield-tkde15.pdf
        # k - number_of_nodes, A - matrix (adjecency)
        A = self.adjacency_matrix
        n = len(A)
        S = [] # nodes for imunization
        v = np.zeros(n)
        score = np.zeros(n)
        L = self.get_eigenvalue()[0] # Lambda (eigenvalue)
        u = self.get_eigenvector()[0] # eigenvector

        for i in range(n):
            v[i] = (2 * L - A[i][i]) * (u[i] ** 2)
        
        for _ in range(k):
            B = A[:, S]
            print(u[S])
            b = np.dot(B, u[S])
            for i in range(n):
                if i in S:
                    score[i] = -1
                else:
                    score[i] = v[i] - 2 * b[i] * u[i]
            S.append(np.argmax(score))
        return S

    
    # def get_nonbacktracking_matrix(self, k, v_c=0):
    #     # ?1 How to know length of walk
    #     # ?2 can be way to v_p nodes from v_c in further walk? if no, some nodes can be cut
    #     # !3 Matrix is different for all v0

    #     B = np.zeros((self.size, self.size))
    #     v_p = -1
    #     for _ in range(k):
    #         v = np.nonzero(self.adjacency_matrix[v_c])
    #         v = np.delete(v, np.argwhere(v == v_p))
    #         if(len(v)-1 <= 0):
    #             return B
    #         v_n = v[random.randint(0, len(v)-1)]
    #         B[v_c][v_n] = 1
    #         v_p = v_c
    #         v_c = v_n
    #     return B

    

    def cut_edges(self, S):
        zero_column = np.resize(np.zeros(self.size), (1, self.size))
        for i in S:
            self.adjacency_matrix[i] = np.zeros(self.size)
            self.adjacency_matrix[:, i] = 0
        print(self.adjacency_matrix)



