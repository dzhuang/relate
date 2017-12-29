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

from django.test import TestCase, RequestFactory, mock
from django.test.utils import override_settings
import datetime
from course import views

from .base_test_mixins import (
    SingleCourseTestMixin,
)

DATE_TIME_PICKER_TIME_FORMAT = "%Y-%m-%d %H:%M"

RELATE_FACILITIES = {
    # intentionally to be different from local_settings.example.py
    "test_center1": {
        "ip_ranges": [
            "192.168.100.0/24",
            ],
        "exams_only": False,
    },
}


class TestSetFakeTime(SingleCourseTestMixin, TestCase):
    fake_time = datetime.datetime(2038, 12, 31, 0, 0, 0, 0)
    set_fake_time_data = {"time": fake_time.strftime(DATE_TIME_PICKER_TIME_FORMAT),
                          "set": ['']}
    unset_fake_time_data = {"time": set_fake_time_data["time"], "unset": ['']}

    def test_set_fake_time_by_anonymous(self):
        with self.temporarily_switch_to_user(None):
            resp = self.get_set_fake_time()
            self.assertEqual(resp.status_code, 302)

            resp = self.post_set_fake_time(self.set_fake_time_data, follow=False)
            self.assertEqual(resp.status_code, 302)
            self.assertSessionFakeTimeIsNone(self.c.session)

    def test_set_fake_time_no_pperm(self):
        with self.temporarily_switch_to_user(self.student_participation.user):
            resp = self.get_set_fake_time()
            self.assertEqual(resp.status_code, 403)

            resp = self.post_set_fake_time(self.set_fake_time_data)
            self.assertEqual(resp.status_code, 403)
            self.assertSessionFakeTimeIsNone(self.c.session)

    def test_set_fake_time_by_instructor(self):
        with self.temporarily_switch_to_user(self.instructor_participation.user):
            resp = self.get_set_fake_time()
            self.assertEqual(resp.status_code, 200)

            # set fake time
            resp = self.post_set_fake_time(self.set_fake_time_data)
            self.assertEqual(resp.status_code, 200)
            self.assertSessionFakeTimeEqual(self.c.session, self.fake_time)

            # unset fake time
            resp = self.post_set_fake_time(self.unset_fake_time_data)
            self.assertEqual(resp.status_code, 200)
            self.assertSessionFakeTimeIsNone(self.c.session)


@override_settings(RELATE_FACILITIES=RELATE_FACILITIES)
class TestSetPretendFacilities(SingleCourseTestMixin, TestCase):
    set_pretend_facilities_data = {
        "facilities": ["test_center1"],
        "custom_facilities": [],
        "add_pretend_facilities_header": ["on"],
        "set": ['']}
    unset_pretend_facilities_data = set_pretend_facilities_data.copy()
    unset_pretend_facilities_data.pop("set")
    unset_pretend_facilities_data["unset"] = ['']

    def test_pretend_facilities_by_anonymous(self):
        with self.temporarily_switch_to_user(None):
            resp = self.get_set_pretend_facilities()
            self.assertEqual(resp.status_code, 302)

            resp = self.post_set_pretend_facilities(
                self.set_pretend_facilities_data, follow=False)
            self.assertEqual(resp.status_code, 302)
            self.assertSessionPretendFacilitiesIsNone(self.c.session)

    def test_pretend_facilities_no_pperm(self):
        with self.temporarily_switch_to_user(self.student_participation.user):
            resp = self.get_set_pretend_facilities()
            self.assertEqual(resp.status_code, 403)

            resp = self.post_set_pretend_facilities(
                self.set_pretend_facilities_data)
            self.assertEqual(resp.status_code, 403)
            self.assertSessionPretendFacilitiesIsNone(self.c.session)

    def test_pretend_facilities_by_instructor(self):
        with self.temporarily_switch_to_user(self.instructor_participation.user):
            resp = self.get_set_pretend_facilities()
            self.assertEqual(resp.status_code, 200)

            resp = self.post_set_pretend_facilities(
                self.set_pretend_facilities_data)
            self.assertEqual(resp.status_code, 200)
            self.assertSessionPretendFacilitiesContains(self.c.session,
                                                        "test_center1")

            resp = self.post_set_pretend_facilities(
                self.unset_pretend_facilities_data)
            self.assertEqual(resp.status_code, 200)
            self.assertSessionPretendFacilitiesIsNone(self.c.session)


