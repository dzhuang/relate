# -*- coding: utf-8 -*-

from utils.latex_utils import latex_jinja_env, _file_write
from utils.transportchart import PriceChart, BaseChart, TransportResult

price = PriceChart(
    sup=[50, 35, 45],
    sup_name=[u"代工厂1", u"代工厂2", u"代工厂3"],
    dem=[30, 40, 50],
    dem_name=[u"城市A", u"城市B", u"城市C"],
    price = [
        [3, 2, 4],
        [2, 3, 5],
        [1, 4, 2],
    ],
    table_type="table"
)


standard_price = PriceChart(
    sup=price.sup
    ,
    sup_name=price.sup_name,
    dem=price.dem + [10]
    ,
    dem_name=price.dem_name + [u'城市D'],
    price = [
        [3, 2, 4, 0],
        [2, 3, 5, 0],
        [1, 4, 2, 0],
    ]
    ,
    table_type="keytable"
)

pricechart_list = []
#pricechart_list.append(price)
pricechart_list.append(standard_price)

basechart = BaseChart(
    pricechart=standard_price
)

result1 = TransportResult(
    base = basechart,
    transport = [
        ["", "40", "10", "", ""],
        ["", "", "25", "10", ""],
        ["30","","15","",""],
    ],
    verify=[
        [0, "", "", 1],
        ["-2", "-1", "", ""],
        ["", "3", "", "3"],
    ]
)

result2 = TransportResult(
    base = basechart,
    transport = [
        ["", "40", "10", "", ""],
        ["25", "", "", "10", ""],
        ["5","","40","",""],
    ],
    verify=[
        [0, "", "", -1],
        ["", "2", "2", ""],
        ["", "0", "", "3"],
    ]
)

result3 = TransportResult(
    base = basechart,
    transport = [
        ["", "40", "5", "5"],
        ["30", "", "", "5"],
        ["","","45",""],
    ],
    verify=[
        [1, "", "", ""],
        ["", "1", "1", ""],
        ["0", "0", "", "2"],
    ]
)


result_list = []
result_list.extend([result1, result2, result3])

template = latex_jinja_env.get_template('/utils/transport-chart.tex')
tex = template.render(
    # description = u"""
    # Mike公司有3个代工厂向3个城市运输新款的Zoom Jobe X球鞋。3个
    # 城市的球鞋需求量分别为30，40，50；3个代工厂的产量分别为50，35
    # 和45（单位:千双）。运价表如下所示（运价单位：千元）。试确定最
    # 经济的运输方案，且求出最小总运费。
    # """,
    pricechart_list=pricechart_list,
    base=basechart,
    result_list=result_list
)

#print tex

_file_write("transport.tex", tex.encode('UTF-8'))