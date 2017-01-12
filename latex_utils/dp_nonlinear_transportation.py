# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env
from latex_utils.utils.graph import network, NetworkNegativeWeightUsingDijkstra, dumps_tikz_doc
from latex_utils.utils.dynamic_programming import force_calculate_feasible_state, NonlinearTransportationProblem
from copy import deepcopy
import numpy as np
import random
import pickle
import random
import sys
import operator

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

SAVED_QUESTION = "dp_nonlinear_transportation_1.bin"

M = 2
N = 3

def is_qualified_question(cost, total_resource, decision_set, supply, demand, opt_type, mem_gain_list, saved_question=SAVED_QUESTION):

    qualified = False
    dp = NonlinearTransportationProblem(
        cost=cost, total_resource=total_resource, decision_set=decision_set,supply=supply, demand=demand, opt_type=opt_type, allow_non_allocated_resource=False)

    #result_force_calculate_feasible_state = dp.solve(allow_state_func=force_calculate_feasible_state)
    result = dp.solve()
    # 需要至少有两个最优决策
    if len(result.policy) not in range(2,4):
        return False

    question_exist = False
    for i, g in enumerate(mem_gain_list):
        if np.all(cost==g):
            print("----------------------question exists-------------------")
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
        r.clipboard_append('    "opt_type": "min"' + ',\n')
        r.clipboard_append('    "allow_non_allocated_resource": False' + ',\n')
        r.clipboard_append("}\n")
        r.clipboard_append("dp_list.append(dp_dict)")
        r.clipboard_append("\n")
        r.clipboard_append("\n")

        print(suggestion)

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
    opt_type = "min"
    while n < 100:
        cost = get_rand_cost()
        if is_qualified_question(cost, total_resource, decision_set, supply, demand, opt_type, mem_gain_list):
            n += 1
            print(n)
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

