# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env
from latex_utils.utils.lpmodel import LP
from copy import deepcopy
import random, pickle, json
from fractions import Fraction

SAVED_QUESTION_2_iter = "lp_dual_simplex_2_iter.bin"
SAVED_QUESTION_3_iter = "lp_dual_simplex_3_iter.bin"

lp_list = []

# 作业题

n = 3
m = 2


def create_random_lp_dual_simplex(n, m, qtype=None):
    if not qtype:
        qtype = "min"

    if qtype == "max":
        goal_range = range(-10,-1)
    else:
        goal_range = range(1, 10)
    para_range = range(-9, 9)
    b_range = range(1, 20)

    def create_goal():
        goal = []
        for i in range(n):
            goal.append(random.choice(goal_range))
        return goal

    def create_constraint():
        c_sign_list = create_constraints_sign()
        constr_list = []
        j = 0
        while len(constr_list) < m:
            single_constr = []
            for i in range(n):
                single_constr.append(random.choice(para_range))
            single_constr.append(c_sign_list[j])
            j += 1
            single_constr.append(random.choice(b_range))
            constr_list.append(single_constr)
        return constr_list

    def create_constraints_sign():
        return [">"] * m

    def create_sign():
        return [">"] * n

    # if not qtype:
    #     qtype = random.choice(["max", "min"])

    lp = LP(qtype=qtype,
            goal=create_goal(),
            constraints=create_constraint(),
            sign=create_sign(),
            dual=True
            )
    return lp

lp_json_list = []

# iters = 0
# while len(lp_json_list) < 40:
#     if iters % 10000 == 0:
#         print(iters)
#     iters += 1
#     lp = create_random_lp_dual_simplex(n, m, qtype="min")
#     try:
#         lp.solve(method="dual_simplex")
#     except:
#         continue
#     lp_json = lp.json
#     if lp.solutionCommon.nit in [2] and lp.res.status == 0:
#         #print(lp.res)
#         valid = True
#         if abs(lp.res.fun) > 200:
#             valid = False
#             continue
#         for t in lp.solutionPhase2.tableau_list:
#             b = t.reshape(1,(m+1)*(m+n+1)).tolist()[0]
#             for i in b:
#                 if len(str(
#                     Fraction(float(i)).limit_denominator()
#                 )) > 4:
#                     valid = False
#                     break
#
#         if valid:
#             if lp_json not in lp_json_list:
#                 lp_json_list.append(lp_json)
#                 dic = json.loads(lp_json)
#                 print('lp = LP(qtype="%s",' % lp.qtype)
#                 print('        goal=%s,' % lp.goal)
#                 print('        constraints=%s)' % dic["constraints"])
#                 print('lp_list.append(lp)')

