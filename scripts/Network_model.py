import igraph
import numpy as np

def complete_graph(size):
    return igraph.Graph.Full(size, directed=False, loops=False)

def ER_model(size, edges):
    return igraph.Graph.Erdos_Renyi(n = size, m = edges, loops = False, directed = False)

def WS_model(size, edges_per_node, reconnection_probability):
    return igraph.Graph.Watts_Strogatz(1, size, edges_per_node, reconnection_probability, loops = False, multiple = False)

def BA_model(size, edges_per_node):
    return igraph.Graph.Barabasi(size, edges_per_node, outpref = False, directed = False)

def get_nodes_for_imunization(graph, amount, type='betweenness_imunization'):
    if type == 'betweenness_imunization':
        data = graph.betweenness(directed=False)
    elif type == 'closeness_imunization':
        data = [round(num, 4) for num in graph.closeness()]
    elif type == 'degree_imunization':
        data = graph.degree()
    else :
        return []
    params = np.array([np.array(value) for value in zip(list(range(0, graph.vcount())), data)])
    sorted = params[params[:,1].argsort()[::-1]]
    best = sorted[:amount]
    #print("best: ", list(best[:,0].astype(int)))
    return list(best[:,0].astype(int))

def imunize(graph, type, amount):
    indexes = get_nodes_for_imunization(graph, amount, type)
    #print(indexes)
    graph.delete_vertices(indexes)
    return graph


def create_network(size, edges, model='complete', reconnection_probability=0):
    if(model == 'Barabasi-Albert' or model == 'BA' or model == 'Barabasi' or model == 'barabasi'):
        graph = BA_model(size, edges)
    elif(model == 'Watts-Strogatz' or model == 'WS' or model == 'small world'):
        graph = WS_model(size, edges, reconnection_probability)
    elif(model == 'Erdos_Renyi' or model == 'ER' or model == 'random'):
        graph = ER_model(size, edges)
    else:
        graph = complete_graph(size)
    
    return graph

# graph = create_network(20, 2, 'BA')
# igraph.plot(graph, layout = graph.layout("circle"))
# print(graph.get_adjacency())
