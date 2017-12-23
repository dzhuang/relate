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
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from course.models import Course

from .base_test_mixins import SingleCourseTestMixin


COURSE_LANGUAGES = [
    ('en', _('English')),
    ('zh-cn', _('Simplified Chinese')),
    ('de', _('German')),
]


VALIDATION_ERROR_LANG_NOT_SUPPORTED_PATTERN = (
    "'%s' is currently not supported as a course specific language at "
    "this site"
)


class CourseSpecificLangTestMixin(SingleCourseTestMixin, TestCase):
    # This is needed when the course is created by post method (instead of db)
    # Or it won't pass validation
    override_settings_at_post_create_course = {"COURSE_LANGUAGES": COURSE_LANGUAGES}

    def setUp(self):  # noqa
        super(CourseSpecificLangTestMixin, self).setUp()
        self.c.force_login(self.instructor_participation.user)
        self.override_enable_course_specific_lang_setting = (
            override_settings(RELATE_ENABLE_COURSE_SPECIFIC_LANG=True)
        )
        self.override_course_langs_settings = (
            override_settings(COURSE_LANGUAGES=COURSE_LANGUAGES))
        self.override_enable_course_specific_lang_setting.enable()
        self.override_course_langs_settings.enable()
        self.addCleanup(self.override_course_langs_settings.disable)
        self.addCleanup(self.override_enable_course_specific_lang_setting.disable)

    def tearDown(self):
        self.c.logout()

    # {{{ assertion method
    def assertResponseLanguageIn(self, resp, langs):  # noqa
        assert isinstance(langs, (list, tuple))
        self.assertIn(resp['content-language'], langs)

    def assertResponseLanguageIsEnglish(self, resp):  # noqa
        # when RELATE_ENABLE_COURSE_SPECIFIC_LANG is not enabled
        # the response language is 'en', when enabled, it is 'en-us'
        return self.assertResponseLanguageIn(resp, ['en', 'en-us'])

    def assertResponseLanguageIsChinese(self, resp):  # noqa
        # when RELATE_ENABLE_COURSE_SPECIFIC_LANG is not enabled
        # the response language is 'en', when enabled, it is 'en-us'
        return self.assertResponseLanguageIn(resp, ['zh-cn', 'zh-hans'])
    # }}}

    # {{{ common tests
    def settings_not_configured_or_course_not_configured_expected_behaviors(self):
        resp = self.c.get(self.course_page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertResponseLanguageIsEnglish(resp)

        resp = self.c.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertResponseLanguageIsEnglish(resp)

        # When user is using browser with send request with
        # "HTTP_ACCEPT_LANGUAGE" in META, it display chinese no matter
        # whether "USE_I18N" is configured
        resp = self.c.get(
            self.course_page_url, HTTP_ACCEPT_LANGUAGE='zh-cn')
        self.assertEqual(resp.status_code, 200)
        self.assertResponseLanguageIsChinese(resp)

        resp = self.c.get(
            "/", HTTP_ACCEPT_LANGUAGE='zh-cn')
        self.assertEqual(resp.status_code, 200)
        self.assertResponseLanguageIsChinese(resp)

    def course_with_zh_lang_expected_behaviors(self):
        resp = self.c.get("/")
        # request to home page is out of course context
        self.assertEqual(resp.status_code, 200)
        self.assertResponseLanguageIsEnglish(resp)

        # It displays Chinese regardless of whether the request has
        # HTTP_ACCEPT_LANGUAGE in META
        resp = self.c.get(self.course_page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertResponseLanguageIsChinese(resp)

        resp = self.c.get(self.course_page_url, HTTP_ACCEPT_LANGUAGE='en-us')
        self.assertEqual(resp.status_code, 200)
        self.assertResponseLanguageIsChinese(resp)

        # This is of course the case
        resp = self.c.get(self.course_page_url, HTTP_ACCEPT_LANGUAGE='zh-cn')
        self.assertResponseLanguageIsChinese(resp)

    # }}}


class CourseSpecificLangConfigureTest(CourseSpecificLangTestMixin, TestCase):
    def test_csl_settings_not_enabled(self):
        with override_settings(RELATE_ENABLE_COURSE_SPECIFIC_LANG=False):
            with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
                self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa
            with override_settings(USE_I18N=False):
                self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa

    def test_csl_settings_not_configured(self):
        # When RELATE_ENABLE_COURSE_SPECIFIC_LANG is not configure
        # it is not enabled.
        del settings.RELATE_ENABLE_COURSE_SPECIFIC_LANG
        with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
            self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa
        with override_settings(USE_I18N=False):
            self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa

    def test_neither_cls_settings_and_course_langs_settings_configured(self):
        del settings.COURSE_LANGUAGES
        with override_settings(RELATE_ENABLE_COURSE_SPECIFIC_LANG=False):
            with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
                self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa
            with override_settings(USE_I18N=False):
                self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa

    def test_both_settings_configured_but_course_not_configured(self):
        # courses which not using that field will work as before
        with override_settings(USE_I18N=True, LANGUAGE_CODE='en-us'):
            self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa
        with override_settings(USE_I18N=False):
            self.settings_not_configured_or_course_not_configured_expected_behaviors()  # noqa


class CourseSpecificLangBehaviorTest(CourseSpecificLangTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        super(CourseSpecificLangBehaviorTest, cls).setUpTestData()
        cls.course.force_lang = "zh-cn"
        cls.course.save()

    @override_settings(USE_I18N=True, LANGUAGE_CODE='en-us')
    def test_expected_behavior_with_i18n_enabled(self):
        self.course_with_zh_lang_expected_behaviors()  # noqa

    @override_settings(USE_I18N=False)
    def test_expected_behavior_with_i18n_disabled(self):
        self.course_with_zh_lang_expected_behaviors()  # noqa

    def test_course_save_non_force_lang_behavior(self):
        self.course.force_lang = ""
        self.course.save()
        self.course.refresh_from_db()
        self.settings_not_configured_or_course_not_configured_expected_behaviors()

    def copy_course_dict_and_set_lang_for_post(self, lang):
        kwargs = Course.objects.first().__dict__
        kwargs["force_lang"] = lang
        for k, v in six.iteritems(kwargs):
            if v is None:
                kwargs[k] = ""
        return kwargs

    def test_edit_course_force_lang_invalid(self):
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("foo")
        resp = self.post_edit_course(data=course_kwargs)
        self.assertFormError(resp, "form", "force_lang",
                             VALIDATION_ERROR_LANG_NOT_SUPPORTED_PATTERN % "foo")
        self.course.refresh_from_db()
        self.assertEqual(self.course.force_lang, "zh-cn")

    def test_edit_course_force_lang_valid(self):
        langs = COURSE_LANGUAGES + [("foo", "Some other language"), ]
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("foo")

        with override_settings(COURSE_LANGUAGES=langs):
            resp = self.post_edit_course(data=course_kwargs)

        self.assertEqual(resp.status_code, 200)
        self.course.refresh_from_db()
        self.assertEqual(self.course.force_lang, "foo")

    def test_edit_course_force_lang_invalid_in_global_lang(self):
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("zh-hans")
        resp = self.post_edit_course(data=course_kwargs)
        self.assertFormError(resp, "form", "force_lang",
                         VALIDATION_ERROR_LANG_NOT_SUPPORTED_PATTERN % "zh-hans")
        self.course.refresh_from_db()
        self.assertEqual(self.course.force_lang, "zh-cn")

    def test_edit_course_force_lang_valid_course_lang_not_configured(self):
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("zh-hans")

        del settings.COURSE_LANGUAGES
        resp = self.post_edit_course(data=course_kwargs)
        self.assertEqual(resp.status_code, 200)
        self.course.refresh_from_db()
        self.assertEqual(self.course.force_lang, "zh-hans")

    def test_create_course_force_lang_invalid(self):
        course_kwargs = self.copy_course_dict_and_set_lang_for_post("foo")
        course_kwargs["identifier"] = "another-test-course"
        course_count = Course.objects.count()
        resp = self.post_create_course(raise_error=False, **course_kwargs)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Course.objects.count(), course_count)

# vim: foldmethod=marker
