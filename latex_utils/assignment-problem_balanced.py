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


SAVED_QUESTION = "assignment_balanced.bin"
STEP_RANGE = [12, 16]
MAX_RETRY_ITERATION = 1000
N = 5
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
        suggestion = "cost=%s" % repr(cost)
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

cost=np.array([[ 8, 11, 10,  5, 15],
       [13,  6,  3,  8, 16],
       [11, 16,  3, 11,  2],
       [ 8, 14,  7,  2,  4],
       [16, 15, 19, 11,  9]])
cost_list.append(cost)

cost=np.array([[ 7, 15,  3, 14, 16],
       [18,  8, 13,  9,  7],
       [ 6,  5, 17, 13,  4],
       [18, 13,  7, 16, 18],
       [10,  2,  8,  6, 19]])
cost_list.append(cost)

cost=np.array([[16,  8,  9,  2,  8],
       [17, 16,  3, 11,  3],
       [16,  5, 10, 13,  8],
       [ 7, 11, 17,  6, 13],
       [12,  3,  8, 18,  7]])
cost_list.append(cost)

cost=np.array([[10, 16,  9,  7,  5],
       [ 6, 17, 14,  2, 18],
       [ 5,  7, 13, 17, 10],
       [13, 19, 13, 13,  2],
       [ 2, 13,  9, 10,  9]])
cost_list.append(cost)

cost=np.array([[ 9, 14,  5, 19, 19],
       [ 7,  8,  4,  5, 19],
       [ 6, 15, 15, 19, 18],
       [ 7, 19, 12, 10, 15],
       [ 5,  8,  2,  2, 10]])
cost_list.append(cost)

cost=np.array([[ 3, 15,  5, 10,  2],
       [16,  4, 17, 12, 13],
       [ 7,  3, 15, 11, 19],
       [18, 12, 18,  2, 12],
       [17,  5, 18, 18, 17]])
cost_list.append(cost)

cost=np.array([[13,  9, 12, 12, 10],
       [ 5,  5,  9, 19,  8],
       [ 9, 10, 13, 15, 18],
       [ 4, 11,  7,  2, 14],
       [12,  8, 12,  4,  8]])
cost_list.append(cost)

cost=np.array([[10, 16, 11, 15,  5],
       [ 2, 13,  2,  2,  3],
       [ 8,  8, 18,  7, 12],
       [15,  9,  7,  4, 14],
       [15,  6, 19,  5,  4]])
cost_list.append(cost)

cost=np.array([[ 5, 16,  2, 12,  8],
       [12,  5,  2, 17,  4],
       [16, 14, 11,  5,  4],
       [12,  3, 15,  6, 12],
       [14,  5, 14, 10,  8]])
cost_list.append(cost)

cost=np.array([[12, 12, 18,  4,  3],
       [ 8, 17,  8, 10, 10],
       [ 5,  3,  8,  9,  5],
       [10, 13, 12, 15,  8],
       [14, 17, 19,  4,  3]])
cost_list.append(cost)

cost=np.array([[19, 15, 13,  6,  4],
       [ 4, 13, 11,  4, 11],
       [10, 17, 16, 17,  2],
       [ 2, 17,  2,  3, 10],
       [11,  9, 10, 14,  2]])
cost_list.append(cost)

cost=np.array([[ 6, 11, 19, 10, 14],
       [11, 11,  3, 18, 16],
       [ 2,  2, 11,  5, 11],
       [ 9, 16,  4,  6, 14],
       [ 8,  3,  6,  9,  7]])
cost_list.append(cost)

cost=np.array([[15,  3, 11, 12, 13],
       [18, 10,  4, 16,  9],
       [11, 10, 13, 11, 16],
       [ 7,  9,  8, 19, 15],
       [17,  5, 13, 19,  9]])
cost_list.append(cost)

cost=np.array([[ 3, 14,  9, 11, 11],
       [ 9,  2, 18,  4, 16],
       [19,  7,  3, 11,  2],
       [15, 13, 11, 18,  4],
       [12,  8,  9, 18,  8]])
cost_list.append(cost)