class TestEditCourse(SingleCourseTestMixin, TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def copy_course_dict_and_set_lang_for_post(self, lang):
        from course.models import Course
        kwargs = Course.objects.first().__dict__
        kwargs["force_lang"] = lang

        import six
        for k, v in six.iteritems(kwargs):
            if v is None:
                kwargs[k] = ""
        return kwargs

    def test_non_auth_edit_get(self):
        with self.temporarily_switch_to_user(None):
            resp = self.get_edit_course()
        self.assertTrue(resp.status_code, 404)

    def test_non_auth_edit_post(self):
        with self.temporarily_switch_to_user(None):
            resp = self.post_edit_course(data={})
        self.assertTrue(resp.status_code, 404)

    def test_student_edit_get(self):
        with self.temporarily_switch_to_user(self.student_participation.user):
            resp = self.get_edit_course()
        self.assertTrue(resp.status_code, 404)

    def test_student_edit_post(self):
        with self.temporarily_switch_to_user(self.student_participation.user):
            resp = self.post_edit_course(data={})
        self.assertTrue(resp.status_code, 404)

    def test_instructor_edit_get(self):
        with self.temporarily_switch_to_user(self.instructor_participation.user):
            resp = self.get_edit_course()
        self.assertTrue(resp.status_code, 200)

    def test_instructor_edit_post_unchanged(self):
        with mock.patch('course.views.EditCourseForm.is_valid') as mock_is_valid, \
            mock.patch('course.views.EditCourseForm.has_changed') as mock_changed, \
            mock.patch('course.views.messages') as mock_messages,\
            mock.patch("course.views.render_course_page"),\
                mock.patch("course.views._") as mock_gettext:

            mock_is_valid.return_value = True
            mock_changed.return_value = False
            mock_gettext.side_effect = lambda x: x
            request = self.rf.post(self.get_edit_course_url(),
                                   data=mock.MagicMock())
            request.user = self.instructor_participation.user
            course_identifier = self.get_default_course_identifier()
            resp = views.edit_course(request, course_identifier)
            self.assertTrue(resp.status_code, 200)
            self.assertTrue(mock_messages.add_message.call_count, 1)
            self.assertIn("No change was made on the settings.",
                          mock_messages.add_message.call_args[0])

    def test_instructor_edit_post_saved(self):
        with mock.patch('course.views.EditCourseForm.is_valid') as mock_is_valid, \
            mock.patch('course.views.EditCourseForm.has_changed') as mock_changed, \
            mock.patch('course.views.EditCourseForm.save'), \
            mock.patch('course.views.messages') as mock_messages,\
            mock.patch("course.views.render_course_page"),\
                mock.patch("course.views._") as mock_gettext:

            mock_is_valid.return_value = True
            mock_changed.return_value = True
            mock_gettext.side_effect = lambda x: x
            request = self.rf.post(self.get_edit_course_url(),
                                   data=mock.MagicMock())
            request.user = self.instructor_participation.user
            course_identifier = self.get_default_course_identifier()
            resp = views.edit_course(request, course_identifier)
            self.assertTrue(resp.status_code, 200)
            self.assertTrue(mock_messages.add_message.call_count, 1)
            self.assertIn("Successfully updated course settings.",
                          mock_messages.add_message.call_args[0])

    def test_instructor_edit_post_saved_default(self):
        data = self.copy_course_dict_and_set_lang_for_post("")
        with mock.patch('course.views.EditCourseForm.has_changed') as mock_changed, \
            mock.patch('course.views.EditCourseForm.save'), \
            mock.patch('course.views.messages') as mock_messages,\
            mock.patch("course.views.render_course_page"),\
                mock.patch("course.views._") as mock_gettext:

            mock_changed.return_value = True
            mock_gettext.side_effect = lambda x: x
            request = self.rf.post(self.get_edit_course_url(),
                                   data=data)
            request.user = self.instructor_participation.user
            course_identifier = self.get_default_course_identifier()
            resp = views.edit_course(request, course_identifier)
            self.assertTrue(resp.status_code, 200)
            self.assertTrue(mock_messages.add_message.call_count, 1)
            self.assertIn("Successfully updated course settings.",
                          mock_messages.add_message.call_args[0])

    def test_instructor_edit_post_saved_spaces_as_lang(self):
        data = self.copy_course_dict_and_set_lang_for_post("   ")
        with mock.patch('course.views.EditCourseForm.has_changed') as mock_changed, \
            mock.patch('course.views.EditCourseForm.save'), \
            mock.patch('course.views.messages') as mock_messages,\
            mock.patch("course.views.render_course_page"),\
                mock.patch("course.views._") as mock_gettext:

            mock_changed.return_value = True
            mock_gettext.side_effect = lambda x: x
            request = self.rf.post(self.get_edit_course_url(),
                                   data=data)
            request.user = self.instructor_participation.user
            course_identifier = self.get_default_course_identifier()
            resp = views.edit_course(request, course_identifier)
            self.assertTrue(resp.status_code, 200)
            self.assertTrue(mock_messages.add_message.call_count, 1)
            self.assertIn("Successfully updated course settings.",
                          mock_messages.add_message.call_args[0])

    def test_instructor_edit_post_form_invalid(self):
        with mock.patch('course.views.EditCourseForm.is_valid') as mock_is_valid, \
            mock.patch('course.views.messages') as mock_messages,\
            mock.patch("course.views.render_course_page"),\
                mock.patch("course.views._") as mock_gettext:

            mock_is_valid.return_value = False
            mock_gettext.side_effect = lambda x: x
            request = self.rf.post(self.get_edit_course_url(),
                                   data=mock.MagicMock())
            request.user = self.instructor_participation.user
            course_identifier = self.get_default_course_identifier()
            resp = views.edit_course(request, course_identifier)
            self.assertTrue(resp.status_code, 200)
            self.assertTrue(mock_messages.add_message.call_count, 1)
            self.assertIn("Failed to update course settings.",
                          mock_messages.add_message.call_args[0])
