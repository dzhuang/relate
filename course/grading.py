# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2014 Andreas Kloeckner"

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


from django.utils.translation import ugettext as _
from django.shortcuts import (  # noqa
        get_object_or_404, redirect)
from relate.utils import retry_transaction_decorator
from django.core.exceptions import (  # noqa
        PermissionDenied, SuspiciousOperation,
        ObjectDoesNotExist)
from django import http

from course.models import (
        FlowSession, FlowPageVisitGrade,
        get_flow_grading_opportunity,
        get_feedback_for_grade,
        update_bulk_feedback)
from course.constants import participation_role
from course.utils import (
        course_view, render_course_page,
        get_session_grading_rule,
        FlowPageContext)
from course.views import get_now_or_fake_time
from django.conf import settings
from django.utils import translation


# {{{ grading driver

from django_select2.forms import Select2Widget
from relate.utils import StyledForm
from crispy_forms.layout import Submit
from django import forms

class FlowSessionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        user = obj.user
        return (
                _("%(user_email)s - %(user_lastname)s, "
                    "%(user_firstname)s")
                % {
                    "user_email": user.email,
                    "user_lastname": user.last_name,
                    "user_firstname": user.first_name})

class GradingFlowSessionSelectForm(StyledForm):
    def __init__(self, pctx, flow_session, *args, **kwargs):
        super(GradingFlowSessionSelectForm, self).__init__(*args, **kwargs)

        self.fields["sessions"] = FlowSessionChoiceField(
                queryset=(FlowSession.objects
                    .filter(
                        course=pctx.course,
                        flow_id=flow_session.flow_id,
                        participation__isnull=False,
                        in_progress=flow_session.in_progress)
                    .order_by(
                        "participation__user__last_name",
                        "start_time")),
                required=True,
                help_text=_("Select session."),
                label=_("Arbitary session"),
                widget=Select2Widget())

        self.helper.add_input(
                Submit("go","go"))

@course_view
@retry_transaction_decorator()
def grade_flow_page(pctx, flow_session_id, page_ordinal):
    page_ordinal = int(page_ordinal)

    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied(
                _("must be instructor or TA to view grades"))

    flow_session = get_object_or_404(FlowSession, id=int(flow_session_id))

    if flow_session.course.pk != pctx.course.pk:
        raise SuspiciousOperation(
                _("Flow session not part of specified course"))
    if flow_session.participation is None:
        raise SuspiciousOperation(
                _("Cannot grade anonymous session"))

    fpctx = FlowPageContext(pctx.repo, pctx.course, flow_session.flow_id,
            page_ordinal, participation=flow_session.participation,
            flow_session=flow_session, request=pctx.request)

    if fpctx.page_desc is None:
        raise http.Http404()

    # {{{ enable flow session zapping

    all_flow_sessions = list(FlowSession.objects
            .filter(
                course=pctx.course,
                flow_id=flow_session.flow_id,
                participation__isnull=False,
                in_progress=flow_session.in_progress)
            .order_by(
                "participation__user__last_name",
                "start_time"))
    
    # {{{ session select2 
    all_flow_sessions_json = []

    from django.core.urlresolvers import reverse
    for flowsession in all_flow_sessions:
        uri = reverse("relate-grade_flow_page",
            args=(
                pctx.course.identifier,
                flowsession.id,
                fpctx.page_data.ordinal))

        flowsession_json = {
                "id": flowsession.pk,
                "text": "%(userfullname)s (%(email)s) started at %(start_time)s"  % {"userfullname": flowsession.participation.user.get_full_name(), "email": flowsession.participation.user.email,  "start_time": flowsession.start_time},
                "url": uri,
                }
        all_flow_sessions_json.append(flowsession_json)
    # }}}
    
    # neet post/get definition and form_to_html

    next_flow_session_id = None
    prev_flow_session_id = None
    for i, other_flow_session in enumerate(all_flow_sessions):
        if other_flow_session.pk == flow_session.pk:
            if i > 0:
                prev_flow_session_id = all_flow_sessions[i-1].id
            if i + 1 < len(all_flow_sessions):
                next_flow_session_id = all_flow_sessions[i+1].id

    # }}}

    # {{{ reproduce student view

    form = None
    feedback = None
    answer_data = None
    grade_data = None
    most_recent_grade = None

    if fpctx.page.expects_answer():
        if fpctx.prev_answer_visit is not None:
            answer_data = fpctx.prev_answer_visit.answer

            most_recent_grade = fpctx.prev_answer_visit.get_most_recent_grade()
            if most_recent_grade is not None:
                feedback = get_feedback_for_grade(most_recent_grade)
                grade_data = most_recent_grade.grade_data
            else:
                feedback = None
                grade_data = None

        else:
            feedback = None

        from course.page.base import PageBehavior
        page_behavior = PageBehavior(
                show_correctness=True,
                show_answer=False,
                may_change_answer=False)

        form = fpctx.page.make_form(
                fpctx.page_context, fpctx.page_data.data,
                answer_data, page_behavior)

    if form is not None:
        form_html = fpctx.page.form_to_html(
                pctx.request, fpctx.page_context, form, answer_data)
    else:
        form_html = None

    # }}}

    # {{{ grading form

    if (fpctx.page.expects_answer()
            and fpctx.page.is_answer_gradable()
            and fpctx.prev_answer_visit is not None
            and not flow_session.in_progress):
        request = pctx.request
        if pctx.request.method == "POST":
            grading_form = fpctx.page.post_grading_form(
                    fpctx.page_context, fpctx.page_data, grade_data,
                    request.POST, request.FILES)
            if grading_form.is_valid():
                grade_data = fpctx.page.update_grade_data_from_grading_form(
                        fpctx.page_context, fpctx.page_data, grade_data,
                        grading_form, request.FILES)

                with translation.override(settings.RELATE_ADMIN_EMAIL_LOCALE):
                    feedback = fpctx.page.grade(
                            fpctx.page_context, fpctx.page_data,
                            answer_data, grade_data)

                if feedback is not None:
                    correctness = feedback.correctness
                else:
                    correctness = None

                if feedback is not None:
                    feedback_json, bulk_feedback_json = feedback.as_json()
                else:
                    feedback_json = bulk_feedback_json = None

                most_recent_grade = FlowPageVisitGrade(
                        visit=fpctx.prev_answer_visit,
                        grader=pctx.request.user,
                        graded_at_git_commit_sha=pctx.course_commit_sha,

                        grade_data=grade_data,

                        max_points=fpctx.page.max_points(fpctx.page_data),
                        correctness=correctness,
                        feedback=feedback_json)

                most_recent_grade.save()

                update_bulk_feedback(
                        fpctx.prev_answer_visit.page_data,
                        most_recent_grade,
                        bulk_feedback_json)

                grading_rule = get_session_grading_rule(
                        flow_session, flow_session.participation.role,
                        fpctx.flow_desc, get_now_or_fake_time(request))

                from course.flow import grade_flow_session
                grade_flow_session(fpctx, flow_session, grading_rule)

        else:
            grading_form = fpctx.page.make_grading_form(
                    fpctx.page_context, fpctx.page_data, grade_data)

    else:
        grading_form = None

    if grading_form is not None:
        from crispy_forms.layout import Submit
        grading_form.helper.form_class += " relate-grading-form"
        grading_form.helper.add_input(
                Submit(
                    "submit", _("Submit"),
                    accesskey="s",
                    css_class="relate-grading-save-button"))

        grading_form_html = fpctx.page.grading_form_to_html(
                pctx.request, fpctx.page_context, grading_form, grade_data)

    else:
        grading_form_html = None

    # }}}

    # {{{ compute points_awarded

    max_points = None
    points_awarded = None
    if (fpctx.page.expects_answer()
            and fpctx.page.is_answer_gradable()):
        max_points = fpctx.page.max_points(fpctx.page_data)
        if feedback is not None and feedback.correctness is not None:
            points_awarded = max_points * feedback.correctness

    # }}}

    grading_rule = get_session_grading_rule(
            flow_session, flow_session.participation.role,
            fpctx.flow_desc, get_now_or_fake_time(pctx.request))

    if grading_rule.grade_identifier is not None:
        grading_opportunity = get_flow_grading_opportunity(
                pctx.course, flow_session.flow_id, fpctx.flow_desc,
                grading_rule)
    else:
        grading_opportunity = None

    from json import dumps
    return render_course_page(
            pctx,
            "course/grade-flow-page.html",
            {
                "flow_identifier": fpctx.flow_id,
                "flow_session": flow_session,
                "flow_desc": fpctx.flow_desc,
                "ordinal": fpctx.ordinal,
                "page_data": fpctx.page_data,

                "body": fpctx.page.body(
                    fpctx.page_context, fpctx.page_data.data),
                "form": form,
                "form_html": form_html,
                #"select_flow_session_form": select_flow_session_form,
                "feedback": feedback,
                "max_points": max_points,
                "points_awarded": points_awarded,
                "most_recent_grade": most_recent_grade,

                "grading_opportunity": grading_opportunity,

                "prev_flow_session_id": prev_flow_session_id,
                "next_flow_session_id": next_flow_session_id,
                "all_flow_sessions_json": dumps(all_flow_sessions_json),

                "grading_form": grading_form,
                "grading_form_html": grading_form_html,
            
            })

