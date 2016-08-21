# -*- coding: utf-8 -*-

import numpy as np
import copy
from collections import Counter
from scipy.optimize._linprog import OptimizeResult

DEFAULT_TRANSPORT_STRING_DICT={
    "SUPPLY_PREFIX": "A",
    "DEMAND_PREFIX": "B",
    "SUPPLY_DESC": u"产地",
    "DEMAND_DESC": u"销地",
    "SUPPLY_AMOUNT_DESC": u"产量",
    "DEMAND_AMOUNT_DESC": u"销量",
    "COST_DESC": u"单位运费",
    "VIRTUAL_SUPPLY": u"虚拟产地",
    "VIRTUAL_DEMAND": u"虚拟销地",
    "MIN_SUPPLY": u"最低供应量",
    "MAX_SUPPLY": u"最高供应量",
    "MIN_DEMAND": u"最低需求量",
    "MAX_DEMAND": u"最高需求量",
}

class NotStandardizableError(Exception):
    """for problem with lowerbound"""

def get_array_to_str_list_recursive(array_list, nan_as="", inf_as="M", tex_eq_wrap=False):
    assert isinstance(array_list, (list, np.ndarray))
    if isinstance(array_list, np.ndarray):
        array_list = array_list.tolist()
    if isinstance(array_list, list):
        for i, l in enumerate(array_list):
            if isinstance(l, (np.ndarray, list)):
                array_list[i] = get_array_to_str_list_recursive(l, nan_as=nan_as, inf_as=inf_as, tex_eq_wrap=tex_eq_wrap)
            else:
                try:
                    if l == int(l):
                        s = str(int(l))
                    else:
                        s = str(l)
                except:
                    s = str(l).replace("nan", nan_as).replace("inf", inf_as)
                if tex_eq_wrap and s != nan_as:
                    s = "$%s$" % s
                array_list[i] = s

    return array_list


def get_split_idx_list(list_to_split, idx_to_be_split_list):
    def append_tex(s, append_string):
        is_tex = False
        if s[0] == "$" and s[-1] == "$":
            s = s[1:-1]
            is_tex = True
        if is_tex:
            return "$%s%s$" % (s, append_string)
        else:
            return "%s$%s$" % (s, append_string)

    n = len(list_to_split)
    idx_list = range(n)
    assert isinstance(idx_to_be_split_list, list)
    if idx_to_be_split_list:
        assert set(idx_to_be_split_list).issubset(set(idx_list))
    split_idx_list = []
    for idx, item in enumerate(list_to_split):
        if idx in idx_to_be_split_list:
            split_idx_list.append(append_tex(list_to_split[idx], "'"))
            split_idx_list.append(append_tex(list_to_split[idx], "''"))
        else:
            split_idx_list.append(list_to_split[idx])
    return split_idx_list

class transport_table_element(object):
    def __init__(self, n_sup, n_dem, tex_table_type="table", enable_split=False, **kwargs):
        assert tex_table_type in ["table", "keytable"]
        self.tex_table_type = tex_table_type
        self.sup_desc=kwargs.get(
            "sup_desc", DEFAULT_TRANSPORT_STRING_DICT["SUPPLY_DESC"])
        self.dem_desc=kwargs.get(
            "dem_desc", DEFAULT_TRANSPORT_STRING_DICT["DEMAND_DESC"])
        self.dem_amount_desc=kwargs.get(
            "dem_amount_desc", DEFAULT_TRANSPORT_STRING_DICT["DEMAND_AMOUNT_DESC"])
        self.sup_amount_desc=kwargs.get(
            "sup_amount_desc", DEFAULT_TRANSPORT_STRING_DICT["SUPPLY_AMOUNT_DESC"])
        self.cost_desc = kwargs.get(
            "cost_desc", DEFAULT_TRANSPORT_STRING_DICT["COST_DESC"]
        )
        self.sup_min_desc=kwargs.get(
            "sup_min_desc", DEFAULT_TRANSPORT_STRING_DICT["MIN_SUPPLY"])
        self.sup_max_desc=kwargs.get(
            "sup_max_desc", DEFAULT_TRANSPORT_STRING_DICT["MAX_SUPPLY"])
        self.dem_min_desc=kwargs.get(
            "dem_min_desc", DEFAULT_TRANSPORT_STRING_DICT["MIN_DEMAND"])
        self.dem_max_desc=kwargs.get(
            "dem_max_desc", DEFAULT_TRANSPORT_STRING_DICT["MAX_DEMAND"])
        dem_split_idx_list = []
        sup_split_idx_list = []
        if enable_split:
            dem_split_idx_list = kwargs.get(
                "dem_split_idx_list", []
            )
            sup_split_idx_list = kwargs.get(
                "sup_split_idx_list", []
            )
        assert set(dem_split_idx_list).issubset(set(range(n_dem)))
        assert set(sup_split_idx_list).issubset(set(range(n_sup)))

        sup_name_list = kwargs.get("sup_name_list", None)
        dem_name_list = kwargs.get("dem_name_list", None)
        sup_name_prefix = kwargs.get("sup_name_prefix", None)
        dem_name_prefix = kwargs.get("dem_name_prefix", None)
        if sup_name_list:
            assert isinstance(sup_name_list, list)
            try:
                assert len(sup_name_list) == n_sup
            except:
                sup_name_list = None
        if not sup_name_list:
            if sup_name_prefix:
                sup_name_list = [
                    "%(prefix)s%(idx)s"
                    % {"prefix": sup_name_prefix,
                       "idx": idx + 1
                       }
                    for idx in range(n_sup)]
                assert len(sup_name_list) == n_sup
        if not sup_name_list:
            sup_name_list = [
                "$%(prefix)s_{%(idx)s}$"
                % {"prefix": DEFAULT_TRANSPORT_STRING_DICT["SUPPLY_PREFIX"],
                   "idx": idx + 1
                   }
                for idx in range(n_sup)]
        self.sup_name_list = get_split_idx_list(sup_name_list, sup_split_idx_list)

        if dem_name_list:
            assert isinstance(dem_name_list, list)
            self.dem_name_list = dem_name_list
            try:
                assert len(dem_name_list) == n_dem
            except:
                dem_name_list = None
        if not dem_name_list:
            if dem_name_prefix:
                dem_name_list = [
                    "%(prefix)s%(idx)s"
                    % {"prefix": dem_name_prefix,
                       "idx": idx + 1
                       }
                    for idx in range(n_dem)]
                assert len(dem_name_list) == n_dem
        if not dem_name_list:
            dem_name_list = [
                "$%(prefix)s_{%(idx)s}$"
                % {"prefix": DEFAULT_TRANSPORT_STRING_DICT["DEMAND_PREFIX"],
                   "idx": idx + 1
                   }
                for idx in range(n_dem)]
        self.dem_name_list = get_split_idx_list(dem_name_list, dem_split_idx_list)


