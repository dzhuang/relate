# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra, dumps_tikz_doc
from latex_utils.utils.dynamic_programming import force_calculate_feasible_state, NonlinearTransportationProblem
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
dp_list = []

SAVED_QUESTION = "dp_nonlinear_dp1.bin"

M = 2
N = 3
PROJECT_LIST = [u"子公司%s" % str(idx) for idx in range(1, M + 1)]

def is_qualified_question(cost, total_resource, decision_set, supply, demand, mem_gain_list, saved_question=SAVED_QUESTION):

    qualified = False
    dp = NonlinearTransportationProblem(
        cost=cost, total_resource=total_resource, decision_set=decision_set,supply=supply, demand=demand)

    #result_force_calculate_feasible_state = dp.solve(allow_state_func=force_calculate_feasible_state)
    result = dp.solve()
    # 需要至少有两个最优决策
    if len(result.policy) < 2:
        return False

    question_exist = False
    for i, g in enumerate(mem_gain_list):
        if np.all(cost==g):
            print "----------------------question exists-------------------"
            question_exist = True
            return False
            break

    if not question_exist:
        suggestion = "dp_dict = { 'cost': %s" % repr(cost)
        suggestion = suggestion.replace("matrix", "np.matrix")
        suggestion = suggestion.replace("nan", "np.nan")
        suggestion = suggestion.replace("-inf", "np.nan")
        suggestion = suggestion.replace("inf", "np.nan")
        suggestion = suggestion.replace("float16", "np.float")

        r.clipboard_append(suggestion)
        r.clipboard_append(",\n")
        r.clipboard_append('    "total_resource":' + repr(total_resource) + ',\n')
        r.clipboard_append('    "decision_set":' + repr(decision_set) + ',\n')
        r.clipboard_append('    "supply":' + repr(supply) + ',\n')
        r.clipboard_append('    "demand":' + repr(demand) + ',\n')
        r.clipboard_append("}\n")
        r.clipboard_append("dp_list.append(dp_dict)")
        r.clipboard_append("\n")
        r.clipboard_append("\n")

        print suggestion

        #raise ValueError("Please add above problem")


    return True


def generate_problem(dp, mem_gain_list):
    n = 0
    n_element = M * N
    def get_rand_cost():
        a= list(range(2,10))
        b= list(range(11, 20))
        random.shuffle(a)
        random.shuffle(b)
        a = a[:6]
        b = b[:6]
        c = [(x, y) for x, y in zip(a, b)]
        splitted_list = [c[i:i + 3] for i in xrange(0, len(c), 3)]
        return splitted_list

    total_resource = dp.total_resource
    decision_set = dp.decision_set
    supply = dp.supply
    demand = dp.demand
    while n < 40:
        cost = get_rand_cost()
        if is_qualified_question(cost, total_resource, decision_set, supply, demand,  mem_gain_list):
            n += 1
            print n
            mem_gain_list.append(cost)


def generate():
    with open(SAVED_QUESTION, 'rb') as f:
        dp_list_loaded = pickle.load(f)
        mem_gain_list = [dp_dict["cost"] for dp_dict in dp_list_loaded]
        i = 0
        for dp_dict in dp_list_loaded:
            i += 1
            dp = NonlinearTransportationProblem(**dp_dict)
            generate_problem(dp, mem_gain_list)
            if i == 1:
                break


# generate()
# exit()



from collections import OrderedDict

from latex_utils.utils.dynamic_programming import force_calculate_feasible_state, NonlinearTransportationProblem

