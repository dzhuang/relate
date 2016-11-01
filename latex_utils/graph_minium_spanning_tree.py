# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra
from copy import deepcopy
import numpy as np

SAVED_QUESTION = "graph_MST.bin"

g_list = []

g = {"graph":
         np.matrix([[0., 5., 0., 0., 0., 0., 0., 5., 0., 0.],
                 [0., 0., 0., 9., 0., 0., 7., 8., 0., 0.],
                 [0., 14., 0., 0., 0., 7., 12., 0., 0., 0.],
                 [0., 10., 0., 0., 0., 14., 0., 0., 0., 0.],
                 [0., 0., 0., 0., 0., 0., 13., 0., 0., 0.],
                 [0., 0., 0., 0., 0., 0., 0., 0., 0., 13.],
                 [14., 0., 13., 7., 0., 0., 0., 10., 6., 0.],
                 [0., 0., 0., 0., 0., 0., 0., 0., 12., 0.],
                 [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                 [6., 0., 0., 0., 11., 0., 0., 0., 0., 0.]]),
     "node_label_dict": None,
     "edge_label_style_dict":None,
     "directed": False,
     }

g_list.append(g)


from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()


import pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(g_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    g_list_loaded = pickle.load(f)


n = 0
for g_dict in g_list_loaded:
    n += 1
    # r.clipboard_clear()
    g = network(**g_dict)

    template = latex_jinja_env.get_template('/utils/graph_shortest_path.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_answer = True,
        g=g,
        source = g.node_label_dict[0],
        target = g.node_label_dict[len(g.graph) - 1],
    )

    r.clipboard_append(tex)


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