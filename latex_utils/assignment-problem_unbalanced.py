# -*- coding: utf-8 -*-

from .utils.latex_utils import latex_jinja_env
import numpy as np
import random
from .utils.hungarian import linear_sum_assignment

try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
    from Tkinter import Tk


SAVED_QUESTION = "assignment_unbalanced.bin"
STEP_RANGE = [12, 16]
MAX_RETRY_ITERATION = 1000
N = 4
M = 5
r = Tk()
r.withdraw()
r.clipboard_clear()

def is_qualified_question(cost, mem_cost_list, saved_question=SAVED_QUESTION):

    # with open(saved_question, 'rb') as f:
    #     cost_list_loaded = pickle.load(f)

    qualified = False
    #r = Tk()
    (row_ind, col_ind), nstep = linear_sum_assignment(cost)

    if nstep in STEP_RANGE:
        qualified = True

    if not qualified:
        # 问题不合格
        return False

    question_exist = False
    for i, c in enumerate(mem_cost_list):
        if np.all(cost==c):
            print("----------------------question exists-------------------")
            question_exist = True
            return False
            break

    if not question_exist:
        suggestion = "cost=%s" % repr(cost[:-1])
        suggestion = suggestion.replace("array", "np.array")
        print(suggestion)
        r.clipboard_append(suggestion)
        r.clipboard_append("\n")
        r.clipboard_append("cost_list.append(cost)")
        r.clipboard_append("\n")
        r.clipboard_append("\n")

        #raise ValueError("Please add above problem")

    print(cost)
    print("number of steps:", nstep)

    return True

cost_list = []


# print(len(cost_list))

r = Tk()
r.withdraw()
r.clipboard_clear()


# for i, cost in enumerate(cost_list_loaded):
#     success = False

    # if is_qualified_question(cost):
    #     print("i", i)
    #     count_unbalanced += 1
    # else:

def generate_problem():
    n = 0
    mem_cost_list = []
    while n < 100:
        cost = np.random.randint(2,20,(N,M))
        cost_last = cost[N-1,:]
        cost = np.vstack([cost, cost_last])

        if is_qualified_question(cost, mem_cost_list):
            n += 1
            mem_cost_list.append(cost)

#generate_problem()

cost=np.array([[10, 13,  6, 17, 12],
       [ 3,  7, 11,  6, 12],
       [ 3, 10, 13, 19, 18],
       [ 9, 12, 14,  5, 15]])
cost_list.append(cost)

cost=np.array([[ 5, 12,  9,  7,  5],
       [15, 12,  6,  3,  2],
       [17, 11,  8, 19, 19],
       [16, 17, 17, 19,  5]])
cost_list.append(cost)

cost=np.array([[ 8,  8, 14, 19,  2],
       [ 2,  3,  2, 16, 15],
       [16, 12,  7, 18, 10],
       [ 7, 12, 15, 10, 12]])
cost_list.append(cost)

cost=np.array([[11,  9,  5,  4, 18],
       [ 9,  9,  2,  2,  8],
       [14,  8, 17,  5, 16],
       [ 8,  7,  4, 13,  2]])
cost_list.append(cost)

cost=np.array([[ 7, 11,  8, 18, 15],
       [12, 15,  6,  4, 11],
       [15,  5,  3, 10, 15],
       [ 5, 19,  7, 14,  7]])
cost_list.append(cost)

cost=np.array([[ 5, 16, 15, 12, 18],
       [16, 14,  2, 16, 18],
       [12,  8, 15, 15, 17],
       [ 8, 11, 10, 18, 14]])
cost_list.append(cost)

cost=np.array([[13, 10, 17,  5, 14],
       [ 8,  4, 17, 19, 18],
       [ 4, 15, 11, 11, 14],
       [ 8, 14, 15, 17, 11]])
cost_list.append(cost)

cost=np.array([[ 7,  8,  3,  7, 19],
       [ 7, 17,  7,  3, 10],
       [18, 13, 18,  4,  8],
       [12,  6,  7, 13,  5]])
cost_list.append(cost)

cost=np.array([[ 9, 12, 12, 18, 16],
       [ 2,  7,  8,  7, 14],
       [10, 16,  8, 10, 11],
       [10, 10,  4, 17,  4]])
cost_list.append(cost)

