# -*- coding: utf-8 -*-

from .utils.latex_utils import latex_jinja_env
from .utils.transportation import transportation
import numpy as np
import random
try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
    from Tkinter import Tk


SAVED_QUESTION = "transport_unbalanced.bin"
MAX_RETRY_ITERATION = 1000


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

    # count_unbalanced 产销平衡，Vogel >2 <=4 求解有退化，最后无退化

    # criteria:
    suggested_method = []
    qualified = False
    r = Tk()

    assert not t.is_standard_problem

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
        print("not qualified")
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

tr_dict = {
    "sup": [70, 120, 100],
    "dem": [75, 60, 70],
    "costs": np.matrix ([
        8, 9, 12,
        6, 7, 13,
        18, 12, 6
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 7, 12, 13],
        [ 9,  8, 12],
        [18,  3,  6]]), 'dem': [64, 66, 75], 'sup': [71, 101, 118]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 3, 6],
        [4, 7, 5],
        [7, 5, 9]]), 'dem': [80, 100, 60], 'sup': [90, 70, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 9, 3],
        [7, 4, 7],
        [4, 6, 5]]), 'dem': [80, 100, 60], 'sup': [90, 70, 60]}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [70, 120, 100],
    "dem": [75, 60, 70],
    "costs": np.matrix ([
        8, 9, 12,
        6, 7, 13,
        18, 12, 6
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [30, 40, 30],
    "dem": [25, 20, 40],
    "costs": np.matrix ([
        5, 6, 9,
        9, 4, 8,
        10, 7, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[ 6,  8,  5],
        [ 7, 10,  3],
        [ 8,  4,  2]]), 'dem': [21, 19, 25], 'sup': [31, 39, 30]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 2, 7],
        [8, 4, 9],
        [5, 6, 5]]), 'dem': [50, 80, 70], 'sup': [90, 70, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[6, 7, 4],
        [3, 5, 6],
        [4, 3, 1]]), 'dem': [30, 30, 40], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 6, 3],
        [7, 3, 4],
        [6, 4, 1]]), 'dem': [30, 30, 40], 'sup': [25, 45, 50]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[ 5,  3,  8],
        [ 4, 10,  4],
        [12,  2, 11]]), 'dem': [11, 12, 11], 'sup': [18, 19, 21]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 5,  4, 10],
        [ 4,  8,  3],
        [11,  2, 12]]), 'dem': [11, 9, 14], 'sup': [20, 20, 18]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[15, 12,  6],
        [ 2,  7,  8],
        [ 8,  5,  4]]), 'dem': [32, 40, 30], 'sup': [25, 30, 42]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[1, 3, 3],
        [2, 2, 5],
        [3, 4, 4]]), 'dem': [50, 45, 56], 'sup': [60, 80, 45]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 5,  9, 12],
        [ 8,  3,  9],
        [ 3, 10,  8]]), 'dem': [14, 13, 15], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 8,  3,  9],
        [ 9, 12,  5],
        [ 8,  3, 10]]), 'dem': [14, 15, 13], 'sup': [17, 17, 18]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[12,  8,  9],
        [ 5,  3,  9],
        [ 3,  8, 10]]), 'dem': [14, 13, 15], 'sup': [18, 15, 19]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[7, 7, 6],
        [4, 4, 6],
        [2, 5, 3]]), 'dem': [30, 35, 25], 'sup': [25, 40, 30]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[7, 3, 5],
        [5, 8, 4],
        [4, 6, 6]]), 'dem': [4, 8, 10], 'sup': [9, 7, 8]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 6, 3],
        [4, 7, 6],
        [5, 8, 4]]), 'dem': [8, 7, 7], 'sup': [8, 11, 5]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 3, 4],
        [5, 4, 3],
        [6, 2, 6]]), 'dem': [50, 55, 63], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 6, 2],
        [6, 4, 4],
        [3, 5, 3]]), 'dem': [50, 55, 63], 'sup': [65, 40, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[11,  7,  3],
        [10,  2,  1],
        [ 9,  4,  4]]), 'dem': [5, 12, 9], 'sup': [8, 14, 17]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[11, 10,  2],
        [ 1,  3,  9],
        [ 4,  7,  4]]), 'dem': [6, 7, 13], 'sup': [11, 14, 14]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[ 2,  4,  3],
        [ 9, 10,  4],
        [ 1,  7, 11]]), 'dem': [5, 12, 9], 'sup': [8, 14, 17]}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        50, 60, 30
    ],
    "dem": [
        30, 70, 20
    ],
    "costs": np.matrix ([
        10, 8, 12,
        6, 10, 12,
        7, 14, 10,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 2, 3],
        [3, 6, 2],
        [6, 1, 4]]), 'dem': [70, 60, 70], 'sup': [60, 70, 80]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 5, 3],
        [4, 7, 1],
        [6, 5, 2]]), 'dem': [40, 30, 50], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 2, 5],
        [5, 3, 1],
        [4, 7, 6]]), 'dem': [40, 30, 50], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[7, 1, 7],
        [5, 2, 4],
        [2, 6, 5]]), 'dem': [20, 40, 60], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 5, 5],
        [7, 1, 4],
        [2, 7, 6]]), 'dem': [20, 40, 60], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict = {'costs': np.matrix([[7, 2, 2],
                               [1, 6, 5],
                               [5, 4, 7]]), 'dem': [20, 40, 60], 'sup': [45, 30, 55]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 4, 3],
        [5, 3, 2],
        [8, 5, 6]]), 'dem': [50, 80, 70], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 4, 5],
        [4, 5, 3],
        [2, 6, 8]]), 'dem': [50, 80, 70], 'sup': [80, 60, 70]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[5, 3, 8],
        [6, 4, 4],
        [5, 2, 3]]), 'dem': [50, 80, 70], 'sup': [80, 65, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 6, 4],
        [5, 2, 4],
        [5, 3, 8]]), 'dem': [50, 80, 70], 'sup': [80, 65, 70]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 6, 8],
        [3, 2, 5],
        [4, 3, 4]]), 'dem': [50, 80, 70], 'sup': [80, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 6, 3],
        [3, 8, 4],
        [4, 5, 5]]), 'dem': [50, 80, 70], 'sup': [80, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 4, 2],
        [6, 5, 5],
        [3, 8, 3]]), 'dem': [40, 75, 70], 'sup': [75, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[4, 2, 5],
        [6, 4, 3],
        [8, 3, 5]]), 'dem': [40, 75, 70], 'sup': [75, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[3, 3, 4],
        [5, 6, 2],
        [8, 4, 5]]), 'dem': [40, 75, 60], 'sup': [75, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 6, 3],
        [3, 4, 5],
        [2, 8, 4]]), 'dem': [40, 75, 55], 'sup': [75, 65, 60]}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[2, 2, 3],
        [5, 4, 1],
        [3, 2, 4]]), 'dem': [30, 40, 50], 'sup': [50, 35, 45]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[2, 4, 4],
        [5, 6, 2],
        [4, 5, 3]]), 'dem': [60, 80, 20], 'sup': [70, 60, 55]}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        60, 70, 55
    ],
    "dem": [
        60, 80, 20
    ],
    "costs": np.matrix ([
        3, 2, 2,
        6, 7, 4,
        5, 4, 5,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict={'costs': np.matrix([[5, 3, 3],
        [2, 4, 3],
        [6, 4, 2]]), 'dem': [60, 90, 20], 'sup': [70, 70, 50]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[3, 5, 4],
        [2, 4, 2],
        [3, 6, 3]]), 'dem': [60, 90, 20], 'sup': [70, 60, 50]}
