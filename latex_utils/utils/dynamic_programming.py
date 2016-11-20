# -*- coding: utf-8 -*-

from copy import deepcopy
import numpy as np
from collections import deque, OrderedDict

HUGE_NUMBER = float("inf")

class DPResult(dict):
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


class ResourceAllocationDPResult(DPResult):
    def __init__(self, **kwargs):
        super(ResourceAllocationDPResult, self).__init__(**kwargs)
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
        self.opt_value = self.f[1,-1]
        self.project_list = kwargs["project_list"]


class DynamicProgramming(object):
    def get_gain(self, stage_idx, decision):
        raise NotImplementedError
    pass


class ResourceAllocationDP(DynamicProgramming):

    def __init__(self, total_resource, gain, decision_set, project_list=None, opt_type="max", allow_non_allocated_resource=True, terminal_value=0):
        assert isinstance(total_resource, (int, float))
        assert opt_type in ["max", "min"]
        self.total_resource = total_resource
        self.gain = gain
        if opt_type == "max":
            self.gain[np.isnan(self.gain)] = -np.inf
        else:
            self.gain[np.isnan(self.gain)] = np.inf
        assert isinstance(gain, np.matrix)
        self.decision_set = decision_set
        for d in decision_set:
            assert isinstance(d, (float,int))
        self.opt_type = opt_type
        self.allow_non_allocated_resource = allow_non_allocated_resource
        self.terminal_value = terminal_value

        self.n_stages, self.n_decision = np.shape(self.gain)
        self.project_list = project_list
        if not project_list:
            self.project_list = [i+1 for i in range(self.n_stages)]
            assert self.n_stages == len(self.project_list)
        assert self.n_decision == len(decision_set)
        self.state_set = self.get_all_possible_state()
        # print "self.state_set:", self.state_set
        self.init_f_x()
        self.state_x_table = None
        self.verbose_state_x_dict = None

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
            # print "decision_idx:", decision_idx
            return self.gain[stage_idx, decision_idx]
        else:
            return null_value

    def get_all_possible_state(self):
        state_set = set()
        import itertools
        for L in range(0, len(self.decision_set) + 1):
            for decision_subset in itertools.combinations(self.decision_set, L):
                if decision_subset:
                    remainder = self.total_resource - sum(decision_subset)
                    if remainder >= 0:
                        state_set.add(remainder)
        return sorted(list(state_set))

    def init_f_x(self):
        max_n_state = len(self.state_set)
        f = np.zeros([self.n_stages + 2, max_n_state])
        x = np.zeros([self.n_stages + 1, max_n_state]).tolist()
        if not self.allow_non_allocated_resource:
            for i in range(max_n_state):
                if self.opt_type == "max":
                    f[self.n_stages+1, i] = -HUGE_NUMBER
                    f[self.n_stages+1, 0] = self.terminal_value
                else:
                    f[self.n_stages+1, i] = HUGE_NUMBER
        self.f = f
        self.x = x

    def get_state_idx(self, state):
        return list(self.state_set).index(state)

    def get_opt_policy(self):
        x = deepcopy(self.x)
        f = self.f

        solution_list = []
        queued_x_idx_tuple_deque = deque()
        while True:
            resource = deepcopy(self.total_resource)
            solution = []
            for t in range(1, self.n_stages + 1):
                decision_idx = self.get_state_idx(resource)
                assert isinstance(x[t][decision_idx], list)
                if len(x[t][decision_idx]) > 1:
                    if (t,decision_idx) not in queued_x_idx_tuple_deque:
                        queued_x_idx_tuple_deque.append((t,decision_idx))
                s = x[t][decision_idx][0]
                solution.append(s)
                resource = resource - s
            solution_list.append(solution)

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


    def solve(self, allow_state_func=None):
        state_x_table = deepcopy(self.x)
        for t in range(self.n_stages, 0, -1):
            # if t<5:
            #     break

            # If necessary, determine which states are possible at stage t
            if allow_state_func:
                # allow_state_func should return a 0 based list
                # which should be a subset of possbile_state_idx
                allowed_state_i_idx_list = allow_state_func(self, t)
            else:
                possible_state_idx_list = list(range(len(self.state_set)))
                if t != 1:
                    allowed_state_i_idx_list = [idx for idx in possible_state_idx_list]
                else:
                    allowed_state_i_idx_list = [possible_state_idx_list[-1]]
            for state_i_idx in allowed_state_i_idx_list:
                # Determine set of decisions d which are possible from this state and stage
                allowed_decisions_i = [d for d in self.decision_set
                                       if (
                                           d <= list(self.state_set)[state_i_idx]
                                           and
                                           not np.isinf(self.get_gain(t - 1, d))
                                       )]
                if self.opt_type == "max":
                    value = -HUGE_NUMBER
                else:
                    value = HUGE_NUMBER
                bestMove = []
                state_x_table[t][state_i_idx] = OrderedDict()
                for decisions_i in allowed_decisions_i:
                    # State trasform
                    # 资源分配问题是这样，换个问题可能就不这样定义了
                    next_state = list(self.state_set)[state_i_idx] - decisions_i
                    next_state_idx = list(self.state_set).index(next_state)
                    # Compute immediate costs and/or rewards from decision d
                    gaining_i = self.get_gain(t - 1, decisions_i)

                    # 过程与阶段之间是和的关系，换个问题可能就不这样定义了
                    moveValue = gaining_i + self.f[t + 1, next_state_idx]
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

        return ResourceAllocationDPResult(f=self.f, x=self.x, project_list=self.project_list, state_set=self.state_set, policy=self.get_opt_policy(), verbose_state_x_dict=self.verbose_state_x_dict)


