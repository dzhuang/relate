# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.transportation import transportation
import numpy as np
import random
try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
    from Tkinter import Tk


SAVED_QUESTION = "transport_balanced_vogel.bin"
MAX_RETRY_ITERATION = 10


def is_qualified_question(tr, saved_question=SAVED_QUESTION):
    required_init_method = tr.pop("required_init_method", None)
    used_method_list = [
        "NCM",
        "LCM",
        "VOGEL"
    ]

    with open(saved_question, 'rb') as f:
        transport_dict_list_loaded = pickle.load(f)

    t = transportation(**tr)

    method_result_list = []
    if "NCM" in used_method_list:
        NCM_result = t.solve(init_method="NCM")
        method_result_list.append(NCM_result)
    if "LCM" in used_method_list:
        LCM_result = t.solve(init_method="LCM")
        method_result_list.append(LCM_result)
    if "VOGEL" in used_method_list:
        VOGEL_result = t.solve(init_method="VOGEL")
        method_result_list.append(VOGEL_result)

    # count_vogel 产销平衡，Vogel >2 <=4 求解有退化，最后无退化

    # criteria:
    suggested_method = []
    qualified = False

    assert t.is_standard_problem

    if (t.is_standard_problem
        and not (
                NCM_result.final_is_degenerated_solution or LCM_result.final_is_degenerated_solution or VOGEL_result.final_is_degenerated_solution)
        ):

        # if (len(NCM_result.solution_list) in range(3, 5)
        #     and
        #         (NCM_result.has_degenerated_mid_solution or NCM_result.has_degenerated_init_solution)
        #     ):
        #     qualified = True
        #     suggested_method.append("NCM")
        #
        # lcm_ratio_qualified = False
        # if (len(LCM_result.solution_list) in range(3, 5)
        #     and
        #         (LCM_result.has_degenerated_mid_solution or LCM_result.has_degenerated_init_solution)
        #     ):
        #     suggested_method.append("LCM")
        #     a = random.uniform (0, 1)
        #     qualified = True
        #     if a < 0.05:
        #         lcm_ratio_qualified = True

        if (len(VOGEL_result.solution_list) in range(2, 4)
            and
                (VOGEL_result.has_degenerated_mid_solution or VOGEL_result.has_degenerated_init_solution)
            ):
            qualified = True
            suggested_method.append("VOGEL")

    #print qualified

    if not qualified:
        # 问题不合格
        return False

    tr["required_init_method"] = suggested_method

    #ori_len = len(transport_dict_list_loaded)
    #transport_dict_list_loaded.append(tr)
    question_exist = False
    for i, d in enumerate(transport_dict_list_loaded):
        if np.all(tr["costs"] == d["costs"]):
            if tr["dem"] == d["dem"] and tr["sup"] == d["sup"]:
                d_method = d.get("required_init_method", None)
                if not tr["required_init_method"] == d_method:
                    print tr
                    print suggested_method
                    transport_dict_list_loaded.pop(i)
                    with open(SAVED_QUESTION, 'wb') as f:
                        pickle.dump(transport_dict_list_loaded, f)
                    r.clipboard_clear()
                    r.clipboard_append("'required_init_method': %s" % str(suggested_method))
                    raise ValueError("Existing question with same costs does not have qualified method")
                print "----------------------question exists-------------------"
                question_exist = True

    if not question_exist:
        suggestion = "tr_dict=%s" % str(tr)
        suggestion = suggestion.replace("matrix", "np.matrix")
        print suggestion
        r.clipboard_clear()
        r.clipboard_append(suggestion)
        r.clipboard_append("\n")
        r.clipboard_append("transport_dict_list.append(tr_dict)")
        raise ValueError("Please add above problem")

    print tr
    print "dem:", t.surplus_dem, ", sup:", t.surplus_sup
    if t.is_standard_problem:
        print "标准化问题"
    elif t.is_sup_bounded_problem:
        if t.is_infinity_bounded_problem:
            print "供应无上限的有下限要求的问题"
        elif t.is_sup_bounded_problem:
            print "供应有下限要求的问题"
    elif t.is_dem_bounded_problem:
        if t.is_infinity_bounded_problem:
            print "需求无上限的有下限要求的问题"
        elif t.is_dem_bounded_problem:
            print "需求有下限要求的问题"
    else:
        print "产销不平衡问题"
    if NCM_result:
        print u"西北角法：迭代次数", len(NCM_result.solution_list), \
            u"初始化时有退化解：", NCM_result.has_degenerated_init_solution, \
            u"计算中有退化解：", NCM_result.has_degenerated_mid_solution, \
            u"最优解唯一：", NCM_result.has_unique_solution, \
            u"最优解退化：", NCM_result.final_is_degenerated_solution, \
            u"z", NCM_result.z
    if LCM_result:
        print u"最小元素法：迭代次数", len(LCM_result.solution_list), \
            u"初始化时有退化解：", LCM_result.has_degenerated_init_solution, \
            u"计算中有退化解：", LCM_result.has_degenerated_mid_solution, \
            u"最优解唯一：", LCM_result.has_unique_solution, \
            u"最优解退化：", LCM_result.final_is_degenerated_solution, \
            u"z", LCM_result.z
    if VOGEL_result:
        print u"VOGEL法：迭代次数", len(VOGEL_result.solution_list), \
            u"初始化时有退化解：", VOGEL_result.has_degenerated_init_solution, \
            u"计算中有退化解：", VOGEL_result.has_degenerated_mid_solution, \
            u"最优解唯一：", VOGEL_result.has_unique_solution, \
            u"最优解退化：", VOGEL_result.final_is_degenerated_solution, \
            u"z", VOGEL_result.z

    return True

