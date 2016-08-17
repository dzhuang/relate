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
    "COST_DESC": u"单位运费"
}

class NotStandardizableError(Exception):
    """for problem with lowerbound"""

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
        if sup_name_list:
            assert isinstance(sup_name_list, list)
            assert len(sup_name_list) == n_sup
        else:
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
            assert len(dem_name_list) == n_dem
        else:
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


def validate_numeric_recursive(l):
    assert isinstance(l, (list,tuple))
    try:
        sum_recursive(l)
    except TypeError:
        return False
    return True


class transportation(object):
    def __init__(self, sup, dem, costs, sup_name=None, dem_name=None,  **kwargs):
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

        self.is_standard = False
        self.sup_lower_bound_idx = []
        self.sup_infty_upper_bound_idx = []
        self.dem_lower_bound_idx = []
        self.dem_infty_upper_bound_idx = []
        try:
            if sum(sup) == sum(dem):
                self.is_standard = True
        except TypeError:
            for idx, s in enumerate(sup):
                if isinstance(s, (list, tuple)):
                    if len(s) != 2:
                        raise ValueError("Supply may contain list/tuple with exactly 2 element")
                    else:
                        self.sup_lower_bound_idx.append(idx)
                    if np.infty in s:
                        self.sup_infty_upper_bound_idx.append(idx)

            for idx, d in enumerate(dem):
                if isinstance(d, (list, tuple)):
                    if len(d) != 2:
                        raise ValueError("Demand may contain list/tuple with exactly 2 element")
                    else:
                        self.dem_lower_bound_idx = True
                    if np.infty in d:
                        self.dem_infty_upper_bound_idx.append(idx)

        infty_count = len(self.dem_infty_upper_bound_idx) + len(self.sup_infty_upper_bound_idx)

        if infty_count > 1:
            raise ValueError("Demand/supply with lower bound can only have 1 infinity upper bound")

        if self.dem_lower_bound_idx and self.sup_lower_bound_idx:
            raise ValueError("Problem with lower/upper bound for both demand and supply is not solvable currently")

        self.has_infty_upper_bound = True if infty_count else False

        if sup_name:
            assert isinstance(sup_name, list)
            self.sup_name = sup_name
            assert len(sup_name) == self.n_sup

        if dem_name:
            assert isinstance(dem_name, list)
            assert len(dem_name) == self.n_dem
            self.dem_name = dem_name

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

        try:
            self.get_standardized()
        except NotStandardizableError:
            if self.has_infty_upper_bound:
                self.adjust_infty_upper_bound()

    def adjust_infty_upper_bound(self):
        # this is for 最低需求必须满足/最低产量必需运出的问题
        #def get_infty_upper_bound_value():
        def sum_min_recursive(l, exclude_idx):
            assert isinstance (l, (list, tuple))
            result_list = []
            for idx, i in enumerate(l):
                if isinstance (i, (list, tuple)):
                    try:
                        if idx not in exclude_idx:
                            result_list.append(min(i))
                    except:
                        result_list.append(sum_recursive(i))
                else:
                    result_list.append (i)
            return sum(result_list)

        if self.sup_infty_upper_bound_idx:
            total_dem = sum(self.dem)
            infty_theoretical_value = total_dem - sum_min_recursive(self.sup, exclude_idx=self.sup_infty_upper_bound_idx)
            if infty_theoretical_value < 0:
                raise ValueError(u"问题设置为最低产量大于总需求，无法求解")
            print self.sup, self.sup_infty_upper_bound_idx
            renewed_sup = sorted(self.sup[self.sup_infty_upper_bound_idx[0]])
            renewed_sup[1] = infty_theoretical_value
            self.sup[self.sup_infty_upper_bound_idx[0]] = renewed_sup
            self.sup_infty_upper_bound_idx = []
            self.has_infty_upper_bound = False
        
        if self.dem_infty_upper_bound_idx:
            total_sup = sum(self.sup)
            infty_theoretical_value = total_sup - sum_min_recursive(self.dem, exclude_idx=self.dem_infty_upper_bound_idx)
            if infty_theoretical_value < 0:
                raise ValueError(u"问题设置为最低需求大于总产量，无法求解")
            renewed_dem = sorted(self.dem[self.dem_infty_upper_bound_idx[0]])
            renewed_dem[1] = infty_theoretical_value
            self.dem[self.dem_infty_upper_bound_idx[0]] = renewed_dem
            self.dem_infty_upper_bound_idx = []
            self.has_infty_upper_bound = False

    def get_standardized(self, sup_cost_extra=None, dem_cost_extra=None):
        # this is for 产销不平衡问题
        if self.dem_lower_bound_idx or self.sup_lower_bound_idx:
            raise NotStandardizableError("Demand/supply has lower bound, not standardizable.")
        if self.is_standard:
            self.standard_costs = self.costs
            self.standard_n_dem = self.n_dem
            self.standard_n_sup = self.n_sup
            self.standard_dem = self.dem
            self.standard_sup = self.sup
            return
        self.standard_dem = copy.deepcopy(self.dem)
        self.standard_sup = copy.deepcopy(self.sup)
        if sum(self.sup) > sum(self.dem):
            self.standard_n_dem = self.n_dem + 1
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

        else:
            self.standard_n_sup = self.n_sup + 1
            self.standard_sup.append(sum(self.dem) - sum(self.sup))
            new_row = np.zeros(self.n_dem)
            if sup_cost_extra:
                if not isinstance(sup_cost_extra, list):
                    raise ValueError("sup_cost_extra must be a list")
                if len(sup_cost_extra) != self.n_dem:
                    raise ValueError("The size of sup_cost_extra must be %d" % self.n_dem)
                new_row = np.array(sup_cost_extra)
            self.standard_costs = np.vstack((self.costs, new_row))


    def get_table_element(self, n_sup=None, n_dem=None, enable_split=False, tex_table_type="table", use_given_name=True, **kwargs):
        if not n_sup:
            n_sup = self.n_sup
        if not n_dem:
            n_dem = self.n_dem

        if use_given_name:
            kwargs["sup_desc"] = self.kwargs.get(
                "sup_desc", DEFAULT_TRANSPORT_STRING_DICT["SUPPLY_DESC"])
            kwargs["dem_desc"] = self.kwargs.get(
                "dem_desc", DEFAULT_TRANSPORT_STRING_DICT["DEMAND_DESC"])
            kwargs["dem_amount_desc"] = self.kwargs.get(
                "dem_amount_desc", DEFAULT_TRANSPORT_STRING_DICT["DEMAND_AMOUNT_DESC"])
            kwargs["sup_amount_desc"] = self.kwargs.get(
                "sup_amount_desc", DEFAULT_TRANSPORT_STRING_DICT["SUPPLY_AMOUNT_DESC"])
            kwargs["cost_desc"] = self.kwargs.get(
                "cost_desc", DEFAULT_TRANSPORT_STRING_DICT["COST_DESC"]
            )
            kwargs["sup_name_list"] = self.kwargs.get("sup_name_list", None)
            kwargs["dem_name_list"] = self.kwargs.get("dem_name_list", None)

        return transport_table_element(n_sup, n_dem, enable_split=enable_split, tex_table_type=tex_table_type, **kwargs)

    def solve(self, init_method="VOGEL"):
        return transport_solve(
            supply=self.standard_sup,
            demand=self.standard_dem,
            costs=self.standard_costs,
            init_method=init_method)



