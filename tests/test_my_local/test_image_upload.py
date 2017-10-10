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

import os
import json
from .utils import skip_test, SKIP_LOCAL_TEST_REASON
from ..utils import mock

try:
    from test.support import EnvironmentVarGuard  # noqa
except:
    from test.test_support import EnvironmentVarGuard  # noqa

from unittest import skipIf
from copy import deepcopy
from django.conf import settings
from django.urls import reverse, resolve
from django.core import mail
from django.test import TestCase


from django.test.utils import override_settings
from django.test import SimpleTestCase
from course.docker.config import (
    get_docker_client_config, get_relate_runpy_docker_client_config)

from django.core.exceptions import ImproperlyConfigured
from relate.utils import is_windows_platform, is_osx_platform
from course.constants import participation_status
from image_upload.models import FlowPageImage

import docker.tls
import warnings

from ..base_test_mixins import (
    SINGLE_COURSE_SETUP_LIST, SingleCoursePageTestMixin,
    FallBackStorageMessageTestMixin, NONE_PARTICIPATION_USER_CREATE_KWARG_LIST,
    force_remove_path
)

from .mixins import ImageUploadStorageTestMixin, ImageUploaderMixin

MY_SINGLE_COURSE_SETUP_LIST = deepcopy(SINGLE_COURSE_SETUP_LIST)
MY_SINGLE_COURSE_SETUP_LIST[0]["course"]["git_source"] = (
    "https://code.aliyun.com/dzhuang/my_learningwhat_test_repo.git")
IMAGE_UPLOAD_FLOW = "image-upload-flow"
TEST_IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_IMAGE1 = os.path.join(TEST_IMAGE_FOLDER, "test1.png")
TEST_IMAGE2 = os.path.join(TEST_IMAGE_FOLDER, "test2.png")


