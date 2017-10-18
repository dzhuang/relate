# -*- coding: utf-8 -*-
# Usage
"""
coverage run manage.py test tests --local_test_settings test_local_settings.py
python manage.py test tests.test_my_local --local_test_settings test_local_settings.py

coverage run manage.py test tests.test_my_local.test_latexpage --local_test_settings test_local_settings.py
python manage.py test tests.test_my_local.test_latexpage --local_test_settings test_local_settings.py
"""

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
import os
import json
from .utils import skip_test, SKIP_LOCAL_TEST_REASON
from ..utils import mock
import zipfile
from six import BytesIO
from pymongo import MongoClient

from unittest import skipIf
from copy import deepcopy
from django.conf import settings
from django.urls import reverse, resolve
from django.core import mail
from django.test import TestCase
from django.contrib import messages

from django.test.utils import override_settings
from django.test import SimpleTestCase
from course.docker.config import (
    get_docker_client_config, get_relate_runpy_docker_client_config)

from django.core.exceptions import ImproperlyConfigured
from relate.utils import is_windows_platform, is_osx_platform
from course.constants import participation_status
from course.models import FlowSession, FlowPageData, FlowPageVisit
from image_upload.models import FlowPageImage

import docker.tls
import warnings

from ..base_test_mixins import (
    SINGLE_COURSE_SETUP_LIST, SingleCoursePageTestMixin,
    FallBackStorageMessageTestMixin, NONE_PARTICIPATION_USER_CREATE_KWARG_LIST,
    force_remove_path
)

from ..test_pages import MESSAGE_ANSWER_SAVED_TEXT, MESSAGE_ANSWER_FAILED_SAVE_TEXT
from ..test_sandbox import (
    SingleCoursePageSandboxTestBaseMixin, PAGE_WARNINGS, PAGE_ERRORS)
from .mixins import ImageUploadStorageTestMixin
from .sources import latex_sandbox
from .test_imageupload import MY_SINGLE_COURSE_SETUP_LIST
from image_upload.page.latexpage import (
    get_latex_page_mongo_collection as latex_page_collection,
    get_latex_page_commitsha_template_pair_collection as latex_page_sha_collection)


def disable_cache():
    raise ImproperlyConfigured


LATEXPAGE_FLOW_ID = "latex-flow"


