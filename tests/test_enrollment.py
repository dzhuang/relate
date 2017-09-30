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

from copy import deepcopy

from django.test import TestCase
from django.conf import settings
from django.test.utils import override_settings
from django.core import mail
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse

from course import enrollment
from course.models import (
    Participation, ParticipationRole, ParticipationPreapproval)
from course.constants import participation_status, user_status

from .base_test_mixins import (
    SingleCourseTestMixin, SINGLE_COURSE_SETUP_LIST,
    NONE_PARTICIPATION_USER_CREATE_KWARG_LIST,
    FallBackStorageMessageTestMixin
)
from .utils import LocmemBackendTestsMixin


SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST = (
    deepcopy(SINGLE_COURSE_SETUP_LIST))
_course = SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST[0]["course"]
_course["enrollment_approval_required"] = True

TEST_EMAIL_SUFFIX = "suffix.com"

COURSE_ENROLL_REQUIRE_APPRV_AND_EMAIL_SUFFIX_SETUP_LIST = (
    deepcopy(SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST))
_course = COURSE_ENROLL_REQUIRE_APPRV_AND_EMAIL_SUFFIX_SETUP_LIST[0]["course"]
_course["enrollment_required_email_suffix"] = TEST_EMAIL_SUFFIX

COURSE_ENROLL_REQUIRE_APPRV_AND_VERIFIED_INST_ID_LIST = (
    deepcopy(SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST))
_course = COURSE_ENROLL_REQUIRE_APPRV_AND_VERIFIED_INST_ID_LIST[0]["course"]
_course["preapproval_require_verified_inst_id"] = False

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


class EnrollmentTestBaseMixin(SingleCourseTestMixin,
                              FallBackStorageMessageTestMixin):
    none_participation_user_create_kwarg_list = (
        NONE_PARTICIPATION_USER_CREATE_KWARG_LIST)

    @classmethod
    def setUpTestData(cls):  # noqa
        super(EnrollmentTestBaseMixin, cls).setUpTestData()
        assert cls.non_participation_users.count() >= 4
        cls.non_participation_user1 = cls.non_participation_users[0]
        cls.non_participation_user2 = cls.non_participation_users[1]
        cls.non_participation_user3 = cls.non_participation_users[2]
        cls.non_participation_user4 = cls.non_participation_users[3]
        if cls.non_participation_user1.status != user_status.active:
            cls.non_participation_user1.status = user_status.active
            cls.non_participation_user1.save()
        if cls.non_participation_user2.status != user_status.active:
            cls.non_participation_user2.status = user_status.active
            cls.non_participation_user2.save()
        if cls.non_participation_user3.status != user_status.unconfirmed:
            cls.non_participation_user3.status = user_status.unconfirmed
            cls.non_participation_user3.save()
        if cls.non_participation_user4.status != user_status.unconfirmed:
            cls.non_participation_user4.status = user_status.unconfirmed
            cls.non_participation_user4.save()

    @property
    def enroll_request_url(self):
        return reverse("relate-enroll", args=[self.course.identifier])

    @classmethod
    def get_participation_edit_url(cls, participation_id):
        return reverse("relate-edit_participation",
                       args=[cls.course.identifier, participation_id])

    def get_participation_count_by_status(self, status):
        return Participation.objects.filter(
            course__identifier=self.course.identifier,
            status=status
        ).count()

    @property
    def student_role_post_data(self):
        role, _ = (ParticipationRole.objects.get_or_create(
            course=self.course, identifier="student"))
        return [str(role.pk)]