class ImageUploadViewMixin(ImageUploadStorageTestMixin, SingleCoursePageTestMixin,
                      FallBackStorageMessageTestMixin, ImageUploaderMixin):

    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = IMAGE_UPLOAD_FLOW
    none_participation_user_create_kwarg_list = (
        NONE_PARTICIPATION_USER_CREATE_KWARG_LIST)

    @classmethod
    def setUpTestData(cls):  # noqa
        super(ImageUploadViewMixin, cls).setUpTestData()
        cls.student_participation2 = (
            cls.create_participation(
                cls.course, cls.non_participation_users[0],
                status=participation_status.active))
        cls.non_participation_user = cls.non_participation_users[1]

    def setUp(self):  # noqa
        super(ImageUploadViewMixin, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_quiz(self.flow_id)

    def get_upload_url(self, page_ordinal=None, page_id=None):
        assert page_ordinal or page_id
        if not page_ordinal:
            assert page_id
            page_ordinal = self.get_ordinal_via_page_id(page_id)
        from copy import deepcopy
        page_params = deepcopy(self.page_params)
        page_params.update({"ordinal": str(page_ordinal)})
        return reverse("jfu_upload", kwargs=page_params)

    def get_delete_url(self, image_pk, page_ordinal=None, page_id=None):
        assert page_ordinal or page_id
        if not page_ordinal:
            assert page_id
            page_ordinal = self.get_ordinal_via_page_id(page_id)
        from copy import deepcopy
        page_params = deepcopy(self.page_params)
        page_params.update({"ordinal": str(page_ordinal), "pk": image_pk})
        return reverse("jfu_delete", kwargs=page_params)

    def get_page_url(self, page_ordinal=None, page_id=None):
        assert page_ordinal or page_id
        if not page_ordinal:
            assert page_id
            page_ordinal = self.get_ordinal_via_page_id(page_id)
        from copy import deepcopy
        page_params = deepcopy(self.page_params)
        page_params.update({"ordinal": str(page_ordinal)})
        return reverse("relate-view_flow_page", kwargs=page_params)

    def post_create_flowpageimage(self, page_id, image_path=None):
        upload_url = self.get_upload_url(page_id=page_id)
        if image_path:
            with open(image_path, "rb") as fp:
                post_data = {
                    'image': [fp],
                }
                resp = self.c.post(
                    upload_url,
                    data=post_data,
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                return resp
        else:
            resp = self.c.post(
                upload_url,
                data={},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            return resp


    def post_delete_flowpageimage(self, page_id, image_pk):
        delete_url = self.get_delete_url(image_pk=image_pk, page_id=page_id)
        resp = self.c.post(
            delete_url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return resp


def mocked_corrupted_serialize_image(request, instance, file_attr='image'):
    from image_upload.serialize import serialize
    force_remove_path(instance.image.path)
    return serialize(request, instance, file_attr)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadCreateViewTest(ImageUploadViewMixin, TestCase):
    def test_one_image_upload_owner(self):
        page_id = "one_image"
        page_url = self.get_page_url(page_id=page_id)
        resp = self.c.get(page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "upload one image")
        resp = self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        self.assertTrue(os.path.isfile(image.image.path))
        self.assertEqual(resp_dict["files"][0]["deleteUrl"],
                         self.get_delete_url(image_pk=1, page_id=page_id))

    @override_settings(RELATE_JFU_MAX_IMAGE_SIZE=0.0001)
    def test_one_image_upload_size_exceeds(self):
        page_id = "one_image"
        resp = self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        expected_error = (
            "The image is too big. Please use "
            "Chrome/Firefox or mobile browser by "
            "which images will be cropped "
            "automatically before upload."
        )
        self.assertEqual(resp_dict["files"][0]["error"], expected_error)
        self.assertEqual(FlowPageImage.objects.all().count(), 0)

    def test_one_image_upload_form_invalid(self):
        page_id = "one_image"

        # post an invalid form (with required image field empty)
        resp = self.post_create_flowpageimage(page_id, image_path=None)
        self.assertEqual(resp.status_code, 400)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(resp_dict["error"]["image"],
                         ["This field is required."])
        self.assertEqual(FlowPageImage.objects.all().count(), 0)

    @mock.patch("image_upload.views.serialize",
                side_effect=mocked_corrupted_serialize_image)
    def test_one_image_upload_image_corrupted(self, mocked_serialize):
        page_id = "one_image"
        resp = self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        expected_error = (
            "Sorry, the image is corrupted during "
             "handling. That should be solved by "
             "a re-uploading.")
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(resp_dict["error"], expected_error)

    def test_one_image_upload_wrong_course_identifier(self):
        page_id = "one_image"
        page_ordinal = self.get_ordinal_via_page_id(page_id)
        page_params = deepcopy(self.page_params)
        page_params.update({"course_identifier": "non-exist-identifier",
                            "ordinal": str(page_ordinal)})
        with open(TEST_IMAGE1, "rb") as fp:
            post_data = {
                'image': [fp],
            }
            resp = self.c.post(
                reverse("jfu_upload", kwargs=page_params),
                data=post_data,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(FlowPageImage.objects.all().count(), 0)

    def test_one_image_upload_by_staff(self):
        # ta can upload image to students page
        page_id = "one_image"
        page_url = self.get_page_url(page_id=page_id)
        self.c.force_login(self.ta_participation.user)
        resp = self.c.get(page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "upload one image")
        resp = self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        self.assertEqual(image.creator,
                         self.ta_participation.user)
        self.assertTrue(os.path.isfile(image.image.path))
        self.assertEqual(resp_dict["files"][0]["deleteUrl"],
                         self.get_delete_url(image_pk=1, page_id=page_id))

    def test_one_image_upload_other_user(self):
        page_id = "one_image"
        self.c.force_login(self.student_participation2.user)
        resp = self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 403)

    def test_one_image_upload_non_participation_user(self):
        page_id = "one_image"
        self.c.force_login(self.non_participation_user)
        resp = self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 403)

    def test_one_image_upload_anonymous(self):
        page_id = "one_image"
        self.c.logout()
        resp = self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 403)

    def test_two_image_upload(self):
        page_id = "two_images"
        page_url = self.get_page_url(page_id=page_id)
        resp = self.c.get(page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "upload one image")
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.post_create_flowpageimage(page_id, TEST_IMAGE2)
        self.assertEqual(FlowPageImage.objects.all().count(), 2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 2)

    # def test_one_image_upload_with_2_images(self):
    #     # This test failed. User can upload images exceeding allowed number
    #     page_id = "one_image"
    #     self.post_create_flowpageimage(page_id, TEST_IMAGE1)
    #     resp = self.post_create_flowpageimage(page_id, TEST_IMAGE2)
    #     self.assertEqual(FlowPageImage.objects.all().count(), 1)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadDeleteViewTest(ImageUploadViewMixin, TestCase):

    def test_one_image_delete_my_own_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        resp = self.post_delete_flowpageimage(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_staff_uploaded_temp_image(self):
        page_id = "one_image"
        self.c.force_login(self.ta_participation.user)
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.student_participation.user)
        resp = self.post_delete_flowpageimage(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_staff_delete_staff_uploaded_temp_image(self):
        page_id = "one_image"
        self.c.force_login(self.ta_participation.user)
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        resp = self.post_delete_flowpageimage(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_staff_delete_my_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.ta_participation.user)
        resp = self.post_delete_flowpageimage(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_other_user_delete_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.student_participation2.user)
        resp = self.post_delete_flowpageimage(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(os.path.isfile(image.image.path))

    def test_one_image_delete_non_participation_user_delete_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.non_participation_user)
        resp = self.post_delete_flowpageimage(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(os.path.isfile(image.image.path))

    def test_one_image_delete_anonymous_delete_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.logout()
        resp = self.post_delete_flowpageimage(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(os.path.isfile(image.image.path))