transport_dict_list.append(tr_dict)


tr_dict={'costs': np.matrix([[4, 6, 4],
        [2, 2, 3],
        [5, 3, 3]]), 'dem': [60, 90, 20], 'sup': [70, 60, 55]}
transport_dict_list.append(tr_dict)

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
    required_init_method = tr.get("required_init_method", None)
    success = False

    if is_qualified_question(tr):
        print("i", i)
        if required_init_method:
            assert isinstance(required_init_method, list)
            assert set(required_init_method).issubset(set(["LCM", "NCM", "VOGEL"]))
        # else:
        #     print(tr)
        #     raise ValueError(u"未指定方法:", tr)

        count_unbalanced += 1
    else:

        print(tr)

        costs = tr["costs"]
        #print(costs)
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

        #print(n, m)
        it = 0
        inner_it = 0
        while it < MAX_RETRY_ITERATION:
            it += 1
            print("%d-%d" % (inner_it, it))
            random.shuffle(cost_list)
            # print(cost_list)
            new_cost = np.matrix(cost_list).reshape([n, m])
            tr["costs"] = new_cost
            tr["sup"] = sup
            tr["dem"] = dem
            # if inner_it==0 and it == 100:
            #     print(tr)
            # if inner_it==1 and it == 1:
            #     print(tr)
            #     break
            if is_qualified_question(tr):
                print(tr)
                success = True
                break
            if inner_it < MAX_RETRY_ITERATION*10:
                if it == MAX_RETRY_ITERATION:
                    print(tr)
                    inner_it += 1
                    print(inner_it)
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
    required_init_method = tr.get("required_init_method", ["NCM", "LCM", "VOGEL"])


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


print(success)
print("count_unbalanced:", count_unbalanced)

r.mainloop()

# with open(SAVED_QUESTION, 'wb') as f:
#     pickle.dump(transport_dict_list, f)

