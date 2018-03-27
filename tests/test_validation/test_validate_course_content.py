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

import stat
import hashlib
from dulwich.repo import Tree

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from relate.utils import dict_to_struct

from course import validation
from course.validation import ValidationError
from course.content import get_yaml_from_repo, get_repo_blob, load_yaml
from course.validation import get_yaml_from_repo_safely

from tests import factories
from tests.base_test_mixins import CoursesTestMixinBase
from tests.utils import mock

events_file = "events.yml"
my_events_file = "my_events_file.yml"
course_file = "test_course_file"
validate_sha = "test_validate_sha"


def get_yaml_from_repo_side_effect(repo, full_name, commit_sha, cached=True):
    if full_name == events_file:
        return dict_to_struct(
            {"event_kinds": dict_to_struct({
                "lecture": dict_to_struct({
                    "title": "Lecture {nr}",
                    "color": "blue"
                })}),
                "events": dict_to_struct({
                    "lecture 1": dict_to_struct({
                        "title": "l1"})
                })})
    else:
        return get_yaml_from_repo(repo, full_name, commit_sha, cached)


def get_yaml_from_repo_no_events_file_side_effect(
        repo, full_name, commit_sha, cached=True):
    if full_name in [events_file, my_events_file]:
        raise ObjectDoesNotExist
    else:
        return get_yaml_from_repo(repo, full_name, commit_sha, cached)


FLOW1_WITHOUT_RULE_YAML = """
title: "Flow 1 without rule"
description: |
    # Linear Algebra Recap

pages:

-
    type: Page
    id: intro
    content: |

        # Hello World

"""

FLOW1_WITH_ACCESS_RULE_YAML = """
title: "Flow 1 with access rule"
description: |
    # Linear Algebra Recap

rules:
    access:
    -
        if_has_role: [student, ta, instructor]
        permissions: [view]

    grade_identifier: null

pages:

-
    type: Page
    id: intro
    content: |

        # Hello World

"""

FLOW2_WITH_GRADING_RULE_YAML = """
title: "RELATE Test Quiz1"
description: |

    # RELATE Test Quiz

rules:
    grade_identifier: la_quiz
    grade_aggregation_strategy: use_latest

    grading:
    -
        credit_percent: 100

groups:
-
    id: quiz_start
    shuffle: False
    pages:
    -
        type: TextQuestion
        id: half
        value: 5
        prompt: |

          # A half

          What's a half?

        answers:

          - type: float
            value: 0.5
            rtol: 1e-4
          - <plain>half
          - <plain>a half

"""

FLOW3_WITH_GRADING_RULE_YAML = """
title: "RELATE Test Quiz1"
description: |

    # RELATE Test Quiz

rules:
    grade_identifier: la_quiz2
    grade_aggregation_strategy: use_latest

    grading:
    -
        credit_percent: 100

groups:
-
    id: quiz_start
    shuffle: False
    pages:
    -
        type: TextQuestion
        id: half
        value: 5
        prompt: |

          # A half

          What's a half?

        answers:

          - type: float
            value: 0.5
            rtol: 1e-4
          - <plain>half
          - <plain>a half

"""

FLOW3_WITH_GRADING_RULE_WITH_SAME_GID_AS_FLOW2_YAML = """
title: "RELATE Test Quiz1"
description: |

    # RELATE Test Quiz

rules:
    grade_identifier: la_quiz
    grade_aggregation_strategy: use_latest

    grading:
    -
        credit_percent: 100

groups:
-
    id: quiz_start
    shuffle: False
    pages:
    -
        type: TextQuestion
        id: half
        value: 5
        prompt: |

          # A half

          What's a half?

        answers:

          - type: float
            value: 0.5
            rtol: 1e-4
          - <plain>half
          - <plain>a half

"""


def get_yaml_from_repo_safely_side_effect(repo, full_name, commit_sha):
    if full_name == course_file:
        return "faked_course_desc"
    if full_name == "flows/flow1.yml":
        return dict_to_struct(load_yaml(FLOW1_WITHOUT_RULE_YAML))
    if full_name == "flows/flow2.yml":
        return dict_to_struct(load_yaml(FLOW2_WITH_GRADING_RULE_YAML))
    if full_name == "flows/flow3.yml":
        return dict_to_struct(load_yaml(FLOW3_WITH_GRADING_RULE_YAML))

    if full_name.startswith("staticpages/"):
        return "faked_staticpages"
    else:
        return get_yaml_from_repo_safely(repo, full_name, commit_sha)


