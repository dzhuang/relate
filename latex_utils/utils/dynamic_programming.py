# -*- coding: utf-8 -*-

from copy import deepcopy
import numpy as np
from collections import deque, OrderedDict

HUGE_NUMBER = float("inf")

class DPResultBase(dict):
    """ Represents the optimization result.
    """
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


class DPResult(DPResultBase):
    def __init__(self, **kwargs):
        super(DPResult, self).__init__(**kwargs)
        assert kwargs["f"] is not None
        assert kwargs["x"]
        assert kwargs["policy"]
        assert kwargs["state_set"]
        assert kwargs["verbose_state_x_dict"]
        assert kwargs["project_list"]

        self.f = kwargs["f"]
        self.x = kwargs["x"]
        self.policy = kwargs["policy"]
        self.state_set = kwargs["state_set"]
        self.verbose_state_x_dict = kwargs["verbose_state_x_dict"]
        self.opt_value = get_simplified_float(self.f[1,-1])
        self.project_list = kwargs["project_list"]


class ResourceAllocationDPResult(DPResult):
    pass


class DynamicProgrammingBase(object):
    def get_gain(self, stage_idx, decision):
        raise NotImplementedError
    pass

class DiscreteDynamicProgramming(DynamicProgrammingBase):
    def __init__(self, total_resource, gain=None, decision_set=None, project_list=None,
                 opt_type="max", allow_non_allocated_resource=True, terminal_value=0):
        assert isinstance(total_resource, (int, float))
        assert opt_type in ["max", "min"]
        self.total_resource = total_resource
        self.gain = gain
        self.gain_str_list = None
        self.gain_str_list_transposed = None
        if gain is not None:
            if isinstance(gain, np.matrix):
                if np.any(np.isnan(self.gain)):
                    if opt_type == "max":
                        self.gain[np.isnan(self.gain)] = -np.inf
                    else:
                        self.gain[np.isnan(self.gain)] = np.inf
                self.n_stages, self.n_decision = np.shape(self.gain)
            else:
                assert isinstance(gain, (list, tuple))
                self.n_stages = len(gain)
                self.n_decision = len(gain[0])
                for i in range(self.n_stages):
                    assert len(gain[i]) == self.n_decision
            self.gain_str_list = self.get_gain_str_list()
            self.gain_str_list_transposed = self.get_gain_str_list(transposed=True)

        if decision_set:
            self.decision_set = decision_set
            for d in decision_set:
                assert isinstance(d, (float,int))
        self.opt_type = opt_type
        self.allow_non_allocated_resource = allow_non_allocated_resource
        self.terminal_value = terminal_value


        self.project_list = project_list
        if not project_list:
            self.project_list = [i+1 for i in range(self.n_stages)]
            if self.n_stages:
                assert self.n_stages == len(self.project_list)
        if decision_set:
            assert self.n_decision == len(decision_set)
        self.state_set = self.get_all_possible_state()
        self.f, self.x = self.get_init_f_x()
        self.state_x_table = None

        # "verbose_state_x_dict" display result which include all states and decisions
        # no matter whether or not those state or decisions will appear
        self.verbose_state_x_dict = None
        self.policy = None

    def get_gain_str_list(self, transposed=False):
        if self.gain is None:
            return None
        if isinstance(self.gain, np.matrix):
            gain_list = self.gain.tolist()
        else:
            gain_list = deepcopy(self.gain)

        if transposed:
            gain_list = [list(x) for x in zip(*gain_list)]
        for gl in gain_list:
            for i, g in enumerate(gl):
                if not np.isfinite(g):
                    gl[i] = "-"
                else:
                    gl[i] = get_simplified_float(g)

        return gain_list

    def get_gain(self, stage_idx, decision):
        # need to return a np.matrix, which conains the gaining, 0 based
        raise NotImplementedError

    def get_process_function_tex(self, stage_index, **kwargs):
        """
        :param stage_index: 1-based stage index
        :param kwargs:
        :return: the process function tex need to be generated for table use
        """
        raise NotImplementedError

    def get_formula_tex(self, n_stage, **kwargs):
        """
        :param stage_index: 1-based stage index
        :param kwargs:
        :return: the tex of the full formular
        """
        raise NotImplementedError

    def get_dp_result_class(self):
        """
        :return: the class of the result to be used.
        """
        raise NotImplementedError

    def get_stage_state_transfer_tex(self, stage_i):
        """
        :param stage_i: 1-based stage index
        :return: the tex of state_transfer
        """
        raise NotImplementedError

    def get_opt_x_subscript(self, stage_i):
        """
        :param stage_i: 1-based stage index
        :return: the tex of state_transfer
        """
        return stage_i


    def get_all_possible_state(self):
        # need to return a sorted list of all possible state, 0 based
        state_set = set()
        import itertools
        for L in range(0, len(self.decision_set) + 1):
            for decision_subset in itertools.combinations(self.decision_set, L):
                if decision_subset:
                    remainder = self.total_resource - sum(decision_subset)
                    if remainder >= 0:
                        state_set.add(remainder)
        return sorted(list(state_set))

    def get_init_f_x(self):
        """
        :return: f and x
        Used to initialize self.f and self.x
        f: a np.array, shape(self.n_stages +2, max_n_state)
        With terminal value initiated.

        x  a np.array, shape(self.n_stages +1, max_n_state)

        Example:
            max_n_state = len(self.state_set)
            f = np.zeros([self.n_stages + 2, max_n_state])
            x = np.zeros([self.n_stages + 1, max_n_state]).tolist()

            # initiating terminal values for f
            if not self.allow_non_allocated_resource:
                for i in range(max_n_state):
                    if self.opt_type == "max":
                        f[self.n_stages+1, i] = -HUGE_NUMBER
                        f[self.n_stages+1, 0] = self.terminal_value
                    else:
                        f[self.n_stages+1, i] = HUGE_NUMBER
            return f, x

        """
        max_n_state = len(self.state_set)
        f = np.zeros([self.n_stages + 2, max_n_state])
        x = np.zeros([self.n_stages + 1, max_n_state]).tolist()
        if not self.allow_non_allocated_resource:
            for i in range(max_n_state):
                if self.opt_type == "max":
                    f[self.n_stages+1, i] = -HUGE_NUMBER
                else:
                    f[self.n_stages+1, i] = HUGE_NUMBER
        f[self.n_stages + 1, 0] = self.terminal_value
        return f, x

    def get_state_idx(self, state):
        return list(self.state_set).index(state)

    def get_opt_policy(self):
        x = deepcopy(self.x)

        solution_list = []
        queued_x_idx_tuple_deque = deque()
        while True:
            # initial state
            state = deepcopy(self.total_resource)
            state_dict = {1:state}
            solution_dict = {}
            for t in range(1, self.n_stages + 1):

                decision_idx = self.get_state_idx(state)
                assert isinstance(x[t][decision_idx], list)
                assert len(x[t][decision_idx]) >=1
                if len(x[t][decision_idx]) > 1:
                    if (t,decision_idx) not in queued_x_idx_tuple_deque:
                        queued_x_idx_tuple_deque.append((t,decision_idx))
                s = x[t][decision_idx][0]
                solution_dict.update({t:s})
                state = self.get_next_state(state, s)
                state_dict.update({t + 1: state})
            solution_list.append([{"state":state_dict,"opt_x":solution_dict}])

            if len(queued_x_idx_tuple_deque) == 0:
                break

            x_remove_idx = queued_x_idx_tuple_deque.pop()
            x[x_remove_idx[0]][x_remove_idx[1]].pop(0)

        return solution_list

    def get_verbose_state_x_dict(self):
        state_x_table = self.state_x_table
        n_stage = len(self.project_list)
        x = self.x
        f = self.f
        state_set = self.state_set
        stage_dict = OrderedDict()
        for stage in range(1, n_stage + 1):
            stage_dict[stage] = {}
            stage_dict[stage]["name"] = self.project_list[stage - 1]
            stage_dict[stage]["state"] = OrderedDict()
            # get all possbile state at this stage
            # 该阶段所有可能的状态stage_state_list，即各阶段表的最左列
            # 该阶段所有可能的决策stage_possbile_x_list，即各阶段表的表头（第二行）
            stage_state_set = set()
            stage_possible_x_set = set()
            for state_idx, state in enumerate(state_set):
                stage_x_result = state_x_table[stage][state_idx]
                if isinstance(stage_x_result, OrderedDict) and stage_x_result:
                    stage_state_set.add(state)
                    stage_possible_x_set.update(set(stage_x_result.keys()))

            stage_state_list = sorted(list(stage_state_set))
            stage_possible_x_list = sorted(list(stage_possible_x_set))
            stage_dict[stage]["decisions"] = stage_possible_x_list
            # 所有状态下的决策及其值，最优决策，最优值
            for state in stage_state_list:
                state_dict = OrderedDict()
                state_results = []
                state_idx = state_set.index(state)
                if isinstance(state_x_table[stage][state_idx], OrderedDict):
                    for decision in stage_possible_x_list:
                        if decision in state_x_table[stage][state_idx]:
                            state_results.append(state_x_table[stage][state_idx][decision])
                        else:
                            state_results.append("")
                else:
                    state_results.append("")

                state_f = f[stage, state_idx]
                state_opt_x = x[stage][state_idx]
                state_dict.update(
                    {state:
                        {
                            "state_results": get_simplified_float(state_results),
                            "state_f": get_simplified_float(state_f),
                            "state_opt_x": get_simplified_float(state_opt_x)
                        }
                    }
                )
                stage_dict[stage]["state"].update(state_dict)

        return stage_dict

    def get_next_state(self, current_state, decision):
        raise NotImplementedError

    def get_movevalue(self, gaining_this_stage, f_next_stage):
        """
        :param gaining_this_stage:
        :param f_next_stage:
        :return: the cumulative relationship between stage gaining and process, multiply of plus
        """
        raise NotImplementedError

    def init_decision_result_value(self):
        """

        :return: the init value of a stage, considering the optimization type
        of the problem, and the cumulative relationships between stages and process
        """
        raise NotImplementedError

    def get_allowed_state_i_idx_list(self, stage_i, allow_state_func=None):
        """
        :param stage_i:
        :param allow_state_func:
        :return: a list of the allowed state at stage_i
        """
        raise NotImplementedError

    def get_allowed_decision_i_idx_list(self, stage_i, state_idx):
        """
        :param stage_i:
        :return: a list of the allowed state at stage_i
        """
        raise NotImplementedError

    def solve(self, allow_state_func=None):
        state_x_table = deepcopy(self.x)
        for t in range(self.n_stages, 0, -1):
            # if t<5:
            #     break

            # If necessary, determine which states are possible at stage t

            allowed_state_i_idx_list = self.get_allowed_state_i_idx_list(stage_i=t, allow_state_func=allow_state_func)
            for state_i_idx in allowed_state_i_idx_list:
                # Determine set of decisions d which are possible from this state and stage
                allowed_decisions_i = self.get_allowed_decision_i_idx_list(stage_i=t,state_idx=state_i_idx)
                value = self.init_decision_result_value()
                bestMove = []
                state_x_table[t][state_i_idx] = OrderedDict()
                for decisions_i in allowed_decisions_i:
                    # State transform
                    next_state = self.get_next_state(list(self.state_set)[state_i_idx], decisions_i)
                    next_state_idx = list(self.state_set).index(next_state)
                    # Compute immediate costs and/or rewards from decision d
                    gaining_i = self.get_gain(t - 1, decisions_i)

                    moveValue = self.get_movevalue(gaining_i, self.f[t + 1, next_state_idx])
                    if np.isfinite(moveValue):
                        state_x_table[t][state_i_idx][decisions_i] = moveValue
                    if (
                            (moveValue > value and self.opt_type == "max")
                        or (moveValue < value and self.opt_type == "min")
                    ):
                        value = moveValue
                        bestMove = [decisions_i]
                    elif moveValue == value:
                        value = moveValue
                        if abs(value) != np.inf:
                            bestMove.append(decisions_i)

                # End of d loop
                self.f[t, state_i_idx] = value
                self.x[t][state_i_idx] = bestMove
                self.state_x_table = state_x_table
                self.verbose_state_x_dict = self.get_verbose_state_x_dict()

            # for unknown f(stage,decision), make sure there's penalty, because we init f with all zeros.
            penalty = -HUGE_NUMBER if self.opt_type == "max" else HUGE_NUMBER
            for not_allowed_state_idx in [s for s in list(range(len(self.state_set))) if s not in allowed_state_i_idx_list]:
                self.f[t, not_allowed_state_idx] = penalty

        result_kass = self.get_dp_result_class()
        self.policy = self.get_opt_policy()

        return result_kass(f=self.f, x=self.x, project_list=self.project_list, state_set=self.state_set, policy=self.policy, verbose_state_x_dict=self.verbose_state_x_dict)