transport_dict_list = []


tr_dict={'costs': np.matrix([[ 8,  8,  8, 10],
        [ 5,  4,  7,  3],
        [ 2,  7,  6,  6]]), 'required_init_method': ['VOGEL'], 'dem': [20, 18, 25, 37], 'sup': [25, 25, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 8,  7,  6,  4],
        [ 7,  5,  8, 10],
        [ 8,  2,  3,  6]]), 'required_init_method': ['VOGEL'], 'dem': [15, 20, 30, 35], 'sup': [25, 25, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[11,  9,  7,  7],
        [ 6,  8,  2,  8],
        [ 8,  4,  3,  8]]), 'required_init_method': ['VOGEL'], 'dem': [15, 20, 30, 35], 'sup': [25, 25, 50]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[ 2, 11,  8,  8],
        [ 8,  8,  4,  3],
        [ 7,  9,  7,  6]]), 'required_init_method': ['VOGEL'], 'dem': [15, 20, 30, 35], 'sup': [20, 30, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 5, 2, 4],
        [6, 1, 4, 6],
        [5, 6, 7, 3]]), 'required_init_method': ['VOGEL'], 'dem': [25, 25, 32, 38], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 4, 1, 5],
        [5, 4, 7, 2],
        [3, 6, 6, 3]]), 'required_init_method': ['VOGEL'], 'dem': [30, 30, 40, 20], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 4, 4, 6],
        [5, 3, 6, 2],
        [1, 6, 5, 3]]), 'required_init_method': ['VOGEL'], 'dem': [28, 39, 31, 22], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 6, 8, 5],
        [4, 3, 4, 4],
        [2, 4, 2, 3]]), 'required_init_method': ['VOGEL'], 'dem': [80, 100, 60, 20], 'sup': [90, 90, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 5, 4, 5],
        [3, 8, 2, 4],
        [2, 6, 3, 4]]), 'required_init_method': ['VOGEL'], 'dem': [80, 100, 60, 20], 'sup': [90, 90, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 6, 12,  3,  4],
        [10,  8,  4, 11],
        [ 7,  5,  2,  4]]), 'required_init_method': ['VOGEL'], 'dem': [8, 14, 12, 24], 'sup': [16, 20, 22]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[10,  4,  3, 11],
        [ 4,  5,  2,  8],
        [12,  7,  4,  6]]), 'required_init_method': ['VOGEL'], 'dem': [8, 14, 12, 24], 'sup': [16, 20, 22]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 4, 5, 2],
        [6, 5, 3, 5],
        [4, 7, 4, 8]]), 'required_init_method': ['VOGEL'], 'dem': [40, 60, 60, 80], 'sup': [100, 60, 80]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[4, 2, 5, 6],
        [7, 4, 3, 5],
        [3, 4, 5, 8]]), 'required_init_method': ['VOGEL'], 'dem': [40, 60, 60, 80], 'sup': [100, 60, 80]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[ 7,  8,  4],
        [ 8, 12,  5],
        [10,  6,  6],
        [ 9, 10,  2]]), 'required_init_method': ['VOGEL'], 'dem': [32, 40, 40], 'sup': [25, 30, 42, 15]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[12,  8,  6],
        [ 4,  2,  5],
        [ 8,  6,  7],
        [10,  9, 10]]), 'required_init_method': ['VOGEL'], 'dem': [32, 40, 40], 'sup': [25, 30, 42, 15]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 2, 2, 5],
        [3, 4, 3, 2],
        [1, 3, 5, 3]]), 'required_init_method': ['VOGEL'], 'dem': [10, 20, 35, 25], 'sup': [20, 30, 40]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 3, 2, 3],
        [1, 3, 5, 4],
        [3, 6, 2, 5]]), 'required_init_method': ['VOGEL'], 'dem': [11, 35, 24, 20], 'sup': [20, 30, 40]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 2, 3, 2],
        [3, 5, 2, 5],
        [3, 4, 6, 1]]), 'required_init_method': ['VOGEL'], 'dem': [10, 20, 35, 25], 'sup': [20, 30, 40]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 2, 3, 4],
        [5, 5, 3, 2],
        [2, 4, 1, 3]]), 'required_init_method': ['VOGEL'], 'dem': [51, 41, 45, 48], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 3, 2, 2],
        [3, 3, 4, 3],
        [2, 4, 1, 5]]), 'required_init_method': ['VOGEL'], 'dem': [45, 40, 39, 61], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 1, 6, 3],
        [4, 2, 3, 2],
        [3, 2, 6, 5]]), 'required_init_method': ['VOGEL'], 'dem': [19, 15, 10, 16], 'sup': [15, 25, 20]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 5, 2, 6],
        [3, 5, 6, 2],
        [1, 4, 2, 3]]), 'required_init_method': ['VOGEL'], 'dem': [20, 11, 16, 13], 'sup': [15, 25, 20]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[11,  9,  3, 10],
        [ 7,  7,  6, 15],
        [ 8,  6, 12,  8]]), 'required_init_method': ['VOGEL'], 'dem': [20, 35, 25, 30], 'sup': [40, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 8,  7,  9, 15],
        [12, 10,  6,  3],
        [ 7,  8, 11,  6]]), 'required_init_method': ['VOGEL'], 'dem': [22, 25, 33, 30], 'sup': [31, 33, 46]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 5, 2, 4],
        [5, 6, 5, 4],
        [4, 6, 3, 7]]), 'required_init_method': ['VOGEL'], 'dem': [35, 20, 15, 25], 'sup': [35, 20, 40]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 7, 6, 4],
        [2, 3, 5, 5],
        [4, 5, 6, 3]]), 'required_init_method': ['VOGEL'], 'dem': [28, 29, 32, 6], 'sup': [38, 32, 25]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[5, 3, 3, 4],
        [6, 4, 8, 7],
        [6, 6, 4, 5]]), 'required_init_method': ['VOGEL'], 'dem': [4, 10, 8, 2], 'sup': [8, 12, 4]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 3, 6, 3],
        [4, 4, 8, 5],
        [6, 5, 6, 4]]), 'required_init_method': ['VOGEL'], 'dem': [8, 5, 4, 7], 'sup': [5, 9, 10]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 5, 3, 8],
        [4, 6, 5, 4],
        [7, 6, 3, 4]]), 'required_init_method': ['VOGEL'], 'dem': [4, 10, 8, 2], 'sup': [8, 12, 4]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 4, 3, 2],
        [6, 5, 4, 6],
        [3, 4, 2, 3]]), 'required_init_method': ['VOGEL'], 'dem': [50, 23, 26, 86], 'sup': [43, 66, 76]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 4, 2, 5],
        [4, 3, 2, 6],
        [6, 4, 5, 3]]), 'required_init_method': ['VOGEL'], 'dem': [55, 59, 17, 54], 'sup': [72, 75, 38]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[ 6,  7,  4, 10],
        [ 3, 11,  7,  5],
        [ 1,  2,  4,  3]]), 'required_init_method': ['VOGEL'], 'dem': [5, 12, 9, 13], 'sup': [8, 14, 17]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[12,  6,  7,  9],
        [14, 12, 10,  8],
        [ 8,  5, 10, 10]]), 'required_init_method': ['VOGEL'], 'dem': [30, 70, 20, 20], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[10, 14,  8,  7],
        [12, 10,  5,  9],
        [ 6,  8, 10, 12]]), 'required_init_method': ['VOGEL'], 'dem': [41, 50, 24, 25], 'sup': [41, 58, 41]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[12,  9,  7, 10],
        [10, 14,  8, 12],
        [ 5, 10,  8,  6]]), 'required_init_method': ['VOGEL'], 'dem': [30, 70, 15, 25], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[12,  8, 10,  6],
        [ 9, 14,  8, 12],
        [ 5, 10, 10,  7]]), 'required_init_method': ['VOGEL'], 'dem': [30, 70, 15, 25], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[12,  7,  8, 14],
        [10, 10, 12,  9],
        [ 8,  5,  6, 10]]), 'required_init_method': ['VOGEL'], 'dem': [30, 65, 20, 25], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9, 14, 10,  8],
        [10,  7, 12, 10],
        [ 6,  5,  8, 12]]), 'required_init_method': ['VOGEL'], 'dem': [30, 65, 20, 25], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[ 5, 12,  8,  7],
        [10, 14,  8,  9],
        [ 6, 11, 10, 10]]), 'required_init_method': ['VOGEL'], 'dem': [30, 65, 20, 25], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 3, 2, 4],
        [1, 6, 2, 6],
        [2, 2, 5, 3]]), 'required_init_method': ['VOGEL'], 'dem': [70, 60, 70, 10], 'sup': [60, 70, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 1, 2, 2],
        [2, 4, 5, 6],
        [3, 2, 3, 3]]), 'required_init_method': ['VOGEL'], 'dem': [46, 30, 39, 95], 'sup': [69, 70, 71]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[4, 2, 3, 6],
        [2, 3, 1, 2],
        [3, 6, 5, 2]]), 'required_init_method': ['VOGEL'], 'dem': [39, 19, 62, 90], 'sup': [62, 62, 86]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 2, 1, 3],
        [5, 6, 2, 3],
        [4, 2, 6, 2]]), 'required_init_method': ['VOGEL'], 'dem': [60, 55, 85, 10], 'sup': [60, 65, 85]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 2, 6, 4],
        [3, 2, 6, 2],
        [1, 3, 3, 2]]), 'required_init_method': ['VOGEL'], 'dem': [60, 55, 85, 10], 'sup': [60, 65, 85]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 4, 2, 5],
        [4, 7, 5, 1],
        [6, 7, 5, 2]]), 'required_init_method': ['VOGEL'], 'dem': [33, 45, 11, 41], 'sup': [45, 31, 54]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 8, 6, 5],
        [2, 4, 3, 2],
        [7, 4, 5, 5]]), 'required_init_method': ['VOGEL'], 'dem': [65, 75, 23, 47], 'sup': [67, 70, 73]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 2, 4, 8],
        [2, 5, 7, 6],
        [5, 3, 3, 4]]), 'required_init_method': ['VOGEL'], 'dem': [48, 59, 36, 67], 'sup': [65, 78, 67]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 5, 3, 5],
        [3, 6, 2, 4],
        [4, 8, 7, 4]]), 'required_init_method': ['VOGEL'], 'dem': [51, 27, 21, 116], 'sup': [72, 74, 69]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[8, 4, 2, 3],
        [5, 7, 3, 2],
        [6, 4, 4, 5]]), 'required_init_method': ['VOGEL'], 'dem': [77, 28, 72, 38], 'sup': [77, 77, 61]}
