# -*- coding: utf-8 -*-

from latex_utils import latex_jinja_env, _file_write
from lpmodel import LP


lp = LP(type="max",
        goal=[2, 5, 3, 5],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [1, 1, 3, 4, "<", 8],
            [1, 3, 1, 1, ">", 21],
            [3, 2, 1, 2, ">", 15]
        ],
#        sign=[">", "<", ">", "="],
        )

template = latex_jinja_env.get_template('lp_model.tex')
tex = template.render(
    description = u"""
    """,
    lp = lp
)



# _file_write("lp_test.tex", tex.encode('UTF-8'))
#
from Tkinter import Tk
r = Tk()
r.withdraw()
r.clipboard_clear()
r.clipboard_append(tex)
#
# res=lp.solve()
#
# print res.x
#
# template = latex_jinja_env.get_template('/utils/lp_simplex.tex')
# tex = template.render(
#     pre_description = u"""
#     """,
#     lp = lp,
#     simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
#     """,
#     simplex_after_description=u"""最优解唯一。
#     """
# )
#
# r.clipboard_append(tex)

lp2 = LP(type="max",
        goal=[3, 6, 3, 4],
        # x="y",
        # x_list=["y_1", "y_2", "w_3"],
        constraints=[
            [1, 1, 3, 4, "<", 8],
            [1, 3, 1, 1, ">", 21],
            [3, 2, 1, 2, ">", 15]
        ],
        #        sign=[">", "<", ">", "="],
        )

lp_list = []
lp_list.append(lp)
lp_list.append(lp2)

#import pickle
import dill as pickle
with open('lp.bin', 'wb') as f:
    pickle.dump(lp_list, f)

with open('lp.bin', 'rb') as f:
    lp_list_loaded = pickle.load(f)


for l in lp_list_loaded:
    print l
    l.solve()
    template = latex_jinja_env.get_template('lp_simplex.tex')
    tex = template.render(
        show_question = True,
        show_answer = True,
        pre_description=u"""
        """,
        lp=l,
        simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
        """,
        simplex_after_description=u"""最优解唯一。
        """
    )

    r.clipboard_append(tex)


{'blank1': {'hint': 'Tex can be rendered in hint, e.g. $x_1$.',
            'required': True,
            '_field_names': ['hint', 'required', 'width', 'hint_title', 'correct_answer','type'],
            'width': '6em',
            'hint_title': 'Hint',
            'correct_answer': ['<plain> BAR', '<plain>bar'],
            'type': 'ShortAnswer'},
 'choice2': {'_field_names': ['type', 'choices'],
             'type': 'ChoicesAnswer',
             'choices': ['~CORRECT~ FOO', 'BAR', 'fOO']},
 'choice_a': {'_field_names': ['required', 'type', 'choices'],
              'required': True,
              'type': 'ChoicesAnswer',
              'choices': ['~CORRECT~ Correct', 'Wrong']},
 'blank_2': {'_field_names': ['width', 'type', 'correct_answer', 'hint'],
             'width': '10em',
             'hint': '<ol><li>with no hint title</li><li>HTML is OK</li><ol>',
             'type': 'ShortAnswer',
             'correct_answer': ['<plain> "1/5"',
                                {'_field_names': ['rtol', 'type', 'value'],
                                 'rtol': 1e-05,
                                 'type': 'float',
                                 'value': 0.2},
                                '<plain> 0.2']
             }
 }