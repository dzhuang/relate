import six
import json
from collections import OrderedDict
from image_upload.page.latexpage import b64_pickled_bytes_to_data, \
    deep_convert_ordereddict
from image_upload.utils import deep_convert_ordereddict, deep_eq
from json.decoder import JSONDecodeError
from copy import deepcopy

question_data1 = 'gANjY29sbGVjdGlvbnMKT3JkZXJlZERpY3QKcQApUnEBKFgFAAAAYXJyYXlxAmNudW1weS5jb3JlLm11bHRpYXJyYXkKX3JlY29uc3RydWN0CnEDY251bXB5Cm5kYXJyYXkKcQRLAIVxBUMBYnEGh3EHUnEIKEsBSwFLA4ZxCWNudW1weQpkdHlwZQpxClgCAAAAZjhxC0sASwGHcQxScQ0oSwNYAQAAADxxDk5OTkr/////Sv////9LAHRxD2KJQxgAAAAAAAAYQAAAAAAAAPh/zczMzMzMIUBxEHRxEWJYAwAAAG1hdHESaANjbnVtcHkubWF0cml4bGliLmRlZm1hdHJpeAptYXRyaXgKcRNLAIVxFGgGh3EVUnEWKEsBSwJLAoZxF2gNiUMgAAAAAAAAAEAAAAAAAAD4fwAAAAAAABBAAAAAAAAAFEBxGHRxGWJYAQAAAHhxGksBdS4='
question_data2 = 'gANjY29sbGVjdGlvbnMKT3JkZXJlZERpY3QKcQApUnEBKFgFAAAAYXJyYXlxAmNudW1weS5jb3JlLm11bHRpYXJyYXkKX3JlY29uc3RydWN0CnEDY251bXB5Cm5kYXJyYXkKcQRLAIVxBUMBYnEGh3EHUnEIKEsBSwFLA4ZxCWNudW1weQpkdHlwZQpxClgCAAAAZjhxC0sASwGHcQxScQ0oSwNYAQAAADxxDk5OTkr/////Sv////9LAHRxD2KJQxgAAAAAAABOQAAAAAAAAPh/mpmZmZk5VEBxEHRxEWJYAwAAAG1hdHESaANjbnVtcHkubWF0cml4bGliLmRlZm1hdHJpeAptYXRyaXgKcRNLAIVxFGgGh3EVUnEWKEsBSwJLAoZxF2gNiUMgAAAAAAAANEAAAAAAAAD4fwAAAAAAAERAAAAAAAAASUBxGHRxGWJYAQAAAHhxGksKdS4='
py_prog_b64 = 'aW1wb3J0IG51bXB5IGFzIG5wCgpjbGFzcyBQbHVzRmlyc3RFbGVtZW50KG9iamVjdCk6CiAgICBkZWYgX19pbml0X18oc2VsZiwgeCwgbWF0LCBhcnJheSk6CiAgICAgICAgc2VsZi54ID0gaW50KHgpCiAgICAgICAgc2VsZi55ID0gaW50KG1hdFswLCAwXSkKICAgICAgICBzZWxmLnogPSBpbnQoYXJyYXlbMCwgMF0pCgogICAgZGVmIHNvbHZlKHNlbGYpOgogICAgICAgIHJldHVybiBzZWxmLnggKyBzZWxmLnkgKyBzZWxmLnoK'
jinja_env_b64 = 'aW1wb3J0IGppbmphMgpmcm9tIGppbmphMiBpbXBvcnQgVGVtcGxhdGUKCmxhdGV4X2ppbmphX2VudiA9IGppbmphMi5FbnZpcm9ubWVudCgKICAgIGJsb2NrX3N0YXJ0X3N0cmluZyA9ICdcQkxPQ0t7JywKICAgIGJsb2NrX2VuZF9zdHJpbmcgPSAnfScsCiAgICB2YXJpYWJsZV9zdGFydF9zdHJpbmcgPSAnXFZBUnsnLAogICAgdmFyaWFibGVfZW5kX3N0cmluZyA9ICd9JywKICAgIGNvbW1lbnRfc3RhcnRfc3RyaW5nID0gJ1wjeycsCiAgICBjb21tZW50X2VuZF9zdHJpbmcgPSAnfScsCiAgICBsaW5lX3N0YXRlbWVudF9wcmVmaXggPSAnJSUnLAogICAgbGluZV9jb21tZW50X3ByZWZpeCA9ICclIycsCiAgICB0cmltX2Jsb2NrcyA9IFRydWUsCiAgICBhdXRvZXNjYXBlID0gRmFsc2UKKQ=='
runpy_file_b64 = 'ZnJvbSBpbyBpbXBvcnQgQnl0ZXNJTwppbXBvcnQgcGlja2xlCmltcG9ydCBqc29uCgp0cnk6CiAgICBydW5weV9jb250ZXh0CmV4Y2VwdCBOYW1lRXJyb3I6CiAgICBydW5weV9jb250ZXh0ID0ge30KCnByb2cgPSBkYXRhX2ZpbGVzWyJxdWVzdGlvbi1kYXRhL3JhbmRvbS1wYWdlLXRlc3QvcHlwcm9nLnB5Il0uZGVjb2RlKCJ1dGY4IikKZXhlYyhwcm9nKQpqaW5qYV9lbnYgPSBkYXRhX2ZpbGVzWyJxdWVzdGlvbi1kYXRhL3JhbmRvbS1wYWdlLXRlc3QvamluamFfZW52LnB5Il0uZGVjb2RlKCJ1dGY4IikKZXhlYyhqaW5qYV9lbnYpCnRlbXBsYXRlX2ZpbGUgPSBkYXRhX2ZpbGVzWwogICAgInF1ZXN0aW9uLWRhdGEvcmFuZG9tLXBhZ2UtdGVzdC90ZXN0X3RlbXBsYXRlLnRleCJdLmRlY29kZSgidXRmOCIpCnRlbXBsYXRlID0gbGF0ZXhfamluamFfZW52LmZyb21fc3RyaW5nKHRlbXBsYXRlX2ZpbGUpCmJpbyA9IEJ5dGVzSU8oZGF0YV9maWxlc1sicXVlc3Rpb25fZGF0YSJdKQoKZCA9IHBpY2tsZS5sb2FkKGJpbykKCm8gPSBQbHVzRmlyc3RFbGVtZW50KCoqZCkKcSA9ICIkJXM9JCIgJSAiICsgIi5qb2luKFtzdHIoaSkgZm9yIGkgaW4gW28ueCwgby55LCBvLnpdXSkKYW5zd2VyID0gby5zb2x2ZSgpCgpkaXNwbGF5X2xhdGV4ID0gcnVucHlfY29udGV4dC5nZXQoImRpc3BsYXlfbGF0ZXgiLCBGYWxzZSkKZGlzcGxheV9tYXJrZG93biA9IHJ1bnB5X2NvbnRleHQuZ2V0KCJkaXNwbGF5X21hcmtkb3duIiwgRmFsc2UpCgpibGFua19kZXNjcmlwdGlvbiA9ICgKICAgIHUidGhlIHJlc3VsdDoiCikKCnByZV9kZXNjcmlwdGlvbiA9IHJ1bnB5X2NvbnRleHQuZ2V0KCJwcmVfZGVzY3JpcHRpb24iLCB1IldoYXQgaXMgdGhlIHJlc3VsdD8iKQoKcHJvbXB0X3RleCA9IHRlbXBsYXRlLnJlbmRlcigKICAgIHNob3dfcXVlc3Rpb249VHJ1ZSwKICAgIHNob3dfYW5zd2VyPUZhbHNlLAogICAgcHJlX2Rlc2NyaXB0aW9uPXByZV9kZXNjcmlwdGlvbiwKICAgIGRpc3BsYXlfbGF0ZXg9ZGlzcGxheV9sYXRleCwKICAgIHE9cSwKKQppZiBkaXNwbGF5X21hcmtkb3duOgogICAgcHJvbXB0X3RleCArPSAiW3Byb21wdF0oaHR0cDovL3Byb21wdC5leGFtcGxlLmNvbSkiCmZlZWRfYmFja19kaWN0ID0ge30KZmVlZF9iYWNrX2RpY3QudXBkYXRlKHsicHJvbXB0IjogcHJvbXB0X3RleH0pCgpxdWVzdGlvbl90ZXggPSB0ZW1wbGF0ZS5yZW5kZXIoCiAgICBzaG93X3F1ZXN0aW9uPUZhbHNlLAogICAgc2hvd19hbnN3ZXI9RmFsc2UsCiAgICBibGFua19kZXNjcmlwdGlvbj1ibGFua19kZXNjcmlwdGlvbiwKICAgIGRpc3BsYXlfbGF0ZXg9ZGlzcGxheV9sYXRleCwKICAgIHNob3dfYmxhbms9VHJ1ZSwKICAgIHE9cSwKKQppZiBkaXNwbGF5X21hcmtkb3duOgogICAgcXVlc3Rpb25fdGV4ICs9ICJbcXVlc3Rpb25dKGh0dHA6Ly9xdWVzdGlvbi5leGFtcGxlLmNvbSkiCmZlZWRfYmFja19kaWN0LnVwZGF0ZSh7InF1ZXN0aW9uIjogcXVlc3Rpb25fdGV4fSkKCmFuc3dlcnNfdGV4ID0gdGVtcGxhdGUucmVuZGVyKAogICAgc2hvd19xdWVzdGlvbj1GYWxzZSwKICAgIHNob3dfYW5zd2VyPUZhbHNlLAogICAgc2hvd19ibGFua19hbnN3ZXI9VHJ1ZSwKICAgIGJsYW5rX2Rlc2NyaXB0aW9uPWJsYW5rX2Rlc2NyaXB0aW9uLAogICAgZGlzcGxheV9sYXRleD1kaXNwbGF5X2xhdGV4LAogICAgcT1xLAogICAgYW5zd2VyPWFuc3dlciwKKQpmZWVkX2JhY2tfZGljdC51cGRhdGUoeyJhbnN3ZXJzIjogYW5zd2Vyc190ZXh9KQoKYW5zd2VyX2V4cGxhbmF0aW9uX3RleCA9IHRlbXBsYXRlLnJlbmRlcigKICAgIHNob3dfYW5zd2VyX2V4cGxhbmF0aW9uPVRydWUsCiAgICBhbnN3ZXI9IiQlcyQiICUgYW5zd2VyLAopCmlmIGRpc3BsYXlfbWFya2Rvd246CiAgICBhbnN3ZXJfZXhwbGFuYXRpb25fdGV4ICs9ICJbZXhwbGFuYXRpb25dKGh0dHA6Ly9leHBsYW5hdGlvbi5leGFtcGxlLmNvbSkiCmZlZWRfYmFja19kaWN0LnVwZGF0ZSh7ImFuc3dlcl9leHBsYW5hdGlvbiI6IGFuc3dlcl9leHBsYW5hdGlvbl90ZXh9KQpmZWVkYmFjay5hZGRfZmVlZGJhY2soanNvbi5kdW1wcyhmZWVkX2JhY2tfZGljdCkp'
latex_template_b64 = 'XEJMT0NLey0gaWYgc2hvd19xdWVzdGlvbiAtfQpcQkxPQ0t7LSBpZiBwcmVfZGVzY3JpcHRpb24gLX0KXFZBUntwcmVfZGVzY3JpcHRpb259ClxCTE9DS3stIGVuZGlmIC19IFwjeyBwcmVfZGVzY3JpcHRpb24gfQoKXEJMT0NLey0gaWYgbm90IGRpc3BsYXlfbGF0ZXggLX0KXFZBUntxfQpcQkxPQ0t7LSBlbHNlIC19CjxwIGFsaWduPSJtaWRkbGUiPgp7JSBjYWxsIGxhdGV4KGNvbXBpbGVyPSJwZGZsYXRleCIsIGltYWdlX2Zvcm1hdD0icG5nIikgICV9Clxkb2N1bWVudGNsYXNze2FydGljbGV9Clx1c2VwYWNrYWdlW3V0Zjhde2lucHV0ZW5jfQpcYmVnaW57ZG9jdW1lbnR9ClxMYVRlWCBcVkFSe3F9ClxlbmR7ZG9jdW1lbnR9CnslIGVuZGNhbGwgJX0KPC9wPgpcQkxPQ0t7LSBlbmRpZiAtfQoKXEJMT0NLey0gZW5kaWYgLX0gXCN7IHNob3dfcXVlc3Rpb24gfQoKXEJMT0NLeyBpZiBzaG93X2JsYW5rIC19ClxWQVJ7YmxhbmtfZGVzY3JpcHRpb259W1tibGFuazFdXQpcQkxPQ0t7IGVuZGlmIC19IFwjeyBhZnRlcl9kZXNjcmlwdGlvbiB9CgpcQkxPQ0t7IGlmIHNob3dfYmxhbmtfYW5zd2VyIH0KYmxhbmsxOgogICAgdHlwZTogU2hvcnRBbnN3ZXIKICAgIHdpZHRoOiAxMGVtCiAgICBoaW50OiBzb21lIGhpbnQKICAgIGNvcnJlY3RfYW5zd2VyOgogICAgLSB0eXBlOiBmbG9hdAogICAgICBydG9sOiAwLjAxCiAgICAgIGF0b2w6IDAuMDEKICAgICAgdmFsdWU6ICJcVkFSe2Fuc3dlcn0iClxCTE9DS3sgZW5kaWYgLX0gXCN7IGFmdGVyX2Rlc2NyaXB0aW9uIH0KClxCTE9DS3tpZiBzaG93X2Fuc3dlcl9leHBsYW5hdGlvbn0KXFZBUnthbnN3ZXJ9ClxCTE9DS3sgZW5kaWYgLX0='
latex_template_changed_b64 = 'XEJMT0NLey0gaWYgc2hvd19xdWVzdGlvbiAtfQpcQkxPQ0t7LSBpZiBwcmVfZGVzY3JpcHRpb24gLX0KXFZBUntwcmVfZGVzY3JpcHRpb259ClxCTE9DS3stIGVuZGlmIC19IFwjeyBwcmVfZGVzY3JpcHRpb24gfQoKXEJMT0NLey0gaWYgbm90IGRpc3BsYXlfbGF0ZXggLX0KXFZBUntxfQpcQkxPQ0t7LSBlbHNlIC19CjxwIGFsaWduPSJtaWRkbGUiPgp7JSBjYWxsIGxhdGV4KGNvbXBpbGVyPSJwZGZsYXRleCIsIGltYWdlX2Zvcm1hdD0icG5nIikgICV9Clxkb2N1bWVudGNsYXNze2FydGljbGV9Clx1c2VwYWNrYWdlW3V0Zjhde2lucHV0ZW5jfQpcYmVnaW57ZG9jdW1lbnR9ClxMYVRlWCBcVkFSe3F9ClxlbmR7ZG9jdW1lbnR9CnslIGVuZGNhbGwgJX0KPC9wPgpcQkxPQ0t7LSBlbmRpZiAtfQoKXEJMT0NLey0gZW5kaWYgLX0gXCN7IHNob3dfcXVlc3Rpb24gfQoKXEJMT0NLeyBpZiBzaG93X2JsYW5rIC19ClxWQVJ7YmxhbmtfZGVzY3JpcHRpb259W1tibGFuazFdXQpcQkxPQ0t7IGVuZGlmIC19IFwjeyBhZnRlcl9kZXNjcmlwdGlvbiB9CgpcQkxPQ0t7IGlmIHNob3dfYmxhbmtfYW5zd2VyIH0KYmxhbmsxOgogICAgdHlwZTogU2hvcnRBbnN3ZXIKICAgIHdpZHRoOiAxMGVtCiAgICBoaW50OiBzb21lIGhpbnQKICAgIGNvcnJlY3RfYW5zd2VyOgogICAgLSB0eXBlOiBmbG9hdAogICAgICBydG9sOiAwLjAxCiAgICAgIGF0b2w6IDAuMDEKICAgICAgdmFsdWU6ICJcVkFSe2Fuc3dlcn0iClxCTE9DS3sgZW5kaWYgLX0gXCN7IGFmdGVyX2Rlc2NyaXB0aW9uIH0KClxCTE9DS3tpZiBzaG93X2Fuc3dlcl9leHBsYW5hdGlvbn0KVGhlIGNvcnJlY3QgYW5zd2VyIGlzOiBcVkFSe2Fuc3dlcn0KXEJMT0NLeyBlbmRpZiAtfQ=='
latex_template_failed_b64 = 'XEJMT0NLey0gaWYgc2hvd19xdWVzdGlvbiAtfQpcQkxPQ0t7LSBpZiBwcmVfZGVzY3JpcHRpb24gLX0KXFZBUntwcmVfZGVzY3JpcHRpb259ClxCTE9DS3stIGVuZGlmIC19IFwjeyBwcmVfZGVzY3JpcHRpb24gfQoKXEJMT0NLey0gaWYgbm90IGRpc3BsYXlfbGF0ZXggLX0KXFZBUntxfQpcQkxPQ0t7LSBlbHNlIC19CjxwIGFsaWduPSJtaWRkbGUiPgp7JSBjYWxsIGxhdGV4KGNvbXBpbGVyPSJwZGZsYXRleCIsIGltYWdlX2Zvcm1hdD0icG5nIikgICV9Clxkb2N1bWVudGNsYXNze2FydGljbGV9Clx1c2VwYWNrYWdlW3V0Zjhde2lucHV0ZW5jfQpcYmVnaW57ZG9jdW1lbnR9ClxMYXRleCBcVkFSe3F9ClxlbmR7ZG9jdW1lbnR9CnslIGVuZGNhbGwgJX0KPC9wPgpcQkxPQ0t7LSBlbmRpZiAtfQoKXEJMT0NLey0gZW5kaWYgLX0gXCN7IHNob3dfcXVlc3Rpb24gfQoKXEJMT0NLeyBpZiBzaG93X2JsYW5rIC19ClxWQVJ7YmxhbmtfZGVzY3JpcHRpb259W1tibGFuazFdXQpcQkxPQ0t7IGVuZGlmIC19IFwjeyBhZnRlcl9kZXNjcmlwdGlvbiB9CgpcQkxPQ0t7IGlmIHNob3dfYmxhbmtfYW5zd2VyIH0KYmxhbmsxOgogICAgdHlwZTogU2hvcnRBbnN3ZXIKICAgIHdpZHRoOiAxMGVtCiAgICBoaW50OiBzb21lIGhpbnQKICAgIGNvcnJlY3RfYW5zd2VyOgogICAgLSB0eXBlOiBmbG9hdAogICAgICBydG9sOiAwLjAxCiAgICAgIGF0b2w6IDAuMDEKICAgICAgdmFsdWU6ICJcVkFSe2Fuc3dlcn0iClxCTE9DS3sgZW5kaWYgLX0gXCN7IGFmdGVyX2Rlc2NyaXB0aW9uIH0KClxCTE9DS3tpZiBzaG93X2Fuc3dlcl9leHBsYW5hdGlvbn0KXFZBUnthbnN3ZXJ9ClxCTE9DS3sgZW5kaWYgLX0='


