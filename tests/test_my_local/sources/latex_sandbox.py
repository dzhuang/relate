LATEX_BLANK_FILLING_PAGE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_PAGE_WITH_MARKDOWN = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
runpy_context:
    display_markdown: true
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_DATA_FILES_MISSING_RAND_QUES_DATA_FILE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: foo
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_PAGE_NO_RANDOM_DATA_FILE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_MISSING_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
cache_key_files:
    - "foo"
    - question-data/random-page-test/pyprog.py
"""


LATEX_BLANK_FILLING_RANDOM_DATA_FILE_AS_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
cache_key_files:
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/pyprog.py
"""


LATEX_BLANK_FILLING_MISSING_EXCLUDED_CACHEKEY_FILE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
    - foo
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_DATA_FILE_NOT_FOUND = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - foo
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_MISSING_RUNPY_FILE_AND_MISSING_ATTR = """
type: LatexRandomCodeInlineMultiQuestion
warm_up_by_sandbox: false
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
prompt_process_code: |
    print("abcd")
question_process_code: |
    print("abcd")
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_DATA_FILES_MISSING_RUNPY_FILE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: foo
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_RUNPY_FILE_NOT_EXECUTABLE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_template.tex
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing"""

LATEX_BLANK_FILLING_MISSING_CACHEKEY_ATTRIBUTE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing

cache_key_attrs:
    - answer_explanation
    - excluded_cache_key_files
"""


LATEX_BLANK_FILLING_WITH_RUNPY_CONTEXT = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
runpy_context: 
    z: [abcd]
    display_markdown: true
"""

LATEX_BLANK_FILLING_WITH_REVERSE_RUNPY_CONTEXT = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
runpy_context: 
    display_markdown: true
    z: [abcd]
"""

LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_PAGE_NO_WARMUP_BY_SANDBOX = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
warm_up_by_sandbox: false
"""

LATEX_CODE_QUESTION = """
type: LatexRandomCodeQuestion
id: python_list_getitem
access_rules:
    add_permissions:
        - change_answer
timeout: 10
value: 5
prompt: |
    # Pick data from lists in list
    **Use index** to get from `L`: "Apple"、"Python"、"Lisa", and assign to `x1` and `x2` and `x3` respectively.
data_files:
    - question-data/random-page-test/python_list_index_exercise.bin
random_question_data_file: question-data/random-page-test/python_list_index_exercise.bin
background_code: |
    from io import BytesIO
    bio = BytesIO(data_files["question_data"])
    import pickle
    L = pickle.load(bio, encoding="latin-1")
    for j, l in enumerate(L):
        l = [e.title() if e != "PHP" else e for e in l]
        L[j] = l
prompt_process_code: |
    print("L = %s" % repr(L))
setup_code: |
    from io import BytesIO
    bio = BytesIO(data_files["question_data"])
    import pickle
    L = pickle.load(bio, encoding="latin-1")
names_for_user: [L]
names_from_user: [x1, x2, x3]
initial_code: |
    x1 =
    x2 =
    x3 =
test_code: |
    if not isinstance(x1, str):
        feedback.finish(0, "x1 is not a str.")
    if not isinstance(x2, str):
        feedback.finish(0, "x2 is not a str.")
    if not isinstance(x3, str):
        feedback.finish(0, "x3 is not a str.")
    L_flatten = [item for sublist in L for item in sublist]
    user_list = [x1, x2, x3]
    for x in user_list:
        if x not in L_flatten:
            feedback.finish(0, "You're **not** using index")
    correct_list = ("APPLE", "PYTHON", "LISA")
    percentage = 0
    for i in range(3):
        if user_list[i] == correct_list[i]:
            percentage += 1/3
    if percentage > 0.99:
        feedback.finish(1, "Your answer is right.")
    else:
        feedback.finish(percentage, "Your answer is not correct.")
"""


LATEX_BLANK_FILLING_NOT_LIST_DATA = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/zero_length_set.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/zero_length_set.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""