# }}}


# {{{ grading statistics

@course_view
def show_grading_statistics(pctx, flow_id):
    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied(
                _("must be instructor or TA to view grading stats"))

    grades = (FlowPageVisitGrade.objects
            .filter(
                visit__flow_session__course=pctx.course,
                visit__flow_session__flow_id=flow_id,

                # There are just way too many autograder grades, which makes this
                # report super slow.
                grader__isnull=False)
            .order_by(
                "visit__id",
                "grade_time")
            .select_related("visit")
            .select_related("grader")
            .select_related("visit__page_data"))

    graders = set()

    # tuples: (ordinal, id)
    pages = set()

    counts = {}
    grader_counts = {}
    page_counts = {}

    def commit_grade_info(grade):
        grader = grade.grader
        page = (grade.visit.page_data.ordinal,
                grade.visit.page_data.group_id + "/" + grade.visit.page_data.page_id)

        graders.add(grader)
        pages.add(page)

        key = (page, grade.grader)
        counts[key] = counts.get(key, 0) + 1

        grader_counts[grader] = grader_counts.get(grader, 0) + 1
        page_counts[page] = page_counts.get(page, 0) + 1

    last_grade = None

    for grade in grades.iterator():
        if last_grade is not None and last_grade.visit != grade.visit:
            commit_grade_info(last_grade)

        last_grade = grade

    if last_grade is not None:
        commit_grade_info(last_grade)

    graders = sorted(graders,
            key=lambda grader: grader.last_name if grader is not None else None)
    pages = sorted(pages)

    stats_table = [
            [
                counts.get((page, grader), 0)
                for grader in graders
                ]
            for page in pages
            ]
    page_counts = [
            page_counts.get(page, 0)
            for page in pages
            ]
    grader_counts = [
            grader_counts.get(grader, 0)
            for grader in graders
            ]

    return render_course_page(
            pctx,
            "course/grading-statistics.html",
            {
                "flow_id": flow_id,
                "pages": pages,
                "graders": graders,
                "pages_stats_counts": zip(pages, stats_table, page_counts),
                "grader_counts": grader_counts,
            })

# }}}

# vim: foldmethod=marker
