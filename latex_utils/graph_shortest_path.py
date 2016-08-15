# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network
from copy import deepcopy
import numpy as np

g_list = []

## ---------------------------------------------------
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
g_matrix = np.matrix(g_array)

#g_list.append({"graph":g_matrix, "node_label_dict":None, "edge_label_style_dict":None})

## ---------------------------------------------------

g_matrix = np.matrix([
    [0,2,5,4,0,0,0,0],
    [0,0,-4,2,0,9,0,0],
    [0,0,0,3,-2,0,3,0],
    [0,0,0,0,2,0,8,0],
    [0,0,0,0,0,0,0,3],
    [0,-8,0,2,3,0,0,4],
    [0,0,-2,0,4,0,0,6],
    [0,0,0,0,0,0,0,0]
])


g_list.append({
    "graph":g_matrix,
    "node_label_dict":None,
    "edge_label_style_dict":{(1,2):"pos=0.25",(6,2):"",(3,6):"pos=0.25", (2,4):"pos=0.75"}

    # use bend left=0 to undo bending of edges.
})


#pred, dist = shortest_path_tweaked.bellman_ford_predecessor_and_distance(g, source=0, weight="weight")
#print pred, dist


# all_sp = graph.get_shortest_path()

# for sp in all_sp:
#     print sp


# template = latex_jinja_env.get_template('/utils/lp_model.tex')
# tex = template.render(
#     description = u"""
#     """,
#     lp = lp
# )



#_file_write("lp_test.tex", tex.encode('UTF-8'))

from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()


#lp_json_list = []
#lp_json_list.append(lp.json)
#lp_json_list.append(lp2.json)



import pickle
#import dill as pickle
with open('network.bin', 'wb') as f:
    pickle.dump(g_list, f)

with open('network.bin', 'rb') as f:
    g_list_loaded = pickle.load(f)


for g_dict in g_list_loaded:
    g = network(**g_dict)

    g.get_iterated_solution(method="dijkstra")
    g_graph = g.as_latex()

    #x = g.get_iterated_solution(method="dijkstra")
    #print type(x)

    y = g.get_iterated_solution(method="bellman_ford")
    #print type(y)

    #print g_graph

    # print g.p_node_list
    # print g.dist_list
    # print g.pred_list
    # print g.seen_list
    # g.get_iterated_solution(method="bellman_ford")
    # print g.p_node_list
    # print g.dist_list
    # print g.final_pred
    # for path in g.get_shortest_path():
    #     print path

    # print g.pred_list
    # print g.seen_list

#     lp.solve(method="simplex")
#     lp.sensitive_analysis()
#
#     template = latex_jinja_env.get_template('/utils/lp_sensitivity.tex')
#     tex = template.render(
#         question_iters = iter(range(0,5)),
#         iters=iter(range(0, 20)),
#         show_question = True,
#         show_answer = True,
# #        standardized_lp = lp.standardized_LP(),
#         #pre_description=u"""有线性规划问题
#         #""",
#         #after_description=u"""
#         #""",
#         lp=lp,
# #        show_only_opt_table = True,
#     )

    # r.clipboard_append(tex)


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