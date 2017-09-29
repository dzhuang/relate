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

from django.test.utils import override_settings
from django.core import mail

try:
    from unittest import mock
except:
    import mock


from copy import deepcopy
from django.urls import reverse
from .base_test_mixins import (
    SingleCourseTestMixin, SINGLE_COURSE_SETUP_LIST,
    NONE_PARTICIPATION_USER_CREATE_KWARG_LIST)
from .utils import LocmemBackendTestsMixin
from django.conf import settings

from django.test import TestCase
from course.views import (
    MESSAGE_ENROLL_REQUEST_PENDING_TEXT
)
from course import enrollment

from course.models import Participation

from course.constants import participation_status, user_status

SINGLE_COURSE_ENROLLMENT_REQUIRE_APPROVAL_SETUP_LIST = (
    deepcopy(SINGLE_COURSE_SETUP_LIST))
SINGLE_COURSE_ENROLLMENT_REQUIRE_APPROVAL_SETUP_LIST[0]["course"]\
    ["enrollment_approval_required"] = True

SINGLE_COURSE_ENROLLMENT_REQUIRE_APPROVAL_AND_EMAIL_SUFFIX_SETUP_LIST = (
    deepcopy(SINGLE_COURSE_ENROLLMENT_REQUIRE_APPROVAL_SETUP_LIST))
SINGLE_COURSE_ENROLLMENT_REQUIRE_APPROVAL_AND_EMAIL_SUFFIX_SETUP_LIST[0]["course"]\
    ["enrollment_required_email_suffix"] = "suffix.com"

EMAIL_CONNECTIONS = "EMAIL_CONNECTIONS"
EMAIL_CONNECTION_DEFAULT = "EMAIL_CONNECTION_DEFAULT"
NO_REPLY_EMAIL_FROM = "NO_REPLY_EMAIL_FROM"
NOTIFICATION_EMAIL_FROM = "NOTIFICATION_EMAIL_FROM"
GRADER_FEEDBACK_EMAIL_FROM = "GRADER_FEEDBACK_EMAIL_FROM"
STUDENT_INTERACT_EMAIL_FROM = "STUDENT_INTERACT_EMAIL_FROM"
ENROLLMENT_EMAIL_FROM = "ENROLLMENT_EMAIL_FROM"


class BaseEmailConnectionMixin:
    EMAIL_CONNECTIONS = None
    EMAIL_CONNECTION_DEFAULT = None
    NO_REPLY_EMAIL_FROM = None
    NOTIFICATION_EMAIL_FROM = None
    GRADER_FEEDBACK_EMAIL_FROM = None
    STUDENT_INTERACT_EMAIL_FROM = None
    ENROLLMENT_EMAIL_FROM = None
    ROBOT_EMAIL_FROM = "robot@example.com"

    def setUp(self):
        kwargs = {}
        for attr in [EMAIL_CONNECTIONS, EMAIL_CONNECTION_DEFAULT,
                     NO_REPLY_EMAIL_FROM, NOTIFICATION_EMAIL_FROM,
                     GRADER_FEEDBACK_EMAIL_FROM, STUDENT_INTERACT_EMAIL_FROM,
                     ENROLLMENT_EMAIL_FROM]:
            attr_value = getattr(self, attr, None)
            if attr_value:
                kwargs.update({attr: attr_value})

        self.settings_email_connection_override = (
            override_settings(**kwargs))
        self.settings_email_connection_override.enable()

    def tearDown(self):
        self.settings_email_connection_override.disable()


class EnrollmentTestBaseMixin(SingleCourseTestMixin):
    courses_setup_list = SINGLE_COURSE_ENROLLMENT_REQUIRE_APPROVAL_SETUP_LIST
    none_participation_user_create_kwarg_list = (
        NONE_PARTICIPATION_USER_CREATE_KWARG_LIST)

    @classmethod
    def setUpTestData(cls):  # noqa
        super(EnrollmentTestBaseMixin, cls).setUpTestData()
        assert cls.non_participation_users.count() >= 2
        cls.non_participation_user1 = cls.non_participation_users[0]
        cls.non_participation_user2 = cls.non_participation_users[1]
        if cls.non_participation_user1.status != user_status.active:
            cls.non_participation_user1.status = user_status.active
            cls.non_participation_user1.save()
        if cls.non_participation_user2.status != user_status.active:
            cls.non_participation_user2.status = user_status.active
            cls.non_participation_user2.save()

    @property
    def enroll_request_url(cls):
        return reverse("relate-enroll", args=[cls.course.identifier])

    @classmethod
    def get_participation_edit_url(cls, participation_id):
        return reverse("relate-edit_participation",
                       args=[cls.course.identifier, participation_id])

    def get_participation_count_by_status(self, status):
        return Participation.objects.filter(
            course__identifier=self.course.identifier,
            status=status
        ).count()


