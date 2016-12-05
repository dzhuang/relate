# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra
from copy import deepcopy
import numpy as np
import random
import pickle
from networkx.exception import NetworkXUnbounded

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

MULTI_RESULT_QUESTION = "graph_bellman_sp_multiple.bin"

SAVED_QUESTION = "graph_bellman_sp_multiple.bin"

REQUIRED_NIT = [5, 6]
REQUIRED_NUMBER_OF_SP = [2,3]

def is_qualified_question(mat, ref_g_list, mem_mat_list, saved_question=SAVED_QUESTION):

    qualified = False

    new_g_dict = deepcopy(ref_g_list)
    new_g_dict["graph"] = mat

    g = network(**new_g_dict)
    try:
        result = g.get_iterated_solution(method="bellman_ford")
    except (NetworkXUnbounded, ValueError):
        return False

    if result.nit not in REQUIRED_NIT:
        return False
    if not len(result.shortest_path_list) in REQUIRED_NUMBER_OF_SP:
        return False

    question_exist = False
    for i, c in enumerate(mem_mat_list):
        if np.all(mat==c):
            print "----------------------question exists-------------------"
            question_exist = True
            return False
            break

    if not question_exist:
        suggestion = "g = { 'graph': %s" % repr(mat)
        suggestion = suggestion.replace("matrix", "np.matrix")
        r.clipboard_append(suggestion)
        r.clipboard_append(",\n")
        if new_g_dict["node_label_dict"]:
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

    print len(g_list_loaded)

    for i, g_dict in enumerate(g_list_loaded):
        # print i
        g = g_dict["graph"]
        non_zero_idx = np.nonzero(g)
        all_value = g[non_zero_idx]
        # print non_zero_idx
        # print all_value
        all_value = all_value.tolist()[0]

        n = 0
        while n < 100:
            n += 1
            # print "-------------%s--------------" % n
            g_test = deepcopy(g)
            random.shuffle(all_value)
            new_value = np.array([all_value])
            g_test[non_zero_idx] = new_value
            if i == 1:
                print g_test
            if is_qualified_question(g_test, g_dict, mem_mat_list):
                mem_mat_list.append(g)
                print repr(g_test)
                break


# generate_problem()
# print "here"
# exit()