dp_dict = { 'cost': [[(5, 13), (8, 15), (2, 14)], [(7, 16), (3, 19), (4, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 19), (4, 13), (5, 14)], [(6, 16), (2, 11), (9, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 15), (9, 19), (2, 14)], [(7, 18), (4, 13), (6, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 15), (7, 11), (8, 16)], [(6, 17), (3, 13), (4, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 18), (3, 17), (2, 13)], [(7, 14), (4, 16), (6, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 14), (3, 18), (5, 11)], [(2, 19), (6, 13), (9, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 19), (7, 17), (8, 15)], [(5, 12), (3, 11), (2, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 19), (5, 18), (8, 14)], [(9, 15), (3, 12), (4, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 13), (4, 15), (3, 16)], [(6, 12), (9, 11), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 18), (4, 17), (5, 15)], [(8, 14), (2, 16), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 18), (7, 13), (5, 15)], [(2, 19), (6, 12), (8, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 15), (2, 16), (5, 12)], [(7, 17), (6, 19), (9, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 14), (4, 16), (7, 11)], [(9, 19), (3, 17), (2, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 16), (6, 18), (8, 11)], [(9, 12), (5, 13), (4, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 14), (3, 16), (4, 12)], [(6, 11), (5, 18), (8, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 17), (2, 18), (7, 11)], [(6, 14), (9, 19), (3, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 16), (6, 18), (3, 17)], [(2, 14), (5, 13), (8, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 18), (5, 19), (8, 12)], [(6, 14), (9, 13), (2, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 14), (3, 12), (6, 11)], [(5, 19), (9, 16), (8, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 12), (4, 15), (3, 14)], [(9, 16), (6, 18), (5, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 15), (5, 17), (7, 11)], [(8, 14), (6, 18), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 16), (8, 12), (4, 13)], [(9, 19), (6, 17), (3, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 11), (3, 15), (7, 14)], [(4, 13), (2, 12), (6, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 19), (8, 11), (3, 14)], [(6, 17), (7, 12), (4, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 19), (5, 15), (3, 12)], [(9, 17), (2, 11), (4, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 16), (3, 14), (9, 11)], [(8, 13), (7, 12), (6, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 13), (2, 19), (7, 15)], [(8, 14), (6, 17), (3, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 18), (3, 14), (8, 13)], [(5, 15), (4, 12), (7, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 14), (6, 16), (2, 15)], [(5, 13), (4, 12), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 15), (6, 11), (3, 13)], [(8, 14), (7, 12), (5, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 12), (2, 16), (5, 19)], [(8, 15), (4, 18), (3, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 18), (7, 12), (3, 14)], [(2, 16), (9, 11), (4, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 19), (3, 17), (4, 12)], [(6, 18), (7, 11), (2, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 15), (9, 12), (3, 14)], [(6, 11), (5, 13), (2, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 13), (9, 18), (4, 16)], [(7, 17), (2, 12), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 13), (3, 17), (9, 11)], [(5, 14), (2, 15), (8, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 16), (9, 14), (5, 15)], [(3, 12), (7, 11), (2, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 13), (5, 16), (4, 11)], [(8, 12), (9, 18), (3, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 16), (3, 19), (8, 15)], [(2, 12), (6, 14), (7, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 19), (3, 18), (8, 15)], [(9, 13), (6, 11), (5, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 19), (5, 17), (2, 12)], [(8, 14), (7, 13), (3, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 11), (4, 13), (2, 15)], [(3, 17), (5, 18), (7, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 18), (5, 14), (6, 12)], [(9, 19), (7, 17), (4, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 13), (8, 11), (5, 16)], [(3, 17), (6, 15), (9, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 19), (8, 14), (3, 18)], [(7, 13), (6, 11), (2, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 15), (3, 13), (6, 11)], [(7, 19), (4, 16), (5, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 16), (4, 15), (6, 19)], [(2, 14), (9, 12), (7, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 15), (8, 12), (2, 18)], [(5, 16), (6, 14), (4, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 17), (4, 19), (6, 14)], [(9, 15), (2, 16), (8, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 18), (7, 19), (4, 13)], [(8, 11), (5, 16), (2, 12)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 13), (9, 11), (6, 12)], [(5, 14), (8, 16), (4, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 13), (7, 17), (5, 16)], [(3, 12), (2, 14), (8, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 17), (6, 15), (9, 11)], [(3, 16), (5, 12), (7, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 17), (5, 19), (9, 11)], [(7, 16), (3, 15), (4, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 16), (5, 15), (7, 18)], [(4, 11), (3, 13), (8, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 16), (8, 14), (7, 17)], [(2, 13), (4, 15), (6, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 18), (3, 19), (4, 11)], [(2, 14), (7, 12), (5, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 11), (4, 17), (7, 15)], [(3, 12), (6, 13), (5, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 16), (4, 13), (2, 14)], [(8, 15), (7, 11), (6, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 13), (2, 11), (7, 16)], [(6, 15), (5, 12), (8, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 16), (7, 17), (4, 12)], [(9, 19), (3, 18), (8, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 17), (5, 19), (6, 15)], [(3, 12), (7, 14), (2, 11)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 19), (3, 16), (6, 17)], [(4, 11), (8, 13), (2, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 14), (8, 13), (9, 12)], [(4, 16), (3, 11), (5, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 17), (9, 14), (5, 11)], [(3, 12), (7, 16), (6, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 19), (3, 18), (9, 13)], [(2, 17), (6, 15), (5, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 18), (4, 13), (7, 15)], [(5, 14), (3, 11), (9, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 19), (9, 12), (3, 16)], [(6, 13), (8, 11), (7, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 15), (4, 17), (3, 13)], [(9, 19), (5, 18), (8, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 18), (7, 17), (6, 15)], [(4, 16), (9, 11), (2, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 12), (2, 18), (6, 11)], [(3, 15), (8, 14), (4, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 19), (8, 16), (7, 11)], [(5, 18), (2, 14), (6, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 15), (8, 13), (4, 12)], [(2, 19), (9, 18), (5, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 13), (6, 19), (9, 15)], [(3, 11), (5, 16), (8, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 13), (8, 11), (7, 15)], [(9, 18), (4, 17), (5, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 18), (8, 13), (6, 15)], [(5, 16), (2, 12), (3, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 15), (2, 19), (8, 16)], [(4, 12), (3, 14), (5, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 19), (4, 14), (6, 15)], [(2, 17), (3, 11), (9, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 14), (8, 13), (2, 11)], [(5, 17), (4, 18), (6, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(9, 16), (8, 19), (4, 14)], [(7, 13), (6, 15), (3, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 17), (4, 14), (5, 11)], [(6, 18), (8, 12), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 14), (3, 15), (4, 13)], [(6, 18), (2, 17), (9, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(8, 18), (6, 15), (9, 13)], [(3, 16), (4, 11), (2, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 17), (4, 15), (7, 14)], [(2, 16), (3, 12), (8, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 17), (3, 19), (7, 15)], [(8, 11), (6, 12), (9, 14)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 15), (3, 16), (2, 11)], [(9, 17), (5, 19), (6, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 11), (2, 18), (6, 14)], [(7, 13), (9, 19), (8, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 18), (3, 13), (5, 11)], [(7, 14), (6, 19), (9, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 17), (8, 12), (2, 16)], [(7, 14), (5, 13), (9, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 15), (4, 19), (3, 14)], [(8, 12), (2, 13), (9, 17)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 12), (2, 14), (8, 11)], [(5, 16), (3, 17), (7, 15)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 13), (4, 15), (7, 14)], [(9, 11), (3, 12), (2, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 16), (3, 14), (9, 11)], [(4, 13), (7, 12), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 19), (6, 17), (2, 11)], [(8, 13), (7, 14), (5, 18)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(5, 14), (3, 15), (7, 13)], [(9, 17), (2, 16), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(4, 18), (6, 17), (2, 13)], [(3, 11), (9, 12), (8, 16)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(3, 14), (7, 12), (4, 11)], [(9, 17), (6, 15), (8, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(7, 16), (6, 19), (5, 12)], [(8, 18), (3, 17), (9, 13)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(6, 15), (2, 18), (4, 16)], [(7, 12), (5, 11), (3, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)

dp_dict = { 'cost': [[(2, 18), (6, 13), (9, 11)], [(4, 16), (5, 15), (8, 19)]],
    "total_resource":5,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "supply":[5, 12],
    "demand":[7, 6, 4],
    "opt_type": "min",
    "allow_non_allocated_resource": False,
}
dp_list.append(dp_dict)




import pickle
import dill as pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(dp_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    dp_list_loaded = pickle.load(f)



for i, dp_dict in enumerate(dp_list_loaded):

    dp = NonlinearTransportationProblem(**dp_dict)
    result = dp.solve()

    if len(result.policy) > 3:
        print(repr(dp_dict))
        break
        continue

    decision_result = []
    for p in result.policy:
        policy, = p
        a_1 = [s for s in policy["opt_x"].values()]
        a_2 = list(map(operator.sub, dp.demand, a_1))
        d = [a_1, a_2]
        decision_result.append(d)

    print(decision_result)

    question_template = latex_jinja_env.get_template('dp_nonlinear_transportation_1.tex')
    blank_template = latex_jinja_env.get_template('dp_nonlinear_transportation_1_blank.tex')
    answer_template = latex_jinja_env.get_template('/utils/dynamic_programming_template.tex')
    human_readable_result_template = latex_jinja_env.get_template('dp_nonlinear_transportation_1_final_result.tex')

    blank_tex = blank_template.render(
        show_blank=True,
        show_blank_answer=True,
        dp=dp,
        dp_result_list=[result],
        result=result,
        blank1_desc=u"最低运费为",
        blank2_desc=u"可能的最优策略的个数为",
        blank3_desc=u"以销地$B_1$,$B_2$,$B_3$为次序划分阶段，且以产地$A_1$至各销地的运输量为各阶段的决策时，一个最优策略为",
    )
    print(blank_tex)

    question_tex = question_template.render(
        show_question=True,
        show_answer_explanation=True,
        dp=dp
    )
    r.clipboard_append(question_tex)

    human_readable_result = human_readable_result_template.render(
        decision_result=decision_result,
        result=result,
        dp=dp
    )

    answer_table_iters = iter(range(1, 50))
    tex = answer_template.render(
        answer_table_iters=answer_table_iters,
        show_question=True,
        show_answer_explanation=True,
        show_answer=True,
        show_blank=True,
        show_blank_answer=True,
        dp=dp,
        dp_result_list=[result],
        human_readable_result=human_readable_result
    )

    r.clipboard_append(tex)

print(len(dp_list_loaded))