cost=np.array([[ 7,  9,  7, 19, 10],
       [ 8, 19, 13, 15,  9],
       [13, 17, 10,  3,  4],
       [17, 13, 18, 16,  9]])
cost_list.append(cost)

cost=np.array([[13, 13,  6, 16,  5],
       [15,  9, 14,  5, 16],
       [ 9, 17,  3, 17,  8],
       [17, 10,  8, 14, 10]])
cost_list.append(cost)

cost=np.array([[18,  8,  2,  6, 15],
       [19,  2, 13,  6, 15],
       [15, 18,  9,  9,  7],
       [ 7, 13,  3, 16, 15]])
cost_list.append(cost)

cost=np.array([[ 5,  7, 17,  8, 17],
       [ 4,  7,  5,  2, 19],
       [18, 13, 13, 15, 13],
       [18, 16, 13,  5, 17]])
cost_list.append(cost)

cost=np.array([[ 9, 15,  9,  6,  2],
       [ 8,  9, 19,  3, 13],
       [ 3, 16, 17,  2, 14],
       [19, 18,  2, 18,  4]])
cost_list.append(cost)

cost=np.array([[19, 19,  8, 10,  8],
       [18,  2, 15, 12, 13],
       [ 4, 19,  8, 12, 16],
       [ 9, 15,  8, 17,  9]])
cost_list.append(cost)

cost=np.array([[11, 15, 16, 18, 14],
       [10,  8,  7, 17,  5],
       [11,  3,  8,  6, 10],
       [ 3, 11, 17,  5,  8]])
cost_list.append(cost)

cost=np.array([[ 9, 18, 10, 14, 16],
       [ 5, 17, 11,  7, 15],
       [18,  9,  6, 13,  9],
       [18, 14, 12, 19,  5]])
cost_list.append(cost)

cost=np.array([[ 5, 13, 16, 16, 10],
       [ 5, 12, 12, 11,  4],
       [11, 11, 12,  4,  6],
       [10,  8, 18,  6, 16]])
cost_list.append(cost)

cost=np.array([[ 9,  2,  3, 16,  7],
       [ 8, 10, 11,  5, 18],
       [19,  4,  5, 14, 19],
       [ 5, 17,  3,  9, 16]])
cost_list.append(cost)

cost=np.array([[13, 13, 16,  4, 11],
       [ 5,  9,  5,  2,  9],
       [ 3,  2, 18,  6,  8],
       [ 3, 14,  9, 13, 12]])
cost_list.append(cost)

cost=np.array([[ 3, 12, 19,  7, 15],
       [ 6, 15, 18, 15, 16],
       [ 9,  8, 11,  5, 10],
       [18, 17, 19, 15,  7]])
cost_list.append(cost)

cost=np.array([[10, 15, 10, 13, 19],
       [ 9,  3, 13, 12,  9],
       [12,  4,  9, 17,  2],
       [12, 15, 14, 18, 17]])
cost_list.append(cost)

cost=np.array([[10,  7, 12, 11,  9],
       [17, 18,  4, 16,  9],
       [ 3, 17, 14, 12, 12],
       [18,  5, 15, 17, 12]])
cost_list.append(cost)

cost=np.array([[12,  5,  9,  2,  4],
       [18, 18,  2, 10,  9],
       [15,  9,  9,  9, 11],
       [15, 16, 11,  4,  7]])
cost_list.append(cost)

cost=np.array([[ 9,  2, 11, 17,  8],
       [13, 17, 15, 12, 11],
       [ 7, 14, 14, 14,  5],
       [17, 18, 18,  5, 17]])
cost_list.append(cost)

cost=np.array([[ 7, 13, 13, 15, 15],
       [ 6,  6, 13,  4,  2],
       [10,  8, 11,  6, 12],
       [ 2, 15,  3,  5,  3]])
cost_list.append(cost)

cost=np.array([[ 4, 19, 16, 10,  9],
       [17, 13, 15, 10, 14],
       [11, 19,  6, 11, 18],
       [12, 18, 19, 15, 15]])
cost_list.append(cost)

cost=np.array([[ 4, 15,  5, 17, 10],
       [11,  2, 18, 18, 11],
       [18, 13, 10, 19, 19],
       [10,  2, 11, 18, 19]])
cost_list.append(cost)

cost=np.array([[15,  8, 16, 11,  7],
       [18, 16,  4, 16, 16],
       [ 2, 10,  9,  3, 18],
       [18, 19, 15, 18,  5]])
