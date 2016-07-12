# -*- coding: utf-8 -*-

import copy
import six
import numpy as np
import re

EQ = [">", "<", "=", ">=", "<=", "=<", "=>"]
SIGN = [">", "<", "=", ">=", "<=", "=<", "=>", "int", "bin"]


class LpSolution(object):
    def __init__(self):
        # 未字符串化
        self.tableau_list = []
        self.basis_list = []
        self.pivot_list = []
        self.variable_list = []
        self.slack_variable_list = []
        self.artificial_variable_list = []
        self.original_goal_list = []
        self.need_two_phase = False
        self.qtype = ""
        self.method = ""

        # 已字符串化
        self.m = 0
        self.goal_str_list = []
        self.xb_str_list = []
        self.cb_str_list = []
        self.tableau_str_list = []
        self.slack_str_list_intro = []
        self.neg_slack_str_list_intro = []
        self.artificial_str_list_intro = []
        self.all_variable_str_list = []
        self.non_zero_artificial_in_opt = []

        # 用于改进单纯形法
        self.modi_CB_list = []
        self.modi_B_list = []
        self.modi_B_1_list = []
        self.modi_XB_list = []
        self.modi_CJBAR_list = []
        self.modi_CJBAR_idx_list = []
        self.modi_b_list = []
        self.modi_basis_list = []
        self.modi_bp_list = []
        self.modi_pj_list = []

    def get_all_variable(self):
        if not isinstance(self, LpSolutionCommon):
            raise NotImplementedError()

    def get_goal_list(self):
        if not isinstance(self, LpSolutionCommon):
            raise NotImplementedError()

    def transform_big_m(self):

        # 输出大M法单纯形表格
        from sympy import symbols, Matrix
        M = symbols("M")
        artificial_list = self.artificial_variable_list
        tableau_list = self.tableau_list
        basis_list = self.basis_list

        for a in artificial_list:
            if self.qtype == "max":
                self.original_goal_list[a] = -M
            else:
                self.original_goal_list[a] = M

        C = Matrix(self.original_goal_list[:-1]).T

        CB_list = []
        for bs in basis_list:
            CB_list_single = []
            for bsi in bs:
                CB_list_single.append(self.original_goal_list[bsi])
                CB_vector = Matrix([CB_list_single])
            CB_list.append(CB_vector)

        # 用于改进单纯形法
        self.modi_CB_list = CB_list

        A_np = tableau_list[0][:-1, :-1]
        A = Matrix(A_np.tolist())
        b_np = tableau_list[0][:-1, -1]
        b = Matrix(b_np.tolist())

        for i, t in enumerate(tableau_list):
            t = t.tolist()
            B_list_i = []
            for j, bs in enumerate(basis_list[i]):
                B_list_i.append(A_np[:, bs].tolist())
                B = Matrix(B_list_i).T
            CB = CB_list[i]
            B_1 = B.inv()
            C_j_BAR = C - CB*B_1*A
            Z = CB*B_1*b
            t[-1] = C_j_BAR.tolist()[0] + Z.tolist()[0]

            # 用于改进单纯形法
            self.tableau_list[i] = Matrix(t)
            self.modi_B_list.append(B_list_i)
            self.modi_B_1_list.append(B_1)
            self.modi_b_list.append(self.tableau_list[i][:-1, -1])
            self.modi_CJBAR_list.append(C_j_BAR.tolist())

    def transform_modified_simplex(self):
        self.modi_B_list =[]
        self.modi_B_1_list = []
        self.modi_b_list = []
        self.modi_CJBAR_list= []
        self.modi_pj_list = []

        self.transform_big_m()
        self.modi_basis_list = copy.deepcopy(self.basis_list)
        self.modi_bp_list  = copy.deepcopy(self.basis_list)
        self.modi_b_list = []
        for i in range(len(self.basis_list)):
            self.modi_basis_list[i] = [get_variable_symbol("x", j+1) for j in self.modi_basis_list[i]]
            self.modi_bp_list[i] = [get_variable_symbol("p", j+1) for j in self.modi_bp_list[i]]
            self.modi_B_list[i] = [list_to_matrix(self.modi_B_list[i])]
            self.modi_B_1_list[i] = [list_to_matrix(self.modi_B_1_list[i].tolist())]

            all_variable = self.get_all_variable()
            non_basis_index = []
            for idx in range(len(all_variable)):
                if idx not in self.basis_list[i]:
                    non_basis_index.append(idx)

            self.modi_CJBAR_idx_list.append(non_basis_index)
            self.modi_CJBAR_list[i] = [trans_latex_fraction (str (cjbar), wrap=False) for cjbar in
                                       self.modi_CJBAR_list[i][0]]
            self.modi_b_list.append(
                [trans_latex_fraction(str(bi[0]), wrap=False) for bi in self.tableau_list[i][:-1, -1].tolist()])
            try:
                p_j = self.tableau_list[i][:-1, self.pivot_list[i][1]]
            except IndexError:
                p_j = None
            if p_j:
                self.modi_pj_list.append([trans_latex_fraction(str(pj[0]), wrap=False) for pj in p_j.tolist()])

    def get_solution_string(self):
        if not self.m:
            self.m = len(self.basis_list[0])

        self.get_variable_instro_str_list()
        all_variable = self.get_all_variable()

        if isinstance(self, LpSolutionPhase2) and self.method == "big_m_simplex":
            self.transform_big_m()

        if isinstance(self, LpSolutionPhase2) and self.method == "modified_simplex":
            self.transform_modified_simplex()

        tableau_list = self.tableau_list

        if self.method not in ["big_m_simplex", "modified_simplex"]:
            for t in tableau_list:
                if self.qtype == "max":
                    t[-1, :-1] *= -1
                else:
                    t[-1, -1] *= -1

        self.all_variable_str_list = ["$x_{%d}$" % (abs(idx) + 1) for idx in all_variable]

        goal_list = self.get_goal_list()
        self.goal_str_list = ["%s" % trans_latex_fraction(str(c)) for c in goal_list]

        for basis in self.basis_list:
            self.xb_str_list.append(["$x_{%d}$" % (idx + 1) for idx in basis])
            cb_str_list_single = []
            for idx in basis:
                cb_str_list_single.append(self.goal_str_list[idx])
            self.cb_str_list.append(cb_str_list_single)

        self.tableau_str_list = [[],] * len(tableau_list)

        for i, tableau in enumerate(tableau_list):
            t = tableau.tolist()
            for j, t_line in enumerate(t):
                t_line_filtered = [t_line[v] for v in all_variable]
                t_line_filtered.append(t_line[-1])
                t[j] = ["%s" % trans_latex_fraction(str(c)) for c in t_line_filtered]
            temp_list = t[0:self.m]
            temp_list.append(t[-1])
            self.tableau_str_list[i] = temp_list
            try:
                t_i, t_j = self.pivot_list[i]
                t[int(t_i)][int(t_j)] = "[$\mathbf{%s}$]" % t[int(t_i)][int(t_j)].replace("$", "")
            except ValueError:
                # completed, no pivot
                pass

    def get_variable_instro_str_list(self):
        self.slack_str_list_intro = []
        self.neg_slack_str_list_intro = []
        self.artificial_str_list_intro = []
        for v in self.slack_variable_list:
            if v >= 0:
                self.slack_str_list_intro.append(get_variable_symbol("x", v + 1))
            else:
                self.neg_slack_str_list_intro.append(get_variable_symbol("x", -v + 1))
        for v in self.artificial_variable_list:
            self.artificial_str_list_intro.append(get_variable_symbol("x", v + 1))


