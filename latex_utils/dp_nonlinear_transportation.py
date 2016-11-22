# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra, dumps_tikz_doc
from copy import deepcopy
import numpy as np
import random
import pickle
import random

try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
    from Tkinter import Tk

r = Tk()
r.withdraw()
r.clipboard_clear()

from collections import OrderedDict

from latex_utils.utils.dynamic_programming import force_calculate_feasible_state, NonlinearTransportationProblem

total_resource=6
cost=[
    [(7,3), (5,3), (6,2), (5,5)],
    [(6,2), (4,6), (5,4), (9,2)]
]
supply = [6, 14]
demand = [7, 4, 4, 5]
company = [1,2,3,4]
invest = [0, 1, 2, 3, 4, 5, 6]


# gain=np.matrix([
#     0, 9, 12, 16, 21, np.nan,
#     0, 10, 16, 21, 31, 33,
#     0, 7, 12, 17, 21, np.nan,
#     0, 11, 20, 23, 34, 40,
#     np.nan, np.nan, 21, 25, 37, np.nan
# ]).reshape(5,6)
# total_resource=100
# invest = [0, 10, 20, 30, 40, 50]


dp = NonlinearTransportationProblem(
    total_resource=supply[0],
    cost=cost,
    supply=supply,
    demand=demand,
    decision_set=invest,
    allow_non_allocated_resource=False,
    opt_type="min"
)


#print dp.get_gain(3, 0)

print dp.get_allowed_state_i_idx_list(4)

print dp.get_allowed_decision_i_idx_list(4,2)

result = dp.solve()
print result
# #print result
# #result = dp.solve()
#
template = latex_jinja_env.get_template('/utils/dynamic_programming_template.tex')

tex = template.render(
    answer_table_iters=iter(range(1,50)),
    show_question=True,
    show_answer=True,
    show_blank=True,
    show_blank_answer=True,
    dp=dp,
    dp_result_list=[result],
)

r.clipboard_append(tex)