class EnrollmentSimpleTest(
        LocmemBackendTestsMixin, EnrollmentTestBaseMixin, TestCase):
    courses_setup_list = SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST

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
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertResponseMessagesCount(resp, 2)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLLMENT_SENT_TEXT,
                   enrollment.MESSAGE_ENROLL_REQUEST_PENDING_TEXT])
        self.assertResponseMessageLevelsEqual(
            resp, [messages.INFO, messages.INFO])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)

        # Second and after visits to course page should display only 1 messages
        resp = self.c.get(self.course_page_url)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLL_REQUEST_PENDING_TEXT])

        mailmessage = self.get_the_email_message()
        self.assertEqual(mailmessage["Subject"],
                         enrollment.EMAIL_NEW_ENROLLMENT_REQUEST_TITLE_PATTERN
                         % self.course.identifier)

        self.c.force_login(self.non_participation_user2)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertRedirects(resp, self.course_page_url)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            2)

    # https://github.com/inducer/relate/issues/370
    def test_pending_user_re_enroll_request_failure(self):
        self.create_participation(self.course, self.non_participation_user1,
                                  status=participation_status.requested)
        self.c.force_login(self.non_participation_user1)
        resp = self.c.post(self.enroll_request_url, follow=True)

        # Second enroll request won't send more emails,
        self.assertEqual(len(mail.outbox), 0)

        self.assertResponseMessagesCount(resp, 2)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLL_REQUEST_ALREADY_PENDING_TEXT,
                   enrollment.MESSAGE_ENROLL_REQUEST_PENDING_TEXT])

        self.assertResponseMessageLevelsEqual(
            resp, [messages.ERROR,
                   messages.INFO])

    def test_denied_user_enroll_request_failure(self):
        self.create_participation(self.course, self.non_participation_user1,
                                  status=participation_status.denied)
        self.c.force_login(self.non_participation_user1)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertEqual(len(mail.outbox), 0)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLL_DENIED_NOT_ALLOWED_TEXT])

        self.assertResponseMessageLevelsEqual(
            resp, [messages.ERROR])

    def test_dropped_user_re_enroll_request_failure(self):
        self.create_participation(self.course, self.non_participation_user1,
                                  status=participation_status.dropped)
        self.c.force_login(self.non_participation_user1)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertEqual(len(mail.outbox), 0)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLL_DROPPED_NOT_ALLOWED_TEXT])

        self.assertResponseMessageLevelsEqual(
            resp, [messages.ERROR])

    #  https://github.com/inducer/relate/issues/369
    def test_unconfirmed_user_enroll_request(self):
        self.c.force_login(self.non_participation_user4)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_EMAIL_NOT_CONFIRMED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)

    def test_enroll_request_fail_re_enroll(self):
        self.c.force_login(self.student_participation.user)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_CANNOT_REENROLL_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(len(mail.outbox), 0)

    def test_enroll_by_get(self):
        self.c.force_login(self.non_participation_user1)
        self.c.get(self.enroll_request_url)
        resp = self.c.get(self.course_page_url)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLL_ONLY_ACCEPT_POST_REQUEST_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(len(mail.outbox), 0)

        # for participations, this show MESSAGE_CANNOT_REENROLL_TEXT
        self.c.force_login(self.student_participation.user)
        self.c.get(self.enroll_request_url)
        resp = self.c.get(self.course_page_url)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_CANNOT_REENROLL_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(len(mail.outbox), 0)

    def test_edit_participation_view_get_for_requested(self):
        self.c.force_login(self.non_participation_user1)
        self.c.post(self.enroll_request_url, follow=True)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)
        my_participation = Participation.objects.get(
            user=self.non_participation_user1
        )
        my_participation_edit_url = (
            self.get_participation_edit_url(my_participation.pk))
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

    # {{{ closed https://github.com/inducer/relate/pull/366
    def test_email_with_email_connections1(self):
        # with EMAIL_CONNECTIONS and ENROLLMENT_EMAIL_FROM configured
        with self.settings(
                RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER=False,
                EMAIL_CONNECTIONS=self.email_connections,
                ROBOT_EMAIL_FROM=self.robot_email_from,
                ENROLLMENT_EMAIL_FROM=self.enrollment_email_from):
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url, follow=True)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.enrollment_email_from)

        with self.settings(
                RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER=True,
                EMAIL_CONNECTIONS=self.email_connections,
                ROBOT_EMAIL_FROM=self.robot_email_from,
                ENROLLMENT_EMAIL_FROM=self.enrollment_email_from):
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url, follow=True)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.enrollment_email_from)

    def test_email_with_email_connections2(self):
        # with EMAIL_CONNECTIONS not configured
        with self.settings(
                RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER=False,
                ROBOT_EMAIL_FROM=self.robot_email_from,
                ENROLLMENT_EMAIL_FROM=self.enrollment_email_from):
            if hasattr(settings, ENROLLMENT_EMAIL_FROM):
                del settings.ENROLLMENT_EMAIL_FROM
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url, follow=True)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.robot_email_from)

        with self.settings(
                RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER=True,
                ROBOT_EMAIL_FROM=self.robot_email_from,
                ENROLLMENT_EMAIL_FROM=self.enrollment_email_from):
            if hasattr(settings, ENROLLMENT_EMAIL_FROM):
                del settings.ENROLLMENT_EMAIL_FROM
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url, follow=True)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.robot_email_from)

    def test_email_with_email_connections3(self):
        # with only EMAIL_CONNECTIONS configured
        with self.settings(
                RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER=True,
                EMAIL_CONNECTIONS=self.email_connections,
                ROBOT_EMAIL_FROM=self.robot_email_from):
            if hasattr(settings, ENROLLMENT_EMAIL_FROM):
                del settings.ENROLLMENT_EMAIL_FROM
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url, follow=True)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.robot_email_from)

        with self.settings(
                RELATE_EMAIL_SMTP_ALLOW_NONAUTHORIZED_SENDER=False,
                ROBOT_EMAIL_FROM=self.robot_email_from,
                ENROLLMENT_EMAIL_FROM=self.enrollment_email_from):
            if hasattr(settings, ENROLLMENT_EMAIL_FROM):
                del settings.ENROLLMENT_EMAIL_FROM
            self.c.force_login(self.non_participation_user1)
            self.c.post(self.enroll_request_url, follow=True)
            msg = mail.outbox[0]
            self.assertEqual(msg.from_email, self.robot_email_from)

    # }}}


