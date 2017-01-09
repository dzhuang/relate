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

from django.conf.urls import url, include
from django.views.i18n import javascript_catalog

from course.constants import COURSE_ID_REGEX

from course_statistics.views import (
    view_stat_book,
    view_stat_by_question,
)
from image_upload.views import (
    ImageCreateView, ImageDeleteView, ImageListView,
    image_crop_modal, image_crop, image_order,
    user_image_download,
    flow_page_image_download,
    flow_page_image_problem,
    flow_page_image_key,
)
import crowdsourcing.urls

#from image_upload.page.imgupload import feedBackEmail

js_info_dict_image_upload = {
    'packages': ('image_upload',),
}

urlpatterns = [
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/statistics/stat-book/$",
        view_stat_book,
        name="relate-view_course_statistics"),
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/statistics/stat-by-ques"
        "/(?P<question_id>[a-zA-Z0-9_]+)"
        "/$",
        view_stat_by_question,
        name="relate-view_course_statistics_by_question"),
    url(r'^crowdsourcing/', include(crowdsourcing.urls)),
]
