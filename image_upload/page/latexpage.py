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
import os

from django.utils.translation import ugettext as _, string_concat
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.conf import settings
from django.utils.html import escape

from course.page import markup_to_html
from course.page.base import (
    PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback,
    PageBaseWithCorrectAnswer)
from course.page import (
    ChoiceQuestion, MultipleChoiceQuestion, TextQuestion,
    InlineMultiQuestion)
from course.validation import ValidationError
from course.content import get_repo_blob, get_repo_blob_data_cached
from course.latex.utils import file_read
from atomicwrites import atomic_write

from image_upload.page.imgupload import ImageUploadQuestion
from course.page.code import (
    PythonCodeQuestion, PythonCodeQuestionWithHumanTextFeedback,
    request_python_run_with_retries)

CACHE_VERSION = "V0"

MAX_JINJIA_RETRY = 3

def is_course_staff(page_context):
    from course.constants import (
        participation_permission as pperm,
    )
    participation = page_context.flow_session.participation
    if participation.has_permission(pperm.assign_grade):
        return True
    else:
        return False


class LatexRandomQuestionBase(PageBaseWithTitle, PageBaseWithValue,
                          PageBaseWithCorrectAnswer):
    grading_sort_by_page_data = True

    def __init__(self, vctx, location, page_desc):
        super(LatexRandomQuestionBase, self).__init__(vctx, location, page_desc)

        self.page_saving_folder = getattr(
            settings, "RELATE_LATEX_PAGE_SAVING_FOLDER_PATH",
            os.path.join(settings.MEDIA_ROOT, "latex_page"))

        if vctx is not None and hasattr(page_desc, "data_files"):
            if hasattr(page_desc, "random_question_data_file"):
                if not page_desc.random_question_data_file in page_desc.data_files:
                    raise ValidationError(
                        "%s: " % location,
                        string_concat(_("'%s' should be listed in 'data_files'"))
                        % page_desc.random_question_data_file)
            if hasattr(page_desc, "cache_key_files"):
                for cf in page_desc.cache_key_files:
                    if not cf in page_desc.data_files:
                        raise ValidationError("%s: '%s' should be listed in 'data_files'"
                                              % (location, cf))
            if hasattr(page_desc, "excluded_cache_key_files"):
                for cf in page_desc.excluded_cache_key_files:
                    if not cf in page_desc.data_files:
                        vctx.add_warning("%s: '%s' is not in 'data_files'"
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

            if not os.path.isdir(self.page_saving_folder):
                os.makedirs(self.page_saving_folder)

        self.docker_run_timeout = getattr(page_desc, "docker_timeout", 2)

        # These files/attrs are used to generate rendered body and correct answer
        
        # Whether use question data file as cache
        use_question_data_file_as_cache = getattr(page_desc, "use_question_data_file_as_cache", False)
        self.cache_key_files = getattr(page_desc, "cache_key_files", getattr(page_desc, "data_files"))
        excluded_cache_key_files = getattr(page_desc, "excluded_cache_key_files", None)
        if excluded_cache_key_files:
            self.cache_key_files = [f for f in self.cache_key_files if f not in excluded_cache_key_files]
        if not use_question_data_file_as_cache:
            self.cache_key_files = [f for f in self.cache_key_files if f != page_desc.random_question_data_file]
        self.cache_key_attrs = getattr(page_desc, "cache_key_attrs", [])
        if not self.cache_key_attrs:
            for attr in [
                "background_code",
                "question_process_code",
                "answer_process_code",
                "blank_answer_process_code",
                "blank_process_code",
                "answer_explanation_process_code",
            ]:
                if hasattr(page_desc, attr):
                    self.cache_key_attrs.append(attr)

        self.will_receive_grade = getattr(page_desc, "will_receive_grade", True)

    def required_attrs(self):
        return super(LatexRandomQuestionBase, self).required_attrs() + (
            ("data_files", (list,str)),
            ("random_question_data_file", str),
            ("question_process_code", str),
        )

    def allowed_attrs(self):
        return super(LatexRandomQuestionBase, self).allowed_attrs() + (
            ("background_code", str),
            ("answer_process_code", str),
            ("docker_timeout", (int, float)),
            ("excluded_cache_key_files", list),
            ("cache_key_files", list),
            ("cache_key_attrs", list),
            ("use_question_data_file_as_cache", bool),
            ("warm_up_by_sandbox", bool),
            ("will_receive_grade", bool),
        )

    def is_answer_gradable(self):
        return self.will_receive_grade

    def update_page_data(self, page_context, page_data):
        question_data = page_data.get("question_data", None)
        key_making_string = ""
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

        if question_data:
            key_making_string += question_data

        page_data["key_making_string_md5"] = md5(key_making_string).hexdigest()

        return page_data

    def generate_question_data_key_making_string(self, page_context, selected_data_bytes):
        from base64 import b64encode
        question_data = b64encode(selected_data_bytes.getvalue()).decode()

        key_making_string = ""
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

        if question_data:
            key_making_string += question_data

        return question_data, key_making_string

    def initialize_page_data(self, page_context):
        if not hasattr(self.page_desc, "random_question_data_file"):
            return {}

        warm_up_by_sandbox = getattr(self.page_desc, "warm_up_by_sandbox", False)

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

        all_data = list(repo_data_loaded)

        from random import choice

        question_data = None
        key_making_string = None

        for i in range(len(all_data)):
            if not page_context.in_sandbox or not warm_up_by_sandbox:
                random_data = choice(all_data)
            else:
                random_data = all_data[i]
            selected_data_bytes = BytesIO()
            pickle.dump(random_data, selected_data_bytes)

            question_data, key_making_string = (
                self.generate_question_data_key_making_string(page_context, selected_data_bytes)
            )

            # for debuging errors using page_data
            # if question_data == "KGRwMApTJ3Byb2plY3RfbGlzdCcKcDEKKGxwMgpWXHU1YjUwXHU1MTZjXHU1M2Y4MQpwMwphVlx1NWI1MFx1NTE2Y1x1NTNmODIKcDQKYVZcdTViNTBcdTUxNmNcdTUzZjgzCnA1CmFWXHU1YjUwXHU1MTZjXHU1M2Y4NApwNgphVlx1NWI1MFx1NTE2Y1x1NTNmODUKcDcKYXNTJ3RvdGFsX3Jlc291cmNlJwpwOApJODAwCnNTJ2dhaW4nCnA5CmNudW1weS5jb3JlLm11bHRpYXJyYXkKX3JlY29uc3RydWN0CnAxMAooY251bXB5Lm1hdHJpeGxpYi5kZWZtYXRyaXgKbWF0cml4CnAxMQooSTAKdHAxMgpTJ2InCnAxMwp0cDE0ClJwMTUKKEkxCihJNQpJNgp0cDE2CmNudW1weQpkdHlwZQpwMTcKKFMnZjgnCnAxOApJMApJMQp0cDE5ClJwMjAKKEkzClMnPCcKcDIxCk5OTkktMQpJLTEKSTAKdHAyMgpiSTAwClMnXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwXHhjMGdAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwaUBceDAwXHgwMFx4MDBceDAwXHgwMGB4QFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMHlAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwXHg4MFtAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBpQFx4MDBceDAwXHgwMFx4MDBceDAwIHdAXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceGY4XHg3Zlx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4ZjhceDdmXHgwMFx4MDBceDAwXHgwMFx4MDBceDgwW0BceDAwXHgwMFx4MDBceDAwXHgwMGBzQFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4ZjhceDdmXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHhmOFx4N2ZceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBZQFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMGlAXHgwMFx4MDBceDAwXHgwMFx4MDBAcEBceDAwXHgwMFx4MDBceDAwXHgwMFx4YTB0QFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4ZjhceDdmXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBZQFx4MDBceDAwXHgwMFx4MDBceDAwXHg4MGFAXHgwMFx4MDBceDAwXHgwMFx4MDBAZUBceDAwXHgwMFx4MDBceDAwXHgwMEBvQFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMHRAJwpwMjMKdHAyNApic1MnZGVjaXNpb25fc2V0JwpwMjUKKGxwMjYKSTAKYUkxMDAKYUkyMDAKYUkzMDAKYUk0MDAKYUk1MDAKYXMu":
            #     #print key_making_string
            #
            #     print "here---------------------"
            #
            #     print md5(key_making_string).hexdigest()

            # this is used to let sandbox do the warm up job for
            # sequentially ordered data(not random)
            if not page_context.in_sandbox or not warm_up_by_sandbox:
                break

            page_data = {"question_data": question_data,
                         "key_making_string_md5": md5(key_making_string).hexdigest()
                         }

            for part in ["answer", "question", "blank", "blank_answer", "answer_explanation"]:
                try:
                    key_exist, result = self.get_cached_result(page_context, page_data, part=part,
                                                               test_key_existance=True)
                    if key_exist:
                        markup_to_html(page_context, result)
                        continue
                except KeyError:
                    continue

        if page_context.in_sandbox and warm_up_by_sandbox:
            random_data = choice(all_data)
            selected_data_bytes = BytesIO()
            pickle.dump(random_data, selected_data_bytes)
            question_data, key_making_string = (
                self.generate_question_data_key_making_string(page_context, selected_data_bytes)
            )

        return {"question_data": question_data,
                "key_making_string_md5": md5(key_making_string).hexdigest()
                }

    def get_cached_result(self, page_context, page_data, part="", test_key_existance=False):
        #assert part in ["question", "answer"]
        will_save_file_local = True

        # if page_context.in_sandbox:
        #     will_save_file_local = True

        # if not getattr(page_data, "question_data", None):
        #     page_data = self.initialize_page_data(page_context)

        #key_making_string = ""
        saved_file_path = None
        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            cache_key = None
        else:
            try:
                key_making_string_md5 = page_data["key_making_string_md5"]
            except KeyError:
                updated_page_data = self.update_page_data(page_context, page_data)
                key_making_string_md5 = updated_page_data["key_making_string_md5"]

            # To be used as saving name of the latex page
            saved_file_name = ("%s_%s" % (md5("%s"
                                      % (key_making_string_md5, )
                                      ).hexdigest(), CACHE_VERSION))

            saved_file_path = os.path.join(self.page_saving_folder,
                                           "%s_%s" % (saved_file_name, part))

            cache_key = ("latexpage:%s:%s:%s"
                         % (CACHE_VERSION,
                            key_making_string_md5,
                            part))

            def_cache = cache.caches["default"]
            result = def_cache.get(cache_key)
            if result is not None:

                assert isinstance(result, six.string_types)
                if will_save_file_local:
                    if not os.path.isfile(saved_file_path):
                        with atomic_write(saved_file_path) as f:
                            f.write(result.encode('UTF-8'))
                if test_key_existance:
                    return True, result
                print("-----I'm reading from cache------")
                return True, result

        # cache_key is None means cache is not enabled
        result = None
        success = False

        if cache_key is None:
            if saved_file_path:
                if os.path.isfile(saved_file_path):
                    try:
                        result = file_read(saved_file_path)
                    except:
                        pass
                    if result is not None:
                        success = True

            if result is None:
                try:
                    print ("------------!!!!! I'm visiting docker !!!!!!!!!!!!---------------")
                    success, result = self.jinja_runpy(
                        page_context,
                        page_data["question_data"],
                        "%s_process_code" % part,
                        common_code_name="background_code")
                except TypeError:
                    return False, result
                    # May raise an "'NoneType' object is not iterable" error
                    # jinja_runpy error may write a broken saved file??
                    # if saved_file_path:
                    #     if os.path.isfile(saved_file_path):
                    #         os.remove(saved_file_path)

                if success and result is not None:
                    if saved_file_path and will_save_file_local:
                        if not os.path.isfile(saved_file_path):
                            with atomic_write(saved_file_path) as f:
                                f.write(result.encode('UTF-8'))

            return success, result

        def_cache = cache.caches["default"]
        if saved_file_path:
            if os.path.isfile(saved_file_path):
                try:
                    result = file_read(saved_file_path)
                except:
                    pass
                if result is not None:
                    success = True
                    print ("-----------I'm reading from saved_file_path-------------")
        if result is not None:
            assert isinstance(result, six.string_types), cache_key
            if success and len(result) <= getattr(settings, "RELATE_CACHE_MAX_BYTES", 0):
                if def_cache.get(cache_key) is None:
                    def_cache.delete(cache_key)
                def_cache.add(cache_key, result)
            return True, result

        try:
            print ("------------!!!!! I'm visiting docker !!!!!!!!!!!!---------------")
            success, result = self.jinja_runpy(
                page_context,
                page_data["question_data"],
                "%s_process_code" % part,
                common_code_name="background_code")
        except TypeError:
            return False, result
            # May raise an "'NoneType' object is not iterable" error
            # jinja_runpy error may write a broken saved file??
            # if saved_file_path:
            #     if os.path.isfile(saved_file_path):
            #         os.remove(saved_file_path)

        if success and len(result) <= getattr(settings, "RELATE_CACHE_MAX_BYTES", 0):
            if def_cache.get(cache_key) is None:
                def_cache.delete(cache_key)
            def_cache.add(cache_key, result)

        if success and result is not None:
            if saved_file_path and will_save_file_local:
                if not os.path.isfile(saved_file_path):
                    with atomic_write(saved_file_path) as f:
                        f.write(result.encode('UTF-8'))

        return success, result

    def body(self, page_context, page_data):
        if page_context.in_sandbox or page_data is None:
            page_data = self.initialize_page_data(page_context)

        question_str = ""
        success = False
        question_str_tmp = ""
        for i in range(MAX_JINJIA_RETRY):
            success, question_str_tmp = self.get_cached_result(
                    page_context, page_data, part="question")
            if success:
                question_str = question_str_tmp
                break

        if not success:
            if page_context.in_sandbox:
                question_str = question_str_tmp

        # generate correct answer at the same time
        #answer_str = ""
        # if hasattr(self.page_desc, "answer_process_code"):
        #     for i in range(MAX_JINJIA_RETRY):
        #         success, answer_str_tmp = self.get_cached_result(
        #                            page_context, page_data, part="answer")
        #         if success:
        #             #markup_to_html(page_context, answer_str_tmp)
        #             break
        #
        #     if not success:
        #         if page_context.in_sandbox:
        #             answer_str = markup_to_html(page_context, answer_str)

        return super(LatexRandomQuestionBase, self).body(page_context, page_data)\
               + markup_to_html(page_context, question_str) #+ answer_str

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
        feedback_bits = []

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
            error_msg_parts.append("code")
            error_msg_parts.append("-------------------------------------")
            error_msg_parts.append(run_jinja_req["setup_code"])
            error_msg_parts.append("-------------------------------------")

            error_msg = "\n".join(error_msg_parts)
            if getattr(settings, "DEBUG"):
                pass
                #response_dict["stdout"] = error_msg
            #else:

            review_url = ""
            if not page_context.in_sandbox:

                from django.core.urlresolvers import reverse
                review_url = reverse(
                    "relate-view_flow_page",
                    kwargs={'course_identifier': page_context.course.identifier,
                            'flow_session_id': page_context.flow_session.id,
                            'ordinal': page_context.ordinal
                            }
                )

            from six.moves.urllib.parse import urljoin
            review_uri = urljoin(getattr(settings, "RELATE_BASE_URL"),
                                 review_url)

            from course.page.code import is_nuisance_failure
            from django.utils import translation
            with translation.override(settings.RELATE_ADMIN_EMAIL_LOCALE):
                from django.template.loader import render_to_string
                message = render_to_string("image_upload/broken-random-latex-question-email.txt", {
                    "site": getattr(settings, "RELATE_BASE_URL"),
                    "username": page_context.flow_session.participation.user.username,
                    "page_id": self.page_desc.id,
                    "course": page_context.course,
                    "error_message": error_msg,
                    "review_uri": review_uri,
                })

                if (
                            not page_context.in_sandbox
                        and
                            not is_nuisance_failure(response_dict)):
                    try:
                        from django.core.mail import EmailMessage
                        msg = EmailMessage(
                                "".join(["[%(course)s] ",
                                         _("LaTex page failed in user %(user)s's session")])
                                % {"course":page_context.course.identifier,
                                   "user": page_context.flow_session.participation.user.username,
                                   },
                                message,
                                settings.ROBOT_EMAIL_FROM,
                                [page_context.course.notify_email])

                        from relate.utils import get_outbound_mail_connection
                        msg.connection = get_outbound_mail_connection("robot")
                        if not getattr(settings, "DEBUG"):
                            msg.send()

                    except Exception:
                        from traceback import format_exc
                        feedback_bits.append(
                            six.text_type(string_concat(
                                "<p>",
                                _(
                                    "Both the code and the attempt to "
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

        if response.result == "success":
            pass
        elif response.result in [
                "uncaught_error",
                "setup_compile_error",
                "setup_error",
                "test_compile_error",
                "test_error"]:
            success = False
            feedback_bits.append("".join([
                "<p>",
                _(
                    "The page failed to be rendered. Sorry about that. "
                    "The staff has been informed, and "
                    "it will be fixed as soon as possible."
                ),
                "</p>"]))

            if is_course_staff(page_context):
                feedback_bits.append("".join([
                    "<p>",
                    _("This is the problematic code"),
                    ":"
                    "<pre>%s</pre></p>"]) % escape(run_jinja_req["setup_code"]))
                if hasattr(response, "traceback") and response.traceback:
                    feedback_bits.append("".join([
                        "<p>",
                        _("This is the exception traceback"),
                        ":"
                        "<pre>%s</pre></p>"]) % escape(response.traceback))

        elif response.result == "timeout":
            success = False
            feedback_bits.append("".join([
                "<p>",
                _(
                    "The page failed to be rendered due to timeout, please "
                    "try to reload the page in a while."
                    ),
                "</p>"])
            )
        else:
            success = False
            raise RuntimeError("invalid runpy result: %s" % response.result)

        if hasattr(response, "figures") and response.figures:
            fig_lines = ["".join([
                "<p>",
                _("Your code produced the following plots"),
                ":</p>"]),
                '<dl class="result-figure-list">',
                ]

            for nr, mime_type, b64data in response.figures:
                fig_lines.extend([
                    "".join([
                        "<dt>",
                        _("Figure"), "%d<dt>"]) % nr,
                    '<dd><img alt="Figure %d" src="data:%s;base64,%s"></dd>'
                    % (nr, mime_type, b64data)])

            fig_lines.append("</dl>")

        if success:
            if hasattr(response, "stdout") and response.stdout:
                return success, response.stdout.encode("utf8")
        else:
            return success, '<div class="latexpage-error alert alert-danger">%s</div>' % "\n".join(feedback_bits)

        # }}}

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        CA_PATTERN = string_concat(_("A correct answer is"), ": %s.")  # noqa
        answer_str = ""
        if hasattr(self.page_desc, "answer_process_code"):
            answer_str = ""
            for i in range(MAX_JINJIA_RETRY):
                success, answer_str_tmp = self.get_cached_result(
                                   page_context, page_data, part="answer")
                if success:
                    answer_str = answer_str_tmp
                    break

        super_correct_answer = super(LatexRandomQuestionBase, self)\
                .correct_answer(page_context, page_data, answer_data, grade_data)
        if super_correct_answer:
            return super_correct_answer + markup_to_html(page_context, answer_str)
        else:
            return CA_PATTERN % markup_to_html(page_context, answer_str)


class LatexRandomQuestion(LatexRandomQuestionBase):
    pass


class LatexRandomImageUploadQuestion(LatexRandomQuestion, ImageUploadQuestion):
    pass


class LatexRandomCodeQuestion(LatexRandomQuestion, PythonCodeQuestion):
    pass


class LatexRandomCodeTextQuestion(LatexRandomQuestion, TextQuestion):
    pass


class LatexRandomCodeInlineMultiQuestion(LatexRandomQuestion, InlineMultiQuestion):
    need_update_page_desc = True

    def __init__(self, vctx, location, page_desc):
        super(LatexRandomCodeInlineMultiQuestion, self).__init__(vctx, location, page_desc)
        #self.update_page_desc(vctx, location)

    def update_page_desc(self, page_context, page_data):
        from course.page.inline import WRAPPED_NAME_RE, NAME_RE, NAME_VALIDATE_RE

        question_str = ""
        for i in range(MAX_JINJIA_RETRY):
            success, question_str_tmp = self.get_cached_result(
                page_context, page_data, part="blank")
            if success:
                question_str = question_str_tmp
                break

        question = markup_to_html(page_context, question_str)

        answers_str = ""
        for i in range(MAX_JINJIA_RETRY):
            success, answer_str_tmp = self.get_cached_result(
                page_context, page_data, part="blank_answer")
            if success:
                answers_str = answer_str_tmp
                break

        from relate.utils import dict_to_struct
        import yaml
        answers = dict_to_struct(yaml.load(answers_str))
        self.page_desc.question = question
        self.page_desc.answers = answers
        self.embedded_wrapped_name_list = WRAPPED_NAME_RE.findall(
                self.page_desc.question)
        self.embedded_name_list = NAME_RE.findall(self.page_desc.question)
        answer_instance_list = []

        for idx, name in enumerate(self.embedded_name_list):
            answers_desc = getattr(self.page_desc.answers, name)

            from course.page.inline import parse_question

            parsed_answer = parse_question(
                    None, None, name, answers_desc)
            answer_instance_list.append(parsed_answer)

        self.answer_instance_list = answer_instance_list

        if hasattr(self.page_desc, "answer_explanation_process_code"):
            answer_explanation_str = ""
            for i in range(MAX_JINJIA_RETRY):
                success, answer_explanation_tmp = self.get_cached_result(
                    page_context, page_data, part="answer_explanation")
                if success:
                    answer_explanation_str = answer_explanation_tmp
                    break

            self.page_desc.answer_explanation = answer_explanation_str


    def get_question(self, page_context, page_data):
        self.update_page_desc(page_context, page_data)
        return super(LatexRandomCodeInlineMultiQuestion, self).get_question(page_context, page_data)

    def body(self, page_context, page_data):

        # blank_str = ""
        # if hasattr(self.page_desc, "blank_process_code"):
        #     success = False
        #     for i in range(MAX_JINJIA_RETRY):
        #         success, blank_str_tmp = self.get_cached_result(
        #             page_context, page_data, part="blank")
        #         if success:
        #             #markup_to_html(page_context, blank_str_tmp)
        #             break
        #
        #     if not success:
        #         if page_context.in_sandbox:
        #             blank_str = markup_to_html(page_context, blank_str_tmp)

        # blank_answer_str = ""
        # if hasattr(self.page_desc, "blank_answer_process_code"):
        #     blank_answer_str = ""
        #     success = False
        #     for i in range(MAX_JINJIA_RETRY):
        #         success, blank_answer_str_tmp = self.get_cached_result(
        #             page_context, page_data, part="blank_answer")
        #         if success:
        #             #markup_to_html(page_context,blank_answer_str_tmp)
        #             break
        #
        #     if not success:
        #         if page_context.in_sandbox:
        #             markup_to_html(page_context,blank_answer_str_tmp)
        #
        # answer_explanation_str = ""
        # if hasattr(self.page_desc, "answer_explanation_process_code"):
        #     success = False
        #     for i in range(MAX_JINJIA_RETRY):
        #         success, answer_explanation_str_tmp = self.get_cached_result(
        #             page_context, page_data, part="answer_explanation")
        #         if success:
        #             #markup_to_html(page_context, answer_explanation_str_tmp)
        #             break
        #
        #     if not success:
        #         if page_context.in_sandbox:
        #             answer_explanation_str = answer_explanation_str_tmp
        #             answer_explanation_str = markup_to_html(page_context,answer_explanation_str)

        return super(LatexRandomCodeInlineMultiQuestion, self).body(page_context, page_data) #+ blank_str #+ blank_answer_str + answer_explanation_str

    def required_attrs(self):
        return super(LatexRandomCodeInlineMultiQuestion, self).required_attrs() + (
            ("blank_process_code", str),
            ("blank_answer_process_code", str)
        )

    def allowed_attrs(self):
        return super(LatexRandomCodeInlineMultiQuestion, self).allowed_attrs() + (
            ("answer_explanation_process_code", str),
        )

    def grade(self, page_context, page_data, answer_data, grade_data):
        self.update_page_desc(page_context, page_data)
        return super(LatexRandomCodeInlineMultiQuestion, self).grade(
            page_context, page_data, answer_data, grade_data)


class LatexRandomCodeQuestionWithHumanTextFeedback(
    LatexRandomQuestion, PythonCodeQuestionWithHumanTextFeedback):
    pass


class LatexRandomMultipleChoiceQuestion(
    LatexRandomQuestion, MultipleChoiceQuestion):

    def initialize_page_data(self, page_context):
        m_page_data = MultipleChoiceQuestion.initialize_page_data(self, page_context)
        l_page_data = LatexRandomQuestion.initialize_page_data(self, page_context)
        page_data = dict(m_page_data, **l_page_data)
        return page_data


class LatexRandomChoiceQuestion(
    LatexRandomQuestion, ChoiceQuestion):

    def initialize_page_data(self, page_context):
        m_page_data = ChoiceQuestion.initialize_page_data(self, page_context)
        l_page_data = LatexRandomQuestion.initialize_page_data(self, page_context)
        page_data = dict(m_page_data, **l_page_data)
        return page_data