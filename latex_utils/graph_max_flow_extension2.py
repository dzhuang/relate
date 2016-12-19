# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra, dumps_tikz_doc
from copy import deepcopy
from networkx.algorithms.flow.preflowpush import preflow_push
from networkx.algorithms.flow import edmonds_karp
import numpy as np
import random
import pickle

try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
    from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()

g_list = []

MULTI_RESULT_QUESTION = "graph_max_flow_ext.bin"

SAVED_QUESTION = "graph_max_flow_ext2.bin"


def is_qualified_question(mat, ref_g_list, mem_mat_list, saved_question=SAVED_QUESTION):

    qualified = False

    new_g_dict = deepcopy(ref_g_list)
    new_g_dict["graph"] = mat

    g = network(**new_g_dict)

    G = g.as_capacity_graph()
    number_of_nodes = len(G.node)
    import networkx as nx

    max_flow_value, partition = nx.minimum_cut(G, 0, number_of_nodes-1)

    if max_flow_value > 1000:
        return False

    if len(partition[0]) >= 8:
        return False

    # if len(partition[0]) < 5:
    #     return False
    #
    if len(partition[1])< 4:
        return False

    R = edmonds_karp(G, 0, number_of_nodes-1, value_only=True)

    cutset = [(u, v, d) for u, v, d in R.edges(data=True)
              if d['flow'] == d['capacity'] and u in partition[0]]

    _, flow_dict = nx.maximum_flow(G, 0, number_of_nodes - 1)

    the_cut_edge_set = [(u, v, d) for u, v, d in G.edges(data=True)
              if u in partition[0] and v in partition[1]]

    for u, v, d in the_cut_edge_set:
        G_copy=deepcopy(G)
        G_copy[u][v]["capacity"] += 1
        new_max_flow_value, new_partition = nx.minimum_cut(G_copy, 0, number_of_nodes - 1)
        if new_max_flow_value == max_flow_value:
            return False

    source_flow = sum([flow_dict[u][v] for u in [1,2,3] for v in flow_dict[u]])
    source_capacity = sum([G[u][v]["capacity"] for u in [1,2,3] for v in G[u]])
    sink_capacity = sum([G[u][v]["capacity"] for v in [10] for u in range(number_of_nodes-1) if G.has_edge(u,v)])


    if max_flow_value==source_capacity or source_flow==sink_capacity:
        return False


#    print(source_flow, source_capacity, sink_capacity)

    # 0点出发所连的点，至少有一条边是未饱和的，设其对应的顶点为x
    not_saturated_source_to = []
    for u in [1,2,3]:
        for v in flow_dict[u]:
            if flow_dict[u][v] < G[u][v]["capacity"]:
                not_saturated_source_to.append(v)
    # print(flow_dict[1], flow_dict[2], flow_dict[3])
    # not_saturated_source_to = [v in flow_dict[u] for u in [1,2,3] if flow_dict[u][v] < G[u][v]["capacity"]]
    print(not_saturated_source_to)
    saturated_source_to = []
    for u in [1,2,3]:
        for v in flow_dict[u]:
            if flow_dict[u][v] == G[u][v]["capacity"]:
                saturated_source_to.append(v)
    #
    # saturated_source_to = [v in flow_dict[u] for u in [1,2,3] if flow_dict[u][v] == G[u][v]["capacity"]]

    if not not_saturated_source_to:
       return False

    this_qualified=False
    for u in saturated_source_to:
        if u in partition[0]:
            this_qualified=True
            break
    if not this_qualified:
        return False

    print(not_saturated_source_to)
    print(saturated_source_to)

    question_exist = False
    for i, c in enumerate(mem_mat_list):
        if np.all(mat==c):
            print("----------------------question exists-------------------")
            question_exist = True
            return False
            break

    if not question_exist:
        suggestion = "g = { 'graph': %s" % repr(mat)
        suggestion = suggestion.replace("matrix", "np.matrix")
        r.clipboard_append(suggestion)
        r.clipboard_append(",\n")
        if hasattr(new_g_dict, "node_label_dict"):
            r.clipboard_append('    "node_label_dict":' + repr(new_g_dict["node_label_dict"]) + ',\n')
        else:
            r.clipboard_append('    "node_label_dict": None,\n')
        if new_g_dict["edge_label_style_dict"]:
            r.clipboard_append('    "edge_label_style_dict":' + repr(new_g_dict["edge_label_style_dict"]) + ',\n')
        else:
            r.clipboard_append('    "edge_label_style_dict": None,\n')
        r.clipboard_append("}\n")
        r.clipboard_append("g_list.append(g)")
        r.clipboard_append("\n")
        r.clipboard_append("\n")

        #raise ValueError("Please add above problem")


    return True

