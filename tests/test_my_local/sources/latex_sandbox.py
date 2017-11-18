LATEX_BLANK_FILLING_PAGE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
"""

LATEX_BLANK_FILLING_PAGE_WITH_MARKDOWN = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
runpy_context:\r
    display_markdown: true\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""

LATEX_BLANK_FILLING_DATA_FILES_MISSING_RAND_QUES_DATA_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: foo\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""

LATEX_BLANK_FILLING_PAGE_NO_RANDOM_DATA_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""

LATEX_BLANK_FILLING_MISSING_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
cache_key_files:\r
    - "foo"\r
    - question-data/random-page-test/pyprog.py\r
"""


LATEX_BLANK_FILLING_RANDOM_DATA_FILE_AS_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
cache_key_files:\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/pyprog.py\r
"""


LATEX_BLANK_FILLING_MISSING_EXCLUDED_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
    - foo\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""

LATEX_BLANK_FILLING_DATA_FILE_NOT_FOUND = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - foo
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
"""


LATEX_BLANK_FILLING_MISSING_RUNPY_FILE_AND_MISSING_ATTR = """
type: LatexRandomCodeInlineMultiQuestion\r
warm_up_by_sandbox: false\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
prompt_process_code: |\r
    print("abcd")\r
question_process_code: |\r
    print("abcd")\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r\r
"""

LATEX_BLANK_FILLING_DATA_FILES_MISSING_RUNPY_FILE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: foo\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
"""

LATEX_BLANK_FILLING_RUNPY_FILE_NOT_EXECUTABLE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_template.tex\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing"""

LATEX_BLANK_FILLING_MISSING_CACHEKEY_ATTRIBUTE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing

cache_key_attrs:\r
    - answer_explanation\r
    - excluded_cache_key_files\r
"""


LATEX_BLANK_FILLING_WITH_RUNPY_CONTEXT = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
runpy_context:\r 
    z: [abcd]\r
    display_markdown: true\r
"""

LATEX_BLANK_FILLING_WITH_REVERSE_RUNPY_CONTEXT = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
runpy_context:\r 
    display_markdown: true\r
    z: [abcd]\r
"""

LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
"""

LATEX_BLANK_FILLING_PAGE_NO_WARMUP_BY_SANDBOX = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
warm_up_by_sandbox: false\r
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
    # Pick data from lists in list\r
    **Use index** to get from `L`: "Apple"、"Python"、"Lisa", and assign to `x1` and `x2` and `x3` respectively.\r
data_files:\r
    - question-data/random-page-test/python_list_index_exercise.bin\r
random_question_data_file: question-data/random-page-test/python_list_index_exercise.bin\r
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
            feedback.finish(0, "You're **not** using index")\r
    correct_list = ("APPLE", "PYTHON", "LISA")\r
    percentage = 0\r
    for i in range(3):\r
        if user_list[i] == correct_list[i]:\r
            percentage += 1/3\r
    if percentage > 0.99:\r
        feedback.finish(1, "Your answer is right.")\r
    else:\r
        feedback.finish(percentage, "Your answer is not correct.")
"""


LATEX_BLANK_FILLING_NOT_LIST_DATA = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/zero_length_set.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/zero_length_set.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
"""

LATEX_BLANK_FILLING_EMPTY_LIST_DATA = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/zero_length_list.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/zero_length_list.bin\r
runpy_file: question-data/random-page-test/test_random_runpy.py\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
background_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\r
    exec(prog)\r
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    template_file = data_files[\r
        "question-data/random-page-test/test_template.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(template_file)\r
    bio = BytesIO(data_files["question_data"])\r
    d = pickle.load(bio)\r
    o = PlusFirstElement(**d)\r
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\r
    answer = o.solve()\r
    display_latex = False\r
    display_markdown = True\r
    blank_description = (\r
        u"the result:"\r
    )\r
    pre_description = u"What is the result?"\r
    prompt_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=pre_description,\r
        display_latex=display_latex,\r
        q=q,\r
    )\r
    if display_markdown:\r
        prompt_tex += "[prompt](http://prompt.example.com)"\r
    question_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        show_blank=True,\r
        q=q,\r
    )\r
    if display_markdown:\r
        question_tex += "[question](http://question.example.com)"\r
    answers_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        q=q,\r
        answer=answer,\r
    )\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer="$%s$" % answer,\r
    )\r
    if display_markdown:\r
        answer_explanation_tex += "[explanation](http://explanation.example.com)"\r
