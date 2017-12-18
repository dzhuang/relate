from __future__ import division

__copyright__ = "Copyright (C) 2017 Dong Zhuang, Andreas Kloeckner, Zesheng Wang"

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
import datetime
from django.conf import settings
from django.test import Client, override_settings
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from relate.utils import force_remove_path
from course.models import (
    Course, Participation, ParticipationRole, FlowSession, FlowPageData,
    FlowPageVisit)
from course.constants import participation_status, user_status
from .utils import mock

CREATE_SUPERUSER_KWARGS = {
    "username": "test_admin",
    "password": "test_admin",
    "email": "test_admin@example.com",
    "first_name": "Test",
    "last_name": "Admin"}

SINGLE_COURSE_SETUP_LIST = [
    {
        "course": {
            "identifier": "test-course",
            "name": "Test Course",
            "number": "CS123",
            "time_period": "Fall 2016",
            "hidden": False,
            "listed": True,
            "accepts_enrollment": True,
            "git_source": "git://github.com/inducer/relate-sample",
            "course_file": "course.yml",
            "events_file": "events.yml",
            "enrollment_approval_required": False,
            "enrollment_required_email_suffix": "",
            "preapproval_require_verified_inst_id": True,
            "from_email": "inform@tiker.net",
            "notify_email": "inform@tiker.net"},
        "participations": [
            {
                "role_identifier": "instructor",
                "user": {
                    "username": "test_instructor",
                    "password": "test_instructor",
                    "email": "test_instructor@example.com",
                    "first_name": "Test",
                    "last_name": "Instructor"},
                "status": participation_status.active
            },
            {
                "role_identifier": "ta",
                "user": {
                    "username": "test_ta",
                    "password": "test",
                    "email": "test_ta@example.com",
                    "first_name": "Test",
                    "last_name": "TA"},
                "status": participation_status.active
            },
            {
                "role_identifier": "student",
                "user": {
                    "username": "test_student",
                    "password": "test",
                    "email": "test_student@example.com",
                    "first_name": "Test",
                    "last_name": "Student"},
                "status": participation_status.active
            }
        ],
    }
]


NONE_PARTICIPATION_USER_CREATE_KWARG_LIST = [
    {
        "username": "test_user1",
        "password": "test_user1",
        "email": "test_user1@suffix.com",
        "first_name": "Test",
        "last_name": "User1",
        "institutional_id": "test_user1_institutional_id",
        "institutional_id_verified": True,
        "status": user_status.active
    },
    {
        "username": "test_user2",
        "password": "test_user2",
        "email": "test_user2@nosuffix.com",
        "first_name": "Test",
        "last_name": "User2",
        "institutional_id": "test_user2_institutional_id",
        "institutional_id_verified": False,
        "status": user_status.active
    },
    {
        "username": "test_user3",
        "password": "test_user3",
        "email": "test_user3@suffix.com",
        "first_name": "Test",
        "last_name": "User3",
        "institutional_id": "test_user3_institutional_id",
        "institutional_id_verified": True,
        "status": user_status.unconfirmed
    },
    {
        "username": "test_user4",
        "password": "test_user4",
        "email": "test_user4@no_suffix.com",
        "first_name": "Test",
        "last_name": "User4",
        "institutional_id": "test_user4_institutional_id",
        "institutional_id_verified": False,
        "status": user_status.unconfirmed
    }
]


