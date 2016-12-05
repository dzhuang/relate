# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra
from copy import deepcopy
import numpy as np


g_list = []

g = {"graph":
         np.matrix([
             0, 4, 7, 3, 0, 0, 0, 0,
             0, 0, 5, 0, 8, 6, 0, 0,
             0, 0, 0, 0, 0, 4, 10, 0,
             0, 0, 3, 0, 0, 0, 8, 0,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 3, 0, 2, 7,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,]).reshape(8,8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }

g_list.append(g)

g = {"graph":
         np.matrix([
             0, 4, 7, 3, 0, 0, 0, 0,
             0, 0, 5, 0, 8, 6, 0, 0,
             0, 0, 0, 0, 0, 4, 10, 0,
             0, 0, 3, 0, 0, 0, 8, 0,
             0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 3, 0, 2, 5,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 6, 4, 3, 0, 0, 0, 0,
             0, 0, 0, 0, 1, 0, 0, 0,
             0, 3, 0, 2, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 10, 0, 0,
             0, 0, 0, 6, 0, 4, 3, 5,
             0, 0, 0, 0, 10, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 0, 2,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 1, 2, 3, 0, 0, 0, 0,
             0, 0, 0, 2, 3, 0, 0, 0,
             0, 0, 0, 2, 0, 0, 5, 0,
             0, 0, 0, 0, 0, 2, 0, 0,
             0, 0, 0, 0, 0, 2, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 0, 1, 0, 1,
             0, 0, 0, 0, 1, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 0, 4, 2, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 12, 0, 0, 0,
             0, 3, 0, 0, 2, 0, 0, 7, 0,
             0, 0, 1, 0, 0, 0, 0, 6, 0,
             0, 0, 0, 0, 0, 6, 2, 3, 0,
             0, 0, 0, 0, 0, 0, 3, 0, 0,
             0, 0, 0, 0, 0, 5, 0, 0, 10,
             0, 0, 0, 0, 0, 0, 0, 0, 9,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(9, 9),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)


# ！！g = {"graph":
#          np.matrix([
#              0, 2, 2, 0, 0, 0, 0, 0, 0, 0,
#              0, 0, 3, 2, 0, 0, 0, 0, 5, 0,
#              0, 0, 0, 0, 2, 0, 0, 5, 0, 0,
#              0, 0, 0, 0, 1, 3, 0, 0, 0, 0,
#              0, 0, 0, 0, 0, 0, 3, 0, 0, 0,
#              0, 0, 0, 0, 0, 0, 3, 0, 2, 0,
#              0, 0, 0, 0, 0, 0, 0, 2, 0, 0,
#              0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
#              0, 0, 0, 0, 0, 0, 0, 4, 0, 2,
#              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#          ]).reshape(10, 10),
#      "node_label_dict": None,
#      "edge_label_style_dict":None
#     # 2条 看不清楚
#      }
# g_list.append(g)

g = {"graph":
         np.matrix([
             0, 2, 4, 6, 0, 0, 0, 0,
             0, 0, 1, 0, 5, 3, 0, 0,
             0, 0, 0, 1, 0, 3, 4, 0,
             0, 0, 0, 0, 0, 0, 3, 0,
             0, 0, 0, 0, 0, 0, 0, 8,
             0, 0, 0, 0, 2, 0, 3, 9,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 3, 5, 7, 0, 0, 0, 0,
             0, 0, 1, 0, 5, 3, 0, 0,
             0, 0, 0, 1, 0, 2, 5, 0,
             0, 0, 0, 0, 0, 0, 3, 0,
             0, 0, 0, 0, 0, 0, 0, 8,
             0, 0, 0, 0, 2, 0, 3, 8,
             0, 0, 0, 0, 0, 0, 0, 7,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 4, 3, 5, 0, 0, 0, 0,
             0, 0, 0, 0, 3, 0, 4, 0,
             0, 2, 0, 2, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 3, 0,
             0, 0, 0, 0, 0, 0, 0, 7,
             0, 0, 0, 0, 1, 0, 0, 3,
             0, 0, 0, 0, 0, 2, 0, 8,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 4, 3, 6, 0, 0, 0, 0,
             0, 0, 0, 0, 3, 0, 4, 0,
             0, 2, 0, 2, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 3, 0,
             0, 0, 0, 0, 0, 0, 0, 7,
             0, 0, 0, 0, 1, 0, 0, 4,
             0, 0, 0, 0, 0, 2, 0, 8,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 3, 4, 1, 0, 0, 0, 0, 0,
             0, 0, 2, 0, 4, 0, 0, 0, 0,
             0, 0, 0, 0, 1, 4, 5, 0, 0,
             0, 0, 2, 0, 0, 0, 3, 0, 0,
             0, 0, 0, 0, 0, 2, 0, 0, 5,
             0, 0, 0, 0, 0, 0, 0, 4, 3,
             0, 0, 0, 0, 0, 0, 0, 3, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 4,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(9, 9),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 1, 4, 3, 0, 0, 0, 0,
             0, 0, 3, 0, 8, 0, 0, 0,
             0, 0, 0, 0, 5, 3, 6, 0,
             0, 0, 4, 0, 0, 0, 5, 0,
             0, 0, 0, 0, 0, 4, 0, 3,
             0, 0, 0, 0, 0, 0, 0, 4,
             0, 0, 0, 0, 0, 2, 0, 5,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 2, 5, 4, 0, 0, 0, 0,
             0, 0, 3, 0, 8, 0, 0, 0,
             0, 0, 0, 0, 5, 3, 6, 0,
             0, 0, 4, 0, 0, 0, 5, 0,
             0, 0, 0, 0, 0, 4, 0, 4,
             0, 0, 0, 0, 0, 0, 0, 5,
             0, 0, 0, 0, 0, 2, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 4, 6, 0, 0, 0, 0, 0,
             0, 0, 0, 1, 4, 0, 0, 0,
             0, 0, 0, 4, 7, 0, 0, 0,
             0, 0, 0, 0, 0, 9, 7, 0,
             0, 0, 0, 0, 0, 6, 6, 0,
             0, 0, 0, 0, 0, 0, 5, 2,
             0, 0, 0, 0, 0, 0, 0, 5,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": {(2,4):"pos=0.25",(1,3):"pos=0.25",(3,5):"pos=0.25",(4,6):"pos=0.25",}
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 1, 4, 6, 0, 0, 0, 0,
             0, 0, 2, 0, 10, 7, 0, 0,
             0, 0, 0, 1, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 3, 8, 0,
             0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 2, 0, 1, 9,
             0, 0, 0, 0, 0, 0, 0, 4,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 1, 4, 6, 0, 0, 0, 0,
             0, 0, 2, 0, 8, 7, 0, 0,
             0, 0, 0, 1, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 3, 8, 0,
             0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 2, 0, 1, 9,
             0, 0, 0, 0, 0, 0, 0, 5,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 5, 3, 2, 0, 0, 0, 0,
             0, 0, 0, 0, 2, 7, 0, 0,
             0, 1, 0, 0, 2, 0, 0, 0,
             0, 0, 2, 0, 6, 0, 0, 0,
             0, 0, 0, 0, 0, 6, 3, 0,
             0, 0, 0, 0, 0, 0, 1, 1,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": {(0,3):"bend right"}
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 5, 3, 2, 0, 0, 0, 0,
             0, 0, 0, 0, 2, 8, 0, 0,
             0, 1, 0, 0, 4, 0, 0, 0,
             0, 0, 2, 0, 5, 0, 0, 0,
             0, 0, 0, 0, 0, 6, 3, 0,
             0, 0, 0, 0, 0, 0, 1, 1,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": {(0,3):"bend right"}
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 1, 2, 0, 0, 0, 0, 0,
             0, 0, 3, 4, 0, 0, 0, 0,
             0, 0, 0, 5, 2, 0, 0, 0,
             0, 0, 0, 0, 1, 3, 2, 0,
             0, 0, 0, 0, 0, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 2, 0, 4,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 2, 0, 10, 0, 7, 0, 0,
             0, 0, 7, 8, 0, 0, 0, 0,
             0, 0, 0, 0, 3, 0, 0, 6,
             0, 0, 2, 0, 5, 5, 2, 0,
             0, 0, 0, 0, 0, 0, 6, 3,
             0, 0, 0, 0, 0, 0, 4, 0,
             0, 0, 0, 0, 0, 0, 0, 9,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 2, 0, 10, 0, 7, 0, 0,
             0, 0, 7, 8, 0, 0, 0, 0,
             0, 0, 0, 0, 6, 0, 0, 9,
             0, 0, 2, 0, 4, 5, 2, 0,
             0, 0, 0, 0, 0, 0, 6, 3,
             0, 0, 0, 0, 0, 0, 4, 0,
             0, 0, 0, 0, 0, 0, 0, 9,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 1, 2, 0, 0, 0, 0, 0,
             0, 0, 0, 5, 2, 0, 0, 0,
             0, 1, 0, 2, 1, 4, 0, 0,
             0, 0, 0, 0, 3, 6, 8, 0,
             0, 0, 0, 0, 0, 3, 7, 0,
             0, 0, 0, 0, 0, 0, 5, 2,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":{(4, 5): 'pos=0.25', (2, 5): 'pos=0.15', (3, 4): 'pos=0.25', (3, 6): 'bend right, pos=0.75', (1, 4): 'bend left, pos=0.25'},
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 2, 3, 0, 0, 0, 0, 0,
             0, 0, 0, 5, 3, 0, 0, 0,
             0, 1, 0, 2, 2, 7, 0, 0,
             0, 0, 0, 0, 3, 6, 8, 0,
             0, 0, 0, 0, 0, 3, 6, 0,
             0, 0, 0, 0, 0, 0, 5, 3,
             0, 0, 0, 0, 0, 0, 0, 7,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict":{(4, 5): 'pos=0.25', (2, 5): 'pos=0.15', (3, 4): 'pos=0.25', (3, 6): 'bend right, pos=0.75', (1, 4): 'bend left, pos=0.25'},
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 3, 7, 1, 0, 0, 0, 0,
             0, 0, 5, 0, 8, 0, 0, 0,
             0, 0, 0, 0, 4, 6, 7, 0,
             0, 0, 4, 0, 0, 0, 8, 0,
             0, 0, 0, 0, 0, 4, 0, 8,
             0, 0, 0, 0, 0, 0, 0, 5,
             0, 0, 0, 0, 0, 3, 0, 7,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 3, 5, 2, 0, 0, 0, 0,
             0, 0, 1, 0, 7, 8, 0, 0,
             0, 0, 0, 0, 0, 4, 3, 0,
             0, 0, 2, 0, 0, 0, 6, 0,
             0, 0, 0, 0, 0, 1, 0, 7,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 3, 0, 8,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 3, 5, 2, 0, 0, 0, 0,
             0, 0, 2, 0, 7, 6, 0, 0,
             0, 0, 0, 0, 0, 5, 3, 0,
             0, 0, 2, 0, 0, 0, 6, 0,
             0, 0, 0, 0, 0, 1, 0, 7,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 3, 0, 8,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 5, 2, 4, 0, 0, 0, 0, 0,
             0, 0, 1, 0, 3, 0, 0, 0, 0,
             0, 0, 0, 1, 4, 5, 6, 0, 0,
             0, 0, 0, 0, 0, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 3, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 2, 1, 5,
             0, 0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(9, 9),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 5, 2, 4, 0, 0, 0, 0, 0,
             0, 0, 1, 0, 3, 0, 0, 0, 0,
             0, 0, 0, 1, 4, 5, 6, 0, 0,
             0, 0, 0, 0, 0, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 3, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 2, 1, 5,
             0, 0, 0, 0, 0, 0, 0, 0, 4,
             0, 0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(9, 9),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 5, 6, 4, 0, 0, 0, 0, 0,
             0, 0, 1, 0, 3, 0, 0, 0, 0,
             0, 0, 0, 1, 4, 5, 3, 0, 0,
             0, 0, 0, 0, 0, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 4, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 2, 1, 5,
             0, 0, 0, 0, 0, 0, 0, 0, 4,
             0, 0, 0, 0, 0, 0, 0, 0, 3,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(9, 9),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 2, 0, 1, 0, 3, 0, 0,
             0, 0, 6, 0, 5, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 10, 0, 0, 0, 0, 2, 0,
             0, 0, 9, 0, 0, 0, 0, 4,
             0, 0, 0, 5, 0, 0, 4, 0,
             0, 0, 0, 0, 3, 0, 0, 7,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 2, 0, 4, 0, 3, 0, 0,
             0, 0, 6, 0, 5, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 10, 0, 0, 0, 0, 2, 0,
             0, 0, 9, 0, 0, 0, 0, 6,
             0, 0, 0, 5, 0, 0, 4, 0,
             0, 0, 0, 0, 3, 0, 0, 7,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 3, 5, 2, 0, 0, 0, 0,
             0, 0, 1, 0, 6, 8, 0, 0,
             0, 0, 0, 0, 3, 0, 0, 0,
             0, 0, 2, 0, 0, 0, 12, 0,
             0, 0, 0, 0, 0, 6, 3, 7,
             0, 0, 0, 0, 0, 0, 0, 5,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)



g = {"graph":
         np.matrix([
             0, 3, 5, 3, 0, 0, 0, 0,
             0, 0, 1, 0, 5, 8, 0, 0,
             0, 0, 0, 0, 4, 0, 0, 0,
             0, 0, 2, 0, 0, 0, 6, 0,
             0, 0, 0, 0, 0, 6, 3, 7,
             0, 0, 0, 0, 0, 0, 0, 5,
             0, 0, 0, 0, 0, 0, 0, 6,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 2, 4, 0, 0, 0, 0, 0,
             0, 0, 3, 5, 2, 0, 0, 0,
             0, 0, 0, 0, 1, 0, 0, 0,
             0, 0, 0, 0, 0, 2, 4, 0,
             0, 0, 0, 1, 0, 0, 4, 0,
             0, 0, 0, 0, 0, 0, 1, 2,
             0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 2, 4, 0, 0, 0, 0, 0,
             0, 0, 3, 4, 2, 0, 0, 0,
             0, 0, 0, 0, 1, 0, 0, 0,
             0, 0, 0, 0, 0, 2, 2, 0,
             0, 0, 0, 2, 0, 0, 4, 0,
             0, 0, 0, 0, 0, 0, 1, 3,
             0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 6, 4, 5, 0, 0, 0, 0,
             0, 0, 3, 0, 9, 9, 0, 0,
             0, 0, 0, 5, 6, 7, 3, 0,
             0, 0, 0, 0, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 12,
             0, 0, 0, 0, 8, 0, 0, 10,
             0, 0, 0, 0, 0, 4, 0, 15,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": {(2,4):"pos=0.25",(3,5):"pos=0.25", (1,5):"pos=0.25",(2,6):"pos=0.75",}
    # 3条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 6, 4, 5, 0, 0, 0, 0,
             0, 0, 3, 0, 9, 5, 0, 0,
             0, 0, 0, 5, 6, 7, 3, 0,
             0, 0, 0, 0, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 12,
             0, 0, 0, 0, 8, 0, 0, 10,
             0, 0, 0, 0, 0, 5, 0, 15,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": {(2,4):"pos=0.25",(3,5):"pos=0.25", (1,5):"pos=0.25",(2,6):"pos=0.75",}
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 3, 7, 2, 0, 0, 0, 0,
             0, 0, 4, 0, 8, 0, 0, 0,
             0, 0, 0, 0, 4, 4, 7, 0,
             0, 0, 4, 0, 0, 9, 0, 0,
             0, 0, 0, 0, 0, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 8, 3,
             0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 2条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 3, 7, 2, 0, 0, 0, 0,
             0, 0, 4, 0, 8, 0, 0, 0,
             0, 0, 0, 0, 4, 4, 6, 0,
             0, 0, 4, 0, 0, 9, 0, 0,
             0, 0, 0, 0, 0, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 8, 3,
             0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 3, 7, 2, 0, 0, 0, 0,
             0, 0, 4, 0, 8, 0, 0, 0,
             0, 0, 0, 0, 4, 4, 6, 0,
             0, 0, 4, 0, 0, 9, 0, 0,
             0, 0, 0, 0, 0, 0, 2, 0,
             0, 0, 0, 0, 0, 0, 8, 3,
             0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(8, 8),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)

g = {"graph":
         np.matrix([
             0, 1, 2, 0, 4, 0, 0, 0, 0,
             0, 0, 0, 5, 2, 0, 0, 0, 0,
             0, 0, 0, 0, 3, 6, 0, 0, 0,
             0, 0, 0, 0, 3, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 3, 4, 0, 0,
             0, 0, 0, 0, 0, 0, 7, 4, 0,
             0, 0, 0, 0, 0, 0, 0, 3, 4,
             0, 0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(9, 9),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)


g = {"graph":
         np.matrix([
             0, 1, 2, 0, 4, 0, 0, 0, 0,
             0, 0, 0, 5, 2, 0, 0, 0, 0,
             0, 0, 0, 0, 3, 5, 0, 0, 0,
             0, 0, 0, 0, 3, 0, 6, 0, 0,
             0, 0, 0, 0, 0, 4, 4, 0, 0,
             0, 0, 0, 0, 0, 0, 7, 4, 0,
             0, 0, 0, 0, 0, 0, 0, 4, 6,
             0, 0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
         ]).reshape(9, 9),
     "node_label_dict": None,
     "edge_label_style_dict": None
    # 3条
     }
g_list.append(g)

from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()


import pickle
with open('graph_dijk_sp.bin', 'wb') as f:
    pickle.dump(g_list, f)

with open('graph_dijk_sp.bin', 'rb') as f:
    g_list_loaded = pickle.load(f)


n = 0
for g_dict in g_list_loaded:
    n += 1
    # r.clipboard_clear()
    g = network(**g_dict)
    #print g.graph.edge
    #g.as_capacity_graph()
    #continue

    dijkstra_is_allowed = True
    dijkstra_result = None

    try:
        dijkstra_result = g.get_iterated_solution(method="dijkstra")
    except NetworkNegativeWeightUsingDijkstra:
        dijkstra_is_allowed = False

    shortest_path_length=g.final_dist[g.n_node-1]

    template = latex_jinja_env.get_template('/utils/graph_shortest_path.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        answer_table_iters=iter(range(1, 20)),
        #show_question = True,
        show_answer = True,
        g=g,
        source = g.node_label_dict[0],
        target = g.node_label_dict[len(g.graph) - 1],
        shortest_path_length=shortest_path_length,
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