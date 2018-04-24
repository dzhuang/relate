from __future__ import division

__copyright__ = "Copyright (C) 2018 Dong Zhuang"

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

import pytz
import json
import datetime

from django.test import TestCase
from django.utils.timezone import now, timedelta

from relate.utils import as_local_time

from course.models import Event

from tests.base_test_mixins import (
    SingleCourseTestMixin, MockAddMessageMixing, HackRepoMixin)
from tests.utils import mock
from tests import factories
from tests.constants import DATE_TIME_PICKER_TIME_FORMAT


class CreateRecurringEventsTest(SingleCourseTestMixin,
                                MockAddMessageMixing, TestCase):
    """test course.calendar.create_recurring_events"""
    default_event_kind = "lecture"

    def get_create_recurring_events_url(self, course_identifier=None):
        course_identifier = course_identifier or self.get_default_course_identifier()
        return self.get_course_view_url(
            "relate-create_recurring_events", course_identifier)

    def get_create_recurring_events_view(self, course_identifier=None,
                                         force_login_instructor=True):
        course_identifier = course_identifier or self.get_default_course_identifier()
        if not force_login_instructor:
            user = self.get_logged_in_user()
        else:
            user = self.instructor_participation.user

        with self.temporarily_switch_to_user(user):
            return self.c.get(
                self.get_create_recurring_events_url(course_identifier))

    def post_create_recurring_events_view(self, data, course_identifier=None,
                                          force_login_instructor=True):
        course_identifier = course_identifier or self.get_default_course_identifier()
        if not force_login_instructor:
            user = self.get_logged_in_user()
        else:
            user = self.instructor_participation.user

        with self.temporarily_switch_to_user(user):
            return self.c.post(
                self.get_create_recurring_events_url(course_identifier), data)

    def get_post_create_recur_evt_data(
            self, op="submit", starting_ordinal=None, **kwargs):
        data = {
            "kind": self.default_event_kind,
            "time": now().replace(tzinfo=None).strftime(
                DATE_TIME_PICKER_TIME_FORMAT),
            "interval": "weekly",
            "count": 5,
            op: ''
        }

        if starting_ordinal:
            data["starting_ordinal"] = starting_ordinal

        data.update(kwargs)
        return data

    def test_not_authenticated(self):
        with self.temporarily_switch_to_user(None):
            resp = self.get_create_recurring_events_view(
                force_login_instructor=False)
            self.assertEqual(resp.status_code, 302)

            resp = self.post_create_recurring_events_view(
                data={}, force_login_instructor=False)
            self.assertEqual(resp.status_code, 302)

    def test_no_pperm(self):
        with self.temporarily_switch_to_user(self.student_participation.user):
            resp = self.get_create_recurring_events_view(
                force_login_instructor=False)
            self.assertEqual(resp.status_code, 403)

            resp = self.post_create_recurring_events_view(
                data={}, force_login_instructor=False)
            self.assertEqual(resp.status_code, 403)

    def test_get_success(self):
        resp = self.get_create_recurring_events_view()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)

    def test_post_form_not_valid(self):
        with mock.patch(
                "course.calendar.RecurringEventForm.is_valid"
        ) as mock_form_valid:
            mock_form_valid.return_value = False
            resp = self.post_create_recurring_events_view(
                data=self.get_post_create_recur_evt_data())
            self.assertEqual(resp.status_code, 200)

    def test_post_success_starting_ordinal_specified(self):
        resp = self.post_create_recurring_events_view(
            data=self.get_post_create_recur_evt_data(starting_ordinal=4))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Event.objects.count(), 5)
        self.assertListEqual(
            list(Event.objects.values_list("ordinal", flat=True)),
            [4, 5, 6, 7, 8])

        t = None
        for evt in Event.objects.all():
            if t is None:
                t = evt.time
                continue
            else:
                self.assertEqual(evt.time - t, datetime.timedelta(weeks=1))
                t = evt.time

    def test_post_success_starting_ordinal_not_specified(self):
        resp = self.post_create_recurring_events_view(
            data=self.get_post_create_recur_evt_data())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Event.objects.count(), 5)
        self.assertListEqual(
            list(Event.objects.values_list("ordinal", flat=True)),
            [1, 2, 3, 4, 5])

    def test_post_event_already_exists_starting_ordinal_specified(self):
        factories.EventFactory(
            course=self.course, kind=self.default_event_kind, ordinal=7)
        resp = self.post_create_recurring_events_view(
            data=self.get_post_create_recur_evt_data(starting_ordinal=4))
        self.assertEqual(resp.status_code, 200)

        # not created
        self.assertEqual(Event.objects.count(), 1)

        self.assertAddMessageCallCount(1)
        self.assertAddMessageCalledWith(
            "EventAlreadyExists: 'lecture 7' already exists. "
            "No events created.")

    def test_post_event_already_exists_starting_ordinal_not_specified(self):
        factories.EventFactory(
            course=self.course, kind=self.default_event_kind, ordinal=4)
        resp = self.post_create_recurring_events_view(
            data=self.get_post_create_recur_evt_data())
        self.assertEqual(resp.status_code, 200)

        # created and ordinal is not None
        self.assertEqual(
            Event.objects.filter(
                kind=self.default_event_kind, ordinal__isnull=False).count(), 6)

        self.assertAddMessageCallCount(1)
        self.assertAddMessageCalledWith("Events created.")

    def test_unknown_error(self):
        error_msg = "my unknown error"
        with mock.patch(
                "course.calendar._create_recurring_events_backend"
        ) as mock_create_evt_backend:
            mock_create_evt_backend.side_effect = RuntimeError(error_msg)
            resp = self.post_create_recurring_events_view(
                data=self.get_post_create_recur_evt_data(starting_ordinal=4))
            self.assertEqual(resp.status_code, 200)

        # not created
        self.assertEqual(Event.objects.count(), 0)
        self.assertAddMessageCallCount(1)
        self.assertAddMessageCalledWith(
            "RuntimeError: %s. No events created." % error_msg)

    def test_duration_in_minutes(self):
        resp = self.post_create_recurring_events_view(
            data=self.get_post_create_recur_evt_data(
                starting_ordinal=4, duration_in_minutes=20))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Event.objects.count(), 5)
        self.assertListEqual(
            list(Event.objects.values_list("ordinal", flat=True)),
            [4, 5, 6, 7, 8])

        t = None
        for evt in Event.objects.all():
            self.assertEqual(evt.end_time - evt.time, timedelta(minutes=20))
            if t is None:
                t = evt.time
                continue
            else:
                self.assertEqual(evt.time - t, datetime.timedelta(weeks=1))
                t = evt.time

    def test_interval_biweekly(self):
        resp = self.post_create_recurring_events_view(
            data=self.get_post_create_recur_evt_data(
                starting_ordinal=4, interval="biweekly"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Event.objects.count(), 5)
        self.assertListEqual(
            list(Event.objects.values_list("ordinal", flat=True)),
            [4, 5, 6, 7, 8])

        t = None
        for evt in Event.objects.all():
            if t is None:
                t = evt.time
                continue
            else:
                self.assertEqual(evt.time - t, datetime.timedelta(weeks=2))
                t = evt.time


class RenumberEventsTest(SingleCourseTestMixin,
                         MockAddMessageMixing, TestCase):
    """test course.calendar.create_recurring_events"""
    default_event_kind = "lecture"

    def get_renumber_events_events_url(self, course_identifier=None):
        course_identifier = course_identifier or self.get_default_course_identifier()
        return self.get_course_view_url(
            "relate-renumber_events", course_identifier)

    def get_renumber_events_view(self, course_identifier=None,
                                 force_login_instructor=True):
        course_identifier = course_identifier or self.get_default_course_identifier()
        if not force_login_instructor:
            user = self.get_logged_in_user()
        else:
            user = self.instructor_participation.user

        with self.temporarily_switch_to_user(user):
            return self.c.get(
                self.get_renumber_events_events_url(course_identifier))

    def post_renumber_events_view(self, data, course_identifier=None,
                                  force_login_instructor=True):
        course_identifier = course_identifier or self.get_default_course_identifier()
        if not force_login_instructor:
            user = self.get_logged_in_user()
        else:
            user = self.instructor_participation.user

        with self.temporarily_switch_to_user(user):
            return self.c.post(
                self.get_renumber_events_events_url(course_identifier), data)

    def get_post_renumber_evt_data(
            self, starting_ordinal, kind=None, op="submit", **kwargs):

        data = {
            "kind": kind or self.default_event_kind,
            "starting_ordinal": starting_ordinal}

        if starting_ordinal:
            data["starting_ordinal"] = starting_ordinal

        data.update(kwargs)
        return data

    @classmethod
    def setUpTestData(cls):  # noqa
        super(RenumberEventsTest, cls).setUpTestData()
        times = []
        now_time = now()
        for i in range(5):
            times.append(now_time)
            now_time += timedelta(weeks=1)
            factories.EventFactory(
                kind=cls.default_event_kind, ordinal=i * 2 + 1, time=now_time)

        cls.evt1, cls.evt2, cls.evt3, cls.evt4, cls.evt5 = Event.objects.all()

        for i in range(2):
            factories.EventFactory(
                kind="another_kind", ordinal=i * 3 + 1, time=now_time)
            now_time += timedelta(weeks=1)

        cls.evt_another_kind1, cls.evt_another_kind2 = (
            Event.objects.filter(kind="another_kind"))
        cls.evt_another_kind1_ordinal = cls.evt_another_kind1.ordinal
        cls.evt_another_kind2_ordinal = cls.evt_another_kind2.ordinal

    def setUp(self):
        super(RenumberEventsTest, self).setUp()
        self.evt1.refresh_from_db()
        self.evt2.refresh_from_db()
        self.evt3.refresh_from_db()
        self.evt4.refresh_from_db()
        self.evt5.refresh_from_db()

    def test_not_authenticated(self):
        with self.temporarily_switch_to_user(None):
            resp = self.get_renumber_events_view(
                force_login_instructor=False)
            self.assertEqual(resp.status_code, 302)

            resp = self.post_renumber_events_view(data={},
                                                  force_login_instructor=False)
            self.assertEqual(resp.status_code, 302)

    def test_no_pperm(self):
        with self.temporarily_switch_to_user(self.student_participation.user):
            resp = self.get_renumber_events_view(
                force_login_instructor=False)
            self.assertEqual(resp.status_code, 403)

            resp = self.post_renumber_events_view(data={},
                                                  force_login_instructor=False)
            self.assertEqual(resp.status_code, 403)

    def test_get_success(self):
        resp = self.get_renumber_events_view()
        self.assertEqual(resp.status_code, 200)

    def test_post_form_not_valid(self):
        with mock.patch(
                "course.calendar.RenumberEventsForm.is_valid"
        ) as mock_form_valid:
            mock_form_valid.return_value = False

            resp = self.post_renumber_events_view(
                data=self.get_post_renumber_evt_data(starting_ordinal=3))
            self.assertEqual(resp.status_code, 200)

        all_default_evts = Event.objects.filter(kind=self.default_event_kind)
        self.assertEqual(all_default_evts.count(), 5)
        self.assertListEqual(
            list(all_default_evts.values_list("ordinal", flat=True)),
            [1, 3, 5, 7, 9])

        t = None
        for evt in all_default_evts:
            if t is None:
                t = evt.time
                continue
            else:
                self.assertEqual(evt.time - t, datetime.timedelta(weeks=1))
                t = evt.time

        # other events also not affected
        self.evt_another_kind1.refresh_from_db()
        self.evt_another_kind2.refresh_from_db()
        self.assertEqual(
            self.evt_another_kind1.ordinal, self.evt_another_kind1_ordinal)
        self.assertEqual(
            self.evt_another_kind2.ordinal, self.evt_another_kind2_ordinal)

    def test_post_success(self):
        resp = self.post_renumber_events_view(
            data=self.get_post_renumber_evt_data(starting_ordinal=3))
        self.assertEqual(resp.status_code, 200)
        all_pks = list(Event.objects.values_list("pk", flat=True))

        # originally 1, 3, 5, 7, 9, now 3, 4, 5, 6, 7

        all_default_evts = Event.objects.filter(kind=self.default_event_kind)
        self.assertEqual(all_default_evts.count(), 5)
        self.assertListEqual(
            list(all_default_evts.values_list("ordinal", flat=True)),
            [3, 4, 5, 6, 7])

        t = None
        for evt in all_default_evts:
            if t is None:
                t = evt.time
                continue
            else:
                self.assertEqual(evt.time - t, datetime.timedelta(weeks=1))
                t = evt.time

        # other events not affected
        self.evt_another_kind1.refresh_from_db()
        self.evt_another_kind2.refresh_from_db()
        self.assertEqual(
            self.evt_another_kind1.ordinal, self.evt_another_kind1_ordinal)
        self.assertEqual(
            self.evt_another_kind2.ordinal, self.evt_another_kind2_ordinal)

        # no new objects created
        self.assertListEqual(
            list(Event.objects.values_list("pk", flat=True)), all_pks)

        self.assertAddMessageCallCount(1)
        self.assertAddMessageCalledWith("Events renumbered.")

    def test_renumber_non_existing_events(self):
        all_pks = list(Event.objects.values_list("pk", flat=True))

        resp = self.post_renumber_events_view(
            data=self.get_post_renumber_evt_data(
                kind="foo_kind", starting_ordinal=3))
        self.assertEqual(resp.status_code, 200)

        # nothing changed
        all_default_evts = Event.objects.filter(kind=self.default_event_kind)
        self.assertListEqual(
            list(all_default_evts.values_list("ordinal", flat=True)),
            [1, 3, 5, 7, 9])

        # no new objects created
        self.assertListEqual(
            list(Event.objects.values_list("pk", flat=True)), all_pks)

        # other events also not affected
        self.evt_another_kind1.refresh_from_db()
        self.evt_another_kind2.refresh_from_db()
        self.assertEqual(
            self.evt_another_kind1.ordinal, self.evt_another_kind1_ordinal)
        self.assertEqual(
            self.evt_another_kind2.ordinal, self.evt_another_kind2_ordinal)

        self.assertAddMessageCallCount(1)
        self.assertAddMessageCalledWith("No events found.")


class ViewCalendarTest(SingleCourseTestMixin, HackRepoMixin, TestCase):
    """test course.calendar.view_calendar"""

    default_faked_now = datetime.datetime(2019, 1, 1, tzinfo=pytz.UTC)
    default_event_time = default_faked_now - timedelta(hours=12)
    default_event_kind = "lecture"

    def setUp(self):
        super(ViewCalendarTest, self).setUp()
        fake_get_now_or_fake_time = mock.patch(
            "course.views.get_now_or_fake_time")
        self.mock_get_now_or_fake_time = fake_get_now_or_fake_time.start()
        self.mock_get_now_or_fake_time.return_value = now()
        self.addCleanup(fake_get_now_or_fake_time.stop)

        self.addCleanup(factories.EventFactory.reset_sequence)

    def get_course_calender_view(self, course_identifier=None):
        course_identifier = course_identifier or self.get_default_course_identifier()
        return self.c.get(self.get_course_calender_url(course_identifier))

    def switch_to_fake_commit_sha(self):
        self.course.active_git_commit_sha = "my_fake_commit_sha_for_events"
        self.course.events_file = "events.yml"
        self.course.save()

    def test_no_pperm(self):
        with mock.patch(
                "course.utils.CoursePageContext.has_permission"
        ) as mock_has_pperm:
            mock_has_pperm.return_value = False
            resp = self.get_course_calender_view()
            self.assertEqual(resp.status_code, 403)

    def test_neither_events_nor_event_file(self):
        self.mock_get_now_or_fake_time.return_value = self.default_faked_now
        resp = self.get_course_calender_view()
        self.assertEqual(resp.status_code, 200)
        self.assertResponseContextEqual(resp, "events_json", '[]')
        self.assertResponseContextEqual(resp, "event_info_list", [])
        self.assertResponseContextEqual(
            resp, "default_date", self.default_faked_now.date().isoformat())

    def test_no_event_file(self):
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=self.default_event_time)
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=self.default_event_time + timedelta(hours=1))

        resp = self.get_course_calender_view()
        self.assertEqual(resp.status_code, 200)

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 2)
        self.assertDictEqual(
            events_json[0],
            {'id': 1, 'start': self.default_event_time.isoformat(),
             'allDay': False,
             'title': 'lecture 0'})
        self.assertDictEqual(
            events_json[1],
            {'id': 2,
             'start': (self.default_event_time + timedelta(hours=1)).isoformat(),
             'allDay': False,
             'title': 'lecture 1'})

        self.assertResponseContextEqual(resp, "event_info_list", [])

    def test_hidden_event_not_shown(self):
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=self.default_event_time)
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            shown_in_calendar=False,
            time=self.default_event_time + timedelta(hours=1))

        resp = self.get_course_calender_view()
        self.assertEqual(resp.status_code, 200)

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 1)
        self.assertDictEqual(
            events_json[0],
            {'id': 1, 'start': self.default_event_time.isoformat(),
             'allDay': False,
             'title': 'lecture 0'})
        self.assertResponseContextEqual(resp, "event_info_list", [])

    def test_event_has_end_time(self):
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=self.default_event_time,
            end_time=self.default_event_time + timedelta(hours=1))
        resp = self.get_course_calender_view()
        self.assertEqual(resp.status_code, 200)

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 1)
        event_json = events_json[0]
        self.assertDictEqual(
            event_json,
            {'id': 1, 'start': self.default_event_time.isoformat(),
             'allDay': False,
             'title': 'lecture 0',
             'end': (self.default_event_time + timedelta(hours=1)).isoformat(),
             })

        self.assertResponseContextEqual(resp, "event_info_list", [])

    def test_event_course_finished(self):
        self.mock_get_now_or_fake_time.return_value = self.default_faked_now
        self.course.end_date = (self.default_faked_now - timedelta(weeks=1)).date()
        self.course.save()

        resp = self.get_course_calender_view()
        self.assertEqual(resp.status_code, 200)

        self.assertResponseContextEqual(resp, "events_json", '[]')
        self.assertResponseContextEqual(resp, "event_info_list", [])
        self.assertResponseContextEqual(
            resp, "default_date", self.course.end_date.isoformat())

    def test_event_course_not_finished(self):
        self.mock_get_now_or_fake_time.return_value = self.default_faked_now
        self.course.end_date = (self.default_faked_now + timedelta(weeks=1)).date()
        self.course.save()

        resp = self.get_course_calender_view()
        self.assertEqual(resp.status_code, 200)

        self.assertResponseContextEqual(resp, "events_json", '[]')
        self.assertResponseContextEqual(resp, "event_info_list", [])
        self.assertResponseContextEqual(
            resp, "default_date", self.default_faked_now.date().isoformat())

    def test_events_file_no_events(self):
        # make sure it works
        self.switch_to_fake_commit_sha()

        resp = self.get_course_calender_view()

        self.assertResponseContextEqual(resp, "events_json", '[]')
        self.assertResponseContextEqual(resp, "event_info_list", [])

    def test_events_file_with_events_test1(self):
        self.switch_to_fake_commit_sha()

        # lecture 1
        lecture1_start_time = self.default_event_time - timedelta(weeks=1)
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=lecture1_start_time, ordinal=1)

        # lecture 2
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=self.default_event_time, ordinal=2)

        resp = self.get_course_calender_view()

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 2)
        self.assertDictEqual(
            events_json[0],
            {'id': 2, 'start': self.default_event_time.isoformat(),
             'allDay': False,
             'title': 'Lecture 2'})

        self.assertDictEqual(
            events_json[1],
            {'id': 1,
             'color': "red",
             'start': lecture1_start_time.isoformat(),
             'allDay': False,
             'title': 'Alternative title for lecture 1',
             'url': '#event-1'
             })

        event_info_list = resp.context["event_info_list"]

        # lecture 2 doesn't create an EventInfo object
        self.assertEqual(len(event_info_list), 1)

        # check the attributes of EventInfo of lecture 1
        evt_info_dict = event_info_list[0].__dict__
        evt_description = evt_info_dict.pop("description")

        self.assertDictEqual(
            evt_info_dict,
            {"id": 1, "human_title": "Alternative title for lecture 1",
             "start_time": lecture1_start_time,
             "end_time": None})

        # make sure markup_to_html is called
        self.assertIn(
            'href="/course/test-course/flow/prequiz-linear-algebra/start/',
            evt_description)

    def test_events_file_with_events_test2(self):
        self.switch_to_fake_commit_sha()

        self.mock_get_now_or_fake_time.return_value = (
                self.default_event_time + timedelta(minutes=5))

        # lecture 2
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=self.default_event_time, ordinal=2)

        # lecture 3
        lecture3_start_time = self.default_event_time + timedelta(weeks=1)
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=lecture3_start_time, ordinal=3)

        # test event
        test_start_time = self.default_event_time + timedelta(minutes=1)
        factories.EventFactory(
            kind="test", course=self.course, all_day=True,
            time=test_start_time,
            ordinal=None)

        resp = self.get_course_calender_view()

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 3)

        self.assertDictEqual(
            events_json[0],
            {'id': 2, 'start': (lecture3_start_time).isoformat(),
             'allDay': False,
             'title': 'Lecture 3'})

        self.assertDictEqual(
            events_json[1],
            {'id': 1, 'start': self.default_event_time.isoformat(),
             'allDay': False,
             'title': 'Lecture 2',
             'url': '#event-1'})

        self.assertDictEqual(
            events_json[2],
            {'id': 3, 'start': test_start_time.isoformat(),
             'allDay': True,
             'title': 'test'})

        event_info_list = resp.context["event_info_list"]

        # only lecture 2 create an EventInfo object
        self.assertEqual(len(event_info_list), 1)

        # check the attributes of EventInfo of lecture 1
        evt_info_dict = event_info_list[0].__dict__
        evt_description = evt_info_dict.pop("description")

        self.assertDictEqual(
            evt_info_dict,
            {"id": 1, "human_title": "Lecture 2",
             "start_time": self.default_event_time,
             "end_time": None})

        self.assertIn(
            'Can you see this?',
            evt_description)

        # lecture 2's description exceeded show_description_until
        self.mock_get_now_or_fake_time.return_value = (
                lecture3_start_time + timedelta(minutes=5))

        # no EventInfo object
        resp = self.get_course_calender_view()
        self.assertResponseContextEqual(resp, "event_info_list", [])

    def test_events_file_with_events_test3(self):
        self.switch_to_fake_commit_sha()

        exam_end_time = self.default_event_time + timedelta(hours=2)
        factories.EventFactory(
            kind="exam", course=self.course,
            ordinal=None,
            time=self.default_event_time,
            end_time=exam_end_time)

        resp = self.get_course_calender_view()

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 1)

        self.assertDictEqual(
            events_json[0],
            {'id': 1,
             'start': self.default_event_time.isoformat(),
             'allDay': False,
             'title': 'Exam',
             'color': 'red',
             'end': exam_end_time.isoformat()})

        self.assertResponseContextEqual(resp, "event_info_list", [])

    def test_all_day_event(self):
        self.switch_to_fake_commit_sha()

        # lecture 2, no end_time
        lecture2_start_time = datetime.datetime(2019, 1, 1, tzinfo=pytz.UTC)

        self.mock_get_now_or_fake_time.return_value = (
                lecture2_start_time + timedelta(minutes=5))

        lecture2_evt = factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            all_day=True,
            time=lecture2_start_time, ordinal=2)

        # lecture 3
        lecture3_start_time = lecture2_start_time + timedelta(weeks=1)
        factories.EventFactory(
            kind=self.default_event_kind, course=self.course,
            time=lecture3_start_time, ordinal=3)

        resp = self.get_course_calender_view()

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 2)

        self.assertDictEqual(
            events_json[1],
            {'id': 1, 'start': lecture2_start_time.isoformat(),
             'allDay': True,
             'title': 'Lecture 2',
             'url': '#event-1'})

        # now we add end_time of lecture 2 evt to a time which is not midnight
        lecture2_end_time = lecture2_start_time + timedelta(hours=18)
        lecture2_evt.end_time = lecture2_end_time
        lecture2_evt.save()

        resp = self.get_course_calender_view()

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 2)

        self.assertDictEqual(
            events_json[1],
            {'id': 1, 'start': lecture2_start_time.isoformat(),
             'allDay': True,
             'title': 'Lecture 2',
             'url': '#event-1',
             'end': lecture2_end_time.isoformat()
             })

        # now we update end_time of lecture 2 evt to midnight
        while True:
            local_t = as_local_time(lecture2_end_time)
            end_midnight = datetime.time(tzinfo=local_t.tzinfo)
            if local_t.time() == end_midnight:
                lecture2_evt.end_time = lecture2_end_time
                lecture2_evt.save()
                break

            lecture2_end_time += timedelta(hours=1)

        resp = self.get_course_calender_view()

        events_json = json.loads(resp.context["events_json"])
        self.assertEqual(len(events_json), 2)

        self.assertDictEqual(
            events_json[1],
            {'id': 1, 'start': lecture2_start_time.isoformat(),
             'allDay': True,
             'title': 'Lecture 2',
             'url': '#event-1',
             'end': lecture2_end_time.isoformat()
             })