class EnrollmentDecisionTestMixin(LocmemBackendTestsMixin, EnrollmentTestBaseMixin):
    courses_setup_list = SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST

    @classmethod
    def setUpTestData(cls):  # noqa
        super(EnrollmentDecisionTestMixin, cls).setUpTestData()
        my_participation = cls.create_participation(
            cls.course, cls.non_participation_user1,
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
        cls.drop_post_data = {"drop": [""]}
        cls.drop_post_data.update(form_data)


class EnrollmentDecisionTest(EnrollmentDecisionTestMixin, TestCase):
    courses_setup_list = SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST

    @property
    def add_new_url(self):
        return self.get_participation_edit_url(-1)

    def test_edit_participation_view_enroll_decision_approve(self):
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.post(self.my_participation_edit_url, self.approve_post_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_SUCCESSFULLY_ENROLLED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
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
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLLMENT_DENIED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.denied),
            1)

    def test_edit_participation_view_enroll_decision_drop(self):
        self.c.force_login(self.instructor_participation.user)
        self.create_participation(self.course, self.non_participation_user3,
                                  status=participation_status.active)
        resp = self.c.post(self.my_participation_edit_url, self.drop_post_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.dropped),
            1)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLLMENT_DROPPED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertEqual(len(mail.outbox), 0)

    def test_edit_participation_view_add_new_unconfirmed_user(self):
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(self.add_new_url)
        self.assertTrue(resp.status_code, 200)

        if self.non_participation_user3.status != user_status.unconfirmed:
            self.non_participation_user3.status = user_status.unconfirmed
            self.non_participation_user3.save()

        expected_active_user_count = (
            get_user_model()
            .objects.filter(status=user_status.unconfirmed).count())

        expected_active_participation_count = (
            self.get_participation_count_by_status(participation_status.active))

        form_data = {"user": [str(self.non_participation_user3.pk)],
                     "time_factor": 1,
                     "roles": self.student_role_post_data, "notes": [""],
                     "add_new": True
                     }
        add_post_data = {"submit": [""]}
        add_post_data.update(form_data)
        resp = self.c.post(self.add_new_url, add_post_data, follow=True)
        self.assertFormError(resp, 'form', 'user',
                             enrollment.VALIDATION_ERROR_USER_NOT_CONFIRMED)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.active),
            expected_active_participation_count)

        self.assertEqual(
            get_user_model()
            .objects.filter(status=user_status.unconfirmed).count(),
            expected_active_user_count)
        self.assertResponseMessagesCount(resp, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_edit_participation_view_add_new_active_user(self):
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(self.add_new_url)
        self.assertTrue(resp.status_code, 200)

        if self.non_participation_user4.status != user_status.active:
            self.non_participation_user4.status = user_status.active
            self.non_participation_user4.save()

        expected_active_user_count = (
            get_user_model()
            .objects.filter(status=user_status.unconfirmed).count()
        )

        expected_active_participation_count = (
            self.get_participation_count_by_status(participation_status.active) + 1
        )

        form_data = {"user": [str(self.non_participation_user4.pk)],
                     "time_factor": 1,
                     "roles": self.student_role_post_data, "notes": [""],
                     "add_new": True
                     }
        add_post_data = {"submit": [""]}
        add_post_data.update(form_data)
        resp = self.c.post(self.add_new_url, add_post_data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.active),
            expected_active_participation_count)

        self.assertEqual(
            get_user_model()
            .objects.filter(status=user_status.unconfirmed).count(),
            expected_active_user_count)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_PARTICIPATION_CHANGE_SAVED_TEXT])
        self.assertResponseMessageLevelsEqual(
            resp, [messages.SUCCESS])
        self.assertResponseMessagesCount(resp, 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_edit_participation_view_add_new_integrity_error(self):
        self.c.force_login(self.instructor_participation.user)
        form_data = {"user": [str(self.student_participation.user.pk)],
                     "time_factor": 0.5,
                     "roles": self.student_role_post_data, "notes": [""],
                     "add_new": True
                     }
        add_post_data = {"submit": [""]}
        add_post_data.update(form_data)
        resp = self.c.post(self.add_new_url, add_post_data, follow=True)
        from django.forms.models import ModelChoiceField
        self.assertFormError(
            resp, 'form', 'user',
            ModelChoiceField.default_error_messages['invalid_choice'])

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


class EnrollRequireEmailSuffixTest(LocmemBackendTestsMixin,
                                   EnrollmentTestBaseMixin, TestCase):
    courses_setup_list = (
        COURSE_ENROLL_REQUIRE_APPRV_AND_EMAIL_SUFFIX_SETUP_LIST)

    def test_email_suffix_matched(self):
        self.c.force_login(self.non_participation_user1)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertResponseMessagesCount(resp, 2)
        self.assertResponseMessagesEqual(
            resp, [enrollment.MESSAGE_ENROLLMENT_SENT_TEXT,
                   enrollment.MESSAGE_ENROLL_REQUEST_PENDING_TEXT])
        self.assertResponseMessageLevelsEqual(
            resp, [messages.INFO, messages.INFO])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            1)

    def test_email_suffix_not_matched(self):
        self.c.force_login(self.non_participation_user2)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_EMAIL_SUFFIX_REQUIRED_PATTERN % TEST_EMAIL_SUFFIX])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)

    def test_email_suffix_matched_unconfirmed(self):
        self.c.force_login(self.non_participation_user3)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_EMAIL_NOT_CONFIRMED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)

    def test_email_suffix_not_matched_unconfirmed(self):
        self.c.force_login(self.non_participation_user4)
        resp = self.c.post(self.enroll_request_url, follow=True)
        self.assertResponseMessagesCount(resp, 1)
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_EMAIL_NOT_CONFIRMED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            self.get_participation_count_by_status(participation_status.requested),
            0)


