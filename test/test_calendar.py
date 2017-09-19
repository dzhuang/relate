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
from course.models import Event
from base_test_mixins import SingleCourseTestMixin
from django.utils.timezone import now

SHOWN_EVENT_KIND = "test_open_event"
HIDDEN_EVENT_KIND = "test_secret_event"
OPEN_EVENT_NO_ORDINAL = "test_open_no_ordinal"
HIDDEN_EVENT_NO_ORDINAL = "test_secret_no_ordinal"
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
    {"kind": OPEN_EVENT_NO_ORDINAL,
        "shown_in_calendar": True, "time": now()},
    {"kind": HIDDEN_EVENT_NO_ORDINAL,
        "shown_in_calendar": False, "time": now()},
)

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
HTML_EVENT_CREATED_MSG = "Event created."

MSG_EVENT_NOT_CREATED = "No event created."
MSG_PREFIX_EVENT_ALREAD_EXIST_FAILURE_MSG = "EventAlreadyExists:"
MSG_HTML_EVENT_DELETED = "Event deleted."
MSG_EVENT_UPDATED = "Event updated."
MSG_EVENT_NOT_UPDATED = "Event not updated."


class CalendarTest(SingleCourseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        super(CalendarTest, cls).setUpTestData()

        # superuser was previously removed from participation, now we add him back
        from course.constants import participation_status

        cls.create_participation(
            course=cls.course,
            create_user_kwargs={"id": cls.superuser.id},
            role_identifier="instructor",
            status=participation_status.active)

        for event in TEST_EVENTS:
            event.update({
                "course": cls.course,
            })
            Event.objects.create(**event)
        assert Event.objects.count() == N_TEST_EVENTS

    def assertShownEventsCountEqual(self, resp, expected_shown_events_count):  # noqa
        self.assertEqual(
            len(json.loads(resp.context["events_json"])),
            expected_shown_events_count)

    def assertTotalEventsCountEqual(self, expected_total_events_count):  # noqa
        self.assertEqual(Event.objects.count(), expected_total_events_count)

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
        # Failing to create events already exist
        post_data = {
            "kind": SHOWN_EVENT_KIND,
            "ordinal": "3",
            "time": "2017-09-14 17:14",  # forgive me
            "shown_in_calendar": True,
            'submit': ['']
        }

        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, MSG_PREFIX_EVENT_ALREAD_EXIST_FAILURE_MSG)
        self.assertContains(resp, MSG_EVENT_NOT_CREATED)
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS)

    def test_instructor_calendar_edit_post_create_success(self):
        # Successfully create new event
        self.c.force_login(self.instructor_participation.user)
        post_data = {
            "kind": SHOWN_EVENT_KIND,
            "ordinal": "4",
            "time": "2017-09-14 17:14",
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertMessageContains(resp, HTML_EVENT_CREATED_MSG)
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
        self.assertMessageContains(resp, MSG_HTML_EVENT_DELETED)
        self.assertMessageContains(resp, [MSG_HTML_EVENT_DELETED])
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
            "time": "2017-09-14 17:14",  # forgive me
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertMessageContains(resp, MSG_EVENT_UPDATED)
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)
        self.assertShownEventsCountEqual(resp, N_TEST_EVENTS)
        self.assertEqual(
            Event.objects.filter(kind=HIDDEN_EVENT_KIND).count(),
            hidden_count_before_update - 1)
        self.assertEqual(
            Event.objects.filter(kind=SHOWN_EVENT_KIND).count(),
            shown_count_before_update + 1)

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
            "time": "2017-09-14 17:14",  # forgive me
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 404)

    def test_instructor_calendar_edit_update_overwrite_exist_id_failure(self):
        # Failure to update an existing event to overwrite and existing event
        self.c.force_login(self.instructor_participation.user)
        event_to_edit = Event.objects.filter(kind=HIDDEN_EVENT_KIND).first()
        id_to_edit = event_to_edit.id  # forgive me
        post_data = {
            "existing_event_to_save": id_to_edit,
            "kind": HIDDEN_EVENT_NO_ORDINAL,
            "ordinal": "",
            "time": "2017-09-14 17:14",  # forgive me
            "shown_in_calendar": False,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, MSG_PREFIX_EVENT_ALREAD_EXIST_FAILURE_MSG)
        self.assertContains(resp, MSG_EVENT_NOT_UPDATED)
        self.assertTotalEventsCountEqual(N_TEST_EVENTS)

    def test_no_pperm_edit_event_post_create_fail(self):
        self.c.force_login(self.student_participation.user)
        post_data = {
            "kind": FAILURE_EVENT_KIND,
            "ordinal": "1",
            "time": "2017-09-14 17:14",  # forgive me
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
            "time": "2017-09-14 17:14",  # forgive me
            "shown_in_calendar": True,
            'submit': ['']
        }
        resp = self.c.post(
            reverse("relate-edit_calendar", args=[self.course.identifier]),
            post_data
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Event.objects.filter(kind=FAILURE_EVENT_KIND).count(), 0)