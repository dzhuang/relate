# -*- coding: utf-8 -*-
"""
A top-level linear programming interface. Currently this interface only
solves linear programming problems via the Simplex Method.

.. versionadded:: 0.15.0

Functions
---------
.. autosummary::
   :toctree: generated/

    linprog
    linprog_verbose_callback
    linprog_terse_callback

"""

from __future__ import division, print_function, absolute_import

import numpy as np
import copy
from scipy.optimize._linprog import OptimizeResult, _check_unknown_options
from scipy.optimize._linprog import  _solve_simplex

BIG_M = 1E+7

__all__ = ['linprog', 'linprog_verbose_callback', 'linprog_terse_callback']

__docformat__ = "restructuredtext en"


def adjust_order(modified_iter, order_list):
    m = len(order_list)
    t = copy.deepcopy(modified_iter)
    for idx in range(m):
        t[order_list[idx]] = modified_iter[idx]
    return t


def _pivot_col_dual(T, pivrow, tol=1.0E-12):
    ma = np.ma.masked_where(T[pivrow, :-1] >= -tol, T[pivrow, :-1], copy=False)
    if ma.count() == 0:
        return False, np.nan
    mcjbar = np.ma.masked_where(T[pivrow, :-1] >= -tol, T[-1, :-1], copy=False)
    q = abs(mcjbar / ma)
    return True, np.ma.where(q == q.min())[0][0]


def _pivot_row_dual(T, tol=1.0E-12, bland=False):
    ma = np.ma.masked_where(T[:-1, -1] >= -tol, T[:-1, -1], copy=False)
    if ma.count() == 0:
        return False, np.nan
    if bland:
        return True, np.where(ma.mask == False)[0][0]
    return True, np.ma.where(ma == ma.min())[0][0]


