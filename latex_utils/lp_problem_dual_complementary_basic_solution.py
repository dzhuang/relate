# -*- coding: utf-8 -*-

# 只允许最大值问题，且必须满足对称对偶形式

SAVED_QUESTION_2_iter = "lp_dual_complementary_basic_solution_2_iter.bin"
SAVED_QUESTION_3_iter = "lp_dual_complementary_basic_solution_3_iter.bin"

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy

lp = LP(qtype="max",
        goal=[4, -2, 2],
        constraints=[
            [3, 1, 1, "<", 60],
            [1, -1, 2, "<", 10],
            [2, 2, -2, "<", 40],
        ],
        )

lp = LP(qtype="max",
        goal=[3, 1, 3],
        constraints=[
            [2, 1, 1, "<", 2],
            [1, 2, 3, "<", 5],
            [2, 2, 1, "<", 6],
        ],
        )

from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()


lp_json_list = []
lp_json_list.append(lp.json)

#print lp_json_list

import pickle
with open('lp.bin', 'wb') as f:
    pickle.dump(lp_json_list, f)

#lp_simplex_2_iter_max_min.bin
with open('lp_simplex_2_iter_max_min.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)

with open('lp_simplex_3_iter_max_min.bin', 'rb') as f:
    lp_json_list_loaded += pickle.load(f)

template = latex_jinja_env.get_template('/utils/lp_dual_solution.tex')

final_lp_list1 = []
final_lp_list2 = []
count1 = 0
count2 = 0

for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp.solve(method="simplex")
    if lp.qtype == "max":
        qtype_str = u"大"
    else:
        qtype_str = u"小"

    # tex = template.render(
    #     answer_table_iters=iter(range(1, 5)),
    #     show_question = True,
    #     show_answer = True,
    #     show_blank = True,
    #     show_blank_answer = True,
    #     #show_lp = True,
    #     #standardized_lp = lp.standardized_LP(),
    #     pre_description=u"""已知某最%s值线性规划问题在引入松弛变量$%s$标准化后，用单纯形法计算时得到的初始单纯形表及最终单纯形表如下表所示。
    #     """ % (qtype_str, ",".join(lp.solutionCommon.slack_str_list_intro)),
    #     lp=lp,
    #     after_description=u"该问题的对偶问题的最优解是______________________________________________________________________________.",
    #     answer0 = u"<strong>$(%s)$</strong>或<strong>$(%s)$</strong>." % (",".join(lp.dual_opt_solution_str_list[0]), ",".join(lp.dual_opt_solution_str_list[1])),
    #     answer1= "(%s)" % ",".join(lp.dual_opt_solution_list[0]),
    #     answer2 = "(%s)" % ",".join(lp.dual_opt_solution_list[1]),
    #     answer_after_description = u"该问题的对偶问题的最优解是<strong>$(%s)$</strong>或<strong>$(%s)$</strong>." % (",".join(lp.dual_opt_solution_str_list[0]), ",".join(lp.dual_opt_solution_str_list[1])),
    #     forced_left_wrapper='["("]',
    #     forced_right_wrapper='[")", ")^T"]',
    # )
    tex = template.render(
        show_question=True,
        show_answer=False,
        show_blank_answer=True,
        lp=lp,
        answer0=u"<strong>$(%s)$</strong>或<strong>$(%s)$</strong>." % (
        ",".join(lp.dual_opt_solution_str_list[0]), ",".join(lp.dual_opt_solution_str_list[1])),
        answer1="(%s)" % ", ".join(lp.dual_opt_solution_list[0]),
        answer2="(%s)" % ", ".join(lp.dual_opt_solution_list[1]),
        forced_left_wrapper='["("]',
        forced_right_wrapper='[")", ")^T"]',
    )

    if lp.solutionCommon.nit in [2] and lp.res.status == 0 and lp.qtype=="max":
        r.clipboard_append(tex)
        final_lp_list1.append(lp.json)
        count1 += 1
    if lp.solutionCommon.nit in [3,4] and lp.res.status == 0 and lp.qtype=="max":
        final_lp_list2.append(lp.json)
        count2 += 1
        r.clipboard_append(tex)

print count1, count2

with open(SAVED_QUESTION_2_iter, 'wb') as f:
        pickle.dump(final_lp_list1, f)
with open(SAVED_QUESTION_3_iter, 'wb') as f:
    pickle.dump(final_lp_list2, f)
