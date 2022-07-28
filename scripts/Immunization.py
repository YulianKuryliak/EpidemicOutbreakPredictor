from scripts import Network_model
from scripts import Network
import numpy as np
from scripts import Population
import igraph as ig
from numpy.linalg import eig
import math
import copy


def get_non_backtracking_matrix(matrix):
    edges = get_edges_from_adjacency_matrix(matrix)
    B = np.zeros((len(edges), len(edges)))
    for i in range(len(edges)):
        for j in range(len(edges)):
            #print(edges[i], " ", edges[j])
            if edges[i][0] == edges[j][1] and edges[i][1] != edges[j][0]:
                B[i][j] = 1
                #print("true")
    return B

def get_edges_from_adjacency_matrix(matrix):
    return [(i,j) for i,l in enumerate(matrix) for j,v in enumerate(l) if v]


def ideal_nodes_removing(adjacency_matrix, n, mode):
    if mode == 'non-backtracking':
        eigen_value = get_biggest_real_eig(get_non_backtracking_matrix(adjacency_matrix))[0]
    else:
        eigen_value = get_biggest_real_eig(adjacency_matrix)[0]
    temp_adjacency = copy.deepcopy(adjacency_matrix)
    removed_nodes = []
    #print("eigenvalue: ", eigen_value)

    for _ in range(n):
        node_to_remove = -1
        for i in range(len(temp_adjacency)):
            matrix = np.delete(np.delete(temp_adjacency, i, 0), i, 1) #removing a node
            if mode == 'non-backtracking':
                matrix = get_non_backtracking_matrix(matrix) # get_non_backtracking_matrix has to take an adjacency matrix
            temp_eigenvalue = get_biggest_real_eig(matrix)[0]
            #print(temp_eigenvalue)
            if(eigen_value > temp_eigenvalue):
                node_to_remove = i
                eigen_value = temp_eigenvalue
                #print("new eigenvalue")
        if(node_to_remove >=0):
            temp_adjacency = np.delete(np.delete(temp_adjacency, node_to_remove, 0), node_to_remove, 1)
            removed_nodes.append(node_to_remove)
        #print("step")
    return temp_adjacency, removed_nodes



def netShield(A, k=1):
    # https://chenannie45.github.io/netshield-tkde15.pdf
    # k - number_of_elements, A - matrix (adjacency/non-backtracking)
    n = len(A)
    S = [] # nodes for imunization
    v = np.zeros(n)
    score = np.zeros(n)
    L, u = get_biggest_real_eig(A) # Lambda (eigenvalue) # eigenvector

    for i in range(n):
        v[i] = (2 * L - A[i][i]) * (u[i] ** 2)
    
    for _ in range(k):
        print(S)
        B = A[:, S]
        b = np.dot(B, u[S])
        for i in range(n):
            if i in S:
                score[i] = -1
            else:
                score[i] = v[i] - 2 * b[i] * u[i]
        S.append(np.argmax(score))
    print(S)
    return S


def get_max(values, indexes):
    max_index = 0
    max_value = values[indexes[0]]
    for i in range(len(indexes)):
        if max_value < values[indexes[i]]:
            max_value = values[indexes[i]]
            max_index = indexes[i]
    return max_index


def get_biggest_real_eig(B):
    e = eig(B)[0]
    r_e = []
    for i in range(len(e)):
        if math.isclose(i.imag, 0, rel_tol=1e-6):
            r_e.append(i)

    max_eig_index = get_max(e, r_e)
    #print("index: ", max_eig_index)
    eigen_value = e[max_eig_index].real
    return eigen_value, [v.real for v in eig(B)[1][:, max_eig_index]]


if __name__ == "__main__":
    size = 50  
    edges = 2
    network_type = 'BA'
    reconnection_rate = 0
    death_rate_type = 'same'
    k=2
    network = Network_model.create_network(size, edges, network_type, reconnection_rate)

    graph = Network.Network(np.array(list(network.get_adjacency())),
                            Population.get_population(death_rate_type))
    #print(graph.netShield(k))

    # k=3
    # graph.cut_edges(graph.netShield(k))

    #print(graph.get_eigenvalue())
    edges = []
    for edge in network.es:
        edges.append(edge.tuple)
        edges.append(tuple(reversed(edge.tuple)))
    print(edges)

    # print(edges)
    B = get_non_backtracking_matrix(graph.adjacency_matrix)
    print(B)

    rnb = ideal_nodes_removing(graph=graph, n=2, mode='non-backtracking')
    ra = ideal_nodes_removing(graph=graph, n=2, mode='adjacency')
    print(rnb, "\neigenvalue: ", get_biggest_real_eig(rnb[0])[0])
    print(ra, "\neigenvalue: ", get_biggest_real_eig(ra[0])[0])
    # print(eig(B))





    # print(netShield(B, 2))

    #print(eig(B)[0][0].imag)



    # ! to do network creation from adjacency matrix