def get_yaml_from_repo_safely_with_duplicate_grade_identifier_side_effect(
        repo, full_name, commit_sha):
    if full_name == course_file:
        return "faked_course_desc"
    if full_name == "flows/flow1.yml":
        return dict_to_struct(load_yaml(FLOW1_WITH_ACCESS_RULE_YAML))
    if full_name == "flows/flow2.yml":
        return dict_to_struct(load_yaml(FLOW2_WITH_GRADING_RULE_YAML))
    if full_name == "flows/flow3.yml":
        return dict_to_struct(load_yaml(
            FLOW3_WITH_GRADING_RULE_WITH_SAME_GID_AS_FLOW2_YAML))

    if full_name.startswith("staticpages/"):
        return "faked_staticpages"
    else:
        return get_yaml_from_repo_safely(repo, full_name, commit_sha)


def get_repo_blob_side_effect(repo, full_name, commit_sha, allow_tree=True):
    if full_name == "media" and allow_tree:
        raise ObjectDoesNotExist()
    if full_name == "flows" and allow_tree:
        tree = Tree()
        tree.add(b"not_a_flow", stat.S_IFDIR,
                 hashlib.sha224(b"not a flow").hexdigest().encode())
        tree.add(b"flow1.yml", stat.S_IFDIR,
                 hashlib.sha224(b"a flow").hexdigest().encode())
        tree.add(b"flow2.yml", stat.S_IFDIR,
                 hashlib.sha224(b"another flow").hexdigest().encode())
        tree.add(b"flow3.yml", stat.S_IFDIR,
                 hashlib.sha224(b"yet another flow").hexdigest().encode())
        return tree
    if full_name == "staticpages":
        tree = Tree()
        tree.add(b"not_a_page", stat.S_IFDIR,
                 hashlib.sha224(b"not a page").hexdigest().encode())
        tree.add(b"spage1.yml", stat.S_IFDIR,
                 hashlib.sha224(b"a static page").hexdigest().encode())
        return tree
    if full_name == "":
        return Tree()

    return get_repo_blob(repo, full_name, commit_sha, allow_tree)


def get_repo_blob_side_effect1(repo, full_name, commit_sha, allow_tree=True):
    if full_name == "media" and allow_tree:
        tree = Tree()
        tree.add(name=b"media",
                 mode=stat.S_IFDIR,
                 hexsha=hashlib.sha224(b"some media").hexdigest().encode())
        return tree
    if full_name == "flows" and allow_tree:
        tree = Tree()
        tree.add(b"not_a_flow", stat.S_IFDIR,
                 hashlib.sha224(b"not a flow").hexdigest().encode())
        tree.add(b"flow1.yml", stat.S_IFDIR,
                 hashlib.sha224(b"a flow").hexdigest().encode())
        return tree
    if full_name == "staticpages":
        tree = Tree()
        tree.add(b"not_a_page", stat.S_IFDIR,
                 hashlib.sha224(b"not a page").hexdigest().encode())
        tree.add(b"spage1.yml", stat.S_IFDIR,
                 hashlib.sha224(b"a static page").hexdigest().encode())
        return tree
    if full_name == "":
        return Tree()

    return get_repo_blob(repo, full_name, commit_sha, allow_tree)


def get_repo_blob_side_effect2(repo, full_name, commit_sha, allow_tree=True):
    if full_name == "media" and allow_tree:
        raise ObjectDoesNotExist()
    if full_name == "flows" and allow_tree:
        raise ObjectDoesNotExist()
    if full_name == "staticpages":
        tree = Tree()
        tree.add(b"not_a_page", stat.S_IFDIR,
                 hashlib.sha224(b"not a page").hexdigest().encode())
        tree.add(b"spage1.yml", stat.S_IFDIR,
                 hashlib.sha224(b"a static page").hexdigest().encode())
        return tree
    if full_name == "":
        return Tree()

    return get_repo_blob(repo, full_name, commit_sha, allow_tree)


def get_repo_blob_side_effect3(repo, full_name, commit_sha, allow_tree=True):
    if full_name == "media" and allow_tree:
        raise ObjectDoesNotExist()
    if full_name == "flows" and allow_tree:
        tree = Tree()
        tree.add(b"not_a_flow", stat.S_IFDIR,
                 hashlib.sha224(b"not a flow").hexdigest().encode())
        tree.add(b"flow1.yml", stat.S_IFDIR,
                 hashlib.sha224(b"a flow").hexdigest().encode())
        return tree
    if full_name == "staticpages":
        raise ObjectDoesNotExist()
    if full_name == "":
        return Tree()

    return get_repo_blob(repo, full_name, commit_sha, allow_tree)