def generate_problem():
    n = 0
    mem_mat_list = []

    with open(MULTI_RESULT_QUESTION, 'rb') as f:
        g_list_loaded = pickle.load(f)

    #print(len(g_list_loaded))

    for i, g_dict in enumerate(g_list_loaded):
        print(i)
        if i > 15:
            break

        g = deepcopy(g_dict["graph"])
        non_zero_idx = np.nonzero(g)
        #print(non_zero_idx)
        non_zero_idx_list = []
        for i in range(len(non_zero_idx[0])):
            non_zero_idx_list.append((non_zero_idx[0][i], non_zero_idx[1][i]))
        #print(non_zero_idx_list)
        all_value = g[non_zero_idx]

        n_value = len(all_value.tolist()[0])
        number_of_nodes = len(g)
        n_reverse_arrow = random.choice([1,2,3])
        n_reverse_arrow = 0

        #print(non_zero_idx_list)

        # j = 0
        # while j < n_reverse_arrow:
        #     (r,c) = random.choice(non_zero_idx_list)
        #     if r != 0 and c != number_of_nodes-1:
        #  #       print(r,c)
        #         g[c,r] = g[r,c]
        #         g[r,c] = 0
        #         j += 1

        #print(all_value, "------------------")
        all_value = np.random.randint(
            6, 38, n_value) * 5
        all_value = all_value.tolist()

        n = 0
        while n < 10000:
            n += 1
            g_test = deepcopy(g)
            random.shuffle(all_value)
            new_value = np.array([all_value])
            # print(new_value)
            g_test[non_zero_idx] = new_value
            g_test[0, :] *= 1000
#            g_test[:, -1] *= 1000
            # if i == 1:
                # print(g_test)
            if is_qualified_question(g_test, g_dict, mem_mat_list):
                mem_mat_list.append(g)
                print(repr(g_test))
                break


# generate_problem()
# print("here")
# exit()

g = { 'graph': np.matrix([[     0, 120000,  75000,  30000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,     35,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,     95,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     55,    150,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
             85,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    175,
            105,     75,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            160,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    115],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    140],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[    0, 30000, 70000, 60000,     0,     0,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,   165,    70,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,   125,   150,    30,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,    85,    80,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,   105,    85,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,    40,    55,
            30,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,   160,
           140,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   185],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,    35],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   165],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,     0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  85000,  35000, 135000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,     45,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     65,     40,    160,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     40,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     90,
            120,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    125,
            115,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             60,    185,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    125],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 185000, 165000, 180000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,    115,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    180,    105,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     95,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
            175,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
             45,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             35,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 165000, 100000,  90000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    145,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,    115,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    110,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
             95,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
             85,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     65],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[    0, 80000, 50000, 80000,     0,     0,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,    50,   165,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,    45,   155,    50,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,    80,    70,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,    70,   150,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,    80,    30,
           100,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,   100,
            50,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   155],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   160],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   180],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,     0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 175000,  95000, 125000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,     90,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,     35,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
             75,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
             75,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             70,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 155000, 160000,  60000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    115,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,    180,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    140,     55,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
             95,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     50,
             40,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            120,    165,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     60],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 140000,  85000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,     95,    165,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    105,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             95,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
             35,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             35,    120,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     85],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  30000, 180000, 170000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,     75,    105,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    180,    110,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    185,
            125,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
             30,    165,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  80000, 125000, 145000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    145,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,    100,     85,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     70,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    180,
             75,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             80,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            155,    125,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    100],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  80000, 100000, 155000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    175,    175,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,    155,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    140,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             80,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             40,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             95,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     45],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[    0, 40000, 50000, 95000,     0,     0,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,   110,    90,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,    30,   105,    35,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,   130,    75,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,    30,   135,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,   115,    45,
            70,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,   105,
           180,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   140],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   180],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   180],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,     0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 185000,  35000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,    145,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,     55,    120,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     75,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
             40,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             55,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             30,     75,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 100000, 165000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    100,     50,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     90,    150,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     35,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     95,
            180,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             85,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             55,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    135],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)