cost_list.append(cost)

cost=np.array([[18,  6,  5, 16, 19],
       [18,  9, 15, 11,  8],
       [15,  5, 15,  8, 14],
       [13, 16,  8, 14,  6]])
cost_list.append(cost)

cost=np.array([[ 8, 13,  4, 17,  8],
       [13, 14, 11, 15, 12],
       [18,  5,  7, 19, 14],
       [13, 18, 12,  7, 18]])
cost_list.append(cost)

cost=np.array([[ 5, 12,  6,  5,  9],
       [13, 18,  4,  4,  4],
       [ 3, 16,  7, 19, 10],
       [15, 18, 14, 13, 19]])
cost_list.append(cost)

cost=np.array([[ 5, 14, 12, 19,  8],
       [11, 18,  3, 10, 15],
       [16, 16,  2, 15, 16],
       [14,  2,  2, 16,  3]])
cost_list.append(cost)

cost=np.array([[18,  9, 10,  6, 11],
       [ 7, 18, 10,  4, 15],
       [ 5,  9,  4, 11, 13],
       [ 2, 10,  9,  6,  3]])
cost_list.append(cost)

cost=np.array([[17, 14,  4, 16,  3],
       [ 3, 12, 18,  7, 19],
       [ 6, 12, 15, 10,  4],
       [17,  9, 12, 13, 15]])
cost_list.append(cost)

cost=np.array([[16,  7, 14, 15,  6],
       [ 4,  8, 13, 14, 15],
       [ 6, 12, 15, 14,  5],
       [ 4,  2, 11,  7,  3]])
cost_list.append(cost)

cost=np.array([[ 5,  6, 14,  6,  7],
       [ 8,  8, 16,  2,  4],
       [13, 10,  8, 10,  4],
       [13, 12,  4,  3,  4]])
cost_list.append(cost)

cost=np.array([[10,  5,  5, 16, 18],
       [14, 14, 17, 15,  4],
       [ 9, 18,  4, 10,  4],
       [19, 17, 10, 16, 17]])
cost_list.append(cost)

cost=np.array([[ 8, 19, 19,  8,  7],
       [ 3, 13,  9,  4,  9],
       [11, 18, 19, 14, 10],
       [ 9,  3, 19, 12, 19]])
cost_list.append(cost)

cost=np.array([[17, 10, 10, 15, 11],
       [13,  7,  3, 13, 17],
       [14,  5, 10,  8,  8],
       [ 2, 11, 12, 12, 11]])
cost_list.append(cost)

cost=np.array([[13,  8,  7, 11,  4],
       [ 4, 16, 13, 12,  6],
       [13, 12, 13, 15,  9],
       [ 6,  9,  4,  3,  5]])
cost_list.append(cost)

cost=np.array([[19, 19,  8,  3,  3],
       [ 2,  5,  4, 16, 13],
       [19, 12, 18, 10, 15],
       [ 5, 15, 12,  6,  3]])
cost_list.append(cost)

cost=np.array([[ 2,  6, 13,  6, 19],
       [ 3,  3,  6, 14, 19],
       [ 2,  8, 17,  8, 12],
       [16,  8,  9,  5, 12]])
cost_list.append(cost)

cost=np.array([[13,  3,  7, 13,  3],
       [ 7,  4, 11,  4, 15],
       [ 8,  6,  2, 19, 13],
       [14,  3, 19,  2,  8]])
cost_list.append(cost)

cost=np.array([[ 5,  9,  5,  9,  5],
       [11, 12, 11,  4,  7],
       [ 7,  6, 15, 13, 13],
       [19,  3, 15, 15, 16]])
cost_list.append(cost)

cost=np.array([[15, 15,  5, 15, 13],
       [15,  4,  7,  7,  6],
       [19, 17, 10, 16, 10],
       [15,  4,  5, 10, 19]])
cost_list.append(cost)

cost=np.array([[ 7,  6, 16,  7, 17],
       [ 7, 13, 12, 17, 13],
       [16,  2,  6, 18,  4],
       [ 6,  3,  4, 12,  2]])
cost_list.append(cost)

cost=np.array([[12,  3,  7, 14, 12],
       [ 7, 19, 17, 11,  3],
       [11, 11,  7, 12, 14],
       [15, 12,  8,  9,  9]])
cost_list.append(cost)