class ResourceAllocationDP(DiscreteDynamicProgramming):

    def get_gain(self, stage_idx, decision):
        if self.opt_type == "max":
            null_value = -np.inf
        else:
            null_value = np.inf
        try:
            decision_idx = self.decision_set.index(decision)
        except ValueError:
            decision_idx = None
        if decision_idx is not None:
            return self.gain[stage_idx, decision_idx]
        else:
            return null_value


    def get_allowed_state_i_idx_list(self, stage_i, allow_state_func=None):
        """
        return the allowed_state of stage_i
        :param stage_i: index of stage
        :param allow_state_func:  a function to get the allowed_state
        :return:
        """

        if allow_state_func:
            # allow_state_func should return a 0 based list
            # which should be a subset of possbile_state_idx
            allowed_state_i_idx_list = allow_state_func(self, stage_i)
        else:
            possible_state_idx_list = list(range(len(self.state_set)))
            if stage_i != 1:
                allowed_state_i_idx_list = [idx for idx in possible_state_idx_list]
            else:
                allowed_state_i_idx_list = [possible_state_idx_list[-1]]

        return allowed_state_i_idx_list

    def get_allowed_decision_i_idx_list(self, stage_i, state_idx):
        allowed_decisions_i = [d for d in self.decision_set
                               if (
                                   d <= list(self.state_set)[state_idx]
                                   and
                                   not np.isinf(self.get_gain(stage_i - 1, d))
                               )]
        return allowed_decisions_i

    def get_next_state(self, current_state, decision):
        return current_state - decision

    def get_movevalue(self, gaining_this_stage, f_next_stage):
        return gaining_this_stage + f_next_stage

    def init_decision_result_value(self):
        if self.opt_type == "max":
            value = -HUGE_NUMBER
        else:
            value = HUGE_NUMBER
        return value

    def get_process_function_tex(self, stage_index, **kwargs):
        tex = (
            u"g_{%(this_stage)s}(s_{%(this_stage)s}, x_{%(this_stage)s})"
            % {
                "this_stage": str(stage_index),
                "next_stage": str(stage_index + 1),
            }
        )
        if stage_index != self.n_stages:
            tex += (
                u" + f_{%(next_stage)s}(s_{%(this_stage)s} - x_{%(this_stage)s})"
                % {
                    "this_stage": str(stage_index),
                    "next_stage": str(stage_index + 1),
                }
            )
        return tex

    def get_formula_tex(self, n_stage=None, **kwargs):
        if not n_stage:
            n_stage = self.n_stages
        tex = (
            r"""
            \begin{align*}\left\{\begin{array}{ll}
            \begin{array}{lll}f_{k}(s_{k})&=%(opt_type)s\limits_{\mathclap{x_k\in X_k(s_k)}}\{ g_k(s_k,x_k)+f_{k+1} (s_{k+1}) \}& \\
            &=%(opt_type)s\limits_{\mathclap{x_k\in X_k(s_k)}}\{ g_k(s_k,x_k)+f_{k+1}(s_k-x_k) \},&k=%(stages_desc)s \end{array}\\
             f_{%(n_stage_plus1)s}( s_{%(n_stage_plus1)s} )=0
            \end{array}\right.
            \end{align*}
            """
            % {
                "opt_type": r"\min" if self.opt_type=="min" else r"\max",
                "stages_desc": ",".join([str(s) for s in list(range(n_stage, 0, -1))]),
                "n_stage_plus1": str(n_stage + 1),
            }
        )
        return tex

    def get_stage_state_transfer_tex(self, stage_i):
        if not self.policy:
            return
        if stage_i == 1:
            return r""
        return r"s_{%(stage_idx)s}-x^*_{%(stage_idx)s}=" % {"stage_idx": str(stage_i - 1)}


    def get_dp_result_class(self):
        """
        :return: the class of the result to be used.
        """
        return ResourceAllocationDPResult


