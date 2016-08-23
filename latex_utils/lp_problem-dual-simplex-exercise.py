# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy

lp_list = []

# 作业题


lp = LP (qtype="min",
         goal=[1, 4, 3],
         constraints=[
             [1, 1, 1, ">", 3],
             [-2, -1, 1, ">", 2],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 4, 0, 3],
         constraints=[
             [1, 1, -1, 1, ">", 3],
             [-2, -1, 4, 1, ">", 2],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 4],
         constraints=[
             [1, -2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="min",
         goal=[2, 3, 5, 6],
         constraints=[
             [1, 2, 3, 1, ">", 2],
             [-2, 1, -1, 3, "<", -3],
         ],
         )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[160, 50],
        constraints=[
            [4, 1, ">", 2],
            [1, 1, ">", 2],
            [5, 1, ">", 4],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[3, 9],
        constraints=[
            [1, 1, ">", 2],
            [1, 4, ">", 3],
            [1, 7, ">", 3],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[2, 2, 1],
        constraints=[
            [2, 2, 4, ">", 16],
            [1, 2, 1, ">", 10],
            [3, 2, 0, ">", 8],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[3, 2, 2, 5],
        constraints=[
            [2, 1, 1, 3, ">", 12],
            [1, 3, 2, 1, ">", 18],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[3, 2, 1, 4],
        constraints=[
            [2, -1, 1, -2, ">", 8],
            [4, 1, 4, 6, ">", 16],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[1, 2, 4, 1],
        constraints=[
            [1, 2, 3, 3, ">", 21],
            [2, 1, 1, 2, ">", 30],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[3, 4, 6],
        constraints=[
            [1, 2, 1, ">", 4],
            [2, -1, 3, ">", 5],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[4, 4, 5],
        constraints=[
            [1, 2, 2, ">", 6],
            [2, 1, 4, ">", 8],
            [4, -2, 3, ">", 12],
        ],
        )
lp_list.append(lp)


lp = LP(qtype="min",
        goal=[7, 8, 9],
        constraints=[
            [1, 2, 3, ">", 48],
            [0, 2, 1, ">", 20],
        ],
        )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 3],
         constraints=[
             [1, 1, 3, ">", 4],
             [2, -1, 1, ">", 3],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 1, 2],
         constraints=[
             [1, 2, 1, ">", 4],
             [2, 1, 1, ">", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 1, 1],
         constraints=[
             [2, 1, 2, ">", 12],
             [1, 2, 1, ">", 9],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 1, 2],
         constraints=[
             [2, 1, 2, ">", 4],
             [1, 7, 1, ">", 7],
         ],
         )
lp_list.append(lp)


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
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 4],
         constraints=[
             [1, 2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[15, 24, 5],
         constraints=[
             [0, 6, 1, ">", 2],
             [5, 2, 1, ">", 1],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[15, 24, 5],
         constraints=[
             [5, 8, 2, ">", 6],
             [5, 2, 1, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[5, 6, 3],
         constraints=[
             [2, 1, 1, ">", 6],
             [2, 1, 2, ">", 10],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[24, 15, 5],
         constraints=[
             [6, 0, 1, ">", 4],
             [2, 5, 1, ">", 2],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 1, 4],
         constraints=[
             [-1, 2, 3, -6, ">", 9],
             [2, 4, 1, 2, ">", 7],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 2, 1, 4],
         constraints=[
             [2, -1, 3, -6, ">", 6],
             [4, 2, 1, 2, ">", 7],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[-5, -35, -20],
         constraints=[
             [-1, 1, 1, ">", 2],
             [1, 3, 0, ">", 3],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 4, 6],
         constraints=[
             [1, 2, 3, ">", 5],
             [1, 1, 1, ">", 3],
         ],
         )
lp_list.append(lp)


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
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 6, 9],
         constraints=[
             [1, 0, 3, ">", 3],
             [0, 2, 2, ">", 5],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 2, 4],
         constraints=[
             [1, 1, 2, ">", 4],
             [2, 1, 3, ">", 5],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[4, 2, 3],
         constraints=[
             [4, 2, 3, ">", 12],
             [3, 1, 2, ">", 10],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [3, 1, 5, ">", 10],
             [1, 3, 2, ">", 12],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[4, 2, 3],
         constraints=[
             [2, 3, 1, ">", 12],
             [1, 2, 4, ">", 10],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[5, 2, 4],
         constraints=[
             [3, 1, 2, ">", 4],
             [6, 3, 2, ">", 10],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[9, 12, 15],
         constraints=[
             [2, 2, 1, ">", 10],
             [2, 3, 1, ">", 12],
             [1, 1, 5, ">", 14],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 3, 2],
         constraints=[
             [1, -2, 3, ">", 4],
             [3, 1, -2, ">", 6],
#             [1, 1, 5, ">", 14],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 2, -1, ">", 3],
             [2, 1, 1, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 5],
         constraints=[
             [2, 1, 2, ">", 8],
             [1, 2, -1, ">", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 4, 5],
         constraints=[
             [1, 2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 4, 5],
         constraints=[
             [1, -2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 5],
         constraints=[
             [-1, 2, 1, ">", 3],
             [2, -1, 3, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 3, 2, ">", 3],
             [2, 1, 3, ">", 2],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 3, 2, ">", 3],
             [2, 1, 3, ">", 2],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[6, 4, 7],
         constraints=[
             [1, 0, 3, ">", 2],
             [3, 2, 1, ">", 4],
             [-1, 2, 2, ">", 5],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 2, 3],
         constraints=[
             [1, 1, 2, ">", 12],
             [2, -1, 1, ">", 10],
             [2, 4, 2, ">", 15],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 2, 4],
         constraints=[
             [1, -1, 1, ">", 2],
             [-1, 2, 0, ">", 3],
             [2, 0, 1, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 2, 1],
         constraints=[
             [1, -1, 1, ">", 2],
             [-1, 2, 0, ">", 3],
             [2, 0, 1, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 5, 7],
         constraints=[
             [2, -1, 1, ">", 14],
             [1, 2, 1, "<", 13],
             [0, 2, -1, ">", 4],
         ],
         )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[-5, -35, -20],
        constraints=[
            [-1, 1, 1, ">", 2],
            [1, 3, 0, ">", 3],
        ],
        )
lp_list.append(lp)


from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()

lp_json_list = []
for lp in lp_list:
    lp_json_list.append(lp.json)

import pickle
with open('lp.bin', 'wb') as f:
    pickle.dump(lp_json_list, f)

with open('lp.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)


for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp2phase = deepcopy(lp)

    lp.solve(method="dual_simplex")

    template = latex_jinja_env.get_template('/utils/lp_simplex.tex')
    tex = template.render(
        question_table_iters=iter(range(1, 5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_answer = True,
        standardized_lp = lp.standardized_LP(),
        pre_description=u"""有对偶单纯形法求解以下线性规划问题
        """,
        lp=lp,
    )

    r.clipboard_append(tex)
    print lp.solve_opt_res_str
    print lp.solutionCommon.nit