cost=np.array([[19,  6, 15, 16, 13],
       [18,  4,  9, 15, 15],
       [ 8,  7, 14,  8,  7],
       [10, 11, 19,  2,  2]])
cost_list.append(cost)

cost=np.array([[19,  5, 12,  5, 11],
       [19,  5,  6, 10,  8],
       [ 2,  5,  9, 12,  3],
       [ 7,  6,  5, 19,  7]])
cost_list.append(cost)

cost=np.array([[10,  3, 13, 14,  9],
       [15,  2,  7, 17,  6],
       [18, 13,  7, 14, 16],
       [ 9, 19,  9,  7, 19]])
cost_list.append(cost)

cost=np.array([[ 7,  6,  4, 16,  8],
       [ 4,  5,  8,  9, 18],
       [11,  6,  5, 11,  3],
       [14, 11,  7,  9, 10]])
cost_list.append(cost)

cost=np.array([[ 4, 13, 14, 13, 11],
       [ 2,  6, 14,  7, 18],
       [14,  8,  2,  9, 16],
       [17, 10,  8,  2, 13]])
cost_list.append(cost)

cost=np.array([[ 7,  3,  6, 16,  9],
       [ 2,  8,  3, 11, 17],
       [ 7,  9, 16, 13,  9],
       [ 9, 18, 16,  2, 12]])
cost_list.append(cost)

cost=np.array([[17,  4,  6, 17, 18],
       [ 6, 19,  5, 11,  4],
       [12,  6, 15, 18,  5],
       [ 3, 17, 11,  8, 19]])
cost_list.append(cost)

cost=np.array([[ 9, 12,  7, 13, 18],
       [16,  8, 15,  4,  7],
       [13,  8,  7,  2, 10],
       [19,  2, 17, 18,  9]])
cost_list.append(cost)

cost=np.array([[18, 19, 12, 11, 12],
       [12, 11,  2, 16, 17],
       [12,  4, 18, 19, 14],
       [ 4,  2, 10,  3,  7]])
cost_list.append(cost)

cost=np.array([[ 3,  8, 12,  5, 10],
       [ 4,  7,  9, 11, 15],
       [17, 19,  8,  2,  4],
       [10, 15,  6, 13, 13]])
cost_list.append(cost)

cost=np.array([[ 4, 17,  4, 12, 14],
       [12, 12,  2, 12, 16],
       [17,  4,  3, 16, 11],
       [16,  8, 13,  2,  5]])
cost_list.append(cost)

cost=np.array([[11, 10, 11,  3, 11],
       [ 8, 11, 10, 12, 14],
       [15,  5, 16,  2,  3],
       [15,  3,  5, 17, 14]])
cost_list.append(cost)

cost=np.array([[ 6, 14, 17, 12,  7],
       [15, 11, 10,  4,  5],
       [16, 13, 19,  3,  6],
       [ 7,  8, 13, 19,  6]])
cost_list.append(cost)

cost=np.array([[ 7,  7,  7,  5,  8],
       [18, 15, 17,  5,  6],
       [ 3, 18, 13,  5, 16],
       [ 7,  3, 16, 14, 13]])
cost_list.append(cost)

cost=np.array([[14,  4,  5, 16, 18],
       [ 7, 13, 13, 11,  7],
       [ 3,  3, 10,  5,  9],
       [16,  9,  6, 10, 16]])
cost_list.append(cost)

cost=np.array([[19, 11,  8, 12, 11],
       [17, 19,  7,  2,  9],
       [ 8,  9,  2,  8, 11],
       [ 6,  2, 13,  7, 14]])
cost_list.append(cost)

cost=np.array([[11,  2,  3, 13, 19],
       [13, 17,  7, 14, 15],
       [15, 13, 11, 19, 15],
       [12,  7, 17,  7, 13]])
cost_list.append(cost)

cost=np.array([[13,  8, 14, 17,  5],
       [19,  9,  2, 16, 17],
       [10, 15, 10, 14, 12],
       [ 7, 14,  7, 19, 19]])
cost_list.append(cost)

cost=np.array([[ 8, 11, 13,  8, 15],
       [12,  4,  6,  4, 16],
       [11, 11, 13,  4, 18],
       [ 3,  7, 17, 18, 17]])
cost_list.append(cost)

cost=np.array([[ 5,  6,  3,  7, 14],
       [ 8, 11,  3, 17, 15],
       [18, 17,  6, 18,  6],
       [14,  3,  4, 18, 15]])
