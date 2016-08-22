# -*- coding: utf-8 -*-

# 产销平衡，(西北角>2 <=3 or 最小元素>2 <=3) 求解有退化，最后无退化

from utils.latex_utils import latex_jinja_env, _file_write
from utils.transportation import transportation
import numpy as np
import random
from Tkinter import Tk


SAVED_QUESTION = "transport_count1.bin"


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

    # count1 产销平衡，(西北角>2 <=3 or 最小元素>2 <=3) 求解有退化，最后无退化

    # criteria:
    suggested_method = []
    qualified = False

    assert t.is_standard_problem

    if (t.is_standard_problem
        and not (
                NCM_result.final_is_degenerated_solution or LCM_result.final_is_degenerated_solution or VOGEL_result.final_is_degenerated_solution)
        and
            (NCM_result.has_degenerated_mid_solution or LCM_result.has_degenerated_mid_solution or NCM_result.has_degenerated_init_solution or NCM_result.has_degenerated_init_solution)
        ):

        if (len(NCM_result.solution_list) in range(3, 5)
            and
                (NCM_result.has_degenerated_mid_solution or NCM_result.has_degenerated_init_solution)
            ):
            qualified = True
            suggested_method.append("NCM")

        lcm_ratio_qualified = False
        if (len(LCM_result.solution_list) in range(3, 5)
            and
                (LCM_result.has_degenerated_mid_solution or LCM_result.has_degenerated_init_solution)
            ):
            suggested_method.append("LCM")
            a = random.uniform (0, 1)
            qualified = True
            if a < 0.05:
                lcm_ratio_qualified = True


        # if (len(VOGEL_result.solution_list) in range(3, 4)
        #     and
        #         (VOGEL_result.has_degenerated_mid_solution or VOGEL_result.has_degenerated_init_solution)
        #     ):
        #     qualified = True
        #     suggested_method.append("VOGEL")

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
                if not tr["required_init_method"] == d["required_init_method"]:
                    print tr
                    print suggested_method
                    transport_dict_list_loaded.pop(i)
                    with open(SAVED_QUESTION, 'wb') as f:
                        pickle.dump(transport_dict_list_loaded, f)
                    raise ValueError("Existing question with same costs does not have qualified method")
                print "----------------------question exists-------------------"
                question_exist = True

    if not question_exist:
        if lcm_ratio_qualified:
            suggestion = "tr_dict=%s" % str(tr)
            suggestion = suggestion.replace("matrix", "np.matrix")
            print suggestion
            r = Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(suggestion)
            r.clipboard_append("\n")
            r.clipboard_append("transport_dict_list.append(tr_dict)")

            raise ValueError("Please add above problem")
        else:
            r = Tk ()
            r.withdraw ()
            r.clipboard_clear ()
            return False


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

tr_dict = {
    "sup": [
        100, 60, 50
    ],
    "dem": [
        40, 60, 70, 40
    ],
    "costs": np.matrix ([
        4, 3, 5, 4,
        6, 7, 8, 3,
        3, 2, 4, 5,
    ]).reshape(3,4),
    "required_init_method": ["NCM"]
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        100, 60, 50
    ],
    "dem": [
        40, 60, 65, 45
    ],
    "costs": np.matrix ([
        4, 3, 5, 4,
        6, 7, 8, 3,
        3, 2, 4, 5,
    ]).reshape(3,4),
    "required_init_method": ["NCM"]
}
transport_dict_list.append(tr_dict)