# vim: fdm=marker
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

import json
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from django.utils.timezone import now

from course.models import Event
from tests.base_test_mixins import (
    SingleCourseTestMixin, FallBackStorageMessageTestMixin)
from tests.utils import mock

DATE_TIME_PICKER_TIME_FORMAT = "%Y-%m-%d %H:%M"

SHOWN_EVENT_KIND = "test_open_event"
HIDDEN_EVENT_KIND = "test_secret_event"
OPEN_EVENT_NO_ORDINAL_KIND = "test_open_no_ordinal"
HIDDEN_EVENT_NO_ORDINAL_KIND = "test_secret_no_ordinal"
FAILURE_EVENT_KIND = "never_created_event_kind"

TEST_EVENTS = (
    {"kind": SHOWN_EVENT_KIND, "ordinal": "1",
        "shown_in_calendar": True, "time": now()},
    {"kind": SHOWN_EVENT_KIND, "ordinal": "2",
        "shown_in_calendar": True, "time": now()},
    {"kind": SHOWN_EVENT_KIND, "ordinal": "3",
     "shown_in_calendar": True, "time": now()},
    {"kind": HIDDEN_EVENT_KIND, "ordinal": "1",
        "shown_in_calendar": False, "time": now()},
    {"kind": HIDDEN_EVENT_KIND, "ordinal": "2",
        "shown_in_calendar": False, "time": now()},
    {"kind": OPEN_EVENT_NO_ORDINAL_KIND,
        "shown_in_calendar": True, "time": now()},
    {"kind": HIDDEN_EVENT_NO_ORDINAL_KIND,
        "shown_in_calendar": False, "time": now()},
)