class LpSolutionCommon(LpSolution):
    """
    用于表示独立于解法的部分
    """
    pass


class LpSolutionPhase1(LpSolution):
    def get_all_variable(self):
        return self.variable_list + [abs(v) for v in self.slack_variable_list] + self.artificial_variable_list

    def get_goal_list(self):
        if self.need_two_phase:
            n_variable = len(self.get_all_variable())
            goal_list = [0] * n_variable
            for idx in self.artificial_variable_list:
                goal_list[idx] = 1
            return goal_list
        else:
            return self.original_goal_list


class LpSolutionPhase2(LpSolution):
    def get_all_variable(self):
        if self.need_two_phase:
            return self.variable_list + [abs(v) for v in self.slack_variable_list]
        else:
            return self.variable_list + [abs(v) for v in self.slack_variable_list] + self.artificial_variable_list

    def get_goal_list(self):
        n_variable = len(self.get_all_variable())
        return self.original_goal_list[:n_variable]


class LP(object):
    def __init__(self, qtype, goal, constraints, x="x", x_list=None, sign=None, z="Z", sign_str=None, dual=False,
                 required_solve_status=[0, 0.1, 1, 2, 3]):
        assert qtype.lower() in ["min", "max"]
        assert isinstance(required_solve_status, list)
        self.required_solve_status = required_solve_status
        self.qtype = qtype.lower()
        import json
        json_dict = {
            "qtype": qtype,
            "constraints": constraints,
            "x": x,
            "x_list": x_list,
            "sign": sign,
            "z": z,
            "sign_str": sign_str,
            "dual": dual,
            "goal": goal,
        }
        self.json = json.dumps(json_dict)

        assert isinstance(goal, list)
        assert isinstance(constraints, (list, tuple))
        assert isinstance(x, six.string_types)
        assert len(x) == 1
        assert isinstance(z, six.string_types)
        assert len(z) == 1

        self.goal_origin = copy.deepcopy(goal)
        self.constraints_origin = copy.deepcopy(constraints)
        self.goal = copy.deepcopy(goal)
        self.constraints = copy.deepcopy(constraints)

        n_variable = len(goal)

        if x_list:
            assert isinstance(x_list, list)
            assert len(x_list) == n_variable
        else:
            x_list = [x] * n_variable
            for i, s in enumerate(x_list):
                x_list[i] = get_variable_symbol(x_list[i], i + 1)

        for m in self.constraints:
            assert len(m) == n_variable + 2
            assert isinstance(m, list)
            assert m[-2] in EQ
            m[-2] = sign_trans(m[-2])

        if sign:
            assert isinstance(sign, list)
            for i, s in enumerate(sign):
                assert s in SIGN
        else:
            sign = [">"] * n_variable
        assert len(sign) == n_variable

        self.x = x
        self.x_list = x_list
        self.sign = sign[:]
        self.z = z
        if not sign_str:
            self.sign_str = self.get_sign_str(dual)
        else:
            self.sign_str = sign_str

        self.sign_str = r"\rlap{%s}" % self.sign_str
        self.constraints_str_list = self.get_constraint_str()

        self.base_list = []
        self.tableau_list = []
        self.fun = []
        self.tableau_origin = None

        self.solutionCommon = LpSolutionCommon()
        self.solutionPhase1 = LpSolutionPhase1()
        self.has_phase_2 = True
        self.solutionPhase2 = LpSolutionPhase2()
        self.solve_status = 0
        self.solve_status_reason = ""
        self.solve_status_message = ""
        self.solve_opt_res_str = ""
        self.need_artificial_variable = False

        # 对偶问题的最优解（列表） 第1个为只看松弛变量的，第2个为所有变量
        self.dual_opt_solution_str_list = []


    def get_sign_str(self, dual):
        """
        得到变量的符号 x_{1},x_{3}\geqslant 0,\,x_{2}\text{无限制},\,x_{3}\text{为整数}
        """
        sign = self.sign
        x_list = self.x_list
        if not dual:
            sign_set = list(set(self.sign))
            sign_str = []
            for i, ss in enumerate(sign_set):
                temp = []
                for j, s in enumerate(sign):
                    if s == sign_set[i]:
                        temp.append(x_list[j])
                    elif variable_sign_trans(sign_set[i]) == "\geqslant 0" and s == "int":
                        temp.append(x_list[j])
                sign_str.insert(0, ",".join(temp) + variable_sign_trans(sign_set[i]))
            return ",\\,".join(sign_str)
        else:
            # 适用于写出对偶问题，不适用于整数规划！！！
            sign_str = []
            for i, s in enumerate(sign):
                try:
                    if variable_sign_trans(sign[i]) == variable_sign_trans(sign[i + 1]):
                        sign_str.append("%s" % x_list[i])
                    else:
                        sign_str.append("%s%s" % (x_list[i], variable_sign_trans(s)))
                except:
                    sign_str.append("%s%s" % (x_list[i], variable_sign_trans(s)))
            return ",\\,".join(sign_str)

    def get_constraint_str(self):
        c_list = []
        for cnstr in self.constraints:
            c_list.append(self.get_single_constraint(cnstr))
        return c_list

    def get_single_constraint(self, constraint):
        constraint = [trans_latex_fraction(str(cnstr), wrap=False) for cnstr in constraint]
        x_list = [x for x in self.x_list]
        for i, cnstr in enumerate(constraint[:len(self.x_list)]):
            if str(cnstr) == "0":
                constraint[i] = ""
                x_list[i] = ""
            elif str(cnstr) == "-1":
                constraint[i] = "-"
            elif str(cnstr) == "1":
                constraint[i] = " "

        found_first_sign = False
        for i, cnstr in enumerate(constraint[:len(self.x_list)]):
            if not found_first_sign:
                if str(cnstr) != "":
                    found_first_sign = True
                    if str(cnstr).startswith("-"):
                        constraint[i] = "\\mbox{$-$}%s" % str(cnstr)[1:]
                    elif str(cnstr).startswith("+"):
                        constraint[i] = " "
                    constraint[i] = "%s%s&" % (constraint[i], x_list[i])
                else:
                    constraint[i] = "{}{}&%s%s&" % (constraint[i][1:], x_list[i])
            else:
                if str(cnstr).startswith("-"):
                    constraint[i] = "{}-{}&%s%s&" % (constraint[i][1:], x_list[i])
                elif str(cnstr) == "":
                    constraint[i] = "{}{}&%s%s&" % (constraint[i][1:], x_list[i])
                else:
                    constraint[i] = "{}+{}&%s%s&" % (constraint[i], x_list[i])

        lhs = r"%s" % ("".join(constraint[:len(self.x_list)]),)
        eq = constraint[len(self.x_list)]
        rhs = constraint[-1]
        if rhs.startswith("-"):
            rhs = "\\mbox{$-$}%s" % rhs[1:]

        return r"&&%s&{}%s{}&%s\\" % (lhs, eq, rhs)

    def get_goal_str(self):
        goal = self.goal
        goal = [trans_latex_fraction(str(g), wrap=False) for g in goal]
        x_list = self.x_list

        for i, g in reversed(list(enumerate(goal))):
            if str(g) == "0":
                goal.pop(i)
                x_list.pop(i)
            elif str(g) == "-1":
                goal[i] = "-"
            elif str(g) == "1":
                goal[i] = ""

        for i, g in enumerate(goal):
            if i == 0:
                if str(g).startswith("-"):
                    goal[i] = "\\mbox{$-$}%s" % str(g)[1:]
                elif str(g).startswith("+"):
                    goal[i] = " "
                goal[i] = "%s%s" % (goal[i], x_list[0])
            else:
                goal[i] = "%s%s" % (goal[i], x_list[i])
                if not str(g).startswith("-"):
                    goal[i] = "+" + goal[i]

        return r"\%s \quad & \rlap{%s = %s}" % (self.qtype, self.z, "".join(goal))

    def dual_problem(self):
        qtype = list(set(["max", "min"]) - set([self.qtype]))[0]
        x = list(set(["x", "y"]) - set([self.x]))[0]
        z = list(set(["Z", "W"]) - set([self.z]))[0]
        p_constraints = copy.deepcopy(self.constraints_origin)
        rhs = copy.deepcopy(self.goal)
        constraints_sign = copy.deepcopy(self.sign)
        constraints = map(list, map(None, *p_constraints))

        goal = constraints.pop(-1)
        sign = constraints.pop(-1)

        if qtype == "min":
            # 最大值问题的约束条件与最小值问题变量的符号相反
            sign = [sign_reverse(s) for s in sign]
        else:
            constraints_sign = [sign_reverse(s) for s in constraints_sign]

        for i, cnstr in enumerate(constraints):
            constraints[i].append(constraints_sign[i])
            constraints[i].append(rhs[i])

        return LP(
            qtype=qtype,
            goal=goal,
            constraints=constraints,
            sign=sign,
            x=x,
            z=z,
            dual=True
        )

    def solve(self, disp=False, method="simplex"):
        for solution in [self.solutionCommon, self.solutionPhase1, self.solutionPhase2]:
            solution.pivot_list = []
            solution.tableau_list = []
            solution.basis_list = []
            solution.variable_list = []
            solution.slack_variable_list = []
            solution.artificial_variable_list = []

        self.tableau_str_list = []

        constraints = [cnstr for cnstr in self.constraints_origin]
        goal = self.goal_origin
        C = []
        for g in goal:
            if self.qtype == "max":
                C.append(-float(g))
            else:
                C.append(float(g))

        b_ub = []
        A_ub = []
        b_eq = []
        A_eq = []
        ub_cnstr_orig_order = []
        eq_cnstr_orig_order = []
        for i, cnstr in enumerate(constraints):
            i_list = []
            if sign_trans(cnstr[-2]) == sign_trans(">"):
                for cx in cnstr[:-2]:
                    try:
                        i_list.append(-float(cx))
                    except:
                        pass
                A_ub.append(i_list)
                b_ub.append(-float(cnstr[-1]))
                ub_cnstr_orig_order.append(i)
            elif sign_trans(cnstr[-2]) == sign_trans("<"):
                for cx in cnstr[:-2]:
                    try:
                        i_list.append(float(cx))
                    except:
                        pass
                A_ub.append(i_list)
                b_ub.append(float(cnstr[-1]))
                ub_cnstr_orig_order.append(i)
            elif sign_trans(cnstr[-2]) == sign_trans("="):
                for cx in cnstr[:-2]:
                    try:
                        i_list.append(float(cx))
                    except:
                        pass
                A_eq.append(i_list)
                b_eq.append(float(cnstr[-1]))
                eq_cnstr_orig_order.append(i)

        cnstr_orig_order = eq_cnstr_orig_order + ub_cnstr_orig_order

        # from scipy.optimize import linprog
        from linprog import linprog

        def lin_callback(xk, **kwargs):
            t = np.copy(kwargs['tableau'])
            phase = np.copy(kwargs['phase'])
            nit = np.copy(kwargs['nit'])
            basis = np.copy(kwargs['basis'])
            i_p, j_p = np.copy(kwargs['pivot'])

            if nit == 0:
                self.tableau_origin = t.tolist()

            if phase == 1:
                stage_klass = self.solutionPhase1
                stage_klass.qtype = "min"
            else:
                stage_klass = self.solutionPhase2
                stage_klass.qtype = self.qtype

            stage_klass.tableau_list.append(t)
            stage_klass.basis_list.append(basis)
            if not (np.isnan(i_p) and np.isnan(j_p)):
                stage_klass.pivot_list.append([i_p, j_p])
            else:
                stage_klass.pivot_list.append([np.nan, np.nan])
            stage_klass.method = self.solutionCommon.method = method

        solve_kwarg = {}
        solve_kwarg["c"] = C
        if A_ub:
            solve_kwarg["A_ub"] = A_ub
            solve_kwarg["b_ub"] = b_ub
        if A_eq:
            solve_kwarg["A_eq"] = A_eq
            solve_kwarg["b_eq"] = b_eq

        solve_kwarg["cnstr_orig_order"] = cnstr_orig_order

        res = linprog(bounds=((0, None),) * len(self.x_list),
                       options={'disp': disp},
                       callback=lin_callback,
                       method=method,
                       **solve_kwarg
                       )