g = { 'graph': np.matrix([[ 0, -3,  2,  3,  0,  0,  0,  0],
        [ 0,  0,  2,  8,  0,  6,  0,  0],
        [ 0,  0,  0,  3,  3,  0,  3,  0],
        [ 0,  0,  0,  0,  5,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  2,  0,  4,  9,  0,  0, -2],
        [ 0,  0, -2,  0, -8,  0,  0, -5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(1, 2): 'pos=0.25', (6, 2): '', (2, 4): 'pos=0.75', (3, 6): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  8,  3,  0,  0,  0,  0],
        [ 0,  0,  5,  0,  9,  5,  0,  0],
        [ 0,  0,  0,  0,  0, -1,  6,  0],
        [ 0,  0,  1,  0,  0,  0,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  2,  0,  4,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  8, -2, 10,  0,  0,  0,  0],
        [ 0,  0,  7,  0,  4,  3,  0,  0],
        [ 0,  0,  0,  0,  0, -3,  4,  0],
        [ 0,  0,  3,  0,  0,  0,  5,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  3,  0,  2,  8],
        [ 0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  3,  6,  2,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  0,  0,  0],
        [ 0, -3,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0, 10,  0,  0],
        [ 0,  0,  0,  6,  0,  2, 10,  4],
        [ 0,  0,  0,  0,  3,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5,  5,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  5,  0,  0,  0],
        [ 0,  6,  0, -2,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  0,  0],
        [ 0,  0,  0, 10,  0,  4,  3, 10],
        [ 0,  0,  0,  0, -3,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  3,  2,  0,  0,  0,  0],
        [ 0,  0,  0, -2, -1,  0,  0,  0],
        [ 0,  0,  0,  2,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  3,  0,  5],
        [ 0,  0,  0,  0,  1,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  0,  3,  6,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  0,  0,  0],
        [ 0,  9,  0,  0,  4,  0,  0,  5,  0],
        [ 0,  0, -3,  0,  0,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0, -7,  2,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  8,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  7],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0, -6,  9,  5,  0,  0,  0,  0],
        [ 0,  0,  5,  0,  8,  1,  0,  0],
        [ 0,  0,  0,  3,  0,  5,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  3,  0,  2,  5],
        [ 0,  0, -2,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1, -1,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  5,  0,  5,  0],
        [ 0, -1,  0,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  4,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  2,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  3,  2,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  8,  0,  4,  0],
        [ 0, -4,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  3,  0,  0,  7],
        [ 0,  0,  0,  0,  0,  2,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  4,  2,  0,  0,  0,  0,  0],
        [ 0,  0,  4,  0,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  3,  5,  1,  0,  0],
        [ 0,  0,  2,  0,  0,  0,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  4,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  3,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0, -1],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  8,  3,  2,  0,  0,  0,  0],
        [ 0,  0,  5,  0,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  6,  5,  6,  0],
        [ 0,  0,  2,  0,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  5,  0,  0,  5],
        [ 0,  0,  0,  0,  0, -2,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0, -4,  7,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  6,  1,  0,  0,  0],
        [ 0,  0,  0,  6,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  9,  4,  0],
        [ 0,  0,  0,  0,  0,  7,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  6,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(1, 3): 'pos=0.25', (4, 6): 'pos=0.25', (3, 5): 'pos=0.25', (2, 4): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  3,  6,  0,  0,  0,  0],
        [ 0,  0,  7,  0,  4,  3,  0,  0],
        [ 0,  0,  0, -1,  0, 10,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  8,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  9],
        [ 0,  0,  0,  0,  1,  0,  2,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1,  1,  6,  0,  0,  0,  0],
        [ 0,  0,  3,  0,  7, -1,  0,  0],
        [ 0,  0,  0,  4,  0,  8,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  6,  0,  5,  9],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  7,  2,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  6,  0,  0],
        [ 0,  2,  0,  0,  1,  0,  0,  0],
        [ 0,  0, -3,  0,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  3,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  7,  2],
        [ 0,  0,  0,  0,  0,  0,  0, -1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(0, 3): 'bend right'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  8,  3,  6,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  1,  6,  0,  0],
        [ 0,  5,  0,  0,  1,  0,  0,  0],
        [ 0,  0, -2,  0,  2,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  5,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  1,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(0, 3): 'bend right'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1,  2,  0,  0,  0,  0,  0],
        [ 0,  0,  2,  2,  0,  0,  0,  0],
        [ 0,  0,  0,  1,  2,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  3,  5,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0, -1],
        [ 0,  0,  0,  0,  0,  4,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5,  0,  8,  0,  7,  0,  0],
        [ 0,  0,  6,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  0,  0,  5],
        [ 0,  0, -5,  0,  8, 10,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  6,  2],
        [ 0,  0,  0,  0,  0,  0,  7,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  0,  5,  0,  3,  0,  0],
        [ 0,  0, 12, -4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  8,  0,  0,  2],
        [ 0,  0,  6,  0,  7,  8,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  9, -1],
        [ 0,  0,  0,  0,  0,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  6,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  2, -1,  0,  0,  0],
        [ 0,  1,  0,  3,  1,  3,  0,  0],
        [ 0,  0,  0,  0, -1,  5,  2,  0],
        [ 0,  0,  0,  0,  0,  3,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  5,  7],
        [ 0,  0,  0,  0,  0,  0,  0,  8],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(4, 5): 'pos=0.25', (2, 5): 'pos=0.15', (3, 4): 'pos=0.25', (1, 4): 'bend left, pos=0.25', (3, 6): 'bend right, pos=0.75'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  3,  0,  0,  0,  0,  0],
        [ 0,  0,  0, -1,  5,  0,  0,  0],
        [ 0,  2,  0,  7,  2,  3,  0,  0],
        [ 0,  0,  0,  0,  8,  2,  3,  0],
        [ 0,  0,  0,  0,  0,  5,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  7],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(4, 5): 'pos=0.25', (2, 5): 'pos=0.15', (3, 4): 'pos=0.25', (1, 4): 'bend left, pos=0.25', (3, 6): 'bend right, pos=0.75'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  7,  8,  2,  0,  0,  0,  0],
        [ 0,  0,  6,  0,  2,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  7,  0],
        [ 0,  0, -2,  0,  0,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  5,  0,  0,  8],
        [ 0,  0,  0,  0,  0,  3,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  5,  3,  0,  0,  0,  0],
        [ 0,  0,  6,  0, -3,  2,  0,  0],
        [ 0,  0,  0,  0,  0,  3,  5,  0],
        [ 0,  0,  7,  0,  0,  0,  8,  0],
        [ 0,  0,  0,  0,  0,  1,  0,  7],
        [ 0,  0,  0,  0,  0,  0,  6,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5,  3,  2,  0,  0,  0,  0,  0],
        [ 0,  0, -1,  0,  1,  0,  0,  0,  0],
        [ 0,  0,  0,  6,  4,  6,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2,  6],
        [ 0,  0,  0,  0,  0,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1,  4,  5,  0,  0,  0,  0,  0],
        [ 0,  0,  2,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  3,  4,  4,  5,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  0,  0, -1,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  1,  1,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5,  1,  4,  0,  0,  0,  0,  0],
        [ 0,  0,  3,  0,  6,  0,  0,  0,  0],
        [ 0,  0,  0,  4, -1,  2,  6,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  0,  0],
        [ 0,  0,  0,  0,  0,  4,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  4, -2,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5,  0,  6,  0,  2,  0,  0],
        [ 0,  0,  9,  0,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  4,  0,  0,  0,  0,  5,  0],
        [ 0,  0,  1,  0,  0,  0,  0,  7],
        [ 0,  0,  0, -1,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  3,  0,  0, 10],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  0,  6,  0,  2,  0,  0],
        [ 0,  0,  6,  0, 10,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0, -2,  0,  0,  0,  0,  3,  0],
        [ 0,  0, -1,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  7,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  4,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  8,  5,  0,  0,  0,  0],
        [ 0,  0,  6,  0,  6,  7,  0,  0],
        [ 0,  0,  0,  0,  1,  0,  0,  0],
        [ 0,  0,  3,  0,  0,  0,  5,  0],
        [ 0,  0,  0,  0,  0, -1, 12,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5,  6,  4,  0,  0,  0,  0],
        [ 0,  0,  6,  0,  2,  5,  0,  0],
        [ 0,  0,  0,  0,  1,  0,  0,  0],
        [ 0,  0,  5,  0,  0,  0,  7,  0],
        [ 0,  0,  0,  0,  0, -1,  3,  8],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1,  2,  0,  0,  0,  0,  0],
        [ 0,  0,  3,  5,  2,  0,  0,  0],
        [ 0,  0,  0,  0,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  4,  0],
        [ 0,  0,  0, -2,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  2,  0,  0,  0,  0,  0],
        [ 0,  0,  4,  2,  1,  0,  0,  0],
        [ 0,  0,  0,  0, -1,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  1,  0],
        [ 0,  0,  0,  4,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  6, 10,  0,  0,  0,  0],
        [ 0,  0,  5,  0, 15,  5,  0,  0],
        [ 0,  0,  0,  3, 12,  5,  5,  0],
        [ 0,  0,  0,  0,  0,  9,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  4,  0,  0,  7],
        [ 0,  0,  0,  0,  0, -3,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(1, 5): 'pos=0.25', (2, 6): 'pos=0.75', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  9,  4,  1,  0,  0,  0,  0],
        [ 0,  0,  4,  0,  7,  0,  0,  0],
        [ 0,  0,  0,  0, -2,  4,  8,  0],
        [ 0,  0,  3,  0,  0,  7,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  8],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  9,  4,  3,  0,  0,  0,  0],
        [ 0,  0,  4,  0,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  3,  7,  8,  0],
        [ 0,  0, -3,  0,  0,  2,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  8],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  3,  0,  5,  0,  0,  0,  0],
        [ 0,  0,  0,  3,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  4,  0,  7,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0, -2,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  6,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  4,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  1,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  5,  0, -4,  0,  0],
        [ 0,  0,  0,  0,  0,  5,  7,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  4,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  3,  2,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0, -2,  7,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  4,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  5,  0,  4,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  4,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  5,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  6,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)



