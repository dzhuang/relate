# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy


# 作业题(需要使用大M法）
lp_list = []

lp = LP (qtype="min",
         goal=[3, 4, 5],
         constraints=[
             [1, 2, 3, ">", 5],
             [2, 2, 3, ">", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[1, 2, 1],
         constraints=[
             [1, 4, -2, ">", 120],
             [1, 1, 1, "=", 60],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[2, 1],
         constraints=[
             [3, 1, "=", 3],
             [4, 3, ">", 6],
             [1, 2, "<", 3],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[1, 2, 1],
         constraints=[
             [2, 3, 1, ">", 12],
             [1, 1, 3, "=", 9],
#             [1, 2, "<", 3],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[3, -2, -1],
         constraints=[
             [1, -2, 1, "<", 11],
             [-4, 1, 2, ">", 3],
             [-2, 0, 1, "=", 1],
         ],
         )
lp_list.append(lp)


template = latex_jinja_env.get_template('/utils/lp_model.tex')
tex = template.render(
    description = u"""
    """,
    lp = lp
)


_file_write("lp_test.tex", tex.encode('UTF-8'))

from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()
# r.clipboard_append(tex)
#
# res=lp.solve()
#
# print res.x
#
# template = latex_jinja_env.get_template('/utils/lp_simplex.tex')
# tex = template.render(
#     pre_description = u"""
#     """,
#     lp = lp,
#     simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
#     """,
#     simplex_after_description=u"""最优解唯一。
#     """
# )
#
# r.clipboard_append(tex)

# lp = LP(qtype="max",
#         goal=[3, 6, 3, 4],
#         # x="y",
#         # x_list=["y_1", "y_2", "w_3"],
#         constraints=[
#             [1, 1, 3, 4, "<", 8],
#             [1, 3, 1, 1, ">", 21],
#             [3, 2, 1, 2, ">", 15]
#         ],
#         #        sign=[">", "<", ">", "="],
#         )

lp_json_list = []
lp_json_list.append(lp.json)
#lp_json_list.append(lp2.json)
#print lp_json_list


import pickle
#import dill as pickle
with open('lp.bin', 'wb') as f:
    pickle.dump(lp_json_list, f)

with open('lp.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)


for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp2phase = deepcopy(lp)

    lp.solve(method="modified_simplex")
    #lp.solve(method="simplex")
    try:
        lp2phase.solve(method="simplex")
        standardized_lp_2_phase = lp2phase.standardized_LP()
    except ValueError:
        lp2phase = None
        standardized_lp_2_phase = None


    template = latex_jinja_env.get_template('/utils/lp_simplex.tex')
    tex = template.render(
        answer_table_iters=iter(range(1, 5)),
        show_question = True,
        show_answer = True,
        #show_2_stage = True, # 显示两阶段法
        #show_big_m=True,  # 显示大M法
        standardized_lp = lp.standardized_LP(),
        standardized_lp_2_phase=standardized_lp_2_phase,
        pre_description=u"""
        """,
        lp=lp,
        #lp2phase = lp2phase,
        # simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
        # """,
        # simplex_after_description=u"""最优解唯一。
        # """
    )

    r.clipboard_append(tex)