#        print res

        if res.status == 2 and self.solutionCommon.method != "dual_simplex":
            # 原始问题不可行
            self.has_phase_2 = False

        if res.artificial_list:
            self.need_artificial_variable = True

        n_original_variable = len(self.x_list)
        m_constraint_number = len(cnstr_orig_order)

        self.solutionPhase1.variable_list \
            = self.solutionPhase2.variable_list \
            = self.solutionCommon.variable_list \
            = range(n_original_variable)

        self.solutionPhase1.slack_variable_list \
            = self.solutionPhase2.slack_variable_list \
            = self.solutionCommon.slack_variable_list \
            = res.slack_list

        self.solutionPhase1.artificial_variable_list \
            = self.solutionPhase2.artificial_variable_list \
            = self.solutionCommon.artificial_variable_list \
            = res.artificial_list

        origin_goal_list = []
        if method == "simplex":
            origin_goal_list = self.solutionPhase1.tableau_list[0][m_constraint_number]
        elif method in ["big_m_simplex", "modified_simplex"]:
            origin_goal_list = res.init_tablaeu[m_constraint_number]
        elif method == "dual_simplex":
            origin_goal_list = res.init_tablaeu[m_constraint_number]

        if self.qtype == "max":
            origin_goal_list *= -1
            opt_judge_literal = u"非正"
        else:
            opt_judge_literal = u"非负"


        self.solutionPhase1.original_goal_list \
            = self.solutionPhase2.original_goal_list \
            = self.solutionCommon.original_goal_list \
            = origin_goal_list.tolist()

        if len(self.solutionPhase1.tableau_list) > 1:
            self.solutionPhase1.need_two_phase \
                = self.solutionPhase2.need_two_phase \
                = self.solutionCommon.need_two_phase \
                = True

        if method == "simplex":
            self.solutionPhase1.get_solution_string()

        self.solutionCommon.get_variable_instro_str_list()

        # final_tableau 用于判断是否有无穷多最优解
        final_tableau = None
        if self.has_phase_2:
            final_tableau = np.copy(self.solutionPhase2.tableau_list[-1])
            final_basis = np.copy(self.solutionPhase2.basis_list[-1])
            self.solutionPhase2.get_solution_string()

        #self.dual_opt_solution_str
        final_cjbar = final_tableau[-1]
        dual_opt_solution_abstract = [abs(final_cjbar[idx]) for idx in self.solutionCommon.slack_variable_list]
        cjbar_origin_variable = [abs(final_cjbar[idx]) for idx in self.solutionCommon.variable_list]
        dual_opt_solution = dual_opt_solution_abstract + cjbar_origin_variable

        if not self.need_artificial_variable and res.status == 0:
            # 只有引入松弛变量的问题才计算对偶问题的最优解，否则不计算
            dual_opt_solution_abstract_str = [trans_latex_fraction(v, wrap=False) for v in dual_opt_solution_abstract]
            dual_opt_solution_str = [trans_latex_fraction(v, wrap=False) for v in dual_opt_solution]
            self.dual_opt_solution_str_list = [dual_opt_solution_abstract_str] + [dual_opt_solution_str]

        # status:
        #    0 : Optimization terminated successfully
        #    -1: Optimization terminated successfully, with multiple solutions
        #    1 : Iteration limit reached
        #    2 : Problem appears to be infeasible
        #    3 : Problem appears to be unbounded

        self.solve_status = res.status
        if res.status == 0:
            tol = 1.0E-12
            if final_tableau is not None:
                if self.solutionCommon.method in ["big_m_simplex", "modified_simplex"]:
                    for av in self.solutionCommon.artificial_variable_list:
                        if av in final_basis:
                            final_av_idx = np.where(final_basis==av)
                            if final_tableau[final_av_idx, -1] > tol:
                                self.solutionCommon.non_zero_artificial_in_opt.append(get_variable_symbol("x", av + 1))
                    if len(self.solutionCommon.non_zero_artificial_in_opt) > 0:
                        self.solve_status = 2
                        self.solve_status_reason = u"人工问题的最优解中存在非零的人工变量$%s$" % ",\,".join(
                            self.solutionCommon.non_zero_artificial_in_opt)
                        self.solve_status_message = u"无可行解"
                if self.solve_status == 0:
                    ma = np.ma.masked_where(
                        abs(final_tableau[-1, :-1]) <= tol, final_tableau[-1, :-1], copy=False)
                    variable_non_0_cjbar = np.ma.where(ma>tol)[0]
                    m, n_variable = np.shape(self.solutionPhase2.tableau_list[0][:-1, :-1])
                    non_basis_variable_set = set(range(n_variable)) - set(self.solutionPhase2.basis_list[-1])
                    non_basis_variable_0_cjbar_set = non_basis_variable_set - set(variable_non_0_cjbar.tolist())

                    self.solve_status_reason = u"所有非基变量的检验数%s" % opt_judge_literal
                    if len(non_basis_variable_0_cjbar_set) > 0:
                        self.solve_status_reason += u"，且最优解中非基变量$%s$" % \
                                                    [get_variable_symbol("x", idx + 1)
                                                     for idx in list(non_basis_variable_0_cjbar_set)]
                        self.solve_status = 0.1
                        self.solve_status_message = u"有无穷多最优解"
                        if self.solutionCommon.method == "modified_simplex":
                            self.solve_status_message += u"，其中一个最优解为"
                    else:
                        self.solve_status_message = u"有唯一最优解"

                    opt_x = []
                    opt_value = []
                    for idx in range(len(res.x)):
                        opt_x.append(get_variable_symbol(self.x, idx+1, superscript="*"))
                        opt_value.append(trans_latex_fraction(res.x[idx], wrap=False))
                    opt_x_str = r"(%s)^T" % ",\,".join(opt_x)
                    opt_value_str = r"(%s)^T" % ",\,".join(opt_value)
                    opt_solution = "%s = %s" % (opt_x_str, opt_value_str)
                    opt_fun_value = res.fun if self.qtype == "min" else res.fun *(-1)
                    if self.solutionCommon.method != "modified_simplex":
                        opt_fun = "%s^* = %s" % (self.z, trans_latex_fraction(opt_fun_value, wrap=False))
                        self.solve_opt_res_str = "$%s,\, %s$" % (opt_solution, opt_fun)
                    else:
                        opt_fun = r"%s^* = \mathbf{C_BB^{-1}b} = %s" % (self.z, trans_latex_fraction (opt_fun_value, wrap=False))
                        self.solve_opt_res_str = u"即$%s$，最优值为$$%s.$$" % (opt_solution, opt_fun)

        elif res.status == 1:
            self.solve_status_message = u"超过迭代次数仍未优化"
        elif res.status == 2:
            if self.solutionCommon.method == "simplex":
                self.solve_status_reason = u"辅助问题最优目标值不为0"
            elif self.solutionCommon.method == "dual_simplex":
                self.solve_status_reason = u"找不到入基变量"
            self.solve_status_message = u"无可行解"
        elif res.status == 3:
            self.solve_status_reason = u"找不到出基变量"
            self.solve_status_message = u"有无界解"

        if res.status not in self.required_solve_status:
            raise RuntimeError(
                "This problem can not be solved according to solve status")

        return res.status

    def standardized_LP(self):
        tableau = copy.deepcopy(self.tableau_origin)
        method = self.solutionCommon.method
        z = self.z
        qtype = self.qtype
        goal = None
        if method == "simplex":
            if self.solutionCommon.need_two_phase:
                tableau = tableau[:-2]
                z = [w for w in set(["W", "Z"]) - set([z])][0]
                goal = self.solutionPhase1.get_goal_list()
                qtype = "min"
            else:
                tableau = tableau[:-1]
                goal = self.solutionPhase2.get_goal_list ()

        elif method == "dual_simplex":
            tableau = tableau[:-1]
            goal = self.solutionPhase2.get_goal_list()

        elif method in ["big_m_simplex", "modified_simplex"]:
            tableau = tableau[:-1]
            goal_sym = self.solutionPhase2.get_goal_list()
            goal = [str(g) for g in goal_sym]

        constraints = copy.deepcopy(tableau)
        for cnstr in constraints:
            cnstr.insert(-1, "=")

        if goal:
            while len(goal) < (len(tableau[0]) - 1):
                goal.append(0)

            return LP(
                z = z,
                qtype=qtype,
                goal=goal,
                constraints=constraints,
            )
        else:
            return None