g = { 'graph': np.matrix([[ 0,  3,  4,  3,  0,  0,  0,  0],
        [ 0,  0, -2,  2,  0,  3,  0,  0],
        [ 0,  0,  0,  2,  2,  0, -3,  0],
        [ 0,  0,  0,  0,  3,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0, -5],
        [ 0,  3,  0, -8,  3,  0,  0,  5],
        [ 0,  0,  9,  0,  8,  0,  0, -2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(1, 2): 'pos=0.25', (6, 2): '', (2, 4): 'pos=0.75', (3, 6): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  9,  5,  0,  0,  0,  0],
        [ 0,  0, -1,  0,  5,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  4,  8,  0],
        [ 0,  0,  2,  0,  0,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  2,  0,  2,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5, 10,  3,  0,  0,  0,  0],
        [ 0,  0,  3,  0,  5,  4,  0,  0],
        [ 0,  0,  0,  0,  0, -3,  2,  0],
        [ 0,  0,  4,  0,  0,  0,  8,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  8,  0,  7,  3],
        [ 0,  0,  0,  0,  0,  0,  0, -2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2, -3,  6,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  4,  0,  0,  0],
        [ 0,  5,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0, 10,  0,  0],
        [ 0,  0,  0,  6,  0,  4,  2, 10],
        [ 0,  0,  0,  0,  3,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  5, 10,  0,  0,  0,  0],
        [ 0,  0,  0,  0, -3,  0,  0,  0],
        [ 0, 10,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  5,  0,  0],
        [ 0,  0,  0,  2,  0,  2,  5,  6],
        [ 0,  0,  0,  0,  3,  0, -2,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  2,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  1,  3,  0,  0,  0],
        [ 0,  0,  0,  5,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0, -1,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0, -2],
        [ 0,  0,  0,  0,  0,  3,  0,  2],
        [ 0,  0,  0,  0,  2,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  0,  7,  9,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  6,  0,  0,  0],
        [ 0,  2,  0,  0,  8,  0,  0,  2,  0],
        [ 0,  0, -7,  0,  0,  0,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  2, -3,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  5,  0,  0],
        [ 0,  0,  0,  0,  0,  4,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1,  2,  6,  0,  0,  0,  0],
        [ 0,  0, -2,  0,  8,  3,  0,  0],
        [ 0,  0,  0,  5,  0,  5,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  5,  0, -6,  9],
        [ 0,  0,  5,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5, -1,  1,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  0,  2,  0],
        [ 0,  4,  0,  5,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  2,  0,  0, -1],
        [ 0,  0,  0,  0,  0,  2,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  8,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  4,  0,  3,  0],
        [ 0,  2,  0,  7,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  3,  0,  0,  6],
        [ 0,  0,  0,  0,  0, -4,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  3,  4,  5,  0,  0,  0,  0,  0],
        [ 0,  0,  1,  0,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  2,  2,  0,  0],
        [ 0,  0,  3,  0,  0,  0,  4,  0,  0],
        [ 0,  0,  0,  0,  0,  5,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  3,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0, -1],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1,  5,  4,  0,  0,  0,  0],
        [ 0,  0,  4,  0,  8,  0,  0,  0],
        [ 0,  0,  0,  0,  3,  4,  4,  0],
        [ 0,  0,  7,  0,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  0, -1,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  4,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  8],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  3,  6, -2,  0,  0,  0,  0],
        [ 0,  0,  8,  0,  5,  0,  0,  0],
        [ 0,  0,  0,  0,  6,  4,  2,  0],
        [ 0,  0,  2,  0,  0,  0,  5,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  3,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  5,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  5,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  9,  7,  0,  0,  0],
        [ 0,  0,  0,  4, -4,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  4,  6,  0],
        [ 0,  0,  0,  0,  0,  7,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  6,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(2, 4): 'pos=0.25', (1, 3): 'pos=0.25', (4, 6): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  4,  8,  0,  0,  0,  0],
        [ 0,  0, 10,  0,  7,  6,  0,  0],
        [ 0,  0,  0,  3,  0,  4,  0,  0],
        [ 0,  0,  0,  0,  0,  6,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0, -1,  0,  9,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  8,  5,  6,  0,  0,  0,  0],
        [ 0,  0,  1,  0,  3,  6,  0,  0],
        [ 0,  0,  0,  4,  0,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0, -1],
        [ 0,  0,  0,  0,  2,  0,  9,  7],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  6,  7,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  2, -1,  0,  0],
        [ 0,  1,  0,  0,  2,  0,  0,  0],
        [ 0,  0,  2,  0,  6,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  3, -3,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  7],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(0, 3): 'bend right'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2, -2,  8,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  6,  5,  0,  0],
        [ 0,  5,  0,  0,  1,  0,  0,  0],
        [ 0,  0,  1,  0,  6,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(0, 3): 'bend right'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  2,  0,  0,  0,  0,  0],
        [ 0,  0,  1,  2,  0,  0,  0,  0],
        [ 0,  0,  0, -1,  2,  0,  0,  0],
        [ 0,  0,  0,  0,  1,  5,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  4,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  0,  3,  0,  3,  0,  0],
        [ 0,  0,  6, -5,  0,  0,  0,  0],
        [ 0,  0,  0,  0, 10,  0,  0,  2],
        [ 0,  0,  5,  0,  8,  7,  5,  0],
        [ 0,  0,  0,  0,  0,  0,  7,  8],
        [ 0,  0,  0,  0,  0,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  9,  0, 12,  0,  5,  0,  0],
        [ 0,  0,  6, -1,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  4,  0,  0,  3],
        [ 0,  0,  7,  0,  2,  8,  6,  0],
        [ 0,  0,  0,  0,  0,  0, -4,  2],
        [ 0,  0,  0,  0,  0,  0,  8,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  2,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  7,  1,  0,  0,  0],
        [ 0,  3,  0,  2,  1,  5,  0,  0],
        [ 0,  0,  0,  0, -1,  8,  3,  0],
        [ 0,  0,  0,  0,  0,  5,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  4],
        [ 0,  0,  0,  0,  0,  0,  0, -1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(4, 5): 'pos=0.25', (2, 5): 'pos=0.15', (3, 4): 'pos=0.25', (3, 6): 'bend right, pos=0.75', (1, 4): 'bend left, pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  3,  3,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  2,  6,  0,  0,  0],
        [ 0,  5,  0,  2,  6,  8,  0,  0],
        [ 0,  0,  0,  0,  7,  3,  2,  0],
        [ 0,  0,  0,  0,  0,  3,  7,  0],
        [ 0,  0,  0,  0,  0,  0,  3, -1],
        [ 0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(4, 5): 'pos=0.25', (2, 5): 'pos=0.15', (3, 4): 'pos=0.25', (3, 6): 'bend right, pos=0.75', (1, 4): 'bend left, pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  7,  7,  3,  0,  0,  0,  0],
        [ 0,  0,  4,  0,  8,  6,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  8,  0],
        [ 0,  0,  6,  0,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  3,  0,  0,  5],
        [ 0,  0,  0,  0,  0, -2,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  5,  3,  1,  0,  0,  0,  0],
        [ 0,  0,  6,  0,  2,  5,  0,  0],
        [ 0,  0,  0,  0,  0,  3,  8,  0],
        [ 0,  0,  2,  0,  0,  0,  7,  0],
        [ 0,  0,  0,  0,  0,  7,  0,  6],
        [ 0,  0,  0,  0,  0,  0, -3,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  1,  4,  2,  0,  0,  0,  0,  0],
        [ 0,  0,  3,  0,  2,  0,  0,  0,  0],
        [ 0,  0,  0,  6, -1,  5,  4,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  6,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  1,  3],
        [ 0,  0,  0,  0,  0,  5,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  5,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  1,  0,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  5,  4,  1,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  6,  0,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  3, -1,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0, -1,  5,  4,  0,  0,  0,  0,  0],
        [ 0,  0,  2,  0,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  6,  5,  3,  2,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  5,  0,  0],
        [ 0,  0,  0,  0,  0,  4,  0,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  1,  4,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0, -2],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0, 10,  0,  7,  0,  6,  0,  0],
        [ 0,  0,  3,  0,  5,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  9,  0,  0,  0,  0,  6,  0],
        [ 0,  0,  1,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  2,  0,  0,  5,  0],
        [ 0,  0,  0,  0, -1,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  7,  0,  4,  0,  3,  0,  0],
        [ 0,  0,  5,  0, 10,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2],
        [ 0,  6,  0,  0,  0,  0,  3,  0],
        [ 0,  0,  2,  0,  0,  0,  0,  4],
        [ 0,  0,  0, -1,  0,  0,  6,  0],
        [ 0,  0,  0,  0, -2,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  2,  7,  0,  0,  0,  0],
        [ 0,  0,  8,  0,  6,  6,  0,  0],
        [ 0,  0,  0,  0,  6,  0,  0,  0],
        [ 0,  0,  5,  0,  0,  0, 12,  0],
        [ 0,  0,  0,  0,  0,  3,  1,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0, -1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  6,  4,  0,  0,  0,  0],
        [ 0,  0, -1,  0,  5,  6,  0,  0],
        [ 0,  0,  0,  0,  5,  0,  0,  0],
        [ 0,  0,  7,  0,  0,  0,  8,  0],
        [ 0,  0,  0,  0,  0,  3,  1,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  6],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  2,  4, -2,  0,  0,  0],
        [ 0,  0,  0,  0,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  2,  4,  0],
        [ 0,  0,  0,  2,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  5,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  2,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  2,  4,  2,  0,  0,  0],
        [ 0,  0,  0,  0, -1,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  3,  1,  0],
        [ 0,  0,  0,  1,  0,  0,  2,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  3],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  3,  7,  6,  0,  0,  0,  0],
        [ 0,  0, 12,  0,  6, 10,  0,  0],
        [ 0,  0,  0, 15,  6,  3,  9,  0],
        [ 0,  0,  0,  0,  0,  4,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  5],
        [ 0,  0,  0,  0, -3,  0,  0,  5],
        [ 0,  0,  0,  0,  0,  5,  0,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict":{(1, 5): 'pos=0.25', (2, 6): 'pos=0.75', (2, 4): 'pos=0.25', (3, 5): 'pos=0.25'},
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  7,  8,  4,  0,  0,  0,  0],
        [ 0,  0, -2,  0,  3,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  8,  4,  0],
        [ 0,  0,  1,  0,  0,  9,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  7],
        [ 0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  6,  9,  0,  0,  0,  0],
        [ 0,  0,  8,  0,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  2,  4,  8,  0],
        [ 0,  0,  3,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  7,  4],
        [ 0,  0,  0,  0,  0,  0,  0, -3],
        [ 0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  6,  1,  0,  2,  0,  0,  0,  0],
        [ 0,  0,  0,  5,  3,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  7,  4,  0,  0,  0],
        [ 0,  0,  0,  0, -2,  0,  3,  0,  0],
        [ 0,  0,  0,  0,  0,  3,  6,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  1,  3,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  4,  2],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  4,  5,  0,  2,  0,  0,  0,  0],
        [ 0,  0,  0,  5,  4,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  3,  4,  0,  0,  0],
        [ 0,  0,  0,  0,  6,  0,  4,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  7,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  6,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  2,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0, -4],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
}
g_list.append(g)