tr_dict = {
    'costs': np.matrix([[7, 5, 8, 5],
                      [6, 7, 4, 3],
                      [6, 3, 4, 3]]),
    'dem': [40, 60, 80, 30],
    'sup': [90, 60, 60],
    "required_init_method": ["LCM"]
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        25, 45, 50
    ],
    "dem": [
        30, 30, 40, 20
    ],
    "costs": np.matrix ([
        1, 6, 3, 2,
        3, 6, 4, 5,
        4, 5, 7, 6
    ]).reshape(3,4),
    "required_init_method": ['NCM', 'LCM']
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        100, 60, 80
    ],
    "dem": [
        40, 60, 60, 80
    ],
    "costs": np.matrix ([
        2, 5, 4, 5,
        3, 7, 6, 5,
        3, 4, 4, 8
    ]).reshape(3,4),
    "required_init_method": ['NCM', 'LCM']
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        40, 40, 30
    ],
    "dem": [
        20, 35, 25, 30
    ],
    "costs": np.matrix ([
        6, 3, 8, 7,
        11, 6, 15, 8,
        9, 7, 12, 10
    ]).reshape(3,4),
    "required_init_method": ['NCM']
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        45, 55, 30
    ],
    "dem": [
        30, 40, 35, 25
    ],
    "costs": np.matrix ([
        3, 2, 4, 3,
        2, 3, 5, 6,
        1, 4, 2, 3
    ]).reshape(3,4),
    "required_init_method": ['LCM']
}
transport_dict_list.append(tr_dict)

# tr_dict = {
#     "sup": [70, 120, 100],
#     "dem": [75, 60, 70],
#     "costs": np.matrix ([
#         8, 9, 12,
#         6, 7, 13,
#         18, 12, 6
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [70, 80, 90],
#     "dem": [60, 100, 50],
#     "costs": np.matrix ([
#         4, 6, 5,
#         2, 3, 8,
#         8, 7, 9
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [90, 70, 60],
#     "dem": [80, 100, 60],
#     "costs": np.matrix ([
#         4, 3, 5,
#         7, 4, 9,
#         6, 5, 7
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [70, 120, 100],
#     "dem": [75, 60, 70],
#     "costs": np.matrix ([
#         8, 9, 12,
#         6, 7, 13,
#         18, 12, 6
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
tr_dict={'costs': np.matrix([[10, 12,  8,  8],
        [ 8, 11,  9, 10],
        [18,  6,  9,  6]]), 'required_init_method': ['LCM'], 'dem': [75, 60, 70, 85], 'sup': [70, 120, 100]}
transport_dict_list.append(tr_dict)
#
#
#
tr_dict={'costs': np.matrix([[2, 3, 2, 2],
        [3, 1, 5, 3],
        [4, 4, 8, 6]]), 'required_init_method': ['NCM'], 'dem': [4, 7, 6, 2], 'sup': [5, 6, 8]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 4, 5],
        [9, 5, 8],
        [8, 5, 7],
        [6, 4, 6]]), 'required_init_method': ['LCM'], 'dem': [80, 100, 60], 'sup': [90, 70, 60, 20]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 5, 5],
        [8, 8, 6],
        [6, 4, 3],
        [7, 9, 4]]), 'required_init_method': ['LCM'], 'dem': [80, 100, 60], 'sup': [90, 70, 60, 20]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 4, 8, 9],
        [5, 6, 6, 8],
        [7, 2, 7, 3]]), 'required_init_method': ['LCM'], 'dem': [60, 100, 50, 30], 'sup': [70, 80, 90]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 5, 10,  5,  8],
        [ 9,  7,  4,  6],
        [ 9,  9,  8,  7]]), 'required_init_method': ['LCM'], 'dem': [25, 20, 40, 15], 'sup': [30, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 8, 10,  6,  5],
        [ 9,  7,  4,  7],
        [ 5,  9,  8,  9]]), 'required_init_method': ['LCM'], 'dem': [25, 20, 40, 15], 'sup': [30, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9,  4,  5,  7],
        [ 7,  8,  8, 10],
        [ 5,  9,  9,  6]]), 'required_init_method': ['NCM'], 'dem': [25, 20, 40, 15], 'sup': [30, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9,  7,  8,  8],
        [ 7,  6,  4,  9],
        [ 5, 10,  5,  9]]), 'required_init_method': ['LCM'], 'dem': [25, 20, 40, 15], 'sup': [30, 40, 30]}
transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [30, 40, 30],
#     "dem": [25, 20, 40],
#     "costs": np.matrix ([
#         5, 6, 9,
#         9, 4, 8,
#         10, 7, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#

