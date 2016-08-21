# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.transportation import transportation
import numpy as np

transport_dict_list = []

# # # 例题
# # tr_dict = {
# #     "sup": [75, 125, 100], #[[72, 78], [115, 135], 100],
# #     # "sup": [[72, 78], [115, 135], 100],
# #     "dem": [80, 65, 70, 85],
# #     "costs": np.array ([
# #         [9., 10., 13., 17.],
# #         [7., 8., 14., 16.],
# #         [20, 14., 8., 14.]
# #     ]),
# #     "dem_name_prefix": u"市场",
# #     "sup_name_prefix": u"工厂",
# #     "dem_desc": u"城市"
# # }
#
# #transport_dict_list.append(tr_dict)
#
# # # 例题
# # tr_dict = {
# #     "sup": [6, 10, 7], #[[72, 78], [115, 135], 100],
# #     # "sup": [[72, 78], [115, 135], 100],
# #     "dem": [3, 5, 9, 6],
# #     "costs": np.matrix ([
# #         3, 9, 8, 6,
# #         12, 25, 7, 10,
# #         6, 11, 13, 14
# #     ]).reshape(3,4),
# #     # "dem_name_prefix": u"市场",
# #     # "sup_name_prefix": u"工厂",
# #     # "dem_desc": u"城市"
# # }
# #
# # transport_dict_list.append(tr_dict)
#
# # # 例题
# # tr_dict = {
# #     "sup": [40, 20, 15], #[[72, 78], [115, 135], 100],
# #     # "sup": [[72, 78], [115, 135], 100],
# #     "dem": [10, 20, 15, 16, 14],
# #     "costs": np.matrix ([
# #         8, 15, 20, 14, 4,
# #         5, 7, 6, 9, 8,
# #         3, 9, 10, 16, 13,
# #     ]).reshape(3,5),
# #     # "dem_name_prefix": u"市场",
# #     # "sup_name_prefix": u"工厂",
# #     # "dem_desc": u"城市"
# # }
#
# # transport_dict_list.append(tr_dict)
#
#
# # # 重复率太高
# # tr_dict = {
# #     "sup": [5, 6, 8],
# #     "dem": [4, 8, 6],
# #     "costs": np.matrix ([
# #         3, 1, 3,
# #         4, 6, 2,
# #         2, 8, 5
# #     ]).reshape(3,3),
# # }
# # transport_dict_list.append(tr_dict)
#
#
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
    "sup": [70, 80, 90],
    "dem": [60, 100, 50],
    "costs": np.matrix ([
        4, 6, 5,
        2, 3, 8,
        8, 7, 9
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [90, 70, 60],
    "dem": [80, 100, 60],
    "costs": np.matrix ([
        4, 3, 5,
        7, 4, 9,
        6, 5, 7
    ]).reshape(3,3),
}
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
    "sup": [70, 120, 100],
    "dem": [75, 60, 70, 85],
    "costs": np.matrix ([
        8, 9, 12, 10,
        6, 10, 11, 8,
        18, 8, 9, 6
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)



tr_dict = {
    "sup": [5, 6, 8],
    "dem": [4, 7, 6, 2],
    "costs": np.matrix ([
        3, 1, 3, 2,
        4, 6, 2, 3,
        2, 8, 5, 4,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [90, 70, 60, 20],
    "dem": [80, 100, 60],
    "costs": np.matrix ([
        6, 3, 5,
        4, 8, 9,
        6, 5, 7,
        5, 4, 8,
    ]).reshape(4,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [70, 80, 90],
    "dem": [60, 100, 50, 30],
    "costs": np.matrix ([
        4, 6, 5, 7,
        2, 3, 8, 6,
        8, 7, 9, 5
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [30, 40, 30],
    "dem": [25, 20, 40, 15],
    "costs": np.matrix ([
        5, 6, 9, 8,
        9, 4, 8, 7,
        10, 7, 5, 9
    ]).reshape(3,4),
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



from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()

import pickle
#import dill as pickle
with open('transport.bin', 'wb') as f:
    pickle.dump(transport_dict_list, f)

with open('transport.bin', 'rb') as f:
    transport_dict_list_loaded = pickle.load(f)

INIT_METHOD_DICT = {"LCM": u"最小元素法", "NCM": u"西北角法", "VOGEL": u"伏格尔法"}

for i, tr in enumerate(transport_dict_list_loaded):
    r.clipboard_clear ()
    t = transportation(**tr)
    template = latex_jinja_env.get_template('/utils/transportation.tex')
    required_init_method = None
    if required_init_method:
        assert required_init_method in ["LCM", "NCM", "VOGEL"]

    show_LCM_result = True
    show_NCM_result = True
    show_VOGEL_result = True

    # show_LCM_result = False
    # show_NCM_result = False
    # show_VOGEL_result = False

    if required_init_method == "LCM":
        show_LCM_result = True
    elif required_init_method == "NCM":
        show_NCM_result = True
    elif required_init_method == "VOGEL":
        show_VOGEL_result = True

    used_method_list = [required_init_method]
    if not required_init_method:
        used_method_list = [
            "NCM",
            "LCM",
            "VOGEL"
        ]

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

    tex = template.render(
        question_table_iters=iter(range(1, 5)),
        answer_table_iters=iter(range(1, 100)),
        show_question = True,
        show_answer = True,
        # problem_description_pre = u"""
        #             设有产量分别为30，40，30的三个原料产地，欲将原材料运往销量分别为
        #             25，20，40的三个销地，单位运价如下表所示。试求总运费最省的调运方案。""",
        t = t,
#        LCM_result = LCM_result,
#        NCM_result = NCM_result,
#        VOGEL_result = VOGEL_result,
        method_result_list=method_result_list,
        show_LCM_result = show_LCM_result,
        show_NCM_result = show_NCM_result,
        show_VOGEL_result = show_VOGEL_result,
        standardize_only = False,
        init_method = INIT_METHOD_DICT.get(required_init_method, None),
        used_method_list = [INIT_METHOD_DICT.get(used_method) for used_method in used_method_list],
    )

    r.clipboard_append(tex)

    if i == len(transport_dict_list_loaded) - 1:
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
            print u"西北角法：迭代次数", len(NCM_result.solution_list),\
                u"初始化时有退化解：",NCM_result.has_degenerated_init_solution,\
                u"计算中有退化解：", NCM_result.has_degenerated_mid_solution,\
                u"最优解唯一：", NCM_result.has_unique_solution
        if LCM_result:
            print u"最小元素法：迭代次数", len(LCM_result.solution_list),\
                u"初始化时有退化解：",LCM_result.has_degenerated_init_solution,\
                u"计算中有退化解：", LCM_result.has_degenerated_mid_solution,\
                u"最优解唯一：", LCM_result.has_unique_solution
        if VOGEL_result:
            print u"VOGEL法：迭代次数", len(VOGEL_result.solution_list),\
                u"初始化时有退化解：",VOGEL_result.has_degenerated_init_solution,\
                u"计算中有退化解：", VOGEL_result.has_degenerated_mid_solution,\
                u"最优解唯一：", VOGEL_result.has_unique_solution,\
                u"最优检验数表唯一：", VOGEL_result.has_unique_verify_table