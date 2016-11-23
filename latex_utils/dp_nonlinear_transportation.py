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

M = 5
N = 6
PROJECT_LIST = [u"子公司%s" % str(idx) for idx in range(1, M + 1)]

def is_qualified_question(cost, total_resource, decision_set, project_list, mem_gain_list, saved_question=SAVED_QUESTION):

    qualified = False
    dp = NonlinearTransportationProblem(total_resource, cost, decision_set, project_list)

    result_force_calculate_feasible_state = dp.solve(allow_state_func=force_calculate_feasible_state)
    result = dp.solve()
    # 需要至少有两个最优决策
    if len(result.policy) < 2:
        return False

    # 需要至少有一个状态的最优决策多结果的
    x_dict = result_force_calculate_feasible_state.verbose_state_x_dict
    first_multiple_stage=None
    first_multiple_result_state=None
    first_multiple_result_x = None
    for stage, stage_dict in x_dict.items():
        if stage == 1:
            continue
        stage_state_dict = stage_dict["state"]
        #print stage, stage_state_dict
        for state, state_dict in stage_state_dict.items():
            if len(state_dict["state_opt_x"]) > 1:
                first_multiple_result_x = state_dict["state_opt_x"]
                first_multiple_stage = stage
                first_multiple_result_state = state
                break
        if first_multiple_result_x:
            break

    if not (first_multiple_stage and first_multiple_result_state and first_multiple_result_x):
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
        r.clipboard_append("}\n")
        r.clipboard_append("dp_dict['project_list'] = PROJECT_LIST\n")
        r.clipboard_append("dp_list.append(dp_dict)")
        r.clipboard_append("\n")
        r.clipboard_append("\n")

        print suggestion

        #raise ValueError("Please add above problem")


    return True


def generate_problem(dp, mem_gain_list):
    n = 0
    n_element = M * N
    def get_rand_gain():
        rand_list = np.random.randint(10, 45, n_element).tolist()
        splitted_list = [rand_list[i:i + 6] for i in xrange(0, len(rand_list), 6)]
        for i, l in enumerate(splitted_list):
            l[0] = 0
            splitted_list[i] = sorted(l)

        merged_list = []
        for l in splitted_list:
            merged_list.extend(l)
        merged_list = [ 10*s for s in merged_list]
        gain_array = np.array(merged_list, dtype=np.float16)
        rand_nan_idx = np.random.randint(0, 30, 9)
        gain_array[rand_nan_idx] = np.nan
        gain = np.matrix(gain_array).reshape(M, N)
        return gain

    total_resource = dp.total_resource
    decision_set = dp.decision_set
    project_list = dp.project_list
    while n < 100:
        gain = get_rand_gain()
        if is_qualified_question(gain, total_resource, decision_set, project_list, mem_gain_list):
            n += 1
            print n
            mem_gain_list.append(gain)



def generate():
    with open(SAVED_QUESTION, 'rb') as f:
        dp_list_loaded = pickle.load(f)
        mem_gain_list = [dp_dict["gain"] for dp_dict in dp_list_loaded]
        i = 0
        for dp_dict in dp_list_loaded:
            i += 1
            dp = NonlinearTransportationProblem(**dp_dict)
            generate_problem(dp, mem_gain_list)
            if i == 1:
                break



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

dp_dict = { 'cost': [[(7,3), (5,3), (6,2), (5,5)],
                     [(6,2), (4,6), (5,4), (9,2)]],
            "total_resource":6,
            "decision_set":[0, 1, 2, 3, 4, 5, 6],
            "supply": [6, 14],
            "demand": [7, 4, 4, 5]
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)


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

question_template = latex_jinja_env.get_template('dp_nonlinear_transportation_1.tex')
#blank_template = latex_jinja_env.get_template('dp_nonlinear_transportation_1_blank.tex')
answer_template = latex_jinja_env.get_template('/utils/dynamic_programming_template.tex')

question_tex = question_template.render(
    show_question=True,
    show_answer_explanation=True,
    dp=dp
)
r.clipboard_append(question_tex)

# tex = question_template.render(
#     answer_table_iters=iter(range(1,50)),
#     show_question=True,
#     show_answer=True,
#     show_blank=True,
#     show_blank_answer=True,
#     dp=dp,
#     dp_result_list=[result],
# )
#
# r.clipboard_append(tex)