tr_dict={'costs': np.matrix([[ 8,  6,  5,  8],
        [10,  3,  7,  7],
        [ 8,  2,  4,  6]]), 'required_init_method': ['LCM'], 'dem': [15, 20, 30, 35], 'sup': [25, 25, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 7,  2,  4,  5],
        [ 6,  8,  6,  8],
        [ 3,  8,  7, 10]]), 'required_init_method': ['LCM'], 'dem': [15, 20, 30, 35], 'sup': [25, 25, 50]}
transport_dict_list.append(tr_dict)

# tr_dict = {
#     "sup": [25, 25, 50],
#     "dem": [15, 20, 30],
#     "costs": np.matrix ([
#         10, 5, 6,
#         8, 2, 7,
#         8, 3, 4,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
tr_dict={'costs': np.matrix([[ 8,  8,  3,  4],
        [ 4, 11,  5,  4],
        [ 2, 10, 12,  5]]), 'required_init_method': ['LCM'], 'dem': [18, 14, 12, 4], 'sup': [16, 22, 10]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 5,  2,  3,  4],
        [ 4,  8,  5,  8],
        [10, 12,  4, 11]]), 'required_init_method': ['LCM'], 'dem': [18, 14, 12, 4], 'sup': [16, 22, 10]}
transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         90, 70, 50
#     ],
#     "dem": [
#         50, 80, 70
#     ],
#     "costs": np.matrix ([
#         4, 3, 5,
#         6, 7, 8,
#         5, 2, 9,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
#
# tr_dict = {
#     "sup": [
#         25, 45, 50
#     ],
#     "dem": [
#         30, 30, 40
#     ],
#     "costs": np.matrix ([
#         1, 6, 3,
#         3, 6, 4,
#         4, 5, 7
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
#
#

tr_dict={'costs': np.matrix([[4, 8, 3, 2],
        [4, 3, 5, 5],
        [4, 6, 4, 2]]), 'required_init_method': ['NCM'], 'dem': [80, 100, 60, 20], 'sup': [90, 90, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 3, 4, 5],
        [5, 3, 2, 4],
        [6, 2, 4, 8]]), 'required_init_method': ['NCM'], 'dem': [80, 100, 60, 20], 'sup': [90, 90, 80]}
transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         16, 20, 22
#     ],
#     "dem": [
#         8, 14, 12
#     ],
#     "costs": np.matrix ([
#         4, 12, 4,
#         2, 10, 3,
#         8, 5, 11
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
tr_dict={'costs': np.matrix([[11,  4, 10,  4],
        [12,  4,  5,  8],
        [ 6,  7,  3,  2]]), 'required_init_method': ['LCM'], 'dem': [8, 14, 12, 24], 'sup': [16, 20, 22]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 4,  4,  7,  3],
        [11, 10,  2,  4],
        [12,  8,  6,  5]]), 'required_init_method': ['LCM'], 'dem': [8, 14, 12, 24], 'sup': [16, 20, 22]}
transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         100, 60, 80
#     ],
#     "dem": [
#         40, 60, 60
#     ],
#     "costs": np.matrix ([
#         2, 5, 4,
#         3, 7, 6,
#         4, 2, 4
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
#
# tr_dict = {
#     "sup": [
#         25, 30, 42
#     ],
#     "dem": [
#         32, 40, 30
#     ],
#     "costs": np.matrix ([
#         6, 2, 5,
#         8, 12, 7,
#         4, 15, 8
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#

tr_dict={'costs': np.matrix([[ 6,  6,  4],
        [10,  2,  8],
        [ 9, 12,  7],
        [10,  8,  5]]), 'required_init_method': ['LCM'], 'dem': [32, 40, 40], 'sup': [25, 30, 42, 15]}

transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9,  2, 10],
        [ 8, 10,  5],
        [ 6,  7, 12],
        [ 6,  4,  8]]), 'required_init_method': ['LCM'], 'dem': [32, 40, 40], 'sup': [25, 30, 42, 15]}

transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         20, 30, 40
#     ],
#     "dem": [
#         10, 30, 30
#     ],
#     "costs": np.matrix ([
#         4, 2, 3,
#         3, 1, 6,
#         2, 3, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
tr_dict={'costs': np.matrix([[3, 2, 5, 5],
        [2, 3, 3, 4],
        [1, 2, 6, 3]]), 'required_init_method': ['NCM'], 'dem': [10, 20, 35, 25], 'sup': [20, 30, 40]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 2, 2, 6],
        [3, 4, 3, 2],
        [3, 3, 5, 1]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [10, 20, 35, 25], 'sup': [20, 30, 40]}
transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         60, 80, 45
#     ],
#     "dem": [
#         50, 45, 56
#     ],
#     "costs": np.matrix ([
#         2, 3, 4,
#         3, 5, 2,
#         4, 3, 1
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
tr_dict={'costs': np.matrix([[4, 3, 2, 5],
        [2, 3, 1, 3],
        [4, 2, 5, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 3, 2, 5],
        [2, 3, 1, 3],
        [4, 2, 5, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)
#
#

tr_dict={'costs': np.matrix([[3, 3, 4, 2],
        [3, 5, 4, 1],
        [5, 2, 2, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 3, 2, 4],
        [3, 2, 5, 4],
        [3, 1, 5, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

#
#
tr_dict={'costs': np.matrix([[3, 3, 4, 5],
        [3, 5, 1, 4],
        [3, 2, 2, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 3, 5, 4],
        [2, 4, 1, 5],
        [3, 2, 3, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

#
#
# tr_dict = {
#     "sup": [
#         40, 40, 30
#     ],
#     "dem": [
#         40, 45, 25
#     ],
#     "costs": np.matrix ([
#         6, 3, 8,
#         11, 6, 15,
#         9, 7, 12
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         18, 15, 19
#     ],
#     "dem": [
#         14, 13, 15
#     ],
#     "costs": np.matrix ([
#         3, 8, 3,
#         10, 12, 9,
#         5, 8, 9
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         25, 40, 30
#     ],
#     "dem": [
#         30, 35, 25
#     ],
#     "costs": np.matrix ([
#         6, 7, 4,
#         4, 5, 2,
#         7, 6, 3
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#

tr_dict={'costs': np.matrix([[2, 2, 1, 3],
        [3, 4, 5, 5],
        [4, 2, 3, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 3, 1, 5],
        [3, 3, 4, 3],
        [4, 2, 2, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         8, 12, 4
#     ],
#     "dem": [
#         4, 10, 8
#     ],
#     "costs": np.matrix ([
#         4, 3, 5,
#         6, 5, 4,
#         8, 6, 7
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#

tr_dict={'costs': np.matrix([[4, 2, 2, 5],
        [3, 4, 5, 3],
        [3, 1, 3, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[4, 2, 2, 5],
        [3, 2, 3, 4],
        [5, 1, 3, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[1, 3, 5, 4],
        [2, 4, 3, 5],
        [3, 2, 3, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 2, 5, 4],
        [5, 3, 3, 4],
        [2, 1, 3, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[4, 3, 5, 2],
        [2, 5, 4, 3],
        [3, 1, 2, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

#
#
# tr_dict = {
#     "sup": [
#         65, 40, 80
#     ],
#     "dem": [
#         50, 55, 63
#     ],
#     "costs": np.matrix ([
#         3, 2, 4,
#         2, 4, 6,
#         6, 5, 3,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
tr_dict={'costs': np.matrix([[4, 4, 1, 5],
        [2, 3, 2, 3],
        [2, 3, 3, 5]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 3, 2, 5],
        [2, 4, 3, 4],
        [3, 1, 5, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 5, 4, 3],
        [4, 3, 5, 1],
        [3, 2, 2, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)


#
#
# tr_dict = {
#     "sup": [
#         8, 14, 17
#     ],
#     "dem": [
#         5, 12, 9
#     ],
#     "costs": np.matrix ([
#         3, 11, 4,
#         1, 9, 2,
#         7, 4, 10,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#

tr_dict={'costs': np.matrix([[2, 4, 5, 3],
        [4, 3, 5, 2],
        [3, 1, 2, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 3, 3, 4],
        [1, 5, 4, 2],
        [5, 2, 3, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         50, 60, 30
#     ],
#     "dem": [
#         30, 70, 20
#     ],
#     "costs": np.matrix ([
#         10, 8, 12,
#         6, 10, 12,
#         7, 14, 10,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
tr_dict={'costs': np.matrix([[6, 4, 5, 7],
        [3, 3, 6, 5],
        [8, 7, 3, 4]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 8, 4, 7],
        [3, 5, 3, 7],
        [6, 6, 4, 3]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 3, 5, 3],
        [6, 4, 7, 4],
        [8, 7, 5, 3]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[8, 5, 6, 7],
        [3, 3, 7, 5],
        [6, 3, 4, 4]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)
#
#

tr_dict={'costs': np.matrix([[6, 7, 3, 7],
        [3, 3, 4, 6],
        [8, 5, 5, 4]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 6, 3, 8],
        [4, 3, 5, 6],
        [7, 5, 3, 4]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 6, 3, 7],
        [3, 5, 7, 4],
        [5, 8, 4, 3]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

#
tr_dict={'costs': np.matrix([[3, 6, 3, 7],
        [5, 3, 6, 5],
        [8, 4, 7, 4]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 5, 3, 4],
        [6, 5, 7, 8],
        [7, 4, 3, 3]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 8, 6, 7],
        [3, 4, 6, 3],
        [5, 5, 4, 3]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

#
#
# tr_dict = {
#     "sup": [
#         60, 70, 80
#     ],
#     "dem": [
#         70, 60, 70
#     ],
#     "costs": np.matrix ([
#         2, 3, 2,
#         4, 1, 3,
#         6, 2, 6
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#


tr_dict={'costs': np.matrix([[6, 3, 4, 5],
        [3, 3, 8, 5],
        [7, 7, 6, 4]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 3, 5, 8],
        [4, 3, 7, 6],
        [3, 7, 4, 5]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 6, 5, 4],
        [3, 6, 7, 7],
        [3, 8, 5, 3]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 5, 2, 4],
        [3, 2, 3, 4],
        [3, 1, 5, 2]]), 'required_init_method': ['LCM'], 'dem': [50, 45, 56, 34], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 2, 2, 5],
        [4, 6, 3, 2],
        [3, 2, 6, 1]]), 'required_init_method': ['LCM'], 'dem': [70, 60, 70, 10], 'sup': [60, 65, 85]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 5, 3, 7],
        [4, 3, 6, 5],
        [8, 6, 3, 4]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}

tr_dict={'costs': np.matrix([[3, 7, 4, 1],
        [6, 6, 5, 4],
        [3, 2, 5, 6]]), 'required_init_method': ['NCM'], 'dem': [30, 30, 40, 20], 'sup': [25, 45, 50]}


tr_dict={'costs': np.matrix([[3, 1, 3, 5],
        [2, 4, 3, 4],
        [3, 6, 2, 2]]), 'required_init_method': ['LCM'], 'dem': [30, 40, 35, 25], 'sup': [45, 55, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 6, 4, 4],
        [6, 3, 2, 5],
        [5, 1, 6, 3]]), 'required_init_method': ['NCM'], 'dem': [30, 30, 40, 20], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 3, 6, 7],
        [3, 3, 8, 7],
        [5, 4, 6, 4]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 80, 30], 'sup': [90, 60, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 3, 4, 7],
        [5, 3, 2, 4],
        [5, 4, 5, 8]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [40, 60, 60, 80], 'sup': [100, 60, 80]}
transport_dict_list.append(tr_dict)

#
# tr_dict = {
#     "sup": [
#         45, 30, 55
#     ],
#     "dem": [
#         40, 30, 50
#     ],
#     "costs": np.matrix ([
#         5, 1, 7,
#         6, 4, 2,
#         3, 7, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         45, 30, 55
#     ],
#     "dem": [
#         20, 40, 60
#     ],
#     "costs": np.matrix ([
#         5, 1, 7,
#         6, 2, 2,
#         7, 4, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#

tr_dict={'costs': np.matrix([[2, 1, 6, 3],
        [5, 5, 3, 4],
        [6, 4, 6, 7]]), 'required_init_method': ['NCM'], 'dem': [30, 30, 40, 20], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 3, 4, 5],
        [6, 5, 4, 2],
        [3, 4, 5, 8]]), 'required_init_method': ['NCM'], 'dem': [40, 60, 60, 80], 'sup': [100, 60, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 5, 4, 1],
        [6, 5, 3, 3],
        [4, 2, 7, 6]]), 'required_init_method': ['NCM'], 'dem': [30, 30, 40, 20], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 7, 7, 4],
        [2, 5, 2, 1],
        [5, 2, 5, 4]]), 'required_init_method': ['LCM'], 'dem': [20, 40, 60, 10], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 6, 1, 5],
        [7, 5, 4, 5],
        [7, 2, 2, 2]]), 'required_init_method': ['LCM'], 'dem': [20, 40, 60, 10], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

#
# tr_dict = {
#     "sup": [
#         80, 60, 70
#     ],
#     "dem": [
#         50, 80, 70
#     ],
#     "costs": np.matrix ([
#         4, 2, 3,
#         3, 8, 6,
#         4, 5, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#

tr_dict={'costs': np.matrix([[5, 4, 2, 3],
        [5, 2, 4, 3],
        [5, 8, 7, 6]]), 'required_init_method': ['LCM'], 'dem': [50, 80, 70, 10], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 2, 5, 5],
        [7, 5, 4, 6],
        [4, 3, 8, 2]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [50, 80, 70, 10], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 7, 4, 5],
        [3, 2, 6, 8],
        [4, 3, 2, 5]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [50, 80, 70, 10], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[4, 5, 4, 7],
        [2, 2, 5, 3],
        [6, 3, 8, 5]]), 'required_init_method': ['LCM'], 'dem': [50, 80, 70, 10], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         80, 65, 70
#     ],
#     "dem": [
#         50, 80, 70
#     ],
#     "costs": np.matrix ([
#         4, 2, 3,
#         3, 8, 6,
#         4, 5, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#

tr_dict={'costs': np.matrix([[6, 3, 5, 3],
        [2, 4, 2, 7],
        [4, 4, 5, 8]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [50, 80, 70, 15], 'sup': [80, 65, 70]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[6, 3, 4, 8],
        [5, 2, 4, 7],
        [4, 3, 2, 5]]), 'required_init_method': ['LCM'], 'dem': [50, 80, 70, 15], 'sup': [80, 65, 70]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[2, 5, 4, 7],
        [2, 4, 5, 4],
        [8, 6, 3, 3]]), 'required_init_method': ['LCM'], 'dem': [50, 80, 70, 15], 'sup': [80, 65, 70]}
transport_dict_list.append(tr_dict)



#
# tr_dict = {
#     "sup": [
#         80, 65, 60
#     ],
#     "dem": [
#         50, 80, 70
#     ],
#     "costs": np.matrix ([
#         4, 2, 3,
#         3, 8, 6,
#         4, 5, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
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
# tr_dict = {
#     "sup": [
#         75, 65, 60
#     ],
#     "dem": [
#         40, 75, 70
#     ],
#     "costs": np.matrix ([
#         4, 2, 3,
#         3, 8, 6,
#         4, 5, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         75, 65, 60
#     ],
#     "dem": [
#         40, 75, 60
#     ],
#     "costs": np.matrix ([
#         4, 2, 3,
#         3, 8, 6,
#         4, 5, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         75, 65, 60
#     ],
#     "dem": [
#         40, 75, 55
#     ],
#     "costs": np.matrix ([
#         4, 2, 3,
#         3, 8, 6,
#         4, 5, 5
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#
# tr_dict = {
#     "sup": [
#         50, 35, 45
#     ],
#     "dem": [
#         30, 40, 50
#     ],
#     "costs": np.matrix ([
#         3, 2, 4,
#         2, 3, 5,
#         1, 4, 2
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
#

tr_dict={'costs': np.matrix([[4, 3, 2, 2],
        [3, 3, 2, 3],
        [5, 6, 4, 1]]), 'required_init_method': ['LCM'], 'dem': [30, 40, 50, 10], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 4, 2, 2],
        [1, 6, 2, 3],
        [4, 3, 3, 5]]), 'required_init_method': ['LCM'], 'dem': [30, 40, 50, 10], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[2, 4, 3, 2],
        [2, 3, 6, 4],
        [5, 1, 3, 3]]), 'required_init_method': ['LCM'], 'dem': [30, 40, 40, 20], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 2, 3, 2],
        [4, 2, 3, 6],
        [1, 4, 3, 5]]), 'required_init_method': ['LCM'], 'dem': [25, 40, 35, 30], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 4, 5, 2],
        [3, 3, 4, 6],
        [2, 1, 2, 3]]), 'required_init_method': ['LCM'], 'dem': [25, 40, 35, 30], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 1, 3, 4],
        [3, 6, 2, 2],
        [3, 2, 4, 3]]), 'required_init_method': ['NCM', 'LCM'], 'dem': [25, 40, 35, 30], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)

