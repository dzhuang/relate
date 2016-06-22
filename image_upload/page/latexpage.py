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

from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.conf import settings

from course.page import markup_to_html
from course.page.base import (
    PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback,
    PageBaseWithCorrectAnswer)
from course.page.choice import ChoiceQuestion, MultipleChoiceQuestion
from course.validation import ValidationError
from course.content import get_repo_blob, get_repo_blob_data_cached

from image_upload.page.imgupload import ImageUploadQuestion
from course.page.code import (
    PythonCodeQuestion, PythonCodeQuestionWithHumanTextFeedback,
    request_python_run_with_retries)

class LatexRandomQuestion(PageBaseWithTitle, PageBaseWithValue,
                          PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer):
    def __init__(self, vctx, location, page_desc):
        super(LatexRandomQuestion, self).__init__(vctx, location, page_desc)

        if vctx is not None and hasattr(page_desc, "data_files"):
            if hasattr(page_desc, "random_question_data_file"):
                if not page_desc.random_question_data_file in page_desc.data_files:
                    raise ValidationError("%s: '%s' should be listed in 'data_files'"
                                          % (location, page_desc.random_question_data_file))
            if hasattr(page_desc, "cache_key_files"):
                for cf in page_desc.cache_key_files:
                    if not cf in page_desc.data_files:
                        raise ValidationError("%s: '%s' should be listed in 'data_files'"
                                              % (location, cf))
            for data_file in page_desc.data_files:
                try:
                    if not isinstance(data_file, str):
                        raise ObjectDoesNotExist()

                    get_repo_blob(vctx.repo, data_file, vctx.commit_sha)
                except ObjectDoesNotExist:
                    raise ValidationError("%s: data file '%s' not found"
                            % (location, data_file))
            if hasattr(page_desc, "cache_key_attrs"):
                for attr in page_desc.cache_key_attrs:
                    if not hasattr(page_desc, attr):
                        raise ValidationError("%s: attribute '%s' not found"
                                              % (location, attr))

        self.docker_run_timeout = getattr(page_desc, "docker_timeout", 0.5)

        # These files/attrs are used to generate rendered body and correct answer
        
        # Whether use question data file as cache
        use_question_data_file_as_cache = getattr(page_desc, "use_question_data_file_as_cache", False)
        self.cache_key_files = getattr(page_desc, "cache_key_files", getattr(page_desc, "data_files"))
        if not use_question_data_file_as_cache:
            self.cache_key_files = [f for f in self.cache_key_files if f != page_desc.random_question_data_file]
        self.cache_key_attrs = getattr(page_desc, "cache_key_attrs", [])
        if not self.cache_key_attrs:
            for attr in [
                    "question_process_code",
                    "background_code",
                    "question_process_code",
                    "answer_process_code"]:
                if hasattr(page_desc, attr):
                    self.cache_key_attrs.append(attr)

    def required_attrs(self):
        return super(LatexRandomQuestion, self).required_attrs() + (
            ("data_files", (list,str)),
            ("random_question_data_file", str),
            ("question_process_code", str),
        )

    def allowed_attrs(self):
        return super(LatexRandomQuestion, self).allowed_attrs() + (
            ("background_code", str),
            ("answer_process_code", str),
            ("docker_timeout", (int, float)),
            ("cache_key_files", list),
            ("cache_key_attrs", list),
            ("use_question_data_file_as_cache", bool)
        )

    def make_page_data(self, page_context):
        if not hasattr(self.page_desc, "random_question_data_file"):
            return {}

        # get random question_data
        repo_bytes_data = get_repo_blob_data_cached(
            page_context.repo,
            self.page_desc.random_question_data_file,
            page_context.commit_sha)
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

        from base64 import b64encode
        question_data = b64encode(selected_data_bytes.getvalue()).decode()

        return {"question_data": question_data}

    def get_cached_computing_result(self, page_context, page_data, part=""):
        assert part in ["question", "answer"]

        key_making_string = ""

        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            cache_key = None
        else:
            if self.cache_key_files:
                for cfile in self.cache_key_files:
                    try:
                        cfile_data = get_repo_blob_data_cached(
                            page_context.repo,
                            cfile,
                            page_context.commit_sha)
                        key_making_string += cfile_data.encode("utf-8")
                    except UnicodeDecodeError:
                        pass

            if self.cache_key_attrs:
                for cattr in self.cache_key_attrs:
                    key_making_string += str(getattr(self.page_desc, cattr)).encode("utf-8")

            cache_key = ("latexpage:%s:%s:%s"
                         % (str(page_context.commit_sha),
                            md5(key_making_string).hexdigest(),
                            part))

        if cache_key is None or not key_making_string:
            success, result = self.jinja_runpy(
                page_context,
                page_data["question_data"],
                "%s_process_code" % part,
                common_code_name="background_code")
            assert isinstance(result, six.string_types)
            return result

        def_cache = cache.caches["default"]

        result = None
        # Memcache is apparently limited to 250 characters.
        if len(cache_key) < 240:
            result = def_cache.get(cache_key)
        if result is not None:
            (result,) = result
            assert isinstance(result, six.string_types), cache_key
            return result

        success, result = self.jinja_runpy(
            page_context,
            page_data["question_data"],
            "%s_process_code" % part,
            common_code_name="background_code")

        if success and len(result) <= getattr(settings, "RELATE_CACHE_MAX_BYTES", 0):
            def_cache.add(cache_key, (result,), None)

        assert isinstance(result, six.string_types)

        return result

    def body(self, page_context, page_data):
        if page_context.in_sandbox or page_data is None:
            page_data = self.make_page_data(page_context)

        question_str = self.get_cached_computing_result(
                page_context, page_data, part="question")

        return super(LatexRandomQuestion, self).body(page_context, page_data)\
               + markup_to_html(page_context, question_str)

    def jinja_runpy(
            self, page_context, question_data, code_name, common_code_name=""):

        # {{{ request run

        assert question_data
        run_jinja_req = {"compile_only": False}

        def transfer_attr_to(name, from_name=None):
            if from_name:
                if hasattr(self.page_desc, from_name):
                    run_jinja_req[name] = getattr(self.page_desc, from_name)
            elif hasattr(self.page_desc, name):
                run_jinja_req[name] = getattr(self.page_desc, name)

        run_jinja_req["user_code"] = ""

        transfer_attr_to("setup_code", from_name=code_name)
        if common_code_name:
            run_jinja_req["setup_code"] = getattr(
                self.page_desc, common_code_name) + u"\n" + run_jinja_req["setup_code"]

        if hasattr(self.page_desc, "data_files"):
            run_jinja_req["data_files"] = {}

            for data_file in self.page_desc.data_files:
                from base64 import b64encode
                run_jinja_req["data_files"][data_file] = \
                        b64encode(
                                get_repo_blob_data_cached(
                                    page_context.repo, data_file,
                                    page_context.commit_sha)).decode()

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

        success = True

        if response_dict["result"] in [
                "uncaught_error",
                "setup_compile_error",
                "setup_error",
                "test_compile_error",
                "test_error"]:
            error_msg_parts = ["RESULT: %s" % response_dict["result"]]
            success = False
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
            print getattr(settings, "DEBUG")
            if getattr(settings, "DEBUG"):
                response_dict["stdout"] = error_msg
            else:
                raise RuntimeError(error_msg)

        from relate.utils import dict_to_struct
        response = dict_to_struct(response_dict)

        if hasattr(response, "stdout") and response.stdout:
            return success, response.stdout.encode("utf8")
        else:
            return False, ""

        # }}}

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        answer_str = ""
        if hasattr(self.page_desc, "answer_process_code"):
            answer_str = self.get_cached_computing_result(
                page_context, page_data, part="answer")

        super_correct_answer = super(LatexRandomQuestion, self)\
                .correct_answer(page_context, page_data, answer_data, grade_data)
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

class LatexRandomMultipleChoiceQuestion(
    LatexRandomQuestion, MultipleChoiceQuestion):

    def make_page_data(self, page_context):
        m_page_data = MultipleChoiceQuestion.make_page_data(self, page_context)
        l_page_data = LatexRandomQuestion.make_page_data(self, page_context)
        page_data = dict(m_page_data, **l_page_data)
        return page_data

class LatexRandomChoiceQuestion(
    LatexRandomQuestion, ChoiceQuestion):

    def make_page_data(self, page_context):
        m_page_data = ChoiceQuestion.make_page_data(self, page_context)
        l_page_data = LatexRandomQuestion.make_page_data(self, page_context)
        page_data = dict(m_page_data, **l_page_data)
        return page_data