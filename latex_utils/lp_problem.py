# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy


# lp = LP(qtype="max",
#         goal=[2, -1, 3, 1],
#         #x="y",
#         #x_list=["y_1", "y_2", "w_3"],
#         constraints=[
#             [1, 2, 1, 0, "<", 12],
#             [2, -1, 0, 1, "<", 10],
#             [0, 0, 1, 1, "<", 8]
#         ],
#         #sign=[">", ">", "<", "="],
#         )

lp = LP(qtype="max",
        goal=[3, -2, -1],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [1, -2, 1, "<", 11],
            [-4, 1, 2, ">", 3],
            [-2, 0, 1, "=", 1],
            #[-4, 0, 2, "=", 2]
        ],
#        sign=[">", "<", ">", "="],
        )

# lp = LP(qtype="min",
#         goal=[-3, -5],
#         # x="y",
#         # x_list=["y_1", "y_2", "w_3"],
#         constraints=[
#             [1, 0, "<", 4],
#             [0, 1, "<", 6],
#             [3, 2, "<", 18],
#             # [-4, 0, 2, "=", 2]
#         ],
#         #        sign=[">", "<", ">", "="],
#         )

# lp = LP (qtype="max",
#          goal=[1, 1, -5],
#          # x="y",
#          # x_list=["y_1", "y_2", "w_3"],
#          constraints=[
#              [2, 2, 1, "<", 6],
#              #[1, 1, 1, ">", 7],
#              [1, 1, 1, ">", 8],
#              [2, -5, 1, "=", 10],
#              [-4, 0, 2, "=", 2]
#          ],
#          #        sign=[">", "<", ">", "="],
#          )

# lp = LP(qtype="min",
#         goal=[-1, -1, 5],
#         # x="y",
#         # x_list=["y_1", "y_2", "w_3"],
#         constraints=[
#             [2, 2, 1, "<", 6],
#             # [1, 1, 1, ">", 7],
#             [1, 1, 1, ">", 8],
#             [2, -5, 1, "=", 10],
#             [-4, 0, 2, "=", 2]
#         ],
#         #        sign=[">", "<", ">", "="],
#         )

# lp = LP(qtype="max",
#         goal=[-320, -100],
#         # x="y",
#         # x_list=["y_1", "y_2", "w_3"],
#         constraints=[
#             [-8, -2, "<", 5],
#             [4, 2, ">", 4],
#             [5, 1, ">", 2],
#         ],
#         #        sign=[">", "<", ">", "="],
#         )

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

lp = LP(qtype="max",
        goal=[3, 6, 3, 4],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [1, 1, 3, 4, "<", 8],
            [1, 3, 1, 1, ">", 21],
            [3, 2, 1, 2, ">", 15]
        ],
        #        sign=[">", "<", ">", "="],
        )

lp_json_list = []
lp_json_list.append(lp.json)
#lp_json_list.append(lp2.json)

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
    lpBigM = deepcopy(lp)

    lp.solve(method="simplex")
    #lpBigM.solve(method="big_m_simplex")
    try:
        lpBigM.solve(method="big_m_simplex")
        standardized_lp_big_m = lpBigM.standardized_LP()
    except ValueError:
        lpBigM = None
        standardized_lp_big_m = None
    # except:
    #     lpBigM = None
    #     standardized_lp_big_m = None

    template = latex_jinja_env.get_template('/utils/lp_2_stage_simplex.tex')
    tex = template.render(
        iters = iter(range(0,5)),
        show_question = True,
        show_answer = True,
        show_2_stage = True, # 显示两阶段法
        show_big_m=True,  # 显示大M法
        standardized_lp = lp.standardized_LP(),
        standardized_lp_big_m=standardized_lp_big_m,
        pre_description=u"""
        """,
        lp=lp,
        lpBigM = lpBigM,
        # simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
        # """,
        # simplex_after_description=u"""最优解唯一。
        # """
    )

    r.clipboard_append(tex)