class ResponseContextMixin(object):
    """
    Response context refers to "the template Context instance that was used
    to render the template that produced the response content".
    Ref: https://docs.djangoproject.com/en/dev/topics/testing/tools/#django.test.Response.context  # noqa
    """
    def get_response_context_value_by_name(self, response, context_name):
        value = response.context.__getitem__(context_name)
        self.assertIsNotNone(
            value,
            msg="%s does not exist in given response" % context_name)
        return value

    def assertResponseContextIsNone(self, resp, context_name):  # noqa
        try:
            value = self.get_response_context_value_by_name(resp, context_name)
        except AssertionError:
            # the context item doesn't exist
            pass
        else:
            self.assertIsNone(value)

    def assertResponseContextIsNotNone(self, resp, context_name):  # noqa
        value = self.get_response_context_value_by_name(resp, context_name)
        self.assertIsNotNone(value)

    def assertResponseContextEqual(self, resp, context_name, expected_value):  # noqa
        value = self.get_response_context_value_by_name(resp, context_name)
        self.assertEqual(value, expected_value)

    def assertResponseContextContains(self, resp,  # noqa
                                      context_name, expected_value, html=False):
        value = self.get_response_context_value_by_name(resp, context_name)
        if not html:
            self.assertIn(expected_value, value)
        else:
            self.assertInHTML(expected_value, value)

    def assertResponseContextRegex(  # noqa
            self, resp,  # noqa
            context_name, expected_value_regex):
        value = self.get_response_context_value_by_name(resp, context_name)
        six.assertRegex(self, value, expected_value_regex)

    def get_response_context_answer_feedback(self, response):
        return self.get_response_context_value_by_name(response, "feedback")

    def assertResponseContextAnswerFeedbackContainsFeedback(  # noqa
                                        self, response, expected_feedback):
        answer_feedback = self.get_response_context_answer_feedback(response)
        self.assertTrue(hasattr(answer_feedback, "feedback"))
        self.assertIn(expected_feedback, answer_feedback.feedback)

    def assertResponseContextAnswerFeedbackCorrectnessEquals(  # noqa
                                        self, response, expected_correctness):
        answer_feedback = self.get_response_context_answer_feedback(response)
        if expected_correctness is None:
            try:
                self.assertTrue(hasattr(answer_feedback, "correctness"))
            except AssertionError:
                pass
            else:
                self.assertIsNone(answer_feedback.correctness)
        else:
            from decimal import Decimal
            self.assertEqual(answer_feedback.correctness,
                                    Decimal(str(expected_correctness)))

    def get_response_body(self, response):
        return self.get_response_context_value_by_name(response, "body")

    def get_page_response_correct_answer(self, response):
        return self.get_response_context_value_by_name(response, "correct_answer")

    def get_page_response_feedback(self, response):
        return self.get_response_context_value_by_name(response, "feedback")

    def debug_print_response_context_value(self, resp, context_name):
        try:
            value = self.get_response_context_value_by_name(resp, context_name)
            print("\n-----------context %s-------------"
                  % context_name)
            if isinstance(value, (list, tuple)):
                from course.validation import ValidationWarning
                for v in value:
                    if isinstance(v, ValidationWarning):
                        print(v.text)
                    else:
                        print(repr(v))
            else:
                print(value)
            print("-----------context end-------------\n")
        except AssertionError:
            print("\n-------no value for context %s----------" % context_name)


class SuperuserCreateMixin(ResponseContextMixin):
    create_superuser_kwargs = CREATE_SUPERUSER_KWARGS

    @classmethod
    def setUpTestData(cls):  # noqa
        # Create superuser, without this, we cannot
        # create user, course and participation.
        cls.superuser = cls.create_superuser()
        cls.c = Client()
        super(SuperuserCreateMixin, cls).setUpTestData()

    @classmethod
    def tearDownClass(cls):  # noqa
        super(SuperuserCreateMixin, cls).tearDownClass()

    @classmethod
    def create_superuser(cls):
        return get_user_model().objects.create_superuser(
                                                **cls.create_superuser_kwargs)

    def get_impersonate_view_url(self):
        return reverse("relate-impersonate")

    def get_stop_impersonate_view_url(self):
        return reverse("relate-stop_impersonating")

    def get_impersonate(self):
        return self.c.get(self.get_impersonate_view_url())

    def post_impersonate(self, impersonatee, follow=True):
        data = {"add_impersonation_header": ["on"],
                "submit": [''],
                }
        data["user"] = [str(impersonatee.pk)]
        return self.c.post(self.get_impersonate_view_url(), data, follow=follow)

    def get_stop_impersonate(self, follow=True):
        return self.c.get(self.get_stop_impersonate_view_url(), follow=follow)

    def post_stop_impersonate(self, follow=True):
        data = {"submit": ['']}
        return self.c.post(
            self.get_stop_impersonate_view_url(), data, follow=follow)

    def get_fake_time_url(self):
        return reverse("relate-set_fake_time")

    def get_set_fake_time(self):
        return self.c.get(self.get_fake_time_url())

    def post_set_fake_time(self, data, follow=True):
        return self.c.post(self.get_fake_time_url(), data, follow=follow)

    def assertSessionFakeTimeEqual(self, session, expected_date_time):  # noqa
        fake_time_timestamp = session.get("relate_fake_time", None)
        if fake_time_timestamp is None:
            faked_time = None
            if expected_date_time is not None:
                raise AssertionError(
                    "the session doesn't have 'relate_fake_time' attribute")
        else:
            faked_time = datetime.datetime.fromtimestamp(fake_time_timestamp)
        self.assertEqual(faked_time, expected_date_time)

    def assertSessionFakeTimeIsNone(self, session):  # noqa
        self.assertSessionFakeTimeEqual(session, None)

    def get_set_pretend_facilities_url(self):
        return reverse("relate-set_pretend_facilities")

    def get_set_pretend_facilities(self):
        return self.c.get(self.get_set_pretend_facilities_url())

    def post_set_pretend_facilities(self, data, follow=True):
        return self.c.post(self.get_set_pretend_facilities_url(), data,
                           follow=follow)

    def assertSessionPretendFacilitiesContains(self, session, expected_facilities):  # noqa
        pretended = session.get("relate_pretend_facilities", None)
        if expected_facilities is None:
            return self.assertIsNone(pretended)
        if pretended is None:
            raise AssertionError(
                "the session doesn't have "
                "'relate_pretend_facilities' attribute")

        if isinstance(expected_facilities, (list, tuple)):
            self.assertTrue(set(expected_facilities).issubset(set(pretended)))
        else:
            self.assertTrue(expected_facilities in pretended)

    def assertSessionPretendFacilitiesIsNone(self, session):  # noqa
        pretended = session.get("relate_pretend_facilities", None)
        self.assertIsNone(pretended)