def force_calculate_feasible_state(dp_instance, t):
    # 确定允许状态集合的上下限
    minimum_allocation = None

    possible_state_idx_list = list(range(len(dp_instance.state_set)))
    if t == 1:
        return [possible_state_idx_list[-1]]
    else:
        allowed_state_i_idx_list = [idx for idx in possible_state_idx_list]

    # 下限
    # 1前面阶段最多能投多少，剩下的
    # 2后面阶段至少要投多少
    max_sum = 0
    for stage in range(0,t-1):
        max_sum += dp_instance.decision_set[np.where(np.isfinite(dp_instance.gain[stage]))[1][-1]]

    if max_sum < dp_instance.total_resource:
        minimum_allocation = dp_instance.total_resource - max_sum

    min_sum = 0
    for stage in range(t, dp_instance.n_stages):
        min_sum += dp_instance.decision_set[np.where(np.isfinite(dp_instance.gain[stage]))[1][0]]

    if min_sum > 0:
        minimum_allocation = max(minimum_allocation, min_sum)

    if minimum_allocation:
        assert minimum_allocation <= dp_instance.total_resource

    # 上限
    # 1前面阶段至少要投多少，剩下的
    # 2后面阶段最多能投多少
    # 3不能超过总量
    min_sum = 0
    for stage in range(0,t-1):
        min_sum += dp_instance.decision_set[np.where(np.isfinite(dp_instance.gain[stage]))[1][0]]

    assert min_sum <= dp_instance.total_resource

    maximum_allocation = dp_instance.total_resource - min_sum

    max_sum = 0
    for stage in range(t, dp_instance.n_stages):
        max_sum += dp_instance.decision_set[np.where(np.isfinite(dp_instance.gain[stage]))[1][-1]]

    if dp_instance.allow_non_allocated_resource:
        # 上限不能超过总量
        if max_sum > 0:
            maximum_allocation = min(max(maximum_allocation, max_sum), dp_instance.total_resource)

    if maximum_allocation:
        allowed_state_i_idx_list = [a for a in allowed_state_i_idx_list if a <= dp_instance.get_state_idx(maximum_allocation)]

    if minimum_allocation:
        allowed_state_i_idx_list = [a for a in allowed_state_i_idx_list if a >= dp_instance.get_state_idx(minimum_allocation)]

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