cost=np.array([[ 7, 11, 11,  8, 16],
       [19, 17, 13, 11, 18],
       [12,  8, 18,  2, 16],
       [ 7, 12,  6, 12, 14],
       [ 2,  4,  6, 16,  9]])
cost_list.append(cost)

cost=np.array([[ 4, 16,  7,  2, 14],
       [15,  2, 18, 17, 12],
       [ 6, 10, 16,  7,  3],
       [16, 14, 11, 10, 18],
       [16,  8, 18,  2,  3]])
cost_list.append(cost)

cost=np.array([[ 7,  4, 16, 13, 10],
       [ 5,  7,  6, 19, 12],
       [ 2,  7,  8, 15, 19],
       [18,  5, 11, 15, 13],
       [ 4, 10,  5,  3,  9]])
cost_list.append(cost)

cost=np.array([[ 8, 17,  2, 12, 19],
       [17,  8, 17,  5, 15],
       [ 7, 10,  4,  8,  4],
       [19,  8,  5,  8, 15],
       [16,  7,  6, 13,  8]])
cost_list.append(cost)

cost=np.array([[10, 14, 15, 17, 18],
       [15, 19,  6, 17, 10],
       [ 3,  5, 14, 19, 19],
       [12, 14,  9, 13,  9],
       [ 7, 11,  5, 18,  9]])
cost_list.append(cost)

cost=np.array([[ 6, 18, 16,  2,  9],
       [ 9,  5, 17, 13,  8],
       [ 9,  4, 15,  9, 19],
       [18,  7, 19,  4,  7],
       [12,  9, 19, 12,  4]])
cost_list.append(cost)

cost=np.array([[18, 13,  4, 16,  7],
       [ 3, 19, 10,  3,  2],
       [11,  9,  3,  8, 12],
       [10, 18,  6, 17,  4],
       [14, 12, 15, 13, 12]])
cost_list.append(cost)

cost=np.array([[11, 16, 13,  7,  2],
       [12,  6, 12,  4, 19],
       [ 6, 19, 14,  5, 10],
       [ 2, 18, 14,  3,  2],
       [11, 15, 13,  9, 10]])
cost_list.append(cost)

cost=np.array([[14, 18,  2, 12,  6],
       [ 3, 19, 12, 16,  5],
       [15, 16, 12,  6,  5],
       [ 2,  7, 16,  8, 15],
       [ 4,  7, 12,  9, 12]])
cost_list.append(cost)

cost=np.array([[ 8, 11,  7,  6, 12],
       [14,  7,  4,  6, 13],
       [ 6,  2,  3, 10,  3],
       [14,  4,  2, 18,  8],
       [16,  7,  2, 12, 19]])
cost_list.append(cost)

cost=np.array([[15, 13, 13, 19,  5],
       [11, 12,  5, 19, 14],
       [ 5,  9,  2, 14,  3],
       [11,  2,  7, 11,  3],
       [10, 19,  5,  7, 19]])
cost_list.append(cost)

cost=np.array([[ 6, 16,  2, 13,  2],
       [ 6,  8,  5, 17,  3],
       [ 3,  4,  7,  3,  7],
       [18, 16,  4, 13, 18],
       [12,  4,  3, 18, 13]])
cost_list.append(cost)

cost=np.array([[13, 15,  5, 17,  4],
       [13,  6,  2, 19,  9],
       [ 4, 18,  7,  4,  3],
       [14, 18, 11, 19,  7],
       [12,  3, 18, 13,  8]])
cost_list.append(cost)

cost=np.array([[18, 11,  3, 19, 17],
       [11,  9,  2, 17, 19],
       [ 7, 15, 15,  9,  7],
       [11, 18, 10, 12,  5],
       [14, 12,  7, 18,  2]])
cost_list.append(cost)

cost=np.array([[ 5,  8, 11,  6, 19],
       [ 4, 15, 18,  8, 12],
       [13, 11,  3, 19,  8],
       [ 3, 16, 11, 17,  9],
       [ 7,  4,  6, 16,  4]])
cost_list.append(cost)

cost=np.array([[16, 11,  3,  8,  6],
       [10, 11,  9,  3,  5],
       [ 8,  9, 19,  7,  8],
       [11,  9,  3, 16, 13],
       [ 5, 16,  6, 19,  7]])
