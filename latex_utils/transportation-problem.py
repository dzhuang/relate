# -*- coding: utf-8 -*-

from .utils.latex_utils import latex_jinja_env
from .utils.transportation import transportation
import numpy as np

transport_dict_list = []

# # # 例题
# # tr_dict = {
# #     "sup": [75, 125, 100], #[[72, 78], [115, 135], 100],
# #     # "sup": [[72, 78], [115, 135], 100],
# #     "dem": [80, 65, 70, 85],
# #     "costs": np.array ([
# #         [9., 10., 13., 17.],
# #         [7., 8., 14., 16.],
# #         [20, 14., 8., 14.]
# #     ]),
# #     "dem_name_prefix": u"市场",
# #     "sup_name_prefix": u"工厂",
# #     "dem_desc": u"城市"
# # }
#
# #transport_dict_list.append(tr_dict)
#
# # # 例题
# # tr_dict = {
# #     "sup": [6, 10, 7], #[[72, 78], [115, 135], 100],
# #     # "sup": [[72, 78], [115, 135], 100],
# #     "dem": [3, 5, 9, 6],
# #     "costs": np.matrix ([
# #         3, 9, 8, 6,
# #         12, 25, 7, 10,
# #         6, 11, 13, 14
# #     ]).reshape(3,4),
# #     # "dem_name_prefix": u"市场",
# #     # "sup_name_prefix": u"工厂",
# #     # "dem_desc": u"城市"
# # }
# #
# # transport_dict_list.append(tr_dict)
#
# # # 例题
# # tr_dict = {
# #     "sup": [40, 20, 15], #[[72, 78], [115, 135], 100],
# #     # "sup": [[72, 78], [115, 135], 100],
# #     "dem": [10, 20, 15, 16, 14],
# #     "costs": np.matrix ([
# #         8, 15, 20, 14, 4,
# #         5, 7, 6, 9, 8,
# #         3, 9, 10, 16, 13,
# #     ]).reshape(3,5),
# #     # "dem_name_prefix": u"市场",
# #     # "sup_name_prefix": u"工厂",
# #     # "dem_desc": u"城市"
# # }
#
# # transport_dict_list.append(tr_dict)
#
#
# # # 重复率太高
# # tr_dict = {
# #     "sup": [5, 6, 8],
# #     "dem": [4, 8, 6],
# #     "costs": np.matrix ([
# #         3, 1, 3,
# #         4, 6, 2,
# #         2, 8, 5
# #     ]).reshape(3,3),
# # }
# # transport_dict_list.append(tr_dict)
#
#
tr_dict = {
    "sup": [70, 120, 100],
    "dem": [75, 60, 70],
    "costs": np.matrix ([
        8, 9, 12,
        6, 7, 13,
        18, 12, 6
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        100, 60, 50
    ],
    "dem": [
        40, 60, 65, 45
    ],
    "costs": np.matrix ([
        4, 3, 5, 4,
        6, 7, 8, 3,
        3, 2, 4, 5,
    ]).reshape(3,4),
    "required_init_method": ["NCM"]
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        90, 70, 50
    ],
    "dem": [
        50, 80, 70, 10
    ],
    "costs": np.matrix ([
        4, 3, 5, 4,
        6, 7, 8, 3,
        3, 2, 4, 5,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [70, 80, 90],
    "dem": [60, 100, 50],
    "costs": np.matrix ([
        4, 6, 5,
        2, 3, 8,
        8, 7, 9
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [90, 70, 60],
    "dem": [80, 100, 60],
    "costs": np.matrix ([
        4, 3, 5,
        7, 4, 9,
        6, 5, 7
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [70, 120, 100],
    "dem": [75, 60, 70],
    "costs": np.matrix ([
        8, 9, 12,
        6, 7, 13,
        18, 12, 6
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [70, 120, 100],
    "dem": [75, 60, 70, 85],
    "costs": np.matrix ([
        8, 9, 12, 10,
        6, 10, 11, 8,
        18, 8, 9, 6
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)



tr_dict = {
    "sup": [5, 6, 8],
    "dem": [4, 7, 6, 2],
    "costs": np.matrix ([
        3, 1, 3, 2,
        4, 6, 2, 3,
        2, 8, 5, 4,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [90, 70, 60, 20],
    "dem": [80, 100, 60],
    "costs": np.matrix ([
        6, 3, 5,
        4, 8, 9,
        6, 5, 7,
        5, 4, 8,
    ]).reshape(4,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [70, 80, 90],
    "dem": [60, 100, 50, 30],
    "costs": np.matrix ([
        4, 6, 5, 7,
        2, 3, 8, 6,
        8, 7, 9, 5
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [30, 40, 30],
    "dem": [25, 20, 40, 15],
    "costs": np.matrix ([
        5, 6, 9, 8,
        9, 4, 8, 7,
        10, 7, 5, 9
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [30, 40, 30],
    "dem": [25, 20, 40],
    "costs": np.matrix ([
        5, 6, 9,
        9, 4, 8,
        10, 7, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [25, 25, 50],
    "dem": [15, 20, 30, 35],
    "costs": np.matrix ([
        10, 5, 6, 7,
        8, 2, 7 ,6,
        8, 3, 4, 8
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [25, 25, 50],
    "dem": [15, 20, 30],
    "costs": np.matrix ([
        10, 5, 6,
        8, 2, 7,
        8, 3, 4,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        16, 22, 10
    ],
    "dem": [
        18, 14, 12, 4
    ],
    "costs": np.matrix ([
        4, 12, 4, 8,
        8, 5, 11, 5,
        2, 10, 3, 4
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        90, 70, 50
    ],
    "dem": [
        50, 80, 70
    ],
    "costs": np.matrix ([
        4, 3, 5,
        6, 7, 8,
        5, 2, 9,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)



tr_dict = {
    "sup": [
        25, 45, 50
    ],
    "dem": [
        30, 30, 40
    ],
    "costs": np.matrix ([
        1, 6, 3,
        3, 6, 4,
        4, 5, 7
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        25, 45, 50
    ],
    "dem": [
        30, 30, 40, 20
    ],
    "costs": np.matrix ([
        1, 6, 3, 2,
        3, 6, 4, 5,
        4, 5, 7, 6
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        90, 90, 80
    ],
    "dem": [
        80, 100, 60, 20
    ],
    "costs": np.matrix ([
        5, 2, 3, 2,
        8, 4, 3, 4,
        4, 6, 4, 5
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        16, 20, 22
    ],
    "dem": [
        8, 14, 12
    ],
    "costs": np.matrix ([
        4, 12, 4,
        2, 10, 3,
        8, 5, 11
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        16, 20, 22
    ],
    "dem": [
        8, 14, 12, 24
    ],
    "costs": np.matrix ([
        4, 12, 4, 7,
        2, 10, 3, 6,
        8, 5, 11, 4
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        100, 60, 80
    ],
    "dem": [
        40, 60, 60
    ],
    "costs": np.matrix ([
        2, 5, 4,
        3, 7, 6,
        4, 2, 4
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        100, 60, 80
    ],
    "dem": [
        40, 60, 60, 80
    ],
    "costs": np.matrix ([
        2, 5, 4, 5,
        3, 7, 6, 5,
        3, 4, 4, 8
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        25, 30, 42
    ],
    "dem": [
        32, 40, 30
    ],
    "costs": np.matrix ([
        6, 2, 5,
        8, 12, 7,
        4, 15, 8
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        25, 30, 42, 15
    ],
    "dem": [
        32, 40, 40
    ],
    "costs": np.matrix ([
        6, 2, 5,
        8, 6, 7,
        12, 10, 8,
        10, 4, 9,
    ]).reshape(4,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        20, 30, 40
    ],
    "dem": [
        10, 30, 30
    ],
    "costs": np.matrix ([
        4, 2, 3,
        3, 1, 6,
        2, 3, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        20, 30, 40
    ],
    "dem": [
        10, 20, 35, 25
    ],
    "costs": np.matrix ([
        4, 2, 3, 3,
        3, 1, 6, 5,
        2, 3, 5, 2,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        60, 80, 45
    ],
    "dem": [
        50, 45, 56
    ],
    "costs": np.matrix ([
        2, 3, 4,
        3, 5, 2,
        4, 3, 1
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        60, 80, 45
    ],
    "dem": [
        50, 45, 56, 34
    ],
    "costs": np.matrix ([
        2, 3, 4, 2,
        3, 5, 2, 3,
        4, 3, 1, 5
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        60, 80, 45
    ],
    "dem": [
        50, 45, 56, 34
    ],
    "costs": np.matrix ([
        2, 3, 4, 2,
        3, 5, 2, 3,
        4, 3, 1, 5
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        15, 25, 20
    ],
    "dem": [
        10, 20, 18, 12
    ],
    "costs": np.matrix ([
        2, 4, 5, 6,
        5, 2, 3, 2,
        3, 1, 6, 3,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        40, 40, 30
    ],
    "dem": [
        40, 45, 25
    ],
    "costs": np.matrix ([
        6, 3, 8,
        11, 6, 15,
        9, 7, 12
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        40, 40, 30
    ],
    "dem": [
        20, 35, 25, 30
    ],
    "costs": np.matrix ([
        6, 3, 8, 7,
        11, 6, 15, 8,
        9, 7, 12, 10
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        18, 15, 19
    ],
    "dem": [
        14, 13, 15
    ],
    "costs": np.matrix ([
        3, 8, 3,
        10, 12, 9,
        5, 8, 9
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        25, 40, 30
    ],
    "dem": [
        30, 35, 25
    ],
    "costs": np.matrix ([
        6, 7, 4,
        4, 5, 2,
        7, 6, 3
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        35, 20, 40
    ],
    "dem": [
        35, 20, 15, 25
    ],
    "costs": np.matrix ([
        7, 4, 3, 5,
        4, 5, 6, 2,
        5, 6, 3, 4
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        8, 12, 4
    ],
    "dem": [
        4, 10, 8
    ],
    "costs": np.matrix ([
        4, 3, 5,
        6, 5, 4,
        8, 6, 7
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        8, 12, 4
    ],
    "dem": [
        4, 10, 8, 2
    ],
    "costs": np.matrix ([
        4, 3, 5, 6,
        6, 5, 4, 3,
        8, 6, 7, 4
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        8, 12, 4
    ],
    "dem": [
        4, 10, 8, 2
    ],
    "costs": np.matrix ([
        4, 3, 5, 6,
        6, 5, 4, 3,
        8, 6, 7, 4
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        65, 40, 80
    ],
    "dem": [
        50, 55, 63
    ],
    "costs": np.matrix ([
        3, 2, 4,
        2, 4, 6,
        6, 5, 3,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        65, 40, 80
    ],
    "dem": [
        50, 55, 63, 17
    ],
    "costs": np.matrix ([
        3, 2, 4, 5,
        2, 4, 6, 3,
        6, 5, 3, 4,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        8, 14, 17
    ],
    "dem": [
        5, 12, 9
    ],
    "costs": np.matrix ([
        3, 11, 4,
        1, 9, 2,
        7, 4, 10,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        8, 14, 17
    ],
    "dem": [
        5, 12, 9, 13
    ],
    "costs": np.matrix ([
        3, 11, 4, 5,
        1, 7, 2, 3,
        7, 4, 10, 6
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        50, 60, 30
    ],
    "dem": [
        30, 70, 20
    ],
    "costs": np.matrix ([
        10, 8, 12,
        6, 10, 12,
        7, 14, 10,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        50, 60, 30
    ],
    "dem": [
        30, 70, 20, 20
    ],
    "costs": np.matrix ([
        10, 8, 12, 9,
        6, 10, 12, 5,
        7, 14, 10, 8,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        50, 60, 30
    ],
    "dem": [
        30, 70, 15, 25
    ],
    "costs": np.matrix ([
        10, 8, 12, 9,
        6, 10, 12, 5,
        7, 14, 10, 8,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        50, 60, 30
    ],
    "dem": [
        30, 65, 20, 25
    ],
    "costs": np.matrix ([
        10, 8, 12, 9,
        6, 10, 12, 5,
        7, 14, 10, 8,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        50, 60, 30
    ],
    "dem": [
        30, 65, 20, 25
    ],
    "costs": np.matrix ([
        10, 8, 11, 9,
        6, 10, 10, 5,
        7, 14, 12, 8,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        60, 70, 80
    ],
    "dem": [
        70, 60, 70
    ],
    "costs": np.matrix ([
        2, 3, 2,
        4, 1, 3,
        6, 2, 6
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        60, 70, 80
    ],
    "dem": [
        70, 60, 70, 10
    ],
    "costs": np.matrix ([
        2, 3, 2, 5,
        4, 1, 3, 2,
        6, 2, 6, 3,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        60, 65, 85
    ],
    "dem": [
        70, 60, 70, 10
    ],
    "costs": np.matrix ([
        2, 3, 2, 5,
        4, 1, 3, 2,
        6, 2, 6, 3,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        60, 65, 85
    ],
    "dem": [
        60, 55, 85, 10
    ],
    "costs": np.matrix ([
        2, 3, 2, 5,
        4, 1, 3, 2,
        6, 2, 6, 3,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        45, 30, 55
    ],
    "dem": [
        40, 30, 50
    ],
    "costs": np.matrix ([
        5, 1, 7,
        6, 4, 2,
        3, 7, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        45, 30, 55
    ],
    "dem": [
        20, 40, 60
    ],
    "costs": np.matrix ([
        5, 1, 7,
        6, 2, 2,
        7, 4, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        45, 30, 55
    ],
    "dem": [
        20, 40, 60, 10
    ],
    "costs": np.matrix ([
        5, 1, 7, 2,
        4, 6, 2, 5,
        7, 4, 5, 2
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        80, 60, 70
    ],
    "dem": [
        50, 80, 70
    ],
    "costs": np.matrix ([
        4, 2, 3,
        3, 8, 6,
        4, 5, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        80, 60, 70
    ],
    "dem": [
        50, 80, 70, 10
    ],
    "costs": np.matrix ([
        4, 2, 3, 2,
        3, 8, 6, 5,
        4, 5, 5, 7,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        80, 65, 70
    ],
    "dem": [
        50, 80, 70
    ],
    "costs": np.matrix ([
        4, 2, 3,
        3, 8, 6,
        4, 5, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        80, 65, 70
    ],
    "dem": [
        50, 80, 70, 15
    ],
    "costs": np.matrix ([
        4, 2, 3, 4,
        3, 8, 6, 2,
        4, 5, 5, 7,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        80, 65, 60
    ],
    "dem": [
        50, 80, 70
    ],
    "costs": np.matrix ([
        4, 2, 3,
        3, 8, 6,
        4, 5, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

## 有退化解，检验数为0，基本可行方案不唯一，但去掉0之后的基本可行方案是唯一的.
tr_dict = {
    "sup": [
        80, 65, 60
    ],
    "dem": [
        50, 80, 60, 15
    ],
    "costs": np.matrix ([
        4, 2, 3, 2,
        3, 8, 6, 4,
        4, 5, 5, 6,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        75, 65, 60
    ],
    "dem": [
        40, 75, 70
    ],
    "costs": np.matrix ([
        4, 2, 3,
        3, 8, 6,
        4, 5, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        75, 65, 60
    ],
    "dem": [
        40, 75, 60
    ],
    "costs": np.matrix ([
        4, 2, 3,
        3, 8, 6,
        4, 5, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        75, 65, 60
    ],
    "dem": [
        40, 75, 55
    ],
    "costs": np.matrix ([
        4, 2, 3,
        3, 8, 6,
        4, 5, 5
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        50, 35, 45
    ],
    "dem": [
        30, 40, 50
    ],
    "costs": np.matrix ([
        3, 2, 4,
        2, 3, 5,
        1, 4, 2
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        50, 35, 45
    ],
    "dem": [
        30, 40, 50, 10
    ],
    "costs": np.matrix ([
        3, 2, 4, 3,
        2, 3, 5, 6,
        1, 4, 2, 3
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        50, 35, 45
    ],
    "dem": [
        30, 40, 40, 20
    ],
    "costs": np.matrix ([
        3, 2, 4, 3,
        2, 3, 5, 6,
        1, 4, 2, 3
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        50, 35, 45
    ],
    "dem": [
        25, 40, 35, 30
    ],
    "costs": np.matrix ([
        3, 2, 4, 3,
        2, 3, 5, 6,
        1, 4, 2, 3
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        45, 55, 30
    ],
    "dem": [
        30, 40, 35, 25
    ],
    "costs": np.matrix ([
        3, 2, 4, 3,
        2, 3, 5, 6,
        1, 4, 2, 3
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


#
# tr_dict = {
#     "sup": [
#         70, 60, 55
#     ],
#     "dem": [
#         60, 80, 20
#     ],
#     "costs": np.matrix ([
#         3, 2, 2,
#         6, 4, 4,
#         5, 4, 5,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)
#
# tr_dict = {
#     "sup": [
#         60, 70, 55
#     ],
#     "dem": [
#         60, 80, 20
#     ],
#     "costs": np.matrix ([
#         3, 2, 2,
#         6, 7, 4,
#         5, 4, 5,
#     ]).reshape(3,3),
# }
# transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        70, 70, 50
    ],
    "dem": [
        60, 90, 20
    ],
    "costs": np.matrix ([
        3, 2, 2,
        6, 3, 4,
        5, 4, 3,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        50, 80, 60
    ],
    "dem": [
        60, 90, 30, 10
    ],
    "costs": np.matrix ([
        5, 2, 4, 1,
        3, 6, 5, 7,
        2, 4, 3, 3,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        70, 60, 50
    ],
    "dem": [
        60, 90, 20
    ],
    "costs": np.matrix ([
        3, 2, 2,
        6, 3, 4,
        5, 4, 3,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        65, 55, 60
    ],
    "dem": [
        70, 45, 35, 30
    ],
    "costs": np.matrix ([
        5, 4, 6, 8,
        6, 3, 4, 5,
        4, 7, 6, 7,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)


tr_dict = {
    "sup": [
        70, 60, 55
    ],
    "dem": [
        60, 90, 20
    ],
    "costs": np.matrix ([
        3, 2, 2,
        6, 3, 4,
        5, 4, 3,
    ]).reshape(3,3),
}
transport_dict_list.append(tr_dict)

tr_dict = {
    "sup": [
        90, 70, 50
    ],
    "dem": [
        50, 80, 70, 10
    ],
    "costs": np.matrix ([
        4, 3, 5, 4,
        6, 7, 8, 3,
        5, 2, 9, 5,
    ]).reshape(3,4),
}
transport_dict_list.append(tr_dict)

print(len(transport_dict_list))

try:
    # Python 3.x
    from tkinter import Tk
except ImportError:
    # Python 2.x
    from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()

import pickle
#import dill as pickle
with open('transport.bin', 'wb') as f:
    pickle.dump(transport_dict_list, f)

with open('transport.bin', 'rb') as f:
    transport_dict_list_loaded = pickle.load(f)

INIT_METHOD_DICT = {"LCM": u"最小元素法", "NCM": u"西北角法", "VOGEL": u"伏格尔法"}

# 产销平衡，(西北角>2 <=3 or 最小元素>2 <=3) 求解有退化，最后无退化
count1 = 0
count1_list = []


for i, tr in enumerate(transport_dict_list_loaded):
#    r.clipboard_clear ()
    required_init_method = tr.pop("required_init_method", None)
    t = transportation(**tr)
    template = latex_jinja_env.get_template('/utils/transportation.tex')
    required_init_method = None
    if required_init_method:
        assert required_init_method in ["LCM", "NCM", "VOGEL"]

    show_LCM_result = True
    show_NCM_result = True
    show_VOGEL_result = True

    # show_LCM_result = False
    # show_NCM_result = False
    # show_VOGEL_result = False

    if required_init_method == "LCM":
        show_LCM_result = True
    elif required_init_method == "NCM":
        show_NCM_result = True
    elif required_init_method == "VOGEL":
        show_VOGEL_result = True

    used_method_list = [required_init_method]
    if not required_init_method:
        used_method_list = [
            "NCM",
            "LCM",
            "VOGEL"
        ]

    method_result_list = []
    if "NCM" in used_method_list:
        NCM_result = t.solve(init_method="NCM")
        method_result_list.append(NCM_result)
    if "LCM" in used_method_list:
        LCM_result = t.solve(init_method="LCM")
        method_result_list.append(LCM_result)
    if "VOGEL" in used_method_list:
        VOGEL_result = t.solve(init_method="VOGEL")
        method_result_list.append(VOGEL_result)

    tex = template.render(
        question_table_iters=iter(range(1, 5)),
        answer_table_iters=iter(range(1, 100)),
        show_question = True,
        show_answer = True,
        # problem_description_pre = u"""
        #             设有产量分别为30，40，30的三个原料产地，欲将原材料运往销量分别为
        #             25，20，40的三个销地，单位运价如下表所示。试求总运费最省的调运方案。""",
        t = t,
#        LCM_result = LCM_result,
#        NCM_result = NCM_result,
#        VOGEL_result = VOGEL_result,
        method_result_list=method_result_list,
        show_LCM_result = show_LCM_result,
        show_NCM_result = show_NCM_result,
        show_VOGEL_result = show_VOGEL_result,
        standardize_only = False,
        init_method = INIT_METHOD_DICT.get(required_init_method, None),
        used_method_list = [INIT_METHOD_DICT.get(used_method) for used_method in used_method_list],
    )

    r.clipboard_append(tex)



    if True: #i < len(transport_dict_list_loaded) - 1:
        print("dem:", t.surplus_dem, ", sup:", t.surplus_sup)
        if t.is_standard_problem:
            print("标准化问题")
        elif t.is_sup_bounded_problem:
            if t.is_infinity_bounded_problem:
                print("供应无上限的有下限要求的问题")
            elif t.is_sup_bounded_problem:
                print("供应有下限要求的问题")
        elif t.is_dem_bounded_problem:
            if t.is_infinity_bounded_problem:
                print("需求无上限的有下限要求的问题")
            elif t.is_dem_bounded_problem:
                print("需求有下限要求的问题")
        else:
            print("产销不平衡问题")
        if NCM_result:
            print(u"西北角法：迭代次数", len(NCM_result.solution_list),\
                u"初始化时有退化解：",NCM_result.has_degenerated_init_solution,\
                u"计算中有退化解：", NCM_result.has_degenerated_mid_solution,\
                u"最优解唯一：", NCM_result.has_unique_solution, \
                u"最优解退化：", NCM_result.final_is_degenerated_solution, \
                u"z", NCM_result.z)
        if LCM_result:
            print(u"最小元素法：迭代次数", len(LCM_result.solution_list),\
                u"初始化时有退化解：",LCM_result.has_degenerated_init_solution,\
                u"计算中有退化解：", LCM_result.has_degenerated_mid_solution,\
                u"最优解唯一：", LCM_result.has_unique_solution, \
                u"最优解退化：", LCM_result.final_is_degenerated_solution, \
                u"z", LCM_result.z)
        if VOGEL_result:
            print(u"VOGEL法：迭代次数", len(VOGEL_result.solution_list),\
                u"初始化时有退化解：",VOGEL_result.has_degenerated_init_solution,\
                u"计算中有退化解：", VOGEL_result.has_degenerated_mid_solution,\
                u"最优解唯一：", VOGEL_result.has_unique_solution,\
                u"最优解退化：", VOGEL_result.final_is_degenerated_solution, \
                u"z", VOGEL_result.z)


        # count1 产销平衡，(西北角>2 <=3 or 最小元素>2 <=3) 求解有退化，最后无退化

        if (t.is_standard_problem
            and
                (len(NCM_result.solution_list) in range(2,4) or len(LCM_result.solution_list) in range(2,4))
            and not (NCM_result.final_is_degenerated_solution or LCM_result.final_is_degenerated_solution or VOGEL_result.final_is_degenerated_solution)
            and (NCM_result.has_degenerated_mid_solution or LCM_result.has_degenerated_mid_solution or NCM_result.has_degenerated_init_solution or NCM_result.has_degenerated_init_solution)
            ):
            count1 += 1
            count1_list.append(t)


print("count1:", count1)
for i in count1_list:
    print(i.dem, i.sup)

