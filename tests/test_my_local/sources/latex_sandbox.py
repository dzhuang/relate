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
question_process_code: |
    print("abcd")
    
blank_process_code: |
    print("abcd")
    
blank_answer_process_code: |
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
question_process_code: |
    print("abcd")

blank_process_code: |
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
question_process_code: |\r
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