class EnrollmentPreapprovalTestMixin(LocmemBackendTestsMixin,
                                     EnrollmentTestBaseMixin):

    @classmethod
    def setUpTestData(cls):  # noqa
        super(EnrollmentPreapprovalTestMixin, cls).setUpTestData()
        assert cls.non_participation_user1.institutional_id_verified is True
        assert cls.non_participation_user2.institutional_id_verified is False

    @property
    def preapprove_data_emails(self):
        preapproved_user = [self.non_participation_user1,
                            self.non_participation_user2]
        preapproved_data = [u.email for u in preapproved_user]
        return preapproved_data

    @property
    def preapprove_data_institutional_ids(self):
        preapproved_user = [self.non_participation_user1,
                            self.non_participation_user2,
                            self.non_participation_user3]
        preapproved_data = [u.institutional_id for u in preapproved_user]
        return preapproved_data

    @property
    def preapproval_url(self):
        return reverse("relate-create_preapprovals",
                            args=[self.course.identifier])

    @property
    def default_preapprove_role(self):
        role, _ = (ParticipationRole.objects.get_or_create(
            course=self.course, identifier="student"))
        return [str(role.pk)]

    def post_preapprovel(self, user, preapproval_type, preapproval_data=None):
        self.c.force_login(user)
        if preapproval_data is None:
            if preapproval_type == "email":
                preapproval_data = self.preapprove_data_emails
            elif preapproval_type == "institutional_id":
                preapproval_data = self.preapprove_data_institutional_ids

        assert preapproval_data is not None
        assert isinstance(preapproval_data, list)

        data = {
            "preapproval_type": [preapproval_type],
            "preapproval_data": ["\n".join(preapproval_data)],
            "roles": self.student_role_post_data,
            "submit": [""]
        }
        resp = self.c.post(self.preapproval_url, data, follow=True)
        self.c.logout()
        return resp

    def get_preapproval_count(self):
        return ParticipationPreapproval.objects.all().count()


