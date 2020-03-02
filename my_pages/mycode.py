# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2015 Dong Zhuang"

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

import django.forms as forms
from django.utils.translation import ugettext as _, string_concat

from course.page.base import (
    AnswerFeedback, markup_to_html, PageBaseWithTitle, PageBaseWithValue,
    PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer)
from course.validation import ValidationError
from course.content import get_repo_blob, get_repo_blob_data_cached
from course.constants import participation_permission as pperm
from course.page.code import PythonCodeQuestion


class PythonCodeQuestionWrapped(PythonCodeQuestion):
    default_wrap_function_name = "__func"

    def allowed_attrs(self):
        return super(PythonCodeQuestionWrapped, self).allowed_attrs() + (
            ("function_name", str),
            ("global_names", list)
        )

    def _turn_user_code_into_func(self, user_code):
        function_name = getattr(
            self.page_desc, "function_name", self.default_wrap_function_name)
        common_indentations = 4
        spaces = " " * common_indentations
        new_user_code = list()
        new_user_code.append("def %s():" % function_name)
        for _name in (getattr(self.page_desc, "names_from_user", [])
                      + getattr(self.page_desc, "names_for_user", [])):
            new_user_code.append("%sglobal %s" % (spaces, _name))
        for _line in user_code.split("\n"):
            new_user_code.append("%s%s" % (spaces, _line.rstrip("\r")))
        return "\n".join(new_user_code)

    def process_user_code_for_grade(
            self, page_context, answer_data):
        user_code = super(
            PythonCodeQuestionWrapped, self).process_user_code_for_grade(
            page_context, answer_data)

        return self._turn_user_code_into_func(user_code)

    def get_names_from_user(self):
        names_from_user = super(PythonCodeQuestionWrapped, self).get_names_from_user()
        function_name = getattr(
            self.page_desc, "function_name", self.default_wrap_function_name)
        names_from_user.append(function_name)
        return names_from_user