# {{{ defined here so that they can be used by in classmethod and instance method

def get_flow_page_ordinal_from_page_id(flow_session_id, page_id):
    flow_page_data = FlowPageData.objects.get(
        flow_session__id=flow_session_id,
        page_id=page_id
    )
    return flow_page_data.ordinal


def get_flow_page_id_from_page_ordinal(flow_session_id, ordinal):
    flow_page_data = FlowPageData.objects.get(
        flow_session__id=flow_session_id,
        ordinal=ordinal
    )
    return flow_page_data.page_id

# }}}


class CoursesTestMixinBase(SuperuserCreateMixin):

    # A list of Dicts, each of which contain a course dict and a list of
    # participations. See SINGLE_COURSE_SETUP_LIST for the setup for one course.
    courses_setup_list = []
    none_participation_user_create_kwarg_list = []
    courses_attributes_extra_list = None

    @classmethod
    def setUpTestData(cls):  # noqa
        super(CoursesTestMixinBase, cls).setUpTestData()
        cls.n_courses = 0
        if cls.courses_attributes_extra_list is not None:
            if (len(cls.courses_attributes_extra_list)
                    != len(cls.courses_setup_list)):
                raise ValueError(
                    "'courses_attributes_extra_list' must has equal length "
                    "with courses")

        for i, course_setup in enumerate(cls.courses_setup_list):
            if "course" not in course_setup:
                continue

            cls.n_courses += 1
            course_identifier = course_setup["course"]["identifier"]
            cls.remove_exceptionally_undelete_course_repos(course_identifier)
            course_setup_kwargs = course_setup["course"]
            if cls.courses_attributes_extra_list:
                extra_attrs = cls.courses_attributes_extra_list[i]
                assert isinstance(extra_attrs, dict)
                course_setup_kwargs.update(extra_attrs)
            cls.create_course(**course_setup_kwargs)
            course = Course.objects.get(identifier=course_identifier)
            if "participations" in course_setup:
                for participation in course_setup["participations"]:
                    create_user_kwargs = participation.get("user")
                    if not create_user_kwargs:
                        continue
                    role_identifier = participation.get("role_identifier")
                    if not role_identifier:
                        continue
                    cls.create_participation(
                        course=course,
                        user_or_create_user_kwargs=create_user_kwargs,
                        role_identifier=role_identifier,
                        status=participation.get("status",
                                                 participation_status.active)
                    )

                    # Remove superuser from participation for further test
                    # such as impersonate in auth module
                    if role_identifier == "instructor":
                        try:
                            superuser_participations = (
                                Participation.objects.filter(user=cls.superuser))
                            for sp in superuser_participations:
                                Participation.delete(sp)
                        except Participation.DoesNotExist:
                            pass
            cls.non_participation_users = get_user_model().objects.none
            if cls.none_participation_user_create_kwarg_list:
                pks = []
                for create_user_kwargs in (
                        cls.none_participation_user_create_kwarg_list):
                    user = cls.create_user(create_user_kwargs)
                    pks.append(user.pk)
                cls.non_participation_users = (
                    get_user_model().objects.filter(pk__in=pks))

        cls.course_qset = Course.objects.all()

    @classmethod
    def remove_exceptionally_undelete_course_repos(cls, course_identifier):
        """
        Remove existing course repo folders resulted in unexpected
        exceptions in previous tests.
        """
        repo_path = os.path.join(settings.GIT_ROOT, course_identifier)
        try:
            force_remove_path(repo_path)
        except OSError:
            if not os.path.isdir(repo_path):
                # The repo path does not exist, that's good!
                return
            raise

    @classmethod
    def remove_course_repo(cls, course):
        from course.content import get_course_repo_path
        repo_path = get_course_repo_path(course)
        force_remove_path(repo_path)

    @classmethod
    def tearDownClass(cls):
        cls.c.logout()
        # Remove repo folder for all courses
        for course in Course.objects.all():
            cls.remove_course_repo(course)
        super(CoursesTestMixinBase, cls).tearDownClass()

    @classmethod
    def create_user(cls, create_user_kwargs):
        user, created = get_user_model().objects.get_or_create(
            email__iexact=create_user_kwargs["email"], defaults=create_user_kwargs)
        if created:
            try:
                # TODO: why pop failed here?
                password = create_user_kwargs["password"]
            except Exception:
                raise
            user.set_password(password)
            user.save()
        return user

    @classmethod
    def create_participation(
            cls, course, user_or_create_user_kwargs,
            role_identifier=None, status=None):
        if isinstance(user_or_create_user_kwargs, get_user_model()):
            user = user_or_create_user_kwargs
        else:
            assert isinstance(user_or_create_user_kwargs, dict)
            user = cls.create_user(user_or_create_user_kwargs)
        if status is None:
            status = participation_status.active
        participation, p_created = Participation.objects.get_or_create(
            user=user,
            course=course,
            status=status
        )
        if role_identifier is None:
            role_identifier = "student"
        if p_created:
            role = ParticipationRole.objects.filter(
                course=course, identifier=role_identifier)
            participation.roles.set(role)
        return participation

    @classmethod
    def create_course(cls, **create_course_kwargs):
        cls.c.force_login(cls.superuser)
        cls.c.post(reverse("relate-set_up_new_course"), create_course_kwargs)

    @classmethod
    def get_course_page_url(cls, course_identifier=None):
        course_identifier = course_identifier or cls.get_default_course_identifier()
        return reverse("relate-course_page", args=[course_identifier])

    def get_logged_in_user(self):
        try:
            logged_in_user_id = self.c.session['_auth_user_id']
            from django.contrib.auth import get_user_model
            logged_in_user = get_user_model().objects.get(
                pk=int(logged_in_user_id))
        except KeyError:
            logged_in_user = None
        return logged_in_user

    def temporarily_switch_to_user(self, switch_to):
        _self = self

        from functools import wraps

        class ClientUserSwitcher(object):
            def __init__(self, switch_to):
                self.client = _self.c
                self.switch_to = switch_to
                self.logged_in_user = _self.get_logged_in_user()

            def __enter__(self):
                if self.logged_in_user == self.switch_to:
                    return
                if self.switch_to is None:
                    self.client.logout()
                    return
                self.client.force_login(self.switch_to)

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.logged_in_user == self.switch_to:
                    return
                if self.logged_in_user is None:
                    self.client.logout()
                    return
                self.client.force_login(self.logged_in_user)

            def __call__(self, func):
                @wraps(func)
                def wrapper(*args, **kw):
                    with self:
                        return func(*args, **kw)
                return wrapper

        return ClientUserSwitcher(switch_to)

    @classmethod
    def get_default_course_identifier(cls):
        if Course.objects.count() > 1:
            raise AttributeError(
                "course_identifier can not be omitted for "
                "testcases with more than one courses")
        raise NotImplementedError

    def get_latest_session_id(self, course_identifier):
        flow_session_qset = FlowSession.objects.filter(
            course__identifier=course_identifier).order_by('-pk')[:1]
        if flow_session_qset:
            return flow_session_qset[0].id
        else:
            return None

    def get_default_flow_session_id(self, course_identifier):
        raise NotImplementedError

    @classmethod
    def update_default_flow_session_id(cls, course_identifier):
        raise NotImplementedError

    def get_default_instructor_user(self, course_identifier):
        return Participation.objects.filter(
            course__identifier=course_identifier,
            roles__identifier="instructor",
            status=participation_status.active
        ).first().user

    @classmethod
    def start_flow(cls, flow_id, course_identifier=None):
        """
        Notice: this is a classmethod, so this will change the data
        created in setUpTestData, so don't do this in individual tests, or
        testdata will be different between tests.
        """
        course_identifier = course_identifier or cls.get_default_course_identifier()
        existing_session_count = FlowSession.objects.all().count()
        params = {"course_identifier": course_identifier,
                  "flow_id": flow_id}
        resp = cls.c.post(reverse("relate-view_start_flow", kwargs=params))
        assert resp.status_code == 302
        new_session_count = FlowSession.objects.all().count()
        assert new_session_count == existing_session_count + 1
        _, _, params = resolve(resp.url)
        del params["ordinal"]
        cls.default_flow_params = params
        cls.update_default_flow_session_id(course_identifier)
        return resp

    @classmethod
    def end_flow(cls, course_identifier, flow_session_id):
        """
        Be cautious that this is a classmethod
        """
        params = {
            "course_identifier": course_identifier,
            "flow_session_id": flow_session_id
        }
        resp = cls.c.post(reverse("relate-finish_flow_session_view",
                                  kwargs=params), {'submit': ['']})
        return resp

    def get_flow_params(self, course_identifier=None, flow_session_id=None):
        course_identifier = (
            course_identifier or self.get_default_course_identifier())
        if flow_session_id is None:
            flow_session_id = self.get_default_flow_session_id(course_identifier)
        return {
            "course_identifier": course_identifier,
            "flow_session_id": flow_session_id
        }

    def get_page_params(self, course_identifier=None, flow_session_id=None,
                        ordinal=None):
        page_params = self.get_flow_params(course_identifier, flow_session_id)
        if ordinal is None:
            ordinal = 0
        page_params.update({"ordinal": ordinal})
        return page_params

    def get_ordinal_via_page_id(
            self, page_id, course_identifier=None, flow_session_id=None):
        flow_params = self.get_flow_params(course_identifier, flow_session_id)
        return (
            get_flow_page_ordinal_from_page_id(
                flow_params["flow_session_id"], page_id))

    def get_page_view_url_by_ordinal(
            self, viewname, ordinal, course_identifier=None, flow_session_id=None):
        page_params = self.get_page_params(
            course_identifier, flow_session_id, ordinal)
        return reverse(viewname, kwargs=page_params)

    def get_page_view_url_by_page_id(
            self, viewname, page_id, course_identifier=None, flow_session_id=None):
        ordinal = self.get_ordinal_via_page_id(
            page_id, course_identifier, flow_session_id)
        return self.get_page_view_url_by_ordinal(
            viewname, ordinal, course_identifier, flow_session_id)

    def get_page_url_by_ordinal(
            self, ordinal, course_identifier=None, flow_session_id=None):
        return self.get_page_view_url_by_ordinal(
            "relate-view_flow_page",
            ordinal, course_identifier, flow_session_id)

    def get_page_url_by_page_id(
            self, page_id, course_identifier=None, flow_session_id=None):
        ordinal = self.get_ordinal_via_page_id(
            page_id, course_identifier, flow_session_id)
        return self.get_page_url_by_ordinal(
            ordinal, course_identifier, flow_session_id)

    def get_page_grading_url_by_ordinal(
            self, ordinal, course_identifier=None, flow_session_id=None):
        return self.get_page_view_url_by_ordinal(
            "relate-grade_flow_page",
            ordinal, course_identifier, flow_session_id)

    def get_page_grading_url_by_page_id(
            self, page_id, course_identifier=None, flow_session_id=None):
        ordinal = self.get_ordinal_via_page_id(
            page_id, course_identifier, flow_session_id)
        return self.get_page_grading_url_by_ordinal(
            ordinal, course_identifier, flow_session_id)

    def post_answer_by_ordinal(
            self, ordinal, answer_data,
            course_identifier=None, flow_session_id=None):
        submit_data = answer_data
        submit_data.update({"submit": ["Submit final answer"]})
        resp = self.c.post(
            self.get_page_url_by_ordinal(
                ordinal, course_identifier, flow_session_id),
            submit_data)
        return resp

    def post_answer_by_page_id(self, page_id, answer_data,
                               course_identifier=None, flow_session_id=None):
        page_ordinal = self.get_ordinal_via_page_id(
            page_id, course_identifier, flow_session_id)
        return self.post_answer_by_ordinal(
            page_ordinal, answer_data, course_identifier, flow_session_id)

    @classmethod
    def post_answer_by_ordinal_class(cls, ordinal, answer_data,
                                     course_identifier, flow_session_id):
        submit_data = answer_data
        submit_data.update({"submit": ["Submit final answer"]})
        page_params = {
            "course_identifier": course_identifier,
            "flow_session_id": flow_session_id,
            "ordinal": ordinal
        }
        page_url = reverse("relate-view_flow_page", kwargs=page_params)
        resp = cls.c.post(page_url, submit_data)
        return resp

    @classmethod
    def post_answer_by_page_id_class(cls, page_id, answer_data,
                                     course_identifier, flow_session_id):
        ordinal = get_flow_page_ordinal_from_page_id(flow_session_id, page_id)
        return cls.post_answer_by_ordinal_class(ordinal, answer_data,
                                                course_identifier, flow_session_id)

    def post_grade_by_ordinal(self, ordinal, grade_data,
                              course_identifier=None, flow_session_id=None,
                              force_login_instructor=True):
        post_data = {"submit": [""]}
        post_data.update(grade_data)

        page_params = self.get_page_params(
            course_identifier, flow_session_id, ordinal)

        force_login_user = self.get_logged_in_user()
        if force_login_instructor:
            force_login_user = self.get_default_instructor_user(
                page_params["course_identifier"])

        with self.temporarily_switch_to_user(force_login_user):
            response = self.c.post(
                self.get_page_grading_url_by_ordinal(**page_params),
                data=post_data,
                follow=True)
        return response

    def post_grade_by_page_id(self, page_id, grade_data,
                              course_identifier=None, flow_session_id=None,
                              force_login_instructor=True):
        ordinal = self.get_ordinal_via_page_id(
            page_id, course_identifier, flow_session_id)

        return self.post_grade_by_ordinal(
            ordinal, grade_data, course_identifier,
            flow_session_id, force_login_instructor)

    def assertSessionScoreEqual(  # noqa
            self, expect_score, course_identifier=None, flow_session_id=None):
        if flow_session_id is None:
            flow_params = self.get_flow_params(course_identifier, flow_session_id)
            flow_session_id = flow_params["flow_session_id"]
        flow_session = FlowSession.objects.get(id=flow_session_id)
        if expect_score is not None:
            from decimal import Decimal
            self.assertEqual(flow_session.points, Decimal(str(expect_score)))
        else:
            self.assertIsNone(flow_session.points)

    def get_page_submit_history_url_by_ordinal(
            self, ordinal, course_identifier=None, flow_session_id=None):
        return self.get_page_view_url_by_ordinal(
            "relate-get_prev_answer_visits_dropdown_content",
            ordinal, course_identifier, flow_session_id)

    def get_page_grade_history_url_by_ordinal(
            self, ordinal, course_identifier=None, flow_session_id=None):
        return self.get_page_view_url_by_ordinal(
            "relate-get_prev_grades_dropdown_content",
            ordinal, course_identifier, flow_session_id)

    def get_page_submit_history_by_ordinal(
            self, ordinal, course_identifier=None, flow_session_id=None):
        resp = self.c.get(
            self.get_page_submit_history_url_by_ordinal(
                ordinal, course_identifier, flow_session_id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return resp

    def get_page_grade_history_by_ordinal(
            self, ordinal, course_identifier=None, flow_session_id=None):
        resp = self.c.get(
            self.get_page_grade_history_url_by_ordinal(
                ordinal, course_identifier, flow_session_id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return resp

    def assertSubmitHistoryItemsCount(  # noqa
            self, ordinal, expected_count, course_identifier=None,
            flow_session_id=None):
        resp = self.get_page_submit_history_by_ordinal(
            ordinal, course_identifier, flow_session_id)
        import json
        result = json.loads(resp.content.decode())["result"]
        self.assertEqual(len(result), expected_count)

    def assertGradeHistoryItemsCount(  # noqa
            self, ordinal, expected_count,
            course_identifier=None,
            flow_session_id=None,
            force_login_instructor=True):

        if course_identifier is None:
            course_identifier = self.get_default_course_identifier()

        if force_login_instructor:
            switch_to = self.get_default_instructor_user(course_identifier)
        else:
            switch_to = self.get_logged_in_user()

        with self.temporarily_switch_to_user(switch_to):
            resp = self.get_page_grade_history_by_ordinal(
                ordinal, course_identifier, flow_session_id)

        import json
        result = json.loads(resp.content.decode())["result"]
        self.assertEqual(len(result), expected_count)

    def get_update_course_url(self, course_identifier=None):
        if course_identifier is None:
            course_identifier = self.get_default_course_identifier()
        return reverse("relate-update_course", args=[course_identifier])

    def update_course_content(self, commit_sha,
                              fetch_update=False,
                              prevent_discarding_revisions=True,
                              force_login_instructor=True,
                              course_identifier=None,
                              ):

        if course_identifier is None:
            course_identifier = self.get_default_course_identifier()

        try:
            commit_sha = commit_sha.decode()
        except Exception:
            pass

        data = {"new_sha": [commit_sha]}

        if not prevent_discarding_revisions:
            data["prevent_discarding_revisions"] = ["on"]

        if not fetch_update:
            data["update"] = ["Update"]
        else:
            data["fetch_update"] = ["Fetch and update"]

        force_login_user = None
        if force_login_instructor:
            force_login_user = self.get_default_instructor_user(course_identifier)

        with self.temporarily_switch_to_user(force_login_user):
            response = self.c.post(
                self.get_update_course_url(course_identifier), data)
            updated_course = Course.objects.get(identifier=course_identifier)
            updated_course.refresh_from_db()

        return response

    def get_page_data_by_page_id(
            self, page_id, course_identifier=None, flow_session_id=None):
        flow_params = self.get_flow_params(course_identifier, flow_session_id)
        return FlowPageData.objects.get(
            flow_session_id=flow_params["flow_session_id"], page_id=page_id)

    def get_page_visits(self, course_identifier=None,
                        flow_session_id=None, ordinal=None, page_id=None,
                        **kwargs):
        query_kwargs = {}
        if kwargs.get("answer_visit", False):
            query_kwargs.update({"answer__isnull": False})
        flow_params = self.get_flow_params(course_identifier, flow_session_id)
        query_kwargs.update({"flow_session_id": flow_params["flow_session_id"]})
        if ordinal is not None:
            query_kwargs.update({"page_data__ordinal": ordinal})
        elif page_id is not None:
            query_kwargs.update({"page_data__page_id": page_id})
        return FlowPageVisit.objects.filter(**query_kwargs)

    def get_last_answer_visit(self, course_identifier=None,
                              flow_session_id=None, ordinal=None,
                              page_id=None, assert_not_none=True):
        result_qset = self.get_page_visits(course_identifier,
                             flow_session_id, ordinal, page_id,
                             answer_visit=True).order_by('-pk')[:1]
        if result_qset:
            result = result_qset[0]
        else:
            result = None
        if assert_not_none:
            self.assertIsNotNone(result, "The query returns None")
        return result


class SingleCourseTestMixin(CoursesTestMixinBase):
    courses_setup_list = SINGLE_COURSE_SETUP_LIST

    @classmethod
    def setUpTestData(cls):  # noqa
        super(SingleCourseTestMixin, cls).setUpTestData()
        assert len(cls.course_qset) == 1
        cls.course = cls.course_qset.first()
        cls.instructor_participation = Participation.objects.filter(
            course=cls.course,
            roles__identifier="instructor",
            status=participation_status.active
        ).first()
        assert cls.instructor_participation

        cls.student_participation = Participation.objects.filter(
            course=cls.course,
            roles__identifier="student",
            status=participation_status.active
        ).first()
        assert cls.student_participation

        cls.ta_participation = Participation.objects.filter(
            course=cls.course,
            roles__identifier="ta",
            status=participation_status.active
        ).first()
        assert cls.ta_participation
        cls.c.logout()
        cls.course_page_url = cls.get_course_page_url()

    def setUp(self):  # noqa
        super(SingleCourseTestMixin, self).setUp()

        # reload objects created during setUpTestData in case they were modified in
        # tests. Ref: https://goo.gl/AuzJRC#django.test.TestCase.setUpTestData
        self.course.refresh_from_db()
        self.instructor_participation.refresh_from_db()
        self.student_participation.refresh_from_db()
        self.ta_participation.refresh_from_db()

    @classmethod
    def get_default_course_identifier(cls):
        return cls.course.identifier


class TwoCourseTestMixin(CoursesTestMixinBase):
    courses_setup_list = []

    @classmethod
    def setUpTestData(cls):  # noqa
        super(TwoCourseTestMixin, cls).setUpTestData()
        assert len(cls.course_qset) == 2, (
            "'courses_setup_list' should contain two courses")
        cls.course1 = cls.course_qset.first()
        cls.course1_instructor_participation = Participation.objects.filter(
            course=cls.course1,
            roles__identifier="instructor",
            status=participation_status.active
        ).first()
        assert cls.course1_instructor_participation

        cls.course1_student_participation = Participation.objects.filter(
            course=cls.course1,
            roles__identifier="student",
            status=participation_status.active
        ).first()
        assert cls.course1_student_participation

        cls.course1_ta_participation = Participation.objects.filter(
            course=cls.course1,
            roles__identifier="ta",
            status=participation_status.active
        ).first()
        assert cls.course1_ta_participation
        cls.course1_page_url = cls.get_course_page_url(cls.course1.identifier)

        cls.course2 = cls.course_qset.last()
        cls.course2_instructor_participation = Participation.objects.filter(
            course=cls.course2,
            roles__identifier="instructor",
            status=participation_status.active
        ).first()
        assert cls.course2_instructor_participation

        cls.course2_student_participation = Participation.objects.filter(
            course=cls.course2,
            roles__identifier="student",
            status=participation_status.active
        ).first()
        assert cls.course2_student_participation

        cls.course2_ta_participation = Participation.objects.filter(
            course=cls.course2,
            roles__identifier="ta",
            status=participation_status.active
        ).first()
        assert cls.course2_ta_participation
        cls.course2_page_url = cls.get_course_page_url(cls.course2.identifier)

        cls.c.logout()

    def setUp(self):  # noqa
        super(TwoCourseTestMixin, self).setUp()
        # reload objects created during setUpTestData in case they were modified in
        # tests. Ref: https://goo.gl/AuzJRC#django.test.TestCase.setUpTestData
        self.course1.refresh_from_db()
        self.course1_instructor_participation.refresh_from_db()
        self.course1_student_participation.refresh_from_db()
        self.course1_ta_participation.refresh_from_db()

        self.course2.refresh_from_db()
        self.course2_instructor_participation.refresh_from_db()
        self.course2_student_participation.refresh_from_db()
        self.course2_ta_participation.refresh_from_db()


class SingleCoursePageTestMixin(SingleCourseTestMixin):
    # This serves as cache
    _default_session_id = None

    @property
    def flow_id(self):
        raise NotImplementedError

    @classmethod
    def update_default_flow_session_id(cls, course_identifier):
        cls._default_session_id = cls.default_flow_params["flow_session_id"]

    def get_default_flow_session_id(self, course_identifier):
        if self._default_session_id is not None:
            return self._default_session_id
        self._default_session_id = self.get_latest_session_id(course_identifier)
        return self._default_session_id


class TwoCoursePageTestMixin(TwoCourseTestMixin):
    _course1_default_session_id = None
    _course2_default_session_id = None

    @property
    def flow_id(self):
        raise NotImplementedError

    def get_default_flow_session_id(self, course_identifier):
        if course_identifier == self.course1.identifier:
            if self._course1_default_session_id is not None:
                return self._course1_default_session_id
            self._course1_default_session_id = (
                self.get_last_session_id(course_identifier))
            return self._course1_default_session_id
        if course_identifier == self.course2.identifier:
            if self._course2_default_session_id is not None:
                return self._course2_default_session_id
            self._course2_default_session_id = (
                self.get_last_session_id(course_identifier))
            return self._course2_default_session_id

    @classmethod
    def update_default_flow_session_id(cls, course_identifier):
        new_session_id = cls.default_flow_params["flow_session_id"]
        if course_identifier == cls.course1.identifier:
            cls._course1_default_session_id = new_session_id
        elif course_identifier == cls.course2.identifier:
            cls._course2_default_session_id = new_session_id


class FallBackStorageMessageTestMixin(object):
    # In case other message storage are used, the following is the default
    # storage used by django and RELATE. Tests which concerns the message
    # should not include this mixin.
    storage = 'django.contrib.messages.storage.fallback.FallbackStorage'

    def setUp(self):  # noqa
        super(FallBackStorageMessageTestMixin, self).setUp()
        self.settings_override = override_settings(MESSAGE_STORAGE=self.storage)
        self.settings_override.enable()

    def tearDown(self):  # noqa
        self.settings_override.disable()

    def get_listed_storage_from_response(self, response):
        return list(self.get_response_context_value_by_name(response, 'messages'))

    def clear_message_response_storage(self, response):
        # this should only be used for debug, because we are using private method
        # which might change
        try:
            storage = self.get_response_context_value_by_name(response, 'messages')
        except AssertionError:
            # message doesn't exist in response context
            return
        if hasattr(storage, '_loaded_data'):
            storage._loaded_data = []
        elif hasattr(storage, '_loaded_message'):
            storage._loaded_messages = []

        if hasattr(storage, '_queued_messages'):
            storage._queued_messages = []

        self.assertEqual(len(storage), 0)

    def assertResponseMessagesCount(self, response, expected_count):  # noqa
        storage = self.get_listed_storage_from_response(response)
        self.assertEqual(len(storage), expected_count)

    def assertResponseMessagesEqual(self, response, expected_messages):  # noqa
        storage = self.get_listed_storage_from_response(response)
        if not isinstance(expected_messages, list):
            expected_messages = [expected_messages]
        self.assertEqual(len([m for m in storage]), len(expected_messages))
        self.assertEqual([m.message for m in storage], expected_messages)

    def assertResponseMessagesEqualRegex(self, response, expected_message_regexs):  # noqa
        storage = self.get_listed_storage_from_response(response)
        if not isinstance(expected_message_regexs, list):
            expected_message_regexs = [expected_message_regexs]
        self.assertEqual(len([m for m in storage]), len(expected_message_regexs))
        messages = [m.message for m in storage]
        for idx, m in enumerate(messages):
            six.assertRegex(self, m, expected_message_regexs[idx])

    def assertResponseMessagesContains(self, response, expected_messages):  # noqa
        storage = self.get_listed_storage_from_response(response)
        if isinstance(expected_messages, str):
            expected_messages = [expected_messages]
        messages = [m.message for m in storage]
        for em in expected_messages:
            self.assertIn(em, messages)

    def assertResponseMessageLevelsEqual(self, response, expected_levels):  # noqa
        storage = self.get_listed_storage_from_response(response)
        self.assertEqual([m.level for m in storage], expected_levels)

    def debug_print_response_messages(self, response):
        """
        For debugging :class:`django.contrib.messages` objects in post response
        :param response: response
        """
        try:
            storage = self.get_listed_storage_from_response(response)
            print("\n-----------message start (%i total)-------------"
                  % len(storage))
            for m in storage:
                print(m.message)
            print("-----------message end-------------\n")
        except KeyError:
            print("\n-------no message----------")


class SubprocessRunpyContainerMixin(object):
    """
    This mixin is used to fake a runpy container, only needed when
    the TestCase include test(s) for code questions
    """
    @classmethod
    def setUpClass(cls):  # noqa
        if six.PY2:
            from unittest import SkipTest
            raise SkipTest("In process fake container is configured for "
                           "PY3 only, since currently runpy docker only "
                           "provide PY3 envrionment")

        super(SubprocessRunpyContainerMixin, cls).setUpClass()
        cls.faked_container_patch = mock.patch(
            "course.page.code.SPAWN_CONTAINERS_FOR_RUNPY", False)
        cls.faked_container_patch.start()

        python_executable = os.getenv("PY_EXE")

        if not python_executable:
            import sys
            python_executable = sys.executable

        import subprocess
        args = [python_executable,
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__), os.pardir,
                        "docker-image-run-py", "runpy")),
                ]
        cls.faked_container_process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,

            # because runpy prints to stderr
            stderr=subprocess.DEVNULL
        )

        cls.faked_container_patch.start()

    @classmethod
    def tearDownClass(cls):  # noqa
        super(SubprocessRunpyContainerMixin, cls).tearDownClass()
        cls.faked_container_patch.stop()
        cls.faked_container_process.kill()


def improperly_configured_cache_patch():
    # can be used as context manager or decorator
    if six.PY3:
        built_in_import_path = "builtins.__import__"
        import builtins  # noqa
    else:
        built_in_import_path = "__builtin__.__import__"
        import __builtin__ as builtins  # noqa
    built_in_import = builtins.__import__

    def my_disable_cache_import(name, globals=None, locals=None, fromlist=(),
                                level=0):
        if name == "django.core.cache":
            raise ImproperlyConfigured()
        return built_in_import(name, globals, locals, fromlist, level)

    return mock.patch(built_in_import_path, side_effect=my_disable_cache_import)

# vim: fdm=marker