transport_dict_list.append(tr_dict)


# ## 有退化解，检验数为0，基本可行方案不唯一，但去掉0之后的基本可行方案是唯一的.
# tr_dict = {
#     "sup": [
#         80, 65, 60
#     ],
#     "dem": [
#         50, 80, 60, 15
#     ],
#     "costs": np.matrix ([
#         4, 2, 3, 2,
#         3, 8, 6, 4,
#         4, 5, 5, 6,
#     ]).reshape(3,4),
# }
# transport_dict_list.append(tr_dict)
#

tr_dict={'costs': np.matrix([[2, 6, 3, 4],
        [3, 3, 3, 5],
        [2, 1, 4, 2]]), 'required_init_method': ['VOGEL'], 'dem': [49, 38, 10, 33], 'sup': [45, 47, 38]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 1, 5, 2],
        [3, 4, 3, 2],
        [3, 3, 6, 2]]), 'required_init_method': ['VOGEL'], 'dem': [30, 40, 50, 10], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 2, 3, 2],
        [4, 3, 2, 6],
        [1, 5, 3, 3]]), 'required_init_method': ['VOGEL'], 'dem': [21, 40, 30, 39], 'sup': [40, 43, 47]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 1, 3, 3],
        [5, 2, 2, 6],
        [2, 3, 4, 4]]), 'required_init_method': ['VOGEL'], 'dem': [30, 38, 20, 42], 'sup': [38, 50, 42]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 5, 3, 3],
        [6, 3, 1, 2],
        [2, 2, 3, 4]]), 'required_init_method': ['VOGEL'], 'dem': [40, 29, 35, 26], 'sup': [44, 46, 40]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 6, 3, 3],
        [3, 1, 4, 2],
        [3, 2, 5, 4]]), 'required_init_method': ['VOGEL'], 'dem': [26, 33, 27, 44], 'sup': [47, 50, 33]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 6, 3, 3],
        [3, 3, 2, 5],
        [4, 2, 2, 1]]), 'required_init_method': ['VOGEL'], 'dem': [36, 33, 40, 21], 'sup': [42, 36, 52]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 3, 1, 4],
        [3, 2, 2, 5],
        [2, 6, 3, 3]]), 'required_init_method': ['VOGEL'], 'dem': [30, 40, 35, 25], 'sup': [45, 55, 30]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[5, 8, 5, 3],
        [7, 6, 7, 4],
        [4, 6, 4, 6]]), 'required_init_method': ['VOGEL'], 'dem': [52, 32, 41, 55], 'sup': [55, 61, 64]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 6, 6, 3],
        [4, 5, 7, 6],
        [4, 5, 8, 7]]), 'required_init_method': ['VOGEL'], 'dem': [53, 50, 57, 20], 'sup': [58, 57, 65]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 8, 5, 3],
        [5, 5, 4, 2],
        [3, 4, 9, 7]]), 'required_init_method': ['VOGEL'], 'dem': [50, 80, 70, 10], 'sup': [90, 70, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 5, 5, 9],
        [4, 3, 8, 6],
        [3, 4, 2, 5]]), 'required_init_method': ['VOGEL'], 'dem': [45, 17, 52, 96], 'sup': [62, 88, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 9, 4, 5],
        [4, 3, 2, 7],
        [5, 5, 8, 6]]), 'required_init_method': ['VOGEL'], 'dem': [68, 46, 79, 17], 'sup': [64, 61, 85]}
