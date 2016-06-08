# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.lpmodel import LP

lp = LP(type="max",
        goal=[1, 1, -1, 1],
        constraints=[
            [1, 2, 1, -1, "<", 2],
            [1, -1, 1, 1,  ">", 1],
            [1, 0, 1, 0, "=",1],
            #[-1, 3, -2, -2, "<", 3]
        ],
        sign=[">", ">", "<", "="],
        #x="y",
        #z="W",
        #x_list=["y_1", "y_2", "w_3"],
        dual=True
        )

# lp = LP(type="max",
#         goal=[5, 6, 3],
#         # x="y",
#         # x_list=["y_1", "y_2", "w_3"],
#         constraints=[
#             [1, 2, 2,  "=", 5],
#             [-1, 5, -1,  ">", 3],
#             [4, 7, 3, "<", 8],
#             #[-3, -5, 3, "=", 4],
#         ],
#         sign=["=", ">",  "<"],
#         dual=True
#         )
#
# lp = LP(type="min",
#         goal=[3, 2, -6, 0, 2],
#         #x="y",
#         #x_list=["y_1", "y_2", "w_3"],
#         constraints=[
#             [2, 1, -4, 1, 3,  ">", 7],
#             [1 , 0, 2, -1, 0, "<", 4],
#             [-1, 3, 0, -4, 1, "=", -2]
#         ],
#         sign=[">", ">", ">", "<", "="],
#         dual=True
#         )


template = latex_jinja_env.get_template('/utils/lp_model.tex')
tex = template.render(
    description = u"""
    """,
    lp = lp
)


#_file_write("lp_dual.tex", tex.encode('UTF-8'))

from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()
r.clipboard_append(tex)

tex = template.render(
    description = u"""
    """,
    lp = lp.dual_problem()
)

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

r.clipboard_append(tex)