cost_list.append(cost)

cost=np.array([[13,  7,  2, 12, 16],
       [19, 18, 16, 12,  5],
       [14, 12, 10, 11,  6],
       [ 6,  9, 18,  7, 13]])
cost_list.append(cost)

cost=np.array([[10,  9, 14, 19,  8],
       [19, 19, 17,  6, 11],
       [ 9, 16, 12,  7,  9],
       [ 6, 16,  7, 17, 12]])
cost_list.append(cost)

cost=np.array([[10, 17,  6, 13, 18],
       [17,  3,  9,  4,  9],
       [11,  7,  4, 18, 10],
       [18,  6, 10,  3,  8]])
cost_list.append(cost)

cost=np.array([[ 7, 13, 11, 16,  6],
       [13, 13,  8, 16,  7],
       [12, 15, 16, 11, 16],
       [ 8,  5,  3, 10, 12]])
cost_list.append(cost)

cost=np.array([[12,  4, 13,  6,  8],
       [10,  2,  3, 17,  6],
       [12,  6, 19,  2,  7],
       [14,  7, 18, 18,  3]])
cost_list.append(cost)

cost=np.array([[ 3, 18,  9, 10,  4],
       [ 6, 18,  4, 12,  5],
       [ 3, 10,  8,  8, 11],
       [13, 11,  8, 16,  8]])
cost_list.append(cost)

cost=np.array([[13, 19, 13,  4, 10],
       [ 5, 16, 17,  9,  5],
       [14, 18, 16, 19,  9],
       [ 9,  8, 15,  9,  5]])
cost_list.append(cost)

cost=np.array([[15, 11,  5, 17, 15],
       [18,  2, 14, 10, 10],
       [11, 19,  2, 15, 12],
       [13, 16, 11,  5, 16]])
cost_list.append(cost)

cost=np.array([[ 5,  2, 15,  7, 13],
       [ 7, 18, 15, 17, 19],
       [17, 17,  6,  8,  6],
       [14,  2,  6,  9, 17]])
cost_list.append(cost)

cost=np.array([[ 9,  3, 10,  7,  6],
       [12, 15, 15, 11,  8],
       [19, 16,  7, 19, 16],
       [13,  2, 14, 16,  4]])
cost_list.append(cost)

cost=np.array([[19,  2,  6, 17,  8],
       [17,  8, 13,  2,  9],
       [10,  6, 17, 12, 16],
       [ 3, 11, 15,  9,  6]])
cost_list.append(cost)

cost=np.array([[ 8,  3, 18, 17, 10],
       [15, 19, 10,  3, 19],
       [ 3, 12,  5,  2,  3],
       [ 8, 10,  6, 13,  3]])
cost_list.append(cost)

cost=np.array([[19,  7, 15, 12, 12],
       [14,  5,  5, 12,  7],
       [10,  7,  2, 12,  7],
       [ 3, 16, 17, 15, 11]])
cost_list.append(cost)

cost=np.array([[13, 19,  4, 10, 15],
       [ 5, 19, 15, 11, 11],
       [13, 14,  4,  4, 12],
       [ 5, 12,  5, 11, 14]])
cost_list.append(cost)

cost=np.array([[ 3,  9, 16, 16,  2],
       [ 3,  3, 10, 16, 11],
       [11,  2,  6, 14, 17],
       [14, 13, 10, 12,  7]])
cost_list.append(cost)

cost=np.array([[11, 14, 17,  7,  5],
       [ 6, 14, 19, 14, 14],
       [ 4,  2, 17,  7, 14],
       [10, 18, 16, 19,  6]])
cost_list.append(cost)

cost=np.array([[12, 13,  2, 16,  3],
       [15,  7,  8,  7,  7],
       [ 3,  9,  3,  8,  3],
       [ 4,  2, 11, 11,  8]])
cost_list.append(cost)

cost=np.array([[18, 16,  6,  3,  2],
       [ 4,  9,  9, 14, 18],
       [ 3, 13,  9, 10,  6],
       [12, 19,  9,  6, 17]])
cost_list.append(cost)

cost=np.array([[ 6, 15,  3, 17, 12],
       [ 2,  6,  2, 15, 12],
       [ 3,  5,  2,  9,  2],
       [13, 15,  8, 10, 17]])
cost_list.append(cost)

