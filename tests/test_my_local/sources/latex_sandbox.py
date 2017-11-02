LATEX_BLANK_FILLING_PAGE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_PAGE_WITH_MARKDOWN = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack_with_markdown-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack_with_markdown-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_DATA_FILES_MISSING_RAND_QUES_DATA_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
random_question_data_file: "foo"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: blah\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_PAGE_NO_RANDOM_DATA_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_MISSING_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "foo"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""


LATEX_BLANK_FILLING_RANDOM_DATA_FILE_AS_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
cache_key_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_MISSING_EXCLUDED_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "foo"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_DATA_FILE_NOT_FOUND = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - foo
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
    - [1, 2]
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "foo"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_MISSING_RUNPY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
warm_up_by_sandbox: false\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r

cache_key_attrs:\r
    - answer_explanation\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
prompt_process_code: |
    print("abcd")
    
question_process_code: |
    print("abcd")
    
answers_process_code: |
    print("abcd")

question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_MISSING_RUNPY_FILE_AND_MISSING_ATTR = """
type: LatexRandomCodeInlineMultiQuestion\r
warm_up_by_sandbox: false\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
prompt_process_code: |
    print("abcd")

question_process_code: |
    print("abcd")

question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_DATA_FILES_MISSING_RUNPY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: foo\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_RUNPY_FILE_NOT_EXECUTABLE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_MISSING_CACHEKEY_ATTRIBUTE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
cache_key_attrs:\r
    - answer_explanation\r
    - excluded_cache_key_files\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_SUCCESS_WITH_CACHEKEY_ATTRIBUTE_AND_RUNPY_CONTEXT = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
    - question-data/some_file
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
runpy_context: 
        abcd: abcd
        show_result_of_all_init_method: true
background_code: |\r
    print("abcd")\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_PAGE_NO_WARMUP_BY_SANDBOX = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
warm_up_by_sandbox: false\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_CODE_QUESTION = """
type: LatexRandomCodeQuestion\r
id: python_list_getitem\r
access_rules:\r
    add_permissions:\r
        - change_answer\r
timeout: 10\r
value: 5\r
prompt: |\r
    # 取出多维列表中的数据\r
    **用索引的形式**从L中取出"Apple"、"Python"、"Lisa"的数据，分别赋予x1、x2、x3三个变量.\r
data_files:\r
    - "question-data/python/python_list_index_exercise.bin"\r
random_question_data_file: "question-data/python/python_list_index_exercise.bin"\r
background_code: |\r
    from io import BytesIO\r
    bio = BytesIO(data_files["question_data"])\r
    import pickle\r
    L = pickle.load(bio, encoding="latin-1")\r
    for j, l in enumerate(L):\r
        l = [e.title() if e != "PHP" else e for e in l]\r
        L[j] = l\r
prompt_process_code: |\r
    print("L = %s" % repr(L))\r
setup_code: |\r
    from io import BytesIO\r
    bio = BytesIO(data_files["question_data"])\r
    import pickle\r
    L = pickle.load(bio, encoding="latin-1")\r
names_for_user: [L]\r
names_from_user: [x1, x2, x3]\r
initial_code: |\r
    x1 =\r
    x2 =\r
    x3 =\r
test_code: |\r
    if not isinstance(x1, str):\r
        feedback.finish(0, "x1 is not a str.")\r
    if not isinstance(x2, str):\r
        feedback.finish(0, "x2 is not a str.")\r
    if not isinstance(x3, str):\r
        feedback.finish(0, "x3 is not a str.")\r
    L_flatten = [item for sublist in L for item in sublist]\r
    user_list = [x1, x2, x3]\r
    for x in user_list:\r
        if x not in L_flatten:\r
            feedback.finish(0, "您**不是**通过索引取出的数据")\r
    correct_list = ("APPLE", "PYTHON", "LISA")\r
    percentage = 0\r
    for i in range(3):\r
        if user_list[i] == correct_list[i]:\r
            percentage += 1/3\r
    if percentage > 0.99:\r
        feedback.finish(1, "您提取的结果是正确的.")\r
    else:\r
        feedback.finish(percentage, "您提取的结果是错误的.")
