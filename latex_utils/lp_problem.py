# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.lpmodel import LP

# lp = LP(type="max",
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

lp = LP(type="max",
        goal=[2, 5, 3, 5],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [1, 1, 3, 4, "<", 8],
            [1, 3, 1, 1, "<", 21],
            [3, 2, 1, 2, "<", 15]
        ],
        sign=[">", "<", ">", "="],
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
r.clipboard_append(tex)

lp.solve()

template = latex_jinja_env.get_template('/utils/lp_simplex.tex')
tex = template.render(
    pre_description = u"""
    """,
    lp = lp,
    simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
    """,
    simplex_after_description=u"""最优解唯一。
    """
)

r.clipboard_append(tex)