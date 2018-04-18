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
import unittest
from django.test import TestCase, RequestFactory
from django.core.exceptions import ObjectDoesNotExist

from course.models import FlowSession
from course import content

from tests.base_test_mixins import (
    SingleCourseTestMixin,
    improperly_configured_cache_patch, SingleCoursePageTestMixin)
from tests.test_sandbox import SingleCoursePageSandboxTestBaseMixin
from tests.utils import mock
from tests import factories  # noqa


class SingleCoursePageCacheTest(SingleCoursePageTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):  # noqa
        super(SingleCoursePageCacheTest, cls).setUpTestData()
        cls.start_flow(cls.flow_id)

    @improperly_configured_cache_patch()
    def test_disable_cache(self, mock_cache):
        from django.core.exceptions import ImproperlyConfigured
        with self.assertRaises(ImproperlyConfigured):
            from django.core.cache import cache  # noqa

    def test_view_flow_with_cache(self):
        resp = self.c.get(self.get_page_url_by_ordinal(0))
        self.assertEqual(resp.status_code, 200)
        self.c.get(self.get_page_url_by_ordinal(1))

        with mock.patch("course.content.get_repo_blob") as mock_get_repo_blob:
            resp = self.c.get(self.get_page_url_by_ordinal(0))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(mock_get_repo_blob.call_count, 0)

    def test_view_flow_with_cache_improperly_configured(self):
        resp = self.c.get(self.get_page_url_by_ordinal(0))
        self.assertEqual(resp.status_code, 200)
        self.c.get(self.get_page_url_by_ordinal(1))

        with improperly_configured_cache_patch():
            resp = self.c.get(self.get_page_url_by_ordinal(0))
            self.assertEqual(resp.status_code, 200)


# {{{ Test Nbconvert for rendering ipynb notebook

QUESTION_MARKUP_FULL = """
type: Page
id: ipynb
content: |

  # Ipython notebook Examples

  {{ render_notebook_cells("test.ipynb") }}
"""

QUESTION_MARKUP_SLICED1 = """
type: Page
id: ipynb
content: |

  # Ipython notebook Examples

  {{ render_notebook_cells("test.ipynb", indices=[0, 1, 2]) }}
"""

QUESTION_MARKUP_SLICED2 = """
type: Page
id: ipynb
content: |

  # Ipython notebook Examples

  {{ render_notebook_cells("test.ipynb", indices=[1, 2]) }}
"""

QUESTION_MARKUP_CLEAR_MARKDOWN = """
type: Page
id: ipynb
content: |

  # Ipython notebook Examples

  {{ render_notebook_cells("test.ipynb", clear_markdown=True) }}
"""

QUESTION_MARKUP_CLEAR_OUTPUT = """
type: Page
id: ipynb
content: |

  # Ipython notebook Examples

  {{ render_notebook_cells("test.ipynb", clear_output=True) }}
"""

QUESTION_MARKUP_CLEAR_ALL = """
type: Page
id: ipynb
content: |

  # Ipython notebook Examples

  {{ render_notebook_cells("test.ipynb", clear_markdown=True, clear_output=True) }}
"""

MARKDOWN_PLACEHOLDER = "wzxhzdk"

