# -*- coding: utf-8 -*-

from latex_utils.utils.dynamic_programming import ResourceAllocationDP, force_calculate_feasible_state
from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
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

from io import BytesIO
from base64 import b64encode

from collections import OrderedDict


SAVED_QUESTION = "resource_allocation_dp1.bin"

M = 5
N = 6
PROJECT_LIST = [u"子公司%s" % str(idx) for idx in range(1, M + 1)]

n_project = 5


def is_qualified_question(gain, total_resource, decision_set, project_list, mem_gain_list, saved_question=SAVED_QUESTION):

    qualified = False
    dp = ResourceAllocationDP(total_resource, gain, decision_set, project_list)

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
        if np.all(gain==g):
            print "----------------------question exists-------------------"
            question_exist = True
            return False
            break

    if not question_exist:
        suggestion = "dp_dict = { 'gain': %s" % repr(gain)
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
            dp = ResourceAllocationDP(**dp_dict)
            generate_problem(dp, mem_gain_list)
            if i == 1:
                break


# generate()
# exit()

from latex_utils.utils.dynamic_programming import ResourceAllocationDP, force_calculate_feasible_state

dp_list = []

# dp_dict = {
#     "total_resource": 800,
#     "gain": np.matrix([
#         [0, 130, 150, np.nan, np.nan, np.nan],
#         [0, 100, 160, 210, np.nan, 410],
#         [0, 100, 120, np.nan, 210, np.nan],
#         [np.nan, 110, 200, 250, 330, 370],
#         [np.nan, np.nan, 210, 290, 320, np.nan]
#     ]),
#     "decision_set": [0, 100, 200, 300, 400, 500],
#     "project_list": [u"子公司%s" % str(idx) for idx in range(1, n_project + 1)]
# }

