# -*- coding: utf-8 -*-

# coverage run manage.py test tests --local_test_settings test_local_settings.py  # noqa
# python manage.py test tests.test_my_local.test_imageupload --local_test_settings test_local_settings.py  # noqa

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
import zipfile
from copy import deepcopy
from six import BytesIO

from unittest import skipIf
from django.urls import reverse
from django.test import TestCase
from django.contrib import messages
from django.test.utils import override_settings

from course.constants import participation_status
from course.models import FlowSession
from image_upload.models import FlowPageImage

from tests.test_my_local.utils import skip_test, SKIP_LOCAL_TEST_REASON
from tests.base_test_mixins import (
    SINGLE_COURSE_SETUP_LIST, SingleCoursePageTestMixin,
    FallBackStorageMessageTestMixin, NONE_PARTICIPATION_USER_CREATE_KWARG_LIST,
)
from tests.utils import mock

from tests.test_pages.test_generic import (
    MESSAGE_ANSWER_SAVED_TEXT, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
from tests.test_sandbox import SingleCoursePageSandboxTestBaseMixin
from tests.test_my_local.mixins import ImageUploadStorageTestMixin

MY_SINGLE_COURSE_SETUP_LIST = deepcopy(SINGLE_COURSE_SETUP_LIST)
MY_SINGLE_COURSE_SETUP_LIST[0]["course"]["git_source"] = (
    "https://code.aliyun.com/dzhuang/my_learningwhat_test_repo.git")
IMAGE_UPLOAD_FLOW = "image-upload-flow"
TEST_IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_IMAGE1 = os.path.join(TEST_IMAGE_FOLDER, "test1.jpg")
TEST_IMAGE2 = os.path.join(TEST_IMAGE_FOLDER, "test2.png")
TEST_IMAGE_TRUNCATED = os.path.join(TEST_IMAGE_FOLDER, "test_truncated.jpg")


class ImageUploadViewMixin(ImageUploadStorageTestMixin,
                           FallBackStorageMessageTestMixin,
                           SingleCoursePageTestMixin):
    def get_upload_url_by_page_id(self, page_id, course_identifier=None,
                                  flow_session_id=None):
        page_ordinal = self.get_page_ordinal_via_page_id(page_id, course_identifier,
                                                         flow_session_id)
        page_params = self.get_page_params(course_identifier, flow_session_id,
                                           page_ordinal)
        return reverse("jfu_upload", kwargs=page_params)

    def get_list_url_by_page_id(self, page_id=None, course_identifier=None,
                                flow_session_id=None):
        page_ordinal = self.get_page_ordinal_via_page_id(page_id, course_identifier,
                                                         flow_session_id)
        page_params = self.get_page_params(course_identifier, flow_session_id,
                                           page_ordinal)
        return reverse("jfu_view", kwargs=page_params)

    def get_delete_url_by_page_id(self, image_pk, page_id=None,
                                  course_identifier=None, flow_session_id=None):
        page_ordinal = self.get_page_ordinal_via_page_id(page_id, course_identifier,
                                                         flow_session_id)
        page_params = self.get_page_params(course_identifier, flow_session_id,
                                           page_ordinal)
        page_params.update({"pk": image_pk})
        return reverse("jfu_delete", kwargs=page_params)

    def get_crop_url_by_page_id(self, image_pk, page_id=None,
                                  course_identifier=None, flow_session_id=None):
        page_ordinal = self.get_page_ordinal_via_page_id(page_id, course_identifier,
                                                         flow_session_id)
        page_params = self.get_page_params(course_identifier, flow_session_id,
                                           page_ordinal)
        page_params.update({"pk": image_pk})
        return reverse("image_crop", kwargs=page_params)

    def post_create_flowpageimage_by_page_id(self, page_id, image_path=None,
                                             course_identifier=None,
                                             flow_session_id=None):
        upload_url = self.get_upload_url_by_page_id(page_id, course_identifier,
                                                    flow_session_id)
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

    def post_delete_flowpageimage_by_page_id(self, page_id,
                                             image_pk, course_identifier=None,
                                             flow_session_id=None):
        delete_url = self.get_delete_url_by_page_id(image_pk, page_id,
                                                    course_identifier,
                                                    flow_session_id)
        resp = self.c.post(delete_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return resp

    def post_crop_flowpageimage_by_page_id(self, page_id, image_pk, crop_data,
                                           course_identifier=None,
                                           flow_session_id=None):
        crop_url = self.get_crop_url_by_page_id(image_pk, page_id,
                                                course_identifier, flow_session_id)
        post_data = {"croppedResult": json.dumps(crop_data)}
        resp = self.c.post(
            crop_url,
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return resp


class ImageUploadQuizMixin(ImageUploadViewMixin):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = IMAGE_UPLOAD_FLOW
    none_participation_user_create_kwarg_list = (
        NONE_PARTICIPATION_USER_CREATE_KWARG_LIST)

    @classmethod
    def setUpTestData(cls):  # noqa
        super(ImageUploadQuizMixin, cls).setUpTestData()
        cls.student_participation2 = (
            cls.create_participation(
                cls.course, cls.non_participation_users[0],
                status=participation_status.active))
        cls.non_participation_user = cls.non_participation_users[1]

    def setUp(self):  # noqa
        super(ImageUploadQuizMixin, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)


def mocked_corrupted_serialize_image(request, instance, file_attr='image'):
    from image_upload.serialize import serialize
    from relate.utils import force_remove_path
    force_remove_path(instance.image.path)
    return serialize(request, instance, file_attr)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadCreateViewTest(ImageUploadQuizMixin, TestCase):
    def test_one_image_upload_owner(self):
        page_id = "one_image"
        page_url = self.get_page_url_by_page_id(page_id=page_id)
        resp = self.c.get(page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "upload one image")
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        self.assertTrue(os.path.isfile(image.image.path))
        self.assertEqual(resp_dict["files"][0]["deleteUrl"],
                         self.get_delete_url_by_page_id(
                             image_pk=1, page_id=page_id))

    @override_settings(RELATE_JFU_MAX_IMAGE_SIZE=0.0001)
    def test_one_image_upload_size_exceeds(self):
        page_id = "one_image"
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
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

    def create_not_my_session_image(self, user):
        page_id = "one_image"
        self.c.force_login(self.student_participation2.user)
        self.start_flow(self.flow_id)
        his_session = FlowSession.objects.all().order_by("-start_time")[0]
        if user is not None:
            self.c.force_login(user)
        else:
            self.c.logout()
        resp = self.post_create_flowpageimage_by_page_id(
            page_id, TEST_IMAGE1, flow_session_id=his_session.pk)

        if user is None or user != self.instructor_participation.user:
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(FlowPageImage.objects.all().count(), 0)
        else:
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(FlowPageImage.objects.all().count(), 1)

    def test_create_not_my_session_image(self):
        self.create_not_my_session_image(self.student_participation.user)

    def test_create_not_my_session_image_staff(self):
        self.create_not_my_session_image(self.instructor_participation.user)

    def test_create_not_my_session_image_anonymous(self):
        self.create_not_my_session_image(None)

    # def test_create_ordinal_invalid_image(self):
    #     page_id = "one_image"
    #     invalid_page_ordinal = 100
    #     resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1,
    #                                                      page_ordinal=invalid_page_ordinal)
    #
    #     self.assertEqual(resp.status_code, 404)
    #     self.assertEqual(FlowPageImage.objects.all().count(), 0)

    def create_not_allowed_for_finished_page(self, user):
        self.c.force_login(self.student_participation.user)
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        # submit page
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        # end session
        self.end_flow()

        if user is not None:
            self.c.force_login(user)
        else:
            self.c.logout()
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)

    def test_create_not_allowed_for_finished_page_owner(self):
        self.create_not_allowed_for_finished_page(
            self.student_participation.user)

    def test_create_not_allowed_for_finished_page_another(self):
        self.create_not_allowed_for_finished_page(
            self.student_participation2.user)

    def test_create_not_allowed_for_finished_page_staff(self):
        self.create_not_allowed_for_finished_page(
            self.instructor_participation.user)

    def test_create_not_allowed_for_finished_page_anonymous(self):
        self.create_not_allowed_for_finished_page(None)

    def test_one_image_upload_form_invalid(self):
        page_id = "one_image"

        # post an invalid form (with required image field empty)
        resp = self.post_create_flowpageimage_by_page_id(page_id, image_path=None)
        self.assertEqual(resp.status_code, 400)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(resp_dict["error"]["image"],
                         ["This field is required."])
        self.assertEqual(FlowPageImage.objects.all().count(), 0)

    @mock.patch("image_upload.views.serialize",
                side_effect=mocked_corrupted_serialize_image)
    def test_one_image_upload_image_corrupted(self, mocked_serialize):
        page_id = "one_image"
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        expected_error = (
            "Sorry, the image is corrupted during "
            "handling. That should be solved by "
            "a re-uploading.")
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(resp_dict["error"], expected_error)

    def test_one_image_upload_wrong_course_identifier(self):
        page_id = "one_image"
        page_ordinal = self.get_page_ordinal_via_page_id(page_id)
        page_params = self.get_page_params(page_ordinal=page_ordinal)
        page_params.update({"course_identifier": "non-exist-identifier"})
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
        page_url = self.get_page_url_by_page_id(page_id=page_id)
        self.c.force_login(self.ta_participation.user)
        resp = self.c.get(page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "upload one image")
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        self.assertEqual(image.creator,
                         self.ta_participation.user)
        self.assertTrue(os.path.isfile(image.image.path))
        self.assertEqual(resp_dict["files"][0]["deleteUrl"],
                         self.get_delete_url_by_page_id(image_pk=1, page_id=page_id))

    def test_one_image_upload_other_user(self):
        page_id = "one_image"
        self.c.force_login(self.student_participation2.user)
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 403)

    def test_one_image_upload_non_participation_user(self):
        page_id = "one_image"
        self.c.force_login(self.non_participation_user)
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 403)

    def test_one_image_upload_anonymous(self):
        page_id = "one_image"
        self.c.logout()
        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.assertEqual(resp.status_code, 403)

    def test_two_image_upload(self):
        page_id = "two_images"
        page_url = self.get_page_url_by_page_id(page_id=page_id)
        resp = self.c.get(page_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "upload one image")
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        self.assertEqual(FlowPageImage.objects.all().count(), 2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 2)

    def test_one_image_upload_trancated(self):
        page_id = "one_image"
        resp = self.post_create_flowpageimage_by_page_id(page_id,
                                                         TEST_IMAGE_TRUNCATED)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertIsNone(resp_dict.get("error"))
        self.assertIsNotNone(resp_dict.get("files"))
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        self.assertTrue(os.path.isfile(image.image.path))


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadDeleteViewTest(ImageUploadQuizMixin, TestCase):

    def test_one_image_delete_my_own_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_staff_uploaded_temp_image(self):
        page_id = "one_image"
        self.c.force_login(self.ta_participation.user)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.student_participation.user)
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_staff_delete_staff_uploaded_temp_image(self):
        page_id = "one_image"
        self.c.force_login(self.ta_participation.user)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_staff_delete_my_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.ta_participation.user)
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), "true")
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(image.image.path))

    def test_one_image_delete_other_user_delete_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.student_participation2.user)
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(os.path.isfile(image.image.path))

    def test_one_image_delete_non_participation_user_delete_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.force_login(self.non_participation_user)
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(os.path.isfile(image.image.path))

    def test_one_image_delete_anonymous_delete_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.get()
        self.c.logout()
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(os.path.isfile(image.image.path))

    def delete_not_allowed_for_finished_page(self, user):
        self.c.force_login(self.student_participation.user)
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        # submit page
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        # end session
        self.end_flow()

        if user is not None:
            self.c.force_login(user)
        else:
            self.c.logout()

        resp = self.post_delete_flowpageimage_by_page_id(page_id=page_id, image_pk=1)

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)

    def test_delete_not_allowed_for_finished_page_owner(self):
        self.delete_not_allowed_for_finished_page(
            self.student_participation.user)

    def test_delete_not_allowed_for_finished_page_another(self):
        self.delete_not_allowed_for_finished_page(
            self.student_participation2.user)

    def test_delete_not_allowed_for_finished_page_staff(self):
        self.delete_not_allowed_for_finished_page(
            self.instructor_participation.user)

    def test_delete_not_allowed_for_finished_page_anonymous(self):
        self.delete_not_allowed_for_finished_page(None)