class EnrollmentPreapprovalTest(EnrollmentPreapprovalTestMixin, TestCase):
    courses_setup_list = (
        SINGLE_COURSE_ENROLL_REQUIRE_APPRV_SETUP_LIST)

    def test_preapproval_url_get(self):
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(self.preapproval_url)
        self.assertTrue(resp.status_code, 200)

    def test_preapproval_create_email_type(self):
        resp = self.post_preapprovel(
            self.instructor_participation.user,
            "email",
            self.preapprove_data_emails)
        self.assertEqual(
            self.get_preapproval_count(), len(self.preapprove_data_emails))
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_BATCH_PREAPPROVED_RESULT_PATTERN
             % {
                 'n_created': len(self.preapprove_data_emails),
                 'n_exist': 0,
                 'n_requested_approved': 0
             }]
        )

        # repost same data
        resp = self.post_preapprovel(
            self.instructor_participation.user,
            "email",
            self.preapprove_data_emails)
        self.assertEqual(
            self.get_preapproval_count(), len(self.preapprove_data_emails))
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_BATCH_PREAPPROVED_RESULT_PATTERN
             % {
                 'n_created': 0,
                 'n_exist': len(self.preapprove_data_emails),
                 'n_requested_approved': 0
             }]
        )

    def test_preapproval_create_institutional_id_type(self):
        resp = self.post_preapprovel(
            self.instructor_participation.user, "institutional_id",
            self.preapprove_data_institutional_ids)
        self.assertEqual(
            self.get_preapproval_count(),
            len(self.preapprove_data_institutional_ids))
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_BATCH_PREAPPROVED_RESULT_PATTERN
             % {
                 'n_created': len(self.preapprove_data_institutional_ids),
                 'n_exist': 0,
                 'n_requested_approved': 0
             }]
        )

        # repost same data
        resp = self.post_preapprovel(
            self.instructor_participation.user, "institutional_id",
            self.preapprove_data_institutional_ids)
        self.assertEqual(
            self.get_preapproval_count(),
            len(self.preapprove_data_institutional_ids))
        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_BATCH_PREAPPROVED_RESULT_PATTERN
             % {
                 'n_created': 0,
                 'n_exist': len(self.preapprove_data_institutional_ids),
                 'n_requested_approved': 0
             }]
        )

    def test_preapproval_create_permission_error(self):
        self.c.force_login(self.student_participation.user)
        resp = self.c.get(self.preapproval_url)
        self.assertEqual(resp.status_code, 403)
        resp = self.post_preapprovel(
            self.student_participation.user,
            "email",
            self.preapprove_data_emails)
        self.assertEqual(
            self.get_preapproval_count(), 0)
        self.assertEqual(resp.status_code, 403)

    def test_preapproval_email_type_approve_pendings(self):
        enroll_request_users = [self.non_participation_user1]
        for u in enroll_request_users:
            self.c.force_login(u)
            self.c.post(self.enroll_request_url, follow=True)
            self.c.logout()
        self.flush_mailbox()
        expected_participation_count = (
            self.get_participation_count_by_status(participation_status.active) + 1)
        resp = self.post_preapprovel(
            self.instructor_participation.user, "email",
            self.preapprove_data_emails)
        self.assertEqual(
            self.get_participation_count_by_status(
                participation_status.active), expected_participation_count)

        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_BATCH_PREAPPROVED_RESULT_PATTERN
             % {
                 'n_created': len(self.preapprove_data_emails),
                 'n_exist': 0,
                 'n_requested_approved': len(enroll_request_users)
             }]
        )
        self.assertEqual(
            len([m.to for m in mail.outbox]), len(enroll_request_users))

    def test_preapproval_inst_id_type_approve_pending_require_id_verified(self):
        assert self.course.preapproval_require_verified_inst_id is True
        enroll_request_users = [
            self.non_participation_user1, self.non_participation_user2]
        for u in enroll_request_users:
            self.c.force_login(u)
            self.c.post(self.enroll_request_url, follow=True)
            self.c.logout()
        self.flush_mailbox()
        n_expected_newly_enrolled_users = (
            len([u for u in enroll_request_users if u.institutional_id_verified]))
        expected_participation_count = (
            self.get_participation_count_by_status(participation_status.active)
            + n_expected_newly_enrolled_users
        )
        resp = self.post_preapprovel(
            self.instructor_participation.user, "institutional_id",
            self.preapprove_data_institutional_ids)
        self.assertEqual(
            self.get_participation_count_by_status(
                participation_status.active), expected_participation_count)

        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_BATCH_PREAPPROVED_RESULT_PATTERN
             % {
                 'n_created': len(self.preapprove_data_institutional_ids),
                 'n_exist': 0,
                 'n_requested_approved': n_expected_newly_enrolled_users
             }]
        )
        self.assertEqual(
            len([m.to for m in mail.outbox]), n_expected_newly_enrolled_users)


