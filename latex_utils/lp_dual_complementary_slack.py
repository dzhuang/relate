# -*- coding: utf-8 -*-

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
with open('lp.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)

with open('lp_simplex_3_iter_max_min.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)

template = latex_jinja_env.get_template('/utils/lp_dual_complementary_slack.tex')

for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp.solve(method="simplex")

    use_prime_result=False

    after_description=(
        u"的最优解是$%s = (%s)^T$，" % (r"(%s)^T" % ",\,".join(lp.opt_x), ",\,". join(lp.opt_value),)
        +
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")

    blank_description = (
        "$(%s)=$"
        % ",\,".join(["y_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))])
    )

    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])

    if not use_prime_result:
        after_description = (
            u"的对偶问题最优解是$(%s) = (%s)$，" % (
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))]),
                ",\,".join(lp.dual_opt_solution_str_list[0]))
            +
            u"则该问题的<strong>最优解</strong>是：")
        blank_description = (
            "$%s=$"
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)
        )

        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)

    tex = template.render(
        answer_table_iters=iter(range(1, 5)),
        show_question = True,
        show_answer = True,
        show_blank = True,
        show_blank_answer = True,
        use_prime_result=use_prime_result,
        blank_description=blank_description,
        #show_lp = True,
        #standardized_lp = lp.standardized_LP(),
        pre_description=u"已知线性规划问题",
        lp=lp,
        after_description=after_description,
        #answer0 = u"<strong>$(%s)$</strong>或<strong>$(%s)$</strong>." % (",\,".join(lp.dual_opt_solution_str_list[0]), ",\,".join(lp.dual_opt_solution_str_list[1])),
        answer1= answer1,
        forced_left_wrapper='["("]',
        forced_right_wrapper='[")", ")^T"]',
    )
    # tex = template.render(
    #     show_question=True,
    #     show_answer=False,
    #     show_blank_answer=True,
    #     lp=lp,
    #     answer0=u"<strong>$(%s)$</strong>或<strong>$(%s)$</strong>." % (
    #     ",".join(lp.dual_opt_solution_str_list[0]), ",".join(lp.dual_opt_solution_str_list[1])),
    #     answer1="(%s)" % ", ".join(lp.dual_opt_solution_list[0]),
    #     answer2="(%s)" % ", ".join(lp.dual_opt_solution_list[1]),
    #     forced_left_wrapper='["("]',
    #     forced_right_wrapper='[")", ")^T"]',
    # )

    r.clipboard_append(tex)

