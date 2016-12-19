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
lp_json_list.append(lp.json)

print(lp_json_list)

import pickle
with open('lp.bin', 'wb') as f:
    pickle.dump(lp_json_list, f)


with open('lp.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)


template = latex_jinja_env.get_template('/utils/lp_fillform.tex')

for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp.solve(method="simplex")
    if lp.qtype == "max":
        qtype_str = u"大"
    else:
        qtype_str = u"小"

    tex = template.render(
        answer_table_iters=iter(range(1, 5)),
        show_question = True,
        show_answer = True,
        #show_lp = True,
        #standardized_lp = lp.standardized_LP(),
        pre_description=u"""已知某最%s值线性规划问题在引入松弛变量$%s$标准化后，用单纯形法计算时得到的初始单纯形表及最终单纯形表如下表所示，请将最终表中$\\mathbf{\\bar p}_j$、$\\bar c_j$、$\\mathbf{\\bar b}$、$Z$的数字补齐。
        """ % (qtype_str, ",".join(lp.solutionCommon.slack_str_list_intro)),
        lp=lp,
        after_description=u"该问题的对偶问题的最优解是______________________________________________________________________________.",
        answer_after_description = u"该问题的对偶问题的最优解是<strong>$(%s)$</strong>或<strong>$(%s)$</strong>." % (",".join(lp.dual_opt_solution_str_list[0]), ",".join(lp.dual_opt_solution_str_list[1]))
    )

    r.clipboard_append(tex)

r.mainloop()