lp = LP(qtype="min",
        goal=[3, 5, 1],
        constraints=[[-3, 4, 1, u'>', 9], [-1, 8, 4, u'>', 16]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 4, 2],
        constraints=[[-3, 8, -7, u'>', 16], [-5, 1, -1, u'>', 14]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 5, 1],
        constraints=[[-1, 2, 6, u'>', 11], [-6, 2, 3, u'>', 7]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 2, 4],
        constraints=[[-1, 0, 6, u'>', 13], [-6, 3, 8, u'>', 17]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 6, 2],
        constraints=[[3, 8, -4, u'>', 7], [-6, -8, 8, u'>', 12]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[4, 7, 3],
        constraints=[[-3, 3, 8, u'>', 11], [-4, -7, 2, u'>', 4]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 8, 9],
        constraints=[[4, -6, -8, u'>', 10], [1, -7, 1, u'>', 3]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 8, 4],
        constraints=[[2, -2, 1, u'>', 6], [0, -9, 1, u'>', 9]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[1, 2, 9],
        constraints=[[-6, 8, 4, u'>', 13], [-8, 4, 3, u'>', 8]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 5, 4],
        constraints=[[4, 4, -8, u'>', 12], [2, -2, -6, u'>', 7]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 9, 8],
        constraints=[[6, 2, 3, u'>', 15], [3, -1, -7, u'>', 8]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[7, 9, 8],
        constraints=[[-7, -1, 1, u'>', 13], [-1, 2, 2, u'>', 14]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 1, 7],
        constraints=[[2, -3, -2, u'>', 7], [4, -2, 5, u'>', 13]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 2, 8],
        constraints=[[-1, 6, 8, u'>', 18], [-4, 2, 1, u'>', 15]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 9, 3],
        constraints=[[4, -3, 4, u'>', 6], [5, 3, 8, u'>', 8]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 1, 4],
        constraints=[[-1, -1, 2, u'>', 10], [-3, -6, 8, u'>', 12]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 2, 8],
        constraints=[[2, 3, 8, u'>', 18], [-9, 1, -2, u'>', 17]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 9, 4],
        constraints=[[3, 1, -2, u'>', 4], [1, -6, -3, u'>', 4]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 2, 5],
        constraints=[[8, 6, -2, u'>', 16], [2, 3, -4, u'>', 11]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 6, 3],
        constraints=[[6, 6, 3, u'>', 18], [1, -3, -3, u'>', 9]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 9, 1],
        constraints=[[-3, 4, 3, u'>', 18], [2, -2, -1, u'>', 9]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 2, 1],
        constraints=[[-4, -9, 4, u'>', 8], [-3, -6, 8, u'>', 11]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 3, 4],
        constraints=[[1, 8, -3, u'>', 11], [1, 4, -8, u'>', 9]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 6, 3],
        constraints=[[4, -2, 0, u'>', 16], [6, 1, 3, u'>', 19]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 7, 2],
        constraints=[[8, 4, -4, u'>', 16], [3, -6, -3, u'>', 11]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 6, 3],
        constraints=[[-2, 1, -8, u'>', 2], [7, 7, -7, u'>', 8]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 4, 1],
        constraints=[[-2, 0, 2, u'>', 2], [1, -7, 8, u'>', 7]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 1, 4],
        constraints=[[-1, 1, 2, u'>', 2], [3, -1, 6, u'>', 4]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 8, 2],
        constraints=[[-7, 2, 8, u'>', 5], [-7, 3, 6, u'>', 5]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 2, 2],
        constraints=[[-5, 6, -2, u'>', 13], [6, -6, -3, u'>', 6]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 5, 1],
        constraints=[[5, -4, 2, u'>', 5], [1, -4, 0, u'>', 17]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 4, 1],
        constraints=[[-3, 1, -8, u'>', 2], [-3, 8, -2, u'>', 8]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 5, 1],
        constraints=[[8, 6, -3, u'>', 2], [-1, -7, 1, u'>', 3]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 8, 8],
        constraints=[[4, -8, -6, u'>', 18], [2, -5, 1, u'>', 15]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 9, 3],
        constraints=[[5, 0, -6, u'>', 10], [-2, 0, 3, u'>', 7]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 9, 1],
        constraints=[[-8, 0, 4, u'>', 13], [-1, -6, 8, u'>', 14]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 1, 8],
        constraints=[[-2, 1, -6, u'>', 6], [7, 2, -9, u'>', 7]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 8, 8],
        constraints=[[0, -2, 2, u'>', 6], [4, -6, 3, u'>', 5]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 2, 5],
        constraints=[[6, -4, -3, u'>', 6], [3, -8, 1, u'>', 4]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 9, 3],
        constraints=[[8, 6, 6, u'>', 1], [8, 2, 0, u'>', 6]])
lp_list.append(lp)

lp = LP(qtype="min",
        goal=[1, 7, 1, 4],
        constraints=[[-2, -8, -2, 2, u'>', 14], [8, 2, -2, -6, u'>', 6], [4, -9, 0, -3, u'>', 12]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[1, 3, 9, 5],
        constraints=[[6, -2, -1, 4, u'>', 19], [3, 3, 0, 7, u'>', 11], [1, -1, -3, -9, u'>', 4]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 5, 2, 1],
        constraints=[[2, -5, -4, 8, u'>', 18], [-1, -5, -5, 4, u'>', 10], [1, 5, -3, 0, u'>', 4]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 7, 4, 8],
        constraints=[[0, -2, 2, -4, u'>', 18], [6, 4, -4, -8, u'>', 3], [-3, -3, 4, 4, u'>', 18]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[7, 4, 8, 6],
        constraints=[[0, 1, -4, -5, u'>', 12], [1, 0, 1, 2, u'>', 5], [1, 6, -6, 4, u'>', 18]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 4, 5, 3],
        constraints=[[2, -4, -2, 0, u'>', 8], [1, -6, 2, 6, u'>', 10], [3, -6, 1, 4, u'>', 13]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[4, 6, 5, 2],
        constraints=[[2, -3, -2, 2, u'>', 10], [-6, 0, 5, 0, u'>', 1], [-1, -7, -2, 4, u'>', 12]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 2, 9, 6],
        constraints=[[0, -3, -3, 8, u'>', 5], [8, -9, 5, 8, u'>', 10], [6, -8, 4, 8, u'>', 10]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 4, 4, 8],
        constraints=[[-3, 3, 4, 1, u'>', 14], [6, 0, -8, -4, u'>', 5], [-9, 4, 6, -3, u'>', 9]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 3, 5, 2],
        constraints=[[0, 2, -6, 0, u'>', 8], [3, 1, -7, 1, u'>', 17], [3, -8, 6, 0, u'>', 6]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 3, 3, 6],
        constraints=[[-7, 4, -3, -1, u'>', 2], [-3, 8, -3, 4, u'>', 10], [-3, 0, 3, -1, u'>', 12]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 2, 2, 3],
        constraints=[[-3, 1, 2, -7, u'>', 8], [-3, -5, 1, -1, u'>', 6], [-5, -4, 6, -9, u'>', 9]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 1, 6, 1],
        constraints=[[2, 1, -3, -4, u'>', 7], [7, 6, -1, 4, u'>', 18], [0, 3, -5, -5, u'>', 15]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 9, 1, 4],
        constraints=[[3, -2, 0, 6, u'>', 6], [0, -4, 1, -3, u'>', 2], [6, 5, 2, -4, u'>', 14]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 7, 5, 9],
        constraints=[[4, 5, 4, 6, u'>', 16], [3, -4, 6, 5, u'>', 11], [-1, -2, 1, 0, u'>', 7]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 5, 9, 5],
        constraints=[[-3, -9, -9, 3, u'>', 13], [-1, -4, 0, 2, u'>', 10], [1, 1, -1, 6, u'>', 18]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 7, 1, 4],
        constraints=[[-6, 3, -4, 3, u'>', 18], [-7, -2, -2, 1, u'>', 8], [2, 1, -7, 0, u'>', 6]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 6, 2, 1],
        constraints=[[3, -7, 0, -2, u'>', 6], [6, 2, 2, -9, u'>', 17], [-9, -3, 4, -8, u'>', 13]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 1, 4, 6],
        constraints=[[-6, 1, -9, -1, u'>', 8], [-3, 4, -4, 2, u'>', 12], [2, 2, -3, 8, u'>', 12]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[7, 1, 1, 3],
        constraints=[[-7, 4, -6, 0, u'>', 16], [4, -4, 4, 6, u'>', 10], [5, -4, 8, 3, u'>', 1]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[4, 3, 1, 7],
        constraints=[[2, 2, 0, -2, u'>', 3], [3, 8, 5, 4, u'>', 7], [-8, 6, 5, 2, u'>', 3]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[7, 7, 9, 9],
        constraints=[[6, 8, 4, -6, u'>', 10], [4, 4, 1, -3, u'>', 1], [4, 4, 0, -5, u'>', 10]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 6, 1, 9],
        constraints=[[1, -2, 1, -5, u'>', 14], [-5, 4, 4, -5, u'>', 14], [2, -3, -1, -7, u'>', 13]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 1, 8, 4],
        constraints=[[-5, -4, 4, 4, u'>', 10], [-1, -8, 2, 0, u'>', 7], [7, 4, -8, 8, u'>', 10]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[1, 3, 3, 6],
        constraints=[[1, -5, 0, -1, u'>', 8], [-1, -5, 2, -8, u'>', 18], [-2, -7, 1, -5, u'>', 13]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 1, 6, 1],
        constraints=[[-2, 4, -8, -2, u'>', 17], [-6, 0, 0, 3, u'>', 15], [7, 6, 7, -6, u'>', 15]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 2, 4, 6],
        constraints=[[-4, 6, 6, -4, u'>', 14], [-4, -3, 0, 4, u'>', 2], [5, -3, 3, 1, u'>', 2]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[3, 1, 6, 7],
        constraints=[[6, 6, -6, -1, u'>', 18], [7, 3, -9, -7, u'>', 4], [0, -2, 6, -3, u'>', 12]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 5, 3, 4],
        constraints=[[0, 5, 3, -5, u'>', 3], [6, 3, 5, 3, u'>', 17], [6, 2, 2, -1, u'>', 16]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[5, 7, 3, 1],
        constraints=[[-4, 0, 2, 1, u'>', 13], [-9, -7, 4, 7, u'>', 4], [-9, 1, 1, 0, u'>', 7]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[6, 8, 6, 6],
        constraints=[[0, 6, -8, 8, u'>', 12], [-7, 1, -6, 0, u'>', 5], [6, 1, -7, 2, u'>', 5]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[1, 4, 2, 8],
        constraints=[[-1, 1, 0, -3, u'>', 2], [7, 0, 4, -7, u'>', 8], [-7, 8, 4, -7, u'>', 18]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 8, 1, 2],
        constraints=[[-6, 5, 8, -8, u'>', 18], [-1, -6, 4, -8, u'>', 3], [-2, 5, 0, 4, u'>', 15]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[4, 2, 3, 8],
        constraints=[[-1, -4, 3, 1, u'>', 3], [-2, -3, 6, 8, u'>', 10], [-6, -4, 0, 4, u'>', 3]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 7, 3, 3],
        constraints=[[-2, -9, 0, 3, u'>', 4], [1, 1, -1, 0, u'>', 2], [6, 2, -4, 6, u'>', 18]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[8, 6, 4, 5],
        constraints=[[-5, -2, 4, 2, u'>', 6], [-6, 4, 4, -2, u'>', 19], [-9, 2, 0, -4, u'>', 13]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 6, 8, 6],
        constraints=[[6, 1, 6, 3, u'>', 10], [3, 5, -8, 0, u'>', 4], [0, 0, 0, 3, u'>', 4]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 7, 9, 2],
        constraints=[[-1, 3, -8, 0, u'>', 7], [2, 1, 6, 2, u'>', 10], [-2, -3, -4, 4, u'>', 2]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[2, 7, 5, 2],
        constraints=[[-1, 0, 2, -2, u'>', 4], [1, 1, -1, -5, u'>', 11], [4, 1, 3, -8, u'>', 3]])
lp_list.append(lp)
lp = LP(qtype="min",
        goal=[9, 4, 5, 2],
        constraints=[[-6, 6, -3, 3, u'>', 12], [2, -8, 6, 0, u'>', 10], [-9, -2, -4, 4, u'>', 5]])
lp_list.append(lp)


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
             [2, -1, 1, -3, ">", 3],
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

lp = LP(qtype="max",
        goal=[-5, -35, -20],
        constraints=[
            [-1, 1, 1, ">", 2],
            [1, 3, 0, ">", 3],
        ],
        )


try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
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


final_lp_list1 = []
final_lp_list2 = []
count1 = 0
count2 = 0

for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp2phase = deepcopy(lp)

    lp.solve(method="dual_simplex")

    template = latex_jinja_env.get_template('/utils/lp_dual_simplex.tex')
    tex = template.render(
        question_table_iters=iter(range(1, 5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_answer = True,
        show_2_stage = True,
        standardized_lp = lp.standardized_LP(),
        pre_description=u"""求解以下线性规划问题
        """,
        lp=lp,
    )
    r.clipboard_append(tex)

    if lp.solutionCommon.nit in [2] and lp.res.status == 0:
        #r.clipboard_append(tex)
        final_lp_list1.append(lp.json)
        count1 += 1
    if lp.solutionCommon.nit in [3] and lp.res.status == 0:
        final_lp_list2.append(lp.json)
        count2 += 1

print(count1, count2)

with open(SAVED_QUESTION_2_iter, 'wb') as f:
        pickle.dump(final_lp_list1, f)
with open(SAVED_QUESTION_3_iter, 'wb') as f:
    pickle.dump(final_lp_list2, f)