def _solve_dual_simplex(T, n, basis, maxiter=1000, phase=2, callback=None,
                   tol=1.0E-12, nit0=0, bland=False):
    """
    Solve a linear programming problem in "standard maximization form" using
    the Simplex Method.

    Minimize :math:`f = c^T x`

    subject to

    .. math::

        Ax = b
        x_i >= 0
        b_j >= 0

    Parameters
    ----------
    T : array_like
        A 2-D array representing the simplex T corresponding to the
        maximization problem.  It should have the form:

        [[A[0, 0], A[0, 1], ..., A[0, n_total], b[0]],
         [A[1, 0], A[1, 1], ..., A[1, n_total], b[1]],
         .
         .
         .
         [A[m, 0], A[m, 1], ..., A[m, n_total], b[m]],
         [c[0],   c[1], ...,   c[n_total],    0]]

        for a Phase 2 problem, or the form:

        [[A[0, 0], A[0, 1], ..., A[0, n_total], b[0]],
         [A[1, 0], A[1, 1], ..., A[1, n_total], b[1]],
         .
         .
         .
         [A[m, 0], A[m, 1], ..., A[m, n_total], b[m]],
         [c[0],   c[1], ...,   c[n_total],   0],
         [c'[0],  c'[1], ...,  c'[n_total],  0]]

         for a Phase 1 problem (a Problem in which a basic feasible solution is
         sought prior to maximizing the actual objective.  T is modified in
         place by _solve_simplex.
    n : int
        The number of true variables in the problem.
    basis : array
        An array of the indices of the basic variables, such that basis[i]
        contains the column corresponding to the basic variable for row i.
        Basis is modified in place by _solve_simplex
    maxiter : int
        The maximum number of iterations to perform before aborting the
        optimization.
    phase : int
        The phase of the optimization being executed.  In phase 1 a basic
        feasible solution is sought and the T has an additional row representing
        an alternate objective function.
    callback : callable, optional
        If a callback function is provided, it will be called within each
        iteration of the simplex algorithm. The callback must have the
        signature `callback(xk, **kwargs)` where xk is the current solution
        vector and kwargs is a dictionary containing the following::
        "T" : The current Simplex algorithm T
        "nit" : The current iteration.
        "pivot" : The pivot (row, column) used for the next iteration.
        "phase" : Whether the algorithm is in Phase 1 or Phase 2.
        "basis" : The indices of the columns of the basic variables.
    tol : float
        The tolerance which determines when a solution is "close enough" to
        zero in Phase 1 to be considered a basic feasible solution or close
        enough to positive to to serve as an optimal solution.
    nit0 : int
        The initial iteration number used to keep an accurate iteration total
        in a two-phase problem.
    bland : bool
        If True, choose pivots using Bland's rule [3].  In problems which
        fail to converge due to cycling, using Bland's rule can provide
        convergence at the expense of a less optimal path about the simplex.

    Returns
    -------
    res : OptimizeResult
        The optimization result represented as a ``OptimizeResult`` object.
        Important attributes are: ``x`` the solution array, ``success`` a
        Boolean flag indicating if the optimizer exited successfully and
        ``message`` which describes the cause of the termination. Possible
        values for the ``status`` attribute are:
         0 : Optimization terminated successfully
         1 : Iteration limit reached
         2 : Problem appears to be infeasible
         3 : Problem appears to be unbounded

        See `OptimizeResult` for a description of other attributes.
    """
    nit = nit0
    complete = False

    if phase == 1:
        m = T.shape[0] - 2
    elif phase == 2:
        m = T.shape[0] - 1
    else:
        raise ValueError("Argument 'phase' to _solve_simplex must be 1 or 2")

    if phase == 2:
        # Check if any artificial variables are still in the basis.
        # If yes, check if any coefficients from this row and a column
        # corresponding to one of the non-artificial variable is non-zero.
        # If found, pivot at this term. If not, start phase 2.
        # Do this for all artificial variables in the basis.
        # Ref: "An Introduction to Linear Programming and Game Theory"
        # by Paul R. Thie, Gerard E. Keough, 3rd Ed,
        # Chapter 3.7 Redundant Systems (pag 102)

        # 考虑了有冗余的约束条件时
        # 只会在第二阶段出现，因为只有在第二阶段才有方程
        # 第一阶段的约束条件通常都会引入松弛或剩余变量，而方程都会引入人工变量
        for pivrow in [row for row in range(basis.size)
                       if basis[row] > T.shape[1] - 2]:
            non_zero_row = [col for col in range(T.shape[1] - 1)
                            if T[pivrow, col] != 0]
            if len(non_zero_row) > 0:
                pivcol = non_zero_row[0]
                # variable represented by pivcol enters
                # variable in basis[pivrow] leaves
                basis[pivrow] = pivcol
                pivval = T[pivrow][pivcol]
                T[pivrow, :] = T[pivrow, :] / pivval
                for irow in range(T.shape[0]):
                    if irow != pivrow:
                        T[irow, :] = T[irow, :] - T[pivrow, :] * T[irow, pivcol]
                nit += 1

    if len(basis[:m]) == 0:
        solution = np.zeros(T.shape[1] - 1, dtype=np.float64)
    else:
        solution = np.zeros(max(T.shape[1] - 1, max(basis[:m]) + 1),
                             dtype=np.float64)

    while not complete:
        # Find the pivot column
        pivrow_found, pivrow = _pivot_row_dual(T, tol, bland)
        if not pivrow_found:
            pivcol = np.nan
            pivrow = np.nan
            status = 0
            complete = True
        else:
            # Find the pivot row
            pivcol_found, pivcol = _pivot_col_dual(T, pivrow, tol=1.0E-12)
            if not pivcol_found:
                status = 2
                complete = True

        if callback is not None:
            solution[:] = 0
            solution[basis[:m]] = T[:m, -1]
            callback(solution[:n], **{"tableau": T,
                                      "phase": phase,
                                      "nit": nit,
                                      "pivot": (pivrow, pivcol),
                                      "basis": basis,
                                      "complete": complete and phase == 2})

        if not complete:
            if nit >= maxiter:
                # Iteration limit exceeded
                status = 1
                complete = True
            else:
                # variable represented by pivcol enters
                # variable in basis[pivrow] leaves
                basis[pivrow] = pivcol
                pivval = T[pivrow][pivcol]
                T[pivrow, :] = T[pivrow, :] / pivval
                for irow in range(T.shape[0]):
                    if irow != pivrow:
                        T[irow, :] = T[irow, :] - T[pivrow, :] * T[irow, pivcol]
                nit += 1

    return nit, status