cost_list.append(cost)

cost=np.array([[10,  2,  7, 16, 18],
       [ 7,  2, 16, 15,  8],
       [ 4, 15, 12, 14, 13],
       [19, 15,  5,  3, 15],
       [ 6, 17,  5,  2,  8]])
cost_list.append(cost)

cost=np.array([[ 2,  6, 10, 12,  2],
       [14, 19, 17,  4, 13],
       [10, 13, 13,  7,  2],
       [15, 18, 16,  3,  7],
       [ 8, 11, 17,  2,  8]])
cost_list.append(cost)

cost=np.array([[12,  7,  4, 10, 16],
       [16, 14,  9,  9,  3],
       [ 8, 17, 18, 14,  7],
       [11, 16, 11, 10, 18],
       [13,  6, 12,  3,  3]])
cost_list.append(cost)

cost=np.array([[19, 18, 14,  8, 19],
       [ 9,  6, 17, 10,  6],
       [18, 14,  4,  3, 16],
       [19,  4,  5, 18, 14],
       [ 8, 12,  7, 15,  6]])
cost_list.append(cost)

cost=np.array([[18, 15,  7,  3, 12],
       [17, 13, 13, 19, 11],
       [ 4, 13, 15, 14, 19],
       [ 6, 18, 14, 16,  5],
       [ 8,  8, 16, 17,  4]])
cost_list.append(cost)

cost=np.array([[15, 18, 16, 17, 15],
       [15, 18, 10, 16, 17],
       [ 3, 10, 16, 15, 16],
       [ 8,  5, 18,  5,  4],
       [15, 13,  9, 12,  6]])
cost_list.append(cost)

cost=np.array([[17,  7,  3, 18, 18],
       [17, 13,  7, 19, 19],
       [15, 14,  4,  7, 18],
       [ 8, 15,  9,  6,  7],
       [ 2, 17,  2, 19, 16]])
cost_list.append(cost)

cost=np.array([[ 2, 10, 17,  8,  8],
       [19,  2, 16, 18,  3],
       [11, 19, 15, 14,  9],
       [ 3, 14,  7, 19, 19],
       [18, 12, 13, 16,  5]])
cost_list.append(cost)

cost=np.array([[17, 16,  7, 11, 19],
       [15, 15, 13, 11,  3],
       [13, 16, 10, 16, 12],
       [11, 10, 17, 17,  2],
       [ 7,  9, 11,  2, 15]])
cost_list.append(cost)

cost=np.array([[10,  5,  9,  8, 12],
       [18, 13,  7, 13, 12],
       [12,  3, 12, 18, 14],
       [12, 10, 17, 16, 19],
       [17, 11, 15, 16,  9]])
cost_list.append(cost)

cost=np.array([[ 3, 13,  6,  2,  6],
       [ 3, 19, 16,  3, 17],
       [ 6, 18,  6,  5, 16],
       [ 5,  2, 13, 17, 13],
       [ 2, 10, 17,  2,  6]])
cost_list.append(cost)

cost=np.array([[17, 14, 10,  9, 15],
       [18, 10,  9,  6, 10],
       [ 4, 19, 17,  9,  6],
       [17, 10,  6, 13,  3],
       [ 7,  9, 12, 16, 15]])
cost_list.append(cost)

cost=np.array([[ 4, 19,  8, 12,  6],
       [16, 11, 14, 14, 11],
       [18,  2, 16,  9,  6],
       [ 2,  5,  7,  4,  9],
       [13, 17, 18,  8, 12]])
cost_list.append(cost)

cost=np.array([[ 9,  4,  8, 18,  6],
       [11,  2, 17,  3,  9],
       [ 6,  8, 11, 17,  3],
       [ 9,  7, 19,  9,  2],
       [11,  7,  2, 10,  8]])
cost_list.append(cost)

cost=np.array([[13,  9,  3, 11, 19],
       [ 3,  5, 13, 18,  3],
       [19, 17,  7,  9,  5],
       [ 5, 19, 14, 15,  4],
       [12, 17, 16, 12,  9]])