LATEX_BLANK_FILLING_EMPTY_LIST_DATA = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/zero_length_list.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/zero_length_list.bin
runpy_file: question-data/random-page-test/test_random_runpy.py
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
background_code: |
    from io import BytesIO
    import pickle
    import json
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")
    exec(prog)
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")
    exec(jinja_env)
    template_file = data_files[
        "question-data/random-page-test/test_template.tex"].decode("utf8")
    template = latex_jinja_env.from_string(template_file)
    bio = BytesIO(data_files["question_data"])
    d = pickle.load(bio)
    o = PlusFirstElement(**d)
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])
    answer = o.solve()
    display_latex = False
    display_markdown = True
    blank_description = (
        u"the result:"
    )
    pre_description = u"What is the result?"
    prompt_tex = template.render(
        show_question=True,
        show_answer=False,
        pre_description=pre_description,
        display_latex=display_latex,
        q=q,
    )
    if display_markdown:
        prompt_tex += "[prompt](http://prompt.example.com)"
    question_tex = template.render(
        show_question=False,
        show_answer=False,
        blank_description=blank_description,
        display_latex=display_latex,
        show_blank=True,
        q=q,
    )
    if display_markdown:
        question_tex += "[question](http://question.example.com)"
    answers_tex = template.render(
        show_question=False,
        show_answer=False,
        show_blank_answer=True,
        blank_description=blank_description,
        display_latex=display_latex,
        q=q,
        answer=answer,
    )
    answer_explanation_tex = template.render(
        show_answer_explanation=True,
        answer="$%s$" % answer,
    )
    if display_markdown:
        answer_explanation_tex += "[explanation](http://explanation.example.com)"
prompt_process_code: |
    print(prompt_tex)
question_process_code: |
    print(question_tex)
answers_process_code: |
    print(answers_tex)
answer_explanation_process_code: |
    print(answer_explanation_tex)
question: |
    Fill [[blank_1]]
answers:
  blank_1:
    type: ShortAnswer
    hint: None
    correct_answer:
      - type: float
        value: 5
        atol: 0.0001
        rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MISSING_RUNPY_FILE_WITH_RUNPY_CONTEXT = (
    LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS + (
"""
runpy_context:
    a: b
    c: d
"""))


LATEX_BLANK_FILLING_OLD_STYLE_FAIL_UPDATE_PAGE_DESC = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
prompt_process_code: |
    print("abcd")
question_process_code: |
    print("abcd")
answers_process_code: |
    print("abcd")
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_TEX_TEMPLATE_SPACES = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template_with_more_spaces.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
background_code: |
    from io import BytesIO
    import pickle
    import json
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")
    exec(prog)
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")
    exec(jinja_env)
    template_file = data_files[
        "question-data/random-page-test/test_template_with_more_spaces.tex"].decode("utf8")
    template = latex_jinja_env.from_string(template_file)
    bio = BytesIO(data_files["question_data"])
    d = pickle.load(bio)
    o = PlusFirstElement(**d)
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])
    answer = o.solve()
    display_latex = False
    display_markdown = True
    blank_description = (
        u"the result:"
    )
    pre_description = u"What is the result?"
    prompt_tex = template.render(
        show_question=True,
        show_answer=False,
        pre_description=pre_description,
        display_latex=display_latex,
        q=q,
    )
    if display_markdown:
        prompt_tex += "[prompt](http://prompt.example.com)"
    question_tex = template.render(
        show_question=False,
        show_answer=False,
        blank_description=blank_description,
        display_latex=display_latex,
        show_blank=True,
        q=q,
    )
    if display_markdown:
        question_tex += "[question](http://question.example.com)"
    answers_tex = template.render(
        show_question=False,
        show_answer=False,
        show_blank_answer=True,
        blank_description=blank_description,
        display_latex=display_latex,
        q=q,
        answer=answer,
    )
    answer_explanation_tex = template.render(
        show_answer_explanation=True,
        answer="$%s$" % answer,
    )
    if display_markdown:
        answer_explanation_tex += "[explanation](http://explanation.example.com)"
