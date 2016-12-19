# -*- coding: utf-8 -*-

from .utils.latex_utils import latex_jinja_env, _file_write
from .utils.transportation import transportation, sum_recursive
import numpy as np
import random
import copy

try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
    from Tkinter import Tk


SAVED_QUESTION = "transport_lbub.bin"
MAX_RETRY_ITERATION = 50


def is_qualified_question(tr_test, saved_question=SAVED_QUESTION):
    required_init_method = tr_test.pop("required_init_method", None)
    used_method_list = [
        "NCM",
        "LCM",
        "VOGEL"
    ]

    tr = copy.deepcopy(tr_test)

    with open(saved_question, 'rb') as f:
        transport_dict_list_loaded = pickle.load(f)



    t = transportation(**tr_test)

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

    # count_unbalanced 产销平衡，Vogel >2 <=4 求解有退化，最后无退化

    # criteria:
    suggested_method = []
    qualified = False
    r = Tk()

    assert not t.is_standard_problem

    if not t.is_dem_bounded_problem:
        return False

    if (not t.is_standard_problem
        and not (
                NCM_result.final_is_degenerated_solution or LCM_result.final_is_degenerated_solution or VOGEL_result.final_is_degenerated_solution)
        ):

        if (len(NCM_result.solution_list) in range(2, 5)
            #and
                #(NCM_result.has_degenerated_mid_solution or NCM_result.has_degenerated_init_solution)
            ):
            qualified = True
            suggested_method.append("NCM")

        lcm_ratio_qualified = False
        if (len(LCM_result.solution_list) in range(2, 4)
            #and
            #    (LCM_result.has_degenerated_mid_solution or LCM_result.has_degenerated_init_solution)
            ):
            suggested_method.append("LCM")
            a = random.uniform (0, 1)
            qualified = True
            if a < 0.05:
                lcm_ratio_qualified = True

        if (len(VOGEL_result.solution_list) in range(2, 4)
            #and
            #    (VOGEL_result.has_degenerated_mid_solution or VOGEL_result.has_degenerated_init_solution)
            ):
            qualified = True
            suggested_method.append("VOGEL")

    if not qualified:
        # 问题不合格
        return False

    if not len(suggested_method) == 3:
    #    print("not qualified")
        return False

    #tr["required_init_method"] = suggested_method

    #ori_len = len(transport_dict_list_loaded)
    #transport_dict_list_loaded.append(tr)
    question_exist = False
    for i, d in enumerate(transport_dict_list_loaded):
        if np.all(tr["costs"] == d["costs"]):
            if tr["dem"] == d["dem"] and tr["sup"] == d["sup"]:
                d_method = d.get("required_init_method", None)
                sg_method = tr.get("required_init_method", None)
                if not sg_method == d_method:
                    print(tr)
                    print(suggested_method)
                    transport_dict_list_loaded.pop(i)
                    with open(SAVED_QUESTION, 'wb') as f:
                        pickle.dump(transport_dict_list_loaded, f)
                    r.clipboard_clear()
                    r.clipboard_append("'required_init_method': %s" % str(suggested_method))
                    raise ValueError("Existing question with same costs does not have qualified method")
                print("----------------------question exists-------------------")
                question_exist = True

    if not question_exist:
        if lcm_ratio_qualified:
            suggestion = "tr_dict=%s" % str(tr)
            suggestion = suggestion.replace("matrix", "np.matrix")
            print(suggestion)
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

    print(tr)
    print("dem:", t.surplus_dem, ", sup:", t.surplus_sup)
    if t.is_standard_problem:
        print("标准化问题")
    elif t.is_sup_bounded_problem:
        if t.is_infinity_bounded_problem:
            print("供应无上限的有下限要求的问题")
        elif t.is_sup_bounded_problem:
            print("供应有下限要求的问题")
    elif t.is_dem_bounded_problem:
        if t.is_infinity_bounded_problem:
            print("需求无上限的有下限要求的问题")
        elif t.is_dem_bounded_problem:
            print("需求有下限要求的问题")
    else:
        print("产销不平衡问题")
    if NCM_result:
        print(u"西北角法：迭代次数", len(NCM_result.solution_list), \
            u"初始化时有退化解：", NCM_result.has_degenerated_init_solution, \
            u"计算中有退化解：", NCM_result.has_degenerated_mid_solution, \
            u"最优解唯一：", NCM_result.has_unique_solution, \
            u"最优解退化：", NCM_result.final_is_degenerated_solution, \
            u"z", NCM_result.z)
    if LCM_result:
        print(u"最小元素法：迭代次数", len(LCM_result.solution_list), \
            u"初始化时有退化解：", LCM_result.has_degenerated_init_solution, \
            u"计算中有退化解：", LCM_result.has_degenerated_mid_solution, \
            u"最优解唯一：", LCM_result.has_unique_solution, \
            u"最优解退化：", LCM_result.final_is_degenerated_solution, \
            u"z", LCM_result.z)
    if VOGEL_result:
        print(u"VOGEL法：迭代次数", len(VOGEL_result.solution_list), \
            u"初始化时有退化解：", VOGEL_result.has_degenerated_init_solution, \
            u"计算中有退化解：", VOGEL_result.has_degenerated_mid_solution, \
            u"最优解唯一：", VOGEL_result.has_unique_solution, \
            u"最优解退化：", VOGEL_result.final_is_degenerated_solution, \
            u"z", VOGEL_result.z)

    return True