cost_list.append(cost)

cost=np.array([[ 6,  6, 16,  2, 17],
       [ 4, 11, 16, 18, 16],
       [12, 17, 17,  3, 10],
       [11,  9, 17, 16, 13],
       [15, 13, 10,  3,  6]])
cost_list.append(cost)

cost=np.array([[17, 17,  5, 15, 16],
       [17,  9,  9,  2, 14],
       [ 2, 14, 13, 16,  2],
       [ 5, 15, 15,  7,  9],
       [ 2, 12,  4, 10, 16]])
cost_list.append(cost)

cost=np.array([[ 2,  2,  6,  3,  2],
       [13, 12,  4, 19, 14],
       [ 2, 19, 13,  7, 14],
       [12, 14, 10, 12, 19],
       [ 7,  7, 11, 10, 14]])
cost_list.append(cost)

cost=np.array([[11, 15,  5, 18, 14],
       [ 5, 14, 19,  5, 19],
       [ 4, 17,  9, 17,  7],
       [ 5, 14, 13, 17, 17],
       [ 9,  3, 11,  3,  2]])
cost_list.append(cost)

cost=np.array([[10, 19,  3, 19,  2],
       [ 8, 11,  9, 15, 11],
       [ 3,  2, 16,  3,  9],
       [ 4, 17, 17, 10,  7],
       [ 4,  8,  5, 19,  5]])
cost_list.append(cost)

cost=np.array([[ 6, 11, 18, 16, 13],
       [18, 14,  3,  8,  7],
       [ 2,  4,  3, 15,  4],
       [17, 13,  5, 12,  8],
       [ 5,  8, 11, 10,  2]])
cost_list.append(cost)

cost=np.array([[ 5,  9, 14, 11, 19],
       [16, 13,  3, 18,  5],
       [11,  3, 13, 14, 17],
       [15, 14,  2,  6, 18],
       [ 4,  6,  6,  8,  8]])
cost_list.append(cost)

cost=np.array([[18,  5, 19,  3,  9],
       [ 6,  6, 19, 18, 11],
       [14,  5,  9,  3,  6],
       [15, 14,  6,  3, 13],
       [ 3,  7,  3, 12, 16]])
cost_list.append(cost)

cost=np.array([[ 2, 16, 15,  2, 18],
       [ 6,  7,  6,  4,  8],
       [ 4,  9, 12, 14, 12],
       [ 5,  4, 10, 10, 10],
       [ 8,  3, 14, 11,  4]])
cost_list.append(cost)

cost=np.array([[16, 16, 17, 16, 10],
       [ 4, 13, 12,  8,  4],
       [18, 18, 16, 18,  5],
       [ 8, 12, 19, 12,  9],
       [17, 17,  4, 11,  7]])
cost_list.append(cost)

cost=np.array([[12,  4,  2, 17, 16],
       [16,  5, 10,  4, 13],
       [ 6, 12, 11,  5, 11],
       [11, 14, 17, 14,  6],
       [19, 17,  2, 11, 15]])
cost_list.append(cost)

cost=np.array([[17,  3, 13,  8,  6],
       [ 5,  7, 11, 10, 12],
       [ 2,  9,  2,  2, 16],
       [ 6,  4,  2, 19, 14],
       [ 2, 10,  5, 13, 17]])
cost_list.append(cost)

cost=np.array([[ 8,  7, 16, 17,  7],
       [ 3,  2,  9,  6,  3],
       [19, 13, 16,  9,  7],
       [19, 18,  6, 19,  2],
       [11,  5, 18,  2, 13]])
cost_list.append(cost)

cost=np.array([[15,  9, 17,  2,  4],
       [14,  7, 10, 15,  6],
       [12, 17, 18,  5, 12],
       [15, 12, 13, 18,  7],
       [ 5, 17, 17,  9, 15]])
cost_list.append(cost)

cost=np.array([[16, 18,  3,  3, 18],
       [15, 14,  5, 13,  8],
       [ 4,  2, 16, 15,  7],
       [18,  9, 18, 18,  5],
       [16, 17, 17, 11,  8]])
cost_list.append(cost)

