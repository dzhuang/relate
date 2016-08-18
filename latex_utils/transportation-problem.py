# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.transportation import transportation
import numpy as np

transport_dict_list = []

tr_dict = {
    "sup": [105, 125, 71], #[[72, 78], [115, 135], 100],
    "dem": [80, 65, 70, 85],
    "costs": np.array ([
        [9., 10., 13., 17.],
        [7., 8., 14., 16.],
        [np.inf, 14., 8., 14.]
    ]),
    "dem_name_prefix": u"市场",
    "sup_name_prefix": u"工厂",
    "dem_desc": u"城市"
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


for tr in transport_dict_list_loaded:
    r.clipboard_clear ()
    t = transportation(**tr)
    LCM_result = t.solve(init_method="LCM")
    NCM_result = t.solve(init_method="NCM")
    VOGEL_result = t.solve(init_method="VOGEL")
    template = latex_jinja_env.get_template('/utils/transportation.tex')
    # tex = template.render(
    #     problem_description_pre = u"""
    #                 设有产量分别为30，40，30的三个原料产地，欲将原材料运往销量分别为
    #                 25，20，40的三个销地，单位运价如下表所示。试求总运费最省的调运方案。""",
    #     problem_table_element = t.get_question_table_element(),
    #     problem_costs = t.costs.tolist(),
    #     problem_standard_table_element = t.get_standard_question_table_element(),
    #     problem_solving_table_element = t.get_standard_question_table_element(use_given_name=False),
    #     problem_standard_costs = t.standard_costs,
    #     LCM_result = LCM_result,
    #     NCM_result = NCM_result,
    #     VOGEL_result = VOGEL_result,
    #     show_LCM_result = True,
    #     show_NCM_result = True,
    #     show_VOGEL_result = True
    # )
    # r.clipboard_append(tex)
    if t.is_standard:
        print "标准化问题"
    elif t.is_bounded_problem:
        if t.is_infinity_bounded_problem:
            print "需求无上限的有下限要求的问题"
        elif t.is_bounded_problem:
            print "有下限要求的问题"
    else:
        print "产销不平衡问题"
    print u"西北角法：迭代次数", len(NCM_result.solution_list),\
        u"初始化时有退化解：",NCM_result.has_degenerated_init_solution,\
        u"计算中有退化解：", NCM_result.has_degenerated_mid_solution,\
        u"最优解唯一：", NCM_result.has_unique_solution
    print u"最小元素法：迭代次数", len(LCM_result.solution_list),\
        u"初始化时有退化解：",LCM_result.has_degenerated_init_solution,\
        u"计算中有退化解：", LCM_result.has_degenerated_mid_solution,\
        u"最优解唯一：", LCM_result.has_unique_solution
    print u"VOGEL法：迭代次数", len(VOGEL_result.solution_list),\
        u"初始化时有退化解：",VOGEL_result.has_degenerated_init_solution,\
        u"计算中有退化解：", VOGEL_result.has_degenerated_mid_solution,\
        u"最优解唯一：", VOGEL_result.has_unique_solution
    print VOGEL_result.solution_list
    print t.costs.tolist(), t.standard_costs.tolist()