# -*- coding: utf-8 -*-

import copy

EQ = [">", "<", "=", ">=", "<=", "=<", "=>"]
SIGN = [">", "<", "=", ">=", "<=", "=<", "=>", "int", "bin"]

class LP(object):
    @staticmethod
    def sign_trans(s):
        if ">" in s:
            return "\geqslant"
        elif "<" in s :
            return "\leqslant"
        elif s == "=":
            return "="
        else:
            raise ValueError()

    @staticmethod
    def variable_sign_trans(s):
        if ">" in s:
            return "\geqslant 0"
        elif "<" in s :
            return "\leqslant 0"
        elif s == "=":
            return u"\\text{无限制}"
        elif s == "bin":
            return u"=0\\text{或}1"
        elif s == "int":
            return u"\\text{为整数}"
        else:
            raise ValueError()

    @staticmethod
    def get_variable_symbol(x, i):
        """
        得到x_{i}的形式
        """
        return "%s_{%d}" % (x, i)

    def __init__(self, type, goal, constraints, x="x", x_list=None, sign=None, z="Z", sign_str=None):
        assert type.lower() in ["min", "max"]
        self.type = type.lower()

        assert isinstance(goal,list)
        assert isinstance(constraints, (list,tuple))
        assert isinstance(x, str)
        assert len(x) == 1
        assert isinstance(z, str)
        assert len(z) == 1



        self.goal_origin = copy.deepcopy(goal)
        self.constrains_origin = copy.deepcopy(constraints)
        self.goal = copy.deepcopy(goal)
        self.constraints = copy.deepcopy(constraints)

        n_variable = len(goal)

        if x_list:
            assert isinstance(x_list, list)
            assert len(x_list) == n_variable
        else:
            x_list = [x] * n_variable
            for i, s in enumerate(x_list):
                x_list[i] = self.get_variable_symbol(x_list[i], i+1)

        for m in self.constraints:
            assert len(m) == n_variable + 2
            assert isinstance(m, list)
            assert m[-2] in EQ
            m[-2] = self.sign_trans(m[-2])


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
            self.sign_str = self.get_sign_str()
        else:
            self.sign_str = sign_str

        self.sign_str = r"\rlap{%s}" % self.sign_str
        self.constraints_str_list = self.get_constraint_str()

        self.base_list = []
        self.tableau_list = []
        self.fun = []
        self.solve_n_variable = 0
        self.solve_x_list = []
        self.solve_goal_list =[]
        self.solve_cb_list = []
        self.solve_xb_list = []

    def get_sign_str(self):
        """
        得到变量的符号 x_{1},x_{3}\geqslant 0,\,x_{2}\text{无限制},\,x_{3}\text{为整数}
        """
        sign = self.sign
        x_list = self.x_list
        sign_set = list(set(self.sign))
        sign_str = []
        for i, ss in enumerate(sign_set):
            temp = []
            for j, s in enumerate(sign):
                if s == sign_set[i]:
                    temp.append(x_list[j])
                elif self.variable_sign_trans(sign_set[i]) == "\geqslant 0" and s == "int":
                    temp.append(x_list[j])
            sign_str.insert(0, ",".join(temp) + self.variable_sign_trans(sign_set[i]))
        return ",\\,".join(sign_str)

    def get_constraint_str(self):
        c_list = []
        for c in self.constraints:
            c_list.append(self.get_single_constraint(c))
        return c_list

    def get_single_constraint(self, constraint):
        constraint = [trans_latex_fraction(str(c), wrap=False) for c in constraint]
        x_list = [x for x in self.x_list]
        for i, c in enumerate(constraint[:len(self.x_list)]):
            if str(c) == "0":
                constraint[i] = ""
                x_list[i] = ""
            elif str(c) == "-1":
                constraint[i] = "-"
            elif str(c) == "1":
                constraint[i] = " "

        found_first_sign = False
        for i, c in enumerate(constraint[:len(self.x_list)]):
            if not found_first_sign:
                if str(c) != "":
                    found_first_sign = True
                    if str(c).startswith("-"):
                        constraint[i] = "\\mbox{$-$}%s" % str(c)[1:]
                    elif str(c).startswith("+"):
                        constraint[i] = " "
                    constraint[i] = "%s%s&" % (constraint[i], x_list[i])
                else:
                    constraint[i] = "{}{}&%s%s&" % (constraint[i][1:], x_list[i])
            else:
                if str(c).startswith("-"):
                    constraint[i] = "{}-{}&%s%s&" % (constraint[i][1:], x_list[i])
                elif str(c) == "":
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
        for i, g in enumerate(goal):
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

        return r"\%s \quad & \rlap{%s = %s}" % (self.type, self.z, "".join(goal))

    def solve(self):
        constraints = [c for c in self.constrains_origin]
        goal = self.goal_origin
        C = []
        for g in goal:
            if self.type == "max":
                C.append(-float(g))
            else:
                C.append(float(g))

        b_ub=[]
        A_ub=[]
        b_eq=[]
        A_eq=[]
        for c in constraints:
            i_list = []
            if self.sign_trans(c[-2]) == self.sign_trans(">"):
                for cx in c[:-2]:
                    try:
                        i_list.append(-float(cx))
                    except:
                        pass
                A_ub.append(i_list)
                b_ub.append(-float(c[-1]))
            elif self.sign_trans(c[-2]) == self.sign_trans("<"):
                for cx in c[:-2]:
                    try:
                        i_list.append(float(cx))
                    except:
                        pass
                A_ub.append(i_list)
                b_ub.append(float(c[-1]))
            elif self.sign_trans(c[-2]) == self.sign_trans("="):
                for cx in c[:-2]:
                    try:
                        i_list.append(float(cx))
                    except:
                        pass
                A_eq.append(i_list)
                b_eq.append(float(c[-1]))

        #print C, A_eq, b_eq, A_ub, b_ub

        from scipy.optimize import linprog

        def lin_callback(xk, **kwargs):
            tableau = kwargs.pop('tableau')
            t = copy.deepcopy(tableau)
            i_p, j_p = kwargs.pop('pivot')
            i_p = copy.deepcopy(i_p)
            j_p = copy.deepcopy(j_p)
            t = t.tolist()
            if self.type == "max":
                for i, bar_c in enumerate(t[-1][:-1]):
                    t[-1][i] = -bar_c
            for i, tl in enumerate(t):
                t[i] = [trans_latex_fraction(temp) for temp in tl]
                #print tl
            try:
                t[int(i_p)][int(j_p)] = "[$\mathbf{%s}$]" % t[int(i_p)][int(j_p)].replace("$", "")
            except ValueError:
                # completed, no pivot
                pass

            if len(t) == len(constraints) + 1:
                self.tableau_list.append(t)
                # i, j = kwargs.pop('pivot')
                # print i, j
                basis = kwargs.pop('basis')
                b = copy.deepcopy(basis)
                b = b.tolist()
                cb = copy.deepcopy(self.goal)
                for temp in b:
                    cb.append(0)
                cb_final = [cb[v] for v in b]
                cb_final = ["$%s$" % trans_latex_fraction(str(c), wrap=False) for c in cb_final]
                self.solve_cb_list.append(cb_final)
                #print self.solve_cb_list
                b_index = [temp +1 for temp in b]
                xb = copy.deepcopy(self.x_list)
                for temp_b in range(len(self.x_list)+1, len(self.x_list) + len(b_index) + 1):
                    xb.append("x_{%d}" % temp_b)

                xb_final = [xb[v] for v in b]
                xb_final = ["$%s$" % str(x) for x in xb_final]
                self.solve_xb_list.append(xb_final)
                #print cb_final, xb_final

                self.base_list.append(b_index)


            #print xk

        res = linprog(c=C, A_ub=A_ub, b_ub=b_ub, bounds=((0, None),) * len(self.x_list),
                      options = {'disp': True},
                      callback= lin_callback,
                      )

        n_slack = len(res.slack.tolist())
        self.solve_n_variable = len(self.x_list) + n_slack
        self.solve_goal_list = self.goal + [0] * 3
        self.solve_goal_list = ["$%s$" % trans_latex_fraction(c, wrap=False) for c in self.solve_goal_list]
        #print self.solve_goal_list
        self.solve_x_list = self.x_list

        for n in range(len(self.x_list)+1, len(self.x_list) + n_slack + 1):
            self.solve_x_list += ["x_{%d}" % (n,)]
        self.solve_x_list = ["$%s$" % x for x in self.solve_x_list]


        #print self.solve_x_list


        print res


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