prompt_process_code: |
    print(prompt_tex)
question_process_code: |
    print(question_tex)
answers_process_code: |
    print(answers_tex)
answer_explanation_process_code: |
    print(answer_explanation_tex)
question: |
    Fill [[blank_1]]
answers:
  blank_1:
    type: ShortAnswer
    hint: None
    correct_answer:
      - type: float
        value: 5
        atol: 0.0001
        rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_COMMENTS = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
background_code: |
    from io import BytesIO
    import pickle
    import json
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")
    exec(prog)
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")
    exec(jinja_env)
    template_file = data_files[
        "question-data/random-page-test/test_template.tex"].decode("utf8")
    template = latex_jinja_env.from_string(template_file)
    bio = BytesIO(data_files["question_data"])
    d = pickle.load(bio)
    o = PlusFirstElement(**d)
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])
    answer = o.solve()
    display_latex = False
    display_markdown = True
    blank_description = (
        u"the result:"
    )
    pre_description = u"What is the result?"
    prompt_tex = template.render(
        show_question=True,
        show_answer=False,
        pre_description=pre_description,
        display_latex=display_latex,
        q=q,
    )
    if display_markdown:
        prompt_tex += "[prompt](http://prompt.example.com)"
    question_tex = template.render(
        show_question=False,
        show_answer=False,
        blank_description=blank_description,
        display_latex=display_latex,
        show_blank=True,
        q=q,
    )
    if display_markdown:
        question_tex += "[question](http://question.example.com)"
    answers_tex = template.render(
        show_question=False,
        show_answer=False,
        show_blank_answer=True,
        blank_description=blank_description,
        display_latex=display_latex,
        q=q,
        answer=answer,
    )
    answer_explanation_tex = template.render(
        show_answer_explanation=True,
        answer="$%s$" % answer,
    )
    if display_markdown:
        answer_explanation_tex += "[explanation](http://explanation.example.com)"
prompt_process_code: |
    # comment1
    print(prompt_tex)
question_process_code: |
    # comment2
    print(question_tex)
answers_process_code: |
    # comment3
    print(answers_tex)
answer_explanation_process_code: |
    # comment4
    print(answer_explanation_tex)
question: |
    Fill [[blank_1]]
answers:
  blank_1:
    type: ShortAnswer
    hint: None
    correct_answer:
      - type: float
        value: 5
        atol: 0.0001
        rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_MORE_THAN_COMMENTS = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
background_code: |
    from io import BytesIO
    import pickle
    import json
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")
    exec(prog)
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")
    exec(jinja_env)
    template_file = data_files[
        "question-data/random-page-test/test_template.tex"].decode("utf8")
    template = latex_jinja_env.from_string(template_file)
    bio = BytesIO(data_files["question_data"])
    d = pickle.load(bio)
    o = PlusFirstElement(**d)
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])
    answer = o.solve()
    display_latex = False
    display_markdown = True
    blank_description = (
        u"the result:"
    )
    pre_description = u"What is the result?"
    prompt_tex = template.render(
        show_question=True,
        show_answer=False,
        pre_description=pre_description,
        display_latex=display_latex,
        # comment 5: this is more than comment, because we removed a comma
        q=q
    )
    if display_markdown:
        prompt_tex += "[prompt](http://prompt.example.com)"
    question_tex = template.render(
        show_question=False,
        show_answer=False,
        blank_description=blank_description,
        display_latex=display_latex,
        show_blank=True,
        q=q,
    )
    if display_markdown:
        question_tex += "[question](http://question.example.com)"
    answers_tex = template.render(
        show_question=False,
        show_answer=False,
        show_blank_answer=True,
        blank_description=blank_description,
        display_latex=display_latex,
        q=q,
        answer=answer,
    )
    answer_explanation_tex = template.render(
        show_answer_explanation=True,
        answer="$%s$" % answer,
    )
    if display_markdown:
        answer_explanation_tex += "[explanation](http://explanation.example.com)"
