# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP


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
        goal=[3, -2, -1],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [1, -2, 1, "<", 11],
            [-4, 1, 2, "<", 3],
            [2, 0, 1, "<", 1],
            #[-4, 0, 2, "=", 2]
        ],
#        sign=[">", "<", ">", "="],
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

lp2 = LP(type="max",
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

    # print lp_dict
    # print type(lp_dict["constraints"])
    # print lp_dict["constraints"]
    # print type(lp_dict["x"])

    lp = LP(**lp_dict)


    lp.solve()
    template = latex_jinja_env.get_template('/utils/lp_simplex.tex')
    tex = template.render(
        show_question = True,
        show_answer = True,
        pre_description=u"""
        """,
        lp=lp,
        simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
        """,
        simplex_after_description=u"""最优解唯一。
        """
    )

    r.clipboard_append(tex)