prompt_process_code: |\r
    print(prompt_tex)\r
question_process_code: |\r
    print(question_tex)\r
answers_process_code: |\r
    print(answers_tex)\r
answer_explanation_process_code: |\r
    print(answer_explanation_tex)\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
  blank_1:\r
    type: ShortAnswer\r
    hint: None\r
    correct_answer:\r
      - type: float\r
        value: 5\r
        atol: 0.0001\r
        rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MISSING_RUNPY_FILE_WITH_RUNPY_CONTEXT = (
    LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS + (
"""
runpy_context:\r
    a: b\r
    c: d\r
"""))


LATEX_BLANK_FILLING_OLD_STYLE_FAIL_UPDATE_PAGE_DESC = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
prompt_process_code: |\r
    print("abcd")\r
question_process_code: |\r
    print("abcd")\r
answers_process_code: |\r
    print("abcd")\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_TEX_TEMPLATE_SPACES = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template_with_more_spaces.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
background_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\r
    exec(prog)\r
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    template_file = data_files[\r
        "question-data/random-page-test/test_template_with_more_spaces.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(template_file)\r
    bio = BytesIO(data_files["question_data"])\r
    d = pickle.load(bio)\r
    o = PlusFirstElement(**d)\r
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\r
    answer = o.solve()\r
    display_latex = False\r
    display_markdown = True\r
    blank_description = (\r
        u"the result:"\r
    )\r
    pre_description = u"What is the result?"\r
    prompt_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=pre_description,\r
        display_latex=display_latex,\r
        q=q,\r
    )\r
    if display_markdown:\r
        prompt_tex += "[prompt](http://prompt.example.com)"\r
    question_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        show_blank=True,\r
        q=q,\r
    )\r
    if display_markdown:\r
        question_tex += "[question](http://question.example.com)"\r
    answers_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        q=q,\r
        answer=answer,\r
    )\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer="$%s$" % answer,\r
    )\r
    if display_markdown:\r
        answer_explanation_tex += "[explanation](http://explanation.example.com)"\r
prompt_process_code: |\r
    print(prompt_tex)\r
question_process_code: |\r
    print(question_tex)\r
answers_process_code: |\r
    print(answers_tex)\r
answer_explanation_process_code: |\r
    print(answer_explanation_tex)\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
  blank_1:\r
    type: ShortAnswer\r
    hint: None\r
    correct_answer:\r
      - type: float\r
        value: 5\r
        atol: 0.0001\r
        rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_COMMENTS = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
background_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\r
    exec(prog)\r
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    template_file = data_files[\r
        "question-data/random-page-test/test_template.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(template_file)\r
    bio = BytesIO(data_files["question_data"])\r
    d = pickle.load(bio)\r
    o = PlusFirstElement(**d)\r
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\r
    answer = o.solve()\r
    display_latex = False\r
    display_markdown = True\r
    blank_description = (\r
        u"the result:"\r
    )\r
    pre_description = u"What is the result?"\r
    prompt_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=pre_description,\r
        display_latex=display_latex,\r
        q=q,\r
    )\r
    if display_markdown:\r
        prompt_tex += "[prompt](http://prompt.example.com)"\r
    question_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        show_blank=True,\r
        q=q,\r
    )\r
    if display_markdown:\r
        question_tex += "[question](http://question.example.com)"\r
    answers_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        q=q,\r
        answer=answer,\r
    )\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer="$%s$" % answer,\r
    )\r
    if display_markdown:\r
        answer_explanation_tex += "[explanation](http://explanation.example.com)"\r
prompt_process_code: |\r
    # comment1
    print(prompt_tex)\r
question_process_code: |\r
    # comment2
    print(question_tex)\r
answers_process_code: |\r
    # comment3
    print(answers_tex)\r
answer_explanation_process_code: |\r
    # comment4
    print(answer_explanation_tex)\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
  blank_1:\r
    type: ShortAnswer\r
    hint: None\r
    correct_answer:\r
      - type: float\r
        value: 5\r
        atol: 0.0001\r
        rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_MORE_THAN_COMMENTS = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
