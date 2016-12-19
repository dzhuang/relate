# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy
import numpy as np

SAVED_QUESTION_2_iter = "lp_sensitivity_2_iter.bin"
SAVED_QUESTION_3_iter = "lp_sensitivity_3_iter.bin"

lp_list = []

lp = LP(qtype="max",
        goal=[3, 4, 1],
        constraints=[
            [1, 1, 3, "<", 8],
            [1, 2, 4, "<", 15],
        ],
        sensitive={
            "p": [([2], [-1, 4], [-1, 2]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [([0], None),
                  ([1], 35),
                  # (None, [30, 35])
                  ],
            "A": [([3, 2, 1, "<", 10],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 3, 1],
        constraints=[
            [2, 1, 3, "<", 7],
            [1, 4, 3, "<", 14],
        ],
        sensitive={
            "p": [([2], [-1, 4], [-1, 2]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [([0], None),
                  ([1], 35),
                  # (None, [30, 35])
                  ],
            "A": [([3, 2, 1, "<", 10],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[4, 5, 6],
        constraints=[
            [1, 3, 2, "<", 20],
            [4, 2, 3, "<", 45],
        ],
        sensitive={
            "p": [([1], [2, 3], [1, 1]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([2], None), ],
            "b": [([0], 10),
                  ([1], None),
                  # (None, [30, 35])
                  ],
            "A": [([2, 3, 1, "<", 16],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )
lp_list.append(lp)


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
            "b": [([1], None), ([0], 10)],
            "A": [([1, 1, 1, "<", 3],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )
lp_list.append(lp)


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
            "b": [([1], None), ([0], 9)],
            "A": [([1, 1, 1, "<", 3],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, -1, 3, 1],
        constraints=[
            [1, 2, 1, 0, "<", 12],
            [2, -1, 0, 1, "<", 10],
            [0, 0, 1, 1, "<", 8]
        ],
        sensitive={
            "p": [([1], [2, 1, 0], [0, -1, -2]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([0], None), ],
            "b": [([0], None), (None, [4, 10, 10])],
            "A": [([1, 0, 1, -2, "<", 11],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[5, 2, 3],
        constraints=[
            [1, 2, 3, "<", 90],
            [2, 1, 1, "<", 50],
            # [3, 2, 1, 2, ">", 15]
        ],
        sensitive={
            # "p": [([0], [0, 3]), ],

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
                {"c": 4, "p": [1, 1]},
                # {"c": 4, "p": [3, 2]}
            ]
            ]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 5, 1],
        constraints=[
            [1, 0, 1, "<", 4],
            [0, 2, 0, "<", 12],
            [3, 2, 1, "<", 18],
        ],
        sensitive={
            # "p": [([0], [2, 2, 3]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [
                ([0], None),
                ([1], 16),
                #(None, [4, 10, 16])
            ],
            "A": [([1, 1, 1, "<", 8],), ],
            "x": [[
                {"c": 4, "p": [1, 0, 1]},
            ]
            ]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[3, 6, 2],
        constraints=[
            [0, 2, 0, "<", 12],
            [3, 2, 1, "<", 18],
            [1, 0, 1, "<", 4],
        ],
        sensitive={
            # "p": [([0], [2, 2, 3]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([0], None), ],
            "b": [
                ([2], None),
                ([0], 16),
                #(None, [4, 10, 16])
            ],
            "A": [([1, 1, 1, "<", 8],), ],
            "x": [[
                {"c": 4, "p": [0, 1, 1]},
            ]
            ]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 3, 6],
        constraints=[
            [1, 1, 0, "<", 4],
            [0, 0, 2, "<", 12],
            [1, 3, 2, "<", 18],
        ],
        sensitive={
            # "p": [([0], [2, 2, 3]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([0], None), ],
            "b": [
                ([0], None),
                ([1], 16),
                #(None, [4, 10, 16])
            ],
            "A": [([1, 1, 1, "<", 8],), ],
            "x": [[
                {"c": 4, "p": [1, 0, 1]},
            ]
            ]
        }
        )
lp_list.append(lp)

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
                ([0], 5. / 2),
                # (None, [4, 10, 16])
            ],
            "A": [([1, 0, 1, "<", 2],), ],
            "p": [([1], [2, -1, 2], [1, -1, -1]), ],

            # "x": [[
            #     {"c": 4, "p": [1, 0, 1]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]
            # ]
        }
        )
lp_list.append(lp)


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
            "p": [([1], [1, -1, 2], [1, -1, -1]), ],

            # "x": [[
            #     {"c": 4, "p": [1, 0, 1]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]
            # ]
        }
        )
lp_list.append(lp)


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
                 # 48,
                 None,
                 ),
                ([1],
                 8,
                 # None,
                 )
            ],
            "A": [([1, 1, 1, "<", 10],), ],
            # "x": [[
            #     {"c": 4, "p": [4, 2]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]]
            "p": [([0], [2, 1]), ],
        }
        )
lp_list.append(lp)


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
                 18,
                 #None,
                 ),
                ([1],
                 # 8,
                 None,
                 )
            ],
            "A": [([2, 2, 1, "<", 10],), ],
            # "x": [[
            #     {"c": 4, "p": [4, 2]},
            #     # {"c": 4, "p": [3, 2]}
            #     ]]
            "p": [([0], [2, 3], [1, 1]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[3, 6, 2],
        constraints=[
            [1, 1, 1, "<", 15],
            [1, 4, 7, "<", 45],
        ],
        sensitive={
            "c": [
                ([0], None),
            ],
            "b": [
                ([0],
                 9,
                 # None,
                 ),
                ([1],
                 # 8,
                 None,
                 )
            ],
            "A": [([1, 2, 3, "<", 24],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([2], [1, 2], [1/3., 1/2.]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[6, 3, 2],
        constraints=[
            [1, 1, 1, "<", 3],
            [4, 1, 7, "<", 9],
        ],
        sensitive={
            "c": [
                ([1], None),
            ],
            "b": [
                ([0],
                 2,
                 # None,
                 ),
                ([1],
                 # 8,
                 None,
                 )
            ],
            "A": [([2, 1, 3, "<", 4],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([2], [2, 1], [1 / 3., 1 / 2.]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 4, 3],
        constraints=[
            [2, 2, 1, "<", 15],
            [1, 3, 2, "<", 24],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 # 3,
                 None,
                 ),
                ([1],
                 33,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([1, 2, 3, "<", 21],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([1], [1, 2]), ],
        }
        )
lp_list.append(lp)



lp = LP(qtype="max",
        goal=[3, 4, 2],
        constraints=[
            [1, 2, 2, "<", 15],
            [2, 3, 1, "<", 24],
        ],
        sensitive={
            "c": [
                ([0], None),
            ],
            "b": [
                ([0],
                 # 3,
                 None,
                 ),
                ([1],
                 33,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([3, 2, 1, "<", 21],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([1], [1, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[4, 3, 2],
        constraints=[
            [3, 2, 1, "<", 24],
            [2, 1, 2, "<", 15],
        ],
        sensitive={
            "c": [
                ([1], None),
            ],
            "b": [
                ([1],
                 # 3,
                 None,
                 ),
                ([0],
                 33,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 3, 1, "<", 21],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([0], [2, 1]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[3, 5, 4],
        constraints=[
            [2, 2, 1, "<", 3],
            [5, 15, 10, "<", 24],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 # 3,
                 None,
                 ),
                ([1],
                 36,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 7],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([1], [3, 10], [1, 10]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[4, 5, 3],
        constraints=[
            [1, 2, 2, "<", 3],
            [10, 15, 5, "<", 24],
        ],
        sensitive={
            "c": [
                ([0], None),
            ],
            "b": [
                ([0],
                 # 3,
                 None,
                 ),
                ([1],
                 36,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([3, 2, 2, "<", 7],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([1], [1, 10], [3, 10]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[5, 6, 4],
        constraints=[
            [10, 15, 5, "<", 24],
            [1, 2, 2, "<", 3],
        ],
        sensitive={
            "c": [
                ([0], None),
            ],
            "b": [
                ([0],
                 # 3,
                 None,
                 ),
                ([1],
                 36,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([3, 2, 2, "<", 7],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([1], [10, 1], [10, 3]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[5, 3, 4],
        constraints=[
            [3, 1, 2, "<", 32],
            [4, 3, 4, "<", 48],
            [4, 5, 3, "<", 40]
        ],
        sensitive={
            "p": [([1], [1, 3, 4], [1, 3, 2]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([0], None, 5),
                  #                   ([0], 5),
                  ],
            "b": [([1], None),
                  ([2], 33),
                  # (None, [4, 10, 10])
                  ],
            "A": [([2, 3, 1, "<", 13],), ],
            # "x": [[{"c": 3, "p": [3, 2]}, {"c": 4, "p": [3, 2]}]]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[3, 2, 1],
        constraints=[
            [2, 1, 3, "<", 6],
            [1, 2, 2, "<", 9],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 # 3,
                 None,
                 ),
                ([1],
                 15,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 8],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([2], [2, 1], [-1, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 5, 4],
        constraints=[
            [2, 1, 1, "<", 6],
            [3, 4, 2, "<", 16],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 18,
                 # None,
                 ),
                ([1],
                 # 15,
                 None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 8],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([0], [1, 2], [-2, 1]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[3, 5, -1],
        constraints=[
            [1, 2, 4, "<", 8],
            [2, 1, -2, "<", 7],
        ],
        sensitive={
            "c": [
                ([0], None),
            ],
            "b": [
                ([0],
                 # 14,
                 None,
                 ),
                ([1],
                 22,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 8],), ],
            "x": [[
                {"c": 3, "p": [2, 2]},
                {"c": 4, "p": [1, 2]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [1, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[4, 5, 4],
        constraints=[
            [1, 1, 1, "<", 8],
            [3, 2, 1, "<", 15],
        ],
        sensitive={
            "c": [
                ([0], None),
            ],
            "b": [
                ([0],
                 # 14,
                 None,
                 ),
                ([1],
                 22,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 10],), ],
            # "x": [[
            #     {"c": 3, "p": [2, 2]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([0], [1, 2], [-1, 1]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 5, 2, 4],
        constraints=[
            [2, 3, 1, 2, "<", 20],
            [3, 2, 2, 2, "<", 14],
            [3, 4, 4, 3, "<", 22]
        ],
        sensitive={
            # "p": [([1], [2, 1, 0]), ],

            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [([1], None), ],
            "b": [
                ([0], 14),
                ([1], None),
                # (None, [4, 10, 10])
            ],
            "A": [([2, 3, 1, 2, "<", 14],), ],
            "x": [[{"c": 6, "p": [1, 4, 6]}, {"c": 6, "p": [1, 3, 3]}]]
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[7, 3, 2],
        constraints=[
            [4, 2, 3, "<", 10],
            [3, 1, 2, "<", 6],
        ],
        sensitive={
            "c": [
                ([0], None),
            ],
            "b": [
                ([0],
                 # 14,
                 None,
                 ),
                ([1],
                 20,
                 # None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 6],), ],
            # "x": [[
            #     {"c": 3, "p": [2, 2]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([2], [1, 2], [-1, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[3, 1, 2],
        constraints=[
            [1, 1, 4, "<", 28],
            [2, 2, 1, "<", 42],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 14,
                 # None,
                 ),
                ([1],
                 # 15,
                 None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 26],), ],
            "x": [[
                {"c": 3, "p": [2, 2]},
                {"c": 4, "p": [2, 2]},
            ]]
            # "p": [([0], [1, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[8, 10, 5],
        constraints=[
            [1, 1, 1, "<", 11],
            [4, 12, 1, "<", 48],
            [2, 3, 1, "<", 20],
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                ([0], None),
            ],
            "b": [
                ([2],
                 24,
                 # None,
                 ),
                ([0],
                 # 8,
                 None,
                 )
            ],
            "A": [([2, 1, 2, "<", 18],), ],
            "x": [[
                {"c": 4, "p": [3, 1, 1]},
                {"c": 1, "p": [1, 1, -1]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [3, 11, 8]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[5, 8, 10],
        constraints=[
            [1, 1, 1, "<", 11],
            [1, 4, 12, "<", 48],
            [1, 2, 3, "<", 20],
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                ([1], None),
            ],
            "b": [
                ([2],
                 24,
                 # None,
                 ),
                ([0],
                 # 8,
                 None,
                 )
            ],
            "A": [([2, 2, 1, "<", 18],), ],
            "x": [[
                {"c": 4, "p": [3, 1, 1]},
                {"c": 1, "p": [1, 1, -1]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [3, 11, 8]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[4, 9, 7],
        constraints=[
            [1, 12, 4, "<", 48],
            [1, 1, 1, "<", 11],
            [1, 3, 2, "<", 20],
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                ([2], None),
            ],
            "b": [
                ([2],
                 24,
                 # None,
                 ),
                ([1],
                 # 8,
                 None,
                 )
            ],
            "A": [([2, 1, 2, "<", 18],), ],
            "x": [[
                {"c": 1, "p": [1, 1, -1]},
                {"c": 4, "p": [3, 1, 1]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [3, 11, 8]), ],
        }
        )
lp_list.append(lp)


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
                ([1],
                 9,
                 ),
                ([2],
                 #8,
                 None,
                 )
            ],
            "A": [([2, 2, 1, "<", 16],), ],
            "x": [[
                {"c": 4, "p": [4, 2, 1]},
                {"c": 7, "p": [1, 1, 2]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [3, 11, 8]), ],
        }
        )
lp_list.append(lp)

lp = LP(qtype="max",
        goal=[5, 8, 12],
        constraints=[
            [1, 1, 1, "<", 11],
            [1, 2, 3, "<", 20],
            [1, 4, 12, "<", 48]
        ],
        sensitive={
            # ([0], None, 5) 表示分析c_1的取值范围，以及c_1=5时的结果
            # (None, [2, 5]) 表示分析所有c取值为[2, 5]时的结果
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 6,
                 ),
                ([2],
                 #8,
                 None,
                 )
            ],
            "A": [([2, 2, 1, "<", 14],), ],
            "x": [[
                {"c": 7, "p": [1, 1, 2]},
                {"c": 4, "p": [2, 4, 1]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [3, 11, 8]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 3, 7],
        constraints=[
            [1, 1, 4, "<", 28],
            [2, 2, 1, "<", 42],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 14,
                 # None,
                 ),
                ([1],
                 # 15,
                 None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 26],), ],
            "x": [[
                {"c": 3, "p": [2, 2]},
                {"c": 4, "p": [1, 2]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [1, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[5, 3, 2],
        constraints=[
            [1, 1, 1, "<", 9],
            [5, 2, 3, "<", 30],
            # [1, -2, 1, "<", 18],
        ],
        sensitive={
            "c": [
                ([1], None),
            ],
            "b": [
                ([0],
                 18,
                 None,
                 ),
                ([1],
                 # 15,
                 None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([2, 2, 3, "<", 12],), ],
            "x": [[
                {"c": 3, "p": [2, 2]},
                {"c": 3, "p": [1, 1]},
                # {"c": 4, "p": [3, 2]}
            ]]
            # "p": [([0], [1, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[2, 4, 3],
        constraints=[
            [1, 2, 1, "<", 16],
            [2, 5, 6, "<", 60],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([0],
                 # 3,
                 None,
                 ),
                ([1],
                 # 9,
                 None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([1, 2, 3, "<", 26],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([1], [3, 4], [2, 3]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[4, 6, 5],
        constraints=[
            [2, 5, 6, "<", 60],
            [1, 2, 1, "<", 16],
        ],
        sensitive={
            "c": [
                ([2], None),
            ],
            "b": [
                ([1],
                 # 3,
                 None,
                 ),
                ([0],
                 # 9,
                 None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([3, 2, 1, "<", 26],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([1], [4, 3], [3, 2]), ],
        }
        )
lp_list.append(lp)


lp = LP(qtype="max",
        goal=[6, 4, 3],
        constraints=[
            [2, 1, 2, "<", 15],
            [1, 3, 4, "<", 30],
        ],
        sensitive={
            "c": [
                ([1], None),
            ],
            "b": [
                ([0],
                 9,
                 # None,
                 ),
                ([1],
                 # 7,
                 None,
                 ),
                # (None, [16, 10])
            ],
            "A": [([1, 2, 3, "<", 18],), ],
            # "x": [[
            #     {"c": 4, "p": [1, 3, 1]},
            #     # {"c": 4, "p": [3, 2]}
            # ]]
            "p": [([2], [1, 2], [-1, 2]), ],
        }
        )
lp_list.append(lp)


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

final_lp_list1 = []
final_lp_list2 = []
count1 = 0
count2 = 0

count = 0
for l in lp_json_list_loaded:
    import json
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)
    lp2phase = deepcopy(lp)

    lp.solve(method="simplex")
    lp.sensitive_analysis()

    template = latex_jinja_env.get_template('/utils/lp_sensitivity.tex')
    tex = template.render(
        question_table_iters=iter(range(1, 5)),
        answer_table_iters=iter(range(1, 20)),
        show_question = True,
        show_answer = True,
#        standardized_lp = lp.standardized_LP(),
        #pre_description=u"""有线性规划问题
        #""",
        #after_description=u"""
        #""",
        lp=lp,
        show_only_opt_table = True,
    )


    if lp.solutionCommon.nit in [2] and lp.res.status == 0:
        r.clipboard_append(tex)
        final_lp_list1.append(lp.json)
        count1 += 1
    if lp.solutionCommon.nit in [3,4] and lp.res.status == 0:
        final_lp_list2.append(lp.json)
        count2 += 1
#        r.clipboard_append(tex)

    # if lp.solutionCommon.nit >=3:
    #     #final_lp_list.append(lp.json)
    #     count += 1
    #     print(lp_dict)

    #count += 1
    r.clipboard_append(tex)

print(count1, count2)

r.mainloop()

with open(SAVED_QUESTION_2_iter, 'wb') as f:
        pickle.dump(final_lp_list1, f)
with open(SAVED_QUESTION_3_iter, 'wb') as f:
    pickle.dump(final_lp_list2, f)

#print(count)