prompt_process_code: |
    # comment1
    print(prompt_tex)
question_process_code: |
    # comment2
    print(question_tex)
answers_process_code: |
    # comment3
    print(answers_tex)
answer_explanation_process_code: |
    # comment4
    print(answer_explanation_tex)
question: |
    Fill [[blank_1]]
answers:
  blank_1:
    type: ShortAnswer
    hint: None
    correct_answer:
      - type: float
        value: 5
        atol: 0.0001
        rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
background_code: |
    from io import BytesIO
    import pickle
    import json
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")
    exec(prog)
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")
    exec(jinja_env)
    template_file = data_files[
        "question-data/random-page-test/test_template.tex"].decode("utf8")
    template = latex_jinja_env.from_string(template_file)
    bio = BytesIO(data_files["question_data"])
    d = pickle.load(bio)
    o = PlusFirstElement(**d)
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])
    answer = o.solve()
    display_latex = False
    display_markdown = True
    blank_description = (
        u"the result:"
    )
    pre_description = u"What is the result?"
    prompt_tex = template.render(
        show_question=True,
        show_answer=False,
        pre_description=pre_description,
        display_latex=display_latex,
        q=q,
    )
    if display_markdown:
        prompt_tex += "[prompt](http://prompt.example.com)"
    question_tex = template.render(
        show_question=False,
        show_answer=False,
        blank_description=blank_description,
        display_latex=display_latex,
        show_blank=True,
        q=q,
    )
    if display_markdown:
        question_tex += "[question](http://question.example.com)"
    answers_tex = template.render(
        show_question=False,
        show_answer=False,
        show_blank_answer=True,
        blank_description=blank_description,
        display_latex=display_latex,
        q=q,
        answer=answer,
    )
    answer_explanation_tex = template.render(
        show_answer_explanation=True,
        answer="$%s$" % answer,
    )
    if display_markdown:
        answer_explanation_tex += "[explanation](http://explanation.example.com)"
    class PromptProcessCodeException(Exception):
        pass
    class QuestionProcessCodeException(Exception):
        pass
    class AnswersProcessCodeException(Exception):
        pass
    class AnswerExplanationProcessCodeException(Exception):
        pass
    error_info = "test exception"
prompt_process_code: |
    #raise PromptProcessCodeException(error_info)
    print(prompt_tex)
question_process_code: |
    #raise QuestionProcessCodeException(error_info)
    print(question_tex)
answers_process_code: |
    #raise AnswersProcessCodeException(error_info)
    print(answers_tex)
answer_explanation_process_code: |
    #raise AnswerExplanationProcessCodeException(error_info)
    print(answer_explanation_tex)
question: |
    Fill [[blank_1]]
answers:
  blank_1:
    type: ShortAnswer
    hint: None
    correct_answer:
      - type: float
        value: 5
        atol: 0.0001
        rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data.bin
background_code: |
    from io import BytesIO
    import pickle
    import json
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")
    exec(prog)
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")
    exec(jinja_env)
    template_file = data_files[
        "question-data/random-page-test/test_template.tex"].decode("utf8")
    template = latex_jinja_env.from_string(template_file)
    bio = BytesIO(data_files["question_data"])
    d = pickle.load(bio)
    o = PlusFirstElement(**d)
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])
    answer = o.solve()
    display_latex = False
    display_markdown = True
    blank_description = (
        u"the result:"
    )
    pre_description = u"What is the result?"
    prompt_tex = template.render(
        show_question=True,
        show_answer=False,
        pre_description=pre_description,
        display_latex=display_latex,
        q=q,
    )
    if display_markdown:
        prompt_tex += "[prompt](http://prompt.example.com)"
    question_tex = template.render(
        show_question=False,
        show_answer=False,
        blank_description=blank_description,
        display_latex=display_latex,
        show_blank=True,
        q=q,
    )
    if display_markdown:
        question_tex += "[question](http://question.example.com)"
    answers_tex = template.render(
        show_question=False,
        show_answer=False,
        show_blank_answer=True,
        blank_description=blank_description,
        display_latex=display_latex,
        q=q,
        answer=answer,
    )
    answer_explanation_tex = template.render(
        show_answer_explanation=True,
        answer="$%s$" % answer,
    )
    if display_markdown:
        answer_explanation_tex += "[explanation](http://explanation.example.com)"