"""


LATEX_BLANK_FILLING_NOT_LIST_DATA = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/zero_length_set.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/zero_length_set.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""

LATEX_BLANK_FILLING_EMPTY_LIST_DATA = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack\r
value: 3\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - "question-data/zero_length_list.bin"\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
    - "question-data/jinja_env.py"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"\r
    - "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
excluded_cache_key_files:\r
    - "question-data/linear-programming/lpmodel.py"\r
    - "question-data/linear-programming/linprog.py"\r
random_question_data_file: "question-data/zero_length_list.bin"\r
runpy_file: "question-data/linear-programming/dual-theory/lp_dual_complimentary_slack-runpy.py"\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack1\r
value: 3\r
access_rules:\r
    remove_permissions:\r
        - send_email_about_flow_page\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
    - question-data/jinja_env.py\r
    - question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex\r
excluded_cache_key_files:\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
random_question_data_file: question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
background_code: |\r
    from io import BytesIO\r
    from copy import deepcopy\r
    linprog = data_files["question-data/linear-programming/linprog.py"].decode("utf8")\r
    exec(linprog)\r
    lpmodel = data_files["question-data/linear-programming/lpmodel.py"].decode("utf8")\r
    exec(lpmodel)\r
    jinja_env = data_files["question-data/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    latex_template = data_files["question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(latex_template)\r
    import pickle\r
    bio = BytesIO(data_files["question_data"])\r
    try:\r
        l = pickle.load(bio)\r
        import json\r
        l = json.loads(l)\r
        #print(l)\r
    except Exception as e:\r
        print("%s:%s" % (type(e).__name__, str(e)))\r
    if l["qtype"] == "min":\r
        l["qtype"] = "max"\r
        l["goal"] = [float(i)*(-1) for i in l["goal"]]\r
    lp = LP(**l)\r
    lp.solve(method="simplex")\r
    use_prime_result=False\r
    after_description=(\r
        u"的最优解是$%s = (%s)^T$，" % (r"(%s)^T" % ",\,".join(lp.opt_x), ",\,". join(lp.opt_value),)\r
        +\r
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")\r
    blank_description = (\r
        "$(%s)=$"\r
        % ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))])\r
    )\r
    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])\r
    if not use_prime_result:\r
        after_description = (\r
            u"的对偶问题最优解是$(%s) = (%s)$，" % (\r
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))]),\r
                ",\,".join(lp.dual_opt_solution_str_list[0]))\r
            +\r
            u"则该问题的<strong>最优解</strong>是：")\r
        blank_description = (\r
            "$%s=$"\r
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)\r
        )\r
        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)\r
prompt_process_code: |\r
    tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=u"已知线性规划问题",\r
        after_description=after_description,\r
        lp=lp,\r
    )\r
    print(tex)\r
question_process_code: |\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        after_description=after_description,\r
        blank_description=blank_description,\r
        show_blank=True,\r
        lp=lp,\r
    )\r
    print(tex)\r
answers_process_code: |\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        lp=lp,\r
        answer1= answer1,\r
        forced_left_wrapper='["("]',\r
        forced_right_wrapper='[")", ")^T"]',\r
    )\r
    print(tex)\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r

"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_TEX_TEMPLATE_SPACES = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack1\r
value: 3\r
access_rules:\r
    remove_permissions:\r
        - send_email_about_flow_page\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
    - question-data/jinja_env.py\r
    - question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex\r
excluded_cache_key_files:\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
random_question_data_file: question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
background_code: |\r
    from io import BytesIO\r
    from copy import deepcopy\r
    linprog = data_files["question-data/linear-programming/linprog.py"].decode("utf8")\r
    exec(linprog)\r
    lpmodel = data_files["question-data/linear-programming/lpmodel.py"].decode("utf8")\r
    exec(lpmodel)\r
    jinja_env = data_files["question-data/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    latex_template = data_files["question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(latex_template)\r
    import pickle\r
    bio = BytesIO(data_files["question_data"])\r
    try:\r
        l = pickle.load(bio)\r
        import json\r
        l = json.loads(l)\r
        #print(l)\r
    except Exception as e:\r
        print("%s:%s" % (type(e).__name__, str(e)))\r
    if l["qtype"] == "min":\r
        l["qtype"] = "max"\r
        l["goal"] = [float(i)*(-1) for i in l["goal"]]\r
    lp = LP(**l)\r
    lp.solve(method="simplex")\r
    use_prime_result=False\r
    after_description=(\r
        u"的最优解是$%s = (%s)^T$，" % (r"(%s)^T" % ",\,".join(lp.opt_x), ",\,". join(lp.opt_value),)\r
        +\r
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")\r
    blank_description = (\r
        "$(%s)=$"\r
        % ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))])\r
    )\r
    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])\r
    if not use_prime_result:\r
        after_description = (\r
            u"的对偶问题最优解是$(%s) = (%s)$，" % (\r
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))]),\r
                ",\,".join(lp.dual_opt_solution_str_list[0]))\r
            +\r
            u"则该问题的<strong>最优解</strong>是：")\r
        blank_description = (\r
            "$%s=$"\r
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)\r
        )\r
        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)\r
prompt_process_code: |\r
    tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=u"已知线性规划问题",\r
        after_description=after_description,\r
        lp=lp,\r
    )\r
    print(tex)\r
question_process_code: |\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        after_description=after_description,\r
        blank_description=blank_description,\r
        show_blank=True,\r
        lp=lp,\r
    )\r
    print(tex)\r
answers_process_code: |\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        lp=lp,\r
        answer1= answer1,\r
        forced_left_wrapper='["("]',\r
        forced_right_wrapper='[")", ")^T"]',\r
    )\r
    print(tex)\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r

"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_COMMENTS = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack1\r
value: 3\r
access_rules:\r
    remove_permissions:\r
        - send_email_about_flow_page\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
    - question-data/jinja_env.py\r
    - question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex\r
excluded_cache_key_files:\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
random_question_data_file: question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
background_code: |\r
    from io import BytesIO\r
    # This is some comment\r
    from copy import deepcopy\r
    linprog = data_files["question-data/linear-programming/linprog.py"].decode("utf8")\r
    exec(linprog)\r
    lpmodel = data_files["question-data/linear-programming/lpmodel.py"].decode("utf8")\r
    exec(lpmodel)\r
    jinja_env = data_files["question-data/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    latex_template = data_files["question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(latex_template)\r
    \r
    \r
    import pickle\r
    bio = BytesIO(data_files["question_data"])\r
    try:\r
        l = pickle.load(bio)\r
        import json\r
        l = json.loads(l)\r
        #print(l)\r
    except Exception as e:\r
        print("%s:%s" % (type(e).__name__, str(e)))\r
    if l["qtype"] == "min":\r
        l["qtype"] = "max"\r
        l["goal"] = [float(i)*(-1) for i in l["goal"]]\r
    lp = LP(**l)\r
    lp.solve(method="simplex")\r
    use_prime_result=False\r
    after_description=(\r
        u"的最优解是$%s = (%s)^T$，" % (r"(%s)^T" % ",\,".join(lp.opt_x), ",\,". join(lp.opt_value),)\r
        +\r
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")\r
    blank_description = (\r
        "$(%s)=$"\r
        % ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))])\r
    )\r
    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])\r
    if not use_prime_result:\r
        after_description = (\r
            u"的对偶问题最优解是$(%s) = (%s)$，" % (\r
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))]),\r
                ",\,".join(lp.dual_opt_solution_str_list[0]))\r
            +\r
            u"则该问题的<strong>最优解</strong>是：")\r
        blank_description = (\r
            "$%s=$"\r
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)\r
        )\r
        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)\r
prompt_process_code: |\r
    # This is another comment\r
    tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=u"已知线性规划问题",\r
        after_description=after_description,\r
        lp=lp,\r
    )\r
    print(tex)\r
question_process_code: |\r
    # This is yet another comment, the following block add some spaces\r
    tex = template.render(    \r
        show_question = False,\r
        show_answer=False,     \r
        after_description=after_description,\r
        blank_description=blank_description,\r
        show_blank=True,\r
        lp=lp,\r
    )\r
    print(tex)\r
answers_process_code: |\r
    # This is yyet another comment\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        lp=lp,\r
        answer1= answer1,\r
        forced_left_wrapper='["("]',\r
        forced_right_wrapper='[")", ")^T"]',\r
    )\r
    print(tex)\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r

"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_MORE_THAN_COMMENTS = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack1\r
value: 3\r
access_rules:\r
    remove_permissions:\r
        - send_email_about_flow_page\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
    - question-data/jinja_env.py\r
    - question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex\r
excluded_cache_key_files:\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
random_question_data_file: question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
background_code: |\r
    from io import BytesIO\r
    # This is some comment\r
    from copy import deepcopy\r
    linprog = data_files["question-data/linear-programming/linprog.py"].decode("utf8")\r
    exec(linprog)\r
    lpmodel = data_files["question-data/linear-programming/lpmodel.py"].decode("utf8")\r
    exec(lpmodel)\r
    jinja_env = data_files["question-data/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    latex_template = data_files["question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(latex_template)\r
    \r
    \r
    import sys\r
    import pickle\r
    bio = BytesIO(data_files["question_data"])\r
    try:\r
        l = pickle.load(bio)\r
        import json\r
        l = json.loads(l)\r
        #print(l)\r
    except Exception as e:\r
        print("%s:%s" % (type(e).__name__, str(e)))\r
    if l["qtype"] == "min":\r
        l["qtype"] = "max"\r
        l["goal"] = [float(i)*(-1) for i in l["goal"]]\r
    lp = LP(**l)\r
    lp.solve(method="simplex")\r
    use_prime_result=False\r
    after_description=(\r
        u"的最优解是$%s = (%s)^T$，" % (r"(%s)^T" % ",\,".join(lp.opt_x), ",\,". join(lp.opt_value),)\r
        +\r
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")\r
    blank_description = (\r
        "$(%s)=$"\r
        % ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))])\r
    )\r
    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])\r
    if not use_prime_result:\r
        after_description = (\r
            u"的对偶问题最优解是$(%s) = (%s)$，" % (\r
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))]),\r
                ",\,".join(lp.dual_opt_solution_str_list[0]))\r
            +\r
            u"则该问题的<strong>最优解</strong>是：")\r
        blank_description = (\r
            "$%s=$"\r
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)\r
        )\r
        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)\r
prompt_process_code: |\r
    # This is another comment\r
    tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=u"已知线性规划问题",\r
        after_description=after_description,\r
        lp=lp,\r
    )\r
    print(tex)\r
question_process_code: |\r
    # This is yet another comment, the following block add some spaces\r
    tex = template.render(    \r
        show_question = False,\r
        show_answer=False,     \r
        after_description=after_description,\r
        blank_description=blank_description,\r
        show_blank=True,\r
        lp=lp,\r
    )\r
    print(tex)\r
answers_process_code: |\r
    # And this is not comment at all\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        lp=lp,\r
        answer1= answer1,\r
        forced_left_wrapper='["("]',\r
        forced_right_wrapper='[")", ")^T"]',\r
    )\r
    print(tex)\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r

"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack1\r
value: 3\r
access_rules:\r
    remove_permissions:\r
        - send_email_about_flow_page\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
    - question-data/jinja_env.py\r
    - question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex\r
excluded_cache_key_files:\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
random_question_data_file: question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
background_code: |\r
    from io import BytesIO\r
    # This is some comment\r
    from copy import deepcopy\r
    linprog = data_files["question-data/linear-programming/linprog.py"].decode("utf8")\r
    exec(linprog)\r
    lpmodel = data_files["question-data/linear-programming/lpmodel.py"].decode("utf8")\r
    exec(lpmodel)\r
    jinja_env = data_files["question-data/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    latex_template = data_files["question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(latex_template)\r
    \r
    \r
    import sys\r
    import pickle\r
    bio = BytesIO(data_files["question_data"])\r
    try:\r
        l = pickle.load(bio)\r
        import json\r
        l = json.loads(l)\r
        #print(l)\r
    except Exception as e:\r
        print("%s:%s" % (type(e).__name__, str(e)))\r
    if l["qtype"] == "min":\r
        l["qtype"] = "max"\r
        l["goal"] = [float(i)*(-1) for i in l["goal"]]\r
    lp = LP(**l)\r
    lp.solve(method="simplex")\r
    use_prime_result=False\r
    after_description=(\r
        u"的最优解是$%s = (%s)^T$，" % (r"(%s)^T" % ",\,".join(lp.opt_x), ",\,". join(lp.opt_value),)\r
        +\r
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")\r
    blank_description = (\r
        "$(%s)=$"\r
        % ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))])\r
    )\r
    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])\r
    if not use_prime_result:\r
        after_description = (\r
            u"的对偶问题最优解是$(%s) = (%s)$，" % (\r
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))]),\r
                ",\,".join(lp.dual_opt_solution_str_list[0]))\r
            +\r
            u"则该问题的<strong>最优解</strong>是：")\r
        blank_description = (\r
            "$%s=$"\r
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)\r
        )\r
        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)\r
    \r
    class PromptProcessCodeException(Exception):\r
        pass\r
    class QuestionProcessCodeException(Exception):\r
        pass\r
    class AnswersProcessCodeException(Exception):\r
        pass\r
    class AnswerExplanationProcessCodeException(Exception):\r
        pass\r
    error_info = "test exception"
prompt_process_code: |\r
    # This is another comment\r
    #raise PromptProcessCodeException(error_info)\r
    tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=u"已知线性规划问题",\r
        after_description=after_description,\r
        lp=lp,\r
    )\r
    print(tex)\r
question_process_code: |\r
    # This is yet another comment, the following block add some spaces\r
    #raise QuestionProcessCodeException(error_info)\r
    tex = template.render(    \r
        show_question = False,\r
        show_answer=False,     \r
        after_description=after_description,\r
        blank_description=blank_description,\r
        show_blank=True,\r
        lp=lp,\r
    )\r
    print(tex)\r
answers_process_code: |\r
    # And this is not comment at all\r
    #raise AnswersProcessCodeException(error_info)\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        lp=lp,\r
        answer1= answer1,\r
        forced_left_wrapper='["("]',\r
        forced_right_wrapper='[")", ")^T"]',\r
    )\r
    print(tex)\r
#answer_explanation_process_code: |\r
#    raise AnswerExplanationProcessCodeException(error_info)\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r

"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack1\r
value: 3\r
access_rules:\r
    remove_permissions:\r
        - send_email_about_flow_page\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack.bin\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
    - question-data/jinja_env.py\r
    - question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex\r
excluded_cache_key_files:\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
random_question_data_file: question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack.bin\r
background_code: |\r
    from io import BytesIO\r
    from copy import deepcopy\r
    linprog = data_files["question-data/linear-programming/linprog.py"].decode("utf8")\r
    exec(linprog)\r
    lpmodel = data_files["question-data/linear-programming/lpmodel.py"].decode("utf8")\r
    exec(lpmodel)\r
    jinja_env = data_files["question-data/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    latex_template = data_files["question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(latex_template)\r
    import pickle\r
    bio = BytesIO(data_files["question_data"])\r
    try:\r
        l = pickle.load(bio)\r
        import json\r
        l = json.loads(l)\r
        #print(l)\r
    except Exception as e:\r
        print("%s:%s" % (type(e).__name__, str(e)))\r
    if l["qtype"] == "min":\r
        l["qtype"] = "max"\r
        l["goal"] = [float(i)*(-1) for i in l["goal"]]\r
    lp = LP(**l)\r
    lp.solve(method="simplex")\r
    use_prime_result=False\r
    after_description=(\r
        u"的最优解是$%s = (%s)^T$，" % (r"(%s)^T" % ",\,".join(lp.opt_x), ",\,". join(lp.opt_value),)\r
        +\r
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")\r
    blank_description = (\r
        "$(%s)=$"\r
        % ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))])\r
    )\r
    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])\r
    if not use_prime_result:\r
        after_description = (\r
            u"的对偶问题最优解是$(%s) = (%s)$，" % (\r
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in range(len(lp.dual_opt_solution_list[0]))]),\r
                ",\,".join(lp.dual_opt_solution_str_list[0]))\r
            +\r
            u"则该问题的<strong>最优解</strong>是：")\r
        blank_description = (\r
            "$%s=$"\r
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)\r
        )\r
        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)\r
prompt_process_code: |\r
    tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=u"已知线性规划问题",\r
        after_description=after_description,\r
        lp=lp,\r
    )\r
    print(tex)\r
question_process_code: |\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        after_description=after_description,\r
        blank_description=blank_description,\r
        show_blank=True,\r
        lp=lp,\r
    )\r
    print(tex)\r
answers_process_code: |\r
    tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        lp=lp,\r
        answer1= answer1,\r
        forced_left_wrapper='["("]',\r
        forced_right_wrapper='[")", ")^T"]',\r
    )\r
    print(tex)\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r

"""


LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: lp_dual_complimentary_slack1\r
value: 3\r
access_rules:\r
    remove_permissions:\r
        - send_email_about_flow_page\r
prompt: |\r
    # 互补松弛定理的应用\r
data_files:\r
    - question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
    - question-data/jinja_env.py\r
    - question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex\r
excluded_cache_key_files:\r
    - question-data/linear-programming/lpmodel.py\r
    - question-data/linear-programming/linprog.py\r
random_question_data_file: question-data/linear-programming/dual-theory/lp_simplex_3_iter_max_min_complimentary_slack_01.bin\r
full_process_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    linprog = data_files["question-data/linear-programming/linprog.py"].decode("utf8")\r
    exec(linprog)\r
    lpmodel = data_files["question-data/linear-programming/lpmodel.py"].decode("utf8")\r
    exec(lpmodel)\r
    jinja_env = data_files["question-data/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    latex_template = data_files[\r
        "question-data/linear-programming/dual-theory/lp_dual_complementary_slack.tex"].decode(\r
        "utf8")\r
    template = latex_jinja_env.from_string(latex_template)\r
    bio = BytesIO(data_files["question_data"])\r
    try:\r
        l = pickle.load(bio)\r
        l = json.loads(l)\r
    except Exception as e:\r
        print("%s:%s" % (type(e).__name__, str(e)))\r
    if l["qtype"] == "min":\r
        l["qtype"] = "max"\r
        l["goal"] = [float(i) * (-1) for i in l["goal"]]\r
    lp = LP(**l)\r
    lp.solve(method="simplex")\r
    use_prime_result = False\r
    after_description = (\r
        u"的最优解是$%s = (%s)^T$，" % (\r
        r"(%s)^T" % ",\,".join(lp.opt_x), ",\,".join(lp.opt_value),)\r
        +\r
        u"则该问题的<strong>对偶问题</strong>的<strong>最优解</strong>是:")\r
    blank_description = (\r
        "$(%s)=$"\r
        % ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in\r
                      range(len(lp.dual_opt_solution_list[0]))])\r
    )\r
    answer1 = "(%s)" % ",".join(lp.dual_opt_solution_list[0])\r
    if not use_prime_result:\r
        after_description = (\r
            u"的对偶问题最优解是$(%s) = (%s)$，" % (\r
                ",\,".join(["y^*_{%s}" % str(idx + 1) for idx in\r
                            range(len(lp.dual_opt_solution_list[0]))]),\r
                ",\,".join(lp.dual_opt_solution_str_list[0]))\r
            +\r
            u"则该问题的<strong>最优解</strong>是：")\r
        blank_description = (\r
            "$%s=$"\r
            % (r"(%s)^T" % ",\,".join(lp.opt_x),)\r
        )\r
        answer1 = "(%s)^T" % ",".join(lp.opt_value_without_frac)\r
    question_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=u"已知线性规划问题",\r
        after_description=after_description,\r
        lp=lp,\r
    )\r
    feed_back_dict = {}\r
    feed_back_dict.update({"prompt": question_tex})\r
    blank_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        after_description=after_description,\r
        blank_description=blank_description,\r
        show_blank=True,\r
        lp=lp,\r
    )\r
    feed_back_dict.update({"question": blank_tex})\r
    blank_answer_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        lp=lp,\r
        answer1=answer1,\r
        forced_left_wrapper='["("]',\r
        forced_right_wrapper='[")", ")^T"]',\r
    )\r
    feed_back_dict.update({"answers": blank_answer_tex})\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer1="$%s$" % answer1,\r
    )\r
    feed_back_dict.update({"answer_explanation": answer_explanation_tex})\r
    feedback.add_feedback(json.dumps(feed_back_dict))\r
question: |\r
    The float weight of $\\frac{1}{5}$ is [[blank_1]].\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        width: 10em\r
        hint: <p><strong>输入格式示例:</strong></p><ul><li>(1,2,3,4)</li><li>(1,2,3,4,5)^T</li></ul><p><strong>说明：</strong><ol><li>必须使用英文输入法输入；<li>输入必须是解向量的形式，即用圆括号包围；</li><li>如果需要转置，需要在末尾加上<strong>^T</strong>表示转置.</li></ol>\r
        correct_answer:\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3,4)"\r
        - type: float_list_with_wrapper\r
          forced_left_wrapper: ["("]\r
          forced_right_wrapper: [")", ")^T"]\r
          atol: 0.0001\r
          rtol: 0.0001\r
          value: "(1,2,3)^T"\r
answer_explanation: |\r
    行向量不应有转置符，列向量应有.\r
"""