class NonlinearTransportationProblem(DiscreteDynamicProgramming):
    def __init__(self, cost, supply, demand, **kwargs):
        assert isinstance(cost, list)
        assert len(cost) == 2
        assert len(supply) == 2
        for s in supply:
            assert isinstance(s, (int, float))
            assert s > 0
        self.n_stages = len(demand)
        for c in cost:
            assert len(c) == self.n_stages
        self.cost = cost
        self.demand = demand
        for c in cost:
            for j, c_j in enumerate(c):
                assert isinstance(c_j, (tuple,list))
                assert len(c_j) == 2
                assert isinstance(demand[j], (int,float))
                assert demand[j] > 0
        assert supply[0] <= 6
        assert sum(supply) == sum(demand)
        kwargs.pop("decision_set")
        self.supply = supply
        self.decision_set = list(range(supply[0]+1))
        self.n_decision = len(self.decision_set)
        super(NonlinearTransportationProblem, self).__init__(**kwargs)

    def get_gain(self, stage_idx, decision):
        if self.opt_type == "max":
            null_value = -np.inf
        else:
            null_value = np.inf

        try:
            decision_idx = self.decision_set.index(decision)
        except ValueError:
            decision_idx = None
        if decision_idx is not None:
            if decision == 0:
                first_supplier_cost = 0
            else:
                fixed_cost_first = self.cost[0][stage_idx][0]
                variable_cost_first = self.cost[0][stage_idx][1]
                first_supplier_cost = fixed_cost_first + variable_cost_first * decision
            second_supplier_remainder = self.demand[stage_idx] - decision
            if second_supplier_remainder < 0:
                if self.opt_type == "max":
                    return -HUGE_NUMBER
                else:
                    return HUGE_NUMBER
            assert second_supplier_remainder >= 0
            if second_supplier_remainder == 0:
                second_supplier_cost = 0
            else:
                fixed_cost_second = self.cost[1][stage_idx][0]
                variable_cost_second = self.cost[1][stage_idx][1]
                second_supplier_cost = fixed_cost_second + variable_cost_second * second_supplier_remainder

            return first_supplier_cost + second_supplier_cost

        return null_value

    def get_allowed_state_i_idx_list(self, stage_i, allow_state_func=None):
        if allow_state_func:
            # allow_state_func should return a 0 based list
            # which should be a subset of possbile_state_idx
            allowed_state_i_idx_list = allow_state_func(self, stage_i)
        else:
            afterward_demand_list = []
            for idx in range(len(self.demand)):
                if idx >= stage_i - 1:
                    afterward_demand_list.append(self.demand[idx])
            afterward_demand = sum(afterward_demand_list)
            possible_state_max = min(afterward_demand, self.supply[0])
            possible_state_idx_list = list(range(possible_state_max+1))
            if stage_i != 1:
                allowed_state_i_idx_list = [idx for idx in possible_state_idx_list]
            else:
                allowed_state_i_idx_list = [possible_state_idx_list[-1]]
        return allowed_state_i_idx_list

    def get_allowed_decision_i_idx_list(self, stage_i, state_idx):
        allowed_decisions_i = [d for d in self.decision_set
                               if (
                                   d <= self.state_set[state_idx]
                                   and
                                   not np.isinf(self.get_gain(stage_i - 1, d))
                               )]
        return allowed_decisions_i

    def get_process_function_tex(self, stage_index, **kwargs):
        tex = (
            u"g_{1%(this_stage)s}+g_{2%(this_stage)s}"
            % {
                "this_stage": str(stage_index),
                "next_stage": str(stage_index + 1),
            }
        )
        if stage_index != self.n_stages:
            tex += (
                u" + f_{%(next_stage)s}(s_{%(this_stage)s} - x_{1%(this_stage)s})"
                % {
                    "this_stage": str(stage_index),
                    "next_stage": str(stage_index + 1),
                }
            )
        return tex

    def get_next_state(self, current_state, decision):
        return current_state - decision

    def get_movevalue(self, gaining_this_stage, f_next_stage):
        return gaining_this_stage + f_next_stage

    def init_decision_result_value(self):
        if self.opt_type == "max":
            value = -HUGE_NUMBER
        else:
            value = HUGE_NUMBER
        return value

    def get_formula_tex(self, n_stage=None, **kwargs):
        if not n_stage:
            n_stage = self.n_stages
        tex = (
            r"""
            \begin{align*}\left\{\begin{array}{ll}
            \begin{array}{lll}f_{k}(s_{k})&=%(opt_type)s\limits_{\mathclap{x_{1k}\in X_{1k}}}\{g_{1k} + g_{2k} +f_{k+1}(s_{k+1}) \}& \\
            &=%(opt_type)s\limits_{\mathclap{x_{1k}\in X_{1k}}}\{ g_{1k} + g_{2k} +f_{k+1}(s_{k}-x_{1k}) \},&k=%(stages_desc)s \end{array}\\
             f_{%(n_stage_plus1)s}( s_{%(n_stage_plus1)s} )=0
            \end{array}\right.
            \end{align*}
            """
            % {
                "opt_type": r"\min" if self.opt_type=="min" else r"\max",
                "stages_desc": ",".join([str(s) for s in list(range(n_stage, 0, -1))]),
                "n_stage_plus1": str(n_stage + 1),
            }
        )
        return tex

    def get_stage_state_transfer_tex(self, stage_i):
        if not self.policy:
            return
        if stage_i == 1:
            return ""
        return r"s_{%(stage_idx)s}-x^*_{1%(stage_idx)s}=" % {"stage_idx": str(stage_i-1)}

    def get_opt_x_subscript(self, stage_i):
        """
        :param stage_i: 1-based stage index
        :return: the tex of state_transfer
        """
        return "1%s" % stage_i

    def get_dp_result_class(self):
        """
        :return: the class of the result to be used.
        """
        return DPResult