def transport_solve(supply, demand, costs, init_method="LCM"):

    if not (supply and demand and costs):
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
    vogel_list = []
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
                    xs = sorted(zip(row_indices, C[located_index,:].flatten()), key=lambda (a, b): b)
                else:
                    col_indices = [(i, located_index) for i in range(n) if allow_fill_X[i, located_index]]
                    xs = sorted(zip(col_indices, C[:, located_index].flatten()), key=lambda (a, b): b)

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
        #print S
        if s > 0:
            break
        elif s == 0:
            has_unique_solution = False
            break

        i, j = np.argwhere(S == s)[0]
        start = (i, j)

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
        dist = lambda (x1, y1), (x2, y2): abs(x1-x2) + abs(y1-y2)
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
    for i in range(0, n):
        for j in range(0,m):
            if np.isnan(X_final[i, j]):
                X_final[i, j] = 0
            if C[i, j] == np.inf:
                C[i, j] = 0


    return OptimizeResult(routes=X, z=np.sum(X_final*C), solution_list=solution_list,
                          vogel_list=vogel_list, s_matrix_list=s_matrix_list,
                          has_degenerated_init_solution=has_degenerated_init_solution,
                          has_degenerated_mid_solution=has_degenerated_mid_solution,
                          has_unique_solution=has_unique_solution)


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

if __name__ == '__main__':
    # supply = np.array([105, 125, 70])
    # demand = np.array([80, 65, 70, 85])

    supply = [105, 125, 70]
    demand = [80, 65, 70, 85]

    costs = np.array([[9., 10., 13., 17.],
                      [7., 8., 14., 16.],
                      [20., 14., 8., 14.]])

    # routes, z, solution_list, vogel_list, \
    # s_matrix_list,\
    # has_degenerated_init_solution, \
    # has_degenerated_mid_solution, \
    # has_unique_solution = transport(supply, demand, costs, init_method="VOGEL")
    # print routes, z, has_degenerated_init_solution, has_degenerated_mid_solution, has_unique_solution
    # print vogel_list
    # print solution_list
    # print s_matrix_list
    # assert z == 3125
    # assert has_degenerated_init_solution, has_degenerated_mid_solution
    # assert not has_unique_solution

    # t = transport_table_element(3, 4, sup_split_idx_list=[0,1], dem_split_idx_list=[0,1], enable_split=True, sup_name_list=[u"工厂1", u"工厂2", u"工厂3"])
    # print t.sup_name_list, t.dem_name_list, t.cost_desc, t.sup_desc, t.cost_desc, t.sup_amount_desc
#    print is_ascii(u"你好")
#    print is_ascii("A_1")
    #print sum_recursive([1,[1,2],6])

    #print validate_numeric_recursive([1,2,(3,4), float("inf"), "a"])
    t = transportation(sup=supply, dem=demand, costs=costs)
    #t.get_standardized(sup_cost_extra=[1, 2, 3, 4])
    print t.standard_costs, t.standard_dem, t.standard_sup
    result = t.solve(init_method="VOGEL")
    print result
    t_table = t.get_table_element(t.standard_n_sup, t.standard_n_dem)
    print t_table.sup_name_list, t_table.dem_name_list, t_table.cost_desc, t_table.sup_desc, t_table.cost_desc, t_table.sup_amount_desc
    print t.has_infty_upper_bound, t.sup_infty_upper_bound_idx
    print t.sup, t.dem