transport_dict_list.append(tr_dict)


r = Tk()
r.withdraw()
r.clipboard_clear()

import pickle
#import dill as pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(transport_dict_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    transport_dict_list_loaded = pickle.load(f)

INIT_METHOD_DICT = {"LCM": u"最小元素法", "NCM": u"西北角法", "VOGEL": u"伏格尔法"}

def random_int_list_fixed_sum(l, l_min, l_max):
    l_len = len(l)
    l_sum = sum(l)
    new_list = []
    for i in range(l_len - 1):
        new_list.append(int(round(random.uniform(l_min, l_max))))
    new_list.append(l_sum-sum(new_list))
    return new_list

# 产销平衡，Vogel法 >=2 求解有退化，最后无退化
count_vogel = 0
count_vogel_list = []

for i, tr in enumerate(transport_dict_list_loaded):
    required_init_method = tr.get("required_init_method", None)
    success = False

    if is_qualified_question(tr):
        print "i", i
        if required_init_method:
            assert isinstance(required_init_method, list)
            assert set(required_init_method).issubset(set(["LCM", "NCM", "VOGEL"]))
        else:
            print tr
            raise ValueError(u"未指定方法:", tr)

        count_vogel += 1
    else:

        print tr

        costs = tr["costs"]
        #print costs
        n, m = costs.shape
        cost_list = costs.reshape([1, n*m]).tolist()[0]
        cost_min = min(cost_list)
        cost_max = max(cost_list)
        sup = tr["sup"]
        dem = tr["dem"]
        dem_min = min(dem)
        dem_max = max(dem)
        sup_min = min(sup)
        sup_max = max(sup)

        #print n, m
        it = 0
        inner_it = 0
        while it < MAX_RETRY_ITERATION:
            it += 1
            # print("%d-%d" % (inner_it, it))
            random.shuffle(cost_list)
            # print cost_list
            new_cost = np.matrix(cost_list).reshape([n, m])
            tr["costs"] = new_cost
            tr["sup"] = sup
            tr["dem"] = dem
            # if inner_it==0 and it == 100:
            #     print tr
            # if inner_it==1 and it == 1:
            #     print tr
            #     break
            if is_qualified_question(tr):
                print tr
                success = True
                break
            if inner_it < MAX_RETRY_ITERATION*10:
                if it == MAX_RETRY_ITERATION:
                    print tr
                    inner_it += 1
                    print inner_it
                    sup = random_int_list_fixed_sum(sup, sup_min, sup_max)
                    dem = random_int_list_fixed_sum(dem, dem_min, dem_max)
                    it = 0
            # elif inner_it == MAX_RETRY_ITERATION/100:
            #     if innerest_it < MAX_RETRY_ITERATION:
            #         innerest_it += 1
            #         inner_it = 0
            #         cost_list = [int(round(random.uniform(1, 15))) for i in range(n*m)]


        if it == MAX_RETRY_ITERATION:
            raise ValueError("Failed to create problem")

    t = transportation(**tr)

