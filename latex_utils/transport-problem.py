# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.transportchart import PriceChart, BaseChart, TransportResult, TransportSolve
import numpy as np

price = PriceChart(
    sup=[30, 40, 30],
    #sup_name=[u"A", u"B", u"C"],
    dem=[25, 20, 40],
    #dem_name=[u"I", u"II", u"III"],
    price = [
        [5, 6, 9],
        [9, 4, 8],
        [10, 7, 5],
    ],
    table_type="table"
)


standard_price = PriceChart(
    sup=price.sup
    ,
    #sup_name=price.sup_name,
    dem=price.dem + [15]
    ,
    #dem_name=price.dem_name + [u'IV'],
    price = [
        [5, 6, 9, 0],
        [9, 4, 8, 0],
        [10, 7, 5, 0],
    ]
    ,
    table_type="keytable"
)

pricechart_list = []
pricechart_list.append(price)
pricechart_list.append(standard_price)

basechart = BaseChart(
    pricechart=standard_price,
    #sup_name=["A","B","C"],
    #dem_name=["I","II","III","IV"]
)

result1 = TransportResult(
    base = basechart,
    transport = [
        ["25", "", "", "5", ""],
        ["", "20", "10", "10", ""],
        ["","","30","",""],
    ],
    verify=[
        ["", "2", "1", ""],
        ["4", "", "", ""],
        ["8", "6", "", "3"],
    ]
)

# result2 = TransportResult(
#     base = basechart,
#     transport = [
#         ["", "40", "10", "", ""],
#         ["25", "", "", "10", ""],
#         ["5","","40","",""],
#     ],
#     verify=[
#         [0, "", "", -1],
#         ["", "2", "2", ""],
#         ["", "0", "", "3"],
#     ]
# )
#
# result3 = TransportResult(
#     base = basechart,
#     transport = [
#         ["", "40", "5", "5"],
#         ["30", "", "", "5"],
#         ["","","45",""],
#     ],
#     verify=[
#         [1, "", "", ""],
#         ["", "1", "1", ""],
#         ["0", "0", "", "2"],
#     ]
# )


result_list = []
result_list.extend([result1,
                    # result2, result3
                    ])

template = latex_jinja_env.get_template('/utils/transport-chart.tex')
tex = template.render(
    description = u"""
设有产量分别为30，40，30的三个原料产地，欲将原材料运往销量分别为25，20，40的三个销地，单位运价如下表所示。试求总运费最省的调运方案。
    """,
    pricechart_list=pricechart_list,
    base=basechart,
    result_list=result_list
)

#print tex

#_file_write("transport.tex", tex.encode('UTF-8'))

solve = TransportSolve(
    sup=price.sup
    ,
    # sup_name=price.sup_name,
    dem=price.dem + [15]
    ,
    # dem_name=price.dem_name + [u'IV'],
    price=[
        [5, 6, 9, 0],
        [9, 4, 8, 0],
        [10, 7, 5, 0],
    ]
    ,
    pricechart_table_type="table",

)

result =solve.get_result(method="LCM")

# print result.routes
# print result.has_unique_solution, result.z

solve = TransportSolve(
    sup=[72, 6, 115, 20, 100]
    ,
    # sup_name=price.sup_name,
    dem=[80, 65, 70, 85, 13]
    ,
    # dem_name=price.dem_name + [u'IV'],
    price=[
        [9, 10, 13, 17, np.inf],
        [9, 10, 13, 17, 0],
        [7, 8, 14, 16, np.inf],
        [7, 8, 14, 16, 0],
        [np.inf, 14, 8, 14, np.inf],
    ]
    ,
    pricechart_table_type="table",

)

result =solve.get_result(method="LCM")

# print result.routes
# print result.has_unique_solution, result.z

solve = TransportSolve(
    sup=price.sup
    ,
    # sup_name=price.sup_name,
    dem=price.dem + [15]
    ,
    # dem_name=price.dem_name + [u'IV'],
    price=[
        [5, 6, 9, 0],
        [9, np.inf, np.inf, 0],
        [np.inf, 7, 5, np.inf],
    ]
    ,
    pricechart_table_type="table",

)

result =solve.get_result(method="LCM")

print result.routes
print result.has_unique_solution, result.z