background_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\r
    exec(prog)\r
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    template_file = data_files[\r
        "question-data/random-page-test/test_template.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(template_file)\r
    bio = BytesIO(data_files["question_data"])\r
    d = pickle.load(bio)\r
    o = PlusFirstElement(**d)\r
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\r
    answer = o.solve()\r
    display_latex = False\r
    display_markdown = True\r
    blank_description = (\r
        u"the result:"\r
    )\r
    pre_description = u"What is the result?"\r
    prompt_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=pre_description,\r
        display_latex=display_latex,\r
        # comment 5: this is more than comment, because we removed a comma
        q=q\r
    )\r
    if display_markdown:\r
        prompt_tex += "[prompt](http://prompt.example.com)"\r
    question_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        show_blank=True,\r
        q=q,\r
    )\r
    if display_markdown:\r
        question_tex += "[question](http://question.example.com)"\r
    answers_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        q=q,\r
        answer=answer,\r
    )\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer="$%s$" % answer,\r
    )\r
    if display_markdown:\r
        answer_explanation_tex += "[explanation](http://explanation.example.com)"\r
prompt_process_code: |\r
    # comment1
    print(prompt_tex)\r
question_process_code: |\r
    # comment2
    print(question_tex)\r
answers_process_code: |\r
    # comment3
    print(answers_tex)\r
answer_explanation_process_code: |\r
    # comment4
    print(answer_explanation_tex)\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
  blank_1:\r
    type: ShortAnswer\r
    hint: None\r
    correct_answer:\r
      - type: float\r
        value: 5\r
        atol: 0.0001\r
        rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
background_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\r
    exec(prog)\r
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    template_file = data_files[\r
        "question-data/random-page-test/test_template.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(template_file)\r
    bio = BytesIO(data_files["question_data"])\r
    d = pickle.load(bio)\r
    o = PlusFirstElement(**d)\r
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\r
    answer = o.solve()\r
    display_latex = False\r
    display_markdown = True\r
    blank_description = (\r
        u"the result:"\r
    )\r
    pre_description = u"What is the result?"\r
    prompt_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=pre_description,\r
        display_latex=display_latex,\r
        q=q,\r
    )\r
    if display_markdown:\r
        prompt_tex += "[prompt](http://prompt.example.com)"\r
    question_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        show_blank=True,\r
        q=q,\r
    )\r
    if display_markdown:\r
        question_tex += "[question](http://question.example.com)"\r
    answers_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        q=q,\r
        answer=answer,\r
    )\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer="$%s$" % answer,\r
    )\r
    if display_markdown:\r
        answer_explanation_tex += "[explanation](http://explanation.example.com)"\r
    class PromptProcessCodeException(Exception):\r
        pass\r
    class QuestionProcessCodeException(Exception):\r
        pass\r
    class AnswersProcessCodeException(Exception):\r
        pass\r
    class AnswerExplanationProcessCodeException(Exception):\r
        pass\r
    error_info = "test exception"\r
prompt_process_code: |\r
    #raise PromptProcessCodeException(error_info)\r
    print(prompt_tex)\r
question_process_code: |\r
    #raise QuestionProcessCodeException(error_info)\r
    print(question_tex)\r
answers_process_code: |\r
    #raise AnswersProcessCodeException(error_info)\r
    print(answers_tex)\r
answer_explanation_process_code: |\r
    #raise AnswerExplanationProcessCodeException(error_info)\r
    print(answer_explanation_tex)\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
  blank_1:\r
    type: ShortAnswer\r
    hint: None\r
    correct_answer:\r
      - type: float\r
        value: 5\r
        atol: 0.0001\r
        rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data.bin\r