class lpSolver(object):
    """
    Solve the following linear programming problem via a two-phase
    simplex algorithm.

    maximize:     c^T * x

    subject to:   A_ub * x <= b_ub
                  A_eq * x == b_eq

    Parameters
    ----------
    c : array_like
        Coefficients of the linear objective function to be maximized.
    A_ub : array_like
        2-D array which, when matrix-multiplied by x, gives the values of the
        upper-bound inequality constraints at x.
    b_ub : array_like
        1-D array of values representing the upper-bound of each inequality
        constraint (row) in A_ub.
    A_eq : array_like
        2-D array which, when matrix-multiplied by x, gives the values of the
        equality constraints at x.
    b_eq : array_like
        1-D array of values representing the RHS of each equality constraint
        (row) in A_eq.
    bounds : array_like
        The bounds for each independent variable in the solution, which can take
        one of three forms::
        None : The default bounds, all variables are non-negative.
        (lb, ub) : If a 2-element sequence is provided, the same
                  lower bound (lb) and upper bound (ub) will be applied
                  to all variables.
        [(lb_0, ub_0), (lb_1, ub_1), ...] : If an n x 2 sequence is provided,
                  each variable x_i will be bounded by lb[i] and ub[i].
        Infinite bounds are specified using -np.inf (negative)
        or np.inf (positive).
    callback : callable
        If a callback function is provide, it will be called within each
        iteration of the simplex algorithm. The callback must have the
        signature `callback(xk, **kwargs)` where xk is the current solution
        vector and kwargs is a dictionary containing the following::
        "tableau" : The current Simplex algorithm tableau
        "nit" : The current iteration.
        "pivot" : The pivot (row, column) used for the next iteration.
        "phase" : Whether the algorithm is in Phase 1 or Phase 2.
        "bv" : A structured array containing a string representation of each
               basic variable and its current value.

    Options
    -------
    maxiter : int
       The maximum number of iterations to perform.
    disp : bool
        If True, print exit status message to sys.stdout
    tol : float
        The tolerance which determines when a solution is "close enough" to zero
        in Phase 1 to be considered a basic feasible solution or close enough
        to positive to to serve as an optimal solution.
    bland : bool
        If True, use Bland's anti-cycling rule [3] to choose pivots to
        prevent cycling.  If False, choose pivots which should lead to a
        converged solution more quickly.  The latter method is subject to
        cycling (non-convergence) in rare instances.

    Returns
    -------
    A scipy.optimize.OptimizeResult consisting of the following fields::
        x : ndarray
            The independent variable vector which optimizes the linear
            programming problem.
        slack : ndarray
            The values of the slack variables.  Each slack variable corresponds
            to an inequality constraint.  If the slack is zero, then the
            corresponding constraint is active.
        success : bool
            Returns True if the algorithm succeeded in finding an optimal
            solution.
        status : int
            An integer representing the exit status of the optimization::
             0 : Optimization terminated successfully
             1 : Iteration limit reached
             2 : Problem appears to be infeasible
             3 : Problem appears to be unbounded
        nit : int
            The number of iterations performed.
        message : str
            A string descriptor of the exit status of the optimization.

    Examples
    --------
    Consider the following problem:

    Minimize: f = -1*x[0] + 4*x[1]

    Subject to: -3*x[0] + 1*x[1] <= 6
                 1*x[0] + 2*x[1] <= 4
                            x[1] >= -3

    where:  -inf <= x[0] <= inf

    This problem deviates from the standard linear programming problem.  In
    standard form, linear programming problems assume the variables x are
    non-negative.  Since the variables don't have standard bounds where
    0 <= x <= inf, the bounds of the variables must be explicitly set.

    There are two upper-bound constraints, which can be expressed as

    dot(A_ub, x) <= b_ub

    The input for this problem is as follows:

    >>> from scipy.optimize import linprog
    >>> c = [-1, 4]
    >>> A = [[-3, 1], [1, 2]]
    >>> b = [6, 4]
    >>> x0_bnds = (None, None)
    >>> x1_bnds = (-3, None)
    >>> res = linprog(c, A, b, bounds=(x0_bnds, x1_bnds))
    >>> print(res)
         fun: -22.0
     message: 'Optimization terminated successfully.'
         nit: 1
       slack: array([ 39.,   0.])
      status: 0
     success: True
           x: array([ 10.,  -3.])

    References
    ----------
    .. [1] Dantzig, George B., Linear programming and extensions. Rand
           Corporation Research Study Princeton Univ. Press, Princeton, NJ, 1963
    .. [2] Hillier, S.H. and Lieberman, G.J. (1995), "Introduction to
           Mathematical Programming", McGraw-Hill, Chapter 4.
    .. [3] Bland, Robert G. New finite pivoting rules for the simplex method.
           Mathematics of Operations Research (2), 1977: pp. 103-107.
    """
    @property
    def method(self):
        raise NotImplementedError()

    def __init__(self, c, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
                 bounds=None, maxiter=1000, disp=False, callback=None,
                 tol=1.0E-12, bland=False, cnstr_orig_order=None, **unknown_options):

        # problem
        self.maxiter = maxiter
        #self.method = self.get_method_name()

        self.T_extra_n = self.get_T_extra_n()

        # options
        self.disp = disp
        self.callback = callback
        self.tol = tol
        self.bland = bland
        self.cnstr_orig_order = cnstr_orig_order

        # validation
        _check_unknown_options(unknown_options)

        status = 0
        self.messages = {0: "Optimization terminated successfully.",
                    1: "Iteration limit reached.",
                    2: "Optimization failed. Unable to find a feasible"
                       " starting point.",
                    3: "Optimization failed. The problem appears to be unbounded.",
                    4: "Optimization failed. Singular matrix encountered."}
        self.have_floor_variable = False

        cc = np.asarray(c)

        # The initial value of the objective function element in the tableau
        f0 = 0

        # The number of variables as given by c
        n = len(c)

        # Convert the input arguments to arrays (sized to zero if not provided)
        Aeq = np.asarray(A_eq) if A_eq is not None else np.empty([0, len(cc)])
        Aub = np.asarray(A_ub) if A_ub is not None else np.empty([0, len(cc)])
        beq = np.ravel(np.asarray(b_eq)) if b_eq is not None else np.empty([0])
        bub = np.ravel(np.asarray(b_ub)) if b_ub is not None else np.empty([0])

        # Analyze the bounds and determine what modifications to be made to
        # the constraints in order to accommodate them.
        L = np.zeros(n, dtype=np.float64)
        U = np.ones(n, dtype=np.float64) * np.inf
        if bounds is None or len(bounds) == 0:
            pass
        elif len(bounds) == 2 and not hasattr(bounds[0], '__len__'):
            # All bounds are the same
            a = bounds[0] if bounds[0] is not None else -np.inf
            b = bounds[1] if bounds[1] is not None else np.inf
            L = np.asarray(n * [a], dtype=np.float64)
            U = np.asarray(n * [b], dtype=np.float64)
        else:
            if len(bounds) != n:
                status = -1
                message = ("Invalid input for linprog with method = '%s'.  "
                           "Length of bounds is inconsistent with the length of c" % self.method)
            else:
                try:
                    for i in range(n):
                        if len(bounds[i]) != 2:
                            raise IndexError()
                        L[i] = bounds[i][0] if bounds[i][0] is not None else -np.inf
                        U[i] = bounds[i][1] if bounds[i][1] is not None else np.inf
                except IndexError:
                    status = -1
                    message = ("Invalid input for linprog with "
                               "method = '%s'.  bounds must be a n x 2 "
                               "sequence/array where n = len(c)." % self.method)

        if np.any(L == -np.inf):
            # If any lower-bound constraint is a free variable
            # add the first column variable as the "floor" variable which
            # accommodates the most negative variable in the problem.
            n = n + 1
            L = np.concatenate([np.array([0]), L])
            U = np.concatenate([np.array([np.inf]), U])
            cc = np.concatenate([np.array([0]), cc])
            Aeq = np.hstack([np.zeros([Aeq.shape[0], 1]), Aeq])
            Aub = np.hstack([np.zeros([Aub.shape[0], 1]), Aub])
            self.have_floor_variable = True

        # Now before we deal with any variables with lower bounds < 0,
        # deal with finite bounds which can be simply added as new constraints.
        # Also validate bounds inputs here.
        for i in range(n):
            if(L[i] > U[i]):
                status = -1
                message = ("Invalid input for linprog with method = '%s'.  "
                           "Lower bound %d is greater than upper bound %d" % (self.method, i, i))

            if np.isinf(L[i]) and L[i] > 0:
                status = -1
                message = ("Invalid input for linprog with method = '%s'.  "
                           "Lower bound may not be +infinity" % self.method)

            if np.isinf(U[i]) and U[i] < 0:
                status = -1
                message = ("Invalid input for linprog with method = '%s'.  "
                           "Upper bound may not be -infinity" % self.method)

            if np.isfinite(L[i]) and L[i] > 0:
                # Add a new lower-bound(negative upper-bound) constraint
                Aub = np.vstack([Aub, np.zeros(n)])
                Aub[-1, i] = -1
                bub = np.concatenate([bub, np.array([-L[i]])])
                L[i] = 0

            if np.isfinite(U[i]):
                # Add a new upper-bound constraint
                Aub = np.vstack([Aub, np.zeros(n)])
                Aub[-1, i] = 1
                bub = np.concatenate([bub, np.array([U[i]])])
                U[i] = np.inf

        # Now find negative lower bounds (finite or infinite) which require a
        # change of variables or free variables and handle them appropriately
        for i in range(0, n):
            if L[i] < 0:
                if np.isfinite(L[i]) and L[i] < 0:
                    # Add a change of variables for x[i]
                    # For each row in the constraint matrices, we take the
                    # coefficient from column i in A,
                    # and subtract the product of that and L[i] to the RHS b
                    beq = beq - Aeq[:, i] * L[i]
                    bub = bub - Aub[:, i] * L[i]
                    # We now have a nonzero initial value for the objective
                    # function as well.
                    f0 = f0 - cc[i] * L[i]
                else:
                    # This is an unrestricted variable, let x[i] = u[i] - v[0]
                    # where v is the first column in all matrices.
                    Aeq[:, 0] = Aeq[:, 0] - Aeq[:, i]
                    Aub[:, 0] = Aub[:, 0] - Aub[:, i]
                    cc[0] = cc[0] - cc[i]

            if np.isinf(U[i]):
                if U[i] < 0:
                    status = -1
                    message = ("Invalid input for linprog with "
                               "method = '%s'.  Upper bound may not be -inf." % self.method)

        # The number of upper bound constraints (rows in A_ub and elements in b_ub)
        mub = len(bub)

        # The number of equality constraints (rows in A_eq and elements in b_eq)
        meq = len(beq)

        # The total number of constraints
        m = mub + meq

        # The number of slack variables (one for each of the upper-bound constraints)
        n_slack = mub

        # The number of artificial variables (one for each lower-bound and equality
        # constraint)
        n_artificial = meq + np.count_nonzero(bub < 0)

        try:
            Aub_rows, Aub_cols = Aub.shape
        except ValueError:
            raise ValueError("Invalid input.  A_ub must be two-dimensional")

        try:
            Aeq_rows, Aeq_cols = Aeq.shape
        except ValueError:
            raise ValueError("Invalid input.  A_eq must be two-dimensional")

        if Aeq_rows != meq:
            status = -1
            message = ("Invalid input for linprog with method = '%s'.  "
                       "The number of rows in A_eq must be equal "
                       "to the number of values in b_eq" % self.method)

        if Aub_rows != mub:
            status = -1
            message = ("Invalid input for linprog with method = '%s'.  "
                       "The number of rows in A_ub must be equal "
                       "to the number of values in b_ub" % self.method)

        if Aeq_cols > 0 and Aeq_cols != n:
            status = -1
            message = ("Invalid input for linprog with method = '%s'.  "
                       "Number of columns in A_eq must be equal "
                       "to the size of c" % self.method)

        if Aub_cols > 0 and Aub_cols != n:
            status = -1
            message = ("Invalid input for linprog with method = '%s'.  "
                       "Number of columns in A_ub must be equal to the size of c" % self.method)

        if status != 0:
            # Invalid inputs provided
            raise ValueError(message)

        self.m = m
        self.n = n
        self.n_slack = n_slack
        self.n_artificial = n_artificial
        self.cc = cc
        self.f0 = f0
        self.meq = meq
        self.Aeq = Aeq
        self.beq = beq
        self.mub = mub
        self.Aub = Aub
        self.bub = bub
        self.b = None

        self.T = None
        self.init_tablaeu = None
        self.slack_list =[]
        self.slack_idx = []
        self.artificial_list = []
        self.L = L

    def create_tableau(self):
        m = self.m
        n = self.n
        n_slack = self.n_slack
        n_artificial = self.n_artificial
        meq = self.meq
        Aeq = self.Aeq
        beq = self.beq
        mub = self.mub
        Aub = self.Aub
        bub = self.bub

        # Create the tableau

        n_T_extra_lines = self.get_T_extra_n()
        # 2 extra lines for 2 stage simplex method
        # 1 extra lines for big m method and dual simplex method
        assert n_T_extra_lines in [1, 2]

        T = np.zeros([m + n_T_extra_lines, n + n_slack + n_artificial + 1])

        if n_T_extra_lines == 2:
            # Insert objective into tableau
            T[-n_T_extra_lines, :self.n] = self.cc
            T[-n_T_extra_lines, -1] = self.f0

        b = T[:-n_T_extra_lines, -1]

        if meq > 0:
            # Add Aeq to the tableau
            T[:meq, :n] = Aeq
            # Add beq to the tableau
            b[:meq] = beq
        if mub > 0:
            # Add Aub to the tableau
            T[meq:meq + mub, :n] = Aub
            # At bub to the tableau
            b[meq:meq + mub] = bub
            # Add the slack variables to the tableau
            np.fill_diagonal(T[meq:m, n:n + n_slack], 1)
            self.slack_list = [i for i in range(n, n + n_slack)]
            self.slack_idx = [0] * meq + range(n, n + n_slack)

        self.b = b
        self.T = T
        self.set_up_tableau()

    def set_up_tableau(self):
        raise NotImplementedError()

    def get_T_extra_n(self):
        raise NotImplementedError()

    def solve(self):
        raise NotImplementedError()


