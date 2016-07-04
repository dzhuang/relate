# -*- coding: utf-8 -*-

import copy
import six
import numpy as np

EQ = [">", "<", "=", ">=", "<=", "=<", "=>"]
SIGN = [">", "<", "=", ">=", "<=", "=<", "=>", "int", "bin"]

class LpSolution(object):
    def __init__(self):
        self.tableau_list = []
        self.basis_list = []
        self.pivot_list = []
        self.variable_list = []
        self.slack_variable_list = []
        self.artificial_variable_list = []
        self.need_two_phase = False
        self.qtype = ""

        self.varible_number = 0

        # self.n = 0
        self.m = 0
        self.original_goal_list = []
        self.goal_str_list = []
        self.xb_str_list = []
        self.cb_str_list = []
        self.tableau_str_list = []
        self.slack_str_list_intro = []
        self.neg_slack_str_list_intro = []
        self.artificial_str_list_intro = []
        self.all_variable_str_list = []

    def get_all_varaible(self):
        raise NotImplementedError()

    def get_goal_list(self):
        raise NotImplementedError()

    def get_solution_string(self):
        if not self.m:
            self.m = len(self.basis_list[0])

        tableau_list = self.tableau_list

        for t in tableau_list:
            if self.qtype == "max":
                t[-1, :-1] *= -1
            else:
                t[-1, -1] *= -1

        all_variable = self.get_all_varaible()

        self.all_variable_str_list = ["$x_{%d}$" % (abs(idx) + 1) for idx in all_variable]
        print self.all_variable_str_list

        goal_list = self.get_goal_list()

        self.goal_str_list = ["%s" % trans_latex_fraction(str(c)) for c in goal_list]
        print self.goal_str_list

        for basis in self.basis_list:
            self.xb_str_list.append(["$x_{%d}$" % (idx + 1) for idx in basis])
            cb_str_list_single = []
            for idx in basis:
                cb_str_list_single.append(self.goal_str_list[idx])
            self.cb_str_list.append(cb_str_list_single)

        print self.xb_str_list, self.cb_str_list


        for i, tableau in enumerate(tableau_list):
            t = tableau.tolist()
            for j, t_line in enumerate(t):
                t_line_filtered = [t_line[v] for v in all_variable]
                t_line_filtered.append(t_line[-1])
                t[j] = ["%s" % trans_latex_fraction(str(c)) for c in t_line_filtered]
            temp_list = t[0:self.m]
            temp_list.append(t[-1])
            self.tableau_str_list.append(temp_list)
        print self.tableau_str_list

    def get_variable_instro_str_list(self):
        for v in self.slack_variable_list:
            if v >= 0:
                self.slack_str_list_intro.append(get_variable_symbol("x", v+1))
            else:
                self.neg_slack_str_list_intro.append(get_variable_symbol("x", -v+1))
        for v in self.artificial_variable_list:
            self.artificial_str_list_intro.append("x", v+1)
    
    def get_constraint_str_list(self):
        pass


class LpSolutionPhase1(LpSolution):
    def get_all_varaible(self):
#        if self.need_two_phase:
        return self.variable_list + self.slack_variable_list + self.artificial_variable_list
    def get_goal_list(self):
        if self.need_two_phase:
            n_variable = len(self.get_all_varaible())
            goal_list = [0] * n_variable
            for idx in self.artificial_variable_list:
                goal_list[idx] = 1
            return goal_list
        else:
            return self.original_goal_list


class LpSolutionPhase2(LpSolution):
    def get_all_varaible(self):
        if self.need_two_phase:
            return self.variable_list + self.slack_variable_list
        else:
            return self.variable_list + self.slack_variable_list + self.artificial_variable_list

    def get_goal_list(self):
        n_variable = len(self.get_all_varaible())
        return self.original_goal_list[:n_variable]

