# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra, dumps_tikz_doc
from copy import deepcopy
import numpy as np
import random
import pickle

g=np.matrix([
    [0, 130, 150, np.inf, np.inf, np.inf],
    [0, 100, 160, 210, np.inf, 410],
    [0, 100, 120, np.inf, 210, np.inf],
    [np.inf, 110, 200, 250, 330, 370],
    [np.inf, np.inf, 210, 290, 320, np.inf]
])

company = [1,2,3,4,5]
invest = [0, 100, 200, 300, 400, 500]

# def f(k, sk):
#     if k == 6:
#         return 0
#     else:
#         return max(g[])