prompt_process_code: |
    print(prompt_tex)
question_process_code: |
    print(question_tex)
answers_process_code: |
    print(answers_tex)
answer_explanation_process_code: |
    print(answer_explanation_tex)
question: |
    Fill [[blank_1]]
answers:
  blank_1:
    type: ShortAnswer
    hint: None
    correct_answer:
      - type: float
        value: 5
        atol: 0.0001
        rtol: 0.0001
answer_explanation: |
    Nothing
"""


LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE = """
type: LatexRandomCodeInlineMultiQuestion
id: rand
value: 3
access_rules:
    add_permissions:
        - see_correctness
        - change_answer
prompt: |
    # random question test
data_files:
    - question-data/random-page-test/jinja_env.py
    - question-data/random-page-test/pyprog.py
    - question-data/random-page-test/test_data_01.bin
    - question-data/random-page-test/test_random_runpy.py
    - question-data/random-page-test/test_template.tex
excluded_cache_key_files:
    - question-data/random-page-test/pyprog.py
random_question_data_file: question-data/random-page-test/test_data_01.bin
full_process_code: |
    from io import BytesIO
    import pickle
    import json
    try:
        runpy_context
    except NameError:
        runpy_context = {}
    prog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")
    exec(prog)
    jinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")
    exec(jinja_env)
    template_file = data_files[
        "question-data/random-page-test/test_template.tex"].decode("utf8")
    template = latex_jinja_env.from_string(template_file)
    bio = BytesIO(data_files["question_data"])
    d = pickle.load(bio)
    o = PlusFirstElement(**d)
    q = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])
    answer = o.solve()
    display_latex = runpy_context.get("display_latex", False)
    display_markdown = runpy_context.get("display_markdown", False)
    blank_description = (
        u"the result:"
    )
    pre_description = runpy_context.get("pre_description", u"What is the result?")
    prompt_tex = template.render(
        show_question=True,
        show_answer=False,
        pre_description=pre_description,
        display_latex=display_latex,
        q=q,
    )
    if display_markdown:
        prompt_tex += "[prompt](http://prompt.example.com)"
    feed_back_dict = {}
    feed_back_dict.update({"prompt": prompt_tex})
    question_tex = template.render(
        show_question=False,
        show_answer=False,
        blank_description=blank_description,
        display_latex=display_latex,
        show_blank=True,
        q=q,
    )
    if display_markdown:
        question_tex += "[question](http://question.example.com)"
    feed_back_dict.update({"question": question_tex})
    answers_tex = template.render(
        show_question=False,
        show_answer=False,
        show_blank_answer=True,
        blank_description=blank_description,
        display_latex=display_latex,
        q=q,
        answer=answer,
    )
    feed_back_dict.update({"answers": answers_tex})
    answer_explanation_tex = template.render(
        show_answer_explanation=True,
        answer="$%s$" % answer,
    )
    if display_markdown:
        answer_explanation_tex += "[explanation](http://explanation.example.com)"
    feed_back_dict.update({"answer_explanation": answer_explanation_tex})
    feedback.add_feedback(json.dumps(feed_back_dict))
question: |
    Fill [[blank_1]]
answers:
    blank_1:
        type: ShortAnswer
        hint: None
        correct_answer:
        - type: float
          value: 5
          atol: 0.0001
          rtol: 0.0001
answer_explanation: |
    Nothing
"""
