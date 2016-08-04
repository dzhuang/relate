# -*- coding: utf-8 -*-

import copy
import six
import numpy as np
import re
import sys
from sympy import symbols, Matrix, Poly, latex
from sympy.solvers.inequalities import reduce_rational_inequalities as ineq_solver, solve_rational_inequalities

tol = 1.0E-12
EQ = [">", "<", "=", ">=", "<=", "=<", "=>"]
SIGN = [">", "<", "=", ">=", "<=", "=<", "=>", "int", "bin"]
SA_TYPE = ["SA_c", "SA_p", "SA_b", "SA_A", "SA_x"]
SA_klass_dict = {"c": "sa_c", "p": "sa_p", "b": "sa_b", "A": "sa_A", "x": "sa_x"}
METHOD_NAME_DICT = {"simplex": u"单纯形法", "dual_simplex": u"对偶单纯形法"}
OPT_CRITERIA_LITERAL_DICT = {"max": u"非正", "min": u"非负"}



class SA_base(object):
    def get_method_name(self):
        return METHOD_NAME_DICT[self.opt_method]

    def get_opt_criteria_name(self):
        return OPT_CRITERIA_LITERAL_DICT[self.LP.qtype]

    def __init__(
            self, lp, param, n, x_list, init_tableau,
            opt_tableau, opt_basis, opt_method="simplex"):
        self.LP = lp
        self.param = param
        self.n = n
        self.init_tableau = init_tableau
        #self.goal = goal
        self.opt_tableau = opt_tableau
        self.opt_basis = opt_basis
        assert opt_method in ["simplex", "dual_simplex"]
        self.opt_method = opt_method
        self.opt_changed = False
        self.problem_description = ""
        self.x_list = x_list
        self.n_variable = init_tableau.shape[1] - 1

        C_np = self.init_tableau[-1, :-1]
        self.C = Matrix(C_np.tolist()).T
        self.CB = Matrix(C_np[self.opt_basis].tolist()).T
        A_np = self.init_tableau[:-1, :-1]
        self.A = Matrix(A_np.tolist())
        b_np = self.init_tableau[:-1, -1]
        self.b = Matrix(b_np.tolist())
        self.B = Matrix(A_np[:, self.opt_basis].tolist())
        self.B_1 = self.B.inv()
        self.C_j_BAR = self.C - self.CB * self.B_1 * self.A
        self.z = self.CB * self.B_1 * self.b
        self.non_basis_variable = list(set(range(self.n_variable)) - set(opt_basis))

        # 创建副本
        self.init_tableau_copy = None
        self.opt_tableau_copy = None
        self.opt_basis_copy = None
        self.C_copy = None
        self.CB_copy = None
        self.A_copy = None
        self.b_copy = None
        self.B_copy = None
        self.B_1_copy = None
        self.C_j_BAR_copy = None
        self.goal_copy = None
        self.z_copy = None
        self.problem_copy()


    def problem_copy(self):
        self.goal_copy = copy.deepcopy(self.LP.goal)
        self.init_tableau_copy = copy.deepcopy(self.init_tableau)
        self.opt_tableau_copy = copy.deepcopy(self.opt_tableau)
        self.opt_basis_copy = copy.deepcopy(self.opt_basis)
        self.C_copy = copy.deepcopy(self.C)
        self.CB_copy = copy.deepcopy(self.CB)
        self.A_copy = copy.deepcopy(self.A)
        self.b_copy = copy.deepcopy(self.b)
        self.B_copy = copy.deepcopy(self.B)
        self.B_1_copy = copy.deepcopy(self.B_1)
        self.C_j_BAR_copy = copy.deepcopy(self.C_j_BAR)
        self.z_copy = copy.deepcopy(self.z)

    def update_tableau(self, exclude=[]):
        if "C" not in exclude:
            C_np = self.init_tableau_copy[-1, :-1]
            self.C_copy = Matrix(C_np.tolist()).T
        if "CB" not in exclude:
            CB_copy = [self.C_copy[idx] for idx in self.opt_basis_copy]
            self.CB_copy = Matrix(CB_copy).T
        if "A" not in exclude:
            A_np = self.init_tableau_copy[:-1, :-1]
            self.A_copy = Matrix(A_np.tolist())
        if "b" not in exclude:
            b_np = self.init_tableau_copy[:-1, -1]
            self.b_copy = Matrix(b_np.tolist())
        if "B" not in exclude:
            self.B_copy = Matrix(A_np[:, self.opt_basis_copy].tolist())
            self.B_1_copy = self.B_copy.inv()
        if "C_j_BAR" not in exclude:
            self.C_j_BAR_copy = self.C_copy - self.CB_copy * self.B_1_copy * self.A_copy
        if "z" not in exclude:
            self.z_copy = self.CB_copy * self.B_1_copy * self.b_copy

    def solve_inequality(self, variable, ineq_list, ineq_sign):
        ineq_system = [[
                ((Poly(ineq),Poly(1, variable)), ineq_sign) for ineq in ineq_list]]
        range_str = latex(solve_rational_inequalities(ineq_system))
        return range_str

    def analysis(self):
        raise NotImplementedError

    def get_problem_description(self):
        raise NotImplementedError

class sa_result(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.items())])
        else:
            return self.__class__.__name__ + "()"

class sa_single_result(sa_result):
    pass