class LP(object):
    def __init__(self, qtype, goal, constraints, x="x", x_list=None, sign=None, z="Z", sign_str=None, dual=False, required_solve_status=[0]):
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

        assert isinstance(goal,list)
        assert isinstance(constraints, (list,tuple))
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
                x_list[i] = get_variable_symbol(x_list[i], i+1)

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
        self.two_phase = False
        self.solve_n_variable = 0
        self.solve_n_variable = 0
        self.solve_x_list = []
        self.solve_goal_list =[]
        self.solve_goal_list = []
        self.solve_cb_list = []
        self.solve_cb_list = []
        self.solve_xb_list = []
        self.solve_xb_list = []
        self.tableau_origin = None
        
        self.solutionPhase1 = LpSolutionPhase1()
        self.solutionPhase2 = LpSolutionPhase2()

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
                    if variable_sign_trans(sign[i]) == variable_sign_trans(sign[i+1]):
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

        lhs = r"%s" % ("".join(constraint[:len(self.x_list)]), )
        eq = constraint[len(self.x_list)]
        rhs = constraint[-1]
        if rhs.startswith("-"):
            rhs = "\\mbox{$-$}%s" % rhs[1:]

        return r"&&%s&{}%s{}&%s\\" % (lhs, eq, rhs)

    def get_goal_str(self):
        goal = self.goal
        goal = [trans_latex_fraction(str(g), wrap=False) for g in goal]
        x_list = self.x_list
        # print x_list
        for i, g in reversed(list(enumerate(goal))):
            if str(g) == "0":
                goal.pop(i)
                x_list.pop(i)
            elif str(g) == "-1":
                goal[i] = "-"
            elif str(g) == "1":
                goal[i] = ""

        for i,g in enumerate(goal):
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
            x = x,
            z = z,
            dual=True
        )

    def solve(self, disp=True, method="two_phase"):
        constraints = [cnstr for cnstr in self.constraints_origin]
        goal = self.goal_origin
        C = []
        for g in goal:
            if self.qtype == "max":
                C.append(-float(g))
            else:
                C.append(float(g))

        b_ub=[]
        A_ub=[]
        b_eq=[]
        A_eq=[]
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

        #from scipy.optimize import linprog
        from linprog import linprog

        # linprog will make the constraints out of order
        def adjust_order(modified_list, cnstr_orig_order=cnstr_orig_order):
            m = len(cnstr_orig_order)
            t = copy.deepcopy(modified_list)
            for idx in range(m):
                t[cnstr_orig_order[idx]] = modified_list[idx]
            return t

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
            stage_klass.pivot_list.append([i_p, j_p])

            # used to generate latex formula of the model
            # if nit == 0:
            #     self.tableau_origin = t.tolist()
            #     if t[-1].max() != 0:
            #         self.two_phase = True

            # if self.two_phase:
            #     k = 2
            # else:
            #     k = 1
            #
            # if self.qtype == "max":
            #     t[-1, :-1] *= -1
            #     #t[-k, :-1] *= -1
            # else:
            #     t[-1, -1] *= -1
            #     t[-k, -1] *= -1
            # t = t.tolist()

#             if nit == 0:
#                 self.solve_goal_list = t[-k]
# #                print goal_list

            #print phase, t

            # for idx, e in enumerate(t):
            #     t[idx] = [trans_latex_fraction(v) for v in e]
            # try:
            #     t[int(i_p)][int(j_p)] = "[$\mathbf{%s}$]" % t[int(i_p)][int(j_p)].replace("$", "")
            # except ValueError:
            #     # completed, no pivot
            #     pass



            #stage_klass.tableau_list.append(t)
            # print basis
            #basis = basis.tolist()
            # basis = basis.tolist()
            # #print 'basis', basis
            # #cb = [self.solve_goal_list[v] for v in basis]
            # #cb_string = ["$%s$" % trans_latex_fraction(str(c), wrap=False) for c in cb]
            # x_idx = range(len(t[0][0]))
            # xb_list = ["$x_%s$" % str(x + 1) for x in basis]
            # #print xb_list
            # stage_klass.xb_list.append(xb_list)