def trans_latex_fraction(f, wrap=True):
    from fractions import Fraction
    try:
        frac = str(Fraction(f).limit_denominator())
    except ValueError:
        if "M" in f:
            if f == "-M" and not wrap:
                frac = "-M"
            elif f == "M" and not wrap:
                frac = "M"
            else:
                try:
                    frac = trans_latex_big_m(f)
                except:
                    return f
        else:
            return f
    negative = False
    if frac.startswith("-"):
        negative = True
        frac = frac[1:]
    if "/" in frac:
        frac_list = frac.split("/")
        frac = r"\frac{%s}{%s}" % (frac_list[0], frac_list[1])
    if not wrap:
        if negative:
            frac = r"-" + frac
        return "%s" % frac
    else:
        if negative:
            frac = r"\mbox{$-$}" + frac
        return "$%s$" % frac


BIG_M_RE = re.compile("([-0-9.e]*)[\*]*M([ +-]*)([0-9.]*)")

def trans_latex_big_m(f):
    if f == "-M":
        return "\mbox{$-$}M"
    else:
        zeroM = False
        m = BIG_M_RE.match(f)
        if not m:
            return f
        exp_list = []
        for i, match in enumerate(m.groups()):
            if i == 0:
                s = trans_latex_fraction(match, wrap=False)
                if s == "1":
                    exp_list.append("M")
                elif s == "-1":
                    exp_list.append(r"\mbox{$-$}M")
                elif s == "0":
                    zeroM = True
                else:
                    exp_list.append("%sM" % s)
            if i == 1 and match:
                assert match.strip() in ['-', '+']
                exp_list.append(r"\mbox{$%s$}" % match.strip())
            if i == 2 and match:
                exp_list.append(trans_latex_fraction(match, wrap=False))

        big_m_str = "".join(exp_list)
        if not big_m_str:
            return "0"
        else:
            return big_m_str

def sign_trans(s):
    if ">" in s:
        return "\geqslant"
    elif "<" in s:
        return "\leqslant"
    elif s == "=":
        return "="
    else:
        raise ValueError()


def sign_reverse(s):
    if ">" in s:
        return "<"
    elif "<" in s:
        return ">"
    elif s == "=":
        return "="
    else:
        raise ValueError()


def variable_sign_trans(s):
    if ">" in s:
        return "\geqslant 0"
    elif "<" in s:
        return "\leqslant 0"
    elif s == "=":
        return u"\\text{无约束}"
    elif s == "bin":
        return u"=0\\text{或}1"
    elif s == "int":
        return u"\\text{为整数}"
    else:
        raise ValueError()


def get_variable_symbol(x, i, superscript=""):
    """
    得到x_{i}的形式
    """
    if superscript:
        return "%s_{%d}^{%s}" % (x, i, superscript)
    else:
        return "%s_{%d}" % (x, i)

def list_to_matrix(l, trans_latex=True):
    # l is a list of list
    for i in range(len(l)):
        if trans_latex:
            l[i] = " & ".join([trans_latex_fraction(str(li), wrap=False) for li in l[i]])
        else:
            l[i] = " & ".join(l[i])

    return r"\\".join(l)