MESSAGE_IMAGE_NOT_UPLOADED_TEXT = "You have not upload image(s)!"
FORM_ERROR_IMAGE_NUMBER_EXCEEDED_PATTERN = (
    "You are only allowed to upload %i images, got %i instead")
FORM_ERROR_FORM_DATA_BROKEN_TEXT = ("The form data is broken. "
                                 "please refresh the page and "
                                 "redo the upload and submission.")
FORM_ERROR_SUBMITTING_OTHERS_IMAGE_TEXT = (
    "There're some image(s) which don't belong "
    "to this session. "
    "Please make sure you are the owner of this "
    "session and all images are uploaded by you. "
    "please refresh the page and "
    "redo the upload and submission.")

FORM_ERROR_IMAGE_BROKEN_PATTERN = (
    "Some of you uploaded images just failed for unknown reasons: %s. "
    "please redo the upload and submission.")


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadPageTest(ImageUploadQuizMixin, TestCase):

    def test_page_submit_success(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_SAVED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 0)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 1)

    def test_get_image_grade_page(self):
        page_id = "one_image"
        grade_page_url = self.get_page_grading_url_by_page_id(page_id)
        self.c.force_login(self.ta_participation.user)
        resp = self.c.get(grade_page_url)
        self.assertEqual(resp.status_code, 200)

    def test_page_submit_fail_bad_hidden_answer(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)

        # bad hidden_answer string
        image_pks_str = ",".join([str(pk) for pk in image_pks] + ["not_a_number"])
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        expected_form_error = FORM_ERROR_FORM_DATA_BROKEN_TEXT
        self.assertTrue(resp.status_code, 200)
        self.assertFormError(resp, "form", None, expected_form_error)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_FAILED_SAVE_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 1)

    def test_page_submit_fail_submitting_others_image(self):
        page_id = "two_images"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        his_image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)

        self.c.force_login(self.student_participation2.user)
        # this is student2's quiz, self.params is updated to this session
        self.start_flow(self.flow_id)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)

        image_pks = FlowPageImage.objects.filter(
            creator=self.student_participation2.user).values_list("pk", flat=True)
        self.assertTrue(len(image_pks), 1)

        image_pks = list(image_pks) + list(his_image_pks)
        self.assertTrue(len(image_pks), 1)

        image_pks_str = ",".join([str(pk) for pk in image_pks])
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        expected_form_error = FORM_ERROR_SUBMITTING_OTHERS_IMAGE_TEXT
        self.assertTrue(resp.status_code, 200)
        self.assertFormError(resp, "form", None, expected_form_error)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_FAILED_SAVE_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 0)

    def test_page_submit_success_submitting_staff_uploaded_image(self):
        page_id = "two_images"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.c.force_login(self.ta_participation.user)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)

        image_pks_str = ",".join([str(pk) for pk in image_pks])
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertEqual(FlowPageImage.objects.all().count(), 2)
        self.assertTrue(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_SAVED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 0)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 2)

    def test_page_submit_success_removing_none_exist_image_silent(self):
        page_id = "two_images"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)

        image_pks_str = ",".join([str(pk) for pk in image_pks] + ["100"])
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_SAVED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 0)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 1)

    def test_page_submit_success_removing_imaged_created_by_unknown_user(self):
        page_id = "two_images"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        unknow_image = FlowPageImage.objects.all()[1]
        unknow_image.creator = None
        unknow_image.save()
        self.assertEqual(FlowPageImage.objects.all().count(), 2)

        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertTrue(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_SAVED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        # the unknown image is removed when submit
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 0)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 1)

    def test_page_submit_failure_with_broken_images(self):
        page_id = "two_images"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image = FlowPageImage.objects.all().first()

        # delete the physical file
        os.remove(image.image.path)
        expected_form_error = (
            FORM_ERROR_IMAGE_BROKEN_PATTERN % image.slug)
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [str(image.pk)]})
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertTrue(resp.status_code, 200)
        self.assertFormError(resp, "form", None, expected_form_error)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_FAILED_SAVE_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 1)

    def test_page_submit_no_image_which_requires(self):
        page_id = "one_image"
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [""]})
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertTrue(resp.status_code, 200)
        expected_form_error = MESSAGE_IMAGE_NOT_UPLOADED_TEXT
        self.assertFormError(resp, 'form', None, expected_form_error)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_FAILED_SAVE_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 0)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 0)

    def test_page_submit_no_image_which_allow_non_images(self):
        page_id = "allow_no_image"
        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [""]})
        self.assertEqual(FlowPageImage.objects.all().count(), 0)
        self.assertTrue(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_SAVED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 0)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 0)

    def test_page_submit_exceed_allow_number_of_images(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        resp = self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertEqual(FlowPageImage.objects.all().count(), 2)
        self.assertTrue(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_ANSWER_FAILED_SAVE_TEXT])
        expected_form_error = (
            FORM_ERROR_IMAGE_NUMBER_EXCEEDED_PATTERN % (1, 2))
        self.assertFormError(resp, 'form', None, expected_form_error)
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 0)

    def test_page_submit_already_submitted_page_which_is_not_allowed(self):
        page_id = "one_image_no_change_answer"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})

        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)

        # not allowed to upload image to change_answer
        self.assertEqual(resp.status_code, 403)

    def test_page_submit_already_submitted_page_which_is_allowed(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})

        resp = self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)

        # allowed to upload image to change_answer
        self.assertEqual(resp.status_code, 200)

    def test_page_submit_remove_temp_image(self):
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        # add another image
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 0)

        # submit only the first one
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 0)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 1)

    def test_page_submit_remove_temp_image_other_image_not_removed(self):
        page_id1 = "one_image"
        page_id2 = "two_images"
        self.post_create_flowpageimage_by_page_id(page_id1, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        # add another image to another page
        self.post_create_flowpageimage_by_page_id(page_id2, TEST_IMAGE2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 0)

        # submit only the first one
        self.post_answer_by_page_id(
            page_id1, {"hidden_answer": [image_pks_str]})
        self.assertEqual(FlowPageImage.objects.all().count(), 2)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 1)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=False).count(), 1)

    def test_page_delete_already_submitted_image(self):
        # make sure this is not a real delete, just remove from the rendered page
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})

        image = FlowPageImage.objects.get()
        self.assertFalse(image.is_temp_image)
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)

        # the image is not deleted because it is not a temp_image
        self.assertEqual(resp.content.decode(), "false")

    def test_page_delete_already_submitted_image_by_staff(self):
        # make sure this is not a real delete, just remove from the rendered page
        # make sure staff can't delete the image
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})

        image = FlowPageImage.objects.get()
        self.assertFalse(image.is_temp_image)

        self.c.force_login(self.instructor_participation.user)
        resp = self.post_delete_flowpageimage_by_page_id(page_id, image_pk=1)
        self.assertEqual(resp.status_code, 200)

        # the image is not deleted because it is not a temp_image
        self.assertEqual(resp.content.decode(), "false")

    def test_page_history_no_history(self):
        page_id = "one_image"
        page_ordinal = self.get_page_ordinal_via_page_id(page_id)
        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=0)

        # submit a page with no image which requires
        self.post_answer_by_page_id(page_id, {"hidden_answer": [""]})

        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=0)

        # there should be no points
        self.assertEqual(self.end_flow().status_code, 200)
        self.assertSessionScoreEqual(0)

    def test_page_history_number(self):
        page_id = "two_images"
        page_ordinal = self.get_page_ordinal_via_page_id(page_id)
        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=0)
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=1)

        # submit with no image which requires
        self.post_answer_by_page_id(page_id, {"hidden_answer": [""]})
        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=1)

        # add another image to existing list
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=2)

        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=3)

        self.assertEqual(self.end_flow().status_code, 200)
        self.assertSessionScoreEqual(None)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadListViewTest(ImageUploadQuizMixin, TestCase):
    def test_page_list_view(self):
        page_id = "two_images"
        page_ordinal = self.get_page_ordinal_via_page_id(page_id)
        list_page_url = self.get_list_url_by_page_id(page_id=page_id)

        resp = self.c.get(list_page_url)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(resp_dict, {})

        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.assertSubmitHistoryItemsCount(
            page_ordinal=page_ordinal, expected_count=1)
        resp = self.c.get(list_page_url)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(len(resp_dict["files"]), 1)

        # add another image to existing list
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        resp = self.c.get(list_page_url)
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(len(resp_dict["files"]), 2)

    def test_page_list_view_visit_id_not_int(self):
        page_id = "two_images"
        list_page_url = self.get_list_url_by_page_id(page_id=page_id)
        resp = self.c.get(list_page_url + "?visit_id=abcd")
        self.assertEqual(resp.status_code, 400)

    def test_page_list_view_visit_id(self):
        page_id = "two_images"
        list_page_url = self.get_list_url_by_page_id(page_id=page_id)

        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks1 = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str1 = ",".join([str(pk) for pk in image_pks1])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str1]})

        # add another image to existing list
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        image_pks2 = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str2 = ",".join([str(pk) for pk in image_pks2])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str2]})
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str1]})
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str2]})

        # This visit_id doesn't exist, use the latest
        resp = self.c.get(list_page_url + "?visit_id=100")
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(len(resp_dict["files"]), 2)

        resp = self.c.get(list_page_url + "?visit_id=1")
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(len(resp_dict["files"]), 1)

        resp = self.c.get(list_page_url + "?visit_id=2")
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(len(resp_dict["files"]), 2)

        resp = self.c.get(list_page_url + "?visit_id=3")
        self.assertEqual(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(len(resp_dict["files"]), 1)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadDownloadViewTest(ImageUploadQuizMixin, TestCase):
    def setUp(self):  # noqa
        super(ImageUploadDownloadViewTest, self).setUp()
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.image_download_url = (
            FlowPageImage.objects.all().first().get_absolute_url())

    def test_owner_download(self):
        resp = self.c.get(self.image_download_url)
        self.assertTrue(resp.status_code, 200)
        self.assertEqual(resp.get('Content-Type'), "image/jpeg")

    def test_staff_download(self):
        self.c.force_login(self.ta_participation.user)
        resp = self.c.get(self.image_download_url)
        self.assertTrue(resp.status_code, 200)
        self.assertEqual(resp.get('Content-Type'), "image/jpeg")

    def test_other_user_download(self):
        self.c.force_login(self.student_participation2.user)
        resp = self.c.get(self.image_download_url)
        self.assertTrue(resp.status_code, 403)

    def test_not_authenticated_download(self):
        self.c.logout()
        resp = self.c.get(self.image_download_url)
        self.assertTrue(resp.status_code, 403)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadCropViewTest(ImageUploadQuizMixin, TestCase):
    def setUp(self):  # noqa
        super(ImageUploadCropViewTest, self).setUp()
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        self.image1 = FlowPageImage.objects.first()

        page_id = "two_images"
        self.image2 = FlowPageImage.objects.last()
        image_pks = [self.image2.pk]
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})

    @property
    def crop_data(self):
        return (
            {"x": 0, "y": 0, "width": 20, "height": 19,
             "rotate": 0, "scaleX": 1, "scaleY": 1})

    def test_crop_temp_image(self):
        page_id = "one_image"
        resp = self.post_crop_flowpageimage_by_page_id(
            page_id=page_id, image_pk=self.image1.pk, crop_data=self.crop_data)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(
            FlowPageImage.objects.filter(image_page_id="one_image").count(), 2)

    def test_get_crop_image_url_403(self):
        page_id = "one_image"
        resp = self.c.get(self.get_crop_url_by_page_id(self.image1.pk,
                                                       page_id=page_id))
        self.assertEqual(resp.status_code, 403)

    def test_post_crop_image_url_not_ajax_400(self):
        page_id = "one_image"
        resp = self.c.get(self.get_crop_url_by_page_id(self.image1.pk,
                                                       page_id=page_id))
        self.assertEqual(resp.status_code, 403)

        post_data = {"croppedResult": json.dumps(self.crop_data)}
        resp = self.c.post(
            self.get_crop_url_by_page_id(self.image1.pk, page_id=page_id),
            data=post_data)
        self.assertEqual(resp.status_code, 400)

    def test_crop_image_pk_not_exist_404(self):
        page_id = "one_image"
        resp = self.post_crop_flowpageimage_by_page_id(
            page_id=page_id, image_pk=1000, crop_data=self.crop_data)
        self.assertEqual(resp.status_code, 404)

    def test_crop_none_temp_image(self):
        page_id = "one_image"
        # submit page
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": ["1"]})

        self.assertEqual(
            FlowPageImage.objects.filter(image_page_id="one_image").count(), 1)

        resp = self.post_crop_flowpageimage_by_page_id(
            page_id=page_id, image_pk=self.image1.pk, crop_data=self.crop_data)
        self.assertEqual(resp.status_code, 200)

        # crop non temp image create new
        self.assertEqual(
            FlowPageImage.objects.filter(image_page_id="one_image").count(), 2)

    def crop_not_allowed_for_finished_page_response(self, user):
        self.c.force_login(self.student_participation.user)

        page_id = "one_image"
        # submit page
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": ["1"]})
        # end session
        self.end_flow()

        if user is not None:
            self.c.force_login(user)
        else:
            self.c.logout()

        resp = self.post_crop_flowpageimage_by_page_id(
            page_id=page_id, image_pk=self.image1.pk, crop_data=self.crop_data)
        return resp

    def test_crop_not_allowed_for_finished_page_owner(self):
        resp = self.crop_not_allowed_for_finished_page_response(
            self.student_participation.user)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            FlowPageImage.objects.filter(image_page_id="one_image").count(), 1)

    def test_crop_not_allowed_for_finished_page_another(self):
        resp = self.crop_not_allowed_for_finished_page_response(
            self.student_participation2.user)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            FlowPageImage.objects.filter(image_page_id="one_image").count(), 1)

    def test_crop_allowed_for_finished_page_staff(self):
        resp = self.crop_not_allowed_for_finished_page_response(
            self.instructor_participation.user)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            FlowPageImage.objects.filter(image_page_id="one_image").count(), 2)

    def test_crop_not_allowed_for_finished_page_anonymous(self):
        resp = self.crop_not_allowed_for_finished_page_response(None)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            FlowPageImage.objects.filter(image_page_id="one_image").count(), 1)

    def create_new_course(self, course_identifier):
        # create a new course
        new_course_kwargs = deepcopy(self.courses_setup_list[0]["course"])
        new_course_kwargs["identifier"] = course_identifier
        self.c.force_login(self.instructor_participation.user)
        self.create_course(new_course_kwargs)
        from course.models import Course
        new_course = Course.objects.all().order_by("-pk")[0]
        self.create_participation(new_course, self.student_participation.user,
                                  status=participation_status.active)
        assert Course.objects.count() == 2
        return new_course

    def test_need_adjust_new_instance_course_change(self):
        new_course_identifier = "test-course2"
        self.create_new_course(new_course_identifier)
        self.c.force_login(self.student_participation.user)
        existing_image_number = FlowPageImage.objects.count()
        self.start_flow(self.flow_id, course_identifier=new_course_identifier)
        page_id = "two_images"
        resp = self.post_crop_flowpageimage_by_page_id(
            page_id=page_id, image_pk=self.image1.pk, crop_data=self.crop_data,
            flow_session_id=FlowSession.objects.last().id,
            course_identifier=new_course_identifier)
        self.assertEqual(resp.status_code, 200)
        new_image = FlowPageImage.objects.last()
        self.assertEqual(
            new_image.course.identifier, new_course_identifier)
        self.assertEqual(
            new_image.image_page_id, page_id)
        self.assertEqual(existing_image_number + 1, FlowPageImage.objects.count())