class sa_c(SA_base):
    def __init__(self, *args, **kwargs):
        super(sa_c, self).__init__(*args, **kwargs)
        c_index = None
        if isinstance(self.param[0], list):
            assert len(self.param[0]) == 1
            c_index = self.param[0][0]
        else:
            c_index = self.param[0]
        self.c_index = c_index
        self.c_in_opt_basis = False
        if c_index is not None:
            if c_index in self.opt_basis:
                self.c_in_opt_basis = True

    def get_problem_description(self):
        c_index = self.c_index
        desc = ""
        if c_index is not None:
            c_index_str = get_variable_symbol("c", c_index + 1)
            next_same_desc = False
            for i, v in enumerate(self.param[1:]):
                if v is None:
                    desc += u"$%s$在什么范围内变化时，最优解保持不变？" % c_index_str
                    next_same_desc = False
                else:
                    if next_same_desc:
                        desc += u"$%s=%s$时呢？" % (c_index_str, trans_latex_fraction(v, wrap=False))
                    else:
                        desc += u"$%s=%s$时最优解是什么？" % (c_index_str, trans_latex_fraction(v, wrap=False))
                    next_same_desc = True
        else:
            next_same_desc = False
            for i, v in enumerate(self.param[1:]):
                assert isinstance(v, list)
                #assert len(v) == self.n
                if next_same_desc:
                    desc += u"$\\mathbf{C}=(%s)$时呢？" % ", ".join(trans_latex_fraction(s, wrap=False) for s in v)
                else:
                    desc += u"当$\\mathbf{C}=(%s)$时，最优解是什么？" % ", ".join(trans_latex_fraction(s, wrap=False) for s in v)
                    next_same_desc = True


        #print desc
        return desc

    def analysis(self):
        c_index = self.c_index
        result = []
        desc = self.get_problem_description()
        print desc
        if self.LP.qtype == "max":
            c_ineq = "<="
        else:
            c_ineq = ">="
        if c_index is not None:
            for i, v in enumerate(self.param[1:]):
                new_lp = None
                result_i = sa_result()
                result.append(result_i)

                self.problem_copy()

                answer_description = ""

                if self.c_in_opt_basis:
                    non_basis_varaible = self.non_basis_variable

                    # nb_c_j_bar_np = np.array(self.C_j_BAR_copy.tolist())
                    # ma = np.ma.masked_where(nb_c_j_bar_np > tol, nb_c_j_bar_np, copy=False)
                    # print ma.count()


                    # report all c_j_bar
                    pass
                else:
                    # report c_j_bar of itself
                    pass

                if v is None:
                    # 求解指定变量的目标函数系数的范围
                    c_j = symbols("c_%s" % str(c_index+1), real=True)
                    self.C_copy[c_index] = c_j
                    self.update_tableau(exclude=["C"])

                    ineq_list = []
                    if not self.c_in_opt_basis:
                        ineq_list = [self.C_j_BAR_copy[c_index]]
                    else:
                        ineq_list = [self.C_j_BAR_copy[idx] for idx in self.non_basis_variable]

                    c_range_str = self.solve_inequality(c_j, ineq_list, c_ineq)
                    print c_range_str

                else:
                    # 当指定变量的目标函数系数取固定值时求最优解
                    self.init_tableau_copy[-1, c_index] = v
                    self.update_tableau()
                    nb_c_j_bar_np = np.array(self.C_j_BAR_copy.tolist())[0][self.non_basis_variable]
                    if self.LP.qtype == "max":
                        ma = np.ma.masked_where(nb_c_j_bar_np < tol, nb_c_j_bar_np, copy=False)
                    else:
                        ma = np.ma.masked_where(nb_c_j_bar_np > -tol, nb_c_j_bar_np, copy=False)
                    if ma.count() > 0:
                        change = True
                    else:
                        change = False

                    if change:
                        start_tableau = self.opt_tableau_copy
                        c_j_bar = np.array(self.C_j_BAR_copy.tolist())[0]
                        if self.LP.qtype == "max":
                            c_j_bar *= -1
                        start_tableau[-1, :-1] = c_j_bar
                        start_tableau[-1, -1] = self.z_copy[0]
                        goal = self.goal_copy
                        goal[c_index] = v
                        #print "goal", goal
                        #print start_tableau
                        new_lp = LP(qtype=self.LP.qtype, goal=goal,
                                    start_tableau=start_tableau, start_basis=self.opt_basis.tolist())
                        new_lp.solve(method="simplex")
                        #print new_lp.res



        else:
            self.problem_copy()
            for i, v in enumerate(self.param[1:]):
                self.init_tableau_copy[-1, :self.n] = v
                self.update_tableau()
                start_tableau = self.opt_tableau_copy
                c_j_bar = np.array(self.C_j_BAR_copy.tolist())[0]
                if self.LP.qtype == "max":
                    c_j_bar *= -1
                start_tableau[-1, :-1] = c_j_bar
                start_tableau[-1, -1] = self.z_copy[0]
                self.goal_copy = v
                goal = self.goal_copy
                new_lp = LP(qtype=self.LP.qtype, goal=goal,
                            start_tableau=start_tableau, start_basis=self.opt_basis.tolist())
                new_lp.solve(method="simplex")


        pass