#            print "stage_klass.xb_list", stage_klass.xb_list
            #print "stage1 xb_list", self.solutionPhase1.xb_list
            #print "stage1 tableau_list", self.solutionPhase1.tableau_list
            #print "stage2 xb_list", self.solutionPhase2.xb_list
            #print "stage2 tableau_list", self.solutionPhase2.tableau_list


            #xb_idx = [x_idx[v] for v in basis]
            #print xb
            #print cb

            # cb = copy.deepcopy(self.goal)
            # for i in basis:
            #     cb.append(0)
            # print (basis)
            # print (cb)


            # if phase == 2:
            #     #print "stage2", t
            #     self.tableau_list.append(t)
            #     #print basis
            #     #basis = basis.tolist()
            #     cb = copy.deepcopy(self.goal)
            #     for i in basis:
            #         cb.append(0)
            #     #print (basis)
            #     #print (cb)
            #
            #     cb_final = [cb[v] for v in basis]
            #     cb_final = ["$%s$" % trans_latex_fraction(str(c), wrap=False) for c in cb_final]
            #     self.solve_cb_list.append(cb_final)
            #     b_index = [temp +1 for temp in basis]
            #     xb = copy.deepcopy(self.x_list)
            #     for idx in range(len(self.x_list)+1, len(self.x_list) + len(b_index) + 1):
            #         xb.append("x_{%d}" % idx)
            #
            #     xb_final = [xb[v] for v in basis]
            #     xb_final = ["$%s$" % str(x) for x in xb_final]
            #     self.solve_xb_list.append(xb_final)
            #     self.base_list.append(b_index)
            #     #print self.base_list
            #     #print self.solve_xb_list

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
                      options = {'disp': disp},
                      callback= lin_callback,
                      **solve_kwarg
                      )
        #print "slack", res.slack

        # solve finished
        if res.status not in self.required_solve_status:
            raise RuntimeError("This problem can not be solved according to solve status")

        n_original_variable = len(self.x_list)
        m_constraint_number = len(cnstr_orig_order)

        self.solutionPhase1.variable_list \
            = self.solutionPhase2.variable_list \
            = range(n_original_variable)
        self.solutionPhase1.slack_variable_list \
            = self.solutionPhase2.slack_variable_list \
            = res.slack_list
        self.solutionPhase1.artificial_variable_list \
            = self.solutionPhase2.artificial_variable_list\
            = res.artificial_list
        origin_goal_list = self.solutionPhase1.tableau_list[0][m_constraint_number]
        if self.qtype == "max":
            origin_goal_list *= -1
        self.solutionPhase1.original_goal_list \
            = self.solutionPhase2.original_goal_list \
            = origin_goal_list



        if len(self.solutionPhase1.tableau_list) > 1:
            self.solutionPhase1.need_two_phase = self.solutionPhase2.need_two_phase = True

        # if self.solutionPhase2.need_two_phase:
        #     phase2_first_tableau = self.solutionPhase1.tableau_list[-1]
        #     phase2_first_basis = self.solutionPhase1.basis_list[-1]
        #     phase2_first_pivot = self.solutionPhase1.pivot_list[-1]
        #     self.solutionPhase2.tableau_list.insert(0,phase2_first_tableau)
        #     self.solutionPhase2.basis_list.insert(0, phase2_first_basis)
        #     self.solutionPhase2.pivot_list.insert(0, phase2_first_pivot)

        print "solutionPhase1", self.solutionPhase1.tableau_list, self.solutionPhase1.basis_list, self.solutionPhase1.pivot_list
        print "solutionPhase2", self.solutionPhase2.tableau_list, self.solutionPhase2.basis_list, self.solutionPhase2.pivot_list

        self.solutionPhase1.get_solution_string()
        self.solutionPhase2.get_solution_string()


        # n_slack = len(res.slack_list)
        # n_artificial = len(res.artificial_list)
        # self.solve_n_variable = len(self.x_list) + n_slack + n_artificial
        # self.solve_goal_list = self.goal + [0] * (n_slack + n_artificial)
        # self.solve_goal_list = self.solve_goal_list[:self.solve_n_variable]
        # self.solve_goal_list = ["$%s$" % trans_latex_fraction(c, wrap=False) for c in self.solve_goal_list]
        # self.solve_x_list = self.x_list
        #
        # for n in range(len(self.x_list)+1, len(self.x_list) + n_slack + n_artificial + 1):
        #     self.solve_x_list += ["x_{%d}" % (n,)]
        # self.solve_x_list = ["$%s$" % x for x in self.solve_x_list]

        return res.status

    def standized_LP(self):
        self.solve()
        tableau = copy.deepcopy(self.tableau_origin)
        #print tableau

        tableau.pop(-1)
        tableau.pop(-1)

        constraints = copy.deepcopy(tableau)
        for cnstr in constraints:
            cnstr.insert(-1, "=")

        #print constraints

        qtype = self.qtype
        goal = copy.deepcopy(self.goal)
        while len(goal) < (len(tableau[0]) -1):
            goal.append(0)

        #print goal

        return LP(
            qtype=qtype,
            goal=goal,
            constraints=constraints,
        )


def trans_latex_fraction(f, wrap=True):
    from fractions import Fraction
    try:
        frac = str(Fraction(f).limit_denominator())
    except:
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


def get_variable_symbol(x, i):
    """
    得到x_{i}的形式
    """
    return "%s_{%d}" % (x, i)