#
#
#
#
#
# #
# # tr_dict = {
# #     "sup": [
# #         70, 60, 55
# #     ],
# #     "dem": [
# #         60, 80, 20
# #     ],
# #     "costs": np.matrix ([
# #         3, 2, 2,
# #         6, 4, 4,
# #         5, 4, 5,
# #     ]).reshape(3,3),
# # }
# # transport_dict_list.append(tr_dict)
# #
# # tr_dict = {
# #     "sup": [
# #         60, 70, 55
# #     ],
# #     "dem": [
# #         60, 80, 20
# #     ],
# #     "costs": np.matrix ([
# #         3, 2, 2,
# #         6, 7, 4,
# #         5, 4, 5,
# #     ]).reshape(3,3),
# # }
# # transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         70, 70, 50
#     ],
#     "dem": [
#         60, 90, 20
#     ],
#     "costs": np.matrix ([
#         3, 2, 2,
#         6, 3, 4,
#         5, 4, 3,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#

tr_dict={'costs': np.matrix([[5, 1, 4, 6],
        [4, 3, 3, 7],
        [2, 3, 5, 2]]), 'required_init_method': ['LCM'], 'dem': [60, 90, 30, 10], 'sup': [50, 80, 60]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[4, 5, 3, 6],
        [3, 2, 7, 4],
        [1, 3, 5, 2]]), 'required_init_method': ['LCM'], 'dem': [60, 90, 30, 10], 'sup': [50, 80, 60]}