TEST_IPYNB_BYTES = json.dumps({
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# First Title of Test NoteBook"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {
                "scrolled": True
            },
            "outputs": [
                {
                    "name": "stdout",
                    "output_type": "stream",
                    "text": [
                        "This is function1\n"
                    ]
                }
            ],
            "source": [
                "def function1():\n",
                "    print(\"This is function1\")\n",
                "\n",
                "function1()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Second Title of Test NoteBook"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {
                "collapsed": True
            },
            "outputs": [],
            "source": [
                "def function2():\n",
                "    print(\"This is function2\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": 3,
            "metadata": {},
            "outputs": [
                {
                    "name": "stdout",
                    "output_type": "stream",
                    "text": [
                        "This is function2\n"
                    ]
                }
            ],
            "source": [
                "function2()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {
                "collapsed": True
            },
            "outputs": [],
            "source": [
                "print(`5**18`)"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.5.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}).encode()

FIRST_TITLE_TEXT = "First Title of Test NoteBook"
SECOND_TITLE_TEXT = "Second Title of Test NoteBook"
TEXT_CELL_HTML_CLASS = "text_cell_render"
CODE_CELL_HTML_CLASS = "code_cell"
CODE_CELL_IN_STR_PATTERN = '<div class="prompt input_prompt">In[%s]:</div>'
CODE_CELL_PRINT_STR1 = "This is function1"
CODE_CELL_PRINT_STR2 = "This is function2"
RELATE_IPYNB_CONVERT_PRE_WRAPPER_TAG_NAME = "relate_ipynb"


def strip_nbsp(s):
    """
    Returns the given HTML with '&nbsp;' (introduced by nbconvert) stripped
    """
    from django.utils.encoding import force_text
    return force_text(s).replace('&nbsp;', '').replace(u'\xa0', '')


def get_nb_html_from_response(response):
    from django.utils.safestring import mark_safe
    return strip_nbsp(mark_safe(response.context["body"]))


class NbconvertRenderTestMixin(SingleCoursePageSandboxTestBaseMixin):
    def assertIsValidNbConversion(self, response):  # noqa
        self.assertNotContains(response, MARKDOWN_PLACEHOLDER)
        self.assertNotContains(response, "```")
        self.assertNotContains(response, "# First Title of Test NoteBook")
        self.assertNotContains(response, "# Second Title of Test NoteBook")
        self.assertNotContains(response, RELATE_IPYNB_CONVERT_PRE_WRAPPER_TAG_NAME)

    def setUp(self):
        super(NbconvertRenderTestMixin, self).setUp()
        patcher = mock.patch("course.content.get_repo_blob_data_cached")
        self.mock_func = patcher.start()
        self.mock_func.return_value = TEST_IPYNB_BYTES
        self.addCleanup(patcher.stop)


class NbconvertRenderTest(NbconvertRenderTestMixin, TestCase):

    force_login_student_for_each_test = False

    @classmethod
    def setUpTestData(cls):  # noqa
        super(NbconvertRenderTest, cls).setUpTestData()
        cls.c.force_login(cls.instructor_participation.user)

    def test_notebook_page_view(self):
        self.start_flow(flow_id="001-linalg-recap",
                        course_identifier=self.course.identifier,
                        assume_success=False)
        fs = FlowSession.objects.last()
        resp = self.c.get(
            self.get_page_url_by_page_id(
                "ipynb", course_identifier=self.course.identifier,
                flow_session_id=fs.id))
        self.assertEqual(resp.status_code, 200)

    def test_notebook_file_not_found(self):
        self.start_flow(flow_id="001-linalg-recap",
                        course_identifier=self.course.identifier,
                        assume_success=False)
        with mock.patch(
                "course.content.get_repo_blob_data_cached") as mock_get_blob_cached:

            from django.core.exceptions import ObjectDoesNotExist
            mock_get_blob_cached.side_effect = ObjectDoesNotExist()

            fs = FlowSession.objects.last()
            with self.assertRaises(ObjectDoesNotExist):
                self.c.get(
                    self.get_page_url_by_page_id(
                        "ipynb", course_identifier=self.course.identifier,
                        flow_session_id=fs.id))

    def test_full_notebook_render(self):
        resp = self.get_page_sandbox_preview_response(QUESTION_MARKUP_FULL)

        self.assertIsValidNbConversion(resp)
        self.assertContains(resp, TEXT_CELL_HTML_CLASS, count=2)
        self.assertContains(resp, CODE_CELL_HTML_CLASS, count=4)
        self.assertContains(resp, FIRST_TITLE_TEXT, count=1)
        self.assertContains(resp, SECOND_TITLE_TEXT, count=1)
        self.assertContains(resp, CODE_CELL_PRINT_STR1, count=2)
        self.assertContains(resp, CODE_CELL_PRINT_STR2, count=2)

        # backtick is properly rendered with highlight
        # for "`5**18`". though this syntax is not allowed in PY3
        self.assertContains(
            resp,
            '<span class="err">`</span><span class="mi">5</span>')

        nb_html = get_nb_html_from_response(resp)
        for i in range(1, 4):
            self.assertInHTML(CODE_CELL_IN_STR_PATTERN % i, nb_html)

    def test_notebook_sliced1(self):
        resp = self.get_page_sandbox_preview_response(QUESTION_MARKUP_SLICED1)
        self.assertIsValidNbConversion(resp)
        self.assertContains(resp, TEXT_CELL_HTML_CLASS, count=2)
        self.assertContains(resp, CODE_CELL_HTML_CLASS, count=1)
        self.assertContains(resp, FIRST_TITLE_TEXT, count=1)
        self.assertContains(resp, SECOND_TITLE_TEXT, count=1)
        self.assertContains(resp, CODE_CELL_PRINT_STR1, count=2)
        self.assertNotContains(resp, CODE_CELL_PRINT_STR2)

        nb_html = get_nb_html_from_response(resp)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % 1, nb_html, count=1)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % 2, nb_html, count=0)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % 3, nb_html, count=0)

    def test_notebook_sliced2(self):
        resp = self.get_page_sandbox_preview_response(QUESTION_MARKUP_SLICED2)
        self.assertIsValidNbConversion(resp)
        self.assertContains(resp, TEXT_CELL_HTML_CLASS, count=1)
        self.assertContains(resp, CODE_CELL_HTML_CLASS, count=1)
        self.assertNotContains(resp, FIRST_TITLE_TEXT)
        self.assertContains(resp, SECOND_TITLE_TEXT, count=1)
        self.assertContains(resp, CODE_CELL_PRINT_STR1, count=2)
        self.assertNotContains(resp, CODE_CELL_PRINT_STR2)

        # code highlight functions (in terms of rendered ipynb notebook cells only)
        import six
        if six.PY3:
            self.assertRegex(resp.context["body"], 'class="\w*\s*highlight[^\w]')
        self.assertContains(resp, " highlight hl-ipython3")
        self.assertContains(resp,
                            '<span class="nb">print</span>'
                            '<span class="p">(</span>',
                            count=1)

        nb_html = get_nb_html_from_response(resp)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % 1, nb_html, count=1)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % 2, nb_html, count=0)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % 3, nb_html, count=0)

    def test_notebook_clear_markdown(self):
        resp = self.get_page_sandbox_preview_response(QUESTION_MARKUP_CLEAR_MARKDOWN)
        self.assertIsValidNbConversion(resp)
        self.assertNotContains(resp, TEXT_CELL_HTML_CLASS)
        self.assertContains(resp, CODE_CELL_HTML_CLASS, count=4)
        self.assertNotContains(resp, FIRST_TITLE_TEXT)
        self.assertNotContains(resp, SECOND_TITLE_TEXT)

        nb_html = get_nb_html_from_response(resp)
        for i in range(1, 4):
            self.assertInHTML(CODE_CELL_IN_STR_PATTERN % i, nb_html, count=1)

    def test_notebook_clear_output(self):
        resp = self.get_page_sandbox_preview_response(QUESTION_MARKUP_CLEAR_OUTPUT)
        self.assertIsValidNbConversion(resp)
        self.assertContains(resp, TEXT_CELL_HTML_CLASS, count=2)
        self.assertContains(resp, CODE_CELL_HTML_CLASS, count=4)
        self.assertContains(resp, FIRST_TITLE_TEXT, count=1)
        self.assertContains(resp, SECOND_TITLE_TEXT, count=1)
        self.assertContains(resp, CODE_CELL_PRINT_STR1, count=1)
        self.assertContains(resp, CODE_CELL_PRINT_STR2, count=1)

        nb_html = get_nb_html_from_response(resp)
        for i in range(1, 4):
            self.assertInHTML(CODE_CELL_IN_STR_PATTERN % i, nb_html, count=0)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % "", nb_html, count=4)

    def test_notebook_clear_markdown_and_output(self):
        resp = self.get_page_sandbox_preview_response(QUESTION_MARKUP_CLEAR_ALL)
        self.assertIsValidNbConversion(resp)
        self.assertNotContains(resp, TEXT_CELL_HTML_CLASS)
        self.assertContains(resp, CODE_CELL_HTML_CLASS, count=4)
        self.assertNotContains(resp, FIRST_TITLE_TEXT)
        self.assertNotContains(resp, SECOND_TITLE_TEXT)
        self.assertContains(resp, CODE_CELL_PRINT_STR1, count=1)
        self.assertContains(resp, CODE_CELL_PRINT_STR2, count=1)

        nb_html = get_nb_html_from_response(resp)
        for i in range(1, 4):
            self.assertInHTML(CODE_CELL_IN_STR_PATTERN % i, nb_html, count=0)
        self.assertInHTML(CODE_CELL_IN_STR_PATTERN % "", nb_html, count=4)