#    r.clipboard_clear ()

    #required_init_method = ["LCM", "NCM", "VOGEL"]
    required_init_method = tr.get("required_init_method")


    show_LCM_result = True
    show_NCM_result = True
    show_VOGEL_result = True

    # show_LCM_result = False
    # show_NCM_result = False
    # show_VOGEL_result = False

    if "LCM" in required_init_method:
        show_LCM_result = True
    elif "NCM" in required_init_method:
        show_NCM_result = True
    elif "VOGEL" in required_init_method:
        show_VOGEL_result = True

    used_method_list = required_init_method
    # if not required_init_method:
    # used_method_list = [
    #     "NCM",
    #     "LCM",
    #     "VOGEL"
    # ]

    method_result_list = []
    if "NCM" in used_method_list:
        NCM_result = t.solve(init_method="NCM")
        method_result_list.append(NCM_result)
    if "LCM" in used_method_list:
        LCM_result = t.solve(init_method="LCM")
        method_result_list.append(LCM_result)
    if "VOGEL" in used_method_list:
        VOGEL_result = t.solve(init_method="VOGEL")
        method_result_list.append(VOGEL_result)

    template = latex_jinja_env.get_template('/utils/transportation.tex')

    tex = template.render(
        question_table_iters=iter(range(1, 5)),
        answer_table_iters=iter(range(1, 100)),
        show_question=True,
        show_answer=True,
        # problem_description_pre = u"""
        #             设有产量分别为30，40，30的三个原料产地，欲将原材料运往销量分别为
        #             25，20，40的三个销地，单位运价如下表所示。试求总运费最省的调运方案。""",
        t=t,
        #        LCM_result = LCM_result,
        #        NCM_result = NCM_result,
        #        VOGEL_result = VOGEL_result,
        method_result_list=method_result_list,
        show_LCM_result=show_LCM_result,
        show_NCM_result=show_NCM_result,
        show_VOGEL_result=show_VOGEL_result,
        standardize_only=False,
        init_method_list=[INIT_METHOD_DICT.get(method, None) for method in required_init_method],
        used_method_list=[INIT_METHOD_DICT.get(used_method) for used_method in used_method_list],
    )

    r.clipboard_append(tex)


print success
print "count_vogel:", count_vogel

# with open(SAVED_QUESTION, 'wb') as f:
#     pickle.dump(transport_dict_list, f)