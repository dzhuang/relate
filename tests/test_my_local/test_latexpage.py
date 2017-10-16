# -*- coding: utf-8 -*-

# coverage run manage.py test tests --local_test_settings test_local_settings.py
# python manage.py test tests.test_my_local --local_test_settings test_local_settings.py

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

import os
import json
from .utils import skip_test, SKIP_LOCAL_TEST_REASON
from ..utils import mock
import zipfile
from six import BytesIO

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
from course.models import FlowSession
from image_upload.models import FlowPageImage

import docker.tls
import warnings

from ..base_test_mixins import (
    SINGLE_COURSE_SETUP_LIST, SingleCoursePageTestMixin,
    FallBackStorageMessageTestMixin, NONE_PARTICIPATION_USER_CREATE_KWARG_LIST,
    force_remove_path
)

from ..test_pages import MESSAGE_ANSWER_SAVED_TEXT, MESSAGE_ANSWER_FAILED_SAVE_TEXT
from ..test_sandbox import SingleCoursePageSandboxTestBaseMixin
from .mixins import ImageUploadStorageTestMixin

MY_SINGLE_COURSE_SETUP_LIST = deepcopy(SINGLE_COURSE_SETUP_LIST)
MY_SINGLE_COURSE_SETUP_LIST[0]["course"]["git_source"] = (
    "https://code.aliyun.com/dzhuang/my_learningwhat_test_repo.git")
IMAGE_UPLOAD_FLOW = "image-upload-flow"
TEST_IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_IMAGE1 = os.path.join(TEST_IMAGE_FOLDER, "test1.jpg")
TEST_IMAGE2 = os.path.join(TEST_IMAGE_FOLDER, "test2.png")

LATEXPAGE_FLOW_ID = "latex-flow"


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageTest(SingleCoursePageTestMixin,
                    FallBackStorageMessageTestMixin, TestCase):

    flow_id = LATEXPAGE_FLOW_ID

    def setUp(self):  # noqa
        super(LatexPageTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_quiz(self.flow_id)

    def tearDown(self):
        super(LatexPageTest, self).tearDown()
        mongo_db_name = getattr(settings, "RELATE_MONGODB_NAME", None)
        assert mongo_db_name
        assert mongo_db_name.startswith("test_")
        uri = getattr(settings, "RELATE_MONGO_URI", None)
        assert uri is None

        def drop_mongo():
            from plugins.latex.utils import get_mongo_db
            DB = get_mongo_db()
            from pymongo import MongoClient
            client = MongoClient()
            client.drop_database(mongo_db_name)
        drop_mongo()

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