# }}}


TEST_SANDBOX_MARK_DOWN_PATTERN = r"""
type: Page
id: test_endraw
content: |
    # Title
    {%% raw %%}\newcommand{\superscript}[1] {\ensuremath{^{\textrm{#1}}}}{%% endraw %%}
    [example1](http://example1.com)
    {%% raw %%}
    value=${#1}
    %s
    [example2](http://example2.com)
"""  # noqa


class YamlJinjaExpansionTest(SingleCoursePageSandboxTestBaseMixin, TestCase):

    # {{{ test https://github.com/inducer/relate/pull/376 which
    # fixed https://github.com/inducer/relate/issues/373

    def test_embedded_raw_block1(self):
        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{% endraw %}"
        expected_literal = (
            r'<p>\newcommand{\superscript}[1] {\ensuremath{^{\textrm{#1}}}}'
            '\n'
            '<a href="http://example1.com">example1</a></p>\n'
            '<p>value=${#1}</p>\n'
            '<p><a href="http://example2.com">example2</a></p>')
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{%endraw%}"
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{%  endraw  %}"
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

    def test_embedded_raw_block2(self):
        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{%- endraw %}"

        expected_literal = (
            r'<p>\newcommand{\superscript}[1] {\ensuremath{^{\textrm{#1}}}}'
            '\n'
            '<a href="http://example1.com">example1</a></p>\n'
            '<p>value=${#1}\n'
            '<a href="http://example2.com">example2</a></p>')
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{%-endraw%}"
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

    def test_embedded_raw_block3(self):
        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{%- endraw -%}"
        expected_literal = (
            r'<p>\newcommand{\superscript}[1] {\ensuremath{^{\textrm{#1}}}}'
            '\n'
            '<a href="http://example1.com">example1</a></p>\n'
            '<p>value=${#1}<a href="http://example2.com">example2</a></p>')
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{%-endraw-%}"
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

    def test_embedded_raw_block4(self):
        markdown = TEST_SANDBOX_MARK_DOWN_PATTERN % "{% endraw -%}"
        expected_literal = (
            r'<p>\newcommand{\superscript}[1] {\ensuremath{^{\textrm{#1}}}}'
            '\n'
            '<a href="http://example1.com">example1</a></p>\n'
            '<p>value=${#1}\n'
            '<a href="http://example2.com">example2</a></p>')
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

    # }}}


