# -*- coding: utf-8 -*-

from latex_utils.utils.dynamic_programming import ResourceAllocationDP, force_calculate_feasible_state
from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from copy import deepcopy
import numpy as np
import random
import pickle
import random

from io import BytesIO
from base64 import b64encode

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


SAVED_QUESTION = "resource_allocation_dp2.bin"

M = 3
N = 6
N_nan = 3
OPT_TYPE = "max"
PROJECT_LIST = [u"广州", u"深圳", u"珠海"]
ALLOW_NON_ALLOCATED_RESOURCE = "False"


def is_qualified_question(gain, total_resource, decision_set, project_list, mem_gain_list,
                          opt_type=OPT_TYPE, allow_non_allocated_resource=ALLOW_NON_ALLOCATED_RESOURCE,
                          saved_question=SAVED_QUESTION):

    qualified = False
    dp = ResourceAllocationDP(total_resource, gain, decision_set, project_list, opt_type, allow_non_allocated_resource)

    result_force_calculate_feasible_state = dp.solve(allow_state_func=force_calculate_feasible_state)
    result = dp.solve()

    # 需要至少有两个最优决策或者需要至少有一个状态的最优决策多结果的
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

    if (not ((first_multiple_stage and first_multiple_result_state and first_multiple_result_x) or len(result.policy) > 1)):
        #print first_multiple_stage and first_multiple_result_state and first_multiple_result_x, len(result.policy)
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
        r.clipboard_append('    "opt_type": "' + OPT_TYPE + '",\n')
        r.clipboard_append('    "allow_non_allocated_resource":' + ALLOW_NON_ALLOCATED_RESOURCE + ',\n')
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

        rand_list = np.random.randint(5, 40, n_element).tolist()
        splitted_list = [rand_list[i:i + N] for i in xrange(0, len(rand_list), N)]
        for i, l in enumerate(splitted_list):
            while len(set(splitted_list[i])) != N:
                new_i =  random.choice(range(20,45))
                splitted_list[i].append(new_i)
            splitted_list[i] = list(set(splitted_list[i]))
            splitted_list[i] = sorted(splitted_list[i])
            splitted_list[i][0] = 0

        merged_list = []
        for l in splitted_list:
            merged_list.extend(l)
        gain_array = np.array(merged_list, dtype=np.float16)
        rand_nan_idx = np.random.randint(0, n_element, N_nan)
        gain_array[rand_nan_idx] = np.nan
        gain = np.matrix(gain_array).reshape(M, N)
        return gain

    total_resource = dp.total_resource
    decision_set = dp.decision_set
    project_list = dp.project_list
    while n < 100:
        gain = get_rand_gain()
        # print repr(gain)
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