class sa_p(SA_base):
    def __init__(self, *args, **kwargs):
        super(sa_p, self).__init__(*args, **kwargs)
        p_index = None
        if isinstance(self.param[0], list):
            assert len(self.param[0]) == 1
            p_index = self.param[0][0]
        else:
            p_index = self.param[0]
        self.p_index = p_index
        self.p_in_opt_basis = False
        if p_index is not None:
            if p_index in self.opt_basis:
                self.p_in_opt_basis = True

    def get_problem_description(self):
        p_index = self.p_index
        desc = ""

        p_index_str = get_variable_symbol(r"\mathbf{p}", p_index + 1)
        next_same_desc = False
        for i, v in enumerate(self.param[1:]):
            assert v is not None
            if next_same_desc:
                desc += u"$%s=(%s)^T$时呢？" % (p_index_str, ", ".join(trans_latex_fraction(s, wrap=False) for s in v))
            else:
                desc += u"$%s=(%s)^T$时最优解是什么？" % (p_index_str, ", ".join(trans_latex_fraction(s, wrap=False) for s in v))
                next_same_desc = True

        #print desc
        return desc

    def analysis(self):
        p_index = self.p_index
        result = []
        desc = self.get_problem_description()
        print desc
        if self.LP.qtype == "max":
            c_ineq = "<="
        else:
            c_ineq = ">="
        for i, v in enumerate(self.param[1:]):
            result_i = sa_result()
            result.append(result_i)

            self.problem_copy()
            p_j = symbols("p_%s" % str(p_index+1), real=True)
            self.init_tableau_copy[:-1, p_index] = np.array(v)
            self.update_tableau()

            if not self.p_in_opt_basis:

                # this should be reported
                c_j_bar = self.C_j_BAR_copy[p_index]
                if self.LP.qtype == "max":
                    if c_j_bar > tol:
                        change = True
                    else:
                        change = False
                else:
                    if c_j_bar < -tol:
                        change = True
                    else:
                        change = False

                print change

                if change:
                    start_tableau = self.opt_tableau_copy
                    A_bar = self.B_1 * self.A_copy
                    new_p = A_bar.col(p_index).T.tolist()
                    start_tableau[:-1, p_index] = np.array(new_p)
                    start_tableau[-1, p_index] = c_j_bar

                    if self.LP.qtype == "max":
                        start_tableau[-1, :-1] *= -1
                    goal = self.goal_copy
                    new_lp = LP(qtype=self.LP.qtype, goal=goal,
                                start_tableau=start_tableau, start_basis=self.opt_basis.tolist())
                    new_lp.solve(method="simplex")

            else:
                change = True
                print change
                if change:
                    origin_lp = copy.deepcopy(self.LP)
                    constraints = origin_lp.constraints_origin
                    for i, cnstr in enumerate(constraints):
                        constraints[i][p_index] = v[i]
                    new_lp = LP(qtype=origin_lp.qtype, goal=origin_lp.goal,
                                constraints=constraints, x=origin_lp.x,
                                x_list=origin_lp.x_list,
                                z=origin_lp.z
                                )
                    new_lp.solve(method="simplex")


class sa_b(SA_base):
    def __init__(self, *args, **kwargs):
        super(sa_b, self).__init__(*args, **kwargs)
        b_index = None
        if isinstance(self.param[0], list):
            assert len(self.param[0]) == 1
            b_index = self.param[0][0]
        else:
            b_index = self.param[0]
        self.b_index = b_index

    def get_problem_description(self):
        b_index = self.b_index
        desc = ""

        if b_index is not None:
            b_index_str = get_variable_symbol("b", b_index + 1)
            next_same_desc = False
            for i, v in enumerate(self.param[1:]):
                if v is None:
                    desc += u"$%s$在什么范围内变化时，最优基保持不变？" % b_index_str
                    next_same_desc = False
                else:
                    if next_same_desc:
                        desc += u"当$%s=%s$时呢？" % (b_index_str, trans_latex_fraction(v, wrap=False))
                    else:
                        desc += u"当$%s=%s$时最优解是什么？" % (b_index_str, trans_latex_fraction(v, wrap=False))
                    next_same_desc = True
        else:
            next_same_desc = False
            for i, v in enumerate(self.param[1:]):
                assert isinstance(v, list)
                #assert len(v) == self.n
                if next_same_desc:
                    desc += u"当$\\mathbf{b}=(%s)^T$时呢？" % ", ".join(trans_latex_fraction(s, wrap=False) for s in v)
                else:
                    desc += u"当$\\mathbf{b}=(%s)^T$时，最优解是什么？" % ", ".join(trans_latex_fraction(s, wrap=False) for s in v)
                    next_same_desc = True


        print desc
        return desc

    def analysis(self):
        b_index = self.b_index
        result = []
        desc = self.get_problem_description()
        b_ineq = ">="
        if b_index is not None:
            for i, v in enumerate(self.param[1:]):
                result_i = sa_result()
                result.append(result_i)

                self.problem_copy()
                if v is None:
                    b_i = symbols("b_%s" % str(b_index+1), real=True)
                    self.b_copy[b_index] = b_i
                    self.update_tableau(exclude=["b"])
                    b_bar = self.B_1 * self.b_copy
                    ineq_list = [b_bar[idx] for idx in range(len(self.b))]
                    b_range_str = self.solve_inequality(b_i, ineq_list, b_ineq)
                    #print b_range_str

                else:
                    self.b_copy[b_index] = v
                    self.update_tableau(exclude="b")
                    b_bar_sympy = self.B_1 * self.b_copy
                    b_bar_np = np.array(b_bar_sympy.T.tolist()[0])
                    #print b_bar_np, self.z_copy
                    ma = np.ma.masked_where(b_bar_np > tol, b_bar_np, copy=False)
                    if ma.count() > 0:
                        change = True
                    else:
                        change = False
                    #print change

                    if change:
                        start_tableau = self.opt_tableau_copy
                        # c_j_bar = np.array(self.C_j_BAR_copy.tolist())[0]
                        # if self.LP.qtype == "max":
                        #     c_j_bar *= -1
                        start_tableau[:-1, -1] = b_bar_np
                        if self.LP.qtype == "max":
                            start_tableau[-1, -1] = -self.z_copy[0]
                        else:
                            start_tableau[-1, -1] = self.z_copy[0]

                        new_lp = LP(qtype=self.LP.qtype, goal=self.goal_copy,
                                    start_tableau=start_tableau, start_basis=self.opt_basis.tolist())
                        new_lp.solve(method="dual_simplex")
        #
        else:
            for i, v in enumerate(self.param[1:]):
                self.problem_copy()
                self.b_copy = Matrix(v)
                self.update_tableau(exclude="b")
                b_bar_sympy = self.B_1 * self.b_copy
                b_bar_np = np.array(b_bar_sympy.T.tolist()[0])
                start_tableau = self.opt_tableau_copy
                # c_j_bar = np.array(self.C_j_BAR_copy.tolist())[0]
                # if self.LP.qtype == "max":
                #     c_j_bar *= -1
                start_tableau[:-1, -1] = b_bar_np
                if self.LP.qtype == "max":
                    start_tableau[-1, -1] = -self.z_copy[0]
                else:
                    start_tableau[-1, -1] = self.z_copy[0]
                goal = self.goal_copy
                new_lp = LP(qtype=self.LP.qtype, goal=goal,
                            start_tableau=start_tableau, start_basis=self.opt_basis.tolist())
                new_lp.solve(method="dual_simplex")
        # pass