class GetCourseCommitShaTest(SingleCourseTestMixin, TestCase):
    # test content.get_course_commit_sha
    def setUp(self):
        super(GetCourseCommitShaTest, self).setUp()
        self.valid_sha = self.course.active_git_commit_sha
        self.new_sha = "some_sha"
        self.course.active_git_commit_sha = self.new_sha
        self.course.save()

    def test_no_participation(self):
        self.assertEqual(
            content.get_course_commit_sha(
                course=self.course, participation=None).decode(), self.new_sha)

    def test_invalid_preview_sha(self):
        invalid_sha = "invalid_sha"
        self.ta_participation.preview_git_commit_sha = invalid_sha
        self.ta_participation.save()

        self.assertEqual(
            content.get_course_commit_sha(
                course=self.course, participation=self.ta_participation).decode(),
            self.new_sha)

    def test_invalid_preview_sha_error_raised(self):
        invalid_sha = "invalid_sha"
        self.ta_participation.preview_git_commit_sha = invalid_sha
        self.ta_participation.save()

        with self.assertRaises(content.CourseCommitSHADoesNotExist) as cm:
            content.get_course_commit_sha(
                course=self.course, participation=self.ta_participation,
                raise_on_nonexistent_preview_commit=True)

        expected_error_msg = ("Preview revision '%s' does not exist--"
                      "showing active course content instead."
                      % invalid_sha)
        self.assertIn(expected_error_msg, str(cm.exception))

    def test_passed_repo_not_none(self):
        with self.get_course_page_context(self.ta_participation.user) as pctx:
            self.assertEqual(
                content.get_course_commit_sha(
                    self.course, self.ta_participation,
                    repo=pctx.repo).decode(), self.course.active_git_commit_sha)

    def test_preview_passed_repo_not_none(self):
        self.ta_participation.preview_git_commit_sha = self.valid_sha
        self.ta_participation.save()

        with self.get_course_page_context(self.ta_participation.user) as pctx:
            self.assertEqual(
                content.get_course_commit_sha(
                    self.course, self.ta_participation,
                    repo=pctx.repo).decode(), self.valid_sha)

    def test_repo_is_subdir_repo(self):
        self.course.course_root_path = "/my_subdir"
        self.course.save()
        self.ta_participation.preview_git_commit_sha = self.valid_sha
        self.ta_participation.save()

        with self.get_course_page_context(self.ta_participation.user) as pctx:
            self.assertEqual(
                content.get_course_commit_sha(
                    self.course, self.ta_participation,
                    repo=pctx.repo).decode(), self.valid_sha)