g = { 'graph': np.matrix([[ 0,  7,  5,  0,  6,  0,  0,  0,  0],
        [ 0,  0,  0, -2,  2,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  4,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  3,  0,  2,  0,  0],
        [ 0,  0,  0,  0,  0,  5,  6,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  4,  4,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  3,  4],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0]]),
    "node_label_dict": None,
    "edge_label_style_dict": None,
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
    # r.clipboard_clear()
    g = network(**g_dict)

    dijkstra_is_allowed = True
    dijkstra_result = None

    try:
        dijkstra_result = g.get_iterated_solution(method="dijkstra")
    except NetworkNegativeWeightUsingDijkstra:
        dijkstra_is_allowed = False

    template = latex_jinja_env.get_template('/utils/graph_shortest_path.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_answer = True,
        g=g,
        source = g.node_label_dict[0],
        target = g.node_label_dict[len(g.graph) - 1],
        show_dijkstra = True,
        dijkstra_is_allowed=dijkstra_is_allowed,
        dijkstra_result = dijkstra_result,
        show_bellman_ford = True,
        bellman_ford_result = g.get_iterated_solution(method="bellman_ford"),
    )

    r.clipboard_append(tex)
    print "最短路条数",len(list(g.get_shortest_path()))

print n



# preamble of the picture of the graph.
"""

{% set preabmle %}
\usepackage{tikz}
\usetikzlibrary{graphs,graphs.standard,graphdrawing,quotes,shapes,arrows.meta}
\usegdlibrary{force}
{% endset %}

<p align="middle">
{% call latex(compiler="lualatex", image_format="png", alt="question", tex_preamble=preamble) %}


{% endcall %}
</p>


"""

# 求解结果
"""
{% from "latex.jinja" import mytabular_preamble as preamble %}

<p align="middle">
{% call latex(compiler="pdflatex", image_format="png", alt="question", tex_preamble=preamble) %}

{% endcall %}
</p>
"""