transport_dict_list = []

tr_dict={'costs': np.matrix([[ 8, 18,  6],
        [ 9, 12, 12],
        [13,  6,  7]]), 'dem': [[75, 160], 60, [70, 100]], 'sup': [70, 120, 100]}

transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[18,  7, 12],
        [ 6, 13,  9],
        [12,  8,  6]]), 'dem': [[75, 105], 60, [70, 155]], 'sup': [70, 120, 100]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9,  8, 12],
        [ 6, 18,  7],
        [12, 13,  6]]), 'dem': [75, [60, 80], [70, 155]], 'sup': [70, 120, 100]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9, 18, 12],
        [ 6,  7,  8],
        [13, 12,  6]]), 'dem': [75, [60, 145], [70, 90]], 'sup': [70, 120, 100]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 5, 4],
        [4, 6, 6],
        [3, 3, 1]]), 'dem': [[30, 50], 30, [40, 60]], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 5, 7],
        [3, 1, 4],
        [6, 6, 3]]), 'dem': [[30, 60], 30, [40, 60]], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 1, 6],
        [4, 4, 7],
        [5, 6, 3]]), 'dem': [[30, 50], 30, [40, 70]], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 2,  4,  4],
        [11,  5,  8],
        [12,  3, 10]]), 'dem': [[11, 35], 12, [11, 41]], 'sup': [18, 19, 21]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 2,  3,  4],
        [10,  5, 11],
        [12,  8,  4]]), 'dem': [[11, 35], 12, [11, 26]], 'sup': [18, 19, 21]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 4, 11,  4],
        [ 8,  5, 10],
        [12,  3,  2]]), 'dem': [11, [12, 22], [11, 35]], 'sup': [18, 19, 21]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 4, 11, 12],
        [10,  2,  8],
        [ 4,  5,  3]]), 'dem': [[11, 16], 12, [11, 35]], 'sup': [18, 19, 21]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[12,  2,  4],
        [11,  3,  5],
        [ 4, 10,  8]]), 'dem': [[11, 16], 9, [14, 38]], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 5,  9,  3],
        [12,  3,  8],
        [10,  9,  8]]), 'dem': [14, [15, 25], [13, 23]], 'sup': [17, 17, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[11,  4, 10],
        [ 3,  5,  4],
        [ 8, 12,  2]]), 'dem': [11, [9, 14], [14, 38]], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 2,  5,  3],
        [11,  4,  8],
        [10, 12,  4]]), 'dem': [11, [9, 24], [14, 38]], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 3, 12,  5],
        [ 4,  2, 10],
        [11,  4,  8]]), 'dem': [[11, 35], [9, 19], 14], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 8,  4, 12],
        [ 5, 11,  3],
        [10,  4,  2]]), 'dem': [11, [9, 33], [14, 29]], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 2,  8,  4],
        [12, 11,  4],
        [ 5, 10,  3]]), 'dem': [[11, 35], 9, [14, 19]], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[1, 3, 3],
        [4, 2, 4],
        [3, 2, 5]]), 'dem': [[50, 84], [45, 55], 56], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 3, 2],
        [5, 2, 3],
        [4, 3, 1]]), 'dem': [50, [45, 60], [56, 90]], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[ 5,  9, 12],
        [ 9,  3,  3],
        [10,  8,  8]]), 'dem': [[14, 19], 13, [15, 25]], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 3,  3,  9],
        [10,  5,  8],
        [ 9, 12,  8]]), 'dem': [[14, 19], 13, [15, 25]], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 2, 6],
        [5, 4, 7],
        [7, 3, 1]]), 'dem': [[40, 50], 30, [50, 60]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 4, 4],
        [3, 6, 3],
        [6, 5, 2]]), 'dem': [[50, 67], 55, [63, 73]], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 3, 10, 12],
        [ 5,  3,  9],
        [ 8,  9,  8]]), 'dem': [14, [13, 23], [15, 20]], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[1, 5, 3],
        [2, 3, 4],
        [2, 4, 3]]), 'dem': [50, [45, 55], [56, 90]], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9,  8, 10],
        [ 9,  3,  5],
        [12,  8,  3]]), 'dem': [[14, 24], 15, [13, 28]], 'sup': [17, 17, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 3, 3],
        [4, 5, 6],
        [4, 6, 2]]), 'dem': [50, [55, 72], [63, 73]], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 3, 12,  8],
        [10,  3,  5],
        [ 9,  9,  8]]), 'dem': [[14, 29], 15, [13, 23]], 'sup': [17, 17, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[11,  7,  1],
        [ 3,  9,  4],
        [10,  2,  4]]), 'dem': [[6, 19], 7, [13, 23]], 'sup': [11, 14, 14]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 3, 4],
        [8, 3, 6],
        [5, 5, 2]]), 'dem': [[40, 70], [75, 85], 55], 'sup': [75, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 3,  9,  8],
        [10,  8, 12],
        [ 9,  5,  3]]), 'dem': [[14, 24], 15, [13, 28]], 'sup': [17, 17, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 5,  9,  8],
        [10,  8, 12],
        [ 9,  3,  3]]), 'dem': [[14, 24], [13, 18], 15], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 5, 7],
        [5, 2, 1],
        [7, 4, 6]]), 'dem': [[40, 50], 30, [50, 65]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 5, 6],
        [4, 4, 3],
        [8, 2, 5]]), 'dem': [[50, 70], 80, [70, 80]], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 4, 3],
        [5, 2, 6],
        [4, 8, 3]]), 'dem': [50, [80, 85], [70, 85]], 'sup': [80, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 5, 4],
        [3, 2, 4],
        [6, 3, 2]]), 'dem': [[60, 75], [90, 100], 20], 'sup': [70, 60, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 2, 6],
        [7, 2, 7],
        [4, 1, 5]]), 'dem': [[20, 30], [40, 55], 60], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 2, 3],
        [3, 6, 4],
        [4, 3, 2]]), 'dem': [[60, 80], 90, [20, 40]], 'sup': [70, 70, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 2, 7],
        [1, 7, 4],
        [5, 6, 5]]), 'dem': [20, [40, 50], [60, 80]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 5, 7],
        [1, 6, 5],
        [2, 7, 2]]), 'dem': [20, [40, 50], [60, 75]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 5, 3],
        [4, 5, 6],
        [3, 8, 4]]), 'dem': [50, [80, 90], [70, 85]], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 7, 6],
        [5, 7, 2],
        [4, 2, 1]]), 'dem': [20, [40, 50], [60, 80]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 5, 5],
        [7, 4, 4],
        [2, 6, 3]]), 'dem': [60, [80, 105], [20, 40]], 'sup': [60, 70, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 3, 3],
        [1, 6, 7],
        [4, 6, 4]]), 'dem': [30, [30, 45], [40, 60]], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 3, 5],
        [6, 2, 4],
        [6, 2, 4]]), 'dem': [[50, 67], 55, [63, 83]], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)


