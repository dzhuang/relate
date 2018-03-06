# -*- coding: utf-8 -*-

from __future__ import division, print_function

__copyright__ = "Copyright (C) 2014 Andreas Kloeckner"

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

import json
import jinja2

from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.conf import settings

from course.page.base import (
        markup_to_html,
        get_editor_interaction_mode)
from course.page.code import (
    PythonCodeQuestion, PythonCodeForm,
    is_nuisance_failure
)


# {{{ python code question with page_context

class PythonCodeQuestionWithPageContext(PythonCodeQuestion):
    def _initial_code_with_page_context(self, page_context):
        return self.get_code_with_page_context_str(page_context, "initial_code")

    def allowed_attrs(self):
        return super(PythonCodeQuestionWithPageContext, self).allowed_attrs() + (
            ("warn_suspective_behavior", bool),
            ("penalty_for_suspective_behavior", bool)
        )

    def body(self, page_context, page_data):
        from django.template.loader import render_to_string
        return render_to_string(
                "course/prompt-code-question.html",
                {
                    "prompt_html":
                    markup_to_html(page_context, self.page_desc.prompt),
                    "initial_code":
                        self._initial_code_with_page_context(page_context),
                    "show_setup_code": getattr(
                        self.page_desc, "show_setup_code", False),
                    "setup_code":
                        self.get_code_with_page_context_str(
                            page_context, "setup_code"),
                    "show_test_code": getattr(
                        self.page_desc, "show_test_code", False),
                    "test_code": (
                        self.get_code_with_page_context_str(
                            page_context, "test_code")
                    ),
                    })

    def make_form(self, page_context, page_data,
            answer_data, page_behavior):

        if answer_data is not None:
            answer = {"answer": answer_data["answer"]}
            form = PythonCodeForm(
                    not page_behavior.may_change_answer,
                    get_editor_interaction_mode(page_context),
                    self._initial_code_with_page_context(page_context),
                    answer)
        else:
            answer = None
            form = PythonCodeForm(
                    not page_behavior.may_change_answer,
                    get_editor_interaction_mode(page_context),
                    self._initial_code_with_page_context(page_context),
                    )

        return form

    def process_form_post(
            self, page_context, page_data, post_data, files_data, page_behavior):
        return PythonCodeForm(
                not page_behavior.may_change_answer,
                get_editor_interaction_mode(page_context),
                self._initial_code_with_page_context(page_context),
                post_data, files_data)

    def get_code_with_page_context_str(self, page_context, code_name):
        assert code_name in [
            "test_code", "setup_code", "correct_code", "initial_code"]
        code = getattr(self.page_desc, code_name, None)
        if code is None:
            return code
        jinja_env = jinja2.Environment(
            block_start_string='\BLOCK{',
            block_end_string='}',
            variable_start_string='\VAR{',
            variable_end_string='}',
            comment_start_string='\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
        )
        template = jinja_env.from_string(code.strip())
        return template.render(page_context=page_context)

    def get_test_code(self, page_context):
        return self.get_code_with_page_context_str(page_context, "test_code")

    def get_test_code_with_page_context(self, page_context):
        test_code = self.get_code_with_page_context_str(
            page_context, "test_code")
        if test_code is None:
            return test_code

        correct_code = self.get_code_with_page_context_str(
            page_context, "correct_code")
        if correct_code is None:
            correct_code = ""

        from .code_runpy_backend import substitute_correct_code_into_test_code
        return substitute_correct_code_into_test_code(test_code, correct_code)

    def process_correctness_and_feedback_bits_from_response_dict(
            self, page_context, answer_data, response_dict):

        adjusted_correctness = None

        # {{{ send email if success but have dishonest result
        if response_dict["result"] == "success":
            if "feedback" in response_dict and response_dict["feedback"]:
                message = None
                suspective_reason = None
                for i, item in enumerate(response_dict["feedback"]):
                    try:
                        suspective_reason_dict = json.loads(item)
                        suspective_reason = suspective_reason_dict["suspective_reason"]  # noqa
                        response_dict["feedback"].pop(i)
                    except Exception:
                        pass

                for i, item in enumerate(response_dict["feedback"]):
                    if "suspective_behavior" in item:
                        print("here!!!")
                        error_message = _(
                            "There are suspective "
                            "behavior with submission of "
                            "this code question%s"
                            % (": %s" % suspective_reason
                               if suspective_reason else "")
                        )
                        from relate.utils import local_now, format_datetime_local
                        from course.utils import LanguageOverride
                        with LanguageOverride(page_context.course):
                            from relate.utils import render_email_template
                            message = render_email_template(
                                "course/broken-code-question-email.txt", {
                                    "site": getattr(settings, "RELATE_BASE_URL"),
                                    "page_id": self.page_desc.id,
                                    "course": page_context.course,
                                    "error_message": error_message,
                                    "review_uri": page_context.page_uri,
                                    "time": format_datetime_local(local_now())
                                })
                        if getattr(self.page_desc,
                                   "penalty_for_suspective_behavior", True):
                            adjusted_correctness = 0

                        if not getattr(self.page_desc,
                                   "warn_suspective_behavior", True):
                            response_dict["feedback"].pop(i)
                        break

                if (message and
                        not page_context.in_sandbox
                    and
                        not is_nuisance_failure(response_dict)):
                    try:
                        from django.core.mail import EmailMessage
                        msg = EmailMessage(
                            "".join(["[%s:%s] ",
                                     _(
                                         "code question execution failed")])
                            % (
                                page_context.course.identifier,
                                page_context.flow_session.flow_id
                                if page_context.flow_session is not None
                                else _("<unknown flow>")),
                            message,
                            settings.ROBOT_EMAIL_FROM,
                            [page_context.course.notify_email])

                        from relate.utils import get_outbound_mail_connection
                        msg.connection = get_outbound_mail_connection("robot")
                        msg.send()

                    except Exception:
                        pass

        # }}}

        correctness, feedback_bits, bulk_feedback_bits = (
            super(PythonCodeQuestionWithPageContext, self)
            .process_correctness_and_feedback_bits_from_response_dict(
                page_context, answer_data, response_dict))

        if adjusted_correctness is not None:
            correctness = adjusted_correctness

        return correctness, feedback_bits, bulk_feedback_bits

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        result = ""

        if hasattr(self.page_desc, "correct_code_explanation"):
            result += markup_to_html(
                    page_context,
                    self.page_desc.correct_code_explanation)

        correct_code = self.get_code_with_page_context_str(
            page_context, "correct_code")
        if correct_code is not None:
            result += ("".join([
                _("The following code is a valid answer"),
                ": <pre>%s</pre>"])
                % escape(correct_code))

        return result

# }}}
