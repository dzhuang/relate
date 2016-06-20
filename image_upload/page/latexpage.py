# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2016 Dong Zhuang"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import six
from io import BytesIO
import pickle
from hashlib import md5

from django.core.exceptions import ObjectDoesNotExist

from course.page import markup_to_html
from course.page.base import PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback, \
    PageBaseWithCorrectAnswer
from course.validation import ValidationError
from course.content import get_repo_blob

from image_upload.page.imgupload import ImageUploadQuestion
from course.page.code import (
    PythonCodeQuestion, PythonCodeQuestionWithHumanTextFeedback,
    request_python_run_with_retries)

class LatexRandomQuestion(PageBaseWithTitle, PageBaseWithValue,
                          PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer):
    def __init__(self, vctx, location, page_desc):
        super(LatexRandomQuestion, self).__init__(vctx, location, page_desc)

        if vctx is not None and hasattr(page_desc, "data_files"):
            if hasattr(page_desc, "data_file_for_page_data"):
                if not page_desc.data_file_for_page_data in page_desc.data_files:
                    raise ValidationError("%s: '%s' should be listed in 'data_files'"
                                          % (location, page_desc.data_file_for_page_data))
            if not page_desc.page_data_md5_file in page_desc.data_files:
                raise ValidationError("%s: '%s' should be listed in 'data_files'"
                                      % (location, page_desc.page_data_md5_file))
            if hasattr(page_desc, "jinja_env"):
                if not page_desc.jinja_env in page_desc.data_files:
                    raise ValidationError ("%s: '%s' should be listed in 'data_files'"
                                           % (location, page_desc.jinja_env))
            for data_file in page_desc.data_files:
                try:
                    if not isinstance(data_file, str):
                        raise ObjectDoesNotExist()

                    get_repo_blob(vctx.repo, data_file, vctx.commit_sha)
                except ObjectDoesNotExist:
                    raise ValidationError("%s: data file '%s' not found"
                            % (location, data_file))

        self.question_process_code = getattr(page_desc, "question_process_code", None)
        self.answer_process_code = getattr(page_desc, "answer_process_code", None)
        self.data_file_for_page_data = getattr(page_desc, "answer_process_code", None)
        #self.page_data_md5_file = getattr(page_desc, "page_data_md5_file")
        self.page_context = None
        self.docker_run_timeout = getattr(page_desc, "docker_timeout", 0.5)

    def required_attrs(self):
        return super(LatexRandomQuestion, self).required_attrs() + (
            ("data_files", (list,str)),
            ("question_process_code", str),
            ("page_data_md5_file", str),
            # ("timeout", (int, float)),
        )

    def allowed_attrs(self):
        return super(LatexRandomQuestion, self).allowed_attrs() + (
            ("data_file_for_page_data", str),
            ("setup_code_file", list),
            ("latex_template_file", list),
            ("background_code", str),
            ("answer_process_code", str),
            ("docker_timeout", (int, float))
        )

    def make_page_data(self, page_context):
        if not hasattr(self.page_desc, "data_file_for_page_data"):
            return {}

        # get random question_data
        repo_bytes_data = get_repo_blob(
            page_context.repo,
            self.page_desc.data_file_for_page_data,
            page_context.commit_sha).data
        bio = BytesIO(repo_bytes_data)
        repo_data_loaded = pickle.load(bio)
        if not isinstance(repo_data_loaded, (list, tuple)):
            return {}
        n_data = len(repo_data_loaded)
        if n_data < 1:
            return {}
        import random
        all_data = list(repo_data_loaded)
        random.shuffle(all_data)
        random_data = all_data[0]
        selected_data_bytes = BytesIO()
        pickle.dump(random_data, selected_data_bytes)

        page_data = {}
        from base64 import b64encode
        question_data = b64encode(selected_data_bytes.getvalue()).decode()

        page_data["question_data"] = question_data

        # make latex code of question and answer
        page_data_question_key = self.get_page_data_md5_key(page_context, part="question")
        page_data_answer_key = self.get_page_data_md5_key(page_context, part="answer")

        question_rendered = self.jinja_runpy(
            page_context, question_data, "question_process_code", common_code_name="background_code")
        answer_rendered = self.jinja_runpy(
            page_context, question_data, "answer_process_code", common_code_name="background_code")

        page_data[page_data_question_key] = question_rendered
        page_data[page_data_answer_key] = answer_rendered

        return page_data

    def get_page_data_md5_key(self, page_context, part=""):
        file_data = get_repo_blob(
            page_context.repo,
            self.page_desc.page_data_md5_file,
            page_context.commit_sha).data

        key_pre = md5(file_data.encode("utf-8")
                      ).hexdigest()

        return "%s_%s" % (key_pre, part)

    def body(self, page_context, page_data):
        if page_context.in_sandbox or page_data is None:
            page_data = self.make_page_data(page_context)

        page_data_question_key = self.get_page_data_md5_key(page_context, part="question")

        question_str = page_data[page_data_question_key]

        if not question_str:
            #print "no question_str, so we need to generate one"
            question_str = self.jinja_runpy(
                page_context,
                page_data["question_data"],
                "question_process_code",
                common_code_name="background_code")

        return super(LatexRandomQuestion, self).body(page_context, page_data) + markup_to_html(page_context, question_str)

    def jinja_runpy(self, page_context, question_data, code_name, common_code_name=""):
        # {{{ request run

        assert question_data
        run_jinja_req = {"compile_only": False}

        def transfer_attr_to(name, from_name=None):
            if from_name:
                if hasattr(self.page_desc, from_name):
                    run_jinja_req[name] = getattr(self.page_desc, from_name)
            elif hasattr(self.page_desc, name):
                run_jinja_req[name] = getattr(self.page_desc, name)

        # def prepend_code_to(name, pre_code_name):
        #     if hasattr(self.page_desc, name) and hasattr(self.page_desc, pre_code_name):
        #         print pre_code_name
        #         print getattr(self.page_desc, pre_code_name)
        #         run_jinja_req[name] = getattr(self.page_desc, pre_code_name)+ u"\n" + run_jinja_req[name]

        run_jinja_req["user_code"] = ""

        transfer_attr_to("setup_code", from_name=code_name)
        if common_code_name:
            run_jinja_req["setup_code"] = getattr(self.page_desc, common_code_name) + u"\n" + run_jinja_req["setup_code"]

        if hasattr(self.page_desc, "data_files"):
            run_jinja_req["data_files"] = {}

            for data_file in self.page_desc.data_files:
                from base64 import b64encode
                run_jinja_req["data_files"][data_file] = \
                        b64encode(
                                get_repo_blob(
                                    page_context.repo, data_file,
                                    page_context.commit_sha).data).decode()

            run_jinja_req["data_files"]["question_data"] = question_data

        try:
            response_dict = request_python_run_with_retries(run_jinja_req,
                    run_timeout=self.docker_run_timeout)
        except:
            from traceback import format_exc
            response_dict = {
                    "result": "uncaught_error",
                    "message": "Error connecting to container",
                    "traceback": "".join(format_exc()),
                    }

        if response_dict["result"] in [
                "uncaught_error",
                "setup_compile_error",
                "setup_error",
                "test_compile_error",
                "test_error"]:
            error_msg_parts = ["RESULT: %s" % response_dict["result"]]
            for key, val in sorted(response_dict.items()):
                if (key not in ["result", "figures"]
                        and val
                        and isinstance(val, six.string_types)):
                    error_msg_parts.append("-------------------------------------")
                    error_msg_parts.append(key)
                    error_msg_parts.append("-------------------------------------")
                    error_msg_parts.append(val)
            error_msg_parts.append("-------------------------------------")
            error_msg_parts.append("user code")
            error_msg_parts.append("-------------------------------------")
            error_msg_parts.append(self.page_desc.question_process_code)
            error_msg_parts.append("-------------------------------------")

            error_msg = "\n".join(error_msg_parts)
            raise RuntimeError(error_msg)

        from relate.utils import dict_to_struct
        response = dict_to_struct(response_dict)

        if hasattr(response, "stdout") and response.stdout:
            return response.stdout.encode("utf8")
        else:
            return ""

        # }}}

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        page_data_answer_key = self.get_page_data_md5_key(page_context, part="answer")

        answer_str = page_data[page_data_answer_key]

        if not answer_str:
            #print "no answer_str, so we need to generate one"
            answer_str = self.jinja_runpy(
                page_context,
                page_data["question_data"],
                "answer_process_code",
                common_code_name="background_code")

        super_correct_answer = super(LatexRandomQuestion, self).correct_answer(page_context, page_data, answer_data, grade_data)
        if super_correct_answer:
            return super_correct_answer + markup_to_html(page_context, answer_str)
        else:
            return markup_to_html(page_context, answer_str)


class LatexRandomImageUploadQuestion(LatexRandomQuestion, ImageUploadQuestion):
    pass


class LatexRandomCodeQuestion(LatexRandomQuestion, PythonCodeQuestion):
    pass

class LatexRandomCodeQuestionWithHumanTextFeedback(
    LatexRandomQuestion, PythonCodeQuestionWithHumanTextFeedback):
    pass