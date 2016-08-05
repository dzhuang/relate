# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy
import numpy as np


# lp = LP(qtype="max",
#         goal=[5, 4, 2],
#         constraints=[
#             [8, 4, 5, "<", 320],
#             [2, 2, 1, "<", 100],
#             #            [3, 2, 1, 2, ">", 15]
#         ],
#         sensitive={
#             "p": [([0], [20, 30], [2, 3]), ([2], [1, 0], [2, 3])],
#
#             # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
#             # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
#             "c": [([2], None, 4), ([0], None, 10), (None, [6, 3, 4], [6, 3, 5])],
#             "b": [([0], 360, None, 500), (None, [300, 100], [400, 700])],
#             "A": [([12, 10, 6, "<", 720], [12, 10, 6, "<", 480])],
#             "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
#         }
#         )

lp = LP(qtype="max",
        goal=[3, 2, 4],
        constraints=[
            [6, 3, 5, "<", 45],
            [3, 4, 5, "<", 30],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            "p": [([1], [3, 2]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([0], None, 2), ],
            "b": [([1], None, 60), ],
            "A": [([2, 1, 3, "<", 15],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )

lp = LP(qtype="max",
        goal=[6, -2, 4],
        constraints=[
            [2, -1, 2, "<", 2],
            [1, 1, 4, "<", 4],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            "p": [([2], [1, 1]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [([1], 8), ([0], None)],
            "A": [([1, 1, 1, "<", 3],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )

lp = LP(qtype="max",
        goal=[6, 2, 5],
        constraints=[
            [2, -1, 1, "<", 2],
            [1, 1, 2, "<", 4],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            "p": [([2], [1, 1]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [([1], 8), ([0], None)],
            "A": [([1, 1, 1, "<", 3],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )

lp = LP(qtype="max",
        goal=[-5, 5, 13],
        constraints=[
            [-1, 1, 3, "<", 20],
            [6, 2, 5, "<", 45],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            "p": [([0], [0, 3]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [([0], None), (None, [30, 35])],
            "A": [([2, 3, 5, "<", 50],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )

lp = LP(qtype="max",
        goal=[2, -1, 3, 1],
        constraints=[
            [1, 2, 1, 0, "<", 12],
            [2, -1, 0, 1, "<", 10],
            [0, 0, 1, 1, "<", 8]
        ],
        sensitive={
            "p": [([1], [2, 1, 0]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([0], None), ],
            "b": [([0], None), (None, [4, 10, 10])],
            "A": [([1, 0, 1, -2, "<", 11],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )

lp = LP(qtype="max",
        goal=[5, 2, 3],
        constraints=[
            [1, 2, 3, "<", 90],
            [2, 1, 1, "<", 50],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            #"p": [([0], [0, 3]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([2], None), ],
            "b": [
                    ([1], None),
                    (None, [180, 50])
                  ],
            "A": [([3, 4, 2, "<", 60],), ],
            "x": [[
                    {"c": 4, "p": [4, 2]},
                    #{"c": 4, "p": [3, 2]}
                    ]
                  ]
        }
        )

lp = LP(qtype="max",
        goal=[2, 5, 1],
        constraints=[
            [1, 0, 1, "<", 4],
            [0, 2, 0, "<", 12],
            [3, 2, 1, "<", 18],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            #"p": [([0], [2, 2, 3]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [
                ([0], None),
                (None, [4, 10, 16])
            ],
            "A": [([1, 1, 1, "<", 8],), ],
            "x": [[
                {"c": 4, "p": [1, 0, 1]},
                # {"c": 4, "p": [3, 2]}
            ]
            ]
        }
        )

lp = LP(qtype="max",
        goal=[1, 2, 6],
        constraints=[
            [1, 1, 1, "<", 6],
            [2, -1, 1, "<", 4],
            [0, 1, 2, "<", 4],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                    ([0], None),
                ],
            "b": [
                ([1], None),
                ([0], 5./2),
                # (None, [4, 10, 16])
            ],
            "A": [([1, 0, 1, "<", 2],), ],
            "p": [([1], [2, -1, 2]), ],

            # "x": [[
            #     {"c": 4, "p": [1, 0, 1]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]
            # ]
        }
        )

lp = LP(qtype="max",
        goal=[1, 2, 6],
        constraints=[
            [1, 1, 1, "<", 6],
            [2, -1, 1, "<", 4],
            [0, 1, 2, "<", 4],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                ([2], None),
            ],
            "b": [
                ([2], None),
                ([1], 11),
                # (None, [4, 10, 16])
            ],
            "A": [([1, 0, 1, "<", 1],), ],
            "p": [([1], [1, -1, 2]), ],

            # "x": [[
            #     {"c": 4, "p": [1, 0, 1]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]
            # ]
        }
        )

lp = LP(qtype="max",
        goal=[5, 6, 8],
        constraints=[
            [6, 3, 2, "<", 27],
            [2, 1, 3, "<", 30],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            # "p": [([0], [0, 3]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [
                ([0],
                 #48,
                 None,
                 ),
                ([1],
                 8,
                 #None,
                 )
            ],
            "A": [([1, 1, 1, "<", 10],), ],
            # "x": [[
            #     {"c": 4, "p": [4, 2]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]]
            "p": [([0], [3, 2]), ],
        }
        )

lp = LP(qtype="max",
        goal=[5, 6, 8],
        constraints=[
            [6, 3, 2, "<", 27],
            [2, 1, 3, "<", 30],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([2], None), ],
            "b": [
                ([0],
                 48,
                 #None,
                 ),
                ([1],
                 #8,
                 None,
                 )
            ],
            "A": [([2, 2, 1, "<", 10],), ],
            # "x": [[
            #     {"c": 4, "p": [4, 2]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]]
            "p": [([0], [1, 1]), ],
        }
        )

lp = LP(qtype="max",
        goal=[12, 8, 5],
        constraints=[
            [3, 2, 1, "<", 20],
            [1, 1, 1, "<", 11],
            [12, 4, 1, "<", 48]
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                    ([0], None),
                ],
            "b": [
                ([0],
                 #18,
                 None,
                 ),
                ([2],
                 8,
                 #None,
                 )
            ],
            "A": [([2, 2, 1, "<", 16],), ],
            "x": [[
                {"c": 4, "p": [4, 2, 1]},
                # {"c": 4, "p": [3, 2]}
                ]]
            # "p": [([0], [3, 11, 8]), ],
        }
        )

lp = LP(qtype="max",
        goal=[12, 8, 5],
        constraints=[
            [3, 2, 1, "<", 20],
            [1, 1, 1, "<", 11],
            [12, 4, 1, "<", 48]
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                ([1], None),
            ],
            "b": [
                ([0],
                 24,
                 #None,
                 ),
                ([2],
                 #8,
                 None,
                 )
            ],
            "A": [([1, 2, 2, "<", 18],), ],
            "x": [[
                {"c": 4, "p": [1, 3, 1]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [3, 11, 8]), ],
        }
        )

# template = latex_jinja_env.get_template('/utils/lp_model.tex')
# tex = template.render(
#     description = u"""
#     """,
#     lp = lp
# )



#_file_write("lp_test.tex", tex.encode('UTF-8'))

from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()


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

    lp = LP(**lp_dict)
    #lp = lp
    lp2phase = deepcopy(lp)

    lp.solve(method="simplex")
    lp.sensitive_analysis()

    template = latex_jinja_env.get_template('/utils/lp_sensitivity.tex')
    tex = template.render(
        question_iters = iter(range(0,5)),
        iters=iter(range(0, 20)),
        show_question = True,
        show_answer = True,
#        standardized_lp = lp.standardized_LP(),
        #pre_description=u"""有线性规划问题
        #""",
        #after_description=u"""
        #""",
        lp=lp,
#        show_only_opt_table = True,
    )

    r.clipboard_append(tex)

