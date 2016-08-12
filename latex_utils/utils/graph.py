# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import copy
import networkx.algorithms.shortest_paths.weighted as shortest_path
try:
    import shortest_path_weighted as shortest_path_tweaked
except:
    pass

g_array = np.zeros(shape=(8,8))
g_array[0,1] = 3
g_array[0,2] = 5
g_array[0,3] = 2
g_array[1,2] = 4
g_array[1,4] = 7
g_array[1,5] = 5
g_array[2,5] = 4
g_array[2,6] = 9
g_array[3,2] = 2
g_array[3,6] = 8
g_array[4,7] = 2
g_array[5,4] = 2
g_array[5,6] = 1
g_array[5,7] = 6
g_array[6,7] = 5

ALLOWED_SHORTEST_PATH_METHOD = ['dijkstra', 'bellman_ford']

class graph_shortest_path(object):
    def __init__(self, graph):
        if isinstance(graph, np.ndarray):
            graph = np.matrix(graph)
        if isinstance(graph, np.matrix):
            if not graph.shape[0] == graph.shape[1]:
                raise ValueError("The matrix of the graph is not a square matrix")
            for i in range(graph.shape[0]):
                if not graph[i, i] == 0:
                    raise ValueError(
                        "The diagonal of the matrix is not 0 at [%(idx)d, %(idx)d]" % {"idx": i+1})
            graph = nx.from_numpy_matrix(graph, create_using=nx.DiGraph())
        self.graph = graph
        self.n_node = graph.number_of_nodes()
        self.pred_list = []
        self.seen_list = []
        self.dist_list = []
        self.p_node_list = []
        self.final_pred = []
        self.final_dist = []

    def get_iterated_solution(self, source=0, method="dijkstra"):
        n_node = self.n_node
        pred_list = []
        seen_list = []
        p_node_list = []
        dist_list = []

        def dijkstra_callback(**kwargs):
            pred = copy.deepcopy(kwargs["pred"])
            dist = copy.deepcopy(kwargs["dist"])
            seen = copy.deepcopy((kwargs["seen"]))
            nit = kwargs["nit"]
            p_node = []
            for i in range(n_node):
                if i not in pred:
                    pred[i] = [0]
                if i in dist:
                    p_node.append(i)
                if i not in seen:
                    seen[i] = "$\infty$"
            pred_list.append(pred)
            dist_list.append(dist)
            seen_list.append(seen)
            p_node_list.append(p_node)

        def bellman_ford_callback(**kwargs):
            dist = copy.deepcopy(kwargs["dist"])
            nit = kwargs["nit"]
            p_node = []
            for i in range(n_node):
                if i not in pred:
                    pred[i] = [0]
                if i in dist:
                    p_node.append(i)
            dist_list.append(dist)
            p_node_list.append(p_node)

        callback = None
        if method == "dijkstra":
            callback = dijkstra_callback
        elif method == "bellman_ford":
            callback = bellman_ford_callback

        pred, dist = self.get_predecessor_and_distance(source=source, method=method, callback=callback)
        self.pred_list = pred_list
        self.dist_list = dist_list
        self.seen_list = seen_list
        self.p_node_list = p_node_list

        if method == "dijkstra":
            self.final_pred = pred_list[-1]
        elif method == "bellman_ford":
            self.final_pred = pred
            assert not self.pred_list
            assert not self.seen_list
        self.final_dist = dist

    def get_predecessor_and_distance(self, source=0, method="dijkstra", callback=None):
        if method == "dijkstra":
            return shortest_path_tweaked.dijkstra_predecessor_and_distance(
                self.graph, source=source, callback=callback)
        if method == "bellman_ford":
            dist = {source: 0}
            pred = {source: None}
            if len(self.graph) == 1:
                return pred, dist
            return shortest_path_tweaked.bellman_ford_predecessor_and_distance(
                self.graph, source=0, callback=callback)

    def get_shortest_path(self, target=None):
        # this returns an generator
        if not target:
            target = len(self.graph) - 1
        return shortest_path_tweaked.all_shortest_paths_from_0(self.graph, target=target)

    def get_shortes_distance(self, source=0, target=None, method='dijkstra'):
        if method not in ALLOWED_SHORTEST_PATH_METHOD:
            raise ValueError("Unknown shortest path method: %s" % method)
        if target is None:
            target = self.n_node - 1
        if method == "dijkstra":
            return shortest_path.dijkstra_path_length(self.graph, source=source, target=target)

g_mat = np.matrix(g_array)
g = nx.from_numpy_matrix(g_mat, create_using=nx.DiGraph())
n_node = g.number_of_nodes()
path = nx.dijkstra_path(g,0,7)
length = nx.dijkstra_path_length(g,0,7)
#print path, length

graph = graph_shortest_path(g)
graph.get_iterated_solution(method="dijkstra")
# print graph.p_node_list
# print graph.dist_list
# print graph.pred_list
# print graph.seen_list

# g_mat = np.matrix([
#     [0,2,5,4,0,0,0,0],
#     [0,0,-4,2,0,9,0,0],
#     [0,0,0,3,-2,0,3,0],
#     [0,0,0,0,2,0,8,0],
#     [0,0,0,0,0,0,0,3],
#     [0,-8,0,2,3,0,0,4],
#     [0,0,-2,0,4,0,0,6],
#     [0,0,0,0,0,0,0,0]
# ])

g = nx.from_numpy_matrix(
    g_mat,
    create_using=nx.DiGraph()
)


#print len(g)


#pred, dist = shortest_path_tweaked.bellman_ford_predecessor_and_distance(g, source=0, weight="weight")
#print pred, dist


all_sp = graph.get_shortest_path()

# for sp in all_sp:
#     print sp