TEST_NOT_EXIST_EVENT = {
    "pk": 1000,
    "kind": "DOES_NOT_EXIST_KIND", "ordinal": "1",
    "shown_in_calendar": True, "time": now()}

N_TEST_EVENTS = len(TEST_EVENTS)  # 7 events
N_HIDDEN_EVENTS = len([event
                       for event in TEST_EVENTS
                       if not event["shown_in_calendar"]])  # 3 events
N_SHOWN_EVENTS = N_TEST_EVENTS - N_HIDDEN_EVENTS  # 4 events

# html literals (from template)
MENU_EDIT_EVENTS_ADMIN = "Edit events (admin)"
MENU_VIEW_EVENTS_CALENDAR = "Edit events (calendar)"
MENU_CREATE_RECURRING_EVENTS = "Create recurring events"
MENU_RENUMBER_EVENTS = "Renumber events"

HTML_SWITCH_TO_STUDENT_VIEW = "Switch to Student View"
HTML_SWITCH_TO_EDIT_VIEW = "Switch to Edit View"
HTML_CREATE_NEW_EVENT_BUTTON_TITLE = "create a new event"

MESSAGE_EVENT_CREATED_TEXT = "Event created."
MESSAGE_EVENT_NOT_CREATED_TEXT = "No event created."
MESSAGE_PREFIX_EVENT_ALREADY_EXIST_FAILURE_TEXT = "EventAlreadyExists:"
MESSAGE_PREFIX_EVENT_NOT_DELETED_FAILURE_TEXT = "No event deleted:"
MESSAGE_EVENT_DELETED_TEXT = "Event deleted."
MESSAGE_EVENT_UPDATED_TEXT = "Event updated."
MESSAGE_EVENT_NOT_UPDATED_TEXT = "Event not updated."