class sa_A(SA_base):
    def get_problem_description(self):
        param = copy.deepcopy(self.param)
        desc = ""
        next_same_desc = False
        for i, v in enumerate(param):
            if i > 0:
                next_same_desc = True
            v[-2] = sign_trans(v[-2])
            new_constraint = get_single_constraint(v, self.x_list, use_seperator=False)
            if next_same_desc:
                desc += u"当添加的约束条件为$%s$时呢？" % new_constraint.strip()
            else:
                desc += u"若向原始问题中添加一个新的约束条件$%s$，求解出新的最优解。" % new_constraint.strip()

        #print desc
        return desc


    def analysis(self):
        result = []
        desc = self.get_problem_description()
        for i, v in enumerate(self.param):
            result_i = sa_result()
            result.append(result_i)

            n_variable = self.n_variable

            original_solution_sympy = Matrix(self.LP.res.x.tolist())
            new_cnstr_eq = Matrix(v[:self.n]).T
            new_cnstr_rhs = v[-1]
            new_cnstr_sign = v[-2]

            # this need to be reported.
            new_cnstr_lhs_sympy = new_cnstr_eq * original_solution_sympy
            new_cnstr_lhs = new_cnstr_lhs_sympy[0]

            if new_cnstr_sign in [">", ">="]:
                if new_cnstr_lhs >= new_cnstr_rhs:
                    change = False
                else:
                    change = True
                raise ValueError("New constraint with '>=' is currently not supported.")
            elif new_cnstr_sign in ["<", "<="]:
                if new_cnstr_lhs <= new_cnstr_rhs:
                    change = False
                else:
                    change = True
            else:
                raise ValueError ("New constraint with '=' is currently not supported.")

            #print change

            if change:
                self.problem_copy()
                new_T = np.zeros([self.init_tableau.shape[0]+1, self.init_tableau.shape[1]+1])
                new_T[:-2, :-2] = self.opt_tableau_copy[:-1, :-1]
                new_T[-1, :-2] = self.opt_tableau_copy[-1, :-1]
                new_T[:-2, -1] = self.opt_tableau_copy[:-1, -1]
                new_T[-2, :self.n] = np.array(v[:self.n])
                new_T[-2, -2] = 1
                new_T[-2, -1] = v[-1]
                if self.LP.qtype == "max":
                    new_T[-1, -1] = -self.z[0]
                else:
                    new_T[-1, -1] = self.z[0]
                for i, basis in enumerate(self.opt_basis_copy):
                    new_T[-2] -= new_T[-2, basis] * new_T[i]

                opt_basis = np.copy(self.opt_basis)
                from numpy import append
                new_variable_index = self.init_tableau.shape[1]-1
                opt_basis = append(opt_basis, new_variable_index)

                new_lp = LP(qtype=self.LP.qtype, goal=self.goal_copy,
                            start_tableau=new_T,
                            start_basis=opt_basis.tolist())
                new_lp.solve(method="dual_simplex")