def sum_recursive(l):
    assert isinstance(l, (list,tuple))
    result_list = []
    for i in l:
        if isinstance(i, (list,tuple)):
            result_list.append(sum_recursive(i))
        else:
            result_list.append(i)
    return sum(result_list)


def sum_min_max_recursive(l, exclude_idx=(), criteria_func=min):
    assert criteria_func in [min, max]
    assert isinstance(l, (list, tuple))
    assert isinstance(exclude_idx, (list, tuple))
    result_list = []
    for idx, i in enumerate(l):
        if isinstance(i, (list, tuple)):
            try:
                if idx not in exclude_idx:
                    result_list.append(criteria_func(i))
            except:
                result_list.append(sum_recursive(i))
        else:
            result_list.append(i)
    return sum(result_list)


# def sum_recursive(l):
#     assert isinstance(l, (list,tuple))
#     result_list = []
#     for i in l:
#         if isinstance(i, (list,tuple)):
#             result_list.append(sum_recursive(i))
#         else:
#             result_list.append(i)
#     return sum(result_list)


def validate_numeric_recursive(l):
    assert isinstance(l, (list,tuple))
    try:
        sum_recursive(l)
    except TypeError:
        return False
    return True


class transportation(object):
    def __init__(self, sup, dem, costs, sup_name_list=None, dem_name_list=None, sup_name_prefix=None,
                 dem_name_prefix=None, **kwargs):
        self.kwargs = kwargs

        assert isinstance(sup, list)
        if not validate_numeric_recursive(sup):
            raise ValueError(
                "Supply must be a list which contains only numbers"
            )
        assert isinstance(dem, list)
        if not validate_numeric_recursive(dem):
            raise ValueError(
                "Demand must be a list which contains only numbers"
            )
        assert isinstance(costs, (list, np.matrix, np.ndarray))
        if isinstance(costs, (list, np.matrix)):
            costs = np.array(costs)

        self.n_sup, self.n_dem = costs.shape
        assert len(sup) == self.n_sup
        assert len(dem) == self.n_dem
        self.n_sup = len(sup)
        for p in costs:
            assert len(dem) == len(p)
        self.n_dem = len(dem)

        self.sup = sup
        self.dem = dem
        self.costs = costs

        self.is_standard_problem = self.is_standard = False
        self.sup_lower_bound_idx = []
        self.sup_infty_upper_bound_idx = []
        self.dem_lower_bound_idx = []
        self.dem_infty_upper_bound_idx = []
        try:
            if sum(sup) == sum(dem):
                self.is_standard_problem = self.is_standard = True
        except TypeError:
            for idx, s in enumerate(sup):
                if isinstance(s, (list, tuple)):
                    if len(s) != 2:
                        raise ValueError("Supply may contain list/tuple with exactly 2 element")
                    else:
                        if s[0] == s[1]:
                            raise ValueError("Supply lower bound and upper bound must not be same")
                        self.sup_lower_bound_idx.append(idx)
                        self.sup[idx] = sorted(self.sup[idx])
                    if np.infty in s:
                        self.sup_infty_upper_bound_idx.append(idx)

            for idx, d in enumerate(dem):
                if isinstance(d, (list, tuple)):
                    if len(d) != 2:
                        raise ValueError("Demand may contain list/tuple with exactly 2 element")
                    else:
                        if d[0] == d[1]:
                            raise ValueError("Demand lower bound and upper bound must not be same")
                        self.dem_lower_bound_idx.append(idx)
                        self.dem[idx] = sorted(self.dem[idx])
                    if np.infty in d:
                        self.dem_infty_upper_bound_idx.append(idx)

        self.is_sup_bounded_problem = True if self.sup_lower_bound_idx else False
        self.is_dem_bounded_problem = True if self.dem_lower_bound_idx else False

        infty_count = len(self.dem_infty_upper_bound_idx) + len(self.sup_infty_upper_bound_idx)

        if infty_count > 1:
            raise ValueError(
                "Demand/supply with lower bound can only have 1 infinity upper bound")

        if self.dem_lower_bound_idx and self.sup_lower_bound_idx:
            raise ValueError(
                "Problem with lower/upper bound for both demand "
                "and supply is not solvable currently")

        self.infty_theoretical_value = 0
        self.is_infinity_bounded_problem = self.has_infty_upper_bound = True if infty_count else False

        self.sup_name_list = None
        if sup_name_list:
            assert isinstance(sup_name_list, list)
            self.sup_name_list = sup_name_list
            assert len(sup_name_list) == self.n_sup

        self.dem_name_list = None
        if dem_name_list:
            assert isinstance(dem_name_list, list)
            assert len(dem_name_list) == self.n_dem
            self.dem_name_list = dem_name_list

        self.sup_name_prefix = None
        if sup_name_prefix:
            assert isinstance(sup_name_prefix, (str, unicode))
            self.sup_name_prefix = sup_name_prefix

        self.dem_name_prefix = None
        if dem_name_prefix:
            assert isinstance(dem_name_prefix, (str, unicode))
            self.dem_name_prefix = dem_name_prefix

        self.sup_desc = self.kwargs.get(
            "sup_desc", DEFAULT_TRANSPORT_STRING_DICT["SUPPLY_DESC"])
        self.dem_desc = self.kwargs.get(
            "dem_desc", DEFAULT_TRANSPORT_STRING_DICT["DEMAND_DESC"])
        self.dem_amount_desc = self.kwargs.get(
            "dem_amount_desc", DEFAULT_TRANSPORT_STRING_DICT["DEMAND_AMOUNT_DESC"])
        self.sup_amount_desc = self.kwargs.get(
            "sup_amount_desc", DEFAULT_TRANSPORT_STRING_DICT["SUPPLY_AMOUNT_DESC"])
        self.cost_desc = self.kwargs.get(
            "cost_desc", DEFAULT_TRANSPORT_STRING_DICT["COST_DESC"])
        self.sup_min_desc=kwargs.get(
            "sup_min_desc", DEFAULT_TRANSPORT_STRING_DICT["MIN_SUPPLY"])
        self.sup_max_desc=kwargs.get(
            "sup_max_desc", DEFAULT_TRANSPORT_STRING_DICT["MAX_SUPPLY"])
        self.dem_min_desc=kwargs.get(
            "dem_min_desc", DEFAULT_TRANSPORT_STRING_DICT["MIN_DEMAND"])
        self.dem_max_desc=kwargs.get(
            "dem_max_desc", DEFAULT_TRANSPORT_STRING_DICT["MAX_DEMAND"])

        for kw in [self.sup_desc, self.dem_desc, self.dem_amount_desc, self.sup_amount_desc, self.cost_desc]:
            if kw:
                assert isinstance(kw, (str, unicode))

        self.standard_costs = None
        self.standard_sup = None
        self.standard_n_sup = 0
        self.standard_dem = None
        self.standard_n_dem = 0

        self.LCM_result = None
        self.NCM_result = None
        self.VOGEL_result = None

        self.sup_split_idx_list = []
        self.dem_split_idx_list = []

        self.sup_lower_bound_list_str = None
        self.sup_upper_bound_list_str = None
        self.dem_lower_bound_list_str = None
        self.dem_upper_bound_list_str = None
        if self.sup_lower_bound_idx:
            s_lb_list = []
            s_ub_list = []
            for i in range(self.n_sup):
                if not isinstance(self.sup[i], list):
                    s_lb_list.append(self.sup[i])
                    s_ub_list.append(self.sup[i])
                else:
                    s_lb_list.append(self.sup[i][0])
                    s_ub_list.append(self.sup[i][1])
            self.sup_lower_bound_list_str = get_array_to_str_list_recursive(s_lb_list)
            self.sup_upper_bound_list_str = get_array_to_str_list_recursive(s_ub_list, inf_as=u"无上限")
        if self.dem_lower_bound_idx:
            d_lb_list = []
            d_ub_list = []
            for i in range(self.n_dem):
                if not isinstance(self.dem[i], list):
                    d_lb_list.append(self.dem[i])
                    d_ub_list.append(self.dem[i])
                else:
                    d_lb_list.append(self.dem[i][0])
                    d_ub_list.append(self.dem[i][1])
            self.dem_lower_bound_list_str = get_array_to_str_list_recursive(d_lb_list)
            self.dem_upper_bound_list_str = get_array_to_str_list_recursive(d_ub_list, inf_as=u"无上限")

        self.question_no_need_consider_bound = True
        self.get_standardized()
        self.question_table_element = self.get_question_table_element()
        self.standard_table_element = self.get_standard_question_table_element()
        self.solve_table_element = self.get_standard_question_table_element(use_given_name=False)
        self.costs_str = get_array_to_str_list_recursive(self.costs)
        self.standard_costs_str = get_array_to_str_list_recursive(self.standard_costs)
        self.standard_costs_str_tikz = get_array_to_str_list_recursive(self.standard_costs, inf_as=r'"M"')
        assert sum(self.standard_sup) == sum(self.standard_dem)
        self.standard_total_amount = sum(self.standard_sup)


    def adjust_infty_upper_bound(self):
        # this is for 单个产地/销地上限为无穷大，且最低需求必须满足/最低产量必需运出的问题
        #def get_infty_upper_bound_value():

        if self.sup_infty_upper_bound_idx:
            total_dem = sum(self.dem)
            infty_theoretical_value = total_dem - sum_min_max_recursive(self.sup,
                                                                        exclude_idx=self.sup_infty_upper_bound_idx)
            if infty_theoretical_value < 0:
                raise ValueError(u"问题设置为最低产量大于总需求，无法求解")
            renewed_sup = sorted(self.sup[self.sup_infty_upper_bound_idx[0]])
            renewed_sup[1] = infty_theoretical_value
            self.sup[self.sup_infty_upper_bound_idx[0]] = renewed_sup
            self.sup_infty_upper_bound_idx = []
            self.has_infty_upper_bound = False
        
        if self.dem_infty_upper_bound_idx:
            total_sup = sum(self.sup)
            infty_theoretical_value = total_sup - sum_min_max_recursive(self.dem,
                                                                        exclude_idx=self.dem_infty_upper_bound_idx)
            if infty_theoretical_value < 0:
                raise ValueError(u"问题设置为最低需求大于总产量，无法求解")
            renewed_dem = sorted(self.dem[self.dem_infty_upper_bound_idx[0]])
            renewed_dem[1] = infty_theoretical_value
            self.dem[self.dem_infty_upper_bound_idx[0]] = renewed_dem
            self.dem_infty_upper_bound_idx = []
            self.has_infty_upper_bound = False
        self.infty_theoretical_value = infty_theoretical_value

    def get_bounded_standardized(self):
        # this is for 有上下限的产销不平衡问题
        if self.has_infty_upper_bound:
            self.adjust_infty_upper_bound()
        assert not self.has_infty_upper_bound
        assert self.sup_lower_bound_idx or self.dem_lower_bound_idx
        assert not (self.sup_lower_bound_idx and self.dem_lower_bound_idx)

        self.question_no_need_consider_bound = False
        self.standard_n_sup = self.n_sup
        self.standard_n_dem = self.n_dem

        # 以下为所有需求都能满足/所有产量都能运出的情况
        maximum_sup_amount = sum_min_max_recursive(self.sup, criteria_func=max)
        maximum_dem_amount = sum_min_max_recursive(self.dem, criteria_func=max)
        if maximum_dem_amount == maximum_sup_amount:
            self.is_standard = True

        if self.sup_lower_bound_idx:
            if maximum_dem_amount >= maximum_sup_amount:
                self.question_no_need_consider_bound = True
                for idx in self.sup_lower_bound_idx:
                    self.sup[idx] = max(self.sup[idx])
                validate_numeric_recursive(self.sup)
                self.sup_lower_bound_idx = []
        elif self.dem_lower_bound_idx:
            if maximum_dem_amount <= maximum_sup_amount:
                self.question_no_need_consider_bound = True
                for idx in self.dem_lower_bound_idx:
                    self.dem[idx] = max(self.dem[idx])
                validate_numeric_recursive(self.dem)
                self.dem_lower_bound_idx = []

        if self.question_no_need_consider_bound:
            self.get_standardized()
            return

        self.standard_dem = copy.deepcopy(self.dem)
        self.standard_sup = copy.deepcopy(self.sup)

        costs = np.copy (self.costs)
        costs_trasposed = False if self.sup_lower_bound_idx else True

        if costs_trasposed:
            costs = costs.transpose()

        if self.sup_lower_bound_idx:
            lower_bound_idx = self.sup_lower_bound_idx
            sup_or_dem = self.standard_sup
            sup_or_dem_other = self.standard_dem
            n_sup_or_dem = self.n_sup
            split_idx_list = self.sup_split_idx_list
            costs = np.append(costs, np.zeros([self.n_sup, 1]), axis=1)
            self.standard_n_dem +=1

        else:
            lower_bound_idx = self.dem_lower_bound_idx
            sup_or_dem = self.standard_dem
            sup_or_dem_other = self.standard_sup
            n_sup_or_dem = self.n_dem
            split_idx_list = self.dem_split_idx_list
            costs = np.append(costs, np.zeros([self.n_dem, 1]), axis=1)
            self.standard_n_sup += 1

        for i in reversed(range(n_sup_or_dem)):
            if i not in lower_bound_idx:
                costs[i, -1] = np.inf
            else:
                idx = lower_bound_idx.pop()
                l = sup_or_dem[idx]
                if l[0] == l[1]:
                    sup_or_dem[idx] = l[0]
                    costs[idx, -1] = np.inf
                else:
                    assert l[1] > l[0]
                    sup_or_dem[idx] = l[1]-l[0]
                    sup_or_dem.insert(idx, l[0])
                    split_idx_list.append(idx)
                    costs = np.insert(costs, idx, 0, axis=0)
                    costs[idx,:] = costs[idx+1, :]
                    costs[idx, -1] = np.inf
                    costs[idx+1, -1] = 0

        if costs_trasposed:
            costs = costs.transpose()
        self.standard_costs = costs
        sup_or_dem_other.append(sum(sup_or_dem) - sum(sup_or_dem_other))

    def get_standardized(self, dem=None, sup=None, sup_cost_extra=None, dem_cost_extra=None):
        # this is for 产销不平衡问题
        if self.dem_lower_bound_idx or self.sup_lower_bound_idx:
            #raise NotStandardizableError("Demand/supply has lower bound, not standardizable.")
            self.get_bounded_standardized()

        if self.standard_dem and self.standard_sup:
            return

        if self.is_standard:
            self.standard_costs = self.costs
            self.standard_n_dem = self.n_dem
            self.standard_n_sup = self.n_sup
            self.standard_dem = self.dem
            self.standard_sup = self.sup
            return

        if not dem:
            self.standard_dem = copy.deepcopy(self.dem)
        else:
            assert isinstance(dem, list)
            self.standard_dem = dem
        if not sup:
            self.standard_sup = copy.deepcopy(self.sup)
        else:
            assert isinstance(sup, list)
            self.standard_sup = sup

        if sum(self.sup) > sum(self.dem):
            self.standard_n_dem = self.n_dem + 1
            self.standard_n_sup = self.n_sup
            self.standard_dem.append(sum(self.sup) - sum(self.dem))
            new_column = np.zeros((self.n_sup, 1), dtype=np.int64)
            if dem_cost_extra:
                if not isinstance(dem_cost_extra, list):
                    raise ValueError("dem_cost_extra must be a list")
                if len(dem_cost_extra) != self.n_sup:
                    raise ValueError("The size of dem_cost_extra must be %d" % self.n_sup)
                new_column = np.array(dem_cost_extra)
                new_column.reshape(self.n_sup,1)
            self.standard_costs = np.append(self.costs, new_column, axis=1)

        elif sum(self.sup) < sum(self.dem):
            self.standard_n_sup = self.n_sup + 1
            self.standard_n_dem = self.n_dem
            self.standard_sup.append(sum(self.dem) - sum(self.sup))
            new_row = np.zeros(self.n_dem)
            if sup_cost_extra:
                if not isinstance(sup_cost_extra, list):
                    raise ValueError("sup_cost_extra must be a list")
                if len(sup_cost_extra) != self.n_dem:
                    raise ValueError("The size of sup_cost_extra must be %d" % self.n_dem)
                new_row = np.array(sup_cost_extra)
            self.standard_costs = np.vstack((self.costs, new_row))

    def get_question_table_element(self, tex_table_type="table", use_given_name=True, **kwargs):
        return self.get_table_element(n_sup=self.n_sup, n_dem=self.n_dem, enable_split=False,
                          tex_table_type=tex_table_type, use_given_name=use_given_name, **kwargs)

    def get_standard_question_table_element(self, tex_table_type="keytable", use_given_name=True, **kwargs):
        return self.get_table_element(n_sup=self.standard_n_sup, n_dem=self.standard_n_dem, enable_split=True,
                          tex_table_type=tex_table_type, use_given_name=use_given_name, **kwargs)

    def get_tranport_solve_table_element(self, tex_table_type="keytable", use_given_name=False, **kwargs):
        return self.get_table_element(n_sup=self.standard_n_sup, n_dem=self.standard_n_dem, enable_split=True,
                          tex_table_type=tex_table_type, use_given_name=use_given_name, **kwargs)

    def get_table_element(self, n_sup=None, n_dem=None, enable_split=False,
                          tex_table_type="table", use_given_name=True, **kwargs):
        if not n_sup:
            n_sup = self.n_sup
        if not n_dem:
            n_dem = self.n_dem
        if enable_split:
            kwargs["dem_split_idx_list"] = self.dem_split_idx_list
            kwargs["sup_split_idx_list"] = self.sup_split_idx_list

        if use_given_name:
            kwargs["sup_desc"] = self.sup_desc
            kwargs["dem_desc"] = self.dem_desc
            kwargs["dem_amount_desc"] = self.dem_amount_desc
            kwargs["sup_amount_desc"] = self.sup_amount_desc
            kwargs["cost_desc"] = self.cost_desc
            kwargs["sup_name_list"] = self.sup_name_list
            kwargs["dem_name_list"] = self.dem_name_list
            kwargs["sup_name_prefix"] = self.sup_name_prefix
            kwargs["dem_name_prefix"] = self.dem_name_prefix
            kwargs["sup_min_desc"] = self.sup_min_desc
            kwargs["sup_max_desc"] = self.sup_max_desc
            kwargs["dem_min_desc"] = self.dem_min_desc
            kwargs["dem_max_desc"] = self.dem_max_desc

        return transport_table_element(n_sup, n_dem, enable_split=enable_split, tex_table_type=tex_table_type, **kwargs)

    def solve(self, init_method="VOGEL", stringfy=True):
        return transport_solve(
            supply=self.standard_sup,
            demand=self.standard_dem,
            costs=self.standard_costs,
            init_method=init_method,
            stringfy=stringfy,
        )


