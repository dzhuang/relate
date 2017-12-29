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

import six
import datetime
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _

from course.models import Course
from course.views import EditCourseForm
from course.versioning import CourseCreationForm

from .base_test_mixins import SingleCourseTestMixin
from .test_views import DATE_TIME_PICKER_TIME_FORMAT

LANGUAGES = [
    ('en', _('English')),
    ('ko', _('Korean')),
    ('fr', _('French')),
]

ASSERSION_ERROR_LANGUAGE_PATTERN = (
    "%s page visiting results don't match in terms of "
    "whether the response contains Korean characters."
)

ASSERSION_ERROR_CONTENT_LANGUAGE_PATTERN = (
    "%s page visiting result don't match in terms of "
    "whether the response content-language are restored."
)

VALIDATION_ERROR_LANG_NOT_SUPPORTED_PATTERN = (
    "'%s' is currently not supported as a course specific language at "
    "this site."
)


class CourseSpecificLangTestMixin(SingleCourseTestMixin, TestCase):
    # {{{ assertion method
    def response_contains_korean(self, resp):
        # Korean literals for 12th month (December)
        return "12월" in resp.content.decode("utf-8")

    def assertResponseContainsChinese(self, resp):  # noqa
        self.assertTrue(self.response_contains_korean(resp))

    def assertResponseNotContainsChinese(self, resp):  # noqa
        self.assertFalse(self.response_contains_korean(resp))

    # }}}

    # {{{ common tests
    def resp_info_with_diff_settings(self, url):
        contains_korean_result = []
        response_content_language_result = []

        with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
            resp = self.c.get(url)
            self.assertEqual(resp.status_code, 200)
            contains_korean_result.append(self.response_contains_korean(resp))
            response_content_language_result.append(resp['content-language'])

            resp = self.c.get(url, HTTP_ACCEPT_LANGUAGE='ko')
            self.assertEqual(resp.status_code, 200)
            contains_korean_result.append(self.response_contains_korean(resp))
            response_content_language_result.append(resp['content-language'])

        with override_settings(USE_I18N=False):
            resp = self.c.get(url)
            self.assertEqual(resp.status_code, 200)
            contains_korean_result.append(self.response_contains_korean(resp))
            response_content_language_result.append(resp['content-language'])

            resp = self.c.get(url, HTTP_ACCEPT_LANGUAGE='ko')
            self.assertEqual(resp.status_code, 200)
            contains_korean_result.append(self.response_contains_korean(resp))
            response_content_language_result.append(resp['content-language'])

        return contains_korean_result, response_content_language_result

    def home_resp_contains_korean_with_diff_settings(self):
        return self.resp_info_with_diff_settings("/")

    def course_resp_contains_korean_with_diff_settings(self):
        return self.resp_info_with_diff_settings(self.course_page_url)

    # }}}