cost=np.array([[10, 10, 14, 12, 13],
       [ 8,  2,  9, 10,  7],
       [ 9, 19, 16, 13, 16],
       [12, 19,  6, 15,  5]])
cost_list.append(cost)

cost=np.array([[10, 13, 13,  4,  2],
       [14, 13, 10,  8,  6],
       [ 4, 19, 14, 13, 10],
       [ 9, 15,  4, 12,  4]])
cost_list.append(cost)

cost=np.array([[18, 16, 15, 12,  5],
       [ 9, 15,  3, 11, 12],
       [19, 11,  5,  6,  4],
       [12, 12, 14,  6, 13]])
cost_list.append(cost)

cost=np.array([[ 8,  5,  4, 15,  9],
       [17,  2,  3, 16,  9],
       [17, 17, 19,  3, 14],
       [ 4, 15,  3, 14, 13]])
cost_list.append(cost)

cost=np.array([[19,  7,  8,  3, 16],
       [ 3, 16, 17,  6, 12],
       [18, 16,  8,  5, 13],
       [18, 12, 12, 12, 10]])
cost_list.append(cost)

cost=np.array([[17,  6,  4, 10,  8],
       [ 6, 14, 10,  2,  7],
       [11, 16,  8, 12, 16],
       [ 9, 18, 17, 17,  6]])
cost_list.append(cost)

cost=np.array([[12,  2,  8, 13, 16],
       [18,  7,  7, 16, 15],
       [19,  9, 13, 13, 15],
       [12, 19, 14, 12, 11]])
cost_list.append(cost)

cost=np.array([[14,  4,  9,  7,  4],
       [17,  2,  5,  7,  6],
       [15, 10,  3, 18,  8],
       [13, 17, 14, 11,  9]])
cost_list.append(cost)

cost=np.array([[ 8, 19,  7, 10,  9],
       [ 3, 13, 10, 16,  5],
       [13, 12, 10, 10, 16],
       [ 2,  6, 15, 17, 15]])
cost_list.append(cost)

cost=np.array([[ 6, 18, 15, 16, 10],
       [10, 17, 12,  6,  5],
       [10,  5, 17,  9, 17],
       [ 4, 15, 14, 11,  5]])
cost_list.append(cost)

cost=np.array([[14, 12,  2,  6,  2],
       [ 3, 10,  5, 18,  2],
       [ 2,  6, 19, 10,  6],
       [ 3, 11, 16, 12,  6]])
cost_list.append(cost)

cost=np.array([[16, 14,  7,  9,  6],
       [ 6,  3,  9,  5,  7],
       [ 9, 17,  6, 19, 12],
       [16,  8,  7,  7,  2]])
cost_list.append(cost)

cost=np.array([[ 7, 13,  6, 15,  9],
       [10,  6, 18,  2,  7],
       [10,  5,  2,  2,  3],
       [11, 14, 14, 13,  7]])
cost_list.append(cost)


import pickle
#import dill as pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(cost_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    cost_list_loaded = pickle.load(f)

count_unbalanced = 0
count_unbalanced_list = []


for i, cost in enumerate(cost_list_loaded):
    template = latex_jinja_env.get_template('/utils/assignment_problem.tex')

    from scipy.optimize import linear_sum_assignment

    n, m = np.shape(cost)
    c = cost.tolist()
    cost_last = cost[n-1, :]
    cost = np.vstack([cost, cost_last])

    row_ind, col_ind = linear_sum_assignment(cost)
    result = cost[row_ind, col_ind].sum()

    tex = template.render(
           show_question=True,
           show_answer=True,
           show_blank=True,
           show_blank_answer=True,
           blank_desc=u"完成所有任务至少需要的时间是",
           cost=c,
           n=n,
           m=m,
           person_str=u"员工",
           task_str=u"任务",
           cost_str=u"所需时间",
           problem_description_pre = u"""
              一项工作由连续的%(m)d项任务组成，现有的%(n)d个员工独立完成这%(m)d项任务所需的时间如下表
              所示，现要求完成所有的任务，且员工4指派其中2项任务，其它员工只能指派其中1项.
              """ % {"m":m, "n": n},
           result=result,
    )

    r.clipboard_append(tex)


#print(success)
print("count_unbalanced:", count_unbalanced)

# with open(SAVED_QUESTION, 'wb') as f:
#     pickle.dump(cost_list, f)