QUESTION_MARKUP = """
type: ImageUploadQuestion\r
id: two_images\r
access_rules:\r
    add_permissions:\r
        - change_answer\r
value: 5\r
maxNumberOfFiles: 2\r

prompt: |\r

    # allow upload two images\r

rubric: |\r
    Any image?\r
"""


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadSandboxViewTest(ImageUploadViewMixin,
                                 SingleCoursePageSandboxTestBaseMixin, TestCase):
    @property
    def sandbox_url(self):
        return reverse("relate-view_page_sandbox", args=[self.course.identifier])

    @property
    def page_params(self):
        return {"course_identifier": self.course.identifier}

    def setUp(self):  # noqa
        super(ImageUploadSandboxViewTest, self).setUp()
        self.c.force_login(self.instructor_participation.user)

    def get_sandbox_upload_url(self):
        return reverse("jfu_upload", kwargs=self.page_params)

    def get_sandbox_list_url(self):
        return reverse("jfu_view", kwargs=self.page_params)

    def get_sandbox_delete_url(self, image_pk):
        page_params = deepcopy(self.page_params)
        page_params.update({"pk": image_pk})
        return reverse("jfu_delete", kwargs=page_params)

    def get_sandbox_crop_url(self, image_pk):
        page_params = deepcopy(self.page_params)
        page_params.update({"pk": image_pk})
        return reverse("image_crop", kwargs=page_params)

    def post_sandbox_create_flowpageimage(self, image_path=None):
        upload_url = self.get_sandbox_upload_url()
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

    def post_sandbox_delete_flowpageimage(self, image_pk):
        delete_url = self.get_sandbox_delete_url(image_pk=image_pk)
        resp = self.c.post(
            delete_url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return resp

    def post_sandbox_crop_flowpageimage(self, image_pk, crop_data):
        crop_url = self.get_sandbox_crop_url(image_pk=image_pk)
        post_data = {"croppedResult": json.dumps(crop_data)}
        resp = self.c.post(
            crop_url,
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return resp

    def test_sandbox_imageuploadquestion_render(self):
        resp = self.get_page_sandbox_preview_response(QUESTION_MARKUP)

        # success render
        self.assertEqual(resp.status_code, 200)
        self.assertResponseMessagesCount(resp, 0)
        self.assertContains(resp, "<h1>allow upload two images</h1>")

    def test_sandbox_create_image(self):
        resp = self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        self.assertEqual(
            FlowPageImage.objects.filter(is_temp_image=True).count(), 1)
        image = FlowPageImage.objects.get()
        self.assertTrue(image.is_temp_image)
        self.assertTrue(os.path.isfile(image.image.path))

    def test_sandbox_create_image_403(self):
        self.c.force_login(self.student_participation.user)
        resp = self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.all().count(), 0)

    def test_sandbox_delete_image(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.first()
        image_path = image.image.path
        resp = self.post_sandbox_delete_flowpageimage(image_pk=image.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(os.path.isfile(image_path))
        self.assertEqual(FlowPageImage.objects.all().count(), 0)

    def test_sandbox_delete_image_403(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.assertEqual(FlowPageImage.objects.all().count(), 1)
        image = FlowPageImage.objects.first()
        image_path = image.image.path
        self.c.force_login(self.student_participation.user)
        resp = self.post_sandbox_delete_flowpageimage(image_pk=image.pk)
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(os.path.isfile(image_path))
        self.assertEqual(FlowPageImage.objects.all().count(), 1)

    def test_sandbox_image_page_post(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.post_sandbox_create_flowpageimage(TEST_IMAGE2)
        self.assertEqual(FlowPageImage.objects.all().count(), 2)
        self.assertEqual(FlowPageImage.objects.filter(is_temp_image=True).count(), 2)
        image1 = FlowPageImage.objects.first()
        image1_path = image1.image.path
        image2 = FlowPageImage.objects.last()
        image2_path = image2.image.path

        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        answer_data = {"hidden_answer": [image_pks_str]}
        resp = self.get_page_sandbox_submit_answer_response(
            markup_content=QUESTION_MARKUP, answer_data=answer_data)

        self.assertTrue(resp.status_code, 200)
        # all images are still temp images after page post
        self.assertEqual(FlowPageImage.objects.filter(is_temp_image=True).count(), 2)
        self.assertTrue(os.path.isfile(image1_path))
        self.assertTrue(os.path.isfile(image2_path))

    def test_sandbox_image_page_post_403(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.post_sandbox_create_flowpageimage(TEST_IMAGE2)
        self.assertEqual(FlowPageImage.objects.all().count(), 2)
        self.assertEqual(FlowPageImage.objects.filter(is_temp_image=True).count(), 2)

        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        answer_data = {"hidden_answer": [image_pks_str]}

        self.c.force_login(self.student_participation.user)
        resp = self.get_page_sandbox_submit_answer_response(
            markup_content=QUESTION_MARKUP, answer_data=answer_data)

        self.assertTrue(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.filter(is_temp_image=True).count(), 2)

    def test_sandbox_list_images(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.post_sandbox_create_flowpageimage(TEST_IMAGE2)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        answer_data = {"hidden_answer": [image_pks_str]}
        self.get_page_sandbox_submit_answer_response(
            markup_content=QUESTION_MARKUP, answer_data=answer_data)

        resp = self.c.get(self.get_sandbox_list_url())
        self.assertTrue(resp.status_code, 200)
        resp_dict = json.loads(resp.content.decode())
        self.assertEqual(len(resp_dict["files"]), 2)

    def test_sandbox_list_images_403(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        self.post_sandbox_create_flowpageimage(TEST_IMAGE2)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        answer_data = {"hidden_answer": [image_pks_str]}
        self.get_page_sandbox_submit_answer_response(
            markup_content=QUESTION_MARKUP, answer_data=answer_data)

        self.c.force_login(self.student_participation.user)
        resp = self.c.get(self.get_sandbox_list_url())
        self.assertTrue(resp.status_code, 403)

    def test_sandbox_download_image(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        answer_data = {"hidden_answer": [image_pks_str]}
        self.get_page_sandbox_submit_answer_response(
            markup_content=QUESTION_MARKUP, answer_data=answer_data)
        image_download_url = (
            FlowPageImage.objects.all().first().get_absolute_url())
        resp = self.c.get(image_download_url)
        self.assertTrue(resp.status_code, 200)
        self.assertEqual(resp.get('Content-Type'), "image/jpeg")

    def test_sandbox_download_image403(self):
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        answer_data = {"hidden_answer": [image_pks_str]}
        self.get_page_sandbox_submit_answer_response(
            markup_content=QUESTION_MARKUP, answer_data=answer_data)
        image_download_url = (
            FlowPageImage.objects.all().first().get_absolute_url())
        self.c.force_login(self.student_participation.user)
        resp = self.c.get(image_download_url)
        self.assertTrue(resp.status_code, 403)

    def sandbox_crop_image_resp(self, user):
        self.c.force_login(self.instructor_participation.user)
        self.post_sandbox_create_flowpageimage(TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])

        answer_data = {"hidden_answer": [image_pks_str]}
        self.get_page_sandbox_submit_answer_response(
            markup_content=QUESTION_MARKUP, answer_data=answer_data)

        if user is not None:
            self.c.force_login(user)
        else:
            self.c.logout()

        resp = self.post_sandbox_crop_flowpageimage(
            FlowPageImage.objects.first().pk,
            crop_data={"x": 0, "y": 0, "width": 20, "height": 19,
                       "rotate": 0, "scaleX": 1, "scaleY": 1})
        return resp

    def test_sandbox_crop_image_staff(self):
        resp = self.sandbox_crop_image_resp(self.instructor_participation.user)
        self.assertTrue(resp.status_code, 200)
        self.assertEqual(FlowPageImage.objects.count(), 2)

    def test_sandbox_crop_image_403(self):
        resp = self.sandbox_crop_image_resp(self.student_participation.user)
        self.assertTrue(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.count(), 1)

    def test_sandbox_crop_image_not_auth_403(self):
        resp = self.sandbox_crop_image_resp(None)
        self.assertTrue(resp.status_code, 403)
        self.assertEqual(FlowPageImage.objects.count(), 1)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class ImageUploadDownloadSubmissionTest(ImageUploadQuizMixin, TestCase):
    def setUp(self):  # noqa
        super(ImageUploadDownloadSubmissionTest, self).setUp()
        page_id = "one_image"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE1)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})

        page_id = "two_images"
        self.post_create_flowpageimage_by_page_id(page_id, TEST_IMAGE2)
        image_pks = FlowPageImage.objects.all().values_list("pk", flat=True)
        image_pks_str = ",".join([str(pk) for pk in image_pks])
        self.post_answer_by_page_id(
            page_id, {"hidden_answer": [image_pks_str]})
        self.end_flow()

    def get_download_all_submissions_url(self):
        params = {"course_identifier": self.course.identifier,
                    "flow_id": self.flow_id}
        return reverse("relate-download_all_submissions",
                                            kwargs=params)

    def get_download_all_post_data(self, group_page_id, **kwargs):
        post_data = {'restrict_to_rules_tag': ['<<<ALL>>>'],
                'which_attempt': ['last'],
                'extra_file': [''], 'download': ['Download'],
                'page_id': [],
                'non_in_progress_only': ['on']}
        post_data.update({"page_id": [group_page_id]})
        post_data.update(kwargs)

        return post_data

    def post_download_all_submissions_resp(
            self, group_page_id, post_data=None, **kwargs):
        download_url = self.get_download_all_submissions_url()
        if post_data is None:
            post_data = self.get_download_all_post_data(group_page_id, **kwargs)
        else:
            post_data.update({"page_id": [group_page_id]})
            post_data.update(kwargs)

        return self.c.post(download_url, post_data)

    def test_view_download_image_upload_submissions_one_image(self):
        group_page_id = "image_only/one_image"
        self.c.force_login(self.ta_participation.user)
        resp = self.post_download_all_submissions_resp(group_page_id)
        self.assertEqual(resp.status_code, 200)
        prefix, zip_file = resp["Content-Disposition"].split('=')
        self.assertEqual(prefix, "attachment; filename")
        self.assertEqual(resp.get('Content-Type'), "application/zip")

        buf = BytesIO(resp.content)
        with zipfile.ZipFile(buf, 'r') as zf:
            self.assertIsNone(zf.testzip())
            self.assertEqual(len(zf.filelist), 2)
            for f in zf.filelist:
                self.assertGreater(f.file_size, 0)
            self.assertEqual(zf.filelist[1].filename, 'submit_summary.csv')
            self.assertIn(self.student_participation.user.get_full_name(),
                          zf.filelist[0].filename)
            my_zipped = BytesIO(zf.read(zf.filelist[0].filename))

        with zipfile.ZipFile(my_zipped) as my_zip:
            self.assertIsNone(my_zip.testzip())
            self.assertEqual(len(my_zip.filelist), 1)
            for f in my_zip.filelist:
                self.assertGreater(f.file_size, 0)
            self.assertGreater(my_zip.filelist[0].file_size, 0)
            self.assertEqual(my_zip.filelist[0].filename, '1.jpg')

    def test_view_download_image_upload_submissions_two_images(self):
        group_page_id = "image_only/two_images"
        self.c.force_login(self.ta_participation.user)
        resp = self.post_download_all_submissions_resp(group_page_id)
        self.assertEqual(resp.status_code, 200)
        prefix, zip_file = resp["Content-Disposition"].split('=')
        self.assertEqual(prefix, "attachment; filename")
        self.assertEqual(resp.get('Content-Type'), "application/zip")

        buf = BytesIO(resp.content)
        with zipfile.ZipFile(buf, 'r') as zf:
            self.assertIsNone(zf.testzip())
            self.assertEqual(len(zf.filelist), 2)
            for f in zf.filelist:
                self.assertGreater(f.file_size, 0)
            self.assertEqual(zf.filelist[1].filename, 'submit_summary.csv')
            self.assertIn(self.student_participation.user.get_full_name(),
                          zf.filelist[0].filename)
            my_zipped = BytesIO(zf.read(zf.filelist[0].filename))

        with zipfile.ZipFile(my_zipped) as my_zip:
            self.assertIsNone(my_zip.testzip())
            self.assertEqual(len(my_zip.filelist), 2)
            for f in my_zip.filelist:
                self.assertGreater(f.file_size, 0)
            self.assertEqual(my_zip.filelist[0].filename, '1.jpg')
            self.assertEqual(my_zip.filelist[1].filename, '2.png')

    def test_view_download_image_upload_submissions_two_images_one_corrupted(self):
        group_page_id = "image_only/two_images"
        os.remove(FlowPageImage.objects.last().image.path)
        self.c.force_login(self.ta_participation.user)
        resp = self.post_download_all_submissions_resp(group_page_id)
        self.assertEqual(resp.status_code, 200)
        prefix, zip_file = resp["Content-Disposition"].split('=')
        self.assertEqual(prefix, "attachment; filename")
        self.assertEqual(resp.get('Content-Type'), "application/zip")

        buf = BytesIO(resp.content)
        with zipfile.ZipFile(buf, 'r') as zf:
            self.assertIsNone(zf.testzip())
            self.assertEqual(len(zf.filelist), 2)
            for f in zf.filelist:
                self.assertGreater(f.file_size, 0)
            self.assertEqual(zf.filelist[1].filename, 'submit_summary.csv')
            self.assertIn(self.student_participation.user.get_full_name(),
                          zf.filelist[0].filename)
            my_zipped = BytesIO(zf.read(zf.filelist[0].filename))

        with zipfile.ZipFile(my_zipped) as my_zip:
            self.assertIsNone(my_zip.testzip())
            self.assertEqual(len(my_zip.filelist), 1)
            for f in my_zip.filelist:
                self.assertGreater(f.file_size, 0)

    def test_view_download_image_upload_submissions_no_submission(self):
        group_page_id = "image_only/one_image_no_change_answer"
        self.c.force_login(self.ta_participation.user)
        resp = self.post_download_all_submissions_resp(group_page_id)
        self.assertEqual(resp.status_code, 200)
        prefix, zip_file = resp["Content-Disposition"].split('=')
        self.assertEqual(prefix, "attachment; filename")
        self.assertEqual(resp.get('Content-Type'), "application/zip")

        buf = BytesIO(resp.content)
        with zipfile.ZipFile(buf, 'r') as zf:
            self.assertIsNone(zf.testzip())
            self.assertEqual(len(zf.filelist), 1)
            for f in zf.filelist:
                self.assertGreater(f.file_size, 0)
            self.assertEqual(zf.filelist[0].filename, 'submit_summary.csv')
