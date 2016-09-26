# -*- coding: utf-8 -*-

from latex_utils.utils.latex_utils import latex_jinja_env, _file_write
from latex_utils.utils.lpmodel import LP
from copy import deepcopy
import random
import json
import pickle
from Tkinter import Tk

SAVED_QUESTION_MAX = "lp_problem_dual_problem_max.bin"
SAVED_QUESTION_MIN = "lp_problem_dual_problem_min.bin"

n = 4
m = 3


def create_random_lp(n, m, qtype=None):
    para_range = range(-9, 9)
    b_range = range(1, 40)

    def create_goal():
        goal = []
        for i in range(n):
            goal.append(random.choice(para_range))
        return goal

    def create_constraint():
        c_sign_list = create_constraints_sign()
        constr_list = []
        j = 0
        while len(constr_list) < m:
            single_constr = []
            for i in range(n):
                single_constr.append(random.choice(para_range))
            single_constr.append(c_sign_list[j])
            j += 1
            single_constr.append(random.choice(b_range))
            constr_list.append(single_constr)
        return constr_list

    def create_constraints_sign():
        c_sign_list = ["="]
        j = 0
        sign_choice_list = [">", "<"]
        while len(c_sign_list) < m:
            new_sign = random.choice(sign_choice_list)
            if j != 0 and len(set(c_sign_list + [new_sign])) < 3:
                continue
            else:
                if "=" not in sign_choice_list:
                    sign_choice_list.append("=")
                j += 1
                c_sign_list.append(new_sign)
        random.shuffle(c_sign_list)
        return c_sign_list

    def create_sign():
        sign_list = ["="]
        sign_choice_list = [">", "<"]
        j = 0
        while len(sign_list) < n:
            new_sign = random.choice(sign_choice_list)
            if j != 0 and len(set(sign_list + [new_sign])) < 3:
                continue
            else:
                if "=" not in sign_choice_list:
                    sign_choice_list.append("=")
                j += 1
                sign_list.append(new_sign)
        random.shuffle(sign_list)
        return sign_list

    if not qtype:
        qtype = random.choice(["max", "min"])

    lp = LP(qtype=qtype,
            goal=create_goal(),
            constraints=create_constraint(),
            sign=create_sign(),
            dual=True
            )
    return lp



lp_list = []

try:
    with open(SAVED_QUESTION_MAX, 'rb') as f:
        lp_json_list_max = pickle.load(f)
except:
    lp_json_list_max = []

if len(lp_json_list_max) < 100:
    while len(lp_json_list_max) < 100:
        lp = create_random_lp(n,m,qtype="max")
        lp_json = lp.json
        if lp_json not in lp_json_list_max:
            lp_json_list_max.append(lp_json)

    assert len(lp_json_list_max) == 100

    with open(SAVED_QUESTION_MAX, 'wb') as f:
        pickle.dump(lp_json_list_max, f)

try:
    with open(SAVED_QUESTION_MIN, 'rb') as f:
        lp_json_list_min = pickle.load(f)
except:
    lp_json_list_min = []

if len(lp_json_list_min) < 100:
    while len(lp_json_list_min) < 100:
        lp = create_random_lp(n, m, qtype="min")
        lp_json = lp.json
        if lp_json not in lp_json_list_min:
            lp_json_list_min.append(lp_json)

    assert len(lp_json_list_min) == 100

    with open(SAVED_QUESTION_MIN, 'wb') as f:
        pickle.dump(lp_json_list_min, f)


r = Tk()
r.withdraw()
r.clipboard_clear()

template = latex_jinja_env.get_template('/utils/lp_dual_problem.tex')


with open(SAVED_QUESTION_MAX, 'rb') as f:
    lp_json_list_loaded = pickle.load(f)

with open(SAVED_QUESTION_MIN, 'rb') as f:
    lp_json_list_loaded += pickle.load(f)

for l in lp_json_list_loaded:
    lp_dict = json.loads(l)

    lp = LP(**lp_dict)

    tex = template.render(
        show_question=True,
        show_answer=True,
        lp=lp,
        lp_dual=lp.dual_problem()
    )

    r.clipboard_append(tex)
