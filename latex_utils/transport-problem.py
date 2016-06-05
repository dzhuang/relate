# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.transportchart import PriceChart, BaseChart, TransportResult

price = PriceChart(
    sup=[5, 10, 15],
    sup_name=[u"A", u"B", u"C"],
    dem=[6, 9, 10],
    dem_name=[u"I", u"II", u"III"],
    price = [
        [10, 15, 5],
        [4, 6, 9],
        [8, 7, 11],
    ],
    table_type="table"
)


standard_price = PriceChart(
    sup=price.sup
    ,
    sup_name=price.sup_name,
    dem=price.dem + [5]
    ,
    dem_name=price.dem_name + [u'IV'],
    price = [
        [10, 15, 5, 0],
        [4, 6, 9, 0],
        [8, 7, 11, 0],
    ]
    ,
    table_type="keytable"
)

pricechart_list = []
pricechart_list.append(price)
pricechart_list.append(standard_price)

basechart = BaseChart(
    pricechart=standard_price,
    sup_name=["A","B","C"],
    dem_name=["I","II","III","IV"]
)

result1 = TransportResult(
    base = basechart,
    transport = [
        ["", "", "5", "", ""],
        ["6", "", "4", "", ""],
        ["","9","1","5",""],
    ],
    verify=[
        [10, "14", "", 6],
        ["", "1", "", "2"],
        ["2", "", "", ""],
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
某供应商有A、B、C三个供货地，向某制造商供应零件，该制造商有I、II、III三个工厂，各工厂的需求量、各供货地的产量(单位：千件)，以及单位运价(千元/千件)如下表所示。试求使总运费最少的调运方案。
    """,
    pricechart_list=pricechart_list,
    base=basechart,
    result_list=result_list
)

#print tex

_file_write("transport.tex", tex.encode('UTF-8'))