background_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\r
    exec(prog)\r
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    template_file = data_files[\r
        "question-data/random-page-test/test_template.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(template_file)\r
    bio = BytesIO(data_files["question_data"])\r
    d = pickle.load(bio)\r
    o = PlusFirstElement(**d)\r
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\r
    answer = o.solve()\r
    display_latex = False\r
    display_markdown = True\r
    blank_description = (\r
        u"the result:"\r
    )\r
    pre_description = u"What is the result?"\r
    prompt_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=pre_description,\r
        display_latex=display_latex,\r
        q=q,\r
    )\r
    if display_markdown:\r
        prompt_tex += "[prompt](http://prompt.example.com)"\r
    question_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        show_blank=True,\r
        q=q,\r
    )\r
    if display_markdown:\r
        question_tex += "[question](http://question.example.com)"\r
    answers_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        q=q,\r
        answer=answer,\r
    )\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer="$%s$" % answer,\r
    )\r
    if display_markdown:\r
        answer_explanation_tex += "[explanation](http://explanation.example.com)"\r
prompt_process_code: |\r
    print(prompt_tex)\r
question_process_code: |\r
    print(question_tex)\r
answers_process_code: |\r
    print(answers_tex)\r
answer_explanation_process_code: |\r
    print(answer_explanation_tex)\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
  blank_1:\r
    type: ShortAnswer\r
    hint: None\r
    correct_answer:\r
      - type: float\r
        value: 5\r
        atol: 0.0001\r
        rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""


LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE = """
type: LatexRandomCodeInlineMultiQuestion\r
id: rand\r
value: 3\r
access_rules:\r
    add_permissions:\r
        - see_correctness\r
        - change_answer\r
prompt: |\r
    # random question test\r
data_files:\r
    - question-data/random-page-test/jinja_env.py\r
    - question-data/random-page-test/pyprog.py\r
    - question-data/random-page-test/test_data_01.bin\r
    - question-data/random-page-test/test_random_runpy.py\r
    - question-data/random-page-test/test_template.tex\r
excluded_cache_key_files:\r
    - question-data/random-page-test/pyprog.py\r
random_question_data_file: question-data/random-page-test/test_data_01.bin\r
full_process_code: |\r
    from io import BytesIO\r
    import pickle\r
    import json\r
    try:\r
        runpy_context\r
    except NameError:\r
        runpy_context = {}\r
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\r
    exec(prog)\r
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\r
    exec(jinja_env)\r
    template_file = data_files[\r
        "question-data/random-page-test/test_template.tex"].decode("utf8")\r
    template = latex_jinja_env.from_string(template_file)\r
    bio = BytesIO(data_files["question_data"])\r
    d = pickle.load(bio)\r
    o = PlusFirstElement(**d)\r
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\r
    answer = o.solve()\r
    display_latex = runpy_context.get("display_latex", False)\r
    display_markdown = runpy_context.get("display_markdown", False)\r
    blank_description = (\r
        u"the result:"\r
    )\r
    pre_description = runpy_context.get("pre_description", u"What is the result?")\r
    prompt_tex = template.render(\r
        show_question=True,\r
        show_answer=False,\r
        pre_description=pre_description,\r
        display_latex=display_latex,\r
        q=q,\r
    )\r
    if display_markdown:\r
        prompt_tex += "[prompt](http://prompt.example.com)"\r
    feed_back_dict = {}\r
    feed_back_dict.update({"prompt": prompt_tex})\r
    question_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        show_blank=True,\r
        q=q,\r
    )\r
    if display_markdown:\r
        question_tex += "[question](http://question.example.com)"\r
    feed_back_dict.update({"question": question_tex})\r
    answers_tex = template.render(\r
        show_question=False,\r
        show_answer=False,\r
        show_blank_answer=True,\r
        blank_description=blank_description,\r
        display_latex=display_latex,\r
        q=q,\r
        answer=answer,\r
    )\r
    feed_back_dict.update({"answers": answers_tex})\r
    answer_explanation_tex = template.render(\r
        show_answer_explanation=True,\r
        answer="$%s$" % answer,\r
    )\r
    if display_markdown:\r
        answer_explanation_tex += "[explanation](http://explanation.example.com)"\r
    feed_back_dict.update({"answer_explanation": answer_explanation_tex})\r
    feedback.add_feedback(json.dumps(feed_back_dict))\r
question: |\r
    Fill [[blank_1]]\r
answers:\r
    blank_1:\r
        type: ShortAnswer\r
        hint: None\r
        correct_answer:\r
        - type: float\r
          value: 5\r
          atol: 0.0001\r
          rtol: 0.0001\r
answer_explanation: |\r
    Nothing\r
"""