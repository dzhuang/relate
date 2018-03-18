# -*- coding: utf-8 -*-

import os
from collections import namedtuple

QUIZ_FLOW_ID = "quiz-test"
MESSAGE_ANSWER_SAVED_TEXT = "Answer saved."
MESSAGE_ANSWER_FAILED_SAVE_TEXT = "Failed to submit answer."

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures')


def get_upload_file_path(file_name, fixture_path=FIXTURE_PATH):
    return os.path.join(fixture_path, file_name)


TEST_TEXT_FILE_PATH = get_upload_file_path("test_file.txt")
TEST_PDF_FILE_PATH = get_upload_file_path("test_file.pdf")
TEST_HGTEXT_MARKDOWN_ANSWER = u"""
type: ChoiceQuestion
id: myquestion
shuffle: True
prompt: |

    # What is a quarter?

choices:

  - "1"
  - "2"
  - ~CORRECT~ 1/4
  - ~CORRECT~ $\\frac{1}{4}$
  - 四分之三
"""
TEST_HGTEXT_MARKDOWN_ANSWER_WRONG = u"""
type: ChoiceQuestion
id: myquestion
shuffle: True
prompt: |

    # What is a quarter?

choices:

  - "1"
  - "2"
  - 1/4
  - $\\frac{1}{4}$
  - 四分之三
"""
PageTuple = namedtuple(
    'PageTuple', [
        'page_id',
        'group_id',
        'need_human_grade',
        'expecting_grade',
        'need_runpy',
        'correct_answer',
        'grade_data',
        'full_points',
        'dl_file_extension',
    ]
)
TEST_AUDIO_OUTPUT_ANSWER = """
import numpy as np
t = np.linspace(0, 1, sample_rate, endpoint=False)
signal = np.sin(2*np.pi*t * 440)

output_audio(signal)
"""
TEST_PAGE_TUPLE = (
    PageTuple("welcome", "intro", False, False, False, None, {}, None, None),
    PageTuple("half", "quiz_start", False, True, False, {"answer": '0.5'}, {}, 5,
              ".txt"),
    PageTuple("krylov", "quiz_start", False, True, False, {"choice": ['0']}, {}, 2,
              ".json"),
    PageTuple("ice_cream_toppings", "quiz_start", False, True, False,
              {"choice": ['0', '1', '4']}, {}, 1, ".json"),
    PageTuple("matrix_props", "quiz_start", False, True, False,
              {"choice": ['0', '3']}, {}, 1, ".json"),
    PageTuple("inlinemulti", "quiz_start", False, True, False,
              {'blank1': 'Bar', 'blank_2': '0.2', 'blank3': '1',
               'blank4': '5', 'blank5': 'Bar', 'choice2': '0',
               'choice_a': '0'}, {}, 10, ".json"),
    PageTuple("fear", "quiz_start", True, False, False, {"answer": "NOTHING!!!"},
              {}, 0, ".txt"),
    PageTuple("age_group", "quiz_start", True, False, False, {"choice": 3}, {}, 0,
              ".json"),
    PageTuple("hgtext", "quiz_tail", True, True, False,
              {"answer": TEST_HGTEXT_MARKDOWN_ANSWER},
              {"grade_percent": "100", "released": "on"}, 5, ".txt"),
    PageTuple("addition", "quiz_tail", False, True, True, {"answer": 'c = b + a\r'},
              {"grade_percent": "100", "released": "on"}, 1, ".py"),
    PageTuple("pymult", "quiz_tail", True, True, True, {"answer": 'c = a * b\r'},
              {"grade_percent": "100", "released": "on"}, None, ".py"),
    PageTuple("neumann", "quiz_tail", False, True, False, {"answer": "1/(1-A)"}, {},
              5, ".txt"),
    PageTuple("py_simple_list", "quiz_tail", True, True, True,
              {"answer": 'b = [a] * 50\r'},
              {"grade_percent": "100", "released": "on"}, 4, ".py"),

    # Skipped
    # PageTuple("test_audio_output", "quiz_tail", True, True, True,
    #           {"answer": TEST_AUDIO_OUTPUT_ANSWER}, {}, 1),

    PageTuple("quarter", "quiz_tail", False, True, False, {"answer": ['0.25']},
              {}, 0, ".txt"),
    PageTuple("anyup", "quiz_tail", True, False, False,
              {"uploaded_file": TEST_TEXT_FILE_PATH},
              {"grade_percent": "100", "released": "on"}, 5, None),
    PageTuple("proof", "quiz_tail", True, False, False,
              {"uploaded_file": TEST_PDF_FILE_PATH},
              {"grade_percent": "100", "released": "on"}, 5, ".pdf"),
    PageTuple("eigvec", "quiz_tail", False, True, False, {"answer": 'matrix'}, {},
              2, ".txt"),
    PageTuple("lsq", "quiz_tail", False, True, False, {"choice": ['2']}, {}, 1,
              ".json"),
)
PAGE_WARNINGS = "page_warnings"
PAGE_ERRORS = "page_errors"
HAVE_VALID_PAGE = "have_valid_page"