class GetRepoBlobTest(SingleCourseTestMixin, TestCase):
    # test content.get_repo_blob (for cases not covered by other tests)
    def setUp(self):
        super(GetRepoBlobTest, self).setUp()
        rf = RequestFactory()
        request = rf.get(self.get_course_page_url())
        request.user = self.instructor_participation.user

        from course.utils import CoursePageContext
        self.pctx = CoursePageContext(request, self.course.identifier)

    def test_repo_root_not_allow_tree_key_error(self):
        with self.pctx.repo as repo:
            with self.assertRaises(ObjectDoesNotExist) as cm:
                content.get_repo_blob(
                    repo, "", self.course.active_git_commit_sha.encode(),
                    allow_tree=False)
            expected_error_msg = "repo root is a directory, not a file"
            self.assertIn(expected_error_msg, str(cm.exception))

    def test_access_directory_content_type_error(self):
        full_name = os.path.join("course.yml", "cc.png")
        with self.pctx.repo as repo:
            with self.assertRaises(ObjectDoesNotExist) as cm:
                content.get_repo_blob(
                    repo, full_name, self.course.active_git_commit_sha.encode(),
                    allow_tree=True)
            expected_error_msg = (
                    "resource '%s' is a file, not a directory" % full_name)
            self.assertIn(expected_error_msg, str(cm.exception))

    def test_resource_is_a_directory_error(self):
        full_name = "images"
        with self.pctx.repo as repo:
            with self.assertRaises(ObjectDoesNotExist) as cm:
                content.get_repo_blob(
                    repo, full_name, self.course.active_git_commit_sha.encode(),
                    allow_tree=False)
            expected_error_msg = (
                    "resource '%s' is a directory, not a file" % full_name)
            self.assertIn(expected_error_msg, str(cm.exception))


class GitTemplateLoaderTest(SingleCourseTestMixin, TestCase):
    # test content.GitTemplateLoader
    def setUp(self):
        super(GitTemplateLoaderTest, self).setUp()
        rf = RequestFactory()
        request = rf.get(self.course_page_url)
        request.user = self.instructor_participation.user
        from course.utils import CoursePageContext
        self.pctx = CoursePageContext(request, self.course.identifier)

    def test_object_not_found(self):
        environment = mock.MagicMock()
        template = mock.MagicMock()
        with self.pctx.repo as repo:
            loader = content.GitTemplateLoader(
                repo, self.course.active_git_commit_sha)
            with mock.patch(
                    "course.content.get_repo_blob_data_cached",
                    side_effect=ObjectDoesNotExist):
                with self.assertRaises(content.TemplateNotFound):
                    loader.get_source(environment=environment,
                                      template=template)

    def test_get_source_uptodate(self):
        environment = mock.MagicMock()
        template = mock.MagicMock()
        with self.pctx.repo as repo:
            with mock.patch(
                    "course.content.get_repo_blob_data_cached",
                    return_value=b"blahblah"):
                        loader = content.GitTemplateLoader(
                            repo, self.course.active_git_commit_sha)
                        _, __, uptodate = loader.get_source(environment=environment,
                                                            template=template)
                        self.assertFalse(uptodate())


class YamlBlockEscapingFileSystemLoaderTest(SingleCourseTestMixin, TestCase):
    # test content.YamlBlockEscapingFileSystemLoader
    pass


