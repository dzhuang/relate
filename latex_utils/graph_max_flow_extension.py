# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env
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

SAVED_QUESTION = "graph_max_flow_ext.bin"


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

    if len(partition[0]) == 9:
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
    sink_capacity = sum([G[u][v]["capacity"] for v in [7,8,9] for u in range(number_of_nodes-1) if G.has_edge(u,v)])


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
            g_test[:, -1] *= 1000
            # if i == 1:
                # print(g_test)
            if is_qualified_question(g_test, g_dict, mem_mat_list):
                mem_mat_list.append(g)
                print(repr(g_test))
                break


# generate_problem()
# print("here")
# exit()

g = { 'graph': np.matrix([[     0, 135000, 130000,  65000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     90,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    185,     65,    100,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    140,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     40,
             80,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
             55,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             85,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  90000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 185000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 170000,  35000,  50000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,     90,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    110,     95,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    175,    135,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
            120,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             30,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            175,    160,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 150000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 185000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  65000,  95000, 185000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,     90,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,     75,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    170,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
            125,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     95,
            140,    120,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             85,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 175000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  65000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  75000,  35000, 145000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,     40,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,    135,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    180,    185,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             60,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            105,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 185000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 110000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  80000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 180000, 105000, 170000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,     90,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    115,    120,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     30,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
            100,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    150,
             35,    125,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             50,    125,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 145000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  60000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  30000, 135000, 135000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,     75,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    185,     95,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    175,     80,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     50,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     95,
            165,    180,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            105,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  65000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  55000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 115000, 150000, 155000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    170,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,    160,    165,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    185,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    105,
            125,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
             35,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            125,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 150000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  75000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  75000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 170000,  40000,  55000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    115,     55,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     95,     70,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    145,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
            115,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
             35,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            140,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 155000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 130000,  60000,  40000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,    180,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     95,     75,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    170,    160,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
            110,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             75,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            115,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 150000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  30000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  65000, 110000,  35000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     65,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,    135,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     50,    120,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    125,
            180,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
            150,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            180,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 125000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 170000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 140000, 110000,  85000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     95,     75,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     70,    100,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    115,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     90,
             85,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    125,
            160,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             95,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 125000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 150000, 125000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,     95,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,     75,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    100,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     50,
            115,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
            125,    145,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            160,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  65000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 145000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  60000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000, 175000, 135000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    135,    140,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
            125,    185,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             85,     30,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 155000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 120000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  65000,  45000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    115,    100,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    100,    175,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     85,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
            155,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     65,
             30,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             95,    135,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 110000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 145000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 125000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  50000, 100000,  90000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,    120,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,    160,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     90,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
             65,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    145,
             40,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            170,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 165000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 125000,  45000,  35000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    180,     40,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,    135,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     75,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
            110,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
             45,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             95,    140,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 185000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  70000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  75000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)



g = { 'graph': np.matrix([[     0, 160000,  35000,  75000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,     60,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,    140,     85,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    115,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    145,
            115,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
            140,     30,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             55,     75,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  55000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 185000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  60000,  55000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    180,     60,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    175,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    100,    145,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
            155,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     65,
            150,    125,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  85000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 140000, 160000, 140000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    170,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,    115,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     55,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
            135,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     40,
             50,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 140000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  90000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  70000, 115000, 135000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    170,    160,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,     95,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     35,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
            175,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
            160,     90,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             55,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 125000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  30000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  50000,  50000,  80000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    150,     60,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,    160,    185,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     55,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
             90,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    180,
            140,    120,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             75,    180,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  30000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 155000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  75000,  70000, 140000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,     65,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    150,    100,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     40,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
            120,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             40,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             50,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 170000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 170000, 185000,  85000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,    170,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,    150,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    185,     30,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
            120,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    180,
             80,     70,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            125,    145,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  80000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 115000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  60000, 140000, 145000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     60,     70,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     70,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
             70,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    125,
             50,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            120,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  80000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 185000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 150000, 135000, 175000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,    180,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    170,     95,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    185,    145,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
             70,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
            105,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            150,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  55000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 175000, 180000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,     35,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    155,    140,    135,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     50,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    140,
            165,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    105,
             60,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             50,    180,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 165000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  95000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 170000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 140000,  45000, 180000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    185,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    170,     55,    185,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    115,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
            155,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
            155,    145,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 120000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 115000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 150000,  75000, 165000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    110,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    130,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    150,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
             90,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
             90,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            115,     95,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 175000,  65000, 115000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,     80,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,     90,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     45,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
             40,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
             60,    140,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            100,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 120000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  90000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 100000,  35000, 170000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    105,    175,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    155,    100,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     50,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
            160,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    180,
             85,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            170,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 180000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 140000, 150000,  35000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     95,     45,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    175,     80,    105,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     60,    110,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
            125,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
             45,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            180,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 165000, 185000,  95000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    105,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    170,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     95,    165,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
            105,    135,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             80,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  60000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)



g = { 'graph': np.matrix([[     0,  75000,  55000, 155000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,    145,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    180,    115,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    110,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    135,
             50,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    145,
            115,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            170,     90,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 185000, 185000, 170000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    150,    110,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    135,     50,    185,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    125,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             90,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
            170,     50,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             45,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  85000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 140000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 115000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 105000, 155000, 140000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    100,    155,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     65,     55,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    110,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    180,
            145,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
            100,     55,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             35,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 180000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 120000,  30000, 150000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,    130,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    155,    115,    145,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
            180,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
             75,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            115,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 175000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  85000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  65000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 110000,  35000, 185000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,     30,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,    170,    155,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    170,    165,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    175,
            100,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
            155,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             90,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  75000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 115000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 165000, 145000, 115000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,     40,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    150,     70,     95,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     85,    145,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
             80,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
            130,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            135,     80,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  90000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 165000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 120000,  30000,  40000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    115,     65,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    150,     65,    105,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     70,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
            160,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    110,
            140,     65,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            135,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 180000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  60000,  65000,  70000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     95,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     35,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    180,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
            170,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    105,
             90,    180,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            110,    120,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  85000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 180000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  80000, 155000, 130000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    150,    105,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     95,    165,     95,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    175,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
             70,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     40,
             65,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            155,    125,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 120000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 150000,  75000,  60000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    100,     80,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,     85,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     90,     35,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     80,
            120,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
             40,    145,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            115,     75,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 160000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  70000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 120000,  75000,  85000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,    175,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,    120,     80,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     55,    100,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    140,
            100,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
            160,    160,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            155,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  60000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 110000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000,  65000, 115000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     95,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    120,    120,    160,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    145,     85,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    160,
            150,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     95,
             80,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            170,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 135000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  75000, 140000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    110,     55,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    130,     95,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     30,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    150,
            140,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     90,
            155,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             70,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 165000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 180000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  90000, 130000,  95000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,    160,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    115,    105,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    150,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
            115,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     90,
            185,    165,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             40,    185,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 175000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 140000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  70000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 130000, 100000,  60000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,     35,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,    115,    110,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    130,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             90,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    115,
            150,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            165,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  75000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  60000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  55000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 105000,  90000, 100000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,    155,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     45,     55,     90,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    110,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
             60,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     45,
             95,    170,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            180,     30,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 140000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  70000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  70000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  70000,  60000,  70000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,     40,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,     35,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    180,    115,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             40,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
            145,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            140,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 145000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 140000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 145000,  75000,  85000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,     35,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     85,    160,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    120,    145,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
             35,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             85,     45,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            135,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 175000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  65000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  70000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 150000, 135000, 175000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    155,     55,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    100,    115,     75,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    155,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    155,
            155,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     90,
             35,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 170000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 145000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  60000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  90000, 105000,  65000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    150,    185,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     75,     35,     40,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    180,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     30,
            150,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
             55,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            115,    135,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 120000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 120000, 120000,  35000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,    100,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,     40,    180,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    130,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
            105,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    145,
             70,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             50,    120,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 175000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  90000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 175000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  75000, 165000,  75000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    185,    150,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,    180,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    185,    120,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    185,
             85,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    130,
            180,     35,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            155,    125,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  30000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  90000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 125000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  60000,  95000,  70000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     90,     55,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,    115,     65,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    175,     60,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    125,
             75,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     70,
             80,    100,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            180,    140,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 100000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 150000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 140000, 175000,  65000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    185,     60,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,     60,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    115,    125,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    170,
            110,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
            105,     70,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             80,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 115000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  35000,  70000, 175000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    140,    115,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    125,    155,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    135,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
            135,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     55,
             80,     70,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            145,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 185000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 165000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  95000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 185000, 155000,  60000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    175,    140,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,    105,     55,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    120,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     85,
             55,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     60,
             90,     60,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            135,    130,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  40000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 155000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000, 150000, 170000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    165,    135,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    160,    165,    120,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    105,    170,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    140,
            150,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    120,
            140,    180,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            105,    165,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  65000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 130000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  85000, 105000,  40000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     70,    155,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     55,    180,     70,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    110,     45,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    185,
            150,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     35,
            100,     85,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             30,    110,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  70000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 165000, 170000, 110000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     40,     80,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     50,     40,     50,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    135,    150,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     40,
             80,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     75,
            105,     40,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             40,    155,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 180000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 155000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 105000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0, 135000, 185000, 150000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     35,    115,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     80,     70,    175,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    135,    130,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    145,
            100,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    100,
            100,    150,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
            125,     30,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  35000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  90000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  60000, 180000, 160000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    100,     70,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    180,    135,    160,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,     70,    150,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    165,
            180,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    185,
             70,    105,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             95,    185,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  75000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0, 120000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[     0,  65000, 120000,  95000,      0,      0,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,     30,     30,      0,      0,
              0,      0,      0],
        [     0,      0,      0,      0,    130,    185,    185,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,    135,    150,      0,
              0,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,    150,
            125,      0,      0],
        [     0,      0,      0,      0,      0,      0,      0,     40,
            110,     90,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
             65,    115,      0],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  45000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  95000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,  50000],
        [     0,      0,      0,      0,      0,      0,      0,      0,
              0,      0,      0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(5, 9): 'pos=0.25', (2, 6): 'pos=0.25', (6, 8): 'pos=0.25', (4, 8): 'pos=0.25', (5, 7): 'pos=0.25', (1, 5): 'pos=0.25', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)


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
    from copy import deepcopy
    g_dict_temp = deepcopy(g_dict)
    #mat = g_dict_temp["graph"]
    #mat[0,:] *= 1000
    #mat[:,-1] *= 1000
    #mat[0,0]=0
    #mat[-1,-1]=0
    #mat = abs(mat)
    #print(repr(mat))
    #print(mat[0,1]>0)
    g2 = network(**g_dict_temp)
    G = g2.as_capacity_graph()
    number_of_nodes = len(G.node)
    import networkx as nx

    max_flow_value, partition = nx.minimum_cut(G, 0, number_of_nodes-1)
    hidden_node_list = [0, number_of_nodes-1]

    min_cut_set_s = ", ".join(str(s) for s in partition[0] if s not in hidden_node_list)

    template = latex_jinja_env.get_template('/utils/graph_max_flow_extension.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_blank = True,
        show_blank_answer=True,
        node_distance="3cm",
        g=g2,
        show_flow_network_capacity_only=True,
        show_max_flow_network=True,

        min_cut_set_s=min_cut_set_s,
        max_flow_value=max_flow_value,
        source = u"v_1, v_2, v_3",
        hidden_node_list=hidden_node_list,
        target=u"v_7, v_8, v_9",
        set_allowed_range = [idx+1 for idx in range(number_of_nodes-len(hidden_node_list))],
        blank1_desc=u"求得该网络的最大流流量为",
        blank2_desc=u"最小割$(S^*, T^*)$中属于$S^*$集合的节点为"

    )
    # if n==1:
    r.clipboard_append(tex)
#    print("最短路条数",len(list(g.get_shortest_path())))

r.mainloop()
print(n)

