# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2018 Dong Zhuang"

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
from django.utils.translation import ugettext_lazy as _

from course.validation import validate_struct
from course.page.base import (
        PageBaseWithCorrectAnswer, PageBaseWithTitle, markup_to_html)
from django.conf.global_settings import LANGUAGES
from relate.utils import Struct


class CourseraPageBase(PageBaseWithCorrectAnswer, PageBaseWithTitle):
    """
    A page showing static content.

    .. attribute:: id

        |id-page-attr|

    .. attribute:: type

        ``Page``

    .. attribute:: access_rules

        |access-rules-page-attr|

    .. attribute:: title

        |title-page-attr|

    .. attribute:: content

        The page's content, in :ref:`markup`.

    .. attribute:: coursera_page_type

        The type of coursera page

    """

    def __init__(self, vctx, location, page_desc):
        super(CourseraPageBase, self).__init__(vctx, location, page_desc)

        if hasattr(page_desc, "src_root_url"):
            self.src_root_url = page_desc.src_root_url
        else:
            self.src_root_url = getattr(settings, "COURSE_RESOURCE_BASE_URL")

        if vctx is not None:
            for resource in page_desc.resources:
                self.validate_resource(vctx, location, resource)

    def required_attrs(self):
        return super(CourseraPageBase, self).required_attrs() + (
            ("title", str),
            ("resources", list),
            )

    def allowed_attrs(self):
        return super(CourseraPageBase, self).allowed_attrs() + (
                ("content", "markup"),
                ("src_root_url", "str"),
                )

    def build_resource_url(self, url):
        from six.moves.urllib.parse import urljoin
        return urljoin(self.src_root_url, url)

    def get_coursera_page_html(self):
        raise NotImplementedError()

    def validate_resource(self, vctx, location, resources):
        raise NotImplementedError()

    def expects_answer(self):
        return False


def get_subtitle_lang_from_url(url):
    import os
    name, __ = os.path.splitext(url)
    return name.split(".")[-1]


class CourseraVideoSubtitle(object):
    def __init__(self, url, is_default=False):
        self.url = url
        self.lang = get_subtitle_lang_from_url(url)
        self.lang_name = _(dict(LANGUAGES).get(self.lang, "English"))
        self.is_default = is_default


class CourseraVideo(object):
    def __init__(self, url, subtitle_urls=None):
        self.url = url

        self.subtitles = []
        if subtitle_urls:
            for i, subtitle_url in enumerate(subtitle_urls):
                is_default = False
                if i == 0:
                    is_default = True
                self.subtitles.append(
                    CourseraVideoSubtitle(subtitle_url, is_default))


class CourseraVideoPage(CourseraPageBase):
    def body(self, page_context, page_data):
        content = "# %s\n" % self.title(page_context, page_data)
        if getattr(self.page_desc, "content", ""):
            content += self.page_desc.content + "\n"
        return (
            markup_to_html(page_context, content) + self.get_coursera_page_html())

    def validate_resource(self, vctx, location, resource):
        validate_struct(
            vctx,
            "'resource' in %s" % location,
            resource,
            required_attrs=(
                ("url", str),
                ),
            allowed_attrs=(
                ("subtitle_urls", list),
                ("default_subtitle_url", str),
                ("asset_ids", Struct)
                ),
            )

    def get_coursera_page_html(self):
        videos = []
        for video in self.page_desc.resources:
            subtitle_urls = getattr(video, "default_subtitle_url", [])
            extra_subtitle_urls = list(
                set(getattr(video, "subtitle_urls", [])).difference(set(subtitle_urls)))
            subtitle_urls.extend(extra_subtitle_urls)
            subtitle_urls = [self.build_resource_url(url) for url in subtitle_urls]
            videos.append(
                CourseraVideo(self.build_resource_url(video.url), subtitle_urls))

        from django.template import loader
        context = {"videos": videos}

        return loader.render_to_string(
            "course/coursera-dl/coursera-dl-video-with-subtitle.html",
            context=context)


class CourseraHTMLPage(CourseraPageBase):

    def body(self, page_context, page_data):
        content = "# %s\n" % self.title(page_context, page_data)
        if getattr(self.page_desc, "content", ""):
            content += self.page_desc.content + "\n"
        return (
                markup_to_html(page_context,
                               content) + self.get_coursera_page_html())

    def validate_resource(self, vctx, location, resource):
        validate_struct(
            vctx,
            "'resource' in %s" % location,
            resource,
            required_attrs=(
                ("url", str),
                ),
            allowed_attrs=(
                ("asset_ids", Struct),
            ),
            )

    def get_coursera_page_html(self):
        from six.moves.urllib import request
        htmls = []
        for resource in self.page_desc.resources:
            from lxml.html.clean import Cleaner
            cleaner = Cleaner(
                style=True, scripts=True, forms=False,
                remove_unknown_tags=False, safe_attrs_only=False)
            with request.urlopen(self.build_resource_url(resource.url)) as response:
                htmls.append(cleaner.clean_html(response.read().decode()))

        from django.template import loader
        import json
        context = {"htmls": htmls,
                   "asset_ids":
                       json.dumps(getattr(self.page_desc.resources, "asset_ids", {}))}

        return loader.render_to_string(
            "course/coursera-dl/coursera-dl-html.html",
            context=context)

