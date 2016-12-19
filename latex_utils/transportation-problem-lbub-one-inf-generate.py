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


SAVED_QUESTION = "transport_lbub_with_one_inf.bin"
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

    # method_result_list = []
    # if "NCM" in used_method_list:
    #     NCM_result = t.solve(init_method="NCM")
    #     method_result_list.append(NCM_result)
    # if "LCM" in used_method_list:
    #     LCM_result = t.solve(init_method="LCM")
    #     method_result_list.append(LCM_result)
    # if "VOGEL" in used_method_list:
    #     VOGEL_result = t.solve(init_method="VOGEL")
    #     method_result_list.append(VOGEL_result)

    # count_unbalanced 产销平衡，Vogel >2 <=4 求解有退化，最后无退化

    # criteria:
    suggested_method = []
    qualified = False
    r = Tk()

    assert not t.is_standard_problem

    if not t.is_dem_bounded_problem:
        return False

    # if (not t.is_standard_problem
    #     and not (
    #             NCM_result.final_is_degenerated_solution or LCM_result.final_is_degenerated_solution or VOGEL_result.final_is_degenerated_solution)
    #     ):
    #
    #     if (len(NCM_result.solution_list) in range(2, 5)
    #         #and
    #             #(NCM_result.has_degenerated_mid_solution or NCM_result.has_degenerated_init_solution)
    #         ):
    #         qualified = True
    #         suggested_method.append("NCM")
    #
    #     lcm_ratio_qualified = False
    #     if (len(LCM_result.solution_list) in range(2, 4)
    #         #and
    #         #    (LCM_result.has_degenerated_mid_solution or LCM_result.has_degenerated_init_solution)
    #         ):
    #         suggested_method.append("LCM")
    #         a = random.uniform (0, 1)
    #         qualified = True
    #         if a < 0.05:
    #             lcm_ratio_qualified = True
    #
    #     if (len(VOGEL_result.solution_list) in range(2, 4)
    #         #and
    #         #    (VOGEL_result.has_degenerated_mid_solution or VOGEL_result.has_degenerated_init_solution)
    #         ):
    #         qualified = True
    #         suggested_method.append("VOGEL")

    # if not qualified:
    #     # 问题不合格
    #     return False

    # if not len(suggested_method) == 3:
    # #    print("not qualified")
    #     return False

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
            suggestion = "tr_dict=%s" % str(tr)
            suggestion = suggestion.replace("matrix", "np.matrix")
            suggestion = suggestion.replace("inf", "np.inf")
            print(suggestion)
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(suggestion)
            r.clipboard_append("\n")
            r.clipboard_append("transport_dict_list.append(tr_dict)")
            raise ValueError("Please add above problem")

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

    return True

transport_dict_list = []

tr_dict={'costs': np.matrix([[ 8, 12,  7],
        [ 6,  9, 18],
        [ 6, 13, 12]]), 'dem': [[75, np.inf], [60, 90], 70], 'sup': [70, 120, 100]}

