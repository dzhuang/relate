# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy


# 作业题


lp = LP (qtype="min",
         goal=[1, 4, 3],
         constraints=[
             [1, 1, 1, ">", 3],
             [-2, -1, 1, ">", 2],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 4, 0, 3],
         constraints=[
             [1, 1, -1, 1, ">", 3],
             [-2, -1, 4, 1, ">", 2],
         ],
         )

lp = LP (qtype="min",
         goal=[2, 3, 4],
         constraints=[
             [1, -2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[2, 3, 5, 6],
         constraints=[
             [1, 2, 3, 1, ">", 2],
             [-2, 1, -1, 3, "<", -3],
         ],
         )

lp = LP(qtype="min",
        goal=[160, 50],
        constraints=[
            [4, 1, ">", 2],
            [1, 1, ">", 2],
            [5, 1, ">", 4],
        ],
        )

lp = LP(qtype="min",
        goal=[3, 9],
        constraints=[
            [1, 1, ">", 2],
            [1, 4, ">", 3],
            [1, 7, ">", 3],
        ],
        )

lp = LP(qtype="min",
        goal=[2, 2, 1],
        constraints=[
            [2, 2, 4, ">", 16],
            [1, 2, 1, ">", 10],
            [3, 2, 0, ">", 8],
        ],
        )

lp = LP(qtype="min",
        goal=[3, 2, 2, 5],
        constraints=[
            [2, 1, 1, 3, ">", 12],
            [1, 3, 2, 1, ">", 18],
        ],
        )

lp = LP(qtype="min",
        goal=[3, 2, 1, 4],
        constraints=[
            [2, -1, 1, -2, ">", 8],
            [4, 1, 4, 6, ">", 16],
        ],
        )

lp = LP(qtype="min",
        goal=[1, 2, 4, 1],
        constraints=[
            [1, 2, 3, 3, ">", 21],
            [2, 1, 1, 2, ">", 30],
        ],
        )

lp = LP(qtype="min",
        goal=[3, 4, 6],
        constraints=[
            [1, 2, 1, ">", 4],
            [2, -1, 3, ">", 5],
        ],
        )

lp = LP(qtype="min",
        goal=[4, 4, 5],
        constraints=[
            [1, 2, 2, ">", 6],
            [2, 1, 4, ">", 8],
            [4, -2, 3, ">", 12],
        ],
        )

lp = LP(qtype="min",
        goal=[7, 8, 9],
        constraints=[
            [1, 2, 3, ">", 48],
            [0, 2, 1, ">", 20],
        ],
        )

lp = LP (qtype="min",
         goal=[2, 3, 3],
         constraints=[
             [1, 1, 3, ">", 4],
             [2, -1, 1, ">", 3],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 1, 2],
         constraints=[
             [1, 2, 1, ">", 4],
             [2, 1, 1, ">", 6],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 1, 1],
         constraints=[
             [2, 1, 2, ">", 12],
             [1, 2, 1, ">", 9],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 1, 2],
         constraints=[
             [2, 1, 2, ">", 4],
             [1, 7, 1, ">", 7],
         ],
         )

# 3次迭代
# lp = LP (qtype="min",
#          goal=[8, 6, 6, 9],
#          constraints=[
#              [1, 2, 0, 1, ">", 2],
#              [3, 1, 1, 1, ">", 4],
#              [0, 0, 1, 1, ">", 1],
#              [1, 0, 1, 0, ">", 1],
#          ],
#          )

lp = LP (qtype="min",
         goal=[4, 1, 3],
         constraints=[
             [7, 1, 2, ">", 6],
             [4, 2, 3, ">", 8],
         ],
         )

lp = LP (qtype="min",
         goal=[2, 3, 4],
         constraints=[
             [1, 2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[15, 24, 5],
         constraints=[
             [0, 6, 1, ">", 2],
             [5, 2, 1, ">", 1],
         ],
         )

lp = LP (qtype="min",
         goal=[15, 24, 5],
         constraints=[
             [5, 8, 2, ">", 6],
             [5, 2, 1, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[5, 6, 3],
         constraints=[
             [2, 1, 1, ">", 6],
             [2, 1, 2, ">", 10],
         ],
         )

lp = LP (qtype="min",
         goal=[24, 15, 5],
         constraints=[
             [6, 0, 1, ">", 4],
             [2, 5, 1, ">", 2],
         ],
         )

lp = LP (qtype="min",
         goal=[2, 3, 1, 4],
         constraints=[
             [-1, 2, 3, -6, ">", 9],
             [2, 4, 1, 2, ">", 7],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 2, 1, 4],
         constraints=[
             [2, -1, 3, -6, ">", 6],
             [4, 2, 1, 2, ">", 7],
         ],
         )

lp = LP (qtype="max",
         goal=[-5, -35, -20],
         constraints=[
             [-1, 1, 1, ">", 2],
             [1, 3, 0, ">", 3],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 4, 6],
         constraints=[
             [1, 2, 3, ">", 5],
             [1, 1, 1, ">", 3],
         ],
         )

# # 无可行解
# lp = LP (qtype="min",
#          goal=[3, 2, 1],
#          constraints=[
#              [1, 1, 1, "<", 6],
#              [1, 0, 1, ">", 4],
#              [0, 1, -1, ">", 3],
#          ],
#          )

lp = LP (qtype="min",
         goal=[2, 3, 1],
         constraints=[
             [5, 1, 2, ">", 10],
             [1, 1, 2, ">", 5],
         ],
         )

lp = LP (qtype="min",
         goal=[2, 6, 9],
         constraints=[
             [1, 0, 3, ">", 3],
             [0, 2, 2, ">", 5],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 2, 4],
         constraints=[
             [1, 1, 2, ">", 4],
             [2, 1, 3, ">", 5],
         ],
         )

lp = LP (qtype="min",
         goal=[4, 2, 3],
         constraints=[
             [4, 2, 3, ">", 12],
             [3, 1, 2, ">", 10],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [3, 1, 5, ">", 10],
             [1, 3, 2, ">", 12],
         ],
         )

lp = LP (qtype="min",
         goal=[4, 2, 3],
         constraints=[
             [2, 3, 1, ">", 12],
             [1, 2, 4, ">", 10],
         ],
         )

lp = LP (qtype="min",
         goal=[5, 2, 4],
         constraints=[
             [3, 1, 2, ">", 4],
             [6, 3, 2, ">", 10],
         ],
         )

lp = LP (qtype="min",
         goal=[9, 12, 15],
         constraints=[
             [2, 2, 1, ">", 10],
             [2, 3, 1, ">", 12],
             [1, 1, 5, ">", 14],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 3, 2],
         constraints=[
             [1, -2, 3, ">", 4],
             [3, 1, -2, ">", 6],
#             [1, 1, 5, ">", 14],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 2, -1, ">", 3],
             [2, 1, 1, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[2, 3, 5],
         constraints=[
             [2, 1, 2, ">", 8],
             [1, 2, -1, ">", 6],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 4, 5],
         constraints=[
             [1, 2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 4, 5],
         constraints=[
             [1, -2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[2, 3, 5],
         constraints=[
             [-1, 2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 3, 2, ">", 3],
             [2, 1, 3, ">", 2],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 3, 2, ">", 3],
             [2, 1, 3, ">", 2],
         ],
         )

lp = LP (qtype="min",
         goal=[6, 4, 7],
         constraints=[
             [1, 0, 3, ">", 2],
             [3, 2, 1, ">", 4],
             [-1, 2, 2, ">", 5],
         ],
         )

lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 1, 2, ">", 12],
             [2, -1, 1, ">", 10],
             [2, 4, 2, ">", 15],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 2, 4],
         constraints=[
             [1, -1, 1, ">", 2],
             [-1, 2, 0, ">", 3],
             [2, 0, 1, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 2, 1],
         constraints=[
             [1, -1, 1, ">", 2],
             [-1, 2, 0, ">", 3],
             [2, 0, 1, ">", 4],
         ],
         )

lp = LP (qtype="min",
         goal=[3, 5, 7],
         constraints=[
             [2, -1, 1, ">", 14],
             [1, 2, 1, "<", 13],
             [0, 2, -1, ">", 4],
         ],
         )

lp = LP(qtype="max",
        goal=[-5, -35, -20],
        constraints=[
            [-1, 1, 1, ">", 2],
            [1, 3, 0, ">", 3],
        ],
        )


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

    #lp = lp
    lp = LP(**lp_dict)
    lp2phase = deepcopy(lp)

    lp.solve(method="dual_simplex")
    #lp.solve(method="simplex")
    # try:
    #     lp2phase.solve(method="simplex")
    #     standardized_lp_2_phase = lp2phase.standardized_LP()
    # except ValueError:
    #     lp2phase = None
    #     standardized_lp_2_phase = None


    template = latex_jinja_env.get_template('/utils/lp_simplex.tex')
    tex = template.render(
        iters = iter(range(0,5)),
        show_question = True,
        show_answer = True,
#        show_2_stage = True, # 显示两阶段法
        #show_big_m=True,  # 显示大M法
        standardized_lp = lp.standardized_LP(),
#        standardized_lp_2_phase=standardized_lp_2_phase,
        pre_description=u"""
        """,
        lp=lp,
#        lp2phase = lp2phase,
        # simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
        # """,
        # simplex_after_description=u"""最优解唯一。
        # """
    )

    r.clipboard_append(tex)
    print lp.solve_opt_res_str
    print lp.solutionCommon.nit
