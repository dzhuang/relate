# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra, dumps_tikz_doc
from copy import deepcopy
import numpy as np
import random
import pickle

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


gain=np.matrix([
    0, 9, 12, 16, 21, np.nan,
    0, 10, 16, 21, 31, 33,
    0, 7, 12, 17, 21, np.nan,
    0, 11, 20, 23, 34, 40,
    np.nan, np.nan, 21, 25, 37, np.nan
]).reshape(5,6)
total_resource=100
invest = [0, 10, 20, 30, 40, 50]

dp = ResourceAllocationDP(
    total_resource=total_resource,
    gain=gain,
    decision_set=invest,
    #allow_non_allocated_resource=False
)


result = dp.solve(allow_state_func=force_calculate_feasible_state)
print result
result = dp.solve()
print result