class sa_x(SA_base):
    def __init__(self, *args, **kwargs):
        super(sa_x, self).__init__(*args, **kwargs)
        self.new_variable_index = self.opt_tableau.shape[1] - 1


    def get_problem_description(self):
        desc = ""
        next_same_desc = False
        opt_tableau = copy.deepcopy(self.opt_tableau)
        new_variable_index = self.new_variable_index
        new_variable_str = get_variable_symbol("x", new_variable_index+1)

        for i, v in enumerate(self.param):
            if i > 0:
                next_same_desc = True
            new_c = trans_latex_fraction(v["c"], wrap=False)
            new_p_list = [trans_latex_fraction(p_j, wrap=False) for p_j in v["p"]]
            if next_same_desc:
                desc += (
                    u"若$c_{%s}=%s,\, \mathbf{p}_{%s}=(%s)^T$，"
                    u"结果又是怎样？"
                    % (new_variable_index+1, new_c, new_variable_index+1, ", ".join(new_p_list))
                )
            else:
                desc += (
                    u"若向原始问题中添加一个新的变量$%s$, 且"
                    u"$c_{%s}=%s,\, \mathbf{p}_{%s}=(%s)^T$，"
                    u"最优解会有怎样的变化？"
                    % (new_variable_str, new_variable_index+1, new_c, new_variable_index+1, ", ".join(new_p_list)))

        #print desc
        return desc


    def analysis(self):
        result = []
        desc = self.get_problem_description()
        new_variable_index = self.new_variable_index

        for i, v in enumerate(self.param):
            new_lp = None
            new_c = v["c"]
            new_p_list = v["p"]
            new_p_sympy = Matrix(new_p_list)
            new_p_bar_sympy = self.B_1_copy * new_p_sympy
            new_p_bar_np = np.array(new_p_bar_sympy.T.tolist()[0])
            new_c_j_bar_sympy = Matrix([new_c]) - self.CB_copy * self.B_1_copy * new_p_sympy
            new_c_j_bar = new_c_j_bar_sympy[0]
            change = False
            if self.LP.qtype == "max":
                if new_c_j_bar >= 0:
                    change = True
            else:
                if new_c_j_bar <= 0:
                    change = True

            answer_description = ""

            answer_description += (
                u"当$c_{%(v_index)s}=%(new_c)s,\, \mathbf{p}_{%(v_index)s}=(%(new_p_list)s)^T$时，"
                % {"v_index": new_variable_index + 1,
                   "new_c": new_c,
                   "new_p_list": ", ".join([trans_latex_fraction(p_ele, wrap=False) for p_ele in new_p_list])}
            )

            answer_description += (
                u"先将$x_{%(v_index)s}$视为最优解中的非基变量，计算其检验数:"
                u"$$\\bar c_{%(v_index)s} =c_{%(v_index)s} - C_B B^{-1}\\mathbf{p}_{%(v_index)s} = %(new_c_j_bar)s$$"
                % {"v_index": new_variable_index + 1,
                   "new_c_j_bar": trans_latex_fraction(str(new_c_j_bar), wrap=False),
                   }
            )

            if not change:
                answer_description += (
                    u"由于$\\bar c_{%(v_index)s}$%(opt_criteria)s，原最优解不受影响.<br/><br/>"
                    % {"v_index": new_variable_index + 1,
                       "opt_criteria": self.get_opt_criteria_name()}
                )


            else:
                self.problem_copy()
                new_T = np.zeros([self.init_tableau.shape[0], self.init_tableau.shape[1]+1])
                new_T[:, :-2] = self.opt_tableau_copy[:, :-1]
                new_T[:, -1] = self.opt_tableau_copy[:, -1]
                new_T[:-1, -2] = new_p_bar_np
                new_T[-1, -2] = new_c_j_bar

                if self.LP.qtype == "max":
                    new_T[-1, :-1] *= -1

                goal_np = np.zeros([new_T.shape[1]-1])
                goal_np[:len(self.goal_copy)] = np.array(self.goal_copy)
                goal_np[-1] = new_c
                goal = goal_np.tolist()

                opt_basis = np.copy(self.opt_basis)
                new_lp = LP(qtype=self.LP.qtype, goal=goal,
                            start_tableau=new_T,
                            start_basis=opt_basis.tolist())
                new_lp.solve(method="simplex")

                answer_description += (
                    u"由于$\\bar c_{%(v_index)s}$不满足%(opt_criteria)s，需进一步求解。将$x_{%(v_index)s}$作为非基变量添加到最优表前，"
                    u"需计算$\\mathbf{\\bar p}_{%(v_index)s}$: "
                    u"$$\\mathbf{\\bar p}_{%(v_index)s} = B^{-1}\\mathbf{p}_{%(v_index)s} = (%(new_p_bar)s)^T$$"
                    u"将$c_{%(v_index)s}$, $\\bar c_{%(v_index)s}$和$\\mathbf{\\bar p}_{%(v_index)s}$作为一列"
                    u"加入最优表中，用%(method)s继续求解:"
                    % {"opt_criteria": self.get_opt_criteria_name(),
                       "v_index": new_variable_index + 1,
                       "new_p_bar": ", ".join([trans_latex_fraction(p_ele, wrap=False) for p_ele in new_p_bar_np]),
                       "method": self.get_method_name()
                       }
                )

            result_i = sa_single_result(answer_description=answer_description, change=change, new_lp=new_lp)
            result.append(result_i)
        full_result = sa_result(description=desc, answer=result)
        return full_result