class LatexPageMixin(SingleCoursePageTestMixin, FallBackStorageMessageTestMixin):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = LATEXPAGE_FLOW_ID

    def tearDown(self):  # noqa
        super(LatexPageMixin, self).tearDown()
        self.drop_test_mongo()

    def clear_cache(self):
        logged_in_user_id = self.c.session['_auth_user_id']
        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            return
        else:
            from plugins.latex.utils import get_latex_cache
            def_cache = get_latex_cache(cache)
            def_cache.clear()

        # in case the session cache is cleared so the user is logged out
        try:
            self.c.session['_auth_user_id']
        except KeyError:
            from django.contrib.auth import get_user_model
            logged_in_user = get_user_model().objects.get(pk=int(logged_in_user_id))
            self.c.force_login(logged_in_user)

    def latex_page_commitsha_mongo_items_count(self):
        return latex_page_sha_collection().count()

    def debug_print_latex_page_commitsha_mongo_collection(self, filter=None):
        if filter is None:
            filter = {}
        cursor = latex_page_sha_collection().find(filter)
        for doc in cursor:
            print(doc)

    def latex_page_mongo_items_count(self):
        return latex_page_collection().count()

    def debug_print_latex_page_mongo_collection(self, filter=None, doc_field="full"):
        if filter is None:
            filter = {}
        cursor = latex_page_collection().find(filter)
        for doc in cursor:
            if doc_field is None:
                print(doc)
            else:
                print(doc[doc_field])

    def drop_test_mongo(self):
        mongo_db_name = getattr(settings, "RELATE_MONGODB_NAME", None)
        assert mongo_db_name
        assert mongo_db_name.startswith("test_")
        uri = getattr(settings, "RELATE_MONGO_URI", None)
        assert uri is None

        def drop_mongo():
            client = MongoClient()
            client.drop_database(mongo_db_name)
        drop_mongo()


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageTest(LatexPageMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = LATEXPAGE_FLOW_ID

    def setUp(self):  # noqa
        super(LatexPageTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_quiz(self.flow_id)

    def test_1_success(self):
        page_id = "lp_dual_complimentary_slack1"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.client_post_answer_by_page_id(
            page_id, {"blank1": ["(5/4,19/4,3/2)^T"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_quiz()
        self.assertSessionScoreEqual(1)

    def test_1_wrong(self):
        page_id = "lp_dual_complimentary_slack1"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.client_post_answer_by_page_id(
            page_id, {"blank1": ["(1, 2, 3)^T"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_quiz()
        self.assertSessionScoreEqual(0)

    def test_1_fail(self):
        page_id = "lp_dual_complimentary_slack1"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.client_post_answer_by_page_id(
            page_id, {"blank1": ["1"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_quiz()
        self.assertSessionScoreEqual(0)

    def test_2_correct(self):
        page_id = "lp_dual_complimentary_slack2"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.client_post_answer_by_page_id(
            page_id, {"blank1": ["(5/2,5,1)^T"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_quiz()
        self.assertSessionScoreEqual(1)

    def test_2_wrong(self):
        page_id = "lp_dual_complimentary_slack2"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.client_post_answer_by_page_id(
            page_id, {"blank1": ["(1, 2, 3)^T"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_quiz()
        self.assertSessionScoreEqual(0)

    def test_2_fail(self):
        page_id = "lp_dual_complimentary_slack2"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.client_post_answer_by_page_id(
            page_id, {"blank1": ["1"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_quiz()
        self.assertSessionScoreEqual(0)

    def test_random(self):
        page_id = "lp_dual_complimentary_slack"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageSandboxTest(SingleCoursePageSandboxTestBaseMixin, LatexPageMixin,
                           TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    def test_latexpage_sandbox_preview_success(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHaveValidPage(resp)
        self.assertSandboxResponseContextEqual(resp, PAGE_ERRORS, None)
        self.assertSandboxResponseContextEqual(resp, PAGE_WARNINGS, [])

    def test_latexpage_sandbox_data_files_missing_random_question_data_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_DATA_FILES_MISSING_RAND_QUES_DATA_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS,
            "'foo' should be listed in 'data_files'")

    def test_latexpage_sandbox_no_random_question_data_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_NO_RANDOM_DATA_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS,
            "attribute 'random_question_data_file' missing")

    def test_latexpage_sandbox_missing_cachekey_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_CACHEKEY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS,
            "'foo' should be listed in 'data_files'")

    def test_latexpage_sandbox_missing_excluded_cachekey_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_EXCLUDED_CACHEKEY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHaveValidPage(resp)
        self.assertSandboxResponseContextEqual(resp, PAGE_ERRORS, None)
        self.assertSandboxWarningTextContain(
            resp, "'foo' is not in 'data_files'")

    def test_latexpage_sandbox_data_file_not_found(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_DATA_FILE_NOT_FOUND)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS, "data file 'foo' not found")

    def test_latexpage_sandbox_data_files_missing_runpy_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_DATA_FILES_MISSING_RUNPY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS,
            "'foo' should be listed in 'data_files'")

    def test_latexpage_sandbox_missing_runpy_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_RUNPY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHaveValidPage(resp)
        self.assertSandboxResponseContextEqual(resp, PAGE_ERRORS, None)
        self.assertSandboxWarningTextContain(
            resp, "LatexRandomCodeInlineMultiQuestion not using attribute "
                  "'runpy_file' is for debug only, it should not be used "
                  "in production.")

    def test_latexpage_sandbox_missing_runpy_file_missing_part_attrs(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_RUNPY_FILE_AND_MISSING_ATTR)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS, "'blank_answer_process_code' must be "
                               "configured when neiher 'runpy_file' nor "
                               "'full_processing_code' is configured.")

    def test_latexpage_sandbox_runpy_file_not_executable(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_RUNPY_FILE_NOT_EXECUTABLE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS,
            "'question-data/linear-programming/dual-theory/"
            "lp_dual_complementary_slack.tex' is not a valid Python script file."
            )

    def test_latexpage_sandbox_missing_cachekey_attribute(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_CACHEKEY_ATTRIBUTE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS, " attribute 'excluded_cache_key_files' not found")

    def test_latexpage_sandbox_page_error_with_cachekey_attribute_and_runpy_context(self):  # noqa
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_SUCCESS_WITH_CACHEKEY_ATTRIBUTE_AND_RUNPY_CONTEXT)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHaveValidPage(resp)
        self.assertSandboxResponseContextEqual(resp, PAGE_ERRORS, None)
        self.assertSandboxResponseContextEqual(resp, PAGE_WARNINGS, [])
        # the runpy_context introduced in this page is invalid.
        self.assertContains(resp, ("The page failed to be rendered. "
                                   "Sorry about that. The staff has been "
                                   "informed, and it will be fixed as soon "
                                   "as possible."))
        self.assertContains(resp, (
            "KeyError: 'question-data/linear-programming/linprog.py'"))

    def test_latexpage_sandbox_success_no_warm_up_by_sandbox(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_NO_WARMUP_BY_SANDBOX)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHaveValidPage(resp)
        self.assertSandboxResponseContextEqual(resp, PAGE_ERRORS, None)
        self.assertSandboxResponseContextEqual(resp, PAGE_WARNINGS, [])

    def test_latex_code_page_sandbox_success(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_CODE_QUESTION)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHaveValidPage(resp)
        self.assertSandboxResponseContextEqual(resp, PAGE_ERRORS, None)
        self.assertSandboxResponseContextEqual(resp, PAGE_WARNINGS, [])

    def test_latex_page_sandbox_bad_datatype(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_NOT_LIST_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS, ("'question-data/zero_length_set.bin' must "
                                "be dumped from a list or tuple"))

    def test_latex_page_sandbox_empty_list_data(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_EMPTY_LIST_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHaveValidPage(resp)
        self.assertSandboxResponseContextContains(
            resp, PAGE_ERRORS, ("'question-data/zero_length_list.bin'"
                                " seems to be empty, that's not valid"))


if six.PY3:
    import builtins  # noqa
else:
    import __builtin__ as builtins  # noqa

realimport = builtins.__import__


def my_disable_cache_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    mock import so as to disable cache
    usage:

    import six
    if six.PY3:
        mocking_import = "builtins.__import__"
    else:
        mocking_import = "__builtin__.__import__"
    with mock.patch(mocking_import, side_effect=my_disable_cache_import):
       do something
    """
    if name=="django.core.cache":
        raise ImproperlyConfigured
    return realimport(name, globals, locals, fromlist, level)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageInitalPageDataTest(LatexPageMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = LATEXPAGE_FLOW_ID
    # serialized_rollback = True

    commit_sha_with_same_content =b"bc48c6d16cc60bdbb2f0d097298f81f83dc50031"
    commit_sha_with_different_content = b"29d19f8301c5efd101eb2a3c7753a4ced868597f"

    def setUp(self):  # noqa
        super(LatexPageInitalPageDataTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_quiz(self.flow_id)

        self.page_id = page_id = "lp_dual_complimentary_slack1"
        self.c.get(self.get_page_url_by_page_id(page_id))
        # self.page_data = self.get_page_data()

    def get_page_data(self, page_id=None):
        if page_id is None:
            page_id = self.page_id
        return FlowPageData.objects.get(
            flow_session=FlowSession.objects.first(), page_id=page_id)

    def test_flow_page_data_no_question_data(self):
        # simulate that the question_data is empty, generate a new one
        page_data = self.get_page_data()
        original_question_data = page_data.data["question_data"]
        del page_data.data["question_data"]
        page_data.save()
        with mock.patch("course.content.get_course_commit_sha",
                        return_value=self.commit_sha_with_same_content):
            self.c.get(self.get_page_url_by_page_id(self.page_id))
            new_page_data = self.get_page_data()
            self.assertEqual(new_page_data.data["question_data"],
                             original_question_data)

    def test_flow_page_data_no_template_hash_and_id(self):
        # simulate that the tempate_hash and template_has_id are empty,
        # generate new ones
        page_data = self.get_page_data()
        original_page_data = deepcopy(page_data)
        del page_data.data["template_hash"]
        del page_data.data["template_hash_id"]
        page_data.save()
        with mock.patch("course.content.get_course_commit_sha",
                        return_value=self.commit_sha_with_same_content):
            self.c.get(self.get_page_url_by_page_id(self.page_id))
            new_page_data = self.get_page_data()
            self.assertEqual(new_page_data.data["template_hash"],
                             original_page_data.data["template_hash"])
            self.assertEqual(new_page_data.data["template_hash_id"],
                             original_page_data.data["template_hash_id"])


    def test_flow_page_new_mongo_entry_create_when_change_commit_sha(self):
        self.drop_test_mongo()
        self.clear_cache()
        self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 0)
        self.assertEqual(self.latex_page_mongo_items_count(), 0)

        with mock.patch("course.content.get_course_commit_sha",
                        return_value=self.commit_sha_with_same_content):
            self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 1)
        self.assertEqual(self.latex_page_mongo_items_count(), 1)

    def test_flow_page_runpy_content_changed(self):
        print("--------test started---------")

        from course.content import get_course_commit_sha
        current_commit_sha = get_course_commit_sha(
            self.course, self.student_participation)
        self.drop_test_mongo()
        self.clear_cache()
        self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 0)
        self.assertEqual(self.latex_page_mongo_items_count(), 0)

        import sys
        if sys.version_info >= (3,):
            mocking_import = "builtins.__import__"
        else:
            mocking_import = "__builtin__.__import__"

        self.update_course_to_commit_sha(self.commit_sha_with_same_content)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 1)
        self.assertEqual(self.latex_page_mongo_items_count(), 1)

        # print("--------------------------")
        # self.debug_print_latex_page_commitsha_mongo_collection()
        # print("--------------------------")
        # self.debug_print_latex_page_mongo_collection()

        self.update_course_to_commit_sha(self.commit_sha_with_different_content)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.latex_page_mongo_items_count(), 2)
        print("--------------------------")
        self.debug_print_latex_page_mongo_collection()

        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.latex_page_mongo_items_count(), 2)

        # print("--------------------------")
        # self.debug_print_latex_page_commitsha_mongo_collection()
        # print("--------------------------")
        # self.debug_print_latex_page_mongo_collection()

        self.update_course_to_commit_sha(current_commit_sha)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.latex_page_mongo_items_count(), 2)

        # self.c.get(self.get_page_url_by_page_id("lp_dual_complimentary_slack2"))
        # self.assertEqual(self.latex_page_commitsha_mongo_items_count(), 2)
        # self.assertEqual(self.latex_page_mongo_items_count(), 3)


        # print("--------------------------")
        # self.debug_print_latex_page_commitsha_mongo_collection()
        # print("--------------------------")
        # self.debug_print_latex_page_mongo_collection()