class CourseSpecificLangConfigureTest(CourseSpecificLangTestMixin, TestCase):
    # By default, self.course.force_lang is None

    def setUp(self):
        super(CourseSpecificLangConfigureTest, self).setUp()
        # We use faked time header to find out whether the expected Chinese
        # characters are rendered
        self.c.force_login(self.instructor_participation.user)
        fake_time = datetime.datetime(2038, 12, 31, 0, 0, 0, 0)
        set_fake_time_data = {
            "time": fake_time.strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "set": ['']}
        self.post_set_fake_time(set_fake_time_data)

    def assertResponseBehaveLikeUnconfigured(self):  # noqa
        # For each setting combinations, the response behaves the same
        # as before this functionality was introduced
        expected_result = ([False, True, False, True],
                           ['en', 'ko', 'en', 'ko'])
        self.assertEqual(
            self.home_resp_contains_korean_with_diff_settings()[0],
            expected_result[0],
            ASSERSION_ERROR_LANGUAGE_PATTERN % "Home"
        )

        self.assertEqual(
            self.home_resp_contains_korean_with_diff_settings()[1],
            expected_result[1],
            ASSERSION_ERROR_CONTENT_LANGUAGE_PATTERN % "Home"
        )

        expected_result = ([False, True, False, True],
                           ['en', 'ko', 'en', 'ko'])
        self.assertEqual(
            self.course_resp_contains_korean_with_diff_settings()[0],
            expected_result[0],
            ASSERSION_ERROR_LANGUAGE_PATTERN % "Course"
        )
        self.assertEqual(
            self.course_resp_contains_korean_with_diff_settings()[1],
            expected_result[1],
            ASSERSION_ERROR_CONTENT_LANGUAGE_PATTERN % "Course"
        )

    def assertResponseBehaveAsExpectedForCourseWithForceLang(self):  # noqa
        # For each setting combinations, the response behaves as expected
        expected_result = ([False, True, False, True],
                           ['en', 'ko', 'en', 'ko'])
        self.assertEqual(
            self.home_resp_contains_korean_with_diff_settings()[0],
            expected_result[0],
            ASSERSION_ERROR_LANGUAGE_PATTERN % "Home"
        )

        self.assertEqual(
            self.home_resp_contains_korean_with_diff_settings()[1],
            expected_result[1],
            ASSERSION_ERROR_CONTENT_LANGUAGE_PATTERN % "Home"
        )

        expected_result = ([True, True, True, True],
                           ['en', 'ko', 'en', 'ko'])
        self.assertEqual(
            self.course_resp_contains_korean_with_diff_settings()[0],
            expected_result[0],
            ASSERSION_ERROR_LANGUAGE_PATTERN % "Course"
        )
        self.assertEqual(
            self.course_resp_contains_korean_with_diff_settings()[1],
            expected_result[1],
            ASSERSION_ERROR_CONTENT_LANGUAGE_PATTERN % "Course"
        )

    def set_course_lang_to_zh_hans(self):
        self.course.force_lang = "ko"
        self.course.save()
        self.course.refresh_from_db()

    def test_recsl_configured_true_lang_not_configured(self):
        self.assertResponseBehaveLikeUnconfigured()

    def test_recsl_configured_true_lang_not_configured_course_has_force_lang(self):
        self.set_course_lang_to_zh_hans()
        self.assertResponseBehaveAsExpectedForCourseWithForceLang()

    @override_settings(LANGUAGES=LANGUAGES)
    def test_recsl_configured_true_lang_configured(self):
        # because self.course.force_lang is None
        self.assertResponseBehaveLikeUnconfigured()

    @override_settings(LANGUAGES=LANGUAGES)
    def test_recsl_configured_true_lang_configured_course_has_force_lang(self):
        self.set_course_lang_to_zh_hans()
        self.assertResponseBehaveAsExpectedForCourseWithForceLang()


class CourseSpecificLangFormTest(SingleCourseTestMixin, TestCase):

    def copy_course_dict_and_set_lang_for_post(self, lang):
        kwargs = Course.objects.first().__dict__
        kwargs["force_lang"] = lang
        for k, v in six.iteritems(kwargs):
            if v is None:
                kwargs[k] = ""
        return kwargs

    def test_edit_course_force_lang_invalid(self):
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("foo")
        form = EditCourseForm(course_kwargs, instance=self.course)
        self.assertTrue("force_lang" in form.fields)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["force_lang"][0],
                         VALIDATION_ERROR_LANG_NOT_SUPPORTED_PATTERN % "foo")

    def test_edit_course_force_lang_valid(self):
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("de")
        form = EditCourseForm(course_kwargs, instance=self.course)
        self.assertTrue(form.is_valid())

    def test_create_course_force_lang_invalid(self):
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("foo")
        course_kwargs["identifier"] = "another-test-course"
        expected_course_count = Course.objects.count()
        form = CourseCreationForm(course_kwargs)
        self.assertTrue("force_lang" in form.fields)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["force_lang"][0],
                         VALIDATION_ERROR_LANG_NOT_SUPPORTED_PATTERN % "foo")
        self.assertEqual(Course.objects.count(), expected_course_count)

# vim: foldmethod=marker