class lpSimplexSolver(lpSolver):
    method = "simplex"

    def get_T_extra_n(self):
        return 2

    def get_method_name(self):
        return "simplex"

    def set_up_tableau(self):
        n_artificial = self.n_artificial
        n_slack = self.n_slack
        slack_list = self.slack_list
        slack_idx = self.slack_idx
        cnstr_orig_order = self.cnstr_orig_order
        m = self.m
        n = self.n
        b = self.b
        meq = self.meq
        T = np.copy(self.T)

        # Further set up the tableau.
        # If a row corresponds to an equality constraint or a negative b (a lower
        # bound constraint), then an artificial variable is added for that row.
        # Also, if b is negative, first flip the signs in that constraint.
        # b < 0 是在这里处理
        slcount = 0
        avcount = 0
        basis = np.zeros(m, dtype=int)
        r_artificial = np.zeros(n_artificial, dtype=int)
        artificial_list = []

        # recover the order of constraints
        if cnstr_orig_order:
            r_need_artificial = np.zeros(m, dtype=bool)
            for i in range(m):
                if i < meq or b[i] < 0:
                    r_need_artificial[i] = True

            T = adjust_order(T, cnstr_orig_order)
            r_need_artificial = adjust_order(r_need_artificial, cnstr_orig_order)
            b = adjust_order(b, cnstr_orig_order)
            slack_idx = adjust_order(slack_idx, cnstr_orig_order)

            for i in range(m):
                if r_need_artificial[i]:
                    # basic variable i is in column n+n_slack+avcount
                    basis[i] = n + n_slack + avcount
                    artificial_list.append(basis[i])
                    r_artificial[avcount] = i
                    avcount += 1
                    if b[i] < 0:
                        b[i] *= -1
                        T[i, :-1] *= -1

                        # This line is needed since T and b
                        # are modified
                        T[i, -1] = b[i]

                        # negative slack -- surplus variable
                        # use negative to represent it is a negative slack
                        for j, sl in enumerate(slack_list):
                            if sl == n + i:
                                slack_list[j] = -sl

                    T[i, basis[i]] = 1
                    T[-1, basis[i]] = 1
                else:
                    basis[i] = slack_idx[i]
                    slcount += 1

        else:
            for i in range(m):
                if i < meq or b[i] < 0:
                    # basic variable i is in column n+n_slack+avcount
                    basis[i] = n + n_slack + avcount
                    artificial_list.append(basis[i])
                    r_artificial[avcount] = i
                    avcount += 1
                    if b[i] < 0:
                        b[i] *= -1
                        T[i, :-1] *= -1

                        # negative slack -- surplus variable
                        # use negative to represent it is a negative slack
                        for j, sl in enumerate(slack_list):
                            if sl == n + i - 1:
                                slack_list[j] = -sl

                    T[i, basis[i]] = 1
                    T[-1, basis[i]] = 1
                else:
                    # basic variable i is in column n+slcount
                    basis[i] = n + slcount
                    slcount += 1

        # Make the artificial variables basic feasible variables by subtracting
        # each row with an artificial variable from the Phase 1 objective
        for r in r_artificial:
            T[-1, :] = T[-1, :] - T[r, :]

        self.T = T
        self.init_basis = basis
        self.artificial_list = artificial_list
        self.slack_list = slack_list

    def solve(self):
        self.create_tableau()
        T = np.copy(self.T)
        n = self.n
        basis = np.copy(self.init_basis)
        callback = self.callback
        maxiter = self.maxiter
        tol = self.tol
        bland = self.bland
        n_slack = self.n_slack
        n_artificial = self.n_artificial
        messages = self.messages
        disp = self.disp
        slack_list = self.slack_list
        artificial_list = self.artificial_list
        m = self.m
        have_floor_variable = self.have_floor_variable
        L = self.L

        nit1, status = _solve_simplex (T, n, basis, phase=1, callback=callback,
                                       maxiter=maxiter, tol=tol, bland=bland)

        # if pseudo objective is zero, remove the last row from the tableau and
        # proceed to phase 2

        if abs (T[-1, -1]) < tol:
            # Remove the pseudo-objective row from the tableau
            T = T[:-1, :]
            # Remove the artificial variable columns from the tableau
            # http://docs.scipy.org/doc/numpy/reference/generated/numpy.s_.html#numpy-s 注意
            # http://stackoverflow.com/questions/12616821/numpy-slicing-from-variable
            T = np.delete (T, np.s_[n + n_slack:n + n_slack + n_artificial], 1)
        else:
            # Failure to find a feasible starting point
            status = 2

        if status != 0:
            message = messages[status]
            if disp:
                print (message)
            return OptimizeResult (x=np.nan, fun=-T[-1, -1], nit=nit1, status=status,
                                   slack_list=slack_list, artificial_list=artificial_list,
                                   message=message, success=False)

            # Phase 2
        nit2, status = _solve_simplex (T, n, basis, maxiter=maxiter - nit1, phase=2,
                                       callback=callback, tol=tol, nit0=nit1,
                                       bland=bland)

        solution = np.zeros (n + n_slack + n_artificial)
        solution[basis[:m]] = T[:m, -1]
        x = solution[:n]
        slack = solution[n:n + n_slack]

        # For those variables with finite negative lower bounds,
        # reverse the change of variables
        masked_L = np.ma.array (L, mask=np.isinf (L), fill_value=0.0).filled ()
        x = x + masked_L

        # For those variables with infinite negative lower bounds,
        # take x[i] as the difference between x[i] and the floor variable.
        if have_floor_variable:
            for i in range (1, n):
                if np.isinf (L[i]):
                    x[i] -= x[0]
            x = x[1:]

        # Optimization complete at this point
        obj = -T[-1, -1]

        if status in (0, 1):
            if disp:
                print (messages[status])
                print ("         Current function value: {0: <12.6f}".format (obj))
                print ("         Iterations: {0:d}".format (nit2))
        else:
            if disp:
                print (messages[status])
                print ("         Iterations: {0:d}".format (nit2))

        return OptimizeResult (x=x, fun=obj, nit=int(nit2), status=status, slack=slack,
                               slack_list=slack_list, artificial_list=artificial_list,
                               message=messages[status], success=(status == 0))


