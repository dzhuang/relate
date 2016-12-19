# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy


# 作业题

lp_list = []


lp = LP (qtype="max",
         goal=[1, 2, 1],
         constraints=[
             [1, 1, 1, "<", 4],
             [-1, 2, -2, "<", 6],
             [2, 1, 0, "<", 5],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[2, 4],
         constraints=[
             [-1, 2, "<", 4],
             [1, 2, "<", 10],
             [1, -1, "<", 2],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, 1, 2],
         constraints=[
             [4, 3, 8, "<", 12],
             [4, 1, 12, "<", 8],
             [4, -1, 3, "<", 8],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="min",
         goal=[-1, -4, -5],
         constraints=[
             [1, 1, 0, "<", 6],
             [-1, 1, 3, "<", 8],
             [3, 1, 1, "<", 10],
         ],
         )
lp_list.append(lp)


# # 只有两个约束
# lp = LP(qtype="max",
#         goal=[5, 3, 2],
#         constraints=[
#             [1, 1, 1, "<", 80],
#             [10, 2, 3, "<", 100],
#             #[1, -2, 1, "<", 18],
#         ],
#         )

lp = LP(qtype="max",
        goal=[-1, 3, 2],
        constraints=[
            [2, 4, -1, "<", 30],
            [3, 2, 5, "<", 50],
            [1, -3, 4, "<", 40],
        ],
        )
lp_list.append(lp)

# # 求解太复杂
#lp = LP(qtype="max",
#        goal=[-2, 7, 4],
#        constraints=[
#            [4, 6, 4, "<", 120],
#            [2, 2, -2, "<", 9],
#            [2, 1, -3, "<", 10],
#        ],
#        )


# # 求解太复杂
#lp = LP(qtype="max",
#        goal=[2, 4, 1, 1],
#        constraints=[
#            [1, 3, 0, 1, "<", 4],
#            [2, 1, 0, 0, "<", 3],
#            [0, 1, 4, 1, "<", 3],
#        ],
#        )

lp = LP(qtype="max",
        goal=[2, 3, 1],
        constraints=[
            [1, 1, 0, "<", 5],
            [4, -1, 1, "<", 8],
            [0, 0, 1, "<", 2],
        ],
        )
lp_list.append(lp)

# # 初始表检验数相同，且有无穷多最优解
# lp = LP(qtype="max",
#         goal=[1, 1, 1],
#         constraints=[
#             [2, 2, 3, "<", 8],
#             [1, 1, 2, "<", 10],
#             [2, 1, 2, "<", 7],
#         ],
#         )

# # 4 次迭代，太复杂

lp = LP(qtype="max",
        goal=[4, -2, 2],
        constraints=[
            [3, 1, 1, "<", 60],
            [1, -1, 2, "<", 10],
            [2, 2, -2, "<", 40],
        ],
        )
lp_list.append(lp)


# # 太复杂
#lp = LP(qtype="min",
#        goal=[1, -2, -1],
#        constraints=[
#            [1, 1, -2, "<", 15],
#            [2, -1, 3, "<", 18],
#            [-3, 2, 2, "<", 16],
#        ],
#        )


# # 中间计算太复杂
# lp = LP (qtype="max",
#          goal=[4, 3, 2],
#          constraints=[
#              [1, 1, 1, "<", 32],
#              [3, 1, 1, "<", 84],
#              [2, 3, 1, "<", 60],
#          ],
#          )


# 只有两个约束
# lp = LP (qtype="max",
#          goal=[6, -2, 3],
#          constraints=[
#              [2, -1, 2, "<", 2],
#              [1, 0, 4, "<", 4],
#          ],
#          )

lp = LP (qtype="max",
         goal=[-6, 3, 5],
         constraints=[
             [2, 1, 0, "<", 8],
             [-4, -2, 3, "<", 56],
             [1, -1, 1, "<", 16],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="min",
         goal=[1, -2, 3],
         constraints=[
             [1, 1, 1, "<", 15],
             [2, -1, 3, "<", 18],
             [-3, 2, 2, "<", 16],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[4, 8, 3],
         constraints=[
             [2, 0, 3, "<", 8],
             [0, 1, 0, "<", 5],
             [2, 3, 1, "<", 21],
         ],
         )
lp_list.append(lp)





lp = LP (qtype="max",
         goal=[3, 2, 4],
         constraints=[
             [1, 0, 1, "<", 6],
             [2, 3, 0, "<", 8],
             [1, 1, 2, "<", 10],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[2, 5, 5],
         constraints=[
             [1, 1, 3, "<", 8],
             [1, 3, 1, "<", 20],
             [3, 2, 1, "<", 15],
         ],
         )
lp_list.append(lp)

lp = LP(qtype="max",
        goal=[8, 4, 5],
        constraints=[
            [3, 2, 1, "<", 20],
            [1, 1, 2, "<", 10],
            [5, 4, 1, "<", 40],
        ],
        )
lp_list.append(lp)

lp = LP(qtype="max",
        goal=[1, 2, 1],
        constraints=[
            [1, 1, -2, "<", 5],
            [3, 1, 4, "<", 20],
            [-1, 2, 2, "<", 25],
        ],
        )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[4, 3, 2],
         constraints=[
             [1, 1, 1, "<", 16],
             [4, 1, 1, "<", 40],
             [2, 3, 1, "<", 30],
         ],
         )
lp_list.append(lp)

# -------------------------------------------------------------

lp = LP (qtype="max",
         goal=[3, 1, 3],
         constraints=[
             [2, 1, 1, "<", 2],
             [1, 2, 3, "<", 5],
             [2, 2, 1, "<", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[3, 6, 2],
         constraints=[
             [1, 1, -1, "<", 6],
             [3, 4, 1, "<", 16],
             [-1, 4, 1, "<", 8],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, 2, 3],
         constraints=[
             [1, 1, 1, "<", 80],
             [1, 2, 0, "<", 100],
             [0, 0, 1, "<", 50],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, -1, 3, 1],
         constraints=[
             [1, 2, 1, 0, "<", 12],
             [2, -1, 0, 1, "<", 10],
             [0, 0, 1, 1, "<", 8]
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[12, 8, 5],
         constraints=[
             [3, 2, 1, "<", 20],
             [1, 1, 1, "<", 11],
             [12, 4, 1, "<", 48],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, -3, 4],
         constraints=[
             [1, 4, -2, "<", 20],
             [-3, -1, 3, "<", 30],
             [2, 1, 1, "<", 16],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, 5, 1],
         constraints=[
             [1, 0, 1, "<", 4],
             [0, 1, 0, "<", 6],
             [3, 2, 1, "<", 18],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[-1, 2, 3],
         constraints=[
             [1, 2, -2, "<", 20],
             [-2, 1, 2, "<", 36],
             [4, 3, 1, "<", 63],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="min",
         goal=[1, -2, 3],
         constraints=[
             [1, 1, 1, "<", 15],
             [2, -1, 3, "<", 18],
             [-3, 2, 2, "<", 16],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, 5, 6],
         constraints=[
             [-1, -2, 1, "<", 8],
             [1, 3, 0, "<", 7],
             [3, 2, 1, "<", 16],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[-2, 3, 4],
         constraints=[
             [1, 2, 0, "<", 12],
             [1, 3, 1, "<", 18],
             [0, 0, 1, "<", 4],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[5, 3, 1],
         constraints=[
             [1, 1, 0, "<", 17],
             [1, 1, 3, "<", 24],
             [3, 1, 1, "<", 15],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[12, 8, 5],
         constraints=[
             [3, 2, 1, "<", 18],
             [1, 1, 1, "<", 11],
             [9, 4, 1, "<", 36],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, 2, 1],
         constraints=[
             [1, 1, -2, "<", 10],
             [2, -1, 4, "<", 8],
             [-1, 2, -4, "<", 4],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[6, -3, 5],
         constraints=[
             [2, -2, 3, "<", 20],
             [3, 4, -2, "<", 30],
             [6, 5, 4, "<", 40],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[3, 2, 1],
         constraints=[
             [2, 1, 1, "<", 2],
             [2, 11, 2, "<", 6],
             [3, 4, 2, "<", 8],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="min",
         goal=[1, -2, 1],
         constraints=[
             [1, 1, -2, "<", 10],
             [2, -1, 4, "<", 8],
             [-1, 2, -4, "<", 4],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, 3, 4],
         constraints=[
             [3, 2, 0, "<", 12],
             [0, 1, 3, "<", 18],
             [2, 1, 1, "<", 13],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, 3, 2],
         constraints=[
             [1, 2, -1, "<", 16],
             [1, 2, 1, "<", 32],
             [2, 3, 2, "<", 60],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[6, -3, 3],
         constraints=[
             [2, 1, 0, "<", 8],
             [-4, -2, 3, "<", 14],
             [1, -2, 1, "<", 18],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[10, 15, 12],
         constraints=[
             [5, 3, 1, "<", 18],
             [-1, 1, 3, "<", 3],
             [2, 1, 1, "<", 6],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[3, 4, 5, 2],
         constraints=[
             [1, 3, 2, -2, "<", 4],
             [2, 1, 2, 2, "<", 8],
             [3, 2, 1, 3, "<", 7],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[3, 2, 5],
         constraints=[
             [1, 2, 1, "<", 40],
             [3, 0, 2, "<", 60],
             [1, 4, 0, "<", 30],
         ],
         )
lp_list.append(lp)

lp = LP(qtype="max",
       goal=[2, 4, 1, 1],
       constraints=[
           [1, 2, 0, 1, "<", 4],
           [2, 1, 0, 0, "<", 9],
           [0, 1, 4, 1, "<", 12],
       ],
       )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, 3, 4],
         constraints=[
             [2, 3, 2, "<", 27],
             [2, 2, -2, "<", 8],
             [3, 1, 2, "<", 10],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[4, 5, 3],
         constraints=[
             [1, 1, 1, "<", 6],
             [3, 6, 2, "<", 24],
             [3, 2, -1, "<", 16],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, 4, 5],
         constraints=[
             [2, 2, 0, "<", 3],
             [-1, 1, 3, "<", 9],
             [3, 1, 1, "<", 10],
         ],
         )
lp_list.append(lp)

lp = LP(qtype="max",
        goal=[3, 5, 4],
        constraints=[
            [1, 0, 2, "<", 4],
            [0, 2, 1, "<", 12],
            [3, 2, 1, "<", 18],
        ],
        )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, 6, 5],
         constraints=[
             [1, 1, -2, "<", 20],
             [1, 0, 1, "<", 15],
             [2, 1, 3, "<", 30],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, 1, 1],
         constraints=[
             [1, 1, 1, "<", 10],
             [5, 2, 0, "<", 25],
             [0, 1, 2, "<", 8],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[4, 0, 3],
         constraints=[
             [1, -1, 0, "<", 2],
             [2, 0, 1, "<", 5],
             [1, 1, 1, "<", 4],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[5, 0, 3],
         constraints=[
             [1, -1, 0, "<", 2],
             [2, 0, 1, "<", 5],
             [1, 1, 1, "<", 4],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, 3, 4],
         constraints=[
             [1, 2, -1, "<", 20],
             [2, 1, 2, "<", 30],
             [-1, 3, 2, "<", 60],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[5, 3, 2],
         constraints=[
             [1, 1, 1, "<", 16],
             [10, 4, 5, "<", 60],
             [1, -1, 3, "<", 15],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[2, -1, 1],
         constraints=[
             [3, 1, 1, "<", 60],
             [1, -1, 2, "<", 10],
             [1, 1, -1, "<", 20],
         ],
         )
lp_list.append(lp)

# 4 次迭代
lp = LP (qtype="max",
         goal=[6, 1, 2],
         constraints=[
             [1, 3, 1, "<", 12],
             [2, 0, 1, "<", 6],
             [1, 1, 0, "<", 2],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[1, 2, 1],
         constraints=[
             [1, 1, -1, "<", 10],
             [-1, 2, 1, "<", 12],
             [0, 3, 2, "<", 20],
         ],
         )
lp_list.append(lp)


# 4 次迭代
lp = LP (qtype="max",
         goal=[1, 2, 1],
         constraints=[
             [1, 1, -1, "<", 10],
             [-1, 2, 1, "<", 12],
             [1, 3, 2, "<", 20],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[1, 1, 2],
         constraints=[
             [1, 1, 0, "<", 12],
             [0, 2, 1, "<", 18],
             [1, -1, 1, "<", 6],
         ],
         )
lp_list.append(lp)


lp = LP (qtype="max",
         goal=[3, 5, 1],
         constraints=[
             [2, 3, -1, "<", 32],
             [3, 1, 1, "<", 30],
             [-1, 2, 3, "<", 22],
         ],
         )
lp_list.append(lp)

# 4 次迭代
lp = LP (qtype="max",
         goal=[10, 15, 3],
         constraints=[
             [1, 2, 0, "<", 10],
             [1, 1, 1, "<", 9],
             [0, 3, 1, "<", 15],
         ],
         )
lp_list.append(lp)

lp = LP (qtype="max",
         goal=[5, 2, 3],
         constraints=[
             [1, 0, 1, "<", 16],
             [1, 2, 1, "<", 32],
             [2, 3, 2, "<", 60],
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

lp_json_list = []
for lp in lp_list:
    lp_json_list.append(lp.json)
#lp_json_list.append(lp2.json)
#print(lp_json_list)

print(lp_json_list)


import pickle
#import dill as pickle
with open('lp.bin', 'wb') as f:
    pickle.dump(lp_json_list, f)

with open('lp.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)

final_lp_list = []

count = 0

for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp = lp
    lp2phase = deepcopy(lp)

    lp.solve(method="simplex")
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
        #standardized_lp = lp.standardized_LP(),
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

    #r.clipboard_append(tex)
    #print(lp.solve_opt_res_str)
    print("iterations:", lp.solutionCommon.nit)
    #if lp.solutionCommon.nit in [2]:
    if lp.solutionCommon.nit in [3, 4]: # and lp.qtype=="max":
        final_lp_list.append(lp.json)
        count += 1
        r.clipboard_append(tex)

print(count)

with open('lp_simplex_3_iter_max_min.bin', 'wb') as f:
        pickle.dump(final_lp_list, f)