print(transport_dict_list)

print(len(transport_dict_list))

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
    print("here")
    l_len = len(l)
    l_sum = sum(l)
    new_list = []
    for i in range(l_len - 1):
        new_list.append(int(round(random.uniform(l_min, l_max))))
    new_list.append(l_sum-sum(new_list))
    return new_list


# 产销平衡，(西北角>2 <=3 or 最小元素>2 <=3) 求解有退化，最后无退化
count_unbalanced = 0
count_unbalanced_list = []

for i, tr in enumerate(transport_dict_list_loaded):
    #required_init_method = tr.get("required_init_method", None)
    required_init_method = ["NCM", "LCM", "VOGEL"]
    success = False

    tr_cp = copy.deepcopy(tr)

    tr_test = copy.deepcopy(tr)
    t_test = transportation(**tr_test)
    tr_temp = None

    if is_qualified_question(tr_cp):
        print("i", i)
        if required_init_method:
            assert isinstance(required_init_method, list)
            assert set(required_init_method).issubset(set(["LCM", "NCM", "VOGEL"]))
        # else:
        #     print(tr)
        #     raise ValueError(u"未指定方法:", tr)

        count_unbalanced += 1
    elif t_test.is_dem_bounded_problem:
        print(tr_test)
        r.clipboard_clear()
        raise ValueError("The above question is not valid!!!!!!!!!")
    elif sum_recursive(t_test.dem) >= sum_recursive(t_test.sup):
        # 指定使用供过于求的问题
        print(tr_test)
        r.clipboard_clear()
        raise ValueError("The above question is not valid!!!!!!!!!")
    elif t_test.n_sup!= 3 or t_test.n_dem!= 3:
        print(tr_test)
        r.clipboard_clear()
        raise ValueError("The above question is not valid!!!!!!!!!")
    else:
        costs = tr["costs"]
        #print(costs)
        n, m = costs.shape
        cost_list = costs.reshape([1, n*m]).tolist()[0]
        cost_min = min(cost_list)
        cost_max = max(cost_list)
        sup = copy.deepcopy(tr["sup"])
        dem = copy.deepcopy(tr["dem"])
        dem_total = sum_recursive(dem)
        sup_total = sum_recursive(sup)
        overfill = sup_total - dem_total
        assert overfill > 0
        dem_idx_list = list(range(len(dem)))
        dem_idx1 = random.choice(dem_idx_list)
        dem_idx2 = random.choice([idx for idx in dem_idx_list if idx != dem_idx1])
        dem[dem_idx1] = [dem[dem_idx1], dem[dem_idx1] + overfill]
        if dem_total > 200:
            dem[dem_idx2] = [dem[dem_idx2], dem[dem_idx2] + random.choice([20, 25, 30])]
        elif dem_total< 100:
            dem[dem_idx2] = [dem[dem_idx2], dem[dem_idx2] + random.choice([5, 10, 15])]
        else:
            dem[dem_idx2] = [dem[dem_idx2], dem[dem_idx2] + random.choice([10, 15, 20])]

        #print(n, m)
        it = 0
        inner_it = 0
        while it < MAX_RETRY_ITERATION:
            tr_temp = copy.deepcopy(tr)
            it += 1
            #print("%d-%d" % (inner_it, it))
            random.shuffle(cost_list)
            # print(cost_list)
            new_cost = np.matrix(cost_list).reshape([n, m])
            tr_temp["costs"] = new_cost
            tr_temp["sup"] = sup
            tr_temp["dem"] = dem

            # if inner_it==0 and it == 100:
            #     print(tr)
            # if inner_it==1 and it == 1:
            #     print(tr)
            #     break
            #print("here----------------------",tr_temp)
            if is_qualified_question(tr_temp):
                #print("success")
                success = True
                break
            # if inner_it < MAX_RETRY_ITERATION*10:
            #     if it == MAX_RETRY_ITERATION:
            #         print("--------------inner-----------------")
            #         print(tr)
            #         inner_it += 1
            #         print(inner_it)
            #         sup = random_int_list_fixed_sum(sup, sup_min, sup_max)
            #         dem = random_int_list_fixed_sum(dem, dem_min, dem_max)
            #         it = 0
            # elif inner_it == MAX_RETRY_ITERATION/100:
            #     if innerest_it < MAX_RETRY_ITERATION:
            #         innerest_it += 1
            #         inner_it = 0
            #         cost_list = [int(round(random.uniform(1, 15))) for i in range(n*m)]


        if it == MAX_RETRY_ITERATION:
            print(i)
            continue
            raise ValueError("Failed to create problem")
    if tr_temp:
        t = transportation(**tr_temp)
    else:
        t = transportation(**tr)

#    r.clipboard_clear ()

    #required_init_method = ["LCM", "NCM", "VOGEL"]
    required_init_method = tr.get("required_init_method", ["NCM", "LCM", "VOGEL"])

    show_LCM_result = True
    show_NCM_result = True
    show_VOGEL_result = True

    # show_LCM_result = False
    # show_NCM_result = False
    # show_VOGEL_result = False

    if "LCM" in required_init_method:
        show_LCM_result = True
    if "NCM" in required_init_method:
        show_NCM_result = True
    if "VOGEL" in required_init_method:
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

    template = latex_jinja_env.get_template('/utils/transportation_no_more_than_2_iters.tex')

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
        show_NCM_result=show_NCM_result,
        show_LCM_result=show_LCM_result,
        show_VOGEL_result=show_VOGEL_result,
        standardize_only=False,
        init_method_list=[INIT_METHOD_DICT.get(method, None) for method in required_init_method],
        used_method_list=[INIT_METHOD_DICT.get(used_method) for used_method in used_method_list],
    )

    r.clipboard_append(tex)

print(success)
print("count_unbalanced:", count_unbalanced)

# with open(SAVED_QUESTION, 'wb') as f:
#     pickle.dump(transport_dict_list, f)

