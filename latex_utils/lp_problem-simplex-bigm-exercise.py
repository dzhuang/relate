# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy


lp_list = []

lp = LP(qtype="max",
        goal=[3, -1, -1],
        constraints=[
            [1, -2, 1, "<", 10],
            [-4, 1, 2, ">", 4],
            [-2, 0, 1, "=", 1],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[1, 1, -3],
        constraints=[
            [1, -2, 1, "<", 11],
            [2, 1, -4, ">", 3],
            [1, 0, -2, "=", 1],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[3, 2, 1],
        constraints=[
            [1, 1, 1, "=", 50],
            [4, 5, 2, ">", 80],
#            [1, 0, -2, "=", 1],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[3, 7, 3],
        constraints=[
            [1, 4, 2, ">", 8],
            [3, 2, 0, ">", 6],
            #            [1, 0, -2, "=", 1],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="max",
        goal=[2, 3, -5],
        constraints=[
            [1, 1, 1, "=", 7],
            [2, -5, 1, ">", 10],
            #            [1, 0, -2, "=", 1],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[5, -2, -3],
        constraints=[
            [1, 2, 3, "=", 9],
            [2, 1, 1, "=", 5],
            #            [1, 0, -2, "=", 1],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[2, 2, 4],
        constraints=[
            [2, 3, 5, ">", 2],
            [3, 1, 7, "<", 3],
            [1, 4, 6, "<", 5],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[1, 2, 5],
        constraints=[
            [1, -2, 3, "=", 12],
            [2, 3, -1, "=", 6],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[-3, 1, 2],
        constraints=[
            [1, 2, -1, "<", 10],
            [-2, -1, 1, ">", 2],
            [-4, 1, 2, ">", 5],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[3, 4, 5],
        constraints=[
            [1, 2, 3, ">", 5],
            [2, 2, 1, ">", 6],
        ],
        )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[4, 6, -10],
         constraints=[
             [1, 1, 1, "=", 7],
             [2, -5, 1, ">", 10],
             #            [1, 0, -2, "=", 1],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, -1, -1],
         constraints=[
             [1, 1, 1, "<", 4],
             [-2, 1, -1, ">", 2],
             [0, 2, 1, "=", 6],
         ],
         )
lp_list.append(lp)

# # 迭代次数太少，有无穷多最优解
# lp = LP (qtype="min",
#          goal=[2, 3, 1],
#          constraints=[
#              [1, 4, 2, ">", 8],
#              [3, 2, 0, ">", 6],
#          ],
#          )

lp = LP (qtype="min",
         goal=[2, 3, 4],
         constraints=[
             [1, 2, 1, ">", 9],
             [2, -1, 3, ">", 12],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="min",
         goal=[-1, 1, 1],
         constraints=[
             [1, -1, 2, "<", 10],
             [-1, 1, 1, ">", 4],
             [-1, 0, 1, "=", 2],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[3, 5, 4],
         constraints=[
             [1, 0, 2, "<", 4],
             [0, 2, 1, ">", 12],
             [3, 2, 1, "=", 18],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[-3, 0, 1],
         constraints=[
             [-2, 1, -1, ">", 1],
             [0, 3, 1,  "=", 9],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, 2, 4],
         constraints=[
             [2, 1, 1, "<", 3],
             [3, 4, 2, ">", 8],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[-3, 0, 1],
         constraints=[
             [1, 1, 1, "<", 4],
             [-2, 1, -1, ">", 1],
             [0, 3, 1, "=", 9],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[-2, -1, 1],
         constraints=[
             [1, 1, 2, "=", 6],
             [-1, 4, 1, "=", 8],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[3, 1, -1],
         constraints=[
             [1, 1, 1, "<", 4],
             [-2, 1, -1, ">", 1],
             [0, 3, 1, "=", 9],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[-1, -3, 1],
         constraints=[
             [1, 1, 2, "=", 4],
             [-1, 2, 1, "=", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[4, 5, 1],
         constraints=[
             [3, 2, 1, ">", 6],
             [2, 1, 0, "<", 12],
             [1, 1, -1, "=", 5],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[-2, -1, 0],
         constraints=[
             [1, 1, -1, "=", 3],
             [-1, 1, 0, ">", 1],
             [1, 2, 0, "<", 8],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[-3, 1, 1],
         constraints=[
             [1, -2, 1, "<", 11],
             [-4, 1, 2, ">", 3],
             [-2, 0, 1, "=", 1],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[1, 5, 3],
         constraints=[
             [1, 2, 1, "=", 3],
             [2, -1, 1, "=", 5],
         ],
         )
lp_list.append(lp)


# lp = LP (qtype="max",
#          goal=[3, -1, -1],
#          constraints=[
#              [1, -2, 1, "<", 11],
#              [-4, 1, 2, ">", 3],
#              [-2, 0, 1, "=", 1],
#          ],
#          )

lp = LP (qtype="max",
         goal=[2, 3, 1],
         constraints=[
             [2, 4, 3, ">", 10],
             [2, 2, 6, "=", 15],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[-5, 0, 1],
         constraints=[
             [1, 1, 1, "<", 4],
             [-2, 1, -1, ">", 1],
             [0, 3, 1, "=", 9],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[4, 2, 1],
         constraints=[
             [2, 3, 5, ">", 10],
             [2, 5, 7, "<", 20],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[2, 1, 2],
         constraints=[
             [1, 2, 4, ">", 8],
             [1, 1, 1, "=", 6],
         ],
         )
lp_list.append(lp)


# # 迭代次数太少
# lp = LP (qtype="max",
#          goal=[1, 5, 3],
#          constraints=[
#              [1, 2, 1, "=", 5],
#              [2, -1, 0, ">", 4],
#          ],
#          )

# 无可行解
# lp = LP (qtype="max",
#          goal=[10, 15, 12],
#          constraints=[
#              [5, 3, 1, "<", 9],
#              [-5, 6, 15, "<", 15],
#              [2, 1, 1, ">", 5],
#          ],
#          )


lp = LP (qtype="max",
         goal=[2, 3, 1],
         constraints=[
             [3, 5, 2, ">", 20],
             [4, 6, 3, "=", 30],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[1, 2, 1],
         constraints=[
             [2, 3, 1, ">", 12],
             [1, 1, 3, "=", 9],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[-1, 2, 1],
         constraints=[
             [1, 1, 1, "<", 9],
             [2, -1, 0, ">", 6],
             [0, 1, 3, "=", 12],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 1, -2],
         constraints=[
             [1, 2, 3, "<", 12],
             [2, 1, -2, ">", 8],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[1, 2, 3],
         constraints=[
             [1, 1, 2, "<", 12],
             [2, -1, 1, ">", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[2, 3, 1],
         constraints=[
             [2, -1, 3, ">", 6],
             [4, 1, 5, "=", 24],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 1],
         constraints=[
             [1, 3, 4, ">", 8],
             [3, 2, 2, ">", 18],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[2, 3, 1],
         constraints=[
             [1, 4, 2, ">", 8],
             [3, 2, 0, ">", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="min",
         goal=[1, 1, -3],
         constraints=[
             [1, -2, 1, "<", 1],
             [2, 1, -4, ">", 3],
             [1, 0, -2, "=", 1],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[1, 5, 3],
         constraints=[
             [1, 2, 1, "=", 5],
             [2, -1, 1, ">", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[-3, 0, 1],
         constraints=[
             [-2, 1, -1, ">", 1],
             [0, 3, 1, "=", 9],
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
#import dill as pickle
with open('lp.bin', 'wb') as f:
    pickle.dump(lp_json_list, f)

with open('lp.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)

final_lp_list = []

count = 0

import json

json_list = []

for l in lp_json_list_loaded:
    lp_dict = json.loads (l)
    # json_list.append(lp_dict)
    if lp_dict["qtype"] == "max":
        lp_dict["qtype"] = "min"
    else:
        lp_dict["qtype"] = "max"
    json_list.append (lp_dict)

for lp_dict in json_list:
#    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp2phase = deepcopy(lp)

    lp.solve(method="big_m_simplex")
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
        show_2_stage = True, # 显示两阶段法
        show_big_m=True,  # 显示大M法
        standardized_lp = lp.standardized_LP(),
        standardized_lp_2_phase=standardized_lp_2_phase,
        pre_description=u"""
        """,
        lp=lp,
        lp2phase = lp2phase,
        # simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
        # """,
        # simplex_after_description=u"""最优解唯一。
        # """
    )

    r.clipboard_append(tex)
    print("iterations:", lp.solutionCommon.nit)
    if lp.solutionCommon.nit in [3, 4]:
#    if lp.solutionCommon.nit in [3, 4, 5] and lp.qtype=="max":
        final_lp_list.append(lp.json)
        count += 1

print(count)

r.mainloop()

with open('lp_simplex_3_iter_artificial.bin', 'wb') as f:
        pickle.dump(final_lp_list, f)