def force_calculate_feasible_state(dp_instance, stage_i):
    """
    确定阶段i(stage_i)允许状态集合
    :param dp_instance:
    :param stage_i:
    :return:
    """

    minimum_allocation = None

    possible_state_idx_list = list(range(len(dp_instance.state_set)))
    if stage_i == 1:
        return [possible_state_idx_list[-1]]
    else:
        allowed_state_i_idx_list = [idx for idx in possible_state_idx_list]

    # 确定该阶段之前的阶段，可能出现的剩余未使用资源的状态集合
    prior_stage_i_decision_possibilities_list = (
        [np.array(dp_instance.decision_set)[np.where(
            np.isfinite(dp_instance.gain[stage]))[1]].tolist()
         for stage in range(stage_i - 1)])
    prior_stage_i_decision_sum = get_all_cartesian_product_sum(
        prior_stage_i_decision_possibilities_list, ubound=dp_instance.total_resource
    )
    prior_remainder_set = set([dp_instance.total_resource - decision_sum for decision_sum in prior_stage_i_decision_sum])

    # 确定该阶段起，可能出现的使用资源数量的总和，但仅在不允许有剩余资源的情况下才使用
    if not dp_instance.allow_non_allocated_resource:
        head_on_stage_i_decision_possibilities_list = (
            [np.array(dp_instance.decision_set)[np.where(
                np.isfinite(dp_instance.gain[stage]))[1]].tolist()
             for stage in range(stage_i - 1, dp_instance.n_stages)])
        head_on_stage_i_decision_sum = get_all_cartesian_product_sum(
            head_on_stage_i_decision_possibilities_list, ubound=dp_instance.total_resource
        )
        head_on_remainder_set = set(head_on_stage_i_decision_sum)
        allowed_state_list = sorted(list(prior_remainder_set.intersection(head_on_remainder_set)))
    else:
        allowed_state_list = sorted(prior_remainder_set)

    allowed_state_i_idx_list = [dp_instance.get_state_idx(state) for state in allowed_state_list]

    return allowed_state_i_idx_list


def get_simplified_float(f):
    if isinstance(f, list):
        return list(get_simplified_float(s) for s in f)
    elif isinstance(f, tuple):
        return tuple(get_simplified_float(s) for s in f)
    try:
        if int(f) == f:
            return int(f)
        else:
            return f
    except:
        return f


def get_all_cartesian_product_sum(iter_lists, ubound=None):
    """
    iter_lists中所有元素的可能和的list，如果ubound不为None，则只返回满足的元素
    return all possible sum of elements in iter_list
    ref http://stackoverflow.com/a/798893/3437454
    :param iter_lists:
    :param ubound:
    :return:
    """
    import itertools
    assert isinstance(iter_lists, (list, tuple))
    ubound = ubound or float("inf")
    cartesian_product = list(itertools.product(*iter_lists))
    return list(set([sum(e) for e in cartesian_product if sum(e) <= ubound]))