dp_dict = { 'gain': np.matrix([[   0.,  100.,  np.nan,  160.,  180.,  360.],
        [   0.,  150.,  310.,  310.,  330.,  430.],
        [   0.,  120.,  280.,  360.,  380.,  410.],
        [   0.,  np.nan,  np.nan,  np.nan,  np.nan,  np.nan],
        [   0.,  150.,  170.,  220.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  190.,  np.nan,  290.,  np.nan],
        [   0.,  np.nan,  230.,  440.,  440.,  440.],
        [   0.,  100.,  100.,  210.,  np.nan,  430.],
        [   0.,  210.,  230.,  np.nan,  np.nan,  410.],
        [   0.,  120.,  220.,  220.,  330.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  130.,  270.,  280.,  430.,  np.nan],
        [   0.,  160.,  200.,  320.,  np.nan,  np.nan],
        [   0.,  150.,  np.nan,  190.,  np.nan,  np.nan],
        [   0.,  110.,  120.,  180.,  190.,  300.],
        [ np.nan,  150.,  180.,  310.,  340.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  170.,  np.nan,  350.,  380.],
        [ np.nan,  150.,  150.,  240.,  np.nan,  410.],
        [   0.,  120.,  170.,  np.nan,  300.,  430.],
        [   0.,  110.,  200.,  240.,  370.,  410.],
        [   0.,  np.nan,  280.,  310.,  340.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  np.nan,  330.,  420.,  430.,  430.],
        [ np.nan,  np.nan,  170.,  170.,  390.,  np.nan],
        [ np.nan,  120.,  140.,  240.,  np.nan,  390.],
        [   0.,  130.,  220.,  260.,  300.,  np.nan],
        [   0.,  180.,  210.,  260.,  np.nan,  410.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  110.,  np.nan,  150.,  np.nan,  430.],
        [   0.,  150.,  160.,  np.nan,  340.,  np.nan],
        [   0.,  np.nan,  160.,  260.,  270.,  280.],
        [   0.,  160.,  np.nan,  210.,  np.nan,  np.nan],
        [   0.,  110.,  160.,  270.,  300.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  120.,  220.,  250.,  270.,  310.],
        [   0.,  190.,  210.,  210.,  np.nan,  430.],
        [ np.nan,  np.nan,  np.nan,  290.,  340.,  np.nan],
        [   0.,  130.,  130.,  170.,  170.,  np.nan],
        [   0.,  np.nan,  110.,  270.,  350.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  180.,  240.,  np.nan,  380.],
        [ np.nan,  110.,  140.,  240.,  260.,  280.],
        [   0.,  np.nan,  140.,  160.,  160.,  np.nan],
        [ np.nan,  220.,  220.,  230.,  350.,  400.],
        [   0.,  140.,  150.,  150.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  100.,  np.nan,  160.,  np.nan,  210.],
        [ np.nan,  200.,  260.,  np.nan,  320.,  360.],
        [   0.,  np.nan,  200.,  300.,  np.nan,  440.],
        [   0.,  120.,  220.,  250.,  260.,  280.],
        [   0.,  np.nan,  290.,  300.,  300.,  360.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  100.,  140.,  np.nan,  300.,  np.nan],
        [ np.nan,  160.,  np.nan,  320.,  370.,  420.],
        [ np.nan,  np.nan,  160.,  210.,  310.,  340.],
        [   0.,  100.,  120.,  140.,  260.,  300.],
        [   0.,  np.nan,  200.,  280.,  400.,  400.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  np.nan,  140.,  np.nan,  290.,  300.],
        [   0.,  220.,  np.nan,  350.,  np.nan,  np.nan],
        [   0.,  310.,  310.,  np.nan,  np.nan,  400.],
        [   0.,  120.,  140.,  180.,  190.,  300.],
        [ np.nan,  210.,  310.,  360.,  370.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  100.,  210.,  np.nan,  310.,  np.nan],
        [   0.,  100.,  220.,  250.,  np.nan,  np.nan],
        [   0.,  100.,  np.nan,  310.,  np.nan,  360.],
        [   0.,  np.nan,  260.,  410.,  420.,  420.],
        [   0.,  100.,  150.,  210.,  270.,  370.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  130.,  140.,  230.,  300.,  np.nan],
        [ np.nan,  150.,  210.,  240.,  300.,  410.],
        [   0.,  np.nan,  390.,  410.,  440.,  440.],
        [   0.,  np.nan,  230.,  290.,  np.nan,  np.nan],
        [   0.,  130.,  170.,  190.,  np.nan,  400.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  260.,  350.,  400.,  np.nan],
        [   0.,  100.,  np.nan,  np.nan,  320.,  np.nan],
        [   0.,  100.,  np.nan,  np.nan,  250.,  320.],
        [   0.,  np.nan,  120.,  250.,  440.,  440.],
        [ np.nan,  120.,  np.nan,  210.,  220.,  370.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  190.,  230.,  280.,  290.,  440.],
        [ np.nan,  160.,  np.nan,  310.,  380.,  440.],
        [ np.nan,  np.nan,  240.,  310.,  320.,  380.],
        [   0.,  210.,  290.,  290.,  340.,  410.],
        [ np.nan,  120.,  160.,  np.nan,  np.nan,  310.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  150.,  200.,  280.,  290.,  np.nan],
        [   0.,  130.,  250.,  300.,  330.,  420.],
        [   0.,  150.,  350.,  400.,  400.,  410.],
        [ np.nan,  150.,  170.,  250.,  np.nan,  330.],
        [ np.nan,  190.,  220.,  np.nan,  350.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)


dp_dict = { 'gain': np.matrix([[   0.,  130.,  220.,  270.,  np.nan,  420.],
        [ np.nan,  110.,  120.,  np.nan,  370.,  440.],
        [   0.,  150.,  210.,  240.,  np.nan,  np.nan],
        [ np.nan,  100.,  150.,  300.,  390.,  420.],
        [ np.nan,  140.,  170.,  250.,  280.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  220.,  240.,  270.,  290.,  np.nan],
        [   0.,  160.,  190.,  np.nan,  230.,  370.],
        [   0.,  np.nan,  190.,  210.,  np.nan,  430.],
        [   0.,  100.,  220.,  250.,  np.nan,  380.],
        [ np.nan,  100.,  np.nan,  220.,  np.nan,  390.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  110.,  110.,  200.,  310.,  400.],
        [   0.,  150.,  250.,  np.nan,  290.,  390.],
        [   0.,  np.nan,  260.,  350.,  np.nan,  np.nan],
        [   0.,  np.nan,  280.,  310.,  np.nan,  410.],
        [   0.,  140.,  240.,  np.nan,  350.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  130.,  200.,  np.nan,  np.nan,  350.],
        [   0.,  100.,  210.,  360.,  np.nan,  410.],
        [   0.,  100.,  160.,  np.nan,  390.,  420.],
        [   0.,  130.,  190.,  np.nan,  np.nan,  370.],
        [   0.,  np.nan,  130.,  130.,  340.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  170.,  np.nan,  230.,  np.nan,  np.nan],
        [ np.nan,  150.,  150.,  160.,  280.,  330.],
        [   0.,  120.,  150.,  200.,  380.,  380.],
        [   0.,  100.,  160.,  280.,  380.,  420.],
        [   0.,  np.nan,  np.nan,  280.,  np.nan,  400.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  190.,  250.,  np.nan,  270.,  390.],
        [   0.,  np.nan,  120.,  130.,  np.nan,  160.],
        [   0.,  120.,  200.,  220.,  np.nan,  360.],
        [   0.,  140.,  200.,  np.nan,  430.,  np.nan],
        [   0.,  110.,  190.,  300.,  320.,  370.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  np.nan,  290.,  320.,  440.],
        [   0.,  120.,  140.,  330.,  np.nan,  420.],
        [   0.,  np.nan,  110.,  120.,  270.,  290.],
        [   0.,  210.,  260.,  400.,  400.,  np.nan],
        [ np.nan,  np.nan,  130.,  140.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  130.,  240.,  np.nan,  380.,  np.nan],
        [   0.,  np.nan,  290.,  370.,  390.,  430.],
        [   0.,  110.,  180.,  250.,  np.nan,  410.],
        [   0.,  200.,  220.,  330.,  390.,  np.nan],
        [ np.nan,  210.,  290.,  np.nan,  380.,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  180.,  180.,  np.nan,  390.,  410.],
        [   0.,  240.,  310.,  320.,  390.,  np.nan],
        [   0.,  180.,  240.,  290.,  np.nan,  370.],
        [   0.,  130.,  180.,  210.,  np.nan,  340.],
        [ np.nan,  np.nan,  np.nan,  290.,  360.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  240.,  290.,  360.,  400.,  420.],
        [ np.nan,  np.nan,  140.,  150.,  190.,  np.nan],
        [   0.,  np.nan,  250.,  270.,  280.,  320.],
        [   0.,  100.,  150.,  210.,  np.nan,  np.nan],
        [   0.,  100.,  140.,  np.nan,  270.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  190.,  200.,  np.nan,  220.,  np.nan],
        [   0.,  140.,  np.nan,  300.,  310.,  400.],
        [   0.,  160.,  250.,  320.,  340.,  np.nan],
        [   0.,  140.,  190.,  230.,  290.,  350.],
        [   0.,  np.nan,  300.,  np.nan,  350.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  200.,  220.,  230.,  260.,  350.],
        [ np.nan,  150.,  310.,  np.nan,  np.nan,  np.nan],
        [ np.nan,  130.,  230.,  np.nan,  np.nan,  430.],
        [   0.,  110.,  180.,  290.,  np.nan,  400.],
        [   0.,  170.,  250.,  300.,  320.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  100.,  np.nan,  340.,  350.,  np.nan],
        [   0.,  220.,  240.,  np.nan,  390.,  440.],
        [   0.,  150.,  270.,  np.nan,  390.,  410.],
        [   0.,  np.nan,  240.,  290.,  430.,  np.nan],
        [   0.,  100.,  310.,  350.,  350.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  110.,  260.,  np.nan,  290.,  350.],
        [   0.,  np.nan,  120.,  np.nan,  250.,  np.nan],
        [   0.,  100.,  100.,  150.,  210.,  360.],
        [ np.nan,  210.,  240.,  330.,  np.nan,  380.],
        [ np.nan,  300.,  np.nan,  400.,  410.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  160.,  np.nan,  np.nan,  np.nan],
        [ np.nan,  110.,  170.,  380.,  410.,  440.],
        [   0.,  240.,  np.nan,  340.,  370.,  370.],
        [   0.,  260.,  280.,  np.nan,  np.nan,  440.],
        [   0.,  150.,  240.,  310.,  320.,  340.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  190.,  np.nan,  320.,  np.nan],
        [ np.nan,  np.nan,  220.,  240.,  250.,  280.],
        [   0.,  120.,  130.,  180.,  210.,  np.nan],
        [ np.nan,  100.,  120.,  290.,  360.,  390.],
        [   0.,  100.,  100.,  310.,  320.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  230.,  290.,  390.,  420.],
        [   0.,  200.,  200.,  230.,  np.nan,  np.nan],
        [ np.nan,  100.,  190.,  210.,  np.nan,  400.],
        [   0.,  150.,  150.,  np.nan,  np.nan,  430.],
        [ np.nan,  100.,  np.nan,  310.,  340.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  160.,  260.,  310.,  np.nan],
        [   0.,  230.,  270.,  360.,  np.nan,  440.],
        [ np.nan,  120.,  170.,  np.nan,  np.nan,  290.],
        [   0.,  130.,  140.,  np.nan,  290.,  400.],
        [   0.,  110.,  120.,  np.nan,  320.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  100.,  190.,  np.nan,  np.nan,  np.nan],
        [   0.,  np.nan,  160.,  240.,  380.,  420.],
        [   0.,  np.nan,  140.,  240.,  380.,  380.],
        [   0.,  110.,  150.,  190.,  260.,  440.],
        [ np.nan,  100.,  140.,  np.nan,  280.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  160.,  230.,  360.,  420.],
        [   0.,  100.,  270.,  290.,  300.,  420.],
        [   0.,  240.,  260.,  280.,  np.nan,  440.],
        [ np.nan,  120.,  130.,  230.,  270.,  330.],
        [ np.nan,  130.,  np.nan,  310.,  360.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  100.,  190.,  240.,  250.,  270.],
        [   0.,  np.nan,  np.nan,  350.,  390.,  430.],
        [   0.,  200.,  330.,  np.nan,  420.,  420.],
        [   0.,  np.nan,  220.,  340.,  410.,  420.],
        [   0.,  200.,  280.,  np.nan,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  130.,  150.,  330.,  420.],
        [   0.,  140.,  250.,  np.nan,  350.,  420.],
        [   0.,  160.,  280.,  300.,  310.,  np.nan],
        [ np.nan,  160.,  270.,  280.,  np.nan,  320.],
        [   0.,  110.,  180.,  330.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  np.nan,  np.nan,  np.nan,  np.nan],
        [   0.,  np.nan,  250.,  320.,  360.,  440.],
        [   0.,  160.,  200.,  270.,  420.,  440.],
        [   0.,  120.,  160.,  170.,  np.nan,  330.],
        [   0.,  170.,  290.,  np.nan,  410.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  130.,  190.,  np.nan,  390.,  410.],
        [   0.,  230.,  300.,  np.nan,  np.nan,  430.],
        [   0.,  np.nan,  310.,  np.nan,  410.,  np.nan],
        [   0.,  230.,  290.,  np.nan,  420.,  420.],
        [ np.nan,  100.,  110.,  230.,  290.,  340.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  190.,  200.,  280.,  np.nan,  430.],
        [ np.nan,  200.,  np.nan,  340.,  420.,  np.nan],
        [   0.,  130.,  170.,  250.,  np.nan,  380.],
        [   0.,  130.,  220.,  220.,  np.nan,  np.nan],
        [   0.,  150.,  170.,  290.,  310.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  250.,  310.,  330.,  np.nan],
        [ np.nan,  130.,  150.,  170.,  200.,  np.nan],
        [ np.nan,  240.,  np.nan,  250.,  270.,  np.nan],
        [   0.,  np.nan,  120.,  130.,  140.,  410.],
        [   0.,  150.,  150.,  210.,  330.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)


dp_dict = { 'gain': np.matrix([[ np.nan,  np.nan,  150.,  350.,  np.nan,  np.nan],
        [   0.,  110.,  220.,  np.nan,  320.,  390.],
        [   0.,  np.nan,  250.,  280.,  350.,  380.],
        [   0.,  120.,  230.,  240.,  np.nan,  410.],
        [   0.,  130.,  np.nan,  180.,  230.,  240.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  np.nan,  180.,  320.,  390.],
        [ np.nan,  220.,  230.,  np.nan,  290.,  370.],
        [   0.,  140.,  150.,  320.,  370.,  390.],
        [   0.,  110.,  np.nan,  310.,  np.nan,  350.],
        [   0.,  np.nan,  200.,  210.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  np.nan,  260.,  360.,  np.nan],
        [ np.nan,  np.nan,  160.,  270.,  270.,  280.],
        [   0.,  130.,  320.,  410.,  np.nan,  430.],
        [   0.,  140.,  np.nan,  350.,  430.,  np.nan],
        [   0.,  110.,  150.,  300.,  400.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  np.nan,  210.,  300.,  400.,  np.nan],
        [   0.,  np.nan,  170.,  180.,  np.nan,  np.nan],
        [   0.,  150.,  170.,  260.,  410.,  430.],
        [   0.,  350.,  350.,  np.nan,  np.nan,  410.],
        [   0.,  270.,  270.,  330.,  340.,  380.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  130.,  160.,  270.,  320.,  390.],
        [ np.nan,  170.,  np.nan,  310.,  390.,  np.nan],
        [   0.,  180.,  260.,  np.nan,  np.nan,  370.],
        [   0.,  210.,  np.nan,  np.nan,  280.,  350.],
        [   0.,  120.,  130.,  np.nan,  290.,  320.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  190.,  220.,  np.nan,  260.,  np.nan],
        [   0.,  120.,  np.nan,  140.,  140.,  np.nan],
        [   0.,  120.,  170.,  230.,  260.,  350.],
        [   0.,  np.nan,  250.,  270.,  310.,  np.nan],
        [   0.,  120.,  np.nan,  230.,  np.nan,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  110.,  120.,  140.,  np.nan,  340.],
        [   0.,  220.,  240.,  310.,  400.,  np.nan],
        [   0.,  150.,  np.nan,  np.nan,  310.,  320.],
        [ np.nan,  220.,  310.,  340.,  np.nan,  np.nan],
        [   0.,  150.,  160.,  210.,  250.,  400.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  100.,  120.,  140.,  190.,  430.],
        [   0.,  140.,  np.nan,  260.,  np.nan,  np.nan],
        [   0.,  210.,  320.,  350.,  420.,  420.],
        [   0.,  np.nan,  170.,  260.,  270.,  np.nan],
        [   0.,  130.,  np.nan,  220.,  390.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  110.,  170.,  220.,  260.,  420.],
        [   0.,  np.nan,  230.,  np.nan,  np.nan,  410.],
        [   0.,  200.,  260.,  340.,  420.,  np.nan],
        [   0.,  100.,  np.nan,  np.nan,  np.nan,  310.],
        [   0.,  150.,  170.,  290.,  350.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  100.,  120.,  220.,  270.,  np.nan],
        [ np.nan,  160.,  np.nan,  240.,  330.,  np.nan],
        [   0.,  np.nan,  170.,  350.,  380.,  440.],
        [ np.nan,  150.,  220.,  220.,  240.,  np.nan],
        [   0.,  190.,  260.,  320.,  410.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  150.,  200.,  230.,  280.,  380.],
        [   0.,  150.,  np.nan,  np.nan,  400.,  410.],
        [   0.,  140.,  140.,  240.,  390.,  np.nan],
        [   0.,  140.,  180.,  200.,  210.,  290.],
        [ np.nan,  140.,  np.nan,  np.nan,  340.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  130.,  190.,  190.,  250.,  np.nan],
        [ np.nan,  np.nan,  210.,  250.,  np.nan,  410.],
        [   0.,  100.,  220.,  np.nan,  350.,  430.],
        [   0.,  130.,  np.nan,  310.,  320.,  430.],
        [   0.,  140.,  np.nan,  270.,  np.nan,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)


dp_dict = { 'gain': np.matrix([[   0.,  130.,  200.,  np.nan,  np.nan,  360.],
        [   0.,  160.,  230.,  260.,  380.,  np.nan],
        [   0.,  np.nan,  np.nan,  340.,  350.,  np.nan],
        [   0.,  120.,  170.,  np.nan,  270.,  430.],
        [ np.nan,  180.,  230.,  280.,  350.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  200.,  230.,  np.nan,  340.,  np.nan],
        [   0.,  140.,  180.,  190.,  210.,  390.],
        [   0.,  180.,  200.,  np.nan,  420.,  np.nan],
        [   0.,  np.nan,  np.nan,  np.nan,  210.,  410.],
        [   0.,  230.,  270.,  320.,  360.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  170.,  np.nan,  350.,  440.],
        [   0.,  np.nan,  250.,  260.,  290.,  320.],
        [   0.,  160.,  260.,  280.,  360.,  np.nan],
        [   0.,  160.,  190.,  190.,  220.,  np.nan],
        [   0.,  110.,  np.nan,  np.nan,  350.,  410.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  180.,  200.,  230.,  260.,  350.],
        [   0.,  140.,  200.,  220.,  np.nan,  320.],
        [ np.nan,  np.nan,  120.,  np.nan,  300.,  310.],
        [   0.,  130.,  np.nan,  250.,  330.,  370.],
        [ np.nan,  190.,  np.nan,  370.,  370.,  370.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  140.,  210.,  310.,  420.],
        [   0.,  110.,  np.nan,  170.,  280.,  360.],
        [   0.,  np.nan,  np.nan,  230.,  400.,  np.nan],
        [   0.,  np.nan,  170.,  200.,  320.,  np.nan],
        [   0.,  np.nan,  230.,  340.,  430.,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  210.,  np.nan,  300.,  320.,  380.],
        [   0.,  180.,  190.,  200.,  270.,  np.nan],
        [   0.,  np.nan,  np.nan,  170.,  np.nan,  400.],
        [   0.,  150.,  270.,  330.,  np.nan,  440.],
        [   0.,  150.,  np.nan,  np.nan,  240.,  280.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  170.,  180.,  310.,  390.,  np.nan],
        [   0.,  100.,  np.nan,  260.,  np.nan,  340.],
        [   0.,  150.,  220.,  230.,  270.,  380.],
        [   0.,  np.nan,  np.nan,  270.,  np.nan,  330.],
        [   0.,  120.,  170.,  290.,  np.nan,  350.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  230.,  260.,  300.,  330.,  np.nan],
        [   0.,  np.nan,  100.,  350.,  380.,  410.],
        [   0.,  np.nan,  200.,  360.,  380.,  np.nan],
        [   0.,  170.,  200.,  210.,  np.nan,  380.],
        [   0.,  np.nan,  390.,  np.nan,  440.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  170.,  np.nan,  330.,  390.,  400.],
        [   0.,  180.,  230.,  240.,  np.nan,  280.],
        [ np.nan,  np.nan,  160.,  220.,  320.,  380.],
        [   0.,  100.,  np.nan,  np.nan,  np.nan,  420.],
        [   0.,  140.,  np.nan,  160.,  350.,  400.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  140.,  150.,  np.nan,  440.],
        [   0.,  np.nan,  np.nan,  140.,  np.nan,  410.],
        [   0.,  100.,  np.nan,  140.,  160.,  400.],
        [ np.nan,  120.,  160.,  310.,  360.,  400.],
        [ np.nan,  180.,  280.,  320.,  420.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  190.,  230.,  240.,  np.nan],
        [   0.,  100.,  120.,  270.,  np.nan,  430.],
        [   0.,  np.nan,  110.,  np.nan,  390.,  np.nan],
        [ np.nan,  210.,  280.,  np.nan,  420.,  np.nan],
        [   0.,  np.nan,  160.,  270.,  390.,  400.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  100.,  260.,  340.,  np.nan,  390.],
        [   0.,  np.nan,  120.,  150.,  280.,  np.nan],
        [ np.nan,  120.,  130.,  200.,  240.,  380.],
        [   0.,  130.,  np.nan,  190.,  290.,  420.],
        [ np.nan,  180.,  260.,  270.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  110.,  230.,  240.,  410.,  420.],
        [ np.nan,  160.,  np.nan,  200.,  280.,  340.],
        [   0.,  130.,  130.,  np.nan,  np.nan,  370.],
        [ np.nan,  110.,  np.nan,  150.,  280.,  380.],
        [   0.,  np.nan,  210.,  250.,  380.,  380.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  np.nan,  180.,  180.,  230.],
        [   0.,  150.,  300.,  320.,  380.,  390.],
        [ np.nan,  np.nan,  np.nan,  260.,  280.,  350.],
        [   0.,  np.nan,  np.nan,  280.,  350.,  430.],
        [   0.,  170.,  190.,  290.,  340.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  270.,  300.,  310.,  360.],
        [   0.,  160.,  np.nan,  np.nan,  400.,  430.],
        [   0.,  np.nan,  np.nan,  330.,  380.,  400.],
        [   0.,  100.,  210.,  np.nan,  290.,  320.],
        [ np.nan,  np.nan,  100.,  100.,  np.nan,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  230.,  330.,  360.,  380.],
        [   0.,  220.,  320.,  320.,  np.nan,  np.nan],
        [   0.,  np.nan,  180.,  np.nan,  np.nan,  340.],
        [   0.,  150.,  280.,  320.,  420.,  np.nan],
        [   0.,  120.,  np.nan,  320.,  np.nan,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  200.,  220.,  240.,  340.,  np.nan],
        [ np.nan,  130.,  200.,  270.,  350.,  370.],
        [   0.,  160.,  220.,  340.,  390.,  440.],
        [   0.,  np.nan,  np.nan,  np.nan,  270.,  420.],
        [ np.nan,  190.,  260.,  np.nan,  380.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  210.,  300.,  350.,  350.,  440.],
        [   0.,  np.nan,  110.,  360.,  360.,  390.],
        [   0.,  np.nan,  np.nan,  np.nan,  280.,  np.nan],
        [   0.,  130.,  np.nan,  280.,  320.,  370.],
        [   0.,  190.,  310.,  400.,  410.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  160.,  240.,  260.,  310.,  350.],
        [   0.,  120.,  np.nan,  300.,  320.,  np.nan],
        [ np.nan,  np.nan,  np.nan,  210.,  280.,  420.],
        [   0.,  220.,  260.,  270.,  270.,  np.nan],
        [   0.,  210.,  np.nan,  420.,  430.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  140.,  150.,  np.nan,  np.nan],
        [   0.,  170.,  170.,  220.,  np.nan,  250.],
        [   0.,  230.,  260.,  np.nan,  np.nan,  370.],
        [   0.,  200.,  210.,  220.,  320.,  320.],
        [ np.nan,  180.,  230.,  np.nan,  400.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  np.nan,  190.,  280.,  np.nan],
        [ np.nan,  100.,  320.,  400.,  np.nan,  np.nan],
        [   0.,  110.,  140.,  170.,  np.nan,  400.],
        [   0.,  190.,  np.nan,  260.,  340.,  360.],
        [   0.,  230.,  310.,  330.,  370.,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  160.,  230.,  230.,  240.,  390.],
        [   0.,  140.,  240.,  np.nan,  270.,  380.],
        [   0.,  110.,  np.nan,  np.nan,  np.nan,  360.],
        [   0.,  np.nan,  210.,  210.,  270.,  440.],
        [ np.nan,  140.,  140.,  310.,  np.nan,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  190.,  200.,  390.,  400.],
        [   0.,  np.nan,  110.,  np.nan,  200.,  370.],
        [ np.nan,  np.nan,  np.nan,  110.,  310.,  np.nan],
        [ np.nan,  100.,  200.,  260.,  330.,  np.nan],
        [   0.,  100.,  140.,  170.,  250.,  320.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)


dp_dict = { 'gain': np.matrix([[   0.,  150.,  np.nan,  np.nan,  410.,  420.],
        [   0.,  280.,  np.nan,  np.nan,  340.,  420.],
        [   0.,  170.,  np.nan,  340.,  430.,  440.],
        [   0.,  300.,  np.nan,  390.,  430.,  440.],
        [   0.,  100.,  140.,  280.,  350.,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  150.,  210.,  230.,  390.,  np.nan],
        [   0.,  np.nan,  np.nan,  360.,  360.,  410.],
        [   0.,  130.,  150.,  170.,  210.,  310.],
        [ np.nan,  130.,  190.,  190.,  np.nan,  np.nan],
        [   0.,  190.,  np.nan,  370.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  np.nan,  300.,  390.,  420.],
        [   0.,  160.,  230.,  230.,  np.nan,  340.],
        [   0.,  np.nan,  330.,  330.,  370.,  410.],
        [ np.nan,  np.nan,  280.,  np.nan,  np.nan,  440.],
        [   0.,  160.,  190.,  240.,  260.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  150.,  170.,  np.nan,  np.nan,  440.],
        [   0.,  140.,  190.,  290.,  310.,  np.nan],
        [   0.,  210.,  np.nan,  280.,  400.,  np.nan],
        [   0.,  100.,  240.,  370.,  380.,  np.nan],
        [   0.,  100.,  np.nan,  170.,  170.,  380.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  180.,  200.,  np.nan,  240.,  410.],
        [   0.,  180.,  230.,  250.,  320.,  340.],
        [   0.,  160.,  np.nan,  230.,  np.nan,  np.nan],
        [ np.nan,  100.,  110.,  110.,  np.nan,  np.nan],
        [   0.,  140.,  310.,  320.,  320.,  370.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  160.,  240.,  290.,  330.,  np.nan],
        [   0.,  np.nan,  150.,  230.,  310.,  330.],
        [   0.,  250.,  np.nan,  320.,  np.nan,  370.],
        [   0.,  120.,  160.,  170.,  np.nan,  np.nan],
        [   0.,  np.nan,  220.,  240.,  280.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  190.,  240.,  250.,  400.,  440.],
        [   0.,  130.,  190.,  300.,  380.,  np.nan],
        [   0.,  100.,  220.,  260.,  340.,  360.],
        [   0.,  np.nan,  180.,  240.,  np.nan,  np.nan],
        [ np.nan,  140.,  200.,  390.,  410.,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  180.,  270.,  330.,  np.nan,  440.],
        [   0.,  150.,  280.,  280.,  310.,  np.nan],
        [   0.,  np.nan,  220.,  240.,  360.,  380.],
        [   0.,  np.nan,  310.,  np.nan,  400.,  np.nan],
        [   0.,  np.nan,  260.,  260.,  310.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  190.,  np.nan,  230.,  390.],
        [ np.nan,  np.nan,  320.,  330.,  380.,  400.],
        [   0.,  120.,  140.,  190.,  np.nan,  390.],
        [   0.,  100.,  180.,  290.,  np.nan,  410.],
        [ np.nan,  np.nan,  240.,  320.,  390.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  np.nan,  260.,  340.,  400.],
        [   0.,  120.,  210.,  280.,  np.nan,  440.],
        [ np.nan,  160.,  230.,  260.,  320.,  330.],
        [   0.,  np.nan,  150.,  280.,  np.nan,  440.],
        [ np.nan,  260.,  np.nan,  400.,  410.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  150.,  np.nan,  230.,  310.,  320.],
        [   0.,  130.,  280.,  np.nan,  np.nan,  340.],
        [   0.,  100.,  160.,  200.,  np.nan,  410.],
        [ np.nan,  np.nan,  180.,  190.,  340.,  410.],
        [   0.,  160.,  180.,  190.,  np.nan,  410.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  np.nan,  190.,  250.,  290.,  np.nan],
        [   0.,  220.,  np.nan,  320.,  390.,  390.],
        [   0.,  100.,  np.nan,  160.,  np.nan,  np.nan],
        [   0.,  150.,  180.,  220.,  260.,  430.],
        [   0.,  170.,  np.nan,  210.,  220.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  150.,  260.,  310.,  380.,  400.],
        [   0.,  140.,  np.nan,  np.nan,  420.,  np.nan],
        [   0.,  np.nan,  270.,  320.,  np.nan,  400.],
        [ np.nan,  140.,  150.,  np.nan,  370.,  np.nan],
        [   0.,  140.,  170.,  180.,  280.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  170.,  np.nan,  250.,  310.,  320.],
        [   0.,  160.,  np.nan,  340.,  np.nan,  np.nan],
        [   0.,  150.,  250.,  250.,  280.,  320.],
        [   0.,  140.,  np.nan,  220.,  340.,  400.],
        [   0.,  260.,  np.nan,  440.,  np.nan,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  np.nan,  np.nan,  250.,  320.,  np.nan],
        [   0.,  120.,  np.nan,  140.,  220.,  360.],
        [   0.,  np.nan,  np.nan,  260.,  390.,  400.],
        [   0.,  120.,  np.nan,  170.,  210.,  330.],
        [   0.,  np.nan,  200.,  250.,  270.,  300.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  np.nan,  340.,  370.,  np.nan,  430.],
        [ np.nan,  190.,  290.,  330.,  390.,  430.],
        [   0.,  110.,  210.,  np.nan,  330.,  np.nan],
        [   0.,  100.,  170.,  220.,  330.,  340.],
        [   0.,  160.,  200.,  370.,  390.,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  140.,  230.,  260.,  290.,  np.nan],
        [   0.,  np.nan,  np.nan,  np.nan,  260.,  np.nan],
        [   0.,  120.,  220.,  240.,  360.,  np.nan],
        [   0.,  110.,  150.,  280.,  330.,  np.nan],
        [   0.,  np.nan,  170.,  240.,  340.,  370.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  130.,  250.,  310.,  400.,  420.],
        [   0.,  160.,  230.,  300.,  360.,  np.nan],
        [ np.nan,  220.,  np.nan,  270.,  360.,  390.],
        [   0.,  150.,  280.,  350.,  np.nan,  410.],
        [   0.,  130.,  np.nan,  170.,  np.nan,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  320.,  410.,  430.,  440.],
        [   0.,  100.,  150.,  280.,  np.nan,  np.nan],
        [   0.,  170.,  200.,  250.,  310.,  420.],
        [   0.,  120.,  180.,  190.,  400.,  400.],
        [   0.,  110.,  np.nan,  np.nan,  np.nan,  380.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  150.,  np.nan,  240.,  290.,  320.],
        [   0.,  100.,  230.,  260.,  np.nan,  np.nan],
        [   0.,  130.,  340.,  370.,  np.nan,  np.nan],
        [ np.nan,  140.,  np.nan,  190.,  np.nan,  420.],
        [   0.,  260.,  290.,  400.,  420.,  430.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  190.,  230.,  280.,  np.nan,  440.],
        [ np.nan,  120.,  210.,  230.,  240.,  260.],
        [   0.,  110.,  np.nan,  np.nan,  290.,  350.],
        [   0.,  220.,  260.,  np.nan,  np.nan,  330.],
        [   0.,  100.,  100.,  np.nan,  140.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  150.,  np.nan,  280.,  np.nan,  420.],
        [   0.,  100.,  270.,  np.nan,  np.nan,  420.],
        [ np.nan,  150.,  250.,  280.,  300.,  400.],
        [   0.,  150.,  260.,  270.,  270.,  np.nan],
        [   0.,  180.,  280.,  np.nan,  320.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  np.nan,  220.,  300.,  310.],
        [   0.,  np.nan,  150.,  200.,  np.nan,  390.],
        [   0.,  110.,  140.,  260.,  330.,  350.],
        [ np.nan,  160.,  330.,  370.,  np.nan,  420.],
        [   0.,  np.nan,  220.,  np.nan,  270.,  300.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  280.,  290.,  np.nan,  310.,  np.nan],
        [ np.nan,  140.,  170.,  190.,  np.nan,  330.],
        [   0.,  120.,  150.,  210.,  270.,  np.nan],
        [   0.,  110.,  np.nan,  330.,  350.,  400.],
        [   0.,  110.,  np.nan,  240.,  280.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  120.,  140.,  280.,  350.,  np.nan],
        [   0.,  np.nan,  210.,  np.nan,  390.,  400.],
        [ np.nan,  250.,  310.,  320.,  370.,  390.],
        [   0.,  150.,  170.,  360.,  370.,  390.],
        [   0.,  np.nan,  260.,  270.,  np.nan,  360.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  130.,  np.nan,  np.nan,  400.,  430.],
        [   0.,  240.,  270.,  310.,  np.nan,  np.nan],
        [ np.nan,  100.,  np.nan,  150.,  230.,  400.],
        [   0.,  110.,  np.nan,  np.nan,  200.,  400.],
        [   0.,  140.,  210.,  280.,  410.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  110.,  160.,  np.nan,  390.,  430.],
        [   0.,  140.,  150.,  160.,  270.,  np.nan],
        [   0.,  110.,  180.,  230.,  np.nan,  np.nan],
        [ np.nan,  np.nan,  260.,  330.,  340.,  410.],
        [   0.,  110.,  np.nan,  260.,  310.,  320.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  170.,  190.,  np.nan,  290.,  320.],
        [   0.,  200.,  220.,  220.,  360.,  380.],
        [ np.nan,  190.,  330.,  np.nan,  np.nan,  430.],
        [   0.,  np.nan,  340.,  np.nan,  420.,  440.],
        [   0.,  180.,  200.,  np.nan,  240.,  410.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  150.,  290.,  300.,  np.nan,  400.],
        [   0.,  100.,  np.nan,  200.,  220.,  340.],
        [   0.,  np.nan,  180.,  180.,  270.,  390.],
        [   0.,  100.,  np.nan,  170.,  180.,  np.nan],
        [   0.,  260.,  np.nan,  np.nan,  330.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  130.,  np.nan,  180.,  290.,  np.nan],
        [   0.,  140.,  210.,  np.nan,  np.nan,  310.],
        [   0.,  np.nan,  np.nan,  250.,  270.,  430.],
        [   0.,  120.,  260.,  270.,  290.,  310.],
        [   0.,  np.nan,  270.,  290.,  300.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  210.,  260.,  np.nan,  390.,  420.],
        [   0.,  160.,  160.,  np.nan,  180.,  np.nan],
        [   0.,  130.,  180.,  280.,  np.nan,  380.],
        [   0.,  210.,  np.nan,  360.,  np.nan,  420.],
        [   0.,  np.nan,  np.nan,  270.,  310.,  360.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  140.,  190.,  190.,  np.nan,  350.],
        [ np.nan,  np.nan,  400.,  410.,  430.,  440.],
        [ np.nan,  110.,  160.,  170.,  330.,  np.nan],
        [   0.,  180.,  np.nan,  320.,  340.,  np.nan],
        [   0.,  150.,  240.,  270.,  280.,  390.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  140.,  220.,  270.,  370.,  np.nan],
        [   0.,  270.,  320.,  370.,  380.,  420.],
        [ np.nan,  130.,  150.,  np.nan,  320.,  np.nan],
        [   0.,  130.,  np.nan,  190.,  330.,  410.],
        [ np.nan,  np.nan,  140.,  np.nan,  240.,  290.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  np.nan,  220.,  230.,  np.nan,  np.nan],
        [   0.,  170.,  350.,  360.,  np.nan,  np.nan],
        [   0.,  180.,  290.,  300.,  320.,  340.],
        [   0.,  100.,  200.,  310.,  np.nan,  410.],
        [   0.,  np.nan,  np.nan,  170.,  240.,  350.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  110.,  130.,  np.nan,  310.,  340.],
        [   0.,  270.,  np.nan,  np.nan,  340.,  380.],
        [ np.nan,  150.,  220.,  280.,  np.nan,  410.],
        [   0.,  100.,  160.,  170.,  230.,  np.nan],
        [   0.,  100.,  250.,  310.,  360.,  420.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  190.,  np.nan,  290.,  320.,  370.],
        [   0.,  np.nan,  220.,  290.,  400.,  420.],
        [   0.,  180.,  np.nan,  420.,  420.,  430.],
        [   0.,  210.,  np.nan,  340.,  380.,  410.],
        [ np.nan,  np.nan,  280.,  330.,  np.nan,  400.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  240.,  240.,  250.,  290.,  330.],
        [   0.,  np.nan,  170.,  340.,  380.,  430.],
        [   0.,  np.nan,  np.nan,  300.,  np.nan,  340.],
        [ np.nan,  110.,  180.,  np.nan,  320.,  380.],
        [   0.,  np.nan,  230.,  260.,  390.,  440.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[   0.,  250.,  np.nan,  300.,  np.nan,  np.nan],
        [   0.,  np.nan,  150.,  210.,  330.,  370.],
        [ np.nan,  np.nan,  140.,  250.,  260.,  420.],
        [ np.nan,  170.,  290.,  np.nan,  360.,  410.],
        [ np.nan,  170.,  220.,  300.,  370.,  380.]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[ np.nan,  170.,  190.,  np.nan,  320.,  320.],
        [ np.nan,  150.,  170.,  180.,  np.nan,  390.],
        [ np.nan,  110.,  np.nan,  200.,  270.,  440.],
        [ np.nan,  np.nan,  280.,  380.,  420.,  420.],
        [   0.,  120.,  150.,  260.,  330.,  np.nan]], dtype=np.float),
    "total_resource":800,
    "decision_set":[0, 100, 200, 300, 400, 500],
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)




# print repr(dp_dict["gain"])
#
# exit()


# total_resource=800
# gain=np.matrix([
#     [0, 130, 150, np.nan, np.nan, np.nan],
#     [0, 100, 160, 210, np.nan, 410],
#     [0, 100, 120, np.nan, 210, np.nan],
#     [np.nan, 110, 200, 250, 330, 370],
#     [np.nan, np.nan, 210, 290, 320, np.nan]
# ])
# invest = [0, 100, 200, 300, 400, 500]
# project_list = [u"子公司%s" % str(idx) for idx in range(1, n_project + 1)]

# gain=np.matrix([
#     0, 9, 12, 16, 21, np.nan,
#     0, 10, 16, 21, 31, 33,
#     0, 7, 12, 17, 21, np.nan,
#     0, 11, 20, 23, 34, 40,
#     np.nan, np.nan, 21, 25, 37, np.nan
# ]).reshape(5,6)
# total_resource=100
# invest = [0, 10, 20, 30, 40, 50]


# dp_dict = {
#     "total_resource": 100,
#     "gain": np.matrix([
#         0, 9, 12, 16, 21, np.nan,
#         0, 10, 16, 21, 31, 33,
#         0, 7, 12, 17, 21, np.nan,
#         0, 11, 20, 23, 34, 40,
#         np.nan, np.nan, 21, 25, 37, np.nan
#     ]).reshape(5,6),
#     "decision_set": [0, 10, 20, 30, 40, 50],
#     "project_list": [u"子公司%s" % str(idx) for idx in range(1, 5 + 1)]
# }

#dp_list.append(dp_dict)

# gain=np.matrix([
#     0, 9, 14, 18, 21, 24,
#     0, 4, 9, 15, 22, 30,
#     0, 10, 14, 16, 20, 26,
# ]).reshape(3,6)
# total_resource=5
# invest = [0, 1, 2, 3, 4, 5]


import pickle
#import dill as pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(dp_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    dp_list_loaded = pickle.load(f)

result3 = 0
for i, dp_dict in enumerate(dp_list_loaded):

    dp = ResourceAllocationDP(
        **dp_dict
    )

    selected_data_bytes = BytesIO()
    pickle.dump(dp_dict, selected_data_bytes)

    question_data = b64encode(selected_data_bytes.getvalue()).decode()

    a= "KGRwMApTJ3Byb2plY3RfbGlzdCcKcDEKKGxwMgpWXHU1YjUwXHU1MTZjXHU1M2Y4MQpwMwphVlx1NWI1MFx1NTE2Y1x1NTNmODIKcDQKYVZcdTViNTBcdTUxNmNcdTUzZjgzCnA1CmFWXHU1YjUwXHU1MTZjXHU1M2Y4NApwNgphVlx1NWI1MFx1NTE2Y1x1NTNmODUKcDcKYXNTJ3RvdGFsX3Jlc291cmNlJwpwOApJODAwCnNTJ2dhaW4nCnA5CmNudW1weS5jb3JlLm11bHRpYXJyYXkKX3JlY29uc3RydWN0CnAxMAooY251bXB5Lm1hdHJpeGxpYi5kZWZtYXRyaXgKbWF0cml4CnAxMQooSTAKdHAxMgpTJ2InCnAxMwp0cDE0ClJwMTUKKEkxCihJNQpJNgp0cDE2CmNudW1weQpkdHlwZQpwMTcKKFMnZjgnCnAxOApJMApJMQp0cDE5ClJwMjAKKEkzClMnPCcKcDIxCk5OTkktMQpJLTEKSTAKdHAyMgpiSTAwClMnXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwXHhhMHRAXHgwMFx4MDBceDAwXHgwMFx4MDBAekBceDAwXHgwMFx4MDBceDAwXHgwMFx4ZTB6QFx4MDBceDAwXHgwMFx4MDBceDAwXHhlMHpAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwQGVAXHgwMFx4MDBceDAwXHgwMFx4MDBAZUBceDAwXHgwMFx4MDBceDAwXHgwMGB4QFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4ZjhceDdmXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBeQFx4MDBceDAwXHgwMFx4MDBceDAwXHg4MGFAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwbkBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwYHhAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMEBgQFx4MDBceDAwXHgwMFx4MDBceDAwXHg4MGtAXHgwMFx4MDBceDAwXHgwMFx4MDBAcEBceDAwXHgwMFx4MDBceDAwXHgwMFx4YzByQFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4ZjhceDdmXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4ODBmQFx4MDBceDAwXHgwMFx4MDBceDAwQGpAXHgwMFx4MDBceDAwXHgwMFx4MDBAcEBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwXHhhMHlAJwpwMjMKdHAyNApic1MnZGVjaXNpb25fc2V0JwpwMjUKKGxwMjYKSTAKYUkxMDAKYUkyMDAKYUkzMDAKYUk0MDAKYUk1MDAKYXMu"

    if question_data == a:
        print repr(dp_dict)

    result_force_calculate_feasible_state = dp.solve(allow_state_func=force_calculate_feasible_state)
    result = dp.solve()
    #print result_force_calculate_feasible_state
    #print result


    if len(result.policy) == 3:
        #print repr(dp_dict)
        result3 += 1
        #print result3
        #break
        #continue
    #result = dp.solve()

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

    show_blank4 = False
    blank4_desc = ""
    blank4_result = ""
    if first_multiple_stage and first_multiple_result_state and first_multiple_result_x:
        show_blank4 = True
        blank4_desc = (u"当$s_{%(first_multiple_stage)d}=%(first_multiple_state)s$时，"
                       u"$x^*_{%(first_multiple_stage)s}$(所有可能)取值为"
                       % {
                           "first_multiple_stage": first_multiple_stage,
                           "first_multiple_state": first_multiple_result_state
                       }
                       )
        blank4_result = first_multiple_result_x

    question_template = latex_jinja_env.get_template('dp_resource_allocation_1.tex')
    answer_template = latex_jinja_env.get_template('/utils/dynamic_programming_template.tex')

    result_list = [result_force_calculate_feasible_state]
    show_only_force_calculate_feasible_state = False
    if not show_only_force_calculate_feasible_state:
        can_optimize_stage = []
        equal = True
        for i, j in zip(result.items(), result_force_calculate_feasible_state.items()):
            if i == j:
                continue
            else:
                equal = False
                break

        if not equal:
            result_list.append(result)

    question_tex = question_template.render(
        show_question=True,
        show_answer_explanation=True,
        dp = dp
    )

    r.clipboard_append(question_tex)

    human_readable_result = u"最终结果：最优的总投资收益为%(opt_value)s万元, 最优策略为:" % {
        "opt_value": result.opt_value,
    }
    policy_str = ""

    if len(result.policy) > 1:
        policy_str += "\n"

    project_list = dp.project_list

    for i ,p in enumerate(result.policy):

        if len(result.policy) > 1:
            policy_str += "%s: " % str(i+1)
        policy, = p
        policy_str += u"，".join([
            u"%(project)s投资%(decision)s万元" % {"project": project, "decision":decision}
            for project, decision in zip(project_list, policy["opt_x"].values())
        ])
        policy_str += "\n"
    human_readable_result += policy_str

    answer_tex = answer_template.render(
        answer_table_iters=iter(range(1,50)),
        show_question=True,
        show_answer_explanation=True,
        show_blank=True,
        show_blank_answer=True,
        dp=dp,
        dp_result_list=result_list,
        result=result,
        blank1_desc = u"最优的总投资收益为",
        blank2_desc = u"可能的最优策略的个数为",
        blank3_desc = u"一个最优策略为（如有多个可只列出一个）",
        show_blank4 = show_blank4,
        blank4_desc = blank4_desc,
        blank4_result = blank4_result,
        human_readable_result = human_readable_result
    )

    r.clipboard_append(answer_tex)
