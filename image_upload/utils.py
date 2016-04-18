# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2016 Dong Zhuang"

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

from django.contrib.auth.mixins import UserPassesTestMixin

from course.flow import (
        get_page_behavior, get_and_check_flow_session,
        get_prev_answer_visits_qset)
from course.utils import (
        FlowPageContext, get_session_access_rule,
        get_session_grading_rule)
from course.views import get_now_or_fake_time
from course.utils import CoursePageContext

# extracted from course.flow
def get_page_image_behavior(pctx, flow_session_id, ordinal):

    request = pctx.request

    ordinal = int(ordinal)

    flow_session_id = int(flow_session_id)
    flow_session = get_and_check_flow_session(pctx, flow_session_id)
    flow_id = flow_session.flow_id

    fpctx = FlowPageContext(pctx.repo, pctx.course, flow_id, ordinal,
            participation=pctx.participation,
            flow_session=flow_session,
            request=pctx.request)

    now_datetime = get_now_or_fake_time(request)
    access_rule = get_session_access_rule(
            flow_session, pctx.role, fpctx.flow_desc, now_datetime,
            facilities=pctx.request.relate_facilities)

    grading_rule = get_session_grading_rule(
            flow_session, pctx.role, fpctx.flow_desc, now_datetime)
    generates_grade = (
            grading_rule.grade_identifier is not None
            and
            grading_rule.generates_grade)

    del grading_rule

    permissions = fpctx.page.get_modified_permissions_for_page(
            access_rule.permissions)

    answer_visit = None
    prev_visit_id = None

    prev_answer_visits = list(
            get_prev_answer_visits_qset(fpctx.page_data))

    # {{{ fish out previous answer_visit

    prev_visit_id = pctx.request.GET.get("visit_id")
    if prev_visit_id is not None:
        prev_visit_id = int(prev_visit_id)

    viewing_prior_version = False
    if prev_answer_visits and prev_visit_id is not None:
        answer_visit = prev_answer_visits[0]

        for ivisit, pvisit in enumerate(prev_answer_visits):
            if pvisit.id == prev_visit_id:
                answer_visit = pvisit
                if ivisit > 0:
                    viewing_prior_version = True

                break

        prev_visit_id = answer_visit.id

    elif prev_answer_visits:
        answer_visit = prev_answer_visits[0]
        prev_visit_id = answer_visit.id

    else:
        answer_visit = None

    # }}}

    if answer_visit is not None:
        answer_was_graded = answer_visit.is_submitted_answer
    else:
        answer_was_graded = False

    page_behavior = get_page_behavior(
            page=fpctx.page,
            permissions=permissions,
            session_in_progress=flow_session.in_progress,
            answer_was_graded=answer_was_graded,
            generates_grade=generates_grade,
            is_unenrolled_session=flow_session.participation is None,
            viewing_prior_version=viewing_prior_version)

    return page_behavior


class ImageOperationMixin(UserPassesTestMixin):
    # Mixin for determin if user can upload/delete/modify image in flow_page
    raise_exception = True

    def test_func(self):
        print self.request
        request = self.request
        flow_session_id = self.kwargs['flow_session_id']
        ordinal = self.kwargs['ordinal']
        course_identifier = self.kwargs['course_identifier']

        pctx = CoursePageContext(request, course_identifier)
        
        try:
            return get_page_image_behavior(pctx, flow_session_id, ordinal).may_change_answer
        except ValueError:
            return True