class lpDualSimplexSolver(lpSolver):
    method = "dual_simplex"

    def __init__(self, c, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
                 bounds=None, maxiter=1000, disp=False, callback=None,
                 tol=1.0E-12, bland=False, cnstr_orig_order=None, **unknown_options):
        super(lpDualSimplexSolver, self).__init__(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                 bounds=bounds, maxiter=maxiter, disp=disp, callback=callback,
                 tol=tol, bland=bland, cnstr_orig_order=cnstr_orig_order, **unknown_options)
        beq = np.ravel(np.asarray(b_eq)) if b_eq is not None else np.empty([0])
        status = 0
        message = ""
        if len(beq) > 0:
            status = -1
            message = ("Invalid input for linprog with method = '%s'.  "
                       "This method cannot solve problems with equation constraints." % self.method)
        if status != 0:
            # Invalid inputs provided
            raise ValueError(message)
        self.n_neg_slack = self.n_artificial - len(beq)
        self.n_artificial = 0

    def get_T_extra_n(self):
        return 1

    def set_up_tableau(self):
        n_neg_slack = self.n_neg_slack
        n_slack = self.n_slack
        slack_list = self.slack_list
        slack_idx = self.slack_idx
        cnstr_orig_order = self.cnstr_orig_order
        m = self.m
        n = self.n
        b = self.b
        meq = self.meq
        T = np.copy(self.T)
        tol = self.tol
        f0 = self.f0

        T[-1, :self.n] = self.cc
        T[-1, -1] = f0

        slcount = 0
        basis = np.zeros(m, dtype=int)
        artificial_list = []

        # recover the order of constraints
        if cnstr_orig_order:
            T = adjust_order(T, cnstr_orig_order)
            b = adjust_order(b, cnstr_orig_order)
            slack_idx = adjust_order(slack_idx, cnstr_orig_order)

            for i in range(m):
                if b[i] < 0:
                    for j, sl in enumerate(slack_list):
                        if sl == n + i:
                            slack_list[j] = -sl
                basis[i] = slack_idx[i]
                slcount += 1

        else:
            for i in range(m):
                if b[i] < 0:
                    for j, sl in enumerate(slack_list):
                        if sl == n + i:
                            slack_list[j] = -sl
                basis[i] = slack_idx[i]
                slcount += 1

        self.T = T

        ma = np.ma.masked_where(T[-1, :-1] >= -tol, T[-1, :-1], copy=False)
        if ma.count() > 0:
            raise ValueError(
                "Invalid input for linprog with method = '%s'.  "
                "This method cannot solve problems with non-optimized bar cj." % self.method)
        self.init_tablaeu = np.copy(T)
        self.init_basis = basis
        self.artificial_list = artificial_list
        self.slack_list = slack_list

    def solve(self):
        self.create_tableau()
        T = np.copy(self.T)
        n = self.n
        basis = np.copy(self.init_basis)
        callback = self.callback
        maxiter = self.maxiter
        tol = self.tol
        bland = self.bland
        n_slack = self.n_slack
        n_artificial = self.n_artificial
        messages = self.messages
        disp = self.disp
        slack_list = self.slack_list
        artificial_list = self.artificial_list
        m = self.m
        have_floor_variable = self.have_floor_variable
        L = self.L

        # Phase 2
        nit2, status = _solve_dual_simplex(T, n, basis, maxiter=maxiter, phase=2,
                                           callback=callback, tol=tol, bland=bland)

        solution = np.zeros (n + n_slack + n_artificial)
        solution[basis[:m]] = T[:m, -1]
        x = solution[:n]
        slack = solution[n:n + n_slack]

        # For those variables with finite negative lower bounds,
        # reverse the change of variables
        masked_L = np.ma.array (L, mask=np.isinf (L), fill_value=0.0).filled ()
        x = x + masked_L

        # For those variables with infinite negative lower bounds,
        # take x[i] as the difference between x[i] and the floor variable.
        if have_floor_variable:
            for i in range (1, n):
                if np.isinf (L[i]):
                    x[i] -= x[0]
            x = x[1:]

        # Optimization complete at this point
        obj = -T[-1, -1]

        if status in (0, 1):
            if disp:
                print (messages[status])
                print ("         Current function value: {0: <12.6f}".format (obj))
                print ("         Iterations: {0:d}".format (nit2))
        else:
            if disp:
                print (messages[status])
                print ("         Iterations: {0:d}".format (nit2))

        return OptimizeResult(x=x, fun=obj, nit=int(nit2), status=status, slack=slack,
                              slack_list=slack_list, artificial_list=artificial_list, init_tablaeu=self.init_tablaeu,
                              message=messages[status], success=(status == 0))


