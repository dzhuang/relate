# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy
import numpy as np

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


lp = LP(qtype="min",
        goal=[-1, -1, 5],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [2, 2, 1, "<", 6],
            # [1, 1, 1, ">", 7],
            [1, 1, 1, ">", 8],
            [2, -5, 1, "=", 10],
            [-4, 0, 2, "=", 2]
        ],
        #        sign=[">", "<", ">", "="],
        )


template = latex_jinja_env.get_template('/utils/lp_model.tex')
tex = template.render(
    description = u"""
    """,
    lp = lp
)



#_file_write("lp_test.tex", tex.encode('UTF-8'))

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
        goal=[4, 3],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [3, 4, "<", 12],
            [3, 3, "<", 10],
            [4, 2, "<", 8],
            #            [3, 2, 1, 2, ">", 15]
        ],
        #        sign=[">", "<", ">", "="],
        sensitive={
            "p": [([0], [1,2,3], [2,3,4]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            #"c": [([0], None, 5, 6), (None, [2, 5], [3,5])],
            #"b": [([2], None, 4, 5), (None, [5, 7, 8], [6, 7, 8])],
            "A": [([1, 2, "<", 4],[1, 2, "<", 5])],
            "x": [[{"c": 3, "p":[2,1,3]},{"c": 4, "p":[2,1,3]}]]
        }
        )

lp = LP(qtype="max",
        goal=[4, 3],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [3, 4, "<", 12],
            [3, 3, "<", 10],
            [4, 2, "<", 8],
            #            [3, 2, 1, 2, ">", 15]
        ],
        #        sign=[">", "<", ">", "="],
        sensitive={
            "p": [([0], [1, 2, 3], [2, 3, 4]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([0], None, 5, 6), (None, [2, 5], [3, 5])],
            "b": [([2], None, 4, 5), (None, [5, 7, 8], [6, 7, 8])],
            "A": [([1, 2, "<", 4], [1, 2, "<", 5])],
            "x": [[{"c": 3, "p": [2, 1, 3]}, {"c": 4, "p": [2, 1, 3]}]]
        },
        # start_basis=[0,1,2],
        # start_tableau=np.array([
        #     [  3,   4,   1,   0,   0,  12],
        #     [  3,   3,   0,   1,   0,  10.],
        #     [  4,   2,   0,   0,   1,   8.],
        #     [ -4,  -3,   0,   0,   0,   0.]])
        )

#
# import numpy as np
# lp = LP(qtype="max",
#         goal=[5, 4, 4],
#         start_basis=[0, 1],
#         start_tableau=np.array([
#             [1,   0,   0.75,    0.25, -0.5, 30.],
#             [0,   1. - 0.25 - 0.25,  1,  20.],
#             [0., 0., 1.25, -0.25, -1.5, 230.]
#         ])
#         )

lp = LP(qtype="max",
        goal=[5, 4, 2],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [8, 4, 5, "<", 320],
            [2, 2, 1, "<", 100],
            #            [3, 2, 1, 2, ">", 15]
        ],
        #        sign=[">", "<", ">", "="],
        sensitive={
#            "p": [([0], [20, 30], [2, 3]), ([2], [1, 0], [2, 3])],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([2], None, 4), ([0], None, 10), (None, [6, 3, 4], [6, 3, 5])],
            #"b": [([0], 360, None, 500), (None, [500, 600], [400, 700])],
            #"A": [([12, 10, 6, "<", 720], [12, 10, 6, "<", 480])],
            #"x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )

# import numpy as np
# lp = LP(qtype="max",
#         goal=[5, 4, 4],
#         start_basis=[0, 1],
#         start_tableau=np.array([
#             [1, 0, 0.75, 0.25, -0.5, 30.],
#             [0,   1., -0.25, -0.25,  1,  20.],
#             [0., 0., -1.25, 0.25, 1.5, 230.]
#         ])
#         )

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

    #lp = LP(**lp_dict)
    lp = lp
    lp2phase = deepcopy(lp)

    lp.solve(method="simplex")
    lp.sensitive_analysis()

    # try:
    #     lp2phase.solve(method="simplex")
    #     standardized_lp_2_phase = lp2phase.standardized_LP()
    # except ValueError:
    #     lp2phase = None
    #     standardized_lp_2_phase = None


    template = latex_jinja_env.get_template('/utils/lp_sensitivity.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        iters=iter(range(0, 10)),
        show_question = True,
        show_answer = True,
#        standardized_lp = lp.standardized_LP(),
        pre_description=u"""有线性规划问题
        """,
        after_description=u"""
        """,
        lp=lp,
        show_only_opt_table = True,
    )

    r.clipboard_append(tex)