class GetYamlFromRepoTest(SingleCourseTestMixin, TestCase):
    # test content.get_yaml_from_repo
    def setUp(self):
        super(GetYamlFromRepoTest, self).setUp()
        rf = RequestFactory()
        request = rf.get(self.course_page_url)
        request.user = self.instructor_participation.user
        from course.utils import CoursePageContext
        self.pctx = CoursePageContext(request, self.course.identifier)

    def test_file_uses_tab_in_indentation(self):
        fake_yaml_bytestream = "\tabcd\n".encode()

        class _Blob(object):
            def __init__(self):
                self.data = fake_yaml_bytestream

        with mock.patch("course.content.get_repo_blob") as mock_get_repo_blob:
            mock_get_repo_blob.return_value = _Blob()
            with self.assertRaises(ValueError) as cm:
                with self.pctx.repo as repo:
                    content.get_yaml_from_repo(
                        repo, "course.yml",
                        self.course.active_git_commit_sha.encode())

            expected_error_msg = (
                "File uses tabs in indentation. "
                "This is not allowed.")

            self.assertIn(expected_error_msg, str(cm.exception))


class AttrToStringTest(unittest.TestCase):
    # test content._attr_to_string
    def test(self):
        self.assertEqual(content._attr_to_string("disabled", None), "disabled")
        self.assertEqual(content._attr_to_string(
            "id", "\"abc\""), "id='\"abc\"'")
        self.assertEqual(content._attr_to_string("id", "abc"), "id=\"abc\"")


MARKDOWN_WITH_LINK_FRAGMENT = """
type: Page
id: frag
content: |

    # Test frag in path

    [A static page](staticpage:test#abcd)
    <a href="blablabla">
"""

MARKDOWN_WITH_INVALID_LINK = """
type: Page
id: frag
content: |

    # Test frag in path

    [A static page](course:test#abcd)
"""

MARKDOWN_WITH_URL_STARTS_WITH_COURSE = """
type: Page
id: frag
content: |

    # Test course link

    [A static page](course:another-course)
"""

MARKDOWN_WITH_URL_STARTS_WITH_CALENDAR = """
type: Page
id: frag
content: |

    # Test calendar link

    [A static page](calendar:)
"""

MARKDOWN_WITH_IMG_SRC = """
type: Page
id: frag
content: |

    # Test img with or without src

    ![alt text](https://raw.githubusercontent.com/inducer/relate/master/doc/images/screenshot.png "Example")

    <img src="repo:images/cc.png">
"""  # noqa

MARKDOWN_WITH_OBJECT_DATA = """
type: Page
id: frag
content: |

    # Test object data

    <object width="400" height="400" data="helloworld.swf">
    <object data="repo:images/cc.png">
"""


class LinkFixerTreeprocessorTest(SingleCoursePageSandboxTestBaseMixin, TestCase):
    def test_embedded_raw_block1(self):
        markdown = MARKDOWN_WITH_LINK_FRAGMENT
        expected_literal = [
            '/course/test-course/page/test/#abcd', '<a href="blablabla">']

        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(
            resp, "body", expected_literal, in_bulk=True)

    def test_invalid_relate_url(self):
        markdown = MARKDOWN_WITH_INVALID_LINK
        expected_literal = (
            "data:text/plain;base64,SW52YWxpZCBjaGFyYWN0ZXIgaW4gUkVMQVR"
            "FIFVSTDogY291cnNlOnRlc3QjYWJjZA==")
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(resp, "body", expected_literal)

    def test_url_starts_with_course(self):
        another_course = factories.CourseFactory(identifier="another-course")

        markdown = MARKDOWN_WITH_URL_STARTS_WITH_COURSE
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(
            resp, "body", self.get_course_page_url(another_course.identifier))

    def test_url_starts_with_calendar(self):
        markdown = MARKDOWN_WITH_URL_STARTS_WITH_CALENDAR
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(
            resp, "body", self.get_course_calender_url())

    def test_url_with_object_data(self):
        markdown = MARKDOWN_WITH_OBJECT_DATA
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        self.assertResponseContextContains(
            resp, "body",
            ['data="helloworld.swf"',
             "/course/test-course/file-version/%s/images/cc.png"
             % self.course.active_git_commit_sha], in_bulk=True)

    def test_url_with_img_src(self):
        markdown = MARKDOWN_WITH_IMG_SRC
        resp = self.get_page_sandbox_preview_response(markdown)
        self.assertSandboxHasValidPage(resp)
        expected_value = [
            "https://raw.githubusercontent.com/inducer/relate/master/"
            "doc/images/screenshot.png",
            "/course/test-course/file-version/%s/images/cc.png"
            % self.course.active_git_commit_sha
        ]
        self.assertResponseContextContains(
            resp, "body", expected_value=expected_value, in_bulk=True)

# vim: fdm=marker
