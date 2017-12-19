# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2017 Dong Zhuang"

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

from django.test import TestCase  # noqa
import time  # noqa
from .base_test_mixins import SingleCourseTestMixin, TwoCoursePageTestMixin  # noqa
from .test_auth import TWO_COURSE_SETUP_LIST
import os
from django.test import SimpleTestCase
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.test.utils import override_settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .utils import mock

COURSE_LANGUAGES = [
    ('en', _('English')),
    ('zh-cn', _('Simplified Chinese')),
    ('de', _('German')),
]


class CourseSpecificLangMixin(TwoCoursePageTestMixin):
    courses_setup_list = TWO_COURSE_SETUP_LIST
    courses_attributes_extra_list = [{}, {"force_lang": "zh-cn"}]
    literals = ["Admin site"]

    def setUp(self):
        super(CourseSpecificLangMixin, self).setUp()
        self.c.force_login(self.course1_instructor_participation.user)

    def assertResponseNotContainsLiterals(self, resp):
        for char in self.literals:
            self.assertNotContains(resp, char)

    def assertResponseContainsLiterals(self, resp):
        for char in self.literals:
            self.assertContains(resp, char)


class CourseSpecificLangDisabledMixin(CourseSpecificLangMixin):
    @override_settings(RELATE_ENABLE_COURSE_SPECIFIC_LANG=False)
    def test_relate_enable_course_specific_lang_not_enabled(self):
        with override_settings(USE_I18N=False):
            resp = self.c.get(self.course2_page_url)
            self.assertResponseContainsLiterals(resp)

        with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
            resp = self.c.get(self.course2_page_url)
            self.assertResponseContainsLiterals(resp)

        with override_settings(USE_I18N=False):
            # When user is using browser with send request with
            # "HTTP_ACCEPT_LANGUAGE" in META, it display chinese no matter
            # whether "USE_I18N" is configured
            resp = self.c.get(
                self.course2_page_url, HTTP_ACCEPT_LANGUAGE='zh-hans')
            self.assertResponseNotContainsLiterals(resp)

        with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
            resp = self.c.get(
                self.course2_page_url, HTTP_ACCEPT_LANGUAGE='zh-hans')
            self.assertResponseNotContainsLiterals(resp)

        with override_settings(USE_I18N=True, LANGUAGE_CODE='zh-hans'):
            # if LANGUAGE_CODE is Chinese, it displays Chinese
            resp = self.c.get(self.course2_page_url)
            self.assertResponseNotContainsLiterals(resp)


class CourseSpecificLangEnabledMixin(CourseSpecificLangMixin):
    @override_settings(RELATE_ENABLE_COURSE_SPECIFIC_LANG=True)
    def test_relate_enable_course_specific_lang_enabled(self):
        with override_settings(USE_I18N=False):
            # viewing course 2, which configure force_lang to zh-hans
            # thought i18n is not configured, it displays Chinese
            resp = self.c.get(self.course2_page_url)
            self.assertResponseNotContainsLiterals(resp)

            # for course 1, with force_lang left unconfigured
            # it doesn't display Chinese with no language request
            resp = self.c.get(self.course1_page_url)
            self.assertResponseContainsLiterals(resp)

            # with language request, it displays Chinese
            resp = self.c.get(
                self.course1_page_url, HTTP_ACCEPT_LANGUAGE='zh-hans')
            self.assertResponseNotContainsLiterals(resp)

        with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
            # {{{ viewing course 2
            # It displays Chinese, overrided LANGUAGE_CODE, disregarding browser
            # preference
            resp = self.c.get(self.course2_page_url)
            self.assertResponseNotContainsLiterals(resp)

            resp = self.c.get(
                self.course2_page_url, HTTP_ACCEPT_LANGUAGE='zh-hans')
            self.assertResponseNotContainsLiterals(resp)
            # }}}

            # {{{ viewing course 1
            # it doesn't display Chinese with no language request
            resp = self.c.get(self.course1_page_url)
            self.assertResponseContainsLiterals(resp)

            # with language request, it displays Chinese
            resp = self.c.get(
                self.course1_page_url, HTTP_ACCEPT_LANGUAGE='zh-hans')
            self.assertResponseNotContainsLiterals(resp)
            # }}}

            # {{{ viewing home page
            # it doesn't display Chinese with no language request
            resp = self.c.get("/")
            self.assertResponseContainsLiterals(resp)

            # with language request, it displays Chinese
            resp = self.c.get(
                "/", HTTP_ACCEPT_LANGUAGE='zh-hans')
            self.assertResponseNotContainsLiterals(resp)

            # }}}


@override_settings(COURSE_LANGUAGES=COURSE_LANGUAGES)
class CourseSpecificLangDisabledWithLang(CourseSpecificLangDisabledMixin, TestCase):
    pass


@override_settings(RELATE_ENABLE_COURSE_SPECIFIC_LANG=False)
class CourseSpecificLangDisabledWithNoLang(CourseSpecificLangDisabledMixin,
                                           TestCase):
    def setUp(self):
        super(CourseSpecificLangDisabledWithNoLang, self).setUp()
        del settings.COURSE_LANGUAGES


@override_settings(COURSE_LANGUAGES=COURSE_LANGUAGES)
class CourseSpecificLangEnabledWithLang(CourseSpecificLangEnabledMixin, TestCase):
    pass


@override_settings(RELATE_ENABLE_COURSE_SPECIFIC_LANG=True)
class CourseSpecificLangEnabledWithNoLang(CourseSpecificLangEnabledMixin, TestCase):
    def setUp(self):
        super(CourseSpecificLangEnabledWithNoLang, self).setUp()
        del settings.COURSE_LANGUAGES

# vim: foldmethod=marker