dp_dict = { 'gain': np.matrix([[  0.,  14.,  17., np.nan,  27.,  36.],
        [  0.,  18.,  24.,  25.,  26.,  37.],
        [  0.,  14.,  26., np.nan,  33., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  21.,  24.,  25.,  33.,  35.],
        [np.nan,  10.,  13.,  28.,  37.,  38.],
        [  0., np.nan, np.nan,  24.,  30.,  35.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  21.,  22.,  23.,  34.,  36.],
        [  0.,   9.,  19.,  26.,  34., np.nan],
        [  0.,  13.,  21.,  25., np.nan,  32.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   8.,  13., np.nan,  36.,  37.],
        [  0.,  22.,  23.,  29.,  32.,  37.],
        [  0., np.nan,  27.,  35.,  36., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  11., np.nan,  20.,  23., np.nan],
        [  0.,   7.,   8., np.nan,  14.,  35.],
        [  0.,  22.,  29.,  33.,  39.,  41.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan, np.nan,  17., np.nan,  27.,  39.],
        [  0.,  14.,  24.,  29.,  36.,  41.],
        [  0.,  14.,  27.,  31.,  34.,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   7.,  12.,  18.,  29.,  36.],
        [  0.,  14.,  17., np.nan,  25.,  37.],
        [np.nan,  21.,  23.,  33.,  36.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  15.,  28.,  33.,  38.],
        [  0., np.nan,  16., np.nan,  22.,  38.],
        [  0.,   7.,  11.,  23.,  33.,  35.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  15.,  20., np.nan,  32.,  34.],
        [  0.,  14.,  24.,  32., np.nan,  39.],
        [  0.,   8.,  15.,  17., np.nan,  30.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  10.,  14., np.nan,  24.,  27.],
        [  0.,  20.,  24., np.nan,  34.,  39.],
        [  0.,   7.,   8.,  11.,  18.,  21.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  18.,  20.,  27.,  29.,  33.],
        [  0.,  16.,  24., np.nan,  39.,  43.],
        [  0.,  16.,  19., np.nan,  27., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  24.,  25.,  28.,  31., np.nan],
        [  0.,  22.,  23.,  31.,  32.,  39.],
        [  0.,  25., np.nan,  29.,  31.,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  20.,  22.,  25.,  32.,  37.],
        [  0., np.nan,  21.,  32.,  35.,  36.],
        [np.nan,  18., np.nan,  22.,  29.,  33.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  12.,  21.,  26., np.nan, np.nan],
        [  0., np.nan,  30.,  32.,  34.,  36.],
        [  0.,   9.,  20.,  22.,  35.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  11., np.nan,  34.,  37.],
        [  0., np.nan,  12.,  22.,  26.,  36.],
        [  0.,  16.,  20.,  29.,  36.,  42.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  14.,  16.,  24.,  26.,  38.],
        [  0.,  10.,  15., np.nan,  27.,  31.],
        [  0., np.nan, np.nan,  23.,  31.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  10., np.nan,  22.,  24., np.nan],
        [  0.,  19.,  24.,  25.,  26.,  30.],
        [  0.,  10.,  11.,  15., np.nan,  32.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  16.,  23.,  28.,  37.,  39.],
        [  0.,  16., np.nan,  31.,  32.,  39.],
        [  0.,  14.,  15.,  18., np.nan,  34.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  20.,  25.,  33.,  36.,  39.],
        [  0.,  13.,  14.,  17.,  29.,  36.],
        [np.nan,  16.,  19., np.nan,  29.,  31.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  20.,  22.,  29.,  31., np.nan],
        [  0.,  18.,  21., np.nan,  28.,  31.],
        [  0.,  19.,  22.,  27.,  28., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  24., np.nan,  37.,  39.,  42.],
        [np.nan,  15.,  18.,  19.,  24.,  40.],
        [  0.,  18., np.nan,  28.,  31.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   9., np.nan,  18.,  38.,  39.],
        [np.nan,  23.,  25.,  32., np.nan,  39.],
        [  0.,  15.,  33.,  35.,  36.,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  21.,  28.,  31.,  35.,  41.],
        [  0.,  13.,  15.,  21., np.nan,  33.],
        [  0., np.nan,  27.,  30., np.nan,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   9.,  13., np.nan,  30.,  33.],
        [  0.,   9.,  19.,  23., np.nan,  38.],
        [np.nan,  10.,  17.,  20.,  21.,  44.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  12.,  20.,  21., np.nan, np.nan],
        [  0.,  15.,  17.,  19.,  36.,  37.],
        [np.nan,  22.,  23.,  31.,  32.,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  16.,  18., np.nan,  26.,  38.],
        [  0.,  12.,  20.,  21.,  28.,  33.],
        [  0.,  12.,  31.,  34., np.nan,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  22.,  31.,  34.,  38.,  43.],
        [  0.,  12.,  16., np.nan, np.nan,  26.],
        [  0.,  19.,  22.,  24.,  31.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  21.,  24.,  25.,  32., np.nan],
        [  0.,  16.,  24., np.nan,  28.,  30.],
        [  0.,  13.,  15.,  17.,  24.,  32.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  12.,  19.,  32.,  34.],
        [  0.,  15.,  19.,  21.,  27.,  37.],
        [np.nan,  19., np.nan,  31.,  35.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   7., np.nan,  13., np.nan,  37.],
        [  0.,  24.,  25.,  26.,  29.,  34.],
        [  0.,  10.,  26.,  31., np.nan,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  17.,  25.,  26., np.nan],
        [  0.,  14.,  17.,  23.,  28.,  34.],
        [  0.,   8.,  12.,  20.,  24.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  21.,  24.,  25.,  26.,  28.],
        [  0.,  20., np.nan,  27.,  37.,  38.],
        [np.nan,  11.,  31.,  32., np.nan,  40.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  11.,  15.,  21.,  36.,  38.],
        [np.nan,  12.,  22.,  24.,  26.,  34.],
        [  0., np.nan, np.nan,  35.,  37.,  43.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  16.,  18.,  19., np.nan,  43.],
        [  0.,  16.,  17.,  23., np.nan,  38.],
        [  0.,  16.,  25., np.nan,  30.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  24.,  31., np.nan,  35.],
        [  0.,  22.,  26.,  35.,  36.,  37.],
        [np.nan,   6.,  12.,  19.,  29.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,   7.,  16.,  17.,  24.,  27.],
        [  0.,  21.,  22., np.nan,  27.,  28.],
        [np.nan,  15.,  17.,  23.,  28.,  29.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  10.,  20.,  28., np.nan, np.nan],
        [  0.,  19.,  20.,  23.,  25.,  38.],
        [  0.,  25., np.nan,  30.,  31.,  34.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   8.,  13.,  15.,  16.,  23.],
        [  0.,   7.,   9.,  10.,  33.,  34.],
        [  0.,   7.,  15., np.nan, np.nan, np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  11., np.nan,  15., np.nan,  39.],
        [  0.,  12.,  15.,  17.,  18.,  27.],
        [np.nan,  19.,  22.,  26.,  38.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  16.,  20., np.nan,  34.,  37.],
        [  0.,  12.,  19., np.nan,  33.,  36.],
        [  0.,   8.,  20.,  23.,  27.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  15., np.nan,  19.,  35.,  38.],
        [  0.,  26.,  28.,  30.,  32., np.nan],
        [  0.,  11.,  13.,  15., np.nan,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  16.,  19., np.nan,  23.,  35.],
        [  0.,  18.,  24.,  27.,  28., np.nan],
        [  0.,  18.,  19.,  20.,  34., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  27.,  28.,  29.,  30.,  39.],
        [  0.,  12.,  13., np.nan,  21.,  33.],
        [  0.,  17.,  18.,  25.,  31., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  10.,  21.,  27.,  38.,  42.],
        [np.nan,   6.,   7.,   8.,  14.,  16.],
        [  0.,  15.,  16.,  18., np.nan, np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  17.,  29.,  30., np.nan,  37.],
        [np.nan,  20.,  25.,  35.,  37.,  39.],
        [  0.,  13., np.nan,  22.,  30.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  25.,  26.,  35.,  36.],
        [  0.,  14.,  15.,  19.,  23.,  36.],
        [np.nan,  13.,  14.,  16.,  24., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  11.,  19.,  29.,  30.,  34.],
        [np.nan,  19., np.nan, np.nan,  37.,  38.],
        [  0.,   9.,  11.,  21.,  27.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  13.,  19.,  22., np.nan,  29.],
        [  0.,  18., np.nan,  24., np.nan,  32.],
        [  0.,   8.,  22.,  27.,  28.,  35.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  17.,  23.,  24.,  37.,  38.],
        [  0.,  16.,  20., np.nan,  24.,  27.],
        [np.nan,   7., np.nan,  27.,  28.,  32.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   6.,   7.,  26.,  28., np.nan],
        [  0.,  16.,  21.,  25.,  32.,  34.],
        [np.nan,  12.,  28.,  29.,  31., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  25.,  26.,  29.,  34., np.nan],
        [  0.,  15.,  19., np.nan,  36.,  38.],
        [  0., np.nan,  25.,  29.,  31.,  35.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  23., np.nan,  29.,  33.,  34.],
        [  0.,  12.,  20.,  21.,  25.,  28.],
        [  0.,  17.,  18.,  25., np.nan,  28.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  25.,  29.,  30., np.nan, np.nan],
        [  0.,  17.,  21., np.nan,  30.,  33.],
        [  0.,  21.,  25.,  35.,  37.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  25.,  30.,  31., np.nan],
        [  0.,  11.,  17.,  18.,  31.,  37.],
        [  0.,  14., np.nan,  36.,  37.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   8., np.nan,  22.,  25.,  35.],
        [  0.,  13.,  20.,  29.,  30.,  37.],
        [  0.,  25., np.nan,  33.,  34., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   9.,  10.,  21.,  25.,  30.],
        [  0.,  10.,  17.,  21., np.nan,  37.],
        [  0.,  10., np.nan, np.nan,  30.,  40.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  15.,  23., np.nan,  34.,  36.],
        [  0., np.nan,  22.,  26., np.nan,  41.],
        [  0.,  20.,  23.,  27.,  30.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  13.,  16.,  18.,  31., np.nan],
        [  0.,  15., np.nan,  26.,  33.,  34.],
        [  0.,   8.,  10.,  14.,  19.,  32.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,   9., np.nan,  31.,  34.,  35.],
        [  0.,  13.,  20.,  24.,  27.,  33.],
        [  0.,  20.,  31.,  35.,  36.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  12.,  14.,  23., np.nan,  31.],
        [  0.,  17., np.nan,  24.,  26., np.nan],
        [  0.,  27.,  36.,  38.,  40.,  41.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan, np.nan,  19.,  23.,  28.,  32.],
        [  0.,  20.,  27.,  30.,  32.,  36.],
        [  0.,   6.,   8., np.nan,  17.,  30.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  12., np.nan,  34.,  37.,  39.],
        [  0.,  20.,  21., np.nan,  24.,  35.],
        [  0.,  11.,  14.,  18., np.nan,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  13.,  16.,  17.,  28.,  38.],
        [np.nan,   8.,  10.,  22.,  23.,  40.],
        [  0., np.nan,  10.,  25.,  32.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   9.,  12.,  17., np.nan,  37.],
        [  0.,  17.,  30.,  34.,  35., np.nan],
        [  0.,  13.,  19.,  20.,  34., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  19.,  26.,  31.,  35.,  36.],
        [  0.,  21.,  24.,  26.,  29.,  32.],
        [np.nan,  25., np.nan,  30.,  36.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  34.,  36.,  38.,  39.],
        [  0.,  16.,  24.,  31.,  33.,  34.],
        [  0.,  16.,  21.,  25., np.nan, np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  14.,  17.,  26.,  31.,  33.],
        [np.nan,  16.,  20.,  23.,  34.,  36.],
        [  0.,  14., np.nan,  21.,  28., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  13.,  15.,  21.,  22.,  42.],
        [  0.,  17.,  22.,  23., np.nan,  30.],
        [  0.,  22., np.nan,  28., np.nan,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  14., np.nan,  20.,  28.,  39.],
        [  0.,  21., np.nan,  23.,  33.,  37.],
        [  0., np.nan,  16.,  19.,  27.,  41.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  22.,  23.,  30., np.nan,  38.],
        [  0., np.nan, np.nan,  33.,  36.,  39.],
        [  0.,  15.,  18.,  26.,  28.,  35.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   6., np.nan,  15.,  25.,  32.],
        [  0.,   9.,  14.,  18.,  21.,  32.],
        [  0., np.nan,  27.,  29.,  34., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   8.,  19.,  22.,  33.,  36.],
        [  0.,  15.,  20.,  26., np.nan,  36.],
        [  0.,  15.,  16., np.nan, np.nan,  27.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  23.,  24.,  31.,  36.],
        [  0.,  21.,  25.,  30.,  37.,  38.],
        [  0.,  15.,  26., np.nan, np.nan,  42.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  14.,  17.,  34.,  38.],
        [np.nan,   7.,  12.,  30.,  32., np.nan],
        [  0.,  25.,  27.,  29.,  31.,  32.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   7.,  19.,  24., np.nan,  32.],
        [  0.,   8.,  14.,  20.,  26.,  28.],
        [  0.,  15.,  21., np.nan,  29.,  32.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  12.,  16., np.nan,  20.,  27.],
        [  0.,  10.,  11.,  14.,  15.,  17.],
        [  0.,  14., np.nan,  24.,  28., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  15.,  19.,  33., np.nan,  39.],
        [  0.,  19.,  25.,  26.,  33.,  38.],
        [np.nan,   9.,  13.,  15.,  33.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,   9.,  11.,  15., np.nan,  29.],
        [  0.,  15.,  25.,  26.,  29.,  32.],
        [  0.,  15.,  17.,  22.,  31.,  34.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  27.,  32.,  33.,  38.],
        [  0.,  10.,  16., np.nan,  26.,  30.],
        [  0.,  10.,  12.,  27.,  30.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  22.,  34.,  36.,  37.],
        [  0.,  12.,  15., np.nan,  28.,  36.],
        [  0., np.nan,  24.,  34.,  37.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  11.,  20.,  25., np.nan,  38.],
        [  0.,  20.,  34., np.nan,  36.,  41.],
        [np.nan,  16.,  20.,  30.,  32.,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  15., np.nan,  31.,  34.,  35.],
        [  0.,  13., np.nan,  20.,  33.,  38.],
        [  0.,  19.,  23.,  26.,  37., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  13.,  18.,  35.,  38.,  39.],
        [  0.,  12.,  20.,  29.,  37.,  38.],
        [  0.,  14., np.nan,  25., np.nan,  42.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  31.,  33.,  37.,  40.],
        [  0.,  11.,  13., np.nan,  25.,  32.],
        [  0.,  11., np.nan,  31.,  33.,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  10.,  15.,  18.,  20.,  26.],
        [  0.,  12.,  23.,  27.,  30.,  31.],
        [  0.,  11.,  18.,  24.,  34.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  30., np.nan,  36.,  39.,  41.],
        [np.nan,  10.,  28.,  33.,  37.,  44.],
        [  0.,  18.,  24.,  31., np.nan,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  17.,  21., np.nan,  29.,  36.],
        [  0.,  12., np.nan,  27.,  33., np.nan],
        [  0.,   8.,  18.,  23.,  32.,  34.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  13.,  18.,  24.,  26.,  34.],
        [  0.,  18., np.nan,  21.,  34.,  39.],
        [  0.,  12.,  14.,  23.,  25., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  20.,  26., np.nan,  32.,  35.],
        [np.nan,  21.,  22.,  24.,  26.,  29.],
        [  0., np.nan,  22.,  27.,  28.,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  15.,  20.,  22.,  25.,  30.],
        [  0.,  18.,  30.,  31.,  36.,  38.],
        [np.nan,   9.,  21.,  33., np.nan, np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,  15., np.nan,  22.,  23.,  42.],
        [  0.,   7.,  13., np.nan,  29.,  33.],
        [  0.,  11.,  24.,  31.,  37.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   9.,  10.,  12.,  16.,  41.],
        [np.nan,  17.,  20.,  22.,  30., np.nan],
        [  0.,  13.,  20.,  23., np.nan,  36.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,   9.,  23.,  30.,  32., np.nan],
        [np.nan,  11.,  17.,  21., np.nan,  43.],
        [  0.,  21.,  22.,  26.,  29.,  38.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  14.,  17.,  28.,  35.,  38.],
        [  0.,  22.,  26., np.nan,  32.,  38.],
        [np.nan,  11.,  15.,  24.,  28., np.nan]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  10.,  14., np.nan,  22.,  33.],
        [  0.,  23.,  28.,  32.,  37.,  42.],
        [  0.,  22.,  27.,  28., np.nan,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0., np.nan,  20., np.nan,  36.,  37.],
        [  0.,  16.,  17.,  30.,  33.,  38.],
        [  0., np.nan,  11.,  12.,  23.,  28.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  21.,  23.,  24.,  26.,  35.],
        [  0.,  19.,  26., np.nan, np.nan,  35.],
        [  0., np.nan,  26.,  29.,  30.,  33.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  11.,  16.,  20., np.nan, np.nan],
        [  0.,  23.,  24.,  30.,  37.,  42.],
        [np.nan,  20.,  25.,  27.,  37.,  39.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[np.nan,   9., np.nan,  26.,  34.,  35.],
        [np.nan,  21.,  29.,  32.,  34.,  38.],
        [  0.,  27.,  28.,  31.,  35.,  37.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)

dp_dict = { 'gain': np.matrix([[  0.,  14.,  17., np.nan,  36.,  44.],
        [  0.,  21.,  25.,  27.,  30.,  36.],
        [np.nan,  19.,  21.,  28., np.nan,  34.]], dtype=np.float),
    "total_resource":6,
    "decision_set":[0, 1, 2, 3, 4, 5],
    "opt_type": "max",
    "allow_non_allocated_resource":False,
}
dp_dict['project_list'] = PROJECT_LIST
dp_list.append(dp_dict)



import pickle
#import dill as pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(dp_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    dp_list_loaded = pickle.load(f)

#print len(dp_list_loaded)
for i, dp_dict in enumerate(dp_list_loaded):

    dp = ResourceAllocationDP(
        **dp_dict
    )

    selected_data_bytes = BytesIO()
    pickle.dump(dp_dict, selected_data_bytes)

    question_data = b64encode(selected_data_bytes.getvalue()).decode()

    #print question_data

    a = "KGRwMApTJ3Byb2plY3RfbGlzdCcKcDEKKGxwMgpWXHU1ZTdmXHU1ZGRlCnAzCmFWXHU2ZGYxXHU1NzMzCnA0CmFWXHU3M2UwXHU2ZDc3CnA1CmFzUyd0b3RhbF9yZXNvdXJjZScKcDYKSTYKc1Mnb3B0X3R5cGUnCnA3ClMnbWF4JwpwOApzUydhbGxvd19ub25fYWxsb2NhdGVkX3Jlc291cmNlJwpwOQpJMDAKc1MnZ2FpbicKcDEwCmNudW1weS5jb3JlLm11bHRpYXJyYXkKX3JlY29uc3RydWN0CnAxMQooY251bXB5Lm1hdHJpeGxpYi5kZWZtYXRyaXgKbWF0cml4CnAxMgooSTAKdHAxMwpTJ2InCnAxNAp0cDE1ClJwMTYKKEkxCihJMwpJNgp0cDE3CmNudW1weQpkdHlwZQpwMTgKKFMnZjgnCnAxOQpJMApJMQp0cDIwClJwMjEKKEkzClMnPCcKcDIyCk5OTkktMQpJLTEKSTAKdHAyMwpiSTAwClMnXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwXHgwMDFAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDA7QFx4MDBceDAwXHgwMFx4MDBceDAwXHg4MENAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDAsQFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMDhAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwPUBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBCQFx4MDBceDAwXHgwMFx4MDBceDAwXHg4MERAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDAsQFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMDtAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwP0BceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBBQFx4MDBceDAwXHgwMFx4MDBceDAwXHg4MEJAJwpwMjQKdHAyNQpic1MnZGVjaXNpb25fc2V0JwpwMjYKKGxwMjcKSTAKYUkxCmFJMgphSTMKYUk0CmFJNQphcy4="

    if question_data == a:
        print repr(dp_dict)

    result_force_calculate_feasible_state = dp.solve(allow_state_func=force_calculate_feasible_state)
    result = dp.solve()
    #print result_force_calculate_feasible_state
    #print result

    if len(result.policy) > 3:
        print repr(dp_dict)
        break
        continue

    #result = dp.solve()

    x_dict = result_force_calculate_feasible_state.verbose_state_x_dict
    first_multiple_stage=None
    first_multiple_result_state=None
    first_multiple_result_x = None
    for stage, stage_dict in x_dict.items():
        # if stage == 1:
        #     continue
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

    question_template = latex_jinja_env.get_template('dp_resource_allocation_2.tex')
    blank_template = latex_jinja_env.get_template('dp_resource_allocation_2_blank.tex')
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

    answer_tex = answer_template.render(
        answer_table_iters=iter(range(1,50)),
        show_question=True,
        show_answer_explanation=True,
        show_blank=True,
        show_blank_answer=True,
        dp=dp,
        dp_result_list=result_list,
        result=result,
        blank1_desc = u"最高的总收益为",
        blank2_desc = u"可能的最优策略的个数为",
        blank3_desc = u"以广州、深圳、珠海分别作为分配车辆的第1、2、3阶段时（下同），一个最优策略为（如有多个可只列出一个）",
        show_blank4 = show_blank4,
        blank4_desc = blank4_desc,
        blank4_result = blank4_result
    )

    r.clipboard_append(answer_tex)

    blank_tex = blank_template.render(
        answer_table_iters=iter(range(1,50)),
        show_question=True,
        show_answer_explanation=True,
        show_blank=True,
        show_blank_answer=True,
        dp=dp,
        dp_result_list=result_list,
        result=result,
        blank1_desc = u"最高的总收益为",
        blank2_desc = u"可能的最优策略的个数为",
        blank3_desc = u"以广州、深圳、珠海分别作为分配车辆的第1、2、3阶段时（下同），一个最优策略为（如有多个可只列出一个）",
        show_blank4 = show_blank4,
        blank4_desc = blank4_desc,
        blank4_result = blank4_result
    )

    r.clipboard_append(blank_tex)

    solve_tex = question_template.render(
        answer_table_iters=iter(range(1, 50)),
        show_answer_explanation=True,
        dp=dp,
        dp_result_list=result_list,
    )
    r.clipboard_append(question_tex + solve_tex)