cost=np.array([[10, 14, 18, 13,  5],
       [ 5, 14,  3, 17, 10],
       [ 6, 11, 17, 10, 11],
       [ 4, 16,  2,  3,  3],
       [ 6,  4, 14, 14,  2]])
cost_list.append(cost)

cost=np.array([[12, 12,  7, 11,  8],
       [12, 18,  9,  5, 18],
       [ 2, 13,  4,  3, 10],
       [15,  7, 15,  4,  8],
       [ 2,  6, 14, 15, 19]])
cost_list.append(cost)

cost=np.array([[ 6,  5, 12,  2, 17],
       [10, 10,  9, 10,  7],
       [ 9,  9, 19,  7, 12],
       [ 5,  2, 13,  6,  9],
       [13,  3,  6, 15, 12]])
cost_list.append(cost)

cost=np.array([[ 7, 19, 18,  8, 16],
       [ 8, 15,  2,  4, 12],
       [ 5, 17,  9, 16, 17],
       [10, 17, 18,  7, 19],
       [13, 15,  7, 18, 10]])
cost_list.append(cost)

cost=np.array([[11,  7,  6, 14,  8],
       [ 5, 10,  2,  7,  9],
       [18,  4, 16,  2,  4],
       [ 7,  3,  2,  6, 16],
       [ 3, 10, 13, 16, 12]])
cost_list.append(cost)

cost=np.array([[13, 11,  8, 10, 17],
       [ 2,  7,  6, 10, 14],
       [ 3,  4, 17, 10,  9],
       [ 4,  6,  9,  2,  2],
       [19, 19, 10, 17, 19]])
cost_list.append(cost)

cost=np.array([[15,  4, 12, 14,  5],
       [13,  2, 12,  5, 18],
       [18, 18,  7,  5,  9],
       [17,  5, 11, 13, 16],
       [ 6, 15,  9,  9, 15]])
cost_list.append(cost)

cost=np.array([[ 8,  8, 11,  3,  7],
       [17, 14, 14, 11, 18],
       [ 2, 13,  3, 14,  5],
       [12, 12, 14, 19, 12],
       [18, 10, 17, 17, 14]])
cost_list.append(cost)

cost=np.array([[ 8, 16, 12,  2, 16],
       [16, 13, 13,  3,  8],
       [11, 14,  9, 19,  7],
       [15,  5,  8,  7,  5],
       [10, 16, 15, 13,  3]])
cost_list.append(cost)

cost=np.array([[ 4, 11, 18, 16, 18],
       [13, 11, 14,  8, 11],
       [ 2, 17, 16, 14,  9],
       [ 9, 13, 17,  2, 11],
       [ 3,  8,  2, 12,  2]])
cost_list.append(cost)

cost=np.array([[18,  7, 18, 16, 13],
       [ 4,  2, 17,  5, 11],
       [18,  4, 10, 17,  3],
       [ 5,  6,  4, 16,  8],
       [ 8,  5, 12, 12, 13]])
cost_list.append(cost)

cost=np.array([[ 5, 14,  7, 14, 11],
       [ 8,  8,  2,  2, 13],
       [ 8, 15, 17, 18,  8],
       [ 3,  3,  2, 15, 16],
       [ 2,  4,  7, 15,  9]])
cost_list.append(cost)

cost=np.array([[ 2,  3,  7,  2, 13],
       [15,  4,  8,  4, 10],
       [ 8, 13,  9,  7,  6],
       [11,  2, 17, 16,  6],
       [ 6,  9, 18, 14, 11]])
cost_list.append(cost)

cost=np.array([[ 4,  2, 19, 12, 18],
       [ 3,  9,  3, 14, 16],
       [ 6,  2, 10, 13, 14],
       [ 6, 15,  8, 14,  7],
       [ 4,  5,  6,  2,  8]])
cost_list.append(cost)

cost=np.array([[18, 17,  7, 15, 13],
       [15, 14, 18,  3, 16],
       [ 5, 14,  9, 13, 19],
       [16,  9,  7,  5,  8],
       [11, 13,  3,  2, 14]])
cost_list.append(cost)

