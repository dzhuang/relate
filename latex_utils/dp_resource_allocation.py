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

from latex_utils.utils.dynamic_programming import ResourceAllocationDP, force_calculate_feasible_state

total_resource=800
gain=np.matrix([
    [0, 130, 150, np.nan, np.nan, np.nan],
    [0, 100, 160, 210, np.nan, 410],
    [0, 100, 120, np.nan, 210, np.nan],
    [np.nan, 110, 200, 250, 330, 370],
    [np.nan, np.nan, 210, 290, 320, np.nan]
])

company = [1,2,3,4,5]
invest = [0, 100, 200, 300, 400, 500]


# gain=np.matrix([
#     0, 9, 12, 16, 21, np.nan,
#     0, 10, 16, 21, 31, 33,
#     0, 7, 12, 17, 21, np.nan,
#     0, 11, 20, 23, 34, 40,
#     np.nan, np.nan, 21, 25, 37, np.nan
# ]).reshape(5,6)
# total_resource=100
# invest = [0, 10, 20, 30, 40, 50]


# gain=np.matrix([
#     0, 9, 14, 18, 21, 24,
#     0, 4, 9, 15, 22, 30,
#     0, 10, 14, 16, 20, 26,
# ]).reshape(3,6)
# total_resource=5
# invest = [0, 1, 2, 3, 4, 5]

dp = ResourceAllocationDP(
    total_resource=total_resource,
    gain=gain,
    decision_set=invest,
    allow_non_allocated_resource=False,
    #opt_type="min"
)


result_force_calculate_feasible_state = dp.solve(allow_state_func=force_calculate_feasible_state)
result = dp.solve()
print result
#result = dp.solve()

template = latex_jinja_env.get_template('/utils/dynamic_programming_template.tex')

result_list = [result_force_calculate_feasible_state]
show_only_force_calculate_feasible_state = False
if not show_only_force_calculate_feasible_state:
    can_optimize_stage = []
    equal = True
    for i, j in zip(result.items(), result_force_calculate_feasible_state.items()):
        if i == j:
            continue
        else:
            print i
            equal = False
            break

    if not equal:
        result_list.append(result)

tex = template.render(
    answer_table_iters=iter(range(1,50)),
    show_question=True,
    show_answer=True,
    show_blank=True,
    show_blank_answer=True,
    dp=dp,
    dp_result_list=result_list,
)

r.clipboard_append(tex)
