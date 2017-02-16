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

import six

import jinja2

from django.utils.html import escape
from django.utils.translation import ugettext as _, string_concat
from django.utils import translation
from django.conf import settings

from course.page.base import (
        markup_to_html, AnswerFeedback, get_auto_feedback,
        get_editor_interaction_mode)
from course.page.code import (
    PythonCodeQuestion, PythonCodeForm, request_python_run_with_retries,
    is_nuisance_failure
)


# {{{ python code question with page_context

class PythonCodeQuestionWithPageContext(PythonCodeQuestion):

    def allowed_attrs(self):
        return super(PythonCodeQuestionWithPageContext, self).allowed_attrs() + (
                ("setup_code", str),
                ("show_setup_code", bool),
                ("names_for_user", list),
                ("names_from_user", list),
                ("test_code", str),
                ("show_test_code", bool),
                ("correct_code_explanation", "markup"),
                ("correct_code", str),
                ("initial_code", str),
                ("data_files", list),
                ("single_submission", bool),
                )

    def _initial_code_with_page_context(self, page_context):
        return self.get_code_with_page_context_str(page_context, "initial_code")

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

    def grade(self, page_context, page_data, answer_data, grade_data):
        if answer_data is None:
            return AnswerFeedback(correctness=0,
                    feedback=_("No answer provided."))

        user_code = answer_data["answer"]

        # {{{ request run

        run_req = {"compile_only": False, "user_code": user_code}

        def transfer_attr(name):
            if hasattr(self.page_desc, name):
                run_req[name] = getattr(self.page_desc, name)

        transfer_attr("setup_code")
        transfer_attr("names_for_user")
        transfer_attr("names_from_user")

        if hasattr(self.page_desc, "test_code"):
            run_req["test_code"] = self.get_test_code_with_page_context(page_context)

        if hasattr(self.page_desc, "data_files"):
            run_req["data_files"] = {}

            from course.content import get_repo_blob

            for data_file in self.page_desc.data_files:
                from base64 import b64encode
                run_req["data_files"][data_file] = \
                        b64encode(
                                get_repo_blob(
                                    page_context.repo, data_file,
                                    page_context.commit_sha).data).decode()

        try:
            response_dict = request_python_run_with_retries(run_req,
                    run_timeout=self.page_desc.timeout)
        except:
            from traceback import format_exc
            response_dict = {
                    "result": "uncaught_error",
                    "message": "Error connecting to container",
                    "traceback": "".join(format_exc()),
                    }

        # }}}

        feedback_bits = []

        # {{{ send email if the grading code broke

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
            error_msg_parts.append(user_code)
            error_msg_parts.append("-------------------------------------")

            error_msg = "\n".join(error_msg_parts)

            with translation.override(settings.RELATE_ADMIN_EMAIL_LOCALE):
                from django.template.loader import render_to_string
                message = render_to_string("course/broken-code-question-email.txt", {
                    "page_id": self.page_desc.id,
                    "course": page_context.course,
                    "error_message": error_msg,
                    })

                if (
                        not page_context.in_sandbox
                        and
                        not is_nuisance_failure(response_dict)):
                    try:
                        from django.core.mail import EmailMessage
                        msg = EmailMessage("".join(["[%s:%s] ",
                            _("code question execution failed")])
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
                        from traceback import format_exc
                        feedback_bits.append(
                            six.text_type(string_concat(
                                "<p>",
                                _(
                                    "Both the grading code and the attempt to "
                                    "notify course staff about the issue failed. "
                                    "Please contact the course or site staff and "
                                    "inform them of this issue, mentioning this "
                                    "entire error message:"),
                                "</p>",
                                "<p>",
                                _(
                                    "Sending an email to the course staff about the "
                                    "following failure failed with "
                                    "the following error message:"),
                                "<pre>",
                                "".join(format_exc()),
                                "</pre>",
                                _("The original failure message follows:"),
                                "</p>")))

        # }}}

        from relate.utils import dict_to_struct
        response = dict_to_struct(response_dict)

        bulk_feedback_bits = []
        if hasattr(response, "points"):
            correctness = response.points
            feedback_bits.append(
                    "<p><b>%s</b></p>"
                    % get_auto_feedback(correctness))
        else:
            correctness = None

        if response.result == "success":
            pass
        elif response.result in [
                "uncaught_error",
                "setup_compile_error",
                "setup_error",
                "test_compile_error",
                "test_error"]:
            feedback_bits.append("".join([
                "<p>",
                _(
                    "The grading code failed. Sorry about that. "
                    "The staff has been informed, and if this problem is "
                    "due to an issue with the grading code, "
                    "it will be fixed as soon as possible. "
                    "In the meantime, you'll see a traceback "
                    "below that may help you figure out what went wrong."
                    ),
                "</p>"]))
        elif response.result == "timeout":
            feedback_bits.append("".join([
                "<p>",
                _(
                    "Your code took too long to execute. The problem "
                    "specifies that your code may take at most %s seconds "
                    "to run. "
                    "It took longer than that and was aborted."
                    ),
                "</p>"])
                    % self.page_desc.timeout)

            correctness = 0
        elif response.result == "user_compile_error":
            feedback_bits.append("".join([
                "<p>",
                _("Your code failed to compile. An error message is "
                    "below."),
                "</p>"]))

            correctness = 0
        elif response.result == "user_error":
            feedback_bits.append("".join([
                "<p>",
                _("Your code failed with an exception. "
                    "A traceback is below."),
                "</p>"]))

            correctness = 0
        else:
            raise RuntimeError("invalid runpy result: %s" % response.result)

        if hasattr(response, "feedback") and response.feedback:
            feedback_bits.append("".join([
                "<p>",
                _("Here is some feedback on your code"),
                ":"
                "<ul>%s</ul></p>"]) %
                        "".join(
                            "<li>%s</li>" % fb_item
                            for fb_item in response.feedback))
        if hasattr(response, "traceback") and response.traceback:
            feedback_bits.append("".join([
                "<p>",
                _("This is the exception traceback"),
                ":"
                "<pre>%s</pre></p>"]) % escape(response.traceback))
        if hasattr(response, "exec_host") and response.exec_host != "localhost":
            import socket
            try:
                exec_host_name, dummy, dummy = socket.gethostbyaddr(
                        response.exec_host)
            except socket.error:
                exec_host_name = response.exec_host

            feedback_bits.append("".join([
                "<p>",
                _("Your code ran on %s.") % exec_host_name,
                "</p>"]))

        if hasattr(response, "stdout") and response.stdout:
            bulk_feedback_bits.append("".join([
                "<p>",
                _("Your code printed the following output"),
                ":"
                "<pre>%s</pre></p>"])
                    % escape(response.stdout))
        if hasattr(response, "stderr") and response.stderr:
            bulk_feedback_bits.append("".join([
                "<p>",
                _("Your code printed the following error messages"),
                ":"
                "<pre>%s</pre></p>"]) % escape(response.stderr))
        if hasattr(response, "figures") and response.figures:
            fig_lines = ["".join([
                "<p>",
                _("Your code produced the following plots"),
                ":</p>"]),
                '<dl class="result-figure-list">',
                ]

            for nr, mime_type, b64data in response.figures:
                if mime_type in ["image/jpeg", "image/png"]:
                    fig_lines.extend([
                        "".join([
                            "<dt>",
                            _("Figure"), "%d<dt>"]) % nr,
                        '<dd><img alt="Figure %d" src="data:%s;base64,%s"></dd>'
                        % (nr, mime_type, b64data)])

            fig_lines.append("</dl>")
            bulk_feedback_bits.extend(fig_lines)

        # {{{ html output / santization

        if hasattr(response, "html") and response.html:
            def is_allowed_data_uri(allowed_mimetypes, uri):
                import re
                m = re.match(r"^data:([-a-z0-9]+/[-a-z0-9]+);base64,", uri)
                if not m:
                    return False

                mimetype = m.group(1)
                return mimetype in allowed_mimetypes

            def sanitize(s):
                import bleach

                def filter_audio_attributes(name, value):
                    if name in ["controls"]:
                        return True
                    else:
                        return False

                def filter_source_attributes(name, value):
                    if name in ["type"]:
                        return True
                    elif name == "src":
                        return is_allowed_data_uri([
                            "audio/wav",
                            ], value)
                    else:
                        return False

                def filter_img_attributes(name, value):
                    if name in ["alt", "title"]:
                        return True
                    elif name == "src":
                        return is_allowed_data_uri([
                            "image/png",
                            "image/jpeg",
                            ], value)
                    else:
                        return False

                return bleach.clean(s,
                        tags=bleach.ALLOWED_TAGS + ["audio", "video", "source"],
                        attributes={
                            "audio": filter_audio_attributes,
                            "source": filter_source_attributes,
                            "img": filter_img_attributes,
                            })

            bulk_feedback_bits.extend(
                    sanitize(snippet) for snippet in response.html)

        # }}}

        return AnswerFeedback(
                correctness=correctness,
                feedback="\n".join(feedback_bits),
                bulk_feedback="\n".join(bulk_feedback_bits))

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