cost=np.array([[ 5, 12, 17, 12,  6],
       [12,  8,  3,  3, 13],
       [ 4, 10,  9, 11,  8],
       [15, 18, 18, 19,  7],
       [ 2, 15,  5, 14, 16]])
cost_list.append(cost)

cost=np.array([[ 2, 19, 10,  8,  3],
       [12, 16, 19, 17, 12],
       [17, 10, 18,  7, 11],
       [ 2, 17, 14,  4,  9],
       [ 3, 19, 12,  7, 10]])
cost_list.append(cost)

cost=np.array([[ 5, 13,  5, 17, 10],
       [ 7, 19, 12,  6, 17],
       [ 2, 11,  9,  4, 15],
       [12,  7, 14, 10,  2],
       [12, 16,  7,  6,  9]])
cost_list.append(cost)

cost=np.array([[14,  8,  3, 17,  2],
       [14, 12, 11, 14, 12],
       [15, 10,  3, 12, 10],
       [12,  9,  4,  8, 14],
       [11,  6,  9, 13, 12]])
cost_list.append(cost)

cost=np.array([[ 3, 16, 10, 15, 18],
       [ 8, 13,  6,  6,  3],
       [ 9, 19,  7, 19, 13],
       [11, 10,  7, 10, 18],
       [ 6, 18, 17, 13, 10]])
cost_list.append(cost)

cost=np.array([[18,  4, 17,  9,  7],
       [ 9, 17,  3, 17,  2],
       [11,  7,  3, 11, 17],
       [ 6,  4, 17, 11,  4],
       [17, 19,  4,  7, 15]])
cost_list.append(cost)

cost=np.array([[10, 11, 18, 15, 18],
       [10, 17, 13,  3, 11],
       [ 8, 17, 14,  4,  7],
       [ 6, 16,  7, 12, 10],
       [ 8,  3,  7,  4,  3]])
cost_list.append(cost)

cost=np.array([[ 7,  2, 10, 12, 19],
       [10,  3, 15, 16, 10],
       [14,  5, 16, 11, 13],
       [16,  7,  4, 15,  4],
       [18,  4, 18,  9,  3]])
cost_list.append(cost)

cost=np.array([[17, 17,  2,  8, 11],
       [18, 18, 14, 15, 12],
       [15,  4,  7, 16,  8],
       [ 7,  8, 11, 19,  2],
       [14, 17,  9, 16, 11]])
cost_list.append(cost)

cost=np.array([[ 8, 13, 18,  7,  2],
       [11, 16, 15, 18, 16],
       [ 3,  9, 17, 15, 16],
       [10, 18,  8, 12, 10],
       [ 9, 16,  2,  6,  3]])
cost_list.append(cost)

cost=np.array([[15,  8,  4, 13,  4],
       [ 9, 10,  9,  4, 18],
       [13, 10,  8, 17,  9],
       [ 3,  8,  4, 16,  3],
       [17,  7, 13,  2, 19]])
cost_list.append(cost)

cost=np.array([[18, 15, 10, 19,  3],
       [15,  2, 18,  9, 17],
       [13,  8,  9, 10,  4],
       [ 6, 11, 12,  8, 11],
       [ 5, 19, 14, 14, 11]])
cost_list.append(cost)

cost=np.array([[ 2, 11, 13, 14, 19],
       [ 2, 10, 16, 11, 17],
       [ 3, 14, 13, 11, 13],
       [11, 19,  5, 19, 18],
       [14, 10, 18,  5,  3]])
cost_list.append(cost)

cost=np.array([[ 5,  5,  5, 17, 12],
       [13,  5,  9, 19,  8],
       [14,  2, 11, 11, 18],
       [18, 12,  4, 12,  7],
       [15,  7,  4,  6, 11]])
cost_list.append(cost)

cost=np.array([[19, 10,  2, 15,  8],
       [11, 16,  9,  8,  2],
       [12, 13, 16,  5, 14],
       [13, 16,  3,  5,  7],
       [11, 17,  7,  3, 17]])
cost_list.append(cost)

cost=np.array([[ 5, 18,  7, 16, 15],
       [ 2,  7, 14, 15, 12],
       [ 4, 16, 15,  3, 11],
       [15, 19, 13, 11,  4],
       [ 5, 13, 11, 17, 12]])