transport_dict_list.append(tr_dict)

#
#
# tr_dict = {
#     "sup": [
#         70, 60, 50
#     ],
#     "dem": [
#         60, 90, 20
#     ],
#     "costs": np.matrix ([
#         3, 2, 2,
#         6, 3, 4,
#         5, 4, 3,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
tr_dict={'costs': np.matrix([[8, 5, 7, 4],
        [4, 3, 4, 6],
        [5, 7, 6, 6]]), 'required_init_method': ['LCM'], 'dem': [70, 45, 35, 30], 'sup': [65, 55, 60]}
transport_dict_list.append(tr_dict)



#
#
# tr_dict = {
#     "sup": [
#         70, 60, 55
#     ],
#     "dem": [
#         60, 90, 20
#     ],
#     "costs": np.matrix ([
#         3, 2, 2,
#         6, 3, 4,
#         5, 4, 3,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
# -------------------------------------------------------------------------------



print len(transport_dict_list)

#from Tkinter import Tk
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

# 产销平衡，(西北角>2 <=3 or 最小元素>2 <=3) 求解有退化，最后无退化
count1 = 0
count1_list = []



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

        count1 += 1
    else:

        print tr

        costs = tr["costs"]
        #print costs
        n, m = costs.shape
        cost_list = costs.reshape([1, n*m]).tolist()[0]
        #print n, m
        it = 0
        while it < 10000:
            it += 1
            print it
            random.shuffle(cost_list)
            # print cost_list
            new_cost = np.matrix(cost_list).reshape([n, m])
            tr["costs"] = new_cost
            if is_qualified_question(tr):
                print tr
                success = True
                break

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
print "count1:", count1

with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(transport_dict_list, f)


