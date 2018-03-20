# -*- coding: utf-8 -*-
# Usage
"""
coverage run manage.py test tests --local_test_settings test_local_settings.py
python manage.py test tests.test_my_local --local_test_settings test_local_settings.py  # noqa

coverage run manage.py test tests.test_my_local.test_latexpage --local_test_settings test_local_settings.py  # noqa
python manage.py test tests.test_my_local.test_latexpage --local_test_settings test_local_settings.py  # noqa
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

import os
import sys
from six import StringIO
from unittest import skipIf
from copy import deepcopy
from bson.objectid import ObjectId
import pprint

from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured
from course.models import FlowSession

from image_upload.page.latexpage import (
    get_latex_page_mongo_collection as latex_page_collection,
    get_latex_page_commitsha_template_pair_collection as page_sha_collection)

from tests.base_test_mixins import (
    SingleCoursePageTestMixin, FallBackStorageMessageTestMixin,
    SubprocessRunpyContainerMixin, improperly_configured_cache_patch)

from tests.utils import LocmemBackendTestsMixin, mock
from tests.test_my_local.utils import skip_test, SKIP_LOCAL_TEST_REASON
from tests.test_pages.test_generic import (
    MESSAGE_ANSWER_SAVED_TEXT, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
from tests.test_sandbox import (
    SingleCoursePageSandboxTestBaseMixin)
from tests.contants import PAGE_WARNINGS, PAGE_ERRORS
from tests.test_my_local.sources import latex_sandbox
from tests.test_my_local.test_imageupload import MY_SINGLE_COURSE_SETUP_LIST

source_dir = os.path.join(os.path.dirname(__file__), "sources")

pp = pprint.PrettyPrinter(indent=4)

RANDOM_FLOW = "random"
RANDOM_OLD_FLOW = "random-old-style"
RANDOM_OLD_FULL = "random-old-style-full"
RANDOM_WITH_LATEX_MACRO = "random-with-macro"
RANDOM_ALL_SAME = "random-all-same"

RUNPY_WITH_RETRIES_PATH = "image_upload.page.latexpage.request_python_run_with_retries"  # noqa
INIT_PAGE_DATA_PATH = "image_upload.page.latexpage.LatexRandomQuestionBase.initialize_page_data"  # noqa

COMMIT_SHA_WITH_SAME_CONTENT = b"bec3b0ecd020bb8a4a105c3132c1c7f77acfda23"
COMMIT_SHA_WITH_DIFFERENT_CONTENT = b"ee23f686d5e650fcdd590205d66e18800ae3a3f6"


class LatexPageMixin(SingleCoursePageTestMixin, FallBackStorageMessageTestMixin):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_FLOW

    @property
    def page_id(self):
        raise NotImplementedError()

    def tearDown(self):  # noqa
        super(LatexPageMixin, self).tearDown()
        self.clear_cache()
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

    def get_variant_page_commitsha_mongo_items_count(self):
        return page_sha_collection().count()

    def debug_print_latex_page_commitsha_mongo_collection(
            self, filter=None, compact=False):
        if filter is None:
            filter = {}
        cursor = page_sha_collection().find(filter)
        pp = pprint.PrettyPrinter(indent=4, compact=compact)
        for doc in cursor:
            pp.pprint(doc)

    def get_variant_page_mongo_items_count(self):
        return latex_page_collection().count()

    def debug_print_latex_page_mongo_collection(
            self, filter=None, doc_field="full", compact=False):
        if filter is None:
            filter = {}
        cursor = latex_page_collection().find(filter)
        pp = pprint.PrettyPrinter(indent=4, compact=compact)
        for doc in cursor:
            if doc_field is None:
                pp.pprint(doc)
            else:
                pp.pprint(doc[doc_field])

    def drop_test_mongo(self):
        mongo_db_name = getattr(settings, "RELATE_MONGODB_NAME", 'test_mongo_db')
        assert mongo_db_name
        assert mongo_db_name.startswith("test_")
        uri = getattr(settings, "RELATE_MONGO_URI", None)
        assert uri is None
        from plugins.latex.utils import get_mongo_db
        import mongomock
        assert isinstance(get_mongo_db(), mongomock.database.Database), (
            'You must configure "RELATE_MONGO_CLIENT_PATH = '
            '\'mongomock.MongoClient\' for unit test')

        def drop_mongo():
            from image_upload.page.latexpage import DB
            db = DB
            for col in db.collection_names(include_system_collections=False):
                db.drop_collection(col)
        drop_mongo()


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageTest(SubprocessRunpyContainerMixin, LatexPageMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_FLOW

    def setUp(self):  # noqa
        super(LatexPageTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)

    def test_1_success(self):
        page_id = "rand1"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)
        resp = self.post_answer_by_page_id(page_id, {"blank1": ["9"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(3)

    def test_1_success_assert_only_one_title(self):
        page_id = "rand1"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, u"<h1>random question test1</h1>", count=1)

    def test_1_wrong(self):
        page_id = "rand1"
        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["9.1"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)

    def test_1_fail(self):
        page_id = "rand1"

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["1, 2, 3"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)

    def test_2_correct(self):
        page_id = "rand2"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["90"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(3)

    def test_2_wrong(self):
        page_id = "rand2"

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["91"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)

    def test_2_fail(self):
        page_id = "rand2"
        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["1, 2, 3"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)

    def test_random(self):
        page_id = "rand"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageWithMacroTest(SubprocessRunpyContainerMixin, LatexPageMixin,
                             LocmemBackendTestsMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_WITH_LATEX_MACRO

    def setUp(self):  # noqa
        super(LatexPageWithMacroTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)

    def test_success_page(self):
        page_id = "rand_with_macro"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'data:image/png;base64')
        self.assertContains(resp, 'img-responsive', count=1)
        self.assertNotContains(resp, "The page failed to be rendered")
        self.assertEqual(len(mail.outbox), 0)

    def test_fail_page(self):
        # don't display the error message by latex render
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        page_id = "rand_with_macro_fail"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'img-responsive')
        self.assertContains(resp, "The page failed to be rendered")
        self.assertNotContains(resp, "Undefined control sequence.")
        self.assertEqual(len(mail.outbox), 1)
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        self.assertIn("Undefined control sequence.",
                      self.get_the_latest_message().as_string())


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageOldStyleFullTest(SubprocessRunpyContainerMixin, LatexPageMixin,
                                LocmemBackendTestsMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_OLD_FULL

    def setUp(self):  # noqa
        super(LatexPageOldStyleFullTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)

    def test_old_full_success(self):
        page_id = "single_full"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["9"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(3)

    def test_old_full_wrong(self):
        page_id = "single_full"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["9.1"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)

    def test_old_full_fail(self):
        page_id = "single_full"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["1, 2, 3"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)

    def test_old_full_failure_student_view(self):
        page_id = "single_full_failure"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp, "The page failed to be rendered. Sorry about that.")
        self.assertNotContains(resp, "This is the problematic code")
        self.assertNotContains(resp, "This is the exception traceback")
        self.assertEqual(len(mail.outbox), 1)

    def test_old_full_failure_student_view_email_failure(self):
        page_id = "single_full_failure"
        with mock.patch("image_upload.page.latexpage.LatexRandomQuestionBase.send_error_notification_email",  # noqa
                        autospec=True) as mock_email:
            expected_error_msg = ("This is a test exception for sending "
                                      "a notification email.")
            mock_email.side_effect = RuntimeError(expected_error_msg)
            resp = self.c.get(self.get_page_url_by_page_id(page_id))
            self.assertEqual(resp.status_code, 200)
            self.assertContains(
                resp, "The page failed to be rendered. Sorry about that.")
            self.assertContains(resp, "Both the code and the attempt to")
            self.assertContains(resp, "Sending an email to the course staff")
            self.assertContains(resp, expected_error_msg)
            self.assertEqual(len(mail.outbox), 0)

    def test_old_full_failure_staff_view(self):
        page_id = "single_full_failure"
        self.c.force_login(self.instructor_participation.user)
        self.start_flow(self.flow_id)
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp, "The page failed to be rendered. Sorry about that.")
        self.assertContains(resp, "This is the problematic code")
        self.assertContains(resp, "This is the exception traceback")
        self.assertEqual(len(mail.outbox), 1)

    def test_old_full_random(self):
        page_id = "random_full"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageOldStylePartsTest(SubprocessRunpyContainerMixin, LatexPageMixin,
                                 LocmemBackendTestsMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_OLD_FLOW

    def setUp(self):  # noqa
        super(LatexPageOldStylePartsTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)

    def test_old_parts_success(self):
        page_id = "rand"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["9"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(3)

    def test_old_parts_success_markdown_rendered(self):
        page_id = "rand"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))

        # make sure markdown_to_html is called in each part
        self.assertContains(
            resp, '<a href="http://question.example.com">question</a>')
        self.assertContains(
            resp, '<a href="http://prompt.example.com">prompt</a>')
        self.assertNotContains(
            resp, '<a href="http://explanation.example.com">explanation</a>')

        self.c.force_login(self.instructor_participation.user)
        resp = self.c.get(self.get_page_grading_url_by_page_id(page_id))
        self.assertContains(
            resp, '<a href="http://explanation.example.com">explanation</a>')

    def test_old_parts_wrong(self):
        page_id = "rand"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["9.1"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)

    def test_old_parts_fail(self):
        page_id = "rand"
        resp = self.c.get(self.get_page_url_by_page_id(page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            page_id, {"blank1": ["1, 2, 3"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_FAILED_SAVE_TEXT)
        self.assertEqual(resp.status_code, 200)

        self.end_flow()
        self.assertSessionScoreEqual(0)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageSandboxTest(SubprocessRunpyContainerMixin,
                           SingleCoursePageSandboxTestBaseMixin, LatexPageMixin,
                           LocmemBackendTestsMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_ALL_SAME

    def test_latexpage_sandbox_preview_success(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])
        self.assertContains(resp, u"<h1>random question test</h1>", count=1)
        self.assertContains(resp, u"What is the result?", count=1)

        # clear sandbox
        with self.temporarily_switch_to_user(None):
            pass

        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])
        self.assertContains(resp, u"<h1>random question test</h1>", count=1)
        self.assertContains(resp, u"What is the result?", count=1)

    def test_latexpage_sandbox_preview_markdown_success(self):
        # make sure markdown_to_html is called in each part
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_WITH_MARKDOWN)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])
        self.assertContains(
            resp, '<a href="http://prompt.example.com">prompt</a>')
        self.assertContains(
            resp, '<a href="http://question.example.com">question</a>')
        self.assertContains(
            resp, '<a href="http://explanation.example.com">explanation</a>')

    def test_latexpage_sandbox_answer_success(self):
        answer_data = {'blank1': ["9"]}
        resp = self.get_page_sandbox_submit_answer_response(
            markup_content=latex_sandbox.LATEX_BLANK_FILLING_PAGE,
            answer_data=answer_data)
        self.assertEqual(resp.status_code, 200)
        self.assertResponseContextAnswerFeedbackCorrectnessEquals(resp, 1)

        answer_data = {'blank1': ["9.1"]}
        resp = self.get_page_sandbox_submit_answer_response(
            markup_content=latex_sandbox.LATEX_BLANK_FILLING_PAGE,
            answer_data=answer_data)
        self.assertResponseContextAnswerFeedbackCorrectnessEquals(resp, 0)

    def test_latexpage_sandbox_old_style_preview_success(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertSandboxWarningTextContain(
            resp, "LatexRandomCodeInlineMultiQuestion not using attribute "
                  "'runpy_file' is for debug only, it should not be used "
                  "in production.")

    def test_latexpage_sandbox_old_style_preview_success_no_cache_assert_read_from_mongo(self):  # noqa
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.c.logout()
        self.c.force_login(self.instructor_participation.user)

        # this is also used to cover get result from mongodb
        self.clear_cache()
        self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA)

        # no new entry in mongo page collection
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

    def test_latexpage_sandbox_old_style_preview_success_no_cache_switch_commit_sha_no_new_mongo_entry(self):  # noqa
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.c.logout()
        self.c.force_login(self.instructor_participation.user)

        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)

        self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MULTIPLE_DATA)

        # no new entry in mongo page collection
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.assertSandboxWarningTextContain(
            resp, "LatexRandomCodeInlineMultiQuestion not using attribute "
                  "'runpy_file' is for debug only, it should not be used "
                  "in production.")

    def test_latexpage_sandbox_old_style_answer_success(self):
        answer_data = {'blank1': ["9"]}
        resp = self.get_page_sandbox_submit_answer_response(
            markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS,
            answer_data=answer_data)
        self.assertEqual(resp.status_code, 200)
        self.assertResponseContextAnswerFeedbackCorrectnessEquals(resp, 1)

        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            answer_data = {'blank1': ["9.1"]}
            resp = self.get_page_sandbox_submit_answer_response(
                markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS,  # noqa
                answer_data=answer_data)

            self.assertEqual(mock_runpy.call_count, 0)
            self.assertResponseContextAnswerFeedbackCorrectnessEquals(resp, 0)

    def test_latexpage_sandbox_py_comments_do_not_runpy(self):
        resp = self.get_page_sandbox_preview_response(
            markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS)
        self.assertEqual(resp.status_code, 200)

        self.c.logout()
        self.c.force_login(self.instructor_participation.user)

        # The new markdown added comments to the above one in py file
        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            # The new markdown added comments to the above one in py file
            resp = self.get_page_sandbox_preview_response(
                markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_COMMENTS  # noqa
            )
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(mock_runpy.call_count, 0)

    def test_latexpage_sandbox_tex_template_spaces_do_not_runpy(self):
        # todo: strip comments for latex_page specific tex template
        pass
        # this test failed
        # resp = self.get_page_sandbox_preview_response(
        #     markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS)
        # self.assertEqual(resp.status_code, 200)
        #
        # mock_runpy.reset_mock()
        # self.c.logout()
        # self.c.force_login(self.instructor_participation.user)
        #
        # # The new markdown added spaces to the above one in tex template
        # resp = self.get_page_sandbox_preview_response(
        #     markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_TEX_TEMPLATE_SPACES  # noqa
        # )
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(mock_runpy.call_count, 0)

    def test_latexpage_sandbox_py_more_than_comments_do_runpy(self):
        answer_data = {'blank1': ["9"]}
        self.get_page_sandbox_submit_answer_response(
            markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS,
            answer_data=answer_data)

        self.c.logout()
        self.c.force_login(self.instructor_participation.user)

        # The new markdown added more than comments to the above one in py file,
        # i.e., added a comma
        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            resp = self.get_page_sandbox_preview_response(
                markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_PY_CODE_MORE_THAN_COMMENTS)  # noqa
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(mock_runpy.call_count >= 1)

    def test_latexpage_sandbox_old_style_full_process_preview_success(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertSandboxWarningTextContain(
            resp, "LatexRandomCodeInlineMultiQuestion not using attribute "
                  "'runpy_file' is for debug only, it should not be used "
                  "in production.")
        self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE)

        # to cover get result from mongodb
        self.clear_cache()
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE)
        self.assertEqual(resp.status_code, 200)

    def test_latexpage_sandbox_old_style_full_process_answer_success(self):
        answer_data = {'blank1': ["9"]}
        resp = self.get_page_sandbox_submit_answer_response(
            markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE,  # noqa
            answer_data=answer_data)
        self.assertEqual(resp.status_code, 200)
        result_correctness = resp.context.__getitem__("feedback").correctness
        self.assertEquals(int(result_correctness), 1)

        answer_data = {'blank1': ["9.1"]}
        resp = self.get_page_sandbox_submit_answer_response(
            markup_content=latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_FULL_PROCESS_CODE,  # noqa
            answer_data=answer_data)
        result_correctness = resp.context.__getitem__("feedback").correctness
        self.assertEquals(int(result_correctness), 0)

    def test_latexpage_sandbox_data_files_missing_random_question_data_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_DATA_FILES_MISSING_RAND_QUES_DATA_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS,
            "'foo' should be listed in 'data_files'")

    def test_latexpage_sandbox_warn_random_question_data_file_not_for_cache(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_RANDOM_DATA_FILE_AS_CACHEKEY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        expected_warning_text = (
            "'question-data/random-page-test/test_data_01.bin' "
            "is not expected in 'cache_key_files' as "
            "it will not be used for building cache")
        self.assertSandboxWarningTextContain(resp, expected_warning_text)

    def test_latexpage_sandbox_no_random_question_data_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_NO_RANDOM_DATA_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS,
            "attribute 'random_question_data_file' missing")

    def test_latexpage_sandbox_missing_cachekey_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_CACHEKEY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS,
            "'foo' should be listed in 'data_files'")

    def test_latexpage_sandbox_missing_excluded_cachekey_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_EXCLUDED_CACHEKEY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertSandboxWarningTextContain(
            resp, "'foo' is not in 'data_files'")

    def test_latexpage_sandbox_data_file_not_found(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_DATA_FILE_NOT_FOUND)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS, "data file 'foo' not found")

    def test_latexpage_sandbox_data_files_missing_runpy_file(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_DATA_FILES_MISSING_RUNPY_FILE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS,
            "'foo' should be listed in 'data_files'")

    def test_latexpage_sandbox_parts_missing_runpy_file_runpy_context_not_used(self):  # noqa
        self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS)

        self.c.logout()
        self.c.force_login(self.instructor_participation.user)

        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            resp = self.get_page_sandbox_preview_response(
                latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_MISSING_RUNPY_FILE_WITH_RUNPY_CONTEXT)  # noqa
            self.assertEqual(mock_runpy.call_count, 0)

        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertSandboxWarningTextContain(
            resp, "'runpy_context' is configured with neither "
                  "'runpy_file' nor 'full_process_code' configured "
                  "it will be neglected.")

    def test_latexpage_sandbox_assert_fail_validation_in_update_page_desc(self):
        # this will validate updated_page_desc via super.__init__()
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_FAIL_UPDATE_PAGE_DESC)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(
            resp, (
                "course.validation.ValidationError: None: "
                "attribute \'answers\' has wrong type: "
                "got \'str\', expected "
                "\'&lt;class &#39;relate.utils.Struct&#39;&gt;\'"))

    def test_latexpage_sandbox_missing_runpy_file_missing_part_attrs(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_RUNPY_FILE_AND_MISSING_ATTR)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS, "'answers_process_code' must be "
                               "configured when neither 'runpy_file' nor "
                               "'full_processing_code' is configured.")

    def test_latexpage_sandbox_runpy_file_not_executable(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_RUNPY_FILE_NOT_EXECUTABLE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS,
            "'question-data/random-page-test/test_template.tex' "
            "is not a valid Python script file."
            )

    def test_latexpage_sandbox_missing_cachekey_attribute(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_MISSING_CACHEKEY_ATTRIBUTE)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS, " attribute 'excluded_cache_key_files' not found")  # noqa

    def test_latexpage_sandbox_success_warm_up_by_sandbox(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])

        self.c.logout()
        self.c.force_login(self.instructor_participation.user)

        self.clear_cache()
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])

    def test_latexpage_sandbox_success_warm_up_by_sandbox_page_no_new_mongo_entry(self):  # noqa
        self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX)
        exist_mongo_page_count = self.get_variant_page_mongo_items_count()
        self.assertEqual(exist_mongo_page_count, 2)
        self.start_flow(self.flow_id)

        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            for page_id in ["rand%i" % i
                            for i in range(7)]:
                resp = self.c.get(self.get_page_url_by_page_id(page_id))
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, u"What is the result?")
            self.assertEqual(exist_mongo_page_count,
                             self.get_variant_page_mongo_items_count())
            self.assertEqual(mock_runpy.call_count, 0)

    def test_latexpage_sandbox_success_no_warm_up_by_sandbox(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_NO_WARMUP_BY_SANDBOX)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 1)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])

    def test_latex_page_sandbox_bad_datatype(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_NOT_LIST_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS, ("'question-data/random-page-test/"
                                "zero_length_set.bin' must "
                                "be dumped from a list or tuple"))

    def test_latex_page_sandbox_empty_list_data(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_EMPTY_LIST_DATA)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxNotHasValidPage(resp)
        self.assertResponseContextContains(
            resp, PAGE_ERRORS, ("'question-data/random-page-test/"
                                "zero_length_list.bin'"
                                " seems to be empty, that's not valid"))

    def test_latexpage_sandbox_old_style_raise_error1(self):
        error_markdown = (
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED  # noqa
                .replace("#raise PromptProcessCodeException(error_info)",
                         "raise PromptProcessCodeException(error_info)"
                         ))
        resp = self.get_page_sandbox_preview_response(
            markup_content=error_markdown)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "PromptProcessCodeException: test exception")
        self.assertEqual(len(mail.outbox), 0)

    def test_latexpage_sandbox_old_style_raise_error2(self):
        error_markdown = (
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED  # noqa
                .replace("#raise QuestionProcessCodeException(error_info)",
                         "raise QuestionProcessCodeException(error_info)"
                         ))
        resp = self.get_page_sandbox_preview_response(
            markup_content=error_markdown)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "QuestionProcessCodeException: test exception")
        self.assertEqual(len(mail.outbox), 0)

    def test_latexpage_sandbox_old_style_raise_error3(self):
        error_markdown = (
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED  # noqa
                .replace("#raise AnswersProcessCodeException(error_info)",
                         "raise AnswersProcessCodeException(error_info)"
                         ))
        resp = self.get_page_sandbox_preview_response(
            markup_content=error_markdown)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "AnswersProcessCodeException: test exception")
        self.assertEqual(len(mail.outbox), 0)

    def test_latexpage_sandbox_old_style_raise_error4(self):
        error_markdown = (
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED  # noqa
                .replace("#answer_explanation_process_code",
                         "answer_explanation_process_code")
                .replace("#raise AnswerExplanationProcessCodeException(error_info)",  # noqa
                         "raise AnswerExplanationProcessCodeException(error_info)")  # noqa
        )
        resp = self.get_page_sandbox_preview_response(
            markup_content=error_markdown)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "AnswerExplanationProcessCodeException: test exception")  # noqa
        self.assertEqual(len(mail.outbox), 0)

    def test_latexpage_sandbox_old_style_raise_error5(self):
        error_markdown = (
            latex_sandbox.LATEX_BLANK_FILLING_OLD_STYLE_WITH_PARTS_WITH_EXCEPTION_COMMENTED  # noqa
                .replace("print(answer_explanation_tex)",
                         "pass")
        )
        resp = self.get_page_sandbox_preview_response(
            markup_content=error_markdown)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, ("expects output, while got None"))
        self.assertEqual(len(mail.outbox), 0)

    def test_latexpage_sandbox_success_with_runpy_context(self):  # noqa
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_WITH_RUNPY_CONTEXT)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])
        self.c.logout()
        self.c.force_login(self.instructor_participation.user)
        with mock.patch("image_upload.page.latexpage.request_python_run_with_retries") as mock_runpy:  # noqa
            resp = self.get_page_sandbox_preview_response(
                latex_sandbox.LATEX_BLANK_FILLING_WITH_REVERSE_RUNPY_CONTEXT)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(mock_runpy.call_count, 0)

    def test_latex_code_page_sandbox_success(self):
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_CODE_QUESTION)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertSandboxWarningTextContain(
            resp, "LatexRandomCodeQuestion not using attribute "
                  "'runpy_file' is for debug only, it should not be used "
                  "in production.")


# force_right_wrapper wrong identation
fake_jinja_runpy_success_bad_formatted_return_value = {
    'answer_explanation': (
        '\n\n\n$9$\n'),
    'question': (
        '\n'),
    'answers': (
        '\n'
        '\n'
        'blank1:\n'
        '    type: ShortAnswer\n'
        '    width: 10em\n'
        '  correct_answer:\n'
        '    - type: float\n'
        '      rtol: 0.01\n'
        '      atol: 0.01\n'
        '      value: "9"\n'
        '\n'),
    'prompt': ""
}


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageCacheTest(SubprocessRunpyContainerMixin, LatexPageMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_FLOW
    page_id = "rand1"

    def setUp(self):  # noqa
        super(LatexPageCacheTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)
        self.c.get(self.get_page_url_by_page_id(self.page_id))

    def test_has_cache_no_runpy_for_revisit_page(self):
        # revisit with cache
        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(mock_runpy.call_count, 0)

    def test_cache_cleared_no_runpy_for_revisit_page(self):
        self.clear_cache()
        # revisit with cache cleared
        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(mock_runpy.call_count, 0)

    def test_cache_not_configured_no_runpy_for_revisit_page(self):
        with improperly_configured_cache_patch():
            with self.assertRaises(ImproperlyConfigured):
                # make sure cache is not configured
                import django.core.cache as cache  # noqa

            with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
                resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(mock_runpy.call_count, 0)

    def test_has_mongo_result_no_mongo_operation_for_revisit_page(self):
        # make sure when mongodb has the entry, no update_one is called.
        self.clear_cache()
        with mock.patch(
            "image_upload.page.latexpage.get_latex_page_mongo_collection",
                autospec=True) as mock_mongo_collection:
            import mongomock
            client = mongomock.MongoClient()
            db = client['somedb']
            mock_mongo_collection.return_value = db.a
            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)
            with mock.patch.object(
                    mongomock.collection.Collection, "update_one"
            ) as mock_update_one:
                self.clear_cache()
                resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(mock_update_one.call_count, 0)
                db.a.drop()


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageInitalPageDataTest(SubprocessRunpyContainerMixin, LatexPageMixin,
                                  TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_FLOW
    page_id = "rand1"

    def setUp(self):  # noqa
        super(LatexPageInitalPageDataTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)

        self.c.get(self.get_page_url_by_page_id(self.page_id))

    def test_runpy_with_question_data_missing(self):
        # raise an error when question_data is missing
        self.clear_cache()
        page_data = self.get_page_data_by_page_id(self.page_id)

        # key_making_string_md5 needs to be deleted because
        # key_making_string_md5 by question data
        del page_data.data["key_making_string_md5"]
        del page_data.data["question_data"]
        page_data.save()

        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "'question_data' is missing in page_data.")
        self.c.get(self.get_page_grading_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

    def test_runpy_with_question_data_missing_after_submission(self):
        # raise an error when question_data is missing

        self.post_answer_by_page_id(
            self.page_id, {"blank1": ["9"]})
        self.end_flow()

        self.clear_cache()
        page_data = self.get_page_data_by_page_id(self.page_id)

        # key_making_string_md5 needs to be deleted because
        # key_making_string_md5 by question data
        del page_data.data["key_making_string_md5"]
        del page_data.data["question_data"]
        page_data.save()

        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "'question_data' is missing in page_data.")
        self.c.get(self.get_page_grading_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

    def test_runpy_with_key_making_string_md5_missing(self):

        # the page can be rendered even key_making_string_md5 and template_hash
        # and template_hash_id is not available
        self.clear_cache()
        self.drop_test_mongo()
        page_data = self.get_page_data_by_page_id(self.page_id)
        del page_data.data["template_hash"]
        del page_data.data["key_making_string_md5"]
        del page_data.data["template_hash_id"]
        page_data.save()

        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

        resp = self.post_answer_by_page_id(
            self.page_id, {"blank1": ["9"]})
        self.assertResponseMessagesContains(resp, MESSAGE_ANSWER_SAVED_TEXT)
        self.assertEqual(resp.status_code, 200)
        self.end_flow()
        self.assertSessionScoreEqual(3)

    # {{{ tests for a page which changed commit_sha
    # while content of the page does not change

    @mock.patch(INIT_PAGE_DATA_PATH)
    def test_commit_sha_changed_content_not_changed(self, mock_initialize_page_data):  # noqa

        self.clear_cache()
        original_data = self.get_page_data_by_page_id(self.page_id).data
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 1)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 1)

        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        with mock.patch(RUNPY_WITH_RETRIES_PATH):
            self.c.get(self.get_page_url_by_page_id(self.page_id))

        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 1)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 1)

        # question_data exists in page_data.data()
        # thus won't run initialize_page_data()
        self.assertEqual(mock_initialize_page_data.call_count, 0)

        new_data = self.get_page_data_by_page_id(self.page_id).data

        for k in original_data.keys():
            self.assertEqual(new_data[k], original_data[k])

    @mock.patch(
        "image_upload.page.latexpage.LatexRandomQuestionBase.generate_template_hash",  # noqa
        return_value="88856fafa00fa9b08e109beab35d56cb")
    def test_commit_sha_changed_content_not_changed_assert_get_template_hash_called_once(  # noqa
            self, mock_generate_hash):
        # when commit_sha changed, template_hash is regenerated only once.
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(mock_generate_hash.call_count, 1)
        self.c.get(self.get_page_url_by_page_id("rand"))
        self.assertEqual(mock_generate_hash.call_count, 1)
        self.c.get(self.get_page_url_by_page_id("rand2"))
        self.assertEqual(mock_generate_hash.call_count, 1)

    def test_commit_sha_changed_content_not_changed_no_question_data(self):
        # simulate that the question_data is empty, generate a new one
        page_data = self.get_page_data_by_page_id(self.page_id)
        original_question_data = page_data.data["question_data"]
        del page_data.data["question_data"]
        page_data.save()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        new_page_data = self.get_page_data_by_page_id(self.page_id)
        self.assertEqual(new_page_data.data["question_data"],
                         original_question_data)

    @mock.patch(INIT_PAGE_DATA_PATH)
    def test_commit_sha_changed_content_not_changed_no_qst_data_assert_initialize_page_data_called_once(  # noqa
            self, mock_initialize_page_data):
        page_data = self.get_page_data_by_page_id(self.page_id)
        del page_data.data["question_data"]
        page_data.save()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))

        self.assertEqual(mock_initialize_page_data.call_count, 1)

    def test_commit_sha_changed_content_not_changed_invalid_template_hash_id(self):
        # simulate that the template_hash_id is invalid
        invalid_template_hash_id = "invalid_id"
        page_data = self.get_page_data_by_page_id(self.page_id)
        page_data.data["template_hash_id"] = invalid_template_hash_id
        page_data.save()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)
        new_page_data = self.get_page_data_by_page_id(self.page_id)
        self.assertNotEqual(new_page_data.data["template_hash_id"],
                            invalid_template_hash_id)

    def test_commit_sha_changed_content_not_changed_mongo_template_hash_manualy_changed(self):  # noqa
        # simulate that the template_hash in mongo entry is manually changed
        original_page_data = self.get_page_data_by_page_id(self.page_id)
        current_commit_sha = self.get_course_commit_sha(
            self.student_participation).decode()

        template_hash_id = original_page_data.data["template_hash_id"]
        template_hash = original_page_data.data["template_hash"]
        mongo_fake_changed_template_hash = template_hash + "_change"

        # switch to another commit_sha
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))

        # then we manually changed the mongo data
        page_sha_collection().update_one(
            {"_id": ObjectId(template_hash_id)},
            {"$set": {current_commit_sha: mongo_fake_changed_template_hash}})

        # then we switch back to original commit_sha
        self.post_update_course_content(current_commit_sha)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

        new_mongo_entry = page_sha_collection().find_one(
            {"_id": ObjectId(template_hash_id)},
        )

        # the record is "repaired"
        self.assertEqual(new_mongo_entry[current_commit_sha], template_hash)

    def test_commit_sha_changed_content_not_changed_page_data_hash_manualy_changed(self):  # noqa
        # simulate that the template_hash in page_data entry is manually changed
        original_page_data = self.get_page_data_by_page_id(self.page_id)

        f = FlowSession.objects.last()
        current_commit_sha = f.active_git_commit_sha

        template_hash = original_page_data.data["template_hash"]

        # switch to another commit_sha
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))

        # then we switch back to original commit_sha
        self.post_update_course_content(current_commit_sha)

        # manually change page data
        current_page_data = self.get_page_data_by_page_id(self.page_id)
        data_fake_changed_template_hash = template_hash + "_change"
        current_page_data.data["template_hash"] = data_fake_changed_template_hash
        current_page_data.save()

        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

        # the data is "repaired"
        new_page_data_data = self.get_page_data_by_page_id(self.page_id).data
        for k in new_page_data_data.keys():
            self.assertEqual(new_page_data_data[k], original_page_data.data[k])

    @mock.patch(INIT_PAGE_DATA_PATH)
    def test_commit_sha_changed_content_not_changed_no_template_hash_and_id(
            self, mock_initialize_page_data):
        # simulate that the tempate_hash and template_has_id are empty,
        # generate new ones
        page_data = self.get_page_data_by_page_id(self.page_id)
        original_page_data = deepcopy(page_data)
        del page_data.data["template_hash"]
        del page_data.data["template_hash_id"]
        page_data.save()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        new_page_data = self.get_page_data_by_page_id(self.page_id)
        self.assertEqual(new_page_data.data["template_hash"],
                         original_page_data.data["template_hash"])
        self.assertEqual(new_page_data.data["template_hash_id"],
                         original_page_data.data["template_hash_id"])

        self.assertEqual(mock_initialize_page_data.call_count, 0)

    @mock.patch(
        "image_upload.page.latexpage.LatexRandomQuestionBase.generate_template_hash",  # noqa
        return_value="88856fafa00fa9b08e109beab35d56cb")
    def test_no_tmpl_hash_and_id_assert_generate_hash_called_twice(
            self, mock_generate_hash):
        # simulate that the tempate_hash and template_has_id are empty,
        # generate new ones
        page_data = self.get_page_data_by_page_id(self.page_id)
        del page_data.data["template_hash"]
        del page_data.data["template_hash_id"]
        page_data.save()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        # one for generate template_hash for all other questions, one for this page
        # only
        self.assertEqual(mock_generate_hash.call_count, 2)

    # }}}

    # {{{ tests for a page which changed commit_sha
    # and content of the page does change

    def test_commit_sha_changed_content_changed_no_init_page_data_run(self):
        self.clear_cache()
        new_commit_sha = COMMIT_SHA_WITH_DIFFERENT_CONTENT.decode()

        redirected_entry = page_sha_collection().find_one(
            {"%s_next" % new_commit_sha: {"$exists": True}})
        self.assertIsNone(redirected_entry)

        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)

        with mock.patch(
                INIT_PAGE_DATA_PATH, autospec=True) as mock_initialize_page_data:
            self.c.get(self.get_page_url_by_page_id(self.page_id))

            # question_data exists in page_data.data()
            # thus won't run initialize_page_data()
            self.assertEqual(mock_initialize_page_data.call_count, 0)

    def test_commit_sha_changed_content_changed(self):
        self.clear_cache()
        original_data = self.get_page_data_by_page_id(self.page_id).data
        new_commit_sha = COMMIT_SHA_WITH_DIFFERENT_CONTENT.decode()

        redirected_entry = page_sha_collection().find_one(
            {"%s_next" % new_commit_sha: {"$exists": True}})
        self.assertIsNone(redirected_entry)

        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        new_data = self.get_page_data_by_page_id(self.page_id).data

        # page_data is different except the question_data
        for k in original_data.keys():
            if k == "question_data":
                self.assertEqual(new_data[k], original_data[k])
            else:
                self.assertNotEqual(new_data[k], original_data[k])

        # the original commit_sha mongo entry is altered so as to be able to
        # redirect to new commit_sha entry
        redirected_field_key = "%s_next" % new_commit_sha
        redirected_entry = page_sha_collection().find_one(
            {redirected_field_key: {"$exists": True}})
        self.assertIsNotNone(redirected_entry)

        # get the target_entry
        target_id = redirected_entry[redirected_field_key]

        from bson.objectid import ObjectId
        target_commit_sha_entry = (
            page_sha_collection().find_one(
                {"_id": ObjectId(target_id)}))

        target_template_hash = target_commit_sha_entry["template_hash"]
        self.assertEqual(target_template_hash, new_data["template_hash"])

        question_data = new_data["question_data"]
        from image_upload.page.latexpage import (
            make_latex_page_key, get_latex_cache, get_key_making_string_md5_hash)

        expected_key_making_string_md5 = get_key_making_string_md5_hash(
            target_template_hash, question_data)

        self.assertEqual(
            new_data["key_making_string_md5"], expected_key_making_string_md5)

        try:
            import django.core.cache as cache
            cache_key = make_latex_page_key(expected_key_making_string_md5)
        except ImproperlyConfigured:
            cache_key = None

        if cache_key is not None:
            target_latex_page_entry = latex_page_collection().find_one(
                {"key": cache_key}
            )
            self.assertIsNotNone(target_latex_page_entry)
            def_cache = get_latex_cache(cache)
            result = def_cache.get(cache_key)
            self.assertIsNotNone(result)

            expected_result = target_latex_page_entry["content"]
            for k in expected_result.keys():
                self.assertEqual(result[k], expected_result[k])

            # this is what the original page doesn't have
            self.assertTrue(
                "The correct answer is:" in result["answer_explanation"])

    def test_commit_sha_changed_content_changed_switch_back_and_forth(self):
        f = FlowSession.objects.last()
        current_commit_sha = f.active_git_commit_sha

        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.post_update_course_content(current_commit_sha)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

    def test_commit_sha_changed_content_changed_switch_back_and_forth_redirect_broken(self):  # noqa
        f = FlowSession.objects.last()
        current_commit_sha = f.active_git_commit_sha

        # first, make sure the redirect_id is generated
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.post_update_course_content(current_commit_sha)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        different_commit_sha = COMMIT_SHA_WITH_DIFFERENT_CONTENT.decode()

        # the redirect_entry must exist
        redirect_entry = page_sha_collection().find_one(
            {"%s_next" % different_commit_sha: {"$exists": True}}
        )
        self.assertIsNotNone(redirect_entry)

        # the target entry must exist
        target_id = redirect_entry["%s_next" % different_commit_sha]
        target_entry = page_sha_collection().find_one(
            {"_id": ObjectId(target_id)}
        )
        target_template_hash = target_entry["template_hash"]
        self.assertIsNotNone(target_entry)

        # delete the target entry
        page_sha_collection().delete_one({
            "_id": ObjectId(target_id)
        })
        target_entry = page_sha_collection().find_one(
            {"_id": ObjectId(target_id)})
        # make sure it is deleted
        self.assertIsNone(target_entry)

        # {{{ navigate to different commit_sha, make sure
        # the redirect data is updated
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

        self.post_update_course_content(current_commit_sha)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)
        # }}}

        # make sure the redirect entry is available
        new_redirect_entry = page_sha_collection().find_one(
            {"%s_next" % different_commit_sha: {"$exists": True}}
        )
        self.assertIsNotNone(new_redirect_entry)

        new_target_id = new_redirect_entry["%s_next" % different_commit_sha]
        new_target_entry = page_sha_collection().find_one(
            {"_id": ObjectId(new_target_id)}
        )
        self.assertIsNotNone(new_target_entry)
        new_target_template_hash = new_target_entry["template_hash"]

        # make sure the template hash it the same with the "deleted" redirect_entry
        self.assertEqual(target_template_hash, new_target_template_hash)

        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

    def test_commit_sha_changed_content_changed_switch_back_and_forth_redirect_empty_template_hash(self):  # noqa
        f = FlowSession.objects.last()
        current_commit_sha = f.active_git_commit_sha

        # first, make sure the redirect_id is generated
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.post_update_course_content(current_commit_sha)
        self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        different_commit_sha = COMMIT_SHA_WITH_DIFFERENT_CONTENT.decode()

        # the redirect_entry must exist
        redirect_entry = page_sha_collection().find_one(
            {"%s_next" % different_commit_sha: {"$exists": True}}
        )
        self.assertIsNotNone(redirect_entry)

        # the target entry must exist
        target_id = redirect_entry["%s_next" % different_commit_sha]
        target_entry = page_sha_collection().find_one(
            {"_id": ObjectId(target_id)}
        )
        target_template_hash = target_entry["template_hash"]
        self.assertIsNotNone(target_entry)

        # delete the target entry
        page_sha_collection().update_one(
            {"_id": ObjectId(target_id)},
            {"$set": {
                different_commit_sha: ""}}
        )

        # {{{ navigate to different commit_sha, make sure
        #  the redirect data is updated
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

        self.post_update_course_content(current_commit_sha)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)

        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)
        # }}}

        # make sure the redirect entry is available
        new_redirect_entry = page_sha_collection().find_one(
            {"%s_next" % different_commit_sha: {"$exists": True}}
        )
        self.assertIsNotNone(new_redirect_entry)

        new_target_id = new_redirect_entry["%s_next" % different_commit_sha]
        new_target_entry = page_sha_collection().find_one(
            {"_id": ObjectId(new_target_id)}
        )

        # why they equal????
        self.assertEqual(target_id, new_target_id)

        self.assertIsNotNone(new_target_entry)
        new_target_template_hash = new_target_entry["template_hash"]

        # make sure the template hash it the same with the "modified" redirect_entry
        self.assertEqual(target_template_hash, new_target_template_hash)

        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

    def test_commit_sha_changed_content_changed_assert_jinja_runpy_called_once(
            self):

        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)

        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(mock_runpy.call_count, 1)

    # }}}


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageRunpyFailureTest(SubprocessRunpyContainerMixin,
                                LatexPageMixin,
                                SingleCoursePageSandboxTestBaseMixin,
                                LocmemBackendTestsMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_FLOW
    page_id = "rand1"

    def setUp(self):  # noqa
        super(LatexPageRunpyFailureTest, self).setUp()
        self.c.force_login(self.student_participation.user)
        self.start_flow(self.flow_id)
        self.c.get(self.get_page_url_by_page_id(self.page_id))

    def test_switch_commit_sha_does_create_new_page_doc_in_mongo(self):
        # this is not a failure test, but to ensure new doc is created in mongo
        # page collection
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)
        self.assertEqual(len(mail.outbox), 0)

    def test_switch_commit_sha_does_runpy(self):
        # this is not a failure test, but to ensure new doc is created in mongo
        # page collection
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 1)
        with mock.patch(
                RUNPY_WITH_RETRIES_PATH,
        ) as mock_runpy:
            self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(mock_runpy.call_count, 1)

    def test_switch_to_course_commit_sha_with_bad_result(self):
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.assertEqual(len(mail.outbox), 0)

        with mock.patch(
            "image_upload.page.latexpage.LatexRandomQuestionBase.jinja_runpy",
            return_value=(True, fake_jinja_runpy_success_bad_formatted_return_value)
        ) as mock_runpy:

            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(mock_runpy.call_count, 1)

        expected_error_string = (
            "The page failed to be rendered. Sorry about that")
        self.assertContains(resp, expected_error_string)
        self.assertNotContains(resp,
                               "ParserError: while parsing a block mapping")
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)

        self.assertEqual(self.get_variant_page_mongo_items_count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ParserError: while parsing a block mapping",
                      self.get_the_latest_message().as_string())

    # def test_runpy_raised_error(self):
    #     self.clear_cache()
    #     self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
    #     self.assertEqual(len(mail.outbox), 0)
    #
    #     with mock.patch(
    #             "image_upload.page.latexpage.LatexRandomQuestionBase.jinja_runpy",
    #             autospec=True) as mock_jinja_runpy:
    #         expected_error_str = "This is a test exception."
    #         mock_jinja_runpy.side_effect = RuntimeError(expected_error_str)
    #
    #         resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(mock_jinja_runpy.call_count, 1)
    #
    #         self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)  # noqa
    #         self.assertEqual(self.get_variant_page_mongo_items_count(), 1)
    #
    #         self.assertEqual(len(mail.outbox), 1)
    #         self.assertContains(resp, expected_error_str)

    def test_switch_to_failure_course_commit_sha(self):
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.assertEqual(len(mail.outbox), 0)

        expected_error_str = ("Jinja runpy just failed to "
                            "return an result in the test")

        with mock.patch(
            RUNPY_WITH_RETRIES_PATH,
            return_value={"result": "setup_error", "message": expected_error_str}
        ):
            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)

            self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)

            # no failure result will be saved in latex_page_mongo_collection
            self.assertEqual(self.get_variant_page_mongo_items_count(), 1)

            # {{{ the failure result won't be cached
            new_data = self.get_page_data_by_page_id(self.page_id).data
            template_hash = new_data["template_hash"]
            question_data = new_data["question_data"]

            from image_upload.page.latexpage import (
                make_latex_page_key, get_latex_cache,
                get_key_making_string_md5_hash)

            key_making_string_md5 = get_key_making_string_md5_hash(
                template_hash, question_data)

            import django.core.cache as cache
            cache_key = make_latex_page_key(key_making_string_md5)
            def_cache = get_latex_cache(cache)

            self.assertIsNone(def_cache.get(cache_key),
                              ("Make sure failure result of "
                               "runpy is not cached!"))
            # }}}

            self.assertEqual(len(mail.outbox), 1)

    def test_switch_to_python_run_timeout(self):
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.assertEqual(len(mail.outbox), 0)

        expected_error_str = "The page failed to be rendered due to timeout"

        with mock.patch(
            RUNPY_WITH_RETRIES_PATH,
            return_value={
                "result": "timeout",
                "message": ("Jinja runpy just failed to "
                            "return an result in the test")}
        ):

            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, expected_error_str)

            self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)

            # no failure result will be saved in latex_page_mongo_collection
            self.assertEqual(self.get_variant_page_mongo_items_count(), 1)

            # {{{ the failure result won't be cached
            new_data = self.get_page_data_by_page_id(self.page_id).data
            template_hash = new_data["template_hash"]
            question_data = new_data["question_data"]

            from image_upload.page.latexpage import (
                make_latex_page_key, get_latex_cache,
                get_key_making_string_md5_hash)

            key_making_string_md5 = get_key_making_string_md5_hash(
                template_hash, question_data)

            import django.core.cache as cache
            cache_key = make_latex_page_key(key_making_string_md5)
            def_cache = get_latex_cache(cache)

            self.assertIsNone(def_cache.get(cache_key))
            # }}}

            self.assertEqual(len(mail.outbox), 0)

    def test_switch_to_failure_course_commit_sha_raise_uncaught_error(self):
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.assertEqual(len(mail.outbox), 0)

        with mock.patch(
            RUNPY_WITH_RETRIES_PATH,
            autospec=True
        ) as mock_runpy:
            expected_error_str = ("This is an error raised with "
                                  "request_python_run_with_retries")
            mock_runpy.side_effect = RuntimeError(expected_error_str)

            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)

            self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)

            # no failure result will be saved in latex_page_mongo_collection
            self.assertEqual(self.get_variant_page_mongo_items_count(), 1)

            # {{{ the failure result won't be cached
            new_data = self.get_page_data_by_page_id(self.page_id).data
            template_hash = new_data["template_hash"]
            question_data = new_data["question_data"]

            from image_upload.page.latexpage import (
                make_latex_page_key, get_latex_cache,
                get_key_making_string_md5_hash)

            key_making_string_md5 = get_key_making_string_md5_hash(
                template_hash, question_data)

            import django.core.cache as cache
            cache_key = make_latex_page_key(key_making_string_md5)
            def_cache = get_latex_cache(cache)

            self.assertIsNone(def_cache.get(cache_key))
            # }}}

            self.assertEqual(len(mail.outbox), 1)

    def test_runpy_raise_other_unknown_error(self):
        self.assertEqual(len(mail.outbox), 0)
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_DIFFERENT_CONTENT)
        self.assertEqual(len(mail.outbox), 0)

        with mock.patch(
            RUNPY_WITH_RETRIES_PATH,
            autospec=True
        ) as mock_runpy:
            expected_error_str = ("This is an unknown error raised with "
                                  "request_python_run_with_retries")
            mock_runpy.return_value = {"result": expected_error_str}

            resp = self.c.get(self.get_page_url_by_page_id(self.page_id))
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, expected_error_str)
            self.assertEqual(self.get_variant_page_commitsha_mongo_items_count(), 2)

            # no failure result will be saved in latex_page_mongo_collection
            self.assertEqual(self.get_variant_page_mongo_items_count(), 1)

            # {{{ the failure result won't be cached
            new_data = self.get_page_data_by_page_id(self.page_id).data
            template_hash = new_data["template_hash"]
            question_data = new_data["question_data"]

            from image_upload.page.latexpage import (
                make_latex_page_key, get_latex_cache,
                get_key_making_string_md5_hash)

            key_making_string_md5 = get_key_making_string_md5_hash(
                template_hash, question_data)

            import django.core.cache as cache
            cache_key = make_latex_page_key(key_making_string_md5)
            def_cache = get_latex_cache(cache)

            self.assertIsNone(def_cache.get(cache_key))
            # }}}

            self.assertEqual(len(mail.outbox), 1)


@skipIf(skip_test, SKIP_LOCAL_TEST_REASON)
@override_settings(
    CACHE_BACKEND='dummy:///')
class LatexPageSandboxFlowCombineTest(
        SubprocessRunpyContainerMixin, SingleCoursePageSandboxTestBaseMixin,
        LatexPageMixin, LocmemBackendTestsMixin, TestCase):
    courses_setup_list = MY_SINGLE_COURSE_SETUP_LIST
    flow_id = RANDOM_ALL_SAME

    def test_latexpage_sandbox_success_warm_up_by_sandbox_switch_commit_sha_no_new_page_mongo_entry(self):  # noqa
        self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)

        self.c.logout()
        self.c.force_login(self.instructor_participation.user)

        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        resp = self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX)
        self.assertEqual(resp.status_code, 200)
        self.assertSandboxHasValidPage(resp)
        self.assertEqual(self.get_variant_page_mongo_items_count(), 2)
        self.assertResponseContextIsNone(resp, PAGE_ERRORS)
        self.assertResponseContextEqual(resp, PAGE_WARNINGS, [])

    def test_get_current_commit_sha(self):
        current_commit_sha = self.get_course_commit_sha(
            self.instructor_participation)

        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        new_commit_sha = self.get_course_commit_sha(
            self.instructor_participation)

        self.assertNotEqual(current_commit_sha, new_commit_sha)

        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT,
                                        fetch_update=True, assert_success=False)
        new_commit_sha = self.get_course_commit_sha(
            self.instructor_participation)

        self.assertEqual(current_commit_sha, new_commit_sha)

    def test_latexpage_commit_sha_changed_then_sandbox_warm_up_by_sandbox_new_page_view_no_new_runpy(  # noqa
            self):
        """
        Case: if some session is created and viewed, then then content is changed,
        the instructor did a warm up in sandbox. The test is to ensure that, the
        original pages won't do a new runpy (no new mongo page entry will be created)
        """
        self.clear_cache()
        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)

        self.clear_cache()
        # self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT)
        self.get_page_sandbox_preview_response(
            latex_sandbox.LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX)

        self.post_update_course_content(COMMIT_SHA_WITH_SAME_CONTENT,
                                        fetch_update=True,
                                        assert_success=False)

        self.start_flow(self.flow_id)

        with mock.patch(RUNPY_WITH_RETRIES_PATH) as mock_runpy:
            for page_id in ["rand%i" % i
                            for i in range(7)]:
                resp = self.c.get(self.get_page_url_by_page_id(page_id))
                self.assertEqual(resp.status_code, 200)

            self.get_page_sandbox_preview_response(
                latex_sandbox.LATEX_BLANK_FILLING_PAGE_WARMUP_BY_SANDBOX)

            self.assertEqual(mock_runpy.call_count, 0)

    def test_latexpage_multiple_session_same_template_hash_correct(self):
        """
        this is to make sure the template hash is correct
        across run, or the same content will generate different cache key
        and result in diffrent mongo_page and caches
        """
        def get_commit_sha_template_hash(hash):
            self.clear_cache()
            self.post_update_course_content(hash)
            for page_id in ["rand%i" % i
                            for i in range(7)]:
                resp = self.c.get(self.get_page_url_by_page_id(page_id))
                self.assertEqual(resp.status_code, 200)
                data = self.get_page_data_by_page_id(
                    page_id="rand0").data
                return data["template_hash"]

        self.start_flow(self.flow_id)

        for i in range(4):
            self.assertEqual(
                get_commit_sha_template_hash(COMMIT_SHA_WITH_SAME_CONTENT),
                "82af1de447c4795605160e1f6f29b23e")
            self.assertEqual(
                get_commit_sha_template_hash(COMMIT_SHA_WITH_DIFFERENT_CONTENT),
                "5250f1590d379309661b6d86ef9cce38")