def get_object_or_404_side_effect(klass, *args, **kwargs):
    """
    Delete an existing object from db after get
    """
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(klass, *args, **kwargs)
    obj.delete()
    return obj


class CalendarTestMixin(object):
    @classmethod
    def setUpTestData(cls):  # noqa
        super(CalendarTestMixin, cls).setUpTestData()

        # superuser was previously removed from participation, now we add him back
        from course.constants import participation_status

        cls.create_participation(
            cls.course,
            cls.superuser,
            role_identifier="instructor",
            status=participation_status.active)

        for event in TEST_EVENTS:
            event.update({
                "course": cls.course,
            })
            Event.objects.create(**event)
        assert Event.objects.count() == N_TEST_EVENTS

    def set_course_end_date(self):
        from datetime import timedelta
        self.course.end_date = now() + timedelta(days=120)
        self.course.save()

    def assertShownEventsCountEqual(self, resp, expected_shown_events_count):  # noqa
        self.assertEqual(
            len(json.loads(resp.context["events_json"])),
            expected_shown_events_count)

    def assertTotalEventsCountEqual(self, expected_total_events_count):  # noqa
        self.assertEqual(Event.objects.count(), expected_total_events_count)


class CalendarTest(CalendarTestMixin, SingleCourseTestMixin,
                   FallBackStorageMessageTestMixin, TestCase):

    def test_superuser_instructor_calendar_get(self):
        self.c.force_login(self.superuser)
        resp = self.c.get(
            reverse("relate-view_calendar", args=[self.course.identifier]))
        self.assertEqual(resp.status_code, 200)

        # menu items
        self.assertContains(resp, MENU_EDIT_EVENTS_ADMIN)
        self.assertContains(resp, MENU_VIEW_EVENTS_CALENDAR)
        self.assertContains(resp, MENU_CREATE_RECURRING_EVENTS)
        self.assertContains(resp, MENU_RENUMBER_EVENTS)

        # rendered page html
        self.assertNotContains(resp, HTML_SWITCH_TO_STUDENT_VIEW)
        self.assertContains(resp, HTML_SWITCH_TO_EDIT_VIEW)
        self.assertNotContains(resp, HTML_CREATE_NEW_EVENT_BUTTON_TITLE)

        # see only shown events
        self.assertShownEventsCountEqual(resp, N_SHOWN_EVENTS)

    def test_non_superuser_instructor_calendar_get(self):
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(
            reverse("relate-view_calendar", args=[self.course.identifier]))
        self.assertEqual(resp.status_code, 200)

        # menu items
        self.assertNotContains(resp, MENU_EDIT_EVENTS_ADMIN)
        self.assertContains(resp, MENU_VIEW_EVENTS_CALENDAR)
        self.assertContains(resp, MENU_CREATE_RECURRING_EVENTS)
        self.assertContains(resp, MENU_RENUMBER_EVENTS)

        # rendered page html
        self.assertNotContains(resp, HTML_SWITCH_TO_STUDENT_VIEW)
        self.assertContains(resp, HTML_SWITCH_TO_EDIT_VIEW)
        self.assertNotContains(resp, HTML_CREATE_NEW_EVENT_BUTTON_TITLE)

        # see only shown events
        self.assertShownEventsCountEqual(resp, N_SHOWN_EVENTS)

    def test_student_calendar_get(self):
        self.c.force_login(self.student_participation.user)
        resp = self.c.get(
            reverse("relate-view_calendar", args=[self.course.identifier]))
        self.assertEqual(resp.status_code, 200)

        # menu items
        self.assertNotContains(resp, MENU_EDIT_EVENTS_ADMIN)
        self.assertNotContains(resp, MENU_VIEW_EVENTS_CALENDAR)
        self.assertNotContains(resp, MENU_CREATE_RECURRING_EVENTS)
        self.assertNotContains(resp, MENU_RENUMBER_EVENTS)
        self.assertRegexpMatches

        # rendered page html
        self.assertNotContains(resp, HTML_SWITCH_TO_STUDENT_VIEW)
        self.assertNotContains(resp, HTML_SWITCH_TO_EDIT_VIEW)
        self.assertNotContains(resp, HTML_CREATE_NEW_EVENT_BUTTON_TITLE)

        # see only shown events
        self.assertShownEventsCountEqual(resp, N_SHOWN_EVENTS)

    def test_superuser_instructor_calendar_edit_get(self):
        self.c.force_login(self.superuser)
        resp = self.c.get(
            reverse("relate-edit_calendar", args=[self.course.identifier]))
        self.assertEqual(resp.status_code, 200)

        # menu items
        self.assertContains(resp, MENU_EDIT_EVENTS_ADMIN)
        self.assertContains(resp, MENU_VIEW_EVENTS_CALENDAR)
        self.assertContains(resp, MENU_CREATE_RECURRING_EVENTS)
        self.assertContains(resp, MENU_RENUMBER_EVENTS)

        # rendered page html
        self.assertNotContains(resp, HTML_SWITCH_TO_EDIT_VIEW)
        self.assertContains(resp, HTML_SWITCH_TO_STUDENT_VIEW)
        self.assertContains(resp, HTML_CREATE_NEW_EVENT_BUTTON_TITLE)

        # see all events (including hidden ones)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS)

    def test_non_superuser_instructor_calendar_edit_get(self):
        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(
            reverse("relate-edit_calendar", args=[self.course.identifier]))
        self.assertEqual(resp.status_code, 200)

        # menu items
        self.assertNotContains(resp, MENU_EDIT_EVENTS_ADMIN)
        self.assertContains(resp, MENU_VIEW_EVENTS_CALENDAR)
        self.assertContains(resp, MENU_CREATE_RECURRING_EVENTS)
        self.assertContains(resp, MENU_RENUMBER_EVENTS)

        # rendered page html
        self.assertNotContains(resp, HTML_SWITCH_TO_EDIT_VIEW)
        self.assertContains(resp, HTML_SWITCH_TO_STUDENT_VIEW)
        self.assertContains(resp, HTML_CREATE_NEW_EVENT_BUTTON_TITLE)

        # see all events (including hidden ones)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS)

    def test_student_calendar_edit_get(self):
        self.c.force_login(self.student_participation.user)
        resp = self.c.get(
            reverse("relate-edit_calendar", args=[self.course.identifier]))
        self.assertEqual(resp.status_code, 403)

    def test_instructor_calendar_edit_create_exist_failure(self):
        self.c.force_login(self.instructor_participation.user)
        # Failing to create event already exist
        post_data = {
            "kind": SHOWN_EVENT_KIND,
            "ordinal": "3",
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }

        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        expected_regex = (
            "%s.+%s" % (
                MESSAGE_PREFIX_EVENT_ALREADY_EXIST_FAILURE_TEXT,
                MESSAGE_EVENT_NOT_CREATED_TEXT))
        self.assertResponseMessagesEqualRegex(
            resp, [expected_regex])
        self.assertResponseMessageLevelsEqual(
            resp, [messages.ERROR])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS)

    def test_instructor_calendar_edit_create_exist_no_ordinal_event_faliure(self):
        self.c.force_login(self.instructor_participation.user)
        # Failing to create event (no ordinal) already exist
        post_data = {
            "kind": OPEN_EVENT_NO_ORDINAL_KIND,
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }

        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        expected_regex = (
            "%s.+%s" % (
                MESSAGE_PREFIX_EVENT_ALREADY_EXIST_FAILURE_TEXT,
                MESSAGE_EVENT_NOT_CREATED_TEXT))
        self.assertResponseMessagesEqualRegex(
            resp, [expected_regex])
        self.assertResponseMessageLevelsEqual(
            resp, [messages.ERROR])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS)

    def test_instructor_calendar_edit_post_create_success(self):
        # Successfully create new event
        self.c.force_login(self.instructor_participation.user)
        post_data = {
            "kind": SHOWN_EVENT_KIND,
            "ordinal": "4",
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_EVENT_CREATED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS + 1)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS + 1)

    def test_instructor_calendar_edit_post_create_for_course_has_end_date(self):
        # Successfully create new event
        self.set_course_end_date()
        self.c.force_login(self.instructor_participation.user)
        post_data = {
            "kind": SHOWN_EVENT_KIND,
            "ordinal": "4",
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_EVENT_CREATED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS + 1)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS + 1)

    def test_instructor_calendar_edit_delete_success(self):
        # Successfully remove an existing event
        self.c.force_login(self.instructor_participation.user)
        id_to_delete = Event.objects.filter(kind=SHOWN_EVENT_KIND).first().id
        post_data = {
            "id_to_delete": id_to_delete,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_EVENT_DELETED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS - 1)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS - 1)

    def test_instructor_calendar_edit_delete_for_course_has_end_date(self):
        # Successfully remove an existing event
        self.set_course_end_date()
        self.c.force_login(self.instructor_participation.user)
        id_to_delete = Event.objects.filter(kind=SHOWN_EVENT_KIND).first().id
        post_data = {
            "id_to_delete": id_to_delete,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_EVENT_DELETED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS - 1)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS - 1)

    def test_instructor_calendar_edit_delete_non_exist(self):
        # Successfully remove an existing event
        self.c.force_login(self.instructor_participation.user)
        post_data = {
            "id_to_delete": 1000,  # forgive me
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)

    @mock.patch("course.calendar.get_object_or_404",
                side_effect=get_object_or_404_side_effect)
    def test_instructor_calendar_edit_delete_deleted_event_before_transaction(
            self, mocked_get_object_or_404):
        # Deleting event which exist when get and was deleted before transaction
        self.c.force_login(self.instructor_participation.user)
        id_to_delete = Event.objects.filter(kind=SHOWN_EVENT_KIND).first().id
        post_data = {
            "id_to_delete": id_to_delete,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        expectec_regex = "%s.+" % MESSAGE_PREFIX_EVENT_NOT_DELETED_FAILURE_TEXT
        self.assertResponseMessagesEqualRegex(resp, expectec_regex)
        self.assertResponseMessageLevelsEqual(resp, [messages.ERROR])
        self.assertEqual(resp.status_code, 200)
        self.assertTotalEventsCountEqual(N_TEST_EVENTS - 1)

    def test_instructor_calendar_edit_update_success(self):
        # Successfully update an existing event
        self.c.force_login(self.instructor_participation.user)
        all_hidden_events = Event.objects.filter(kind=HIDDEN_EVENT_KIND)
        hidden_count_before_update = all_hidden_events.count()
        shown_count_before_update = (
            Event.objects.filter(kind=SHOWN_EVENT_KIND).count())
        event_to_edit = all_hidden_events.first()
        id_to_edit = event_to_edit.id
        post_data = {
            "existing_event_to_save": id_to_edit,
            "kind": SHOWN_EVENT_KIND,
            "ordinal": 10,
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_EVENT_UPDATED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS)
        self.assertEqual(
            Event.objects.filter(kind=HIDDEN_EVENT_KIND).count(),
            hidden_count_before_update - 1)
        self.assertEqual(
            Event.objects.filter(kind=SHOWN_EVENT_KIND).count(),
            shown_count_before_update + 1)

    def test_instructor_calendar_edit_update_no_ordinal_event_success(self):
        # Failure to update an existing event to overwrite and existing event
        self.c.force_login(self.instructor_participation.user)
        event_to_edit = Event.objects.filter(kind=HIDDEN_EVENT_KIND).first()
        id_to_edit = event_to_edit.id  # forgive me
        post_data = {
            "existing_event_to_save": id_to_edit,
            "kind": HIDDEN_EVENT_NO_ORDINAL_KIND,
            "ordinal": "",
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": False,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertResponseMessagesEqual(resp, [MESSAGE_EVENT_UPDATED_TEXT])
        self.assertResponseMessageLevelsEqual(resp, [messages.SUCCESS])
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)

    def test_instructor_calendar_edit_update_non_exist_id_to_edit_failure(self):
        self.c.force_login(self.instructor_participation.user)
        id_to_edit = 1000  # forgive me
        post_data = {
            "id_to_edit": id_to_edit,
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 404)

        post_data = {
            "existing_event_to_save": id_to_edit,
            "kind": SHOWN_EVENT_KIND,
            "ordinal": 1000,
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 404)

    def test_no_pperm_edit_event_post_create_fail(self):
        self.c.force_login(self.student_participation.user)
        post_data = {
            "kind": FAILURE_EVENT_KIND,
            "ordinal": "1",
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }

        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)
        self.assertEqual(Event.objects.filter(kind=FAILURE_EVENT_KIND).count(), 0)

    def test_no_pperm_edit_event_post_delete_fail(self):
        self.c.force_login(self.student_participation.user)
        id_to_delete = Event.objects.filter(kind=SHOWN_EVENT_KIND).first().id
        post_data = {
            "id_to_delete": id_to_delete,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)

    def test_no_pperm_edit_event_post_edit(self):
        self.c.force_login(self.student_participation.user)
        id_to_edit = 1
        self.assertIsNotNone(Event.objects.get(id=id_to_edit))
        post_data = {
            "id_to_edit": id_to_edit,
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 403)

        post_data = {
            "existing_event_to_save": id_to_edit,
            "kind": FAILURE_EVENT_KIND,
            "ordinal": 1000,
            "time": now().strftime(DATE_TIME_PICKER_TIME_FORMAT),
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Event.objects.filter(kind=FAILURE_EVENT_KIND).count(), 0)
