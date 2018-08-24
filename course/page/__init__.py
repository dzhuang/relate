# -*- coding: utf-8 -*-

from __future__ import division

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

from django.conf import settings
from course.page.base import (
        InvalidPageData,
        PageBase, AnswerFeedback, PageContext, PageBehavior,
        get_auto_feedback,
        markup_to_html)
from course.page.static import Page
from course.page.text import (
        TextQuestion, SurveyTextQuestion, HumanGradedTextQuestion)
from course.page.inline import InlineMultiQuestion
from course.page.choice import (
        ChoiceQuestion, MultipleChoiceQuestion, SurveyChoiceQuestion)
from course.page.code import (
        PythonCodeQuestion, PythonCodeQuestionWithHumanTextFeedback)
from course.page.upload import FileUploadQuestion

try:
    settings_custom_page_classes = getattr(
        settings, "RELATE_CUSTOM_PAGE_CLASSES", None)

    if settings_custom_page_classes:
        for klass in settings_custom_page_classes:
            from django.utils.module_loading import import_string  # noqa
            from course.utils import get_valiated_custom_page_import_exec_str
            try:
                exec_string = get_valiated_custom_page_import_exec_str(klass)
                assert exec_string
                exec(exec_string)
            except Exception as e:
                raise ValueError(
                    "settings.RELATE_CUSTOM_PAGE_CLASSES: "
                    "Unable to import custom page class from "
                    "'%s'.\n%s: %s" % (str(klass), type(e).__name__, str(e))
                )
except Exception as e:
    from django.core.exceptions import AppRegistryNotReady
    if isinstance(e, AppRegistryNotReady):
        pass

__all__ = (
        "InvalidPageData",
        "PageBase", "AnswerFeedback", "PageContext", "PageBehavior",
        "get_auto_feedback",
        "markup_to_html",
        "Page",

        "TextQuestion", "SurveyTextQuestion", "HumanGradedTextQuestion",
        "InlineMultiQuestion",

        "ChoiceQuestion", "SurveyChoiceQuestion", "MultipleChoiceQuestion",
        "PythonCodeQuestion", "PythonCodeQuestionWithHumanTextFeedback",
        "FileUploadQuestion",

        "CourseraVideoPage", "CourseraHTMLPage"
)


__doc__ = """

.. autoclass:: PageBase
.. autoclass:: AnswerFeedback
.. autoclass:: PageContext

"""
