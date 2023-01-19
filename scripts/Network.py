import numpy as np
import random
import copy

#population_data {"age_range", "gender", "probability", "cumulative"}

def giant_component(graph):
    vc = graph.components()
    vc_sizes = vc.sizes()
    return vc.subgraph(vc_sizes.index(max(vc_sizes)))

class Network:

    def __init__(self, graph, population_data, directed = False):
        self.graph = copy.deepcopy(graph)
        self.adjacency_matrix = np.array(graph.get_adjacency().data)
        self.edges_list = self.graph.get_edgelist()
        if(not directed):
            self.edges_list = self.edges_list + [(egde[1],egde[0]) for egde in self.edges_list]
        self.nodes = list(set(node for edge in self.edges_list for node in edge))
        self.nodes.sort()
        self.nonbacktracking_matrix = None
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
        self.graph.es['color'] = np.array(['#000000' for i in range(len(self.edges_list))])


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


    def get_network_properties(self):
        # classterization coefficient
        # ASPL
        # max adj matrix eigenvalue
        # max nb matrix eigenvalue
        # the highest degree
        # diameter
        return {
            "ASPL" : float(np.mean(giant_component(self.graph).shortest_paths())),
            "adjacency eigenvalue" : self.get_max_eigenvalue(mode = 'adjacency'),
            "non-backtracking eigenvalue" : self.get_max_eigenvalue(mode = 'non-backtracking'),
            "highest degree" : int(np.max(self.graph.degree())),
            "diameter" : int(giant_component(self.graph).diameter())
        }


        #https://www.nature.com/articles/s41598-020-78582-x#Sec1
    def get_non_backtracking_matrix(self):
        nonbacktracking_matrix = np.zeros((len(self.edges_list), len(self.edges_list)))

        for edge_one in self.edges_list:
            for edge_two in self.edges_list:
                if(edge_one[1] == edge_two[0] and edge_one[0] != edge_two[1]):
                    index_one = self.edges_list.index(edge_one)
                    index_two = self.edges_list.index(edge_two)
                    nonbacktracking_matrix[index_one][index_two] = 1
        self.nonbacktracking_matrix = nonbacktracking_matrix
        return nonbacktracking_matrix


    # canon [{???'method': , 'influence_susceptibility': , 'influence_contagiousness': , 'amount': }, ...]
    def do_random_quarantine(self, quarantine_measure):
        rng = np.random.default_rng(12345)
        people_in_quarantine = rng.integers(low=0, high=self.size, size=int(quarantine_measure['amount']))
        #people_in_quarantine = np.random.randint(low=0, high=self.size, size=int(quarantine_measure['amount']))
        for person in people_in_quarantine:
            self.contagiousness_of_nodes[person][0] = self.contagiousness_of_nodes[person][0] * (1 - quarantine_measure['influence_contagiousness'])
            self.susceptibility_of_nodes[person] = self.susceptibility_of_nodes[person] * (1 - quarantine_measure['influence_susceptibility'])


    def remove_node(self, node):
        #new_edges = list(filter(lambda x: node not in x, self.edges_list))
        edges = []
        new_edges = []
        edges_for_removing = []
        for edge in self.edges_list:
            if node not in edge:
                edges.append(True)
                new_edges.append(edge)
            else:
                edges.append(False)
                edges_for_removing.append(edge)
        if(self.nonbacktracking_matrix is not None):
            self.nonbacktracking_matrix = self.nonbacktracking_matrix[edges, :][:, edges]
        if(self.adjacency_matrix is not None):
            self.adjacency_matrix[node] = 0
            self.adjacency_matrix[:,node] = 0


        #check if an appropriate node removes
        self.graph.delete_edges(edges_for_removing)
        #self.graph.delete_vertices(self.nodes.index(node))
        self.nodes.remove(node)
        self.edges_list = new_edges
        a = 0
        #self.edges_list = [edge for edge in self.edges_list if node not in edge]
        # print(edges)
        # print(self.nonbacktracking_matrix)
        # print(self.edges_list)


    def get_max_eigenvalue(self, mode = 'adjacency'):
        if(mode == 'adjacency'):
            return float(np.max([eig.real for eig in np.linalg.eigvals(self.adjacency_matrix)]))
        elif (mode == 'non-backtracking'):
            if(self.nonbacktracking_matrix is not None):
                a = [np.sum(self.nonbacktracking_matrix[i]) for i in range(len(self.nonbacktracking_matrix))]
                return float(np.max([eig.real for eig in np.linalg.eigvals(self.nonbacktracking_matrix)]))
            else:
                a = 0
                return None
        else: 
            return None


    def get_eigenvalue(self):
        return np.linalg.eig(self.adjacency_matrix)[0]
    

    def get_eigenvector(self):
        return np.linalg.eig(self.adjacency_matrix)[1] #incorrect


    def better_removing(self, mode = 'no', number_of_nodes = 1):
        if(mode == 'no'):
            return self
        if(mode == 'non-backtracking' and self.nonbacktracking_matrix is None):
            self.get_non_backtracking_matrix()
        best_network = copy.deepcopy(self)
        best_network.remove_node(self.nodes[0])
        temp_network = copy.deepcopy(self)
        
        best_max_eigenvalue = best_network.get_max_eigenvalue(mode)
        best_aspl = np.mean(best_network.graph.shortest_paths())
        best_degree = np.max(best_network.graph.degree())
        for _ in range(number_of_nodes):
            for node in temp_network.nodes:
                print(node)
                new_network = copy.deepcopy(temp_network)
                new_network.remove_node(node)
                if(mode == 'non-backtracking'):
                    max_eigenvalue = new_network.get_max_eigenvalue(mode)
                elif(mode == 'adjacency'):
                    max_eigenvalue = new_network.get_max_eigenvalue(mode = 'adjacency')
                elif(mode == 'aspl'):
                    new_aspl =  np.mean(new_network.graph.shortest_paths())
                    if(best_aspl < new_aspl):
                        best_aspl = new_aspl
                        best_network = new_network
                elif(mode == 'degree'):
                    # minimization of the highest degree
                    new_degree =  np.max(best_network.graph.degree())
                    if(new_degree < best_degree):
                        best_degree = new_degree
                        best_network = new_network
                else:
                    return self
                if((mode == 'non-backtracking' or (mode == 'adjacency')) and max_eigenvalue < best_max_eigenvalue):
                    best_network = new_network
                    best_max_eigenvalue = max_eigenvalue
                a = 0
            temp_network = copy.deepcopy(best_network)
            
        return temp_network


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