def get_question_data_converted(runpy_req):
    runpy_req = deepcopy(runpy_req)
    if "question_data" in runpy_req["data_files"]:
        question_data = b64_pickled_bytes_to_data(
            runpy_req["data_files"]["question_data"])
        runpy_req["data_files"]["question_data"] = question_data
    return deep_convert_ordereddict(runpy_req)


def get_feedback_ordered(response_dict):
    response_dict = deepcopy(response_dict)
    if "feedback" in six.iterkeys(response_dict):
        feedback = response_dict["feedback"]
        try:
            feedback[0] = json.dumps(
                deep_convert_ordereddict(json.loads(feedback[0])))
            response_dict["feedback"] = feedback
        except JSONDecodeError:
            pass

    return deep_convert_ordereddict(response_dict)


rand1_req = get_question_data_converted(
    {'user_code': '', 'data_files': {
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question_data': question_data1},
     'compile_only': False,
     'setup_code': "runpy_context = {}\nexec(data_files['question-data/random-page-test/test_random_runpy.py'].decode('utf-8'))"}
)

rand1_response = get_feedback_ordered(
    {'feedback': [
        '{"answer_explanation": "\\n\\n\\n$9$\\n", "question": "\\nthe result:[[blank1]]\\n\\n\\n", "prompt": "What is the result?$1 + 2 + 6=$\\n\\n\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"9\\"\\n\\n"}',
        'Execution time: 0.2 s -- Time limit: 5.0 s'], 'stderr': '',
        'result': 'success',
        'exec_host': 'localhost', 'stdout': '',
        'points': None, 'html': []})

rand2_req = get_question_data_converted(
    {
        'user_code': '', 'data_files': {
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question_data': question_data2},
        'compile_only': False,
        'setup_code': "runpy_context = {}\nexec(data_files['question-data/random-page-test/test_random_runpy.py'].decode('utf-8'))"})

rand2_response = get_feedback_ordered(
    {'feedback': [
        '{"question": "\\nthe result:[[blank1]]\\n\\n\\n", "prompt": "What is the result?$10 + 20 + 60=$\\n\\n\\n", "answer_explanation": "\\n\\n\\n$90$\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"90\\"\\n\\n"}',
        'Execution time: 0.2 s -- Time limit: 5.0 s'], 'stdout': '',
        'exec_host': 'localhost',
        'html': [],
        'result': 'success',
        'points': None,
        'stderr': ''})

rand_macro_success_req = get_question_data_converted(
    {'compile_only': False,
     'setup_code': "runpy_context = {'display_latex': True}\nexec(data_files['question-data/random-page-test/test_random_runpy_with_failed_macro.py'].decode('utf-8'))",
     'user_code': '',
     'data_files': {
         'question_data': question_data2,
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template_fail.tex': latex_template_failed_b64,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy_with_failed_macro.py': 'ZnJvbSBpbyBpbXBvcnQgQnl0ZXNJTwppbXBvcnQgcGlja2xlCmltcG9ydCBqc29uCgp0cnk6CiAgICBydW5weV9jb250ZXh0CmV4Y2VwdCBOYW1lRXJyb3I6CiAgICBydW5weV9jb250ZXh0ID0ge30KCnByb2cgPSBkYXRhX2ZpbGVzWyJxdWVzdGlvbi1kYXRhL3JhbmRvbS1wYWdlLXRlc3QvcHlwcm9nLnB5Il0uZGVjb2RlKCJ1dGY4IikKZXhlYyhwcm9nKQpqaW5qYV9lbnYgPSBkYXRhX2ZpbGVzWyJxdWVzdGlvbi1kYXRhL3JhbmRvbS1wYWdlLXRlc3QvamluamFfZW52LnB5Il0uZGVjb2RlKCJ1dGY4IikKZXhlYyhqaW5qYV9lbnYpCnRlbXBsYXRlX2ZpbGUgPSBkYXRhX2ZpbGVzWwogICAgInF1ZXN0aW9uLWRhdGEvcmFuZG9tLXBhZ2UtdGVzdC90ZXN0X3RlbXBsYXRlX2ZhaWwudGV4Il0uZGVjb2RlKCJ1dGY4IikKdGVtcGxhdGUgPSBsYXRleF9qaW5qYV9lbnYuZnJvbV9zdHJpbmcodGVtcGxhdGVfZmlsZSkKYmlvID0gQnl0ZXNJTyhkYXRhX2ZpbGVzWyJxdWVzdGlvbl9kYXRhIl0pCgpkID0gcGlja2xlLmxvYWQoYmlvKQoKbyA9IFBsdXNGaXJzdEVsZW1lbnQoKipkKQpxID0gIiQlcz0kIiAlICIgKyAiLmpvaW4oW3N0cihpKSBmb3IgaSBpbiBbby54LCBvLnksIG8uel1dKQphbnN3ZXIgPSBvLnNvbHZlKCkKCmRpc3BsYXlfbGF0ZXggPSBydW5weV9jb250ZXh0LmdldCgiZGlzcGxheV9sYXRleCIsIEZhbHNlKQpkaXNwbGF5X21hcmtkb3duID0gcnVucHlfY29udGV4dC5nZXQoImRpc3BsYXlfbWFya2Rvd24iLCBGYWxzZSkKCmJsYW5rX2Rlc2NyaXB0aW9uID0gKAogICAgdSJ0aGUgcmVzdWx0OiIKKQoKcHJlX2Rlc2NyaXB0aW9uID0gcnVucHlfY29udGV4dC5nZXQoInByZV9kZXNjcmlwdGlvbiIsIHUiV2hhdCBpcyB0aGUgcmVzdWx0PyIpCgpwcm9tcHRfdGV4ID0gdGVtcGxhdGUucmVuZGVyKAogICAgc2hvd19xdWVzdGlvbj1UcnVlLAogICAgc2hvd19hbnN3ZXI9RmFsc2UsCiAgICBwcmVfZGVzY3JpcHRpb249cHJlX2Rlc2NyaXB0aW9uLAogICAgZGlzcGxheV9sYXRleD1kaXNwbGF5X2xhdGV4LAogICAgcT1xLAopCmlmIGRpc3BsYXlfbWFya2Rvd246CiAgICBwcm9tcHRfdGV4ICs9ICJbcHJvbXB0XShodHRwOi8vcHJvbXB0LmV4YW1wbGUuY29tKSIKZmVlZF9iYWNrX2RpY3QgPSB7fQpmZWVkX2JhY2tfZGljdC51cGRhdGUoeyJwcm9tcHQiOiBwcm9tcHRfdGV4fSkKCnF1ZXN0aW9uX3RleCA9IHRlbXBsYXRlLnJlbmRlcigKICAgIHNob3dfcXVlc3Rpb249RmFsc2UsCiAgICBzaG93X2Fuc3dlcj1GYWxzZSwKICAgIGJsYW5rX2Rlc2NyaXB0aW9uPWJsYW5rX2Rlc2NyaXB0aW9uLAogICAgZGlzcGxheV9sYXRleD1kaXNwbGF5X2xhdGV4LAogICAgc2hvd19ibGFuaz1UcnVlLAogICAgcT1xLAopCmlmIGRpc3BsYXlfbWFya2Rvd246CiAgICBxdWVzdGlvbl90ZXggKz0gIltxdWVzdGlvbl0oaHR0cDovL3F1ZXN0aW9uLmV4YW1wbGUuY29tKSIKZmVlZF9iYWNrX2RpY3QudXBkYXRlKHsicXVlc3Rpb24iOiBxdWVzdGlvbl90ZXh9KQoKYW5zd2Vyc190ZXggPSB0ZW1wbGF0ZS5yZW5kZXIoCiAgICBzaG93X3F1ZXN0aW9uPUZhbHNlLAogICAgc2hvd19hbnN3ZXI9RmFsc2UsCiAgICBzaG93X2JsYW5rX2Fuc3dlcj1UcnVlLAogICAgYmxhbmtfZGVzY3JpcHRpb249YmxhbmtfZGVzY3JpcHRpb24sCiAgICBkaXNwbGF5X2xhdGV4PWRpc3BsYXlfbGF0ZXgsCiAgICBxPXEsCiAgICBhbnN3ZXI9YW5zd2VyLAopCmZlZWRfYmFja19kaWN0LnVwZGF0ZSh7ImFuc3dlcnMiOiBhbnN3ZXJzX3RleH0pCgphbnN3ZXJfZXhwbGFuYXRpb25fdGV4ID0gdGVtcGxhdGUucmVuZGVyKAogICAgc2hvd19hbnN3ZXJfZXhwbGFuYXRpb249VHJ1ZSwKICAgIGFuc3dlcj0iJCVzJCIgJSBhbnN3ZXIsCikKaWYgZGlzcGxheV9tYXJrZG93bjoKICAgIGFuc3dlcl9leHBsYW5hdGlvbl90ZXggKz0gIltleHBsYW5hdGlvbl0oaHR0cDovL2V4cGxhbmF0aW9uLmV4YW1wbGUuY29tKSIKZmVlZF9iYWNrX2RpY3QudXBkYXRlKHsiYW5zd2VyX2V4cGxhbmF0aW9uIjogYW5zd2VyX2V4cGxhbmF0aW9uX3RleH0pCmZlZWRiYWNrLmFkZF9mZWVkYmFjayhqc29uLmR1bXBzKGZlZWRfYmFja19kaWN0KSk='}}
)

rand_macro_success_response = get_feedback_ordered(
    {'feedback': [
        '{"answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"90\\"\\n\\n", "question": "\\nthe result:[[blank1]]\\n\\n\\n", "prompt": "What is the result?<p align=\\"middle\\">\\n{% call latex(compiler=\\"pdflatex\\", image_format=\\"png\\")  %}\\n\\\\documentclass{article}\\n\\\\usepackage[utf8]{inputenc}\\n\\\\begin{document}\\n\\\\Latex $10 + 20 + 60=$\\n\\\\end{document}\\n{% endcall %}\\n</p>\\n\\n\\n", "answer_explanation": "\\n\\n\\n$90$\\n"}',
        'Execution time: 0.2 s -- Time limit: 5.0 s'], 'html': [],
        'result': 'success',
        'exec_host': 'localhost',
        'stderr': '',
        'stdout': '',
        'points': None}
)

rand_macro_success_req2 = get_question_data_converted(
    {'user_code': '',
     'setup_code': "runpy_context = {'display_latex': True}\nexec(data_files['question-data/random-page-test/test_random_runpy.py'].decode('utf-8'))",
     'compile_only': False, 'data_files': {
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
        'question_data': question_data1}}
)

rand_macro_success_response2 = get_feedback_ordered(
    {'stderr': '',
     'result': 'success',
     'stdout': '',
     'html': [],
     'exec_host': 'localhost',
     'feedback': [
         '{"answer_explanation": "\\n\\n\\n$9$\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"9\\"\\n\\n", "prompt": "What is the result?<p align=\\"middle\\">\\n{% call latex(compiler=\\"pdflatex\\", image_format=\\"png\\")  %}\\n\\\\documentclass{article}\\n\\\\usepackage[utf8]{inputenc}\\n\\\\begin{document}\\n\\\\LaTeX $1 + 2 + 6=$\\n\\\\end{document}\\n{% endcall %}\\n</p>\\n\\n\\n", "question": "\\nthe result:[[blank1]]\\n\\n\\n"}',
         'Execution time: 0.2 s -- Time limit: 5.0 s'], 'points': None}
)

rand_macro_fail_req = get_question_data_converted(
    {'compile_only': False,
     'setup_code': "runpy_context = {'display_latex': True}\nexec(data_files['question-data/random-page-test/test_random_runpy.py'].decode('utf-8'))",
     'user_code': '', 'data_files': {
        'question_data': question_data2,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question-data/random-page-test/test_template.tex': latex_template_b64}}
)

rand_macro_fail_response = get_feedback_ordered(
    {'feedback': [
        '{"answer_explanation": "\\n\\n\\n$90$\\n", "prompt": "What is the result?<p align=\\"middle\\">\\n{% call latex(compiler=\\"pdflatex\\", image_format=\\"png\\")  %}\\n\\\\documentclass{article}\\n\\\\usepackage[utf8]{inputenc}\\n\\\\begin{document}\\n\\\\LaTeX $10 + 20 + 60=$\\n\\\\end{document}\\n{% endcall %}\\n</p>\\n\\n\\n", "question": "\\nthe result:[[blank1]]\\n\\n\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"90\\"\\n\\n"}',
        'Execution time: 0.2 s -- Time limit: 5.0 s'],
        'html': [],
        'stderr': '',
        'exec_host': 'localhost',
        'result': 'success',
        'stdout': '',
        'points': None}
)

rand_macro_fail_req2 = get_question_data_converted(
    {'compile_only': False,
     'data_files': {
         'question_data': question_data1,
         'question-data/random-page-test/test_template_fail.tex': latex_template_failed_b64,
         'question-data/random-page-test/test_random_runpy_with_failed_macro.py': 'ZnJvbSBpbyBpbXBvcnQgQnl0ZXNJTwppbXBvcnQgcGlja2xlCmltcG9ydCBqc29uCgp0cnk6CiAgICBydW5weV9jb250ZXh0CmV4Y2VwdCBOYW1lRXJyb3I6CiAgICBydW5weV9jb250ZXh0ID0ge30KCnByb2cgPSBkYXRhX2ZpbGVzWyJxdWVzdGlvbi1kYXRhL3JhbmRvbS1wYWdlLXRlc3QvcHlwcm9nLnB5Il0uZGVjb2RlKCJ1dGY4IikKZXhlYyhwcm9nKQpqaW5qYV9lbnYgPSBkYXRhX2ZpbGVzWyJxdWVzdGlvbi1kYXRhL3JhbmRvbS1wYWdlLXRlc3QvamluamFfZW52LnB5Il0uZGVjb2RlKCJ1dGY4IikKZXhlYyhqaW5qYV9lbnYpCnRlbXBsYXRlX2ZpbGUgPSBkYXRhX2ZpbGVzWwogICAgInF1ZXN0aW9uLWRhdGEvcmFuZG9tLXBhZ2UtdGVzdC90ZXN0X3RlbXBsYXRlX2ZhaWwudGV4Il0uZGVjb2RlKCJ1dGY4IikKdGVtcGxhdGUgPSBsYXRleF9qaW5qYV9lbnYuZnJvbV9zdHJpbmcodGVtcGxhdGVfZmlsZSkKYmlvID0gQnl0ZXNJTyhkYXRhX2ZpbGVzWyJxdWVzdGlvbl9kYXRhIl0pCgpkID0gcGlja2xlLmxvYWQoYmlvKQoKbyA9IFBsdXNGaXJzdEVsZW1lbnQoKipkKQpxID0gIiQlcz0kIiAlICIgKyAiLmpvaW4oW3N0cihpKSBmb3IgaSBpbiBbby54LCBvLnksIG8uel1dKQphbnN3ZXIgPSBvLnNvbHZlKCkKCmRpc3BsYXlfbGF0ZXggPSBydW5weV9jb250ZXh0LmdldCgiZGlzcGxheV9sYXRleCIsIEZhbHNlKQpkaXNwbGF5X21hcmtkb3duID0gcnVucHlfY29udGV4dC5nZXQoImRpc3BsYXlfbWFya2Rvd24iLCBGYWxzZSkKCmJsYW5rX2Rlc2NyaXB0aW9uID0gKAogICAgdSJ0aGUgcmVzdWx0OiIKKQoKcHJlX2Rlc2NyaXB0aW9uID0gcnVucHlfY29udGV4dC5nZXQoInByZV9kZXNjcmlwdGlvbiIsIHUiV2hhdCBpcyB0aGUgcmVzdWx0PyIpCgpwcm9tcHRfdGV4ID0gdGVtcGxhdGUucmVuZGVyKAogICAgc2hvd19xdWVzdGlvbj1UcnVlLAogICAgc2hvd19hbnN3ZXI9RmFsc2UsCiAgICBwcmVfZGVzY3JpcHRpb249cHJlX2Rlc2NyaXB0aW9uLAogICAgZGlzcGxheV9sYXRleD1kaXNwbGF5X2xhdGV4LAogICAgcT1xLAopCmlmIGRpc3BsYXlfbWFya2Rvd246CiAgICBwcm9tcHRfdGV4ICs9ICJbcHJvbXB0XShodHRwOi8vcHJvbXB0LmV4YW1wbGUuY29tKSIKZmVlZF9iYWNrX2RpY3QgPSB7fQpmZWVkX2JhY2tfZGljdC51cGRhdGUoeyJwcm9tcHQiOiBwcm9tcHRfdGV4fSkKCnF1ZXN0aW9uX3RleCA9IHRlbXBsYXRlLnJlbmRlcigKICAgIHNob3dfcXVlc3Rpb249RmFsc2UsCiAgICBzaG93X2Fuc3dlcj1GYWxzZSwKICAgIGJsYW5rX2Rlc2NyaXB0aW9uPWJsYW5rX2Rlc2NyaXB0aW9uLAogICAgZGlzcGxheV9sYXRleD1kaXNwbGF5X2xhdGV4LAogICAgc2hvd19ibGFuaz1UcnVlLAogICAgcT1xLAopCmlmIGRpc3BsYXlfbWFya2Rvd246CiAgICBxdWVzdGlvbl90ZXggKz0gIltxdWVzdGlvbl0oaHR0cDovL3F1ZXN0aW9uLmV4YW1wbGUuY29tKSIKZmVlZF9iYWNrX2RpY3QudXBkYXRlKHsicXVlc3Rpb24iOiBxdWVzdGlvbl90ZXh9KQoKYW5zd2Vyc190ZXggPSB0ZW1wbGF0ZS5yZW5kZXIoCiAgICBzaG93X3F1ZXN0aW9uPUZhbHNlLAogICAgc2hvd19hbnN3ZXI9RmFsc2UsCiAgICBzaG93X2JsYW5rX2Fuc3dlcj1UcnVlLAogICAgYmxhbmtfZGVzY3JpcHRpb249YmxhbmtfZGVzY3JpcHRpb24sCiAgICBkaXNwbGF5X2xhdGV4PWRpc3BsYXlfbGF0ZXgsCiAgICBxPXEsCiAgICBhbnN3ZXI9YW5zd2VyLAopCmZlZWRfYmFja19kaWN0LnVwZGF0ZSh7ImFuc3dlcnMiOiBhbnN3ZXJzX3RleH0pCgphbnN3ZXJfZXhwbGFuYXRpb25fdGV4ID0gdGVtcGxhdGUucmVuZGVyKAogICAgc2hvd19hbnN3ZXJfZXhwbGFuYXRpb249VHJ1ZSwKICAgIGFuc3dlcj0iJCVzJCIgJSBhbnN3ZXIsCikKaWYgZGlzcGxheV9tYXJrZG93bjoKICAgIGFuc3dlcl9leHBsYW5hdGlvbl90ZXggKz0gIltleHBsYW5hdGlvbl0oaHR0cDovL2V4cGxhbmF0aW9uLmV4YW1wbGUuY29tKSIKZmVlZF9iYWNrX2RpY3QudXBkYXRlKHsiYW5zd2VyX2V4cGxhbmF0aW9uIjogYW5zd2VyX2V4cGxhbmF0aW9uX3RleH0pCmZlZWRiYWNrLmFkZF9mZWVkYmFjayhqc29uLmR1bXBzKGZlZWRfYmFja19kaWN0KSk=',
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/jinja_env.py': jinja_env_b64},
     'setup_code': "runpy_context = {'display_latex': True}\nexec(data_files['question-data/random-page-test/test_random_runpy_with_failed_macro.py'].decode('utf-8'))",
     'user_code': ''}
)

rand_macro_fail_response2 = get_feedback_ordered(
    {'stdout': '',
     'result': 'success',
     'feedback': [
         '{"prompt": "What is the result?<p align=\\"middle\\">\\n{% call latex(compiler=\\"pdflatex\\", image_format=\\"png\\")  %}\\n\\\\documentclass{article}\\n\\\\usepackage[utf8]{inputenc}\\n\\\\begin{document}\\n\\\\Latex $1 + 2 + 6=$\\n\\\\end{document}\\n{% endcall %}\\n</p>\\n\\n\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"9\\"\\n\\n", "answer_explanation": "\\n\\n\\n$9$\\n", "question": "\\nthe result:[[blank1]]\\n\\n\\n"}',
         'Execution time: 0.2 s -- Time limit: 5.0 s'], 'points': None, 'html': [],
     'stderr': '',
     'exec_host': 'localhost'}
)

rand_single_full_success_req = get_question_data_converted(
    {
        'setup_code': 'from io import BytesIO\nimport pickle\nimport json\ntry:\n    runpy_context\nexcept NameError:\n    runpy_context = {}\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = runpy_context.get("display_latex", False)\ndisplay_markdown = runpy_context.get("display_markdown", False)\nblank_description = (\n    u"the result:"\n)\npre_description = runpy_context.get("pre_description", u"What is the result?")\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nfeed_back_dict = {}\nfeed_back_dict.update({"prompt": prompt_tex})\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nfeed_back_dict.update({"question": question_tex})\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nfeed_back_dict.update({"answers": answers_tex})\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\nfeed_back_dict.update({"answer_explanation": answer_explanation_tex})\nfeedback.add_feedback(json.dumps(feed_back_dict))\n',
        'user_code': '',
        'compile_only': False,
        'data_files': {
            'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
            'question-data/random-page-test/pyprog.py': py_prog_b64,
            'question-data/random-page-test/test_template.tex': latex_template_b64,
            'question-data/random-page-test/jinja_env.py': jinja_env_b64,
            'question_data': question_data1}}
)

rand_single_full_success_response = get_feedback_ordered(
    {'stdout': '',
     'stderr': '',
     'exec_host': 'localhost',
     'points': None,
     'result': 'success',
     'feedback': [
         '{"answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"9\\"\\n\\n", "question": "\\nthe result:[[blank1]]\\n\\n\\n", "answer_explanation": "\\n\\n\\n$9$\\n", "prompt": "What is the result?$1 + 2 + 6=$\\n\\n\\n"}',
         'Execution time: 0.2 s -- Time limit: 5.0 s'], 'html': []}
)

rand_single_full_success_req2 = get_question_data_converted(
    {'data_files': {
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
        'question_data': question_data2,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64},
        'compile_only': False,
        'setup_code': 'from io import BytesIO\nimport pickle\nimport json\ntry:\n    runpy_context\nexcept NameError:\n    runpy_context = {}\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = runpy_context.get("display_latex", False)\ndisplay_markdown = runpy_context.get("display_markdown", False)\nblank_description = (\n    u"the result:"\n)\npre_description = runpy_context.get("pre_description", u"What is the result?")\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nfeed_back_dict = {}\nfeed_back_dict.update({"prompt": prompt_tex})\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nfeed_back_dict.update({"question": question_tex})\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nfeed_back_dict.update({"answers": answers_tex})\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\nfeed_back_dict.update({"answer_explanation": answer_explanation_tex})\nfeedback.add_feedback(json.dumps(feed_back_dict))\n',
        'user_code': ''}
)

rand_single_full_success_response2 = get_feedback_ordered(
    {'exec_host': 'localhost',
     'stdout': '',
     'html': [],
     'points': None,
     'stderr': '',
     'result': 'success',
     'feedback': [
         '{"question": "\\nthe result:[[blank1]]\\n\\n\\n", "answer_explanation": "\\n\\n\\n$90$\\n", "prompt": "What is the result?$10 + 20 + 60=$\\n\\n\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"90\\"\\n\\n"}',
         'Execution time: 0.2 s -- Time limit: 5.0 s']}
)

rand_single_full_fail_req = get_question_data_converted(
    {'compile_only': False,
     'user_code': '',
     'data_files': {
         'question_data': question_data1,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64},
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\ntry:\n    runpy_context\nexcept NameError:\n    runpy_context = {}\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\n\nd = json.loads(d)\n\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = runpy_context.get("display_latex", False)\ndisplay_markdown = runpy_context.get("display_markdown", False)\nblank_description = (\n    u"the result:"\n)\npre_description = runpy_context.get("pre_description", u"What is the result?")\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nfeed_back_dict = {}\nfeed_back_dict.update({"prompt": prompt_tex})\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nfeed_back_dict.update({"question": question_tex})\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nfeed_back_dict.update({"answers": answers_tex})\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\nfeed_back_dict.update({"answer_explanation": answer_explanation_tex})\nfeedback.add_feedback(json.dumps(feed_back_dict))\n'
     }
)

rand_single_full_fail_response = get_feedback_ordered(
    {'stderr': '',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'],
     'html': [],
     'message': "TypeError: the JSON object must be str, not 'OrderedDict'",
     'stdout': '',
     'exec_host': 'localhost',
     'result': 'setup_error',
     'traceback': 'Traceback (most recent call last):\n  File "/opt/runpy/code_runpy_backend.py", line 233, in run_code\n    exec(setup_code, maint_ctx)\n  File "<setup code>", line 18, in <module>\n  File "/usr/lib/python3.5/json/__init__.py", line 312, in loads\n    s.__class__.__name__))\nTypeError: the JSON object must be str, not \'OrderedDict\'\n'
     })

rand_single_parts_3_answers_success_req = get_question_data_converted(
    {'data_files': {
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question_data': question_data1,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64},
        'user_code': '',
        'compile_only': False,
        'setup_code': '\nfrom io import BytesIO\nimport pickle\nimport json\n\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\n\nd = pickle.load(bio)\n\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\n\ndisplay_latex = False\ndisplay_markdown = True\n\nblank_description = (\n    u"the result:"\n)\n\npre_description = u"What is the result?"\n\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\n\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\n\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\n\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(answers_tex)\n'}
)

rand_single_parts_3_answers_success_response = get_feedback_ordered(
    {'exec_host': 'localhost',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'], 'html': [],
     'stderr': '',
     'stdout': '\n\nblank1:\n    type: ShortAnswer\n    width: 10em\n    hint: some hint\n    correct_answer:\n    - type: float\n      rtol: 0.01\n      atol: 0.01\n      value: "9"\n\n\n',
     'points': None,
     'result': 'success'}
)

rand_single_parts_1_prompt_success_req = get_question_data_converted(
    {'data_files': {
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question_data': question_data1,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64},
        'user_code': '', 'compile_only': False,
        'setup_code': '\nfrom io import BytesIO\nimport pickle\nimport json\n\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\n\nd = pickle.load(bio)\n\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\n\ndisplay_latex = False\ndisplay_markdown = True\n\nblank_description = (\n    u"the result:"\n)\n\npre_description = u"What is the result?"\n\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\n\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\n\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\n\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(prompt_tex)\n'}
)

rand_single_parts_1_prompt_success_response = get_feedback_ordered(
    {'exec_host': 'localhost',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'], 'html': [],
     'stderr': '',
     'stdout': 'What is the result?$1 + 2 + 6=$\n\n\n[prompt](http://prompt.example.com)\n',
     'points': None,
     'result': 'success'}
)

rand_single_parts_2_question_success_req = get_question_data_converted(
    {'data_files': {
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question_data': question_data1,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64},
        'user_code': '', 'compile_only': False,
        'setup_code': '\nfrom io import BytesIO\nimport pickle\nimport json\n\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\n\nd = pickle.load(bio)\n\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\n\ndisplay_latex = False\ndisplay_markdown = True\n\nblank_description = (\n    u"the result:"\n)\n\npre_description = u"What is the result?"\n\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\n\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\n\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\n\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(question_tex)\n'})

rand_single_parts_2_question_success_response = get_feedback_ordered(
    {'exec_host': 'localhost',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'], 'html': [],
     'stderr': '',
     'stdout': '\nthe result:[[blank1]]\n\n\n[question](http://question.example.com)\n',
     'points': None,
     'result': 'success'}
)

rand_single_parts_4_explanation_success_req = get_question_data_converted(
    {'data_files': {
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question_data': question_data1,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64},
        'setup_code': '\nfrom io import BytesIO\nimport pickle\nimport json\n\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\n\nd = pickle.load(bio)\n\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\n\ndisplay_latex = False\ndisplay_markdown = True\n\nblank_description = (\n    u"the result:"\n)\n\npre_description = u"What is the result?"\n\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\n\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\n\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\n\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(answer_explanation_tex)\n',
        'compile_only': False,
        'user_code': ''}
)

rand_single_parts_4_explanation_success_response = get_feedback_ordered(
    {'result': 'success',
     'points': None,
     'stderr': '',
     'exec_host': 'localhost',
     'stdout': '\n\n\n$9$\n[explanation](http://explanation.example.com)\n',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'], 'html': []}
)

rand_with_markdown_req = get_question_data_converted(
    {
        'setup_code': "runpy_context = {'display_markdown': True}\nexec(data_files['question-data/random-page-test/test_random_runpy.py'].decode('utf-8'))",
        'data_files': {
            'question-data/random-page-test/pyprog.py': py_prog_b64,
            'question_data': question_data1,
            'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
            'question-data/random-page-test/test_template.tex': latex_template_b64,
            'question-data/random-page-test/jinja_env.py': jinja_env_b64},
        'compile_only': False,
        'user_code': ''}
)

rand_with_markdown_response = get_feedback_ordered(
    {'points': None,
     'stdout': '',
     'result': 'success',
     'html': [],
     'feedback': [
         '{"question": "\\nthe result:[[blank1]]\\n\\n\\n[question](http://question.example.com)", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"9\\"\\n\\n", "prompt": "What is the result?$1 + 2 + 6=$\\n\\n\\n[prompt](http://prompt.example.com)", "answer_explanation": "\\n\\n\\n$9$\\n[explanation](http://explanation.example.com)"}',
         'Execution time: 0.2 s -- Time limit: 5.0 s'],
     'exec_host': 'localhost',
     'stderr': ''}
)

rand_parts_multiple_req1 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(answer_explanation_tex)\n',
     'compile_only': False, 'data_files': {
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question_data': question_data1,
        'question-data/random-page-test/pyprog.py': py_prog_b64,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response1 = get_feedback_ordered(
    {'html': [],
     'stdout': '\n\n\n$9$\n\n',
     'result': 'success',
     'stderr': '',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'],
     'points': None,
     'exec_host': 'localhost'}
)

rand_parts_multiple_req2 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(answers_tex)\n',
     'compile_only': False,
     'data_files': {
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data1,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response2 = get_feedback_ordered(
    {'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'],
     'stdout': '\n\nblank1:\n    type: ShortAnswer\n    width: 10em\n    hint: some hint\n    correct_answer:\n    - type: float\n      rtol: 0.01\n      atol: 0.01\n      value: "9"\n\n\n',
     'result': 'success',
     'stderr': '',
     'html': [],
     'points': None,
     'exec_host': 'localhost'}
)

rand_parts_multiple_req3 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(prompt_tex)\n',
     'compile_only': False,
     'data_files': {
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data1,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response3 = get_feedback_ordered(
    {'html': [],
     'stdout': 'What is the result?$1 + 2 + 6=$\n\n\n\n',
     'result': 'success',
     'stderr': '',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'], 'points': None,
     'exec_host': 'localhost'}
)

rand_parts_multiple_req4 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(question_tex)\n',
     'compile_only': False,
     'data_files': {
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data1,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response4 = get_feedback_ordered(
    {'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'],
     'stdout': '\nthe result:[[blank1]]\n\n\n\n',
     'result': 'success',
     'stderr': '',
     'html': [],
     'points': None,
     'exec_host': 'localhost'}
)

rand_parts_multiple_req5 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(answer_explanation_tex)\n',
     'compile_only': False,
     'data_files': {
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data2,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response5 = get_feedback_ordered(
    {'points': None,
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'],
     'stdout': '\n\n\n$90$\n\n',
     'stderr': '',
     'html': [],
     'result': 'success',
     'exec_host': 'localhost'}
)

rand_parts_multiple_req6 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(answers_tex)\n',
     'compile_only': False,
     'data_files': {
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data2,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response6 = get_feedback_ordered(
    {'result': 'success',
     'stdout': '\n\nblank1:\n    type: ShortAnswer\n    width: 10em\n    hint: some hint\n    correct_answer:\n    - type: float\n      rtol: 0.01\n      atol: 0.01\n      value: "90"\n\n\n',
     'stderr': '',
     'html': [],
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'],
     'points': None,
     'exec_host': 'localhost'}
)

rand_parts_multiple_req7 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(prompt_tex)\n',
     'compile_only': False,
     'data_files': {
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data2,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response7 = get_feedback_ordered(
    {'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s'],
     'stdout': 'What is the result?$10 + 20 + 60=$\n\n\n\n',
     'result': 'success',
     'stderr': '',
     'html': [],
     'points': None,
     'exec_host': 'localhost'}
)

rand_parts_multiple_req8 = get_question_data_converted(
    {'user_code': '',
     'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    q=q,\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\nprint(question_tex)\n',
     'compile_only': False,
     'data_files': {
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data2,
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_multiple_response8 = get_feedback_ordered(
    {'feedback': ['Execution time: 0.4 s -- Time limit: 5.0 s'],
     'stdout': '\nthe result:[[blank1]]\n\n\n\n',
     'stderr': '',
     'points': None,
     'html': [],
     'result': 'success',
     'exec_host': 'localhost'}
)

# LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_MORE_THAN_COMMENTS

rand_parts_changed_req1 = get_question_data_converted(
    {
        'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    # comment 5: this is more than comment, because we removed a comma\n    q=q\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\n# comment4\nprint(answer_explanation_tex)\n',
        'user_code': '', 'compile_only': False, 'data_files': {
        'question-data/random-page-test/test_template.tex': latex_template_b64,
        'question-data/random-page-test/jinja_env.py': jinja_env_b64,
        'question_data': question_data1,
        'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
        'question-data/random-page-test/pyprog.py': py_prog_b64}
    }
)

rand_parts_changed_response1 = get_feedback_ordered(
    {'html': [],
     'exec_host': 'localhost',
     'points': None,
     'stderr': '',
     'result': 'success',
     'stdout': '\n\n\n$9$\n\n',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s']}
)

rand_parts_changed_req2 = get_question_data_converted(
    {
        'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    # comment 5: this is more than comment, because we removed a comma\n    q=q\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\n# comment3\nprint(answers_tex)\n',
        'user_code': '',
        'compile_only': False,
        'data_files': {
            'question-data/random-page-test/test_template.tex': latex_template_b64,
            'question-data/random-page-test/jinja_env.py': jinja_env_b64,
            'question_data': question_data1,
            'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
            'question-data/random-page-test/pyprog.py': py_prog_b64}}
)

rand_parts_changed_response2 = get_feedback_ordered(
    {'html': [],
     'exec_host': 'localhost',
     'points': None,
     'stderr': '',
     'result': 'success',
     'stdout': '\n\nblank1:\n    type: ShortAnswer\n    width: 10em\n    hint: some hint\n    correct_answer:\n    - type: float\n      rtol: 0.01\n      atol: 0.01\n      value: "9"\n\n\n',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s']}
)

rand_parts_changed_req3 = get_question_data_converted(
    {
        'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    # comment 5: this is more than comment, because we removed a comma\n    q=q\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\n# comment1\nprint(prompt_tex)\n',
        'user_code': '',
        'compile_only': False,
        'data_files': {
            'question-data/random-page-test/test_template.tex': latex_template_b64,
            'question-data/random-page-test/jinja_env.py': jinja_env_b64,
            'question_data': question_data1,
            'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
            'question-data/random-page-test/pyprog.py': py_prog_b64}}
)

rand_parts_changed_response3 = get_feedback_ordered(
    {'html': [],
     'exec_host': 'localhost',
     'points': None,
     'stderr': '',
     'result': 'success',
     'stdout': 'What is the result?$1 + 2 + 6=$\n\n\n\n',
     'feedback': ['Execution time: 0.4 s -- Time limit: 5.0 s']}
)

rand_parts_changed_req4 = get_question_data_converted(
    {
        'setup_code': 'from io import BytesIO\nimport pickle\nimport json\nprog = data_files["question-data/random-page-test/pyprog.py"].decode("utf8")\nexec(prog)\njinja_env = data_files["question-data/random-page-test/jinja_env.py"].decode("utf8")\nexec(jinja_env)\ntemplate_file = data_files[\n    "question-data/random-page-test/test_template.tex"].decode("utf8")\ntemplate = latex_jinja_env.from_string(template_file)\nbio = BytesIO(data_files["question_data"])\nd = pickle.load(bio)\no = PlusFirstElement(**d)\nq = "$%s=$" % " + ".join([str(i) for i in [o.x, o.y, o.z]])\nanswer = o.solve()\ndisplay_latex = False\ndisplay_markdown = True\nblank_description = (\n    u"the result:"\n)\npre_description = u"What is the result?"\nprompt_tex = template.render(\n    show_question=True,\n    show_answer=False,\n    pre_description=pre_description,\n    display_latex=display_latex,\n    # comment 5: this is more than comment, because we removed a comma\n    q=q\n)\nif display_markdown:\n    prompt_tex += "[prompt](http://prompt.example.com)"\nquestion_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    show_blank=True,\n    q=q,\n)\nif display_markdown:\n    question_tex += "[question](http://question.example.com)"\nanswers_tex = template.render(\n    show_question=False,\n    show_answer=False,\n    show_blank_answer=True,\n    blank_description=blank_description,\n    display_latex=display_latex,\n    q=q,\n    answer=answer,\n)\nanswer_explanation_tex = template.render(\n    show_answer_explanation=True,\n    answer="$%s$" % answer,\n)\nif display_markdown:\n    answer_explanation_tex += "[explanation](http://explanation.example.com)"\n\n# comment2\nprint(question_tex)\n',
        'user_code': '',
        'compile_only': False,
        'data_files': {
            'question-data/random-page-test/test_template.tex': latex_template_b64,
            'question-data/random-page-test/jinja_env.py': jinja_env_b64,
            'question_data': question_data1,
            'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
            'question-data/random-page-test/pyprog.py': py_prog_b64}}
)

rand_parts_changed_response4 = get_feedback_ordered(
    {'html': [],
     'exec_host': 'localhost',
     'points': None,
     'stderr': '',
     'result': 'success',
     'stdout': '\nthe result:[[blank1]]\n\n\n\n',
     'feedback': ['Execution time: 0.2 s -- Time limit: 5.0 s']}
)

rand_parts_missing_runpy_req = get_question_data_converted(
    {'setup_code': 'print("abcd")\n',
     'compile_only': False,
     'user_code': '',
     'data_files': {
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_template.tex': latex_template_b64,
         'question_data': question_data1,
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64}}
)

rand_parts_missing_runpy_response = get_feedback_ordered(
    {'stdout': 'abcd\n',
     'stderr': '',
     'points': None,
     'feedback': ['Execution time: 0.1 s -- Time limit: 5.0 s'], 'result': 'success',
     'exec_host': 'localhost', 'html': []}
)

rand_sha_changed1_req = get_question_data_converted(
    {'compile_only': False,
     'setup_code': "runpy_context = {}\nexec(data_files['question-data/random-page-test/test_random_runpy.py'].decode('utf-8'))",
     'data_files': {
         'question-data/random-page-test/pyprog.py': py_prog_b64,
         'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
         'question-data/random-page-test/test_template.tex': latex_template_changed_b64,
         'question-data/random-page-test/jinja_env.py': jinja_env_b64,
         'question_data': question_data1},
     'user_code': ''}
)

rand_sha_changed1_response = get_feedback_ordered(
    {'stdout': '',
     'points': None,
     'result': 'success',
     'exec_host': 'localhost',
     'html': [],
     'stderr': '',
     'feedback': [
         '{"question": "\\nthe result:[[blank1]]\\n\\n\\n", "answer_explanation": "\\n\\n\\nThe correct answer is: $9$\\n", "prompt": "What is the result?$1 + 2 + 6=$\\n\\n\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"9\\"\\n\\n"}',
         'Execution time: 0.2 s -- Time limit: 5.0 s']}
)

rand_sha_changed2_req = get_question_data_converted(
    {
        'setup_code': "runpy_context = {}\nexec(data_files['question-data/random-page-test/test_random_runpy.py'].decode('utf-8'))",
        'compile_only': False,
        'data_files': {
            'question-data/random-page-test/test_random_runpy.py': runpy_file_b64,
            'question_data': question_data2,
            'question-data/random-page-test/jinja_env.py': jinja_env_b64,
            'question-data/random-page-test/pyprog.py': py_prog_b64,
            'question-data/random-page-test/test_template.tex': latex_template_changed_b64},
        'user_code': ''}
)

rand_sha_changed2_response = get_feedback_ordered(
    {'points': None,
     'html': [],
     'stdout': '',
     'exec_host': 'localhost',
     'feedback': [
         '{"question": "\\nthe result:[[blank1]]\\n\\n\\n", "answers": "\\n\\nblank1:\\n    type: ShortAnswer\\n    width: 10em\\n    hint: some hint\\n    correct_answer:\\n    - type: float\\n      rtol: 0.01\\n      atol: 0.01\\n      value: \\"90\\"\\n\\n", "prompt": "What is the result?$10 + 20 + 60=$\\n\\n\\n", "answer_explanation": "\\n\\n\\nThe correct answer is: $90$\\n"}',
         'Execution time: 0.2 s -- Time limit: 5.0 s'], 'stderr': '',
     'result': 'success'}
)


ALL_REQ_RESP_TUPLE = (
    (rand1_req, rand1_response),
    (rand2_req, rand2_response),

    (rand_macro_success_req, rand_macro_success_response),
    (rand_macro_success_req2, rand_macro_success_response2),

    (rand_macro_fail_req, rand_macro_fail_response),

    (rand_single_full_success_req, rand_single_full_success_response),
    (rand_single_full_success_req2, rand_single_full_success_response2),

    (rand_single_full_fail_req, rand_single_full_fail_response),

    (rand_single_parts_3_answers_success_req,
     rand_single_parts_3_answers_success_response),
    (rand_single_parts_1_prompt_success_req,
     rand_single_parts_1_prompt_success_response),
    (rand_single_parts_2_question_success_req,
     rand_single_parts_2_question_success_response),
    (rand_single_parts_4_explanation_success_req,
     rand_single_parts_4_explanation_success_response),

    (rand_with_markdown_req, rand_with_markdown_response),

    (rand_parts_multiple_req1, rand_parts_multiple_response1),
    (rand_parts_multiple_req2, rand_parts_multiple_response2),
    (rand_parts_multiple_req3, rand_parts_multiple_response3),
    (rand_parts_multiple_req4, rand_parts_multiple_response4),
    (rand_parts_multiple_req5, rand_parts_multiple_response5),
    (rand_parts_multiple_req6, rand_parts_multiple_response6),
    (rand_parts_multiple_req7, rand_parts_multiple_response7),
    (rand_parts_multiple_req8, rand_parts_multiple_response8),

    (rand_parts_changed_req1, rand_parts_changed_response1),
    (rand_parts_changed_req2, rand_parts_changed_response2),
    (rand_parts_changed_req3, rand_parts_changed_response3),
    (rand_parts_changed_req4, rand_parts_changed_response4),

    (rand_parts_missing_runpy_req, rand_parts_missing_runpy_response),

    (rand_sha_changed1_req, rand_sha_changed1_response),
    (rand_sha_changed2_req, rand_sha_changed2_response),

)

for i, t in enumerate(ALL_REQ_RESP_TUPLE):
    req, resp = t
    for j, (r, res) in enumerate(ALL_REQ_RESP_TUPLE):
        if deep_eq(req, r) and i > j:
            print(i)