class lpBigMSolver(lpSolver):
    method = "big_m_simplex"
    def get_T_extra_n(self):
        return 1

    def set_up_tableau(self):
        n_artificial = self.n_artificial
        n_slack = self.n_slack
        slack_list = self.slack_list
        slack_idx = self.slack_idx
        cnstr_orig_order = self.cnstr_orig_order
        m = self.m
        n = self.n
        b = self.b
        meq = self.meq
        T = np.copy(self.T)

        # Further set up the tableau.
        # If a row corresponds to an equality constraint or a negative b (a lower
        # bound constraint), then an artificial variable is added for that row.
        # Also, if b is negative, first flip the signs in that constraint.
        # b < 0 是在这里处理
        slcount = 0
        avcount = 0
        basis = np.zeros (m, dtype=int)
        r_artificial = np.zeros (n_artificial, dtype=int)
        artificial_list = []

        # recover the order of constraints
        if cnstr_orig_order:
            r_need_artificial = np.zeros (m, dtype=bool)
            for i in range (m):
                if i < meq or b[i] < 0:
                    r_need_artificial[i] = True

            T = adjust_order (T, cnstr_orig_order)
            r_need_artificial = adjust_order (r_need_artificial, cnstr_orig_order)
            b = adjust_order (b, cnstr_orig_order)
            slack_idx = adjust_order (slack_idx, cnstr_orig_order)

            for i in range (m):
                if r_need_artificial[i]:
                    # basic variable i is in column n+n_slack+avcount
                    basis[i] = n + n_slack + avcount
                    artificial_list.append (basis[i])
                    r_artificial[avcount] = i
                    avcount += 1
                    if b[i] < 0:
                        b[i] *= -1
                        T[i, :-1] *= -1

                        # This line is needed since T and b
                        # are modified
                        T[i, -1] = b[i]

                        # negative slack -- surplus variable
                        # use negative to represent it is a negative slack
                        for j, sl in enumerate (slack_list):
                            if sl == n + i:
                                slack_list[j] = -sl

                    T[i, basis[i]] = 1
                    T[-1, :n] = self.cc
                    T[-1, -1] = self.f0
                    T[-1, basis[i]] = BIG_M
                else:
                    basis[i] = slack_idx[i]
                    slcount += 1

        else:
            for i in range (m):
                if i < meq or b[i] < 0:
                    # basic variable i is in column n+n_slack+avcount
                    basis[i] = n + n_slack + avcount
                    artificial_list.append (basis[i])
                    r_artificial[avcount] = i
                    avcount += 1
                    if b[i] < 0:
                        b[i] *= -1
                        T[i, :-1] *= -1

                        # negative slack -- surplus variable
                        # use negative to represent it is a negative slack
                        for j, sl in enumerate (slack_list):
                            if sl == n + i - 1:
                                slack_list[j] = -sl

                    T[i, basis[i]] = 1
                    T[i, basis[i]] = 1
                    T[-1, basis[i]] = BIG_M
                else:
                    # basic variable i is in column n+slcount
                    basis[i] = n + slcount
                    slcount += 1

        # 大M法的目标函数所在的TGet the goal of the big-m problem
        T[-1, :n] = self.cc
        T[-1, -1] = self.f0
        self.init_tablaeu = np.copy(T)

        # Make the artificial variables basic feasible variables by subtracting
        # each row with an artificial variable from the Phase 1 objective
        for r in r_artificial:
            T[-1, :-1] = T[-1, :-1] - T[r, :-1] * BIG_M
            T[-1, -1] -= T[r, -1] * BIG_M

        self.T = T
        self.init_basis = basis
        self.artificial_list = artificial_list
        self.slack_list = slack_list

    def solve(self):
        self.create_tableau()
        T = np.copy(self.T)
        n = self.n
        basis = np.copy(self.init_basis)
        callback = self.callback
        maxiter = self.maxiter
        tol = self.tol
        bland = self.bland
        n_slack = self.n_slack
        n_artificial = self.n_artificial
        messages = self.messages
        disp = self.disp
        slack_list = self.slack_list
        artificial_list = self.artificial_list
        m = self.m
        have_floor_variable = self.have_floor_variable
        L = self.L

        nit, status = _solve_simplex(T, n, basis, maxiter=maxiter, phase=2,
                                      callback=callback, tol=tol,
                                      bland=bland)

        solution = np.zeros(n + n_slack + n_artificial)
        solution[basis[:m]] = T[:m, -1]
        x = solution[:n]
        slack = solution[n:n + n_slack]

        # For those variables with finite negative lower bounds,
        # reverse the change of variables
        masked_L = np.ma.array (L, mask=np.isinf (L), fill_value=0.0).filled ()
        x = x + masked_L

        # For those variables with infinite negative lower bounds,
        # take x[i] as the difference between x[i] and the floor variable.
        if have_floor_variable:
            for i in range (1, n):
                if np.isinf (L[i]):
                    x[i] -= x[0]
            x = x[1:]

        # Optimization complete at this point
        obj = -T[-1, -1]

        if status in (0, 1):
            if disp:
                print (messages[status])
                print ("         Current function value: {0: <12.6f}".format (obj))
                print ("         Iterations: {0:d}".format (nit))
        else:
            if disp:
                print (messages[status])
                print ("         Iterations: {0:d}".format (nit))

        #print("self.init_tablaeu", self.init_tablaeu)

        return OptimizeResult(x=x, fun=obj, nit=int (nit), status=status, slack=slack,
                               slack_list=slack_list, artificial_list=artificial_list, init_tablaeu=self.init_tablaeu,
                               message=messages[status], success=(status == 0))


def linprog(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
            bounds=None, method='simplex', callback=None,
            cnstr_orig_order=None,
            options=None):
    meth = method.lower()
    if options is None:
        options = {}

    if meth == 'simplex':
        lp = lpSimplexSolver(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                             bounds=bounds, callback=callback, cnstr_orig_order=cnstr_orig_order, **options)
        return lp.solve()
    elif meth == 'big_m_simplex':
        lp = lpBigMSolver(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                             bounds=bounds, callback=callback, cnstr_orig_order=cnstr_orig_order, **options)
        return lp.solve()
    elif meth == 'dual_simplex':
        lp = lpDualSimplexSolver(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                             bounds=bounds, callback=callback, cnstr_orig_order=cnstr_orig_order, **options)
        return lp.solve()
    else:
        raise ValueError('Unknown solver %s' % method)

