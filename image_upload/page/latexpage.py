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

from io import BytesIO
import pickle

from django.core.exceptions import ObjectDoesNotExist

from course.page import markup_to_html
from course.page.base import PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback, \
    PageBaseWithCorrectAnswer
from course.validation import ValidationError
from course.content import get_repo_blob

from image_upload.page.imgupload import ImageUploadQuestion
from course.page.code import PythonCodeQuestion, PythonCodeQuestionWithHumanTextFeedback

from course.page.code import request_python_run_with_retries

class LatexRandomQuestion(PageBaseWithTitle, PageBaseWithValue,
                          PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer):
    def __init__(self, vctx, location, page_desc):
        super(LatexRandomQuestion, self).__init__(vctx, location, page_desc)

        # self.question_data_files_list = []
        # self.question_data_file = ""
        # if isinstance(page_desc.question_data_files, str):
        #     self.question_data_files_list = [page_desc.question_data_files]
        #     self.question_data_file = page_desc.question_data_files
        # else:
        #     self.question_data_files_list = page_desc.question_data_files
        #     self.question_data_file = self.question_data_files_list[0]
        #
        # val_file_list = self.question_data_files_list
        # if hasattr(page_desc, "setup_code_file"):
        #     val_file_list += page_desc.setup_code_file
        #
        # if vctx is not None:
        #     for data_file in val_file_list:
        #         try:
        #             if not isinstance(data_file, str):
        #                 raise ObjectDoesNotExist()
        #
        #             from course.content import get_repo_blob
        #             get_repo_blob(vctx.repo, data_file, vctx.commit_sha)
        #
        #         except ObjectDoesNotExist:
        #             raise ValidationError("%s: file '%s' not found"
        #                     % (location, data_file))


        if vctx is not None and hasattr(page_desc, "data_files"):
            if hasattr(page_desc, "data_file_for_page_data"):
                if not page_desc.data_file_for_page_data in page_desc.data_files:
                    raise ValidationError("%s: '%s' should be listed in 'data_files'"
                                          % (location, page_desc.data_file_for_page_data))
            for data_file in page_desc.data_files:
                try:
                    if not isinstance(data_file, str):
                        raise ObjectDoesNotExist()

                    from course.content import get_repo_blob
                    get_repo_blob(vctx.repo, data_file, vctx.commit_sha)
                except ObjectDoesNotExist:
                    raise ValidationError("%s: data file '%s' not found"
                            % (location, data_file))

        self.question_process_code = getattr(page_desc, "question_process_code", None)
        self.answer_process_code = getattr(page_desc, "answer_process_code", None)
        self.data_file_for_page_data = getattr(page_desc, "answer_process_code", None)
        self.page_context = None

    def required_attrs(self):
        return super(LatexRandomQuestion, self).required_attrs() + (
            ("data_files", (list,str)),
            ("question_process_code", str),
        )

    def allowed_attrs(self):
        return super(LatexRandomQuestion, self).allowed_attrs() + (
            ("data_file_for_page_data", str),
            ("setup_code_file", list),
            ("latex_template_file", list),
            ("setup_code", str),
            ("answer_process_code", str),
        )

    def make_page_data(self, page_context):
        if not hasattr(self.page_desc, "data_file_for_page_data"):
            return {}
        repo_bytes_data = get_repo_blob(
            page_context.repo,
            self.page_desc.data_file_for_page_data,
            page_context.commit_sha).data
        bio = BytesIO(repo_bytes_data)
        repo_data_loaded = pickle.load(bio)
        if not isinstance(repo_data_loaded, (list, tuple)):
            return {}
        n_data = len(repo_data_loaded)
        if n_data <= 1:
            return {}
        import random
        all_data = list(repo_data_loaded)
        random.shuffle(all_data)
        random_data = all_data[0]
        selected_data_bytes = BytesIO()
        pickle.dump(random_data, selected_data_bytes)

        from base64 import b64encode

        problem_data = b64encode(selected_data_bytes.getvalue()).decode()

        return {"problem_data": problem_data}

    def get_problem_data(self, page_context, page_data):
        if page_context.in_sandbox or page_data is None:
            page_data = self.make_page_data(page_context)

        if page_data:
            problem_b64_data = page_data["problem_data"]
            from base64 import b64decode
            problem_bytes_data = b64decode(problem_b64_data)
            from io import BytesIO
            import pickle
            bio = BytesIO(problem_bytes_data)
            problem_data = pickle.load(bio)

            return problem_data
        else:
            return None

    def body(self, page_context, page_data):
        try:
            exec self.process_code
        except:
            pass
            #raise

        from latex_utils.utils import latex_jinja_env

        # l = self.get_problem_data(page_context, page_data)
        # l.solve()
        # template = latex_jinja_env.get_template('latex_utils/utils/lp_simplex.tex')
        # tex = template.render(
        #     show_question = True,
        #     pre_description=u"""
        #         """,
        #     lp=l,
        #     simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
        #         """,
        #     simplex_after_description=u"""最优解唯一。
        #         """
        # )

        return super(LatexRandomQuestion, self).body(page_context, page_data) #+ markup_to_html(page_context, tex)

    # def correct_answer(self, page_context, page_data, answer_data, grade_data):
    #     from latex_utils.utils import latex_jinja_env
    #
    #     l = self.get_problem_data(page_context, page_data)
    #     l.solve()
    #     template = latex_jinja_env.get_template('latex_utils/utils/lp_simplex.tex')
    #     tex = template.render(
    #         show_answer = True,
    #         pre_description=u"""
    #             """,
    #         lp=l,
    #         simplex_pre_description=u"""解：引入松弛变量$x_4, x_5, x_6$，用单纯形法求解如下：
    #             """,
    #         simplex_after_description=u"""最优解唯一。
    #             """
    #     )
    #     return markup_to_html(page_context, tex)


class LatexRandomImageUploadQuestion(LatexRandomQuestion, ImageUploadQuestion):
    pass


class LatexRandomCodeQuestion(LatexRandomQuestion, PythonCodeQuestion):
    pass

class LatexRandomCodeQuestionWithHumanTextFeedback(
    LatexRandomQuestion, PythonCodeQuestionWithHumanTextFeedback):
    pass