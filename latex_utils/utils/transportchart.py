# -*- coding: utf-8 -*-

class PriceChart(object):
    def __init__(self, sup, dem, price, sup_name=None, dem_name=None, table_type="table"):
        assert isinstance(sup, list)
        assert isinstance(dem, list)
        assert isinstance(price, list)
        self.sup = sup
        self.dem = dem
        self.price = price
        if not table_type:
            self.table_type = "table"
        else:
            self.table_type = table_type

        if sup_name:
            assert isinstance(sup_name, list)
            self.sup_name = sup_name
            assert len(sup_name) == len(sup)
        else:
            self.sup_name = None

        if dem_name:
            assert isinstance(dem_name, list)
            assert len(dem_name) == len(dem)
            self.dem_name = dem_name
        else:
            self.dem_name = None

        assert len(sup) == len(price)
        for p in price:
            assert len(dem) == len(p)

        self.n_sup = len(sup)
        self.n_dem = len(dem)
        self.price_list = self.get_price_string_list()
        if not self.dem_name:
            self.dem_name_str = None
        else:
            self.dem_name_str = self.get_dem_name_str()

        if not self.sup_name:
            self.sup_name_list = None
        else:
            self.sup_name_list = sup_name

        self.dem_quantity_str = self.get_dem_quantity_string()

    def get_price_string_list(self):
        s_list = []
        for i, pr in enumerate(self.price):
            # make a copy of lines in price
            p = [ps for ps in pr]
            p.append(self.sup[i])
            p_string = "&".join([str(ps) for ps in p])
            s_list.append(p_string)
        return s_list

    def get_dem_name_str(self):
        name_string = "&".join(self.dem_name) + "&"
        return name_string

    def get_dem_quantity_string(self):
        total = 0
        for q in self.dem:
            total += int(q)
        q_string = "&".join([str(q) for q in self.dem])
        if self.table_type == "keytable":
            return q_string + " & " + str(total)
        else:
            return q_string + " & "


class BaseChart(object):
    # 运输作业表定义
    def __init__(self, pricechart):
        self.sup = pricechart.sup
        self.dem = pricechart.dem
        self.price = pricechart.price
        assert isinstance(pricechart.sup, list)
        assert isinstance(pricechart.dem, list)
        assert isinstance(pricechart.price, list)
        for p in self.price:
            assert isinstance(p, list)
            assert len(self.dem) == len(p)
        assert len(self.sup) == len(self.price)
        self.total = 0
        for s in pricechart.sup:
            self.total += s

        total_test = 0
        for d in pricechart.dem:
            total_test += d

        assert self.total == total_test
        self.n_sup = len(pricechart.sup)
        self.n_dem = len(pricechart.dem)
        self.price_string = self.get_price_string()

    def get_price_string(self):
        # {8,7,9,0},{2,3,8,0},{4,6,5,0}
        s = []
        for p in self.price:
            p_string = "{" + ",".join([str(ps) for ps in p]) + "}"
            # reversed order
            s.insert(0, p_string)
        return ",".join(s)


class TransportResult(object):
    # 方案
    def __init__(self, base, transport, verify):
        assert isinstance(base, BaseChart)
        assert isinstance(transport, list)
        assert len(transport) == base.n_sup
        for t in transport:
            # 运输量最右侧一个数为空""
            assert len(t) == base.n_dem + 1

        self.transport = transport
        self.transport_string = self.get_transport_string()

        if verify:
            assert isinstance(verify, list)
            assert len(verify) == base.n_sup
            for v in verify:
                assert len(v) == base.n_dem
            self.verify = verify
            self.verify_list = self.get_verify_string_list()
        else:
            self.verify = None


    def get_transport_string(self):
        s = []
        for t in self.transport:
            i_list = []
            for i in t:
                if str(i).startswith("\"") and str(i).endswith("\""):
                    i_list.append(str(i))
                else:
                    i_list.append("\"" + str(i) + "\"")
            t_string = "{" + ",".join(i_list) + "}"
            #t_string = t_string.replace("\"\"", "\"")
            # reversed order
            s.insert(0, t_string)
        return ",".join(s)

    def get_verify_string_list(self):
        s_list = []
        for v in self.verify:
            v_string = "&".join([ str(vs) for vs in v])
            # reversed order
            s_list.append( v_string)
        return s_list