class EnrollmentPreapprovalInstIdNotRequireVerifiedTest(
                                        EnrollmentPreapprovalTestMixin, TestCase):
    courses_setup_list = (
        COURSE_ENROLL_REQUIRE_APPRV_AND_VERIFIED_INST_ID_LIST)

    def test_preapproval_inst_id_type_approve_pending_not_require_id_verified(self):
        assert self.course.preapproval_require_verified_inst_id is False
        enroll_request_users = [
            self.non_participation_user1, self.non_participation_user2]
        for u in enroll_request_users:
            self.c.force_login(u)
            self.c.post(self.enroll_request_url, follow=True)
            self.c.logout()
        self.flush_mailbox()
        n_expected_newly_enrolled_users = len(enroll_request_users)
        expected_participation_count = (
            self.get_participation_count_by_status(participation_status.active)
            + n_expected_newly_enrolled_users
        )
        resp = self.post_preapprovel(
            self.instructor_participation.user, "institutional_id",
            self.preapprove_data_institutional_ids)
        self.assertEqual(
            self.get_participation_count_by_status(
                participation_status.active), expected_participation_count)

        self.assertResponseMessagesEqual(
            resp,
            [enrollment.MESSAGE_BATCH_PREAPPROVED_RESULT_PATTERN
             % {
                 'n_created': len(self.preapprove_data_institutional_ids),
                 'n_exist': 0,
                 'n_requested_approved': n_expected_newly_enrolled_users
             }]
        )

        self.assertEqual(
            len([m.to for m in mail.outbox]), n_expected_newly_enrolled_users)