dp_dict = { 'cost': [[(3, 19), (2, 18), (7, 14)], [(8, 17), (6, 16), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 13), (6, 11), (9, 12)], [(4, 19), (2, 17), (8, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 15), (9, 19), (5, 12)], [(8, 18), (2, 16), (4, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 13), (3, 15), (7, 14)], [(8, 12), (6, 17), (4, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 14), (3, 12), (4, 16)], [(6, 19), (7, 11), (9, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 18), (6, 17), (8, 14)], [(5, 13), (9, 11), (7, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 17), (6, 11), (3, 13)], [(4, 16), (7, 18), (2, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 16), (7, 11), (4, 18)], [(5, 12), (3, 14), (9, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 15), (2, 16), (5, 14)], [(6, 19), (3, 11), (7, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 14), (4, 13), (3, 17)], [(6, 18), (5, 19), (7, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 18), (9, 17), (4, 16)], [(8, 11), (6, 15), (2, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 14), (6, 11), (2, 17)], [(7, 13), (8, 15), (9, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 15), (2, 11), (8, 16)], [(6, 13), (7, 12), (9, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 14), (2, 18), (8, 11)], [(5, 19), (4, 16), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 19), (9, 13), (5, 18)], [(2, 16), (4, 12), (3, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)


dp_dict = { 'cost': [[(5, 16), (3, 15), (9, 14)], [(4, 19), (7, 13), (6, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 14), (6, 13), (5, 12)], [(4, 16), (9, 15), (8, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 19), (6, 14), (3, 12)], [(7, 16), (5, 17), (4, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 16), (5, 17), (6, 15)], [(4, 12), (3, 18), (2, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 11), (4, 16), (5, 18)], [(7, 12), (2, 14), (6, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 18), (6, 11), (2, 16)], [(7, 17), (9, 12), (5, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 11), (9, 13), (7, 19)], [(4, 14), (2, 16), (8, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)


dp_dict = { 'cost': [[(6, 19), (3, 18), (5, 12)], [(4, 17), (7, 16), (8, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 14), (3, 18), (8, 12)], [(9, 17), (7, 16), (2, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 19), (3, 11), (4, 15)], [(8, 18), (7, 13), (2, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 17), (8, 11), (5, 13)], [(7, 18), (4, 19), (9, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 13), (6, 12), (8, 16)], [(9, 17), (5, 18), (2, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 15), (5, 18), (9, 14)], [(2, 16), (4, 13), (3, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 14), (4, 16), (8, 15)], [(3, 13), (2, 19), (9, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 12), (4, 16), (8, 13)], [(2, 11), (9, 19), (3, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 15), (8, 11), (7, 16)], [(5, 19), (2, 13), (6, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 12), (2, 17), (6, 16)], [(9, 15), (8, 19), (5, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 11), (7, 12), (6, 15)], [(2, 13), (9, 19), (3, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 17), (4, 11), (6, 13)], [(2, 12), (5, 16), (7, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 11), (8, 16), (2, 18)], [(9, 15), (6, 17), (3, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 18), (9, 17), (7, 16)], [(3, 11), (5, 19), (8, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 11), (6, 13), (8, 19)], [(5, 17), (7, 18), (3, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 15), (2, 17), (8, 14)], [(5, 19), (3, 12), (4, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 13), (6, 12), (5, 16)], [(4, 11), (2, 15), (7, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 13), (2, 19), (9, 16)], [(8, 11), (3, 12), (5, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 18), (2, 13), (4, 11)], [(3, 19), (8, 12), (6, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 18), (5, 12), (8, 13)], [(2, 15), (6, 14), (7, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 13), (4, 15), (5, 18)], [(8, 19), (3, 16), (7, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 16), (5, 12), (7, 17)], [(8, 18), (9, 15), (2, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)


dp_dict = { 'cost': [[(9, 11), (7, 17), (4, 18)], [(8, 12), (2, 14), (3, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 12), (2, 19), (6, 13)], [(4, 11), (8, 15), (9, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)


dp_dict = { 'cost': [[(7, 15), (5, 11), (4, 19)], [(2, 13), (3, 14), (8, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 17), (5, 11), (7, 14)], [(9, 15), (3, 16), (4, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 14), (5, 19), (3, 18)], [(9, 13), (4, 16), (6, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 18), (5, 14), (3, 15)], [(9, 16), (2, 17), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 16), (5, 14), (3, 17)], [(9, 19), (2, 12), (4, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 11), (4, 16), (7, 13)], [(3, 19), (2, 18), (6, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)


dp_dict = { 'cost': [[(9, 18), (8, 14), (6, 15)], [(4, 17), (5, 11), (2, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 17), (7, 19), (4, 18)], [(8, 11), (5, 16), (3, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
}
dp_list.append(dp_dict)


dp_dict = { 'cost': [[(9, 19), (5, 18), (6, 11)], [(7, 13), (3, 12), (4, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 12), (2, 13), (6, 18)], [(4, 15), (5, 17), (9, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 12), (7, 11), (3, 17)], [(8, 18), (4, 16), (2, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 14), (5, 12), (6, 11)], [(3, 13), (7, 17), (9, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 19), (8, 17), (6, 18)], [(3, 16), (4, 14), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 13), (9, 16), (8, 11)], [(6, 15), (7, 12), (3, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 12), (2, 14), (4, 11)], [(5, 18), (3, 16), (8, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 11), (5, 15), (8, 12)], [(6, 13), (9, 19), (3, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 17), (4, 14), (5, 15)], [(8, 19), (3, 13), (9, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 15), (9, 19), (3, 13)], [(2, 17), (6, 18), (7, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 16), (3, 19), (4, 18)], [(6, 14), (5, 12), (2, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 11), (9, 18), (4, 15)], [(5, 19), (3, 17), (7, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 18), (5, 14), (6, 11)], [(8, 15), (9, 16), (3, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 18), (3, 17), (5, 15)], [(8, 14), (2, 16), (7, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 14), (6, 16), (9, 12)], [(5, 18), (3, 13), (8, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 19), (2, 16), (8, 15)], [(9, 13), (4, 14), (5, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 17), (9, 16), (3, 11)], [(6, 15), (2, 13), (8, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 11), (3, 18), (2, 16)], [(6, 13), (8, 17), (4, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 12), (2, 18), (3, 13)], [(4, 17), (8, 16), (9, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 11],
    "demand":[7, 4, 5],
}
dp_list.append(dp_dict)



dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 11), (5, 14), (3, 16)], [(6, 18), (9, 17), (4, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 13), (6, 16), (2, 12)], [(5, 15), (3, 11), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 12), (5, 17), (3, 15)], [(2, 18), (6, 13), (7, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 17), (6, 12), (8, 14)], [(4, 19), (5, 15), (9, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 15), (5, 14), (9, 19)], [(3, 13), (8, 17), (7, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 15), (5, 13), (6, 12)], [(9, 14), (2, 16), (7, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 14), (2, 18), (8, 15)], [(4, 19), (6, 16), (3, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 13), (5, 16), (4, 11)], [(2, 17), (7, 19), (3, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 12), (3, 11), (6, 17)], [(7, 18), (2, 16), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 11), (2, 13), (9, 18)], [(7, 12), (8, 17), (4, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 13), (6, 17), (8, 11)], [(7, 18), (4, 14), (9, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 15), (8, 11), (6, 16)], [(5, 13), (4, 19), (2, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 19), (9, 13), (3, 14)], [(7, 15), (4, 18), (8, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)


dp_dict = { 'cost': [[(9, 12), (8, 18), (6, 16)], [(7, 15), (4, 13), (2, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 14), (3, 18), (9, 13)], [(8, 11), (4, 15), (2, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 19), (2, 13), (7, 18)], [(6, 11), (4, 12), (5, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 15), (6, 19), (9, 18)], [(7, 11), (4, 13), (3, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 11), (7, 16), (3, 15)], [(5, 18), (4, 13), (6, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 15), (9, 19), (6, 14)], [(2, 11), (3, 17), (7, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 10],
    "demand":[6, 5, 4],
}
dp_list.append(dp_dict)








import pickle
#import dill as pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(dp_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    dp_list_loaded = pickle.load(f)


#print dp.get_gain(3, 0)

valid_question_dict_list = []

for i, dp_dict in enumerate(dp_list_loaded):

    dp_dict["allow_non_allocated_resource"] = False
    dp = NonlinearTransportationProblem(**dp_dict)
    result = dp.solve()

    if len(result.policy) > 3:
        print repr(dp_dict)
        break
        continue
    # #print result
    # #result = dp.solve()
    #




    question_template = latex_jinja_env.get_template('dp_nonlinear_transportation_1.tex')
    #blank_template = latex_jinja_env.get_template('dp_nonlinear_transportation_1_blank.tex')
    answer_template = latex_jinja_env.get_template('/utils/dynamic_programming_template.tex')

    question_tex = question_template.render(
        show_question=True,
        show_answer_explanation=True,
        dp=dp
    )
    r.clipboard_append(question_tex)

    tex = answer_template.render(
        answer_table_iters=iter(range(1,50)),
        show_question=True,
        show_answer_explanation=True,
        show_answer=True,
        show_blank=True,
        show_blank_answer=True,
        dp=dp,
        dp_result_list=[result],
    )

    r.clipboard_append(tex)

print len(dp_list_loaded)