class EnrollmentSimpleTest(
    LocmemBackendTestsMixin, EnrollmentTestBaseMixin, TestCase):

    email_connections = {
        "enroll": {
            'host': 'smtp.gmail.com',
            'username': 'blah@blah.com',
            'password': 'password',
            'port': 587,
            'use_tls': True,
        },
    }

    email_connections_none = {
    }

    enrollment_email_from = "enroll@example.com"

    robot_email_from = "robot@example.com"

    def test_enroll_request_non_participation(self):
        self.c.force_login(self.non_participation_user1)
        self.c.post(self.enroll_request_url)

        # First visit to course page after enroll request should display 2 messages
        resp = self.c.get(self.course_page_url)
        self.assertResponseMessageCount(resp, 2)
        self.assertResponseMessageContains(resp,
                                           [enrollment.MESSAGE_ENROLLMENT_SENT_TEXT,
                                            MESSAGE_ENROLL_REQUEST_PENDING_TEXT])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)

        # Second and after visits to course page should display only 1 messages
        resp = self.c.get(self.course_page_url)
        self.assertResponseMessageCount(resp, 1)
        self.assertResponseMessageContains(resp,
                                           [MESSAGE_ENROLL_REQUEST_PENDING_TEXT])

        mailmessage = self.get_the_email_message()
        self.assertEqual(mailmessage["Subject"],
                         enrollment.EMAIL_NEW_ENROLLMENT_REQUEST_TITLE_PATTERN
                         % self.course.identifier)

        # TODO: should this be fixed?
        # Second enroll request won't send more emails,
        # and won't display more messages.

        # self.c.post(self.enroll_request_url)
        # self.assertEqual(len(mail.outbox), 1)  # failed: 2 != 1
        # resp = self.c.get(self.course_page_url)
        # self.assertResponseMessageCount(resp, 1)  # failed: 2 != 1
        # self.assertResponseMessageContains(resp,
        #                                    [MESSAGE_ENROLL_REQUEST_PENDING_TEXT])

        self.c.force_login(self.non_participation_user2)
        resp = self.c.post(self.enroll_request_url)
        self.assertRedirects(resp, self.course_page_url)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            2)

    def test_enroll_request_fail_re_enroll(self):
        self.c.force_login(self.student_participation.user)
        self.c.post(self.enroll_request_url)
        resp = self.c.get(self.course_page_url)
        self.assertResponseMessageCount(resp, 1)
        self.assertResponseMessageContains(resp,
                                           [enrollment.MESSAGE_CANNOT_REENROLL_TEXT])
        self.assertEqual(len(mail.outbox), 0)

    def test_enroll_by_get(self):
        self.c.force_login(self.non_participation_user1)
        self.c.get(self.enroll_request_url)
        resp = self.c.get(self.course_page_url)
        self.debug_print_response_messages(resp)
        self.assertResponseMessageCount(resp, 1)
        self.assertResponseMessageContains(
                    resp,
                    [enrollment.MESSAGE_ENROLL_ONLY_ACCEPT_POST_REQUEST_TEXT])
        self.assertEqual(len(mail.outbox), 0)

        self.c.force_login(self.student_participation.user)
        self.c.get(self.enroll_request_url)
        resp = self.c.get(self.course_page_url)
        self.assertResponseMessageCount(resp, 1)
        self.assertResponseMessageContains(
                    resp,
                    [enrollment.MESSAGE_CANNOT_REENROLL_TEXT])
        self.assertEqual(len(mail.outbox), 0)

    def test_edit_participation_view_get_for_requested(self):
        self.c.force_login(self.non_participation_user1)
        self.c.post(self.enroll_request_url)
        requested_participations = Participation.objects.filter(
            status=participation_status.requested
        )
        self.assertEqual(requested_participations.count(), 1)
        my_participation_edit_url = (
            self.get_participation_edit_url(requested_participations[0].pk))
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 403)

        self.c.force_login(self.non_participation_user2)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 403)

        self.c.force_login(self.student_participation.user)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 403)

        # only instructor may view edit participation page
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "submit-id-submit")
        self.assertContains(resp, "submit-id-approve")
        self.assertContains(resp, "submit-id-deny")

        self.c.force_login(self.ta_participation.user)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "submit-id-submit")
        self.assertContains(resp, "submit-id-approve")
        self.assertContains(resp, "submit-id-deny")

    def test_edit_participation_view_get_for_enrolled(self):
        my_participation_edit_url = (
            self.get_participation_edit_url(self.student_participation.pk))
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 403)

        self.c.force_login(self.non_participation_user1)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 403)

        self.c.force_login(self.student_participation.user)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 403)

        # only instructor may view edit participation page
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "submit-id-submit")
        self.assertContains(resp, "submit-id-drop")

        self.c.force_login(self.ta_participation.user)
        resp = self.c.get(my_participation_edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "submit-id-submit")
        self.assertContains(resp, "submit-id-drop")

    def test_email_with_email_connections1(self):
        # with EMAIL_CONNECTIONS and ENROLLMENT_EMAIL_FROM configured
        with self.settings(
                EMAIL_CONNECTIONS=self.email_connections,
                ROBOT_EMAIL_FROM=self.robot_email_from,
                ENROLLMENT_EMAIL_FROM=self.enrollment_email_from):
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.enrollment_email_from)

    def test_email_with_email_connections2(self):
        # with EMAIL_CONNECTIONS not configured
        with self.settings(
                ROBOT_EMAIL_FROM=self.robot_email_from,
                ENROLLMENT_EMAIL_FROM=self.enrollment_email_from):
            if hasattr(settings, ENROLLMENT_EMAIL_FROM):
                del settings.ENROLLMENT_EMAIL_FROM
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.robot_email_from)

    def test_email_with_email_connections3(self):
        # with only EMAIL_CONNECTIONS configured
        with self.settings(
                EMAIL_CONNECTIONS=self.email_connections,
                ROBOT_EMAIL_FROM=self.robot_email_from):
            if hasattr(settings, ENROLLMENT_EMAIL_FROM):
                del settings.ENROLLMENT_EMAIL_FROM
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.robot_email_from)