def transport_solve(supply, demand, costs, init_method="LCM", stringfy=True):

    if not (supply and demand and costs is not None):
        return

    # Only solves balanced problem
    assert sum(supply) == sum(demand)
    assert init_method in ["LCM", "NCM", "VOGEL"]

    s = np.copy(supply)
    d = np.copy(demand)
    C = np.copy(costs)
    has_degenerated_init_solution = False
    has_degenerated_mid_solution = True
    has_unique_solution = True
    has_unique_verify_table = True
    vogel_list = []
    vogel_iter_loc_idx_list = []
    solution_list = []
    s_matrix_list = []

    n, m = C.shape

    # Finding initial solution
    X = np.full((n, m), np.nan)
    allow_fill_X = np.ones((n, m), dtype=bool)
    indices = [(i, j) for i in range(n) for j in range(m)]

    def _fill_zero_indice(i, j):
        allow_fill_X[i, j] = False
        allowed_indices_i = [
            (i, jj) for jj in range(m)
            if allow_fill_X[i, jj]]
        allowed_indices_j = [
            (ii, j) for ii in range(n)
            if allow_fill_X[ii, j]]
        allowed_indices = allowed_indices_i + allowed_indices_j
        if allowed_indices:
            return allowed_indices[0]
        else:
            return None

    if init_method == "VOGEL":
        # vogel
        n_iter = 0
        while n_iter < m + n - 1:
            row_diff = np.array([np.nan]*n)
            col_diff = np.array([np.nan]*m)
            for i in range(n):
                row_allowed = []
                for j in range(m):
                    if allow_fill_X[i, j]:
                        row_allowed.append(C[i, j])
                row_allowed_sorted = sorted(row_allowed)
                try:
                    row_diff[i] = abs(row_allowed_sorted[0] - row_allowed_sorted[1])
                except:
                    # only one element in row_allowed_sorted
                    row_diff[i] = np.nan
            for j in range(m):
                col_allowed = []
                for i in range(n):
                    if allow_fill_X[i, j]:
                        col_allowed.append(C[i, j])
                col_allowed_sorted = sorted(col_allowed)
                try:
                    col_diff[j] = abs(col_allowed_sorted[0] - col_allowed_sorted[1])
                except:
                    # only one element in row_allowed_sorted
                    col_diff[j] = np.nan

            vogel_list.append([row_diff.tolist(), col_diff.tolist()])

            try:
                diff = np.concatenate((row_diff, col_diff))
                max_diff_index = np.nanargmax(diff)
                max_diff = diff[max_diff_index]
            except:
                max_diff = None

            if max_diff:
                located = False
                located_index = None
                while not located:
                    for i in range(n):
                        if row_diff[i] == max_diff:
                            located = True
                            located_type = "row"
                            located_index = i
                            break
                    for j in range(m):
                        if col_diff[j] == max_diff:
                            located = True
                            located_type = "col"
                            located_index = j
                            break

                assert isinstance(located_index, int)
                assert located_type in ["row", "col"]

                if located_type == "row":
                    row_indices = [(located_index, j) for j in range(m) if allow_fill_X[located_index, j]]
                    row_values = [C[located_index,j] for j in range(m) if allow_fill_X[located_index, j]]
                    xs = sorted(zip(row_indices, row_values), key=lambda (a, b): b)
                    vogel_iter_loc_idx_list.append({"iter": n_iter, "location": "row", "idx":located_index})
                else:
                    col_indices = [(i, located_index) for i in range(n) if allow_fill_X[i, located_index]]
                    col_values = [C[i, located_index] for i in range(n) if allow_fill_X[i, located_index]]
                    xs = sorted(zip(col_indices, col_values), key=lambda (a, b): b)
                    vogel_iter_loc_idx_list.append({"iter": n_iter, "location": "col", "idx":located_index})

                (i, j), _ = xs[0]

            # there's the last cell needed to be filled.
            else:
                xs = [(i, j) for i in range(n) for j in range(m) if allow_fill_X[i, j]]
                (i, j) = xs[0]

            #(i, j), _ = xs[0]
            assert allow_fill_X[i, j]
            grabbed = min([s[i], d[j]])
            X[i, j] = grabbed

            # *both* supply i and demand j is met
            if s[i] == grabbed and d[j] == grabbed:
                fill_zero_indices = _fill_zero_indice(i, j)
                if fill_zero_indices:
                    # fill a 0 in X with allowed_indices
                    X[fill_zero_indices] = 0
                    allow_fill_X[fill_zero_indices] = False
                    n_iter += 1
                    has_degenerated_init_solution = True

            s[i] -= grabbed
            d[j] -= grabbed

            if d[j] == 0:
                allow_fill_X[:, j] = False
            if s[i] == 0:
                allow_fill_X[i, :] = False

            n_iter += 1

    else:

        if init_method == "LCM":
            # Least-Cost method
            xs = sorted(zip(indices, C.flatten()), key=lambda (a, b): b)
        elif init_method == "NCM":
            # Northwest Corner Method
            xs = sorted(zip(indices, C.flatten()), key=lambda (a, b): (a[0],a[1]))

        # Iterating C elements in increasing order
        for (i, j), _ in xs:
            grabbed = min([s[i],d[j]])

            # supply i or demand j has been met
            if grabbed == 0:
                continue

            # X[i,j] is has been filled
            elif not np.isnan(X[i,j]):
                continue
            else:
                X[i, j] = grabbed

                # *both* supply i and demand j is met
                if s[i] == grabbed and d[j] == grabbed:
                    fill_zero_indices = _fill_zero_indice(i, j)
                    if fill_zero_indices:
                        # fill a 0 in X with allowed_indices
                        X[fill_zero_indices] = 0
                        allow_fill_X[fill_zero_indices] = False
                        has_degenerated_init_solution = True

                s[i] -= grabbed
                d[j] -= grabbed

            if d[j] == 0:
                allow_fill_X[:,j] = False
            if s[i] == 0:
                allow_fill_X[i,:] = False

    solution_list.append(np.copy(X))

    # Finding optimal solution
    enter_element_list = []
    while True:
        u = np.array([np.nan]*n)
        v = np.array([np.nan]*m)
        S = np.full((n, m), np.nan)

        _x, _y = np.where(~np.isnan(X))
        basis = zip(_x, _y)
        f = basis[0][0]
        u[f] = 0

        # Finding u, v potentials
        while any(np.isnan(u)) or any(np.isnan(v)):
            for i, j in basis:
                if np.isnan(u[i]) and not np.isnan(v[j]):
                    if C[i, j] == np.inf:
                        u[i] = np.inf
                    else:
                        u[i] = C[i, j] - v[j]
                elif not np.isnan(u[i]) and np.isnan(v[j]):
                    if C[i, j] == np.inf:
                        v[j] = np.inf
                    else:
                        v[j] = C[i, j] - u[i]
                else:
                    continue

        # Finding S-matrix
        for i in range(n):
            for j in range(m):
                if np.isnan(X[i,j]):
                    if C[i, j] == np.inf:
                        S[i, j] = np.inf
                    elif u[i] == np.inf or v[j] == np.inf:
                        S[i, j] = -np.inf
                    else:
                        S[i, j] = C[i, j] - u[i] - v[j]

        s_matrix_list.append(S)

        # Stop condition
        s = np.nanmin(S)
        if s > 0:
            break
        elif s == 0:
            has_unique_solution = False
            break

        i, j = np.argwhere(S == s)[0]
        start = (i, j)
        enter_element_list.append(start)

        # Finding cycle elements
        T = np.zeros((n, m))

        # Element with non-nan value are set as 1
        for i in range(0,n):
            for j in range(0,m):
                if not np.isnan(X[i, j]):
                    T[i, j] = 1

        T[start] = 1
        while True:
            _xs, _ys = np.nonzero(T)
            xcount, ycount = Counter(_xs), Counter(_ys)

            for x, count in xcount.items():
                if count <= 1:
                    T[x,:] = 0
            for y, count in ycount.items():
                if count <= 1:
                    T[:,y] = 0

            if all(x > 1 for x in xcount.values()) \
                    and all(y > 1 for y in ycount.values()):
                break

        # Finding cycle chain order
        dist = lambda (x1, y1), (x2, y2): (abs(x1-x2) + abs(y1-y2)) \
            if ((x1==x2 or y1==y2) and not (x1==x2 and y1==y2)) else np.inf
        fringe = set(tuple(p) for p in np.argwhere(T > 0))

        size = len(fringe)

        path = [start]
        while len(path) < size:
            last = path[-1]
            if last in fringe:
                fringe.remove(last)
            next = min(fringe, key=lambda (x, y): dist(last, (x, y)))
            path.append(next)

        # Improving solution on cycle elements
        neg = path[1::2]
        pos = path[::2]
        q = min(X[zip(*neg)])
        if q == 0:
            has_degenerated_mid_solution = True
        X[start] = 0
        X[zip(*neg)] -= q
        X[zip(*pos)] += q

        # set the first element with value 0 as nan
        for ne in neg:
            if X[ne] == 0:
                X[ne] = np.nan
                break

        solution_list.append (np.copy (X))

    # for calculation of total cost
    X_final = np.copy(X)
    if np.nanmin(X_final) == 0:
        has_unique_verify_table = False

    for i in range(0, n):
        for j in range(0,m):
            if np.isnan(X_final[i, j]):
                X_final[i, j] = 0
            if C[i, j] == np.inf:
                C[i, j] = 1.0E10

    z = np.sum(X_final * C)
    if z == int(z):
        z = int(z)

    result_kwargs = {
        "routes": get_array_to_str_list_recursive(X, inf_as=r'"M"') if stringfy else X,
        "z": z,
        "solution_list": get_array_to_str_list_recursive(solution_list, inf_as=r'"M"') if stringfy else solution_list,
        "vogel_list": None if init_method !="VOGEL" else (get_array_to_str_list_recursive(vogel_list, inf_as=r'"M"') if stringfy else vogel_list),
        "vogel_location": None if init_method !="VOGEL" else vogel_iter_loc_idx_list,
        "s_matrix_list": get_array_to_str_list_recursive(s_matrix_list, tex_eq_wrap=True) if stringfy else s_matrix_list,
        "enter_element_list": enter_element_list,
        "has_degenerated_init_solution": has_degenerated_init_solution,
        "has_degenerated_mid_solution": has_degenerated_mid_solution,
        "has_unique_solution": has_unique_solution,
        "has_unique_verify_table": has_unique_verify_table
    }

    return OptimizeResult(**result_kwargs)