class ValidateCourseContentTest(CoursesTestMixinBase, TestCase):
    # test validation.validate_course_content

    def setUp(self):
        self.repo = mock.MagicMock()

        self.course = factories.CourseFactory()

        self.vctx = validation.ValidationContext(self.repo, "some_sha", self.course)

        fake_get_yaml_from_repo_safely = mock.patch(
            "course.validation.get_yaml_from_repo_safely")
        self.mock_get_yaml_from_repo_safely = fake_get_yaml_from_repo_safely.start()
        self.mock_get_yaml_from_repo_safely.side_effect = (
            get_yaml_from_repo_safely_side_effect)
        self.addCleanup(fake_get_yaml_from_repo_safely.stop)

        fake_validate_staticpage_desc = mock.patch(
            "course.validation.validate_staticpage_desc")
        self.mock_validate_staticpage_desc = fake_validate_staticpage_desc.start()
        self.addCleanup(fake_validate_staticpage_desc.stop)

        fake_get_yaml_from_repo = mock.patch(
            "course.content.get_yaml_from_repo")
        self.mock_get_yaml_from_repo = fake_get_yaml_from_repo.start()
        self.mock_get_yaml_from_repo.side_effect = get_yaml_from_repo_side_effect
        self.addCleanup(fake_get_yaml_from_repo.stop)

        fake_validate_calendar_desc_struct = mock.patch(
            "course.validation.validate_calendar_desc_struct"
        )
        self.mock_validate_calendar_desc_struct = (
            fake_validate_calendar_desc_struct.start())
        self.addCleanup(fake_validate_calendar_desc_struct.stop)

        fake_check_attributes_yml = (
            mock.patch("course.validation.check_attributes_yml"))
        self.mock_check_attributes_yml = fake_check_attributes_yml.start()
        self.addCleanup(fake_check_attributes_yml.stop)

        fake_validate_flow_id = (
            mock.patch("course.validation.validate_flow_id"))
        self.mock_validate_flow_id = fake_validate_flow_id.start()
        self.addCleanup(fake_validate_flow_id.stop)

        fake_validate_flow_desc = (
            mock.patch("course.validation.validate_flow_desc"))
        self.mock_validate_flow_desc = fake_validate_flow_desc.start()
        self.addCleanup(fake_validate_flow_desc.stop)

        fake_check_for_page_type_changes = (
            mock.patch("course.validation.check_for_page_type_changes"))
        self.mock_check_for_page_type_changes = (
            fake_check_for_page_type_changes.start())
        self.addCleanup(fake_check_for_page_type_changes.stop)

        fake_check_grade_identifier_link = (
            mock.patch("course.validation.check_grade_identifier_link"))
        self.mock_check_grade_identifier_link = (
            fake_check_grade_identifier_link.start())
        self.addCleanup(fake_check_grade_identifier_link.stop)

        fake_get_repo_blob = (
            mock.patch("course.validation.get_repo_blob"))
        self.mock_get_repo_blob = fake_get_repo_blob.start()
        self.mock_get_repo_blob.side_effect = get_repo_blob_side_effect
        self.addCleanup(fake_get_repo_blob.stop)

        fake_validate_static_page_name = (
            mock.patch("course.validation.validate_static_page_name"))
        self.mock_validate_static_page_name = fake_validate_static_page_name.start()
        self.addCleanup(fake_validate_static_page_name.stop)

        fake_vctx_add_warning = (
            mock.patch("course.validation.ValidationContext.add_warning"))
        self.mock_vctx_add_warning = fake_vctx_add_warning.start()
        self.addCleanup(fake_vctx_add_warning.stop)

    def test_course_none(self):
        validation.validate_course_content(
            self.repo, course_file, events_file, validate_sha, course=None)
        self.assertEqual(self.mock_vctx_add_warning.call_count, 0)

        # validate_staticpage_desc call to validate course_page, and a staticpage
        self.assertEqual(self.mock_validate_staticpage_desc.call_count, 2)

        # validate_calendar_desc_struct is called
        self.assertEqual(self.mock_validate_calendar_desc_struct.call_count, 1)

        # check_attributes_yml is called
        self.assertEqual(self.mock_check_attributes_yml.call_count, 1)

        # validate_flow_id is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_id.call_count, 3)

        # validate_flow_desc is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_desc.call_count, 3)

        # check_grade_identifier_link is not called, because course is None
        self.assertEqual(self.mock_check_grade_identifier_link.call_count, 0)

        # check_for_page_type_changes is not called, because course is None
        self.assertEqual(self.mock_check_for_page_type_changes.call_count, 0)

        # validate_static_page_name is called once for one static page
        self.assertEqual(self.mock_validate_static_page_name.call_count, 1)

    def test_course_not_none(self):
        validation.validate_course_content(
            self.repo, course_file, events_file, validate_sha, course=self.course)
        self.assertEqual(self.mock_vctx_add_warning.call_count, 0)

        # validate_staticpage_desc call to validate course_page, and a staticpage
        self.assertEqual(self.mock_validate_staticpage_desc.call_count, 2)

        # validate_calendar_desc_struct is called
        self.assertEqual(self.mock_validate_calendar_desc_struct.call_count, 1)

        # check_attributes_yml is called
        self.assertEqual(self.mock_check_attributes_yml.call_count, 1)

        # validate_flow_id is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_id.call_count, 3)

        # validate_flow_desc is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_desc.call_count, 3)

        # check_grade_identifier_link is call twice, only 2 flow
        # has grade_identifier
        self.assertEqual(self.mock_check_grade_identifier_link.call_count, 2)

        # check_for_page_type_changes is called 3 times for 3 flows
        self.assertEqual(self.mock_check_for_page_type_changes.call_count, 3)

        # validate_static_page_name is called once for one static page
        self.assertEqual(self.mock_validate_static_page_name.call_count, 1)

    def test_course_custom_events_file_does_not_exist(self):
        self.mock_get_yaml_from_repo.side_effect = (
            get_yaml_from_repo_no_events_file_side_effect)
        validation.validate_course_content(
            self.repo, course_file, "my_events_file.yml", validate_sha,
            course=self.course)
        self.assertEqual(self.mock_vctx_add_warning.call_count, 1)
        expected_warn_msg = (
            "Your course repository does not have an events "
            "file named 'my_events_file.yml'.")

        self.assertIn(expected_warn_msg, self.mock_vctx_add_warning.call_args[0])

        # validate_staticpage_desc call to validate course_page, and a staticpage
        self.assertEqual(self.mock_validate_staticpage_desc.call_count, 2)

        # validate_calendar_desc_struct is not called
        self.assertEqual(self.mock_validate_calendar_desc_struct.call_count, 0)

        # check_attributes_yml is called
        self.assertEqual(self.mock_check_attributes_yml.call_count, 1)

        # validate_flow_id is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_id.call_count, 3)

        # validate_flow_desc is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_desc.call_count, 3)

        # check_for_page_type_changes is called 3 times for 3 flows
        self.assertEqual(self.mock_check_for_page_type_changes.call_count, 3)

        # validate_static_page_name is called once for one static page
        self.assertEqual(self.mock_validate_static_page_name.call_count, 1)

    def test_course_no_events_file(self):
        self.mock_get_yaml_from_repo.side_effect = (
            get_yaml_from_repo_no_events_file_side_effect)
        validation.validate_course_content(
            self.repo, course_file, events_file, validate_sha, course=self.course)
        self.assertEqual(self.mock_vctx_add_warning.call_count, 0)

        # validate_staticpage_desc call to validate course_page, and a staticpage
        self.assertEqual(self.mock_validate_staticpage_desc.call_count, 2)

        # validate_calendar_desc_struct is not called
        self.assertEqual(self.mock_validate_calendar_desc_struct.call_count, 0)

        # check_attributes_yml is called
        self.assertEqual(self.mock_check_attributes_yml.call_count, 1)

        # validate_flow_id is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_id.call_count, 3)

        # validate_flow_desc is called 3 times, for 3 flow files
        self.assertEqual(self.mock_validate_flow_desc.call_count, 3)

        # check_for_page_type_changes is called 3 times for 3 flows
        self.assertEqual(self.mock_check_for_page_type_changes.call_count, 3)

        # validate_static_page_name is called once for one static page
        self.assertEqual(self.mock_validate_static_page_name.call_count, 1)

    def test_get_repo_blob_media_dir_not_empty(self):
        self.mock_get_repo_blob.side_effect = get_repo_blob_side_effect1
        validation.validate_course_content(
            self.repo, course_file, events_file, validate_sha, course=self.course)
        self.assertEqual(self.mock_vctx_add_warning.call_count, 1)

        expected_warn_msg = (
            "Your course repository has a 'media/' directory. Linking to "
            "media files using 'media:' is discouraged. Use the 'repo:' "
            "and 'repocur:' linkng schemes instead.")

        self.assertIn(expected_warn_msg, self.mock_vctx_add_warning.call_args[0])

        # validate_staticpage_desc call to validate course_page, and a staticpage
        self.assertEqual(self.mock_validate_staticpage_desc.call_count, 2)

        # validate_calendar_desc_struct is called
        self.assertEqual(self.mock_validate_calendar_desc_struct.call_count, 1)

        # check_attributes_yml is called
        self.assertEqual(self.mock_check_attributes_yml.call_count, 1)

        # validate_flow_id is called once, there's only 1 flow file
        self.assertEqual(self.mock_validate_flow_id.call_count, 1)

        # validate_flow_desc is called once, there's only 1 flow file
        self.assertEqual(self.mock_validate_flow_desc.call_count, 1)

        # check_for_page_type_changes is called once, there's only 1 flow file
        self.assertEqual(self.mock_check_for_page_type_changes.call_count, 1)

        # validate_static_page_name is called once for one static page
        self.assertEqual(self.mock_validate_static_page_name.call_count, 1)

    def test_get_repo_blob_flows_dir_empty(self):
        self.mock_get_repo_blob.side_effect = get_repo_blob_side_effect2
        validation.validate_course_content(
            self.repo, course_file, events_file, validate_sha, course=self.course)
        self.assertEqual(self.mock_vctx_add_warning.call_count, 0)

        # validate_staticpage_desc call to validate course_page, and a staticpage
        self.assertEqual(self.mock_validate_staticpage_desc.call_count, 2)

        # validate_calendar_desc_struct is called
        self.assertEqual(self.mock_validate_calendar_desc_struct.call_count, 1)

        # check_attributes_yml is called
        self.assertEqual(self.mock_check_attributes_yml.call_count, 1)

        # validate_flow_id is not called, because no flow files
        self.assertEqual(self.mock_validate_flow_id.call_count, 0)

        # validate_flow_desc is not called, because no flow files
        self.assertEqual(self.mock_validate_flow_desc.call_count, 0)

        # check_for_page_type_changes is not called, because no flow files
        self.assertEqual(self.mock_check_for_page_type_changes.call_count, 0)

        # validate_static_page_name is called once for one static page
        self.assertEqual(self.mock_validate_static_page_name.call_count, 1)

    def test_get_repo_blob_staticpages_empty(self):
        self.mock_get_repo_blob.side_effect = get_repo_blob_side_effect3
        validation.validate_course_content(
            self.repo, course_file, events_file, validate_sha, course=self.course)
        self.assertEqual(self.mock_vctx_add_warning.call_count, 0)

        # validate_staticpage_desc call to validate course_page only
        self.assertEqual(self.mock_validate_staticpage_desc.call_count, 1)

        # validate_calendar_desc_struct is called
        self.assertEqual(self.mock_validate_calendar_desc_struct.call_count, 1)

        # check_attributes_yml is called
        self.assertEqual(self.mock_check_attributes_yml.call_count, 1)

        # validate_flow_id is called 3 times, there's only 1 flow file
        self.assertEqual(self.mock_validate_flow_id.call_count, 1)

        # validate_flow_desc is called once, there's only 1 flow file
        self.assertEqual(self.mock_validate_flow_desc.call_count, 1)

        # check_for_page_type_changes is called once, there's only 1 flow file
        self.assertEqual(self.mock_check_for_page_type_changes.call_count, 1)

        # validate_static_page_name is not called, no static page
        self.assertEqual(self.mock_validate_static_page_name.call_count, 0)

    def test_duplicated_grade_identifier(self):
        self.mock_get_yaml_from_repo_safely.side_effect = (
            get_yaml_from_repo_safely_with_duplicate_grade_identifier_side_effect
        )
        with self.assertRaises(ValidationError) as cm:
            validation.validate_course_content(
                self.repo, course_file, events_file, validate_sha,
                course=self.course)

        expected_error_msg = ("flows/flow3.yml: flow uses the same "
                              "grade_identifier as another flow")
        self.assertIn(expected_error_msg, str(cm.exception))
        self.assertEqual(self.mock_vctx_add_warning.call_count, 0)