tr_dict={'costs': np.matrix([[12, 13,  8],
        [ 7, 18,  6],
        [ 6,  9, 12]]), 'dem': [[75, np.inf], 60, [70, 90]], 'sup': [70, 120, 100]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 6, 13, 18],
        [12, 12,  8],
        [ 7,  3,  9]]), 'dem': [[64, np.inf], 66, [75, 95]], 'sup': [71, 101, 118]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[13,  3,  7],
        [12, 18,  6],
        [ 8, 12,  9]]), 'dem': [64, [66, np.inf], [75, 100]], 'sup': [71, 101, 118]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 7,  6, 12],
        [ 8, 13,  6],
        [ 9, 18, 12]]), 'dem': [75, [60, 85], [70, np.inf]], 'sup': [70, 120, 100]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 8,  6, 12],
        [18, 12, 13],
        [ 7,  9,  6]]), 'dem': [[75, np.inf], [60, 80], 70], 'sup': [70, 120, 100]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9,  7, 10],
        [ 5,  6,  4],
        [ 9,  8,  5]]), 'dem': [[25, np.inf], 20, [40, 45]], 'sup': [30, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 5,  9,  4],
        [ 8,  5,  9],
        [ 6, 10,  7]]), 'dem': [[25, 40], 20, [40, np.inf]], 'sup': [30, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 2,  7, 10],
        [ 3,  5,  4],
        [ 8,  6,  8]]), 'dem': [[21, np.inf], [19, 24], 25], 'sup': [31, 39, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 8,  8,  5],
        [ 6,  4,  7],
        [ 3,  2, 10]]), 'dem': [[21, np.inf], 19, [25, 40]], 'sup': [31, 39, 30]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[9, 5, 4],
        [3, 5, 2],
        [7, 8, 6]]), 'dem': [50, [80, np.inf], [70, 80]], 'sup': [90, 70, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 9, 7],
        [6, 2, 8],
        [3, 5, 4]]), 'dem': [[50, 60], [80, np.inf], 70], 'sup': [90, 70, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 3, 1],
        [4, 6, 5],
        [7, 6, 3]]), 'dem': [[30, np.inf], 30, [40, 55]], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 5, 6],
        [6, 1, 7],
        [3, 4, 3]]), 'dem': [[30, np.inf], 30, [40, 60]], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 6, 7],
        [3, 6, 4],
        [4, 3, 1]]), 'dem': [30, [30, np.inf], [40, 60]], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 1, 4],
        [6, 5, 6],
        [4, 3, 7]]), 'dem': [[30, np.inf], [30, 40], 40], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[12, 11,  2],
        [ 3, 10,  8],
        [ 5,  4,  4]]), 'dem': [11, [12, np.inf], [11, 21]], 'sup': [18, 19, 21]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 4,  8,  5],
        [10,  4, 12],
        [ 3,  2, 11]]), 'dem': [11, [12, np.inf], [11, 26]], 'sup': [18, 19, 21]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[10, 11,  8],
        [ 2,  4,  5],
        [12,  3,  4]]), 'dem': [[11, np.inf], 9, [14, 24]], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 2, 10,  4],
        [ 5,  3,  4],
        [11,  8, 12]]), 'dem': [[11, np.inf], 9, [14, 19]], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 3, 2],
        [1, 4, 4],
        [5, 3, 3]]), 'dem': [[50, 60], 45, [56, np.inf]], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 9,  3, 10],
        [ 8, 12,  9],
        [ 5,  8,  3]]), 'dem': [[14, np.inf], 13, [15, 30]], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 3,  5,  9],
        [ 8,  9, 10],
        [ 3, 12,  8]]), 'dem': [[14, np.inf], 15, [13, 28]], 'sup': [17, 17, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[10,  3,  8],
        [ 3,  5,  9],
        [ 9,  8, 12]]), 'dem': [[14, np.inf], 13, [15, 20]], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 4, 4],
        [2, 5, 6],
        [7, 6, 7]]), 'dem': [[30, np.inf], 35, [25, 30]], 'sup': [25, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 4, 4],
        [2, 3, 6],
        [7, 7, 6]]), 'dem': [[30, np.inf], 35, [25, 30]], 'sup': [25, 40, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 3, 5],
        [5, 6, 4],
        [8, 7, 4]]), 'dem': [[4, np.inf], 8, [10, 25]], 'sup': [9, 7, 8]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 4, 8],
        [5, 7, 6],
        [4, 3, 6]]), 'dem': [[4, np.inf], [8, 23], 10], 'sup': [9, 7, 8]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 6, 8],
        [6, 4, 5],
        [3, 4, 5]]), 'dem': [[8, 18], 7, [7, np.inf]], 'sup': [8, 11, 5]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 8, 4],
        [6, 4, 7],
        [5, 3, 6]]), 'dem': [8, [7, np.inf], [7, 22]], 'sup': [8, 11, 5]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 2, 6],
        [4, 3, 4],
        [6, 2, 3]]), 'dem': [[50, np.inf], 55, [63, 83]], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 2, 2],
        [5, 4, 3],
        [6, 6, 3]]), 'dem': [[50, 70], [55, np.inf], 63], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 4, 4],
        [6, 3, 2],
        [3, 5, 2]]), 'dem': [[50, np.inf], [55, 75], 63], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[11, 10,  2],
        [ 4,  9,  3],
        [ 4,  7,  1]]), 'dem': [5, [12, 17], [9, np.inf]], 'sup': [8, 14, 17]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 4,  3,  1],
        [ 9, 11,  7],
        [ 2, 10,  4]]), 'dem': [[5, np.inf], [12, 22], 9], 'sup': [8, 14, 17]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 3,  1,  2],
        [ 9, 10,  7],
        [ 4,  4, 11]]), 'dem': [6, [7, 22], [13, np.inf]], 'sup': [11, 14, 14]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 4, 11,  2],
        [ 1,  4,  9],
        [ 7,  3, 10]]), 'dem': [[5, 20], 12, [9, np.inf]], 'sup': [8, 14, 17]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[10, 12, 12],
        [10,  6,  7],
        [14,  8, 10]]), 'dem': [[30, np.inf], [70, 85], 20], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[14,  7, 10],
        [ 6,  8, 12],
        [10, 10, 12]]), 'dem': [[30, 40], [70, np.inf], 20], 'sup': [50, 60, 30]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 4, 6],
        [2, 3, 6],
        [1, 2, 2]]), 'dem': [[70, np.inf], 60, [70, 85]], 'sup': [60, 70, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 2, 2],
        [4, 2, 6],
        [6, 3, 1]]), 'dem': [[70, 90], 60, [70, np.inf]], 'sup': [60, 70, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 2, 5],
        [4, 1, 6],
        [7, 3, 5]]), 'dem': [[40, np.inf], [30, 45], 50], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 2, 6],
        [7, 3, 4],
        [1, 5, 5]]), 'dem': [40, [30, np.inf], [50, 70]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 7, 5],
        [7, 2, 1],
        [6, 4, 5]]), 'dem': [[40, np.inf], 30, [50, 65]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 5, 7],
        [4, 2, 3],
        [5, 7, 1]]), 'dem': [[40, 60], 30, [50, np.inf]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 2, 6],
        [1, 7, 5],
        [5, 4, 2]]), 'dem': [20, [40, np.inf], [60, 70]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 5, 1],
        [7, 4, 2],
        [6, 2, 7]]), 'dem': [20, [40, np.inf], [60, 75]], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 6, 7],
        [2, 1, 5],
        [7, 4, 5]]), 'dem': [[20, 40], [40, np.inf], 60], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 5, 4],
        [8, 3, 2],
        [3, 5, 4]]), 'dem': [[50, 60], 80, [70, np.inf]], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 4, 5],
        [2, 8, 5],
        [3, 6, 3]]), 'dem': [[50, 60], [80, np.inf], 70], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 5, 3],
        [8, 2, 4],
        [4, 3, 5]]), 'dem': [[50, np.inf], [80, 95], 70], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 2, 3],
        [4, 5, 5],
        [3, 8, 6]]), 'dem': [[50, 65], [80, np.inf], 70], 'sup': [80, 60, 70]}
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
    success = False

    tr_cp = copy.deepcopy(tr)

    tr_test = copy.deepcopy(tr)
    t_test = transportation(**tr_test)
    tr_temp = None

    if is_qualified_question(tr_cp):
        print("i", i)
        count_unbalanced += 1
    elif t_test.is_dem_bounded_problem:
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
        dem[dem_idx1] = [dem[dem_idx1], np.inf]
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


    template = latex_jinja_env.get_template('/utils/transportation.tex')

    tex = template.render(
        t=t,
        question_table_iters=iter(range(1, 5)),
        answer_table_iters=iter(range(1, 100)),
        show_question=True,
        show_answer=True,
        method_result_list=[],
        show_NCM_result=False,
        show_LCM_result=False,
        show_VOGEL_result=False,
        standardize_only=True,
        problem_description_after = u"<strong>提示：</strong>由于只有一个销地的最高需求是无限，所以可以求出该最高需求的理论上限，即考虑其它销地都只满足最低需求.",
    )

    r.clipboard_append(tex)

print(success)
print("count_unbalanced:", count_unbalanced)
r.mainloop()

# with open(SAVED_QUESTION, 'wb') as f:
#     pickle.dump(transport_dict_list, f)