def is_ascii(text):
    if isinstance(text, unicode):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    else:
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    return True

# if __name__ == '__main__':
#     # supply = [105, 125, 70]
#     # demand = [80, [30,80], 70, 85]
#
#     supply = [[72,78], [115, np.infty], 100]
#     demand = [80, 65, 70, 85]
#
#     costs = np.array([[9., 10., 13., 17.],
#                       [7., 8., 14., 16.],
#                       [np.inf, 14., 8., 14.]])
#
#     # routes, z, solution_list, vogel_list, \
#     # s_matrix_list,\
#     # has_degenerated_init_solution, \
#     # has_degenerated_mid_solution, \
#     # has_unique_solution = transport(supply, demand, costs, init_method="VOGEL")
#     # print routes, z, has_degenerated_init_solution, has_degenerated_mid_solution, has_unique_solution
#     # print vogel_list
#     # print solution_list
#     # print s_matrix_list
#     # assert z == 3125
#     # assert has_degenerated_init_solution, has_degenerated_mid_solution
#     # assert not has_unique_solution
#
#     # t = transport_table_element(3, 4, sup_split_idx_list=[0,1], dem_split_idx_list=[0,1], enable_split=True, sup_name_list=[u"工厂1", u"工厂2", u"工厂3"])
#     # print t.sup_name_list, t.dem_name_list, t.cost_desc, t.sup_desc, t.cost_desc, t.sup_amount_desc
# #    print is_ascii(u"你好")
# #    print is_ascii("A_1")
#     #print sum_recursive([1,[1,2],6])
#
#     #print validate_numeric_recursive([1,2,(3,4), float("inf"), "a"])
#     t = transportation(sup=supply, dem=demand, costs=costs, dem_name_prefix=u"市场", sup_name_prefix=u"工厂", dem_desc=u"城市")
#     #t.get_standardized(sup_cost_extra=[1, 2, 3, 4])
# #    print t.standard_costs, t.standard_dem, t.standard_sup
# #    result = t.solve(init_method="VOGEL")
# #    print result
#     t_table = t.get_table_element(t.standard_n_sup, t.standard_n_dem, enable_split=True, use_given_name=True)
#     #t_table = t.get_table_element(t.n_sup, t.n_dem, enable_split=False, use_given_name=True)
#     print t.costs
#     print t_table.sup_name_list, t_table.dem_name_list, t_table.cost_desc, t_table.sup_desc, t_table.sup_amount_desc, t_table.dem_desc
#     for i in t_table.sup_name_list:
#         print i
#     for i in t_table.dem_name_list:
#         print i
#
#     result = t.solve(stringfy=False)
#     solution_list = result.solution_list
#     solution_list_str = get_array_to_str_list_recursive(solution_list)
#     #print solution_list_str
#     #print get_array_to_str_list_recursive(t.costs)
#     #print get_array_to_str_list_recursive(t.standard_costs)
# #    print result.routes
#     print t.standard_costs_str, t.sup
#     qtable = t.question_table_element
#     print qtable.sup_desc,qtable.dem_desc, qtable.cost_desc, qtable.dem_amount_desc
#     print qtable.sup_name_list, qtable.dem_min_desc, qtable.dem_name_list
#     print t.sup_lower_bound_list_str, t.sup_upper_bound_list_str,
#     #qtable.sup_name_list
#     print "t.standard_costs_str_tikz", t.standard_costs_str_tikz
#
#
#
#
#
#
#
# #    print t.has_infty_upper_bound, t.sup_infty_upper_bound_idx
# #    print t.sup, t.dem
#
#     # costs = np.array([[9., 10., 13., 17.],
#     #                   [7., 8., 14., 16.],
#     #                   [20., 14., 8., 14.]])
#     #
#     # costs2 = np.insert(costs, 1, 0, axis=0)
#     # print costs2
#
#
#
#
