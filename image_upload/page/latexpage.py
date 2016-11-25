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

   