cost_list.append(cost)

cost=np.array([[16,  4, 14,  9, 12],
       [ 8,  8,  4, 12, 19],
       [ 2,  6, 18, 15,  9],
       [ 4,  7,  6, 14, 17],
       [10,  6,  9, 18, 17]])
cost_list.append(cost)

cost=np.array([[ 8, 19, 17, 15, 15],
       [ 2, 17, 15, 14, 14],
       [16, 11, 17,  3, 15],
       [19,  3,  7,  6, 12],
       [11,  4,  7, 12, 13]])
cost_list.append(cost)

cost=np.array([[ 8, 12, 17,  7,  3],
       [ 3,  2,  9,  8,  7],
       [17,  3,  3,  8, 12],
       [11, 11,  5, 13,  9],
       [11, 13,  3,  7, 17]])
cost_list.append(cost)

cost=np.array([[ 4, 18,  3, 19, 10],
       [ 6,  2,  3, 15, 14],
       [16, 17,  3, 12, 18],
       [14, 13, 10, 19,  8],
       [ 6, 19,  2, 16,  7]])
cost_list.append(cost)

cost=np.array([[ 3, 12, 18, 14, 11],
       [11, 12, 12,  2, 10],
       [17, 10, 17,  7,  2],
       [ 2, 17, 19, 15,  8],
       [ 8,  9, 16,  2, 10]])
cost_list.append(cost)

cost=np.array([[10,  9, 14, 15, 12],
       [ 4,  3, 17,  4,  3],
       [ 9,  3,  7,  9, 11],
       [ 2,  5, 14,  6,  3],
       [18, 11, 17, 10,  3]])
cost_list.append(cost)

cost=np.array([[ 5, 12, 11,  6,  6],
       [ 5, 11, 18, 15, 15],
       [ 8, 14,  7,  8,  9],
       [ 8, 10,  8, 17,  4],
       [ 2, 18,  6,  4,  3]])
cost_list.append(cost)

cost=np.array([[ 9,  7, 13, 10,  7],
       [18, 18,  8, 15, 12],
       [10,  7,  3,  4, 19],
       [11,  2, 17,  8, 11],
       [16,  8, 13,  2,  6]])
cost_list.append(cost)

cost=np.array([[ 8, 17, 13,  7,  6],
       [ 2,  2, 10, 10,  7],
       [19, 13, 16,  8, 19],
       [ 4, 16, 17, 11,  8],
       [ 4, 18, 15,  3, 14]])
cost_list.append(cost)


# print(len(cost_list))

r = Tk()
r.withdraw()
r.clipboard_clear()

import pickle
#import dill as pickle
with open(SAVED_QUESTION, 'wb') as f:
    pickle.dump(cost_list, f)

with open(SAVED_QUESTION, 'rb') as f:
    cost_list_loaded = pickle.load(f)

count_balanced = 0
count_balanced_list = []

# for i, cost in enumerate(cost_list_loaded):
#     success = False

    # if is_qualified_question(cost):
    #     print("i", i)
    #     count_balanced += 1
    # else:

def generate_problem():
    n = 0
    mem_cost_list = []
    while n < 100:
        cost = np.random.randint(2,20,(5,5))
        if is_qualified_question(cost, mem_cost_list):
            n += 1
            mem_cost_list.append(cost)

for i, cost in enumerate(cost_list_loaded):
    template = latex_jinja_env.get_template('/utils/assignment_problem.tex')

    from scipy.optimize import linear_sum_assignment

    row_ind, col_ind = linear_sum_assignment(cost)
    result = cost[row_ind, col_ind].sum()

    c = cost.tolist()
    n, m = np.shape(cost)

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
              所示，如何将这%(m)d项任务指派给这%(n)d个员工(每人1项任务，每项任务由1个人完成)可使该工作
              的完成时间最短？
              """ % {"m":m, "n": n},
           result=result,
    )

    r.clipboard_append(tex)


#print(success)
print("count_balanced:", count_balanced)

# with open(SAVED_QUESTION, 'wb') as f:
#     pickle.dump(cost_list, f)