g = { 'graph': np.matrix([[     0,  50000,  75000, 105000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     65,    140,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    155,     45,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    140,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    150,
             65,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
             55,     70,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            110,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     50],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 165000, 170000, 165000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,    105,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,     70,    145,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     35,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     50,
            125,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    140,
            160,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            160,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 125000,  45000,  80000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     90,     95,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     55,    100,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             95,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             70,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             45,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  90000, 170000, 150000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,    120,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    175,     85,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     45,
             95,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             55,    175,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 155000,  55000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    100,     45,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,     30,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     60,     55,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             30,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
            170,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,    180,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    100],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  85000, 115000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,     50,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,     30,    160,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     95,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
             90,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    145,
            180,    120,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             75,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     40],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  90000, 115000, 135000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    185,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     40,    150,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     90,    100,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
             75,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             85,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             55,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    100],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  85000, 130000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,    125,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,    185,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    120,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
            155,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     40,
             60,     95,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            185,    140,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     75],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 170000,  95000, 170000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,     80,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,     85,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    100,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
             35,     90,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             60,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    110],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 120000, 160000,  50000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,    165,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,    110,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    175,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
             40,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,    135,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    135],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  85000,  70000, 135000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,    135,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,     85,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     90,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
            115,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
            130,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            120,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    125],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 105000, 120000, 145000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    105,    100,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    105,    170,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             30,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
            100,     75,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 145000, 120000,  85000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,     85,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,     75,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    120,    160,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
             45,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             85,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             85,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    135],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 180000, 135000, 100000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    105,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    135,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    105,     85,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             30,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     45,
             60,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     80],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    135],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)



g = { 'graph': np.matrix([[     0, 150000,  35000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,     35,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,     30,    155,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     50,     85,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
             90,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
             50,    185,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             75,     75,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    105],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     40],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000, 135000, 100000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,    110,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    175,    175,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    105,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     45,
             95,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     65,
            185,     90,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            185,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    140],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 125000, 140000, 120000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    155,     65,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     95,    115,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    140,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
             30,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
            135,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            135,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     80],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 145000, 180000, 130000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,     35,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     55,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     40,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     50,
             60,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
            155,     95,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 160000,  60000, 170000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,    155,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,    125,    135,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     90,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
            120,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     65,
             80,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,    135,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     95],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 110000,  55000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,     75,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,    130,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     85,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
             40,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     95,
             90,     70,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            185,    180,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     90],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 115000,  90000, 185000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     55,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     60,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     75,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
             70,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            145,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    115],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    105],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 125000, 145000,  45000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,     70,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     40,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    115,     85,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
             45,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    185,
             35,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             55,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     65],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    140],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  80000, 110000, 115000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,    165,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,     35,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    145,     55,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
             35,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    150,
             65,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            180,    125,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    100],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 115000, 120000,  95000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     30,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,     30,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     75,     80,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
            180,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    140,
            110,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             85,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 180000, 160000,  85000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,    155,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    170,    165,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     30,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     95,
            180,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
             40,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             60,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 165000, 110000,  95000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,     65,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,     40,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    120,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             45,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
             90,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            175,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    140],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 145000,  90000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    120,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,     90,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    115,    150,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
            155,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
            145,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             70,     95,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    110],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  40000, 185000,  75000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,    115,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,    135,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    175,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
             35,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
             40,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            175,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     95],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 180000, 130000, 165000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     95,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     95,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     60,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     90,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             55,     95,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             85,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    100],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)



g = { 'graph': np.matrix([[     0,  60000, 185000,  55000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,    125,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    115,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    125,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     50,
            145,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
             40,    160,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             90,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     70],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 105000, 130000,  85000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     90,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,     85,    160,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    105,    135,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
            150,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             35,    160,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             95,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    135],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 145000, 110000,  65000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,    105,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,     95,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,    100,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             40,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
             35,    135,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            185,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  80000,  95000, 120000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    160,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    115,    135,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     40,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
             45,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    125,
             90,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             60,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  75000, 100000,  90000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    185,     80,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    135,     95,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     55,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    175,
             40,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            185,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  95000, 115000, 100000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,     50,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,     55,     55,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    130,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             50,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    105,
             55,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            125,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     90],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     85],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 115000, 125000,  70000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     65,     70,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,     75,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     30,    145,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
             95,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
             60,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             35,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    110],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 130000,  50000, 180000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,     65,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     80,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     75,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    125,
            150,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            110,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 165000,  70000, 115000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    150,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    115,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
             45,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     40,
            160,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            125,     75,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    140],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000, 180000, 165000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,     95,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    125,    135,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    160,    120,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             70,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
            110,    135,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    105],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 170000, 165000, 145000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     45,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    175,     45,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     35,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     50,
             40,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
             40,     70,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            145,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 110000,  50000, 145000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,     60,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    170,     45,    100,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     35,     80,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
             90,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     90,
            155,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             50,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  80000, 110000,  70000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,    165,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,     35,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     60,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    180,
             40,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,    140,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 105000, 175000, 100000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,     70,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,     65,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     35,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    150,
            175,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
             65,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             90,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)




