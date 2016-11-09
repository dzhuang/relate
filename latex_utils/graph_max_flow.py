# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra
from copy import deepcopy
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

MULTI_RESULT_QUESTION = "graph_max_flow.bin"

SAVED_QUESTION = "graph_max_flow.bin"

def is_qualified_question(mat, ref_g_list, mem_mat_list, saved_question=SAVED_QUESTION):

    qualified = False

    new_g_dict = deepcopy(ref_g_list)
    new_g_dict["graph"] = mat

    g = network(**new_g_dict)
    result = g.get_iterated_solution(method="bellman_ford")
    if len(result.shortest_path_list) > 1:
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
        print i
        g = g_dict["graph"]
        non_zero_idx = np.nonzero(g)
        all_value = g[non_zero_idx]
        print non_zero_idx
        print all_value
        all_value = all_value.tolist()[0]

        n = 0
        while n < 100:
            n += 1
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

import networkx as nx
from networkx.algorithms.flow import edmonds_karp

G = nx.DiGraph()
G.add_edge('s','r1', capacity=140)
G.add_edge('s','r2', capacity=150)
G.add_edge('s','r3', capacity=150)
G.add_edge('r1','a', capacity=75)
G.add_edge('r1','b', capacity=65)
G.add_edge('r2','a', capacity=40)
G.add_edge('r2','b', capacity=50)
G.add_edge('r2','c', capacity=60)
G.add_edge('r3','b', capacity=80)
G.add_edge('r3','c', capacity=70)
G.add_edge('a','d', capacity=60)
G.add_edge('a','e', capacity=45)
G.add_edge('b','d', capacity=70)
G.add_edge('b','e', capacity=55)
G.add_edge('b','f', capacity=45)
G.add_edge('c','e', capacity=70)
G.add_edge('c','f', capacity=90)
G.add_edge('d','t', capacity=120)
G.add_edge('e','t', capacity=190)
G.add_edge('f','t', capacity=130)

R = edmonds_karp(G, 's', 't')
flow_value = nx.maximum_flow_value(G, 's', 't')
print flow_value

cut_value, partition = nx.minimum_cut(G, 's', 't')
print partition

mat = nx.to_numpy_matrix(G, weight="capacity", dtype=int, nodelist=["s", "r1", "r2", "r3", "a", "b", "c", "d", "e", "f", "t"])
print repr(mat)

mat = np.matrix([
    [0, 140, 150, 150, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 75, 65, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 40, 50, 60, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 80, 70, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 60, 45, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 70, 55, 45, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 70, 90, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 120],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 190],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 130],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

g = { 'graph': mat,
    "edge_label_style_dict": {
        k:"pos=0.25" for k in [(1, 5), (3, 5), (2, 4), (2, 6), (5, 7), (5, 9), (6, 8), (4, 8)]
    },
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
    G = g.as_capacity_graph()
    number_of_nodes = len(G.node)
    import networkx as nx

    #R = edmonds_karp(G, 0, number_of_nodes-1)
    #max_flow_value = nx.maximum_flow_value(G, 0, number_of_nodes-1)
    max_flow_value, partition = nx.minimum_cut(G, 0, number_of_nodes-1)

    print partition[0]

    template = latex_jinja_env.get_template('/utils/graph_max_flow.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_blank = True,
        show_blank_answer=True,
        node_distance="3cm",
        g=g,
        min_cut_set_s=", ".join(str(s+1) for s in partition[0]),
        max_flow_value=max_flow_value,
        source = g.node_label_dict[0],
        target = g.node_label_dict[len(g.graph) - 1],
        set_allowed_range = [idx+1 for idx in range(number_of_nodes)],
        blank1_desc=u"求得该网络的最大流流量为",
        blank2_desc=u"最小割集$(S, \\bar S)$中属于$S$集合的节点为"
        #show_bellman_ford = True,
        #bellman_ford_result = g.get_iterated_solution(method="bellman_ford"),

    )

    r.clipboard_append(tex)
#    print "最短路条数",len(list(g.get_shortest_path()))

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