class EnrollmentDecisionTestMixin(LocmemBackendTestsMixin, EnrollmentTestBaseMixin):
    @classmethod
    def setUpTestData(cls):  # noqa
        super(EnrollmentDecisionTestMixin, cls).setUpTestData()
        my_participation = cls.create_participation(cls.course,
                                 cls.non_participation_user1,
                                 status=participation_status.requested)
        time_factor = [str(my_participation.time_factor)]
        roles = [str(r.pk) for r in my_participation.roles.all()]
        notes = [str(my_participation.notes)]

        cls.my_participation_edit_url = (
            cls.get_participation_edit_url(my_participation.pk))

        form_data = {"time_factor": time_factor,
                     "roles": roles, "notes": notes}
        cls.approve_post_data = {"approve": [""]}
        cls.approve_post_data.update(form_data)
        cls.deny_post_data = {"deny": [""]}
        cls.deny_post_data.update(form_data)



class EnrollmentDecisionTest(EnrollmentDecisionTestMixin, TestCase):
    def test_edit_participation_view_enroll_decision_approve(self):
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.post(self.my_participation_edit_url, self.approve_post_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Participation.objects.filter(
            status=participation_status.requested).count(), 0)
        self.assertResponseMessageContains(resp,
                                   enrollment.MESSAGE_SUCCESSFULLY_ENROLLED_TEXT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)

    def test_edit_participation_view_enroll_decision_approve_no_permission1(self):
        self.c.force_login(self.student_participation.user)
        resp = self.c.post(self.my_participation_edit_url, self.approve_post_data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)

    def test_edit_participation_view_enroll_decision_approve_no_permission2(self):
        self.c.force_login(self.non_participation_user1)
        resp = self.c.post(self.my_participation_edit_url, self.approve_post_data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)

    def test_edit_participation_view_enroll_decision_deny(self):
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.post(self.my_participation_edit_url, self.deny_post_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Participation.objects.filter(
            status=participation_status.requested).count(), 0)
        self.assertResponseMessageContains(resp,
                                   enrollment.MESSAGE_SUCCESSFULLY_ENROLLED_TEXT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.denied),
            1)

    def test_edit_participation_view_enroll_decision_deny_no_permission1(self):
        self.c.force_login(self.student_participation.user)
        resp = self.c.post(self.my_participation_edit_url, self.deny_post_data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.denied),
            0)

    def test_edit_participation_view_enroll_decision_deny_no_permission2(self):
        self.c.force_login(self.non_participation_user1)
        resp = self.c.post(self.my_participation_edit_url, self.deny_post_data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.denied),
            0)