class LP(object):
    def __init__(self, qtype="max", goal=None, constraints=None, x="x", x_list=None, sign=None, z="Z",
                 sign_str=None, dual=False,
                 sensitive={}, required_solve_status=[0, 0.1, 1, 2, 3],
                 start_tableau=None, start_basis=None
                 ):

        assert qtype.lower() in ["min", "max"]
        assert isinstance(required_solve_status, list)
        self.required_solve_status = required_solve_status
        self.qtype = qtype.lower()

        if start_tableau is not None or start_basis:
            if not (start_tableau is not None and start_basis is not None):
                raise ValueError(
                    "start_tableau and start_basis should both be "
                    "specified if one of them is specified")
            if not goal:
                raise ValueError(
                    "goal should both be specified if start_tableau "
                    "and start_basis are specified")
        if sensitive:
            assert isinstance(sensitive, dict)

            # 灵敏度分析，可以分析系数的取值变化后的结果，也可以分析系数在什么范围内变化时，最优解(基)不变（限于c和b）
            for k in sensitive:
                if k not in ["c", "p", "x", "A", "b"]:
                    raise ValueError("Unknown key '%s' for sensitivity analysis" % k)
                if not isinstance(sensitive[k], list):
                    raise ValueError("Sensitivity analysis with key '%s' should be an instance of list" % k)
                for item in sensitive[k]:
                    if k in ["c", "p", "b"]:
                        if not isinstance(item, (list, tuple)):
                            raise ValueError("Items in sensitivity analysis with key '%s' should be instances of list or tuple" % k)
                        if len(item) < 2:
                            raise ValueError(
                                "Items in sensitivity analysis with key '%s' should have at least 2 elements: %s" % (k, str(item)))
                        for item_j in item[1:]:
                            if item[1:].count(item_j) > 1:
                                raise ValueError(
                                    "There are duplicate elements in item in sensitivity analysis with key '%s': %s" % (
                                        k, str(item)))

                        # c, p, b的每个灵敏度分析，各参数的维数限制
                        value_range = 0
                        if k in ["c", "p"]:
                            value_range = range(len(goal))
                        elif k in ["b"]:
                            value_range = range(len(constraints))

                        if isinstance(item[0], list):
                            item1list = item[0]
                        else:
                            item1list = [item[0]]
                        for i in item1list:
                            if i is not None:
                                if int(i) not in value_range:
                                    raise ValueError(
                                        "The 1st element in item '%s' in sensitivity analysis with key '%s' "
                                        "should be within %s, while got %s" % (
                                            str(item), k, str(value_range), str(i)))

                        # p的灵敏度分析，不能分析取值范围
                        if k in ["p"]:
                            for item_j in item[1:]:
                                if item_j is None:
                                    raise ValueError(
                                        "The 2nd afterward elements in item in sensitivity analysis with key '%s' "
                                        "can't be None, while got %s" % (
                                            k, str(str(item))))
                                if not isinstance(item_j, list):
                                    raise ValueError(
                                        "The 2nd afterward element in item in sensitivity analysis with key '%s' "
                                        "must be a list, while got '%s'" % (
                                            k, str(str(item))))
                                if len(item_j) != len(constraints):
                                    raise ValueError(
                                        "The size of 2nd afterward element in item in sensitivity analysis with key '%s' "
                                        "must be %d, while got %d: %s" % (
                                            k, len(constraints), len(item_j), str(str(item))))


                        if k in ["c", "b"]:
                            # 如果item中第2个以后的元素为None，则前面只能是一个维数，item中的其它分析项也必须为一个数字
                            if None in item[1:]:
                                if isinstance(item[0], list):
                                    if len(item[0]) > 1:
                                        raise ValueError(
                                            "The 1st element in item in sensitivity analysis with key '%s' "
                                            "can't have more than 1 index when one of the 2nd afterward element is None, while got %s: %s" % (
                                                k, str(len(item[0])), str(item) ))
                                    if item_j is not None:
                                        if isinstance(item_j, list) and len(item_j) > 1:
                                            raise ValueError(
                                                "The length of 2nd afterward element in item in sensitivity analysis with key '%s' "
                                                "can't have more than 1 element when one of the 2nd afterward element is None, while got %s: %s" % (
                                                k, str(len(item_j)), str(item) ))


                            # 如果item中第1个元素为None，则后面必须提供全部系数
                            if item[0] is None:
                                # if len(item) > 2:
                                #     raise ValueError(
                                #         "The size of list in sensitivity analysis with key '%s' with 1st element as 'None' "
                                #         "must be 2, while got '%d': %s" % (
                                #             k, len(item), str(item)))
                                for item_j in item[1:]:
                                    if not isinstance(item_j, (list, tuple)):
                                        raise ValueError(
                                            "The 2nd afterward element in item in sensitivity analysis with key '%s' "
                                            "must be a list or tuple when the 1st element is None, while got '%s': %s" % (
                                                k, str(item_j), str(item)))
                                    if len(item_j) != len(value_range):
                                        raise ValueError(
                                            "The 1st element in item in sensitivity analysis with key '%s' "
                                            "must have the size of %d when the 2nd afterward element is None, while got %d: %s" % (
                                                k, len(value_range), len(item_j), str(item) ))

                    elif k in ["A"]:
                        # A 的灵敏度分析仅限于添加约束条件，添加变量的为'x'
                        if not isinstance(item, (list, tuple)):
                            raise ValueError("Items in sensitivity analysis with key '%s' should be instances of list of tuple" % k)
                        for item_j in item:
                            if len(item_j) != len(constraints[0]):
                                raise ValueError(
                                    "List in items in sensitivity analysis with key '%s' should be have exactly "
                                    "the length %d, while got %d: %s"
                                    % (k, len(constraints[0]), len(item_j), str(item_j)))
                            if not item_j[-2] in EQ:
                                raise ValueError(
                                    "The -2 element in list in items in sensitivity analysis with key '%s' "
                                    "should be within %s while got '%s': %s"
                                    % (k, ",".join(EQ), str(item_j[-2]), str(item_j)))

                    elif k in ["x"]:
                        # 添加新的变量
                        if not isinstance(item, (list, tuple)):
                            raise ValueError("Items in sensitivity analysis with key '%s' should be instances of list of tuple" % k)
                        for item_j in item:
                            if not isinstance(item_j, dict):
                                raise ValueError("Items in sensitivity analysis with key '%s' should be instances of dict: %s" % (k, str(item_j)))
                            for attr in item_j:
                                if attr not in ["c", "p"]:
                                    raise ValueError("Unkown items '%s' in sensitivity analysis with key '%s': '%s'" % (attr, k, str(item_j)))
                            for attr in ["c", "p"]:
                                if not attr in item_j:
                                    raise ValueError(
                                        "Dict in items in sensitivity analysis with key '%s' must "
                                        "contain key '%s': %s" % (k, attr, str(item_j)))
                            if not isinstance(item_j['p'], list):
                                raise ValueError(
                                    "The 2nd afterward element in item in sensitivity analysis with key '%s' "
                                    "must be a list, while got '%s'" % (
                                        k, str(str(item_j))))
                            if len(item_j['p']) != len(constraints):
                                raise ValueError(
                                    "The size of 2nd afterward element in item in sensitivity analysis with key '%s' "
                                    "must be %d, while got %d: %s" % (
                                        k, len(constraints), len(item_j['p']), str(str(item_j))))

        self.sensitive = sensitive

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
            "sensitive": sensitive,
        }
        self.json = json.dumps(json_dict)

        if goal:
            assert isinstance(goal, list)
        if constraints:
            assert isinstance(constraints, (list, tuple))
        if x:
            assert isinstance(x, six.string_types)
            assert len(x) == 1
        if z:
            assert isinstance(z, six.string_types)
            assert len(z) == 1

        self.goal_origin = copy.deepcopy(goal)
        self.constraints_origin = copy.deepcopy(constraints)
        self.goal = copy.deepcopy(goal)
        self.constraints = copy.deepcopy(constraints)

        if start_tableau is None and start_basis is None:
            n_variable = len(goal)
        else:
            n_variable = start_tableau.shape[1] - 1

        if x_list:
            assert isinstance(x_list, list)
            assert len(x_list) == n_variable
        else:
            x_list = [x] * n_variable
            for i, s in enumerate(x_list):
                x_list[i] = get_variable_symbol(x_list[i], i + 1)

        if start_tableau is None:
            for cstr in self.constraints:
                assert len(cstr) == n_variable + 2
                assert isinstance(cstr, list)
                assert cstr[-2] in EQ
                cstr[-2] = sign_trans(cstr[-2])

            if sign:
                assert isinstance(sign, list)
                for i, s in enumerate(sign):
                    assert s in SIGN
            else:
                sign = [">"] * n_variable
            assert len(sign) == n_variable

        self.x = x
        self.x_list = x_list
        self.z = z

        if not (start_tableau is not None and start_basis):
            self.sign = sign[:]
            if not sign_str:
                self.sign_str = self.get_sign_str(dual)
            else:
                self.sign_str = sign_str

            self.sign_str = r"\rlap{%s}" % self.sign_str
            self.constraints_str_list = self.get_constraint_str()

        self.base_list = []
        self.tableau_list = []
        self.res = []
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

        # 灵敏度分析
        self.sa_result = []

        # 灵敏度分析时的目标函数系数向量
        #self.start_goal_list = start_goal_list
        self.start_tableau = start_tableau
        self.start_basis = start_basis

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
        cstr_list = []
        for cnstr in self.constraints:
            cstr_list.append(get_single_constraint(cnstr, self.x_list))
        return cstr_list

    def get_goal_str(self):
        goal = self.goal
        try:
            goal = [trans_latex_fraction(str(g), wrap=False) for g in goal]
        except TypeError:
            return ""
        x_list = copy.deepcopy(self.x_list)

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

    def sensitive_analysis(self):
        sensitive = self.sensitive
        tableau_list = copy.deepcopy(self.solutionPhase2.tableau_list)
        opt_basis = copy.deepcopy(self.solutionPhase2.basis_list[-1])
        n = len(self.x_list)
        init_tableau = copy.deepcopy(tableau_list[0])
        opt_tableau = copy.deepcopy(tableau_list[-1])
        #goal_list = self.solutionCommon.original_goal_list

        for key in ["c", "b", "p", "x", "A"]:
            sa_klass = getattr(sys.modules[__name__], SA_klass_dict[key])
            if key in sensitive:
                #print sensitive[key]
                for ana in sensitive[key]:
                    analysis = sa_klass(
                        lp=self,
                        param=ana, n=n, x_list=self.x_list, init_tableau=init_tableau,
                        opt_tableau=opt_tableau, opt_basis=opt_basis)
                    self.sa_result.append(analysis.analysis())


    def solve(self, disp=False, method="simplex"):
        for solution in [self.solutionCommon, self.solutionPhase1, self.solutionPhase2]:
            solution.pivot_list = []
            solution.tableau_list = []
            solution.basis_list = []
            solution.variable_list = []
            solution.slack_variable_list = []
            solution.artificial_variable_list = []

        self.tableau_str_list = []
        b_ub = []
        A_ub = []
        b_eq = []
        A_eq = []
        C = []
        goal = self.goal_origin
        for g in goal:
            if self.qtype == "max":
                C.append(-float(g))
            else:
                C.append(float(g))
        cnstr_orig_order = []

        if not (self.start_tableau is not None and self.start_basis):
            constraints = [cnstr for cnstr in self.constraints_origin]

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
        else:
            cnstr_orig_order = range(len(self.start_basis))

        # from scipy.optimize import linprog
        from linprog import linprog

        def lin_callback(xk, **kwargs):
            t = np.copy(kwargs['tableau'])
            phase = np.copy(kwargs['phase'])
            nit = np.copy(kwargs['nit'])
            basis = np.copy(kwargs['basis'])
            i_p, j_p = np.copy(kwargs['pivot'])
            # if self.solutionCommon.method == "dual_simplex":
            #     print t
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
        solve_kwarg["start_tableau"] = self.start_tableau
        solve_kwarg["start_basis"] = self.start_basis

        res = linprog(bounds=((0, None),) * len(self.x_list),
                       options={'disp': disp},
                       callback=lin_callback,
                       method=method,
                       **solve_kwarg
                       )

        if res.status == 0:
            self.solutionCommon.nit = res.nit
            self.res = res

        #print res
        #print res.status


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

        existing_basic_variable_list = sorted([idx for idx in res.existing_basic_variable_list if idx is not None])
        self.solutionPhase1.existing_basic_variable_str_list \
            = self.solutionPhase2.existing_basic_variable_str_list \
            = self.solutionCommon.existing_basic_variable_str_list \
            = [get_variable_symbol(self.x, idx+1) for idx in existing_basic_variable_list]

        self.solutionPhase1.slack_variable_list \
            = self.solutionPhase2.slack_variable_list \
            = self.solutionCommon.slack_variable_list \
            = res.slack_list

        self.solutionPhase1.artificial_variable_list \
            = self.solutionPhase2.artificial_variable_list \
            = self.solutionCommon.artificial_variable_list \
            = res.artificial_list

        n_original_goal_list = n_original_variable + len(res.slack_list) + len(res.artificial_list)

        origin_goal_list = np.zeros(n_original_goal_list, dtype=np.float64)

        origin_goal_list[:len(C)] = C
        if self.qtype == "max":
            origin_goal_list *= -1

        opt_judge_literal = OPT_CRITERIA_LITERAL_DICT[self.qtype]

        self.solutionPhase1.original_goal_list \
            = self.solutionPhase2.original_goal_list \
            = self.solutionCommon.original_goal_list \
            = origin_goal_list.tolist()

        if len(self.solutionPhase1.tableau_list) > 1:
            self.solutionPhase1.need_two_phase \
                = self.solutionPhase2.need_two_phase \
                = self.solutionCommon.need_two_phase \
                = True

        if method == "simplex" and self.start_tableau is None:
            self.solutionPhase1.get_solution_string()

        self.solutionCommon.get_variable_instro_str_list()

        # final_tableau 用于判断是否有无穷多最优解
        final_tableau = None
        if self.has_phase_2:
            final_tableau = np.copy(self.solutionPhase2.tableau_list[-1])
            final_basis = np.copy(self.solutionPhase2.basis_list[-1])
            self.solutionPhase2.get_solution_string()

        if final_tableau is not None:
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
                        self.solve_status_reason += u"，且最优解中非基变量$%s$检验数为0" % ",".join(
                            [get_variable_symbol("x", idx + 1) for idx in list(non_basis_variable_0_cjbar_set)])
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


def get_single_constraint(constraint, x_list, use_seperator=True):
    constraint = [trans_latex_fraction(str(cnstr), wrap=False) for cnstr in constraint]
    x_list = [x for x in x_list]
    for i, cnstr in enumerate(constraint[:len(x_list)]):
        if str(cnstr) == "0":
            constraint[i] = ""
            x_list[i] = ""
        elif str(cnstr) == "-1":
            constraint[i] = "-"
        elif str(cnstr) == "1":
            constraint[i] = " "

    found_first_sign = False
    for i, cnstr in enumerate(constraint[:len(x_list)]):
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

    lhs = r"%s" % ("".join(constraint[:len(x_list)]),)
    eq = constraint[len(x_list)]
    rhs = constraint[-1]
    if rhs.startswith("-"):
        rhs = "\\mbox{$-$}%s" % rhs[1:]

    constraint_str = r"&&%s&{}%s{}&%s\\" % (lhs, eq, rhs)
    if not use_seperator:
        constraint_str = constraint_str.replace("&", "").replace("{}", " ").replace(r"\\", "")

    return constraint_str


def trans_latex_fraction(f, wrap=True):
    from fractions import Fraction
    if not isinstance(f, str):
        try:
            f = str(f)
        except:
            pass
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
        self.nit = 0

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
        M = symbols("M")
        artificial_list = self.artificial_variable_list
        tableau_list = self.tableau_list
        basis_list = self.basis_list

        for a in artificial_list:
            if self.qtype == "max":
                self.original_goal_list[a] = -M
            else:
                self.original_goal_list[a] = M

        C = Matrix(self.original_goal_list).T

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