g = { 'graph': np.matrix([[     0,  65000,  55000, 105000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    105,     40,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,    110,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     60,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
            160,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             70,    175,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 120000, 175000,  60000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    155,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    170,    150,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    135,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
             75,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
             45,     70,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            150,     95,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     80],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    150],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[    0, 35000, 50000, 65000,     0,     0,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,    55,    40,     0,     0,     0,
             0,     0],
        [    0,     0,     0,     0,   175,    85,   105,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,   145,    65,     0,     0,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,   115,    55,
             0,     0],
        [    0,     0,     0,     0,     0,     0,     0,    95,    60,
            40,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,   120,
           135,     0],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   130],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   165],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,   185],
        [    0,     0,     0,     0,     0,     0,     0,     0,     0,
             0,     0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 105000, 100000, 115000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,    110,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    125,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    170,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    105,
            100,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             75,    160,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     95],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    135],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  95000, 170000, 115000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     55,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    130,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    135,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
            160,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
            120,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     60],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 155000,  70000,  95000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     50,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,     55,    135,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     75,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
            125,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    175,
             75,    160,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             85,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    135],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 160000, 155000,  95000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    125,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    105,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    150,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
            110,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
             40,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             40,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  90000, 145000, 120000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    170,    115,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,    100,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    135,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     65,
             95,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             35,     90,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             70,     95,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     95],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  85000, 115000, 100000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,     95,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,     55,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     50,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
             40,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
            125,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            130,     30,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    165],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    100],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 180000,  35000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    155,     80,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,     45,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
             70,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
             75,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             50,    185,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    175],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    145],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  50000,  85000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,     70,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,     55,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     70,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
             75,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
            130,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             90,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    110],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000, 120000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,     75,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    160,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     95,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
            140,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
             45,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             80,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    140],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  50000, 155000, 155000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,     55,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,     70,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     65,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
            155,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             70,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    155],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    170],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 120000, 155000,  60000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,    180,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    150,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    125,    155,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    185,
             85,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
            150,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            155,     90,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    180],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 100000, 175000, 105000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,     70,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    105,     50,     55,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     45,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     45,
            135,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    185,
             80,    120,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            155,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    160],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,     80],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000,  55000, 125000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,     50,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,     60,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     45,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
            120,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
            120,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            175,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    185],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    130],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,    110],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)





from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()



with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(g_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    g_list_loaded = pickle.load(f)


n = 0
for g_dict in g_list_loaded:
    n += 1
    # if n > 1:
    #     break
    g = network(**g_dict)
    G = g.as_capacity_graph()
    number_of_nodes = len(G.node)
    import networkx as nx

    max_flow_value, partition = nx.minimum_cut(G, 0, number_of_nodes-1)
    hidden_node_list = [0]

    min_cut_set_s = ", ".join(str(s) for s in partition[0] if s not in hidden_node_list)

    template = latex_jinja_env.get_template('/utils/graph_max_flow_extension.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_blank = True,
        show_blank_answer=True,
        node_distance="3cm",
        g=g,
        show_flow_network_capacity_only=True,
        show_max_flow_network=True,

        min_cut_set_s=min_cut_set_s,
        max_flow_value=max_flow_value,
        source = u"v_1, v_2, v_3",
        hidden_node_list=hidden_node_list,
        target=u"v_{10}",
        set_allowed_range = [idx+1 for idx in range(number_of_nodes-len(hidden_node_list))],
        blank1_desc=u"求得该网络的最大流流量为",
        blank2_desc=u"最小割$(S^*, T^*)$中属于$S^*$集合的节点为"

    )
    # if n==1:
    r.clipboard_append(tex)
#    print("最短路条数",len(list(g.get_shortest_path())))

print(n)

