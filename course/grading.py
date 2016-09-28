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
from django.utils.translation import ugettext as _, string_concat
from django.db import connection
from django.db.models import Q
from django.shortcuts import (  # noqa
        get_object_or_404, redirect)
from django.core.exceptions import (  # noqa
        PermissionDenied, SuspiciousOperation,
        ObjectDoesNotExist)
from django import http
from django.urls import reverse

from relate.utils import as_local_time, compact_local_datetime_str
from relate.utils import retry_transaction_decorator


from course.models import (
        FlowSession, FlowPageVisitGrade, FlowPageData,
        get_flow_grading_opportunity,
        get_feedback_for_grade,
        update_bulk_feedback)
from course.constants import (
        #participation_role,
        grade_aggregation_strategy)
from course.utils import (
        course_view, render_course_page,
        get_session_grading_rule,
        FlowPageContext)
from course.flow import get_all_page_data
from course.views import get_now_or_fake_time
from django.conf import settings
from django.utils import translation
from course.constants import (
        participation_permission as pperm,
        )

# {{{ for mypy

from typing import Text, Any, Optional  # noqa
from course.models import (  # noqa
        GradingOpportunity)
from course.utils import (  # noqa
        CoursePageContext)
import datetime  # noqa

# }}}


# {{{ grading driver

@course_view
def grade_flow_page(pctx, flow_session_id, page_ordinal):
    # type: (CoursePageContext, int, int) -> http.HttpResponse
    now_datetime = get_now_or_fake_time(pctx.request)

    page_ordinal = int(page_ordinal)

    viewing_prev_grade = False
    prev_grade_id = pctx.request.GET.get("grade_id")
    if prev_grade_id is not None:
        try:
            prev_grade_id = int(prev_grade_id)
            viewing_prev_grade = True
        except ValueError:
            raise SuspiciousOperation("non-integer passed for 'grade_id'")

    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view grade book"))

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

    assert fpctx.page is not None
    assert fpctx.page_context is not None

    from course.flow import adjust_flow_session_page_data
    adjust_flow_session_page_data(pctx.repo, flow_session,
            pctx.course.identifier, fpctx.flow_desc,
            respect_preview=True)

    grading_rule = get_session_grading_rule(
            flow_session, fpctx.flow_desc, get_now_or_fake_time(pctx.request))

    # {{{ enable flow session zapping

    from time import time
    start = time()
    all_flow_qs = FlowSession.objects.filter(
        course=pctx.course,
        flow_id=flow_session.flow_id,
        participation__isnull=False,
        in_progress=flow_session.in_progress).select_related("user")

    # if pctx.role != participation_role.instructor:
    #     all_flow_qs = all_flow_qs.exclude(
    #         participation__role=participation_role.instructor)

    flow_order_by_list = ['participation__user__username']
    if (grading_rule.grade_aggregation_strategy
            == grade_aggregation_strategy.use_earliest):
        flow_order_by_list.append('-start_time')
    all_flow_qs = all_flow_qs.order_by(*flow_order_by_list)

    if (connection.features.can_distinct_on_fields
        and
        grading_rule.grade_aggregation_strategy in [
                grade_aggregation_strategy.use_earliest,
                grade_aggregation_strategy.use_latest]
        ):
        all_flow_qs = all_flow_qs \
            .distinct('participation__user__username')

    all_flow_sessions = list(all_flow_qs)

    this_flow_page_data = FlowPageData.objects.get(
        flow_session=flow_session, ordinal=page_ordinal)

    page_id = this_flow_page_data.page_id
    group_id = this_flow_page_data.group_id

    # {{{ order pages by page_data

    if getattr(fpctx.page, "grading_sort_by_page_data", False):
        flow_page_data_order_list = ["flow_session__participation__user__username"]
        all_flow_sessions_pks = all_flow_qs.values_list('pk', flat=True)
        all_flow_session_page_data_qs = FlowPageData.objects.filter(
            flow_session__pk__in=all_flow_sessions_pks,
            group_id=group_id,
            page_id = page_id,
        )

        if (grading_rule.grade_aggregation_strategy
                == grade_aggregation_strategy.use_earliest):
            flow_page_data_order_list.append("-flow_session__start_time")
        elif (grading_rule.grade_aggregation_strategy
                  == grade_aggregation_strategy.use_latest):
            flow_page_data_order_list.append("flow_session__start_time")
        all_flow_session_page_data_qs = all_flow_session_page_data_qs.order_by(*flow_page_data_order_list)

        if this_flow_page_data.data:
            # for random generated question, put pages with same page_data.data
            # closer for grading
            all_flow_session_page_data = list(
                all_flow_session_page_data_qs.values_list("data", flat=True))

            # add index to each of the item the resulting queryset so that preserve
            # the ordering of page with the same page_data.data when do the following sorting
            for idx in range(len(all_flow_session_page_data)):
                all_flow_session_page_data[idx] += str(idx)

            # sorting the flowsessions according to the page_data.data
            all_flow_session_page_data, all_flow_sessions = (
                list(t) for t in (
                    zip(*sorted(zip(all_flow_session_page_data, all_flow_sessions)))
                )
            )

    # }}}

    # {{{ session select2
    graded_flow_sessions_json = []
    ungraded_flow_sessions_json = []

    fpvg_flowsession_id_list = []
    fpvg_flowsession_time_list = []
    page_graded_flow_session_list = []
    if fpctx.page.expects_answer():
        fpvg_qs = (
            FlowPageVisitGrade.objects.filter(
                visit__flow_session__course=pctx.course,
                visit__flow_session__flow_id=flow_session.flow_id,
                visit__flow_session__in_progress=False,
                visit__page_data__group_id=group_id,
                visit__page_data__page_id=page_id,

                ## exclude auto grader for non submitting problems
                # grader__isnull=False
            ).order_by(
                "visit__flow_session__participation__user",
                "-grade_time"
            ).select_related(
                "visit__flow_session__participation__user",
                "visit__flow_session"
            )
        )

        if (grading_rule.grade_aggregation_strategy in [
            grade_aggregation_strategy.use_earliest,
            grade_aggregation_strategy.use_latest]):
            fpvg_qs = fpvg_qs.distinct(
                "visit__flow_session__participation__user")

        visit_pk_list = list(fpvg_qs.values_list("pk", flat=True))

        fpvg_qs = fpvg_qs.filter(
            pk__in=visit_pk_list, correctness__isnull=False)

        fpvg_flowsession_id_time_list = (
                list(fpvg_qs
                     .values_list(
                        "visit__flow_session__pk",
                        "grade_time")
                     ))



        fpvg_flowsession_id_time_list.sort(key=lambda (x, y): y)
        fpvg_flowsession_id_list = [v[0] for v in fpvg_flowsession_id_time_list]
        page_graded_flow_session_list = [fs for fs in all_flow_sessions if fs.pk in fpvg_flowsession_id_list]


        fpvg_flowsession_time_list = [v[1] for v in fpvg_flowsession_id_time_list]

    graded_fs_list = []
    if page_graded_flow_session_list is not None:
        graded_fs_list = sorted(page_graded_flow_session_list,
                          key=lambda x: (
                              x.pk in fpvg_flowsession_id_list,
                              fpvg_flowsession_id_list.index(x.pk) if x.pk in fpvg_flowsession_id_list else None
                          ),
                          reverse= True)

    page_ungraded_flow_session_list = list(set(all_flow_sessions) - set(page_graded_flow_session_list))
    ungraded_fs_list = sorted(page_ungraded_flow_session_list,
                      key=lambda x: (
                          x.participation.user.get_full_name()
                      ))

    adjusted_list = graded_fs_list + ungraded_fs_list

    all_flow_sessions_json = []

    for idx, flow_session_idx in enumerate(adjusted_list):
        text = string_concat(
            "%(user_fullname)s",
            " ", _("started at %(start_time)s"),
        ) % {
                   "user_fullname": flow_session_idx.participation \
                       .user.get_full_name(),
                   "start_time": compact_local_datetime_str(
                       as_local_time(flow_session_idx.start_time),
                       get_now_or_fake_time(pctx.request),
                       in_python=True)
               }

        flow_page_data_idx = FlowPageData.objects.get(
            flow_session=flow_session_idx,
            group_id=group_id,
            page_id=page_id)

        uri = reverse("relate-grade_flow_page",
            args=(
                pctx.course.identifier,
                flow_session_idx.id,
                flow_page_data_idx.ordinal))

        grade_time = None

        if fpvg_flowsession_id_list:
            try:
                g_idx = fpvg_flowsession_id_list.index(flow_session_idx.pk)
                grade_time = fpvg_flowsession_time_list[g_idx]
            except ValueError:
                pass

        if grade_time:
            text += (
                    string_concat(", ",
                        _("graded at %(grade_time)s"), ".") %
                    {"grade_time": compact_local_datetime_str(
                        as_local_time(grade_time),
                        get_now_or_fake_time(pctx.request),
                        in_python=True)}
                    )
        else:
            text +="."

        flow_session_json = {
                "id": flow_session_idx.pk,
                "text": text,
                "url": uri,
                }

        if grade_time:
            graded_flow_sessions_json.append(flow_session_json)
        else:
            ungraded_flow_sessions_json.append(flow_session_json)

        if fpctx.page.expects_answer():
            all_flow_sessions_json = [
                {"id":'', "text":''},
                {
                    "id": '',
                    "text": _('Ungraded (by username)'),
                    "children": ungraded_flow_sessions_json
                },
                {
                    "id": '',
                    "text": _('Graded (by grade time)'),
                    "children": graded_flow_sessions_json
                }
            ]
        else:
            all_flow_sessions_json = [{"id":'', "text":''}] + ungraded_flow_sessions_json

    # }}}

    # neet post/get definition and form_to_html

    next_flow_session_id = None
    next_flow_session_ordinal = None
    prev_flow_session_id = None
    prev_flow_session_ordinal = None
    for i, other_flow_session in enumerate(all_flow_sessions):
        if other_flow_session.pk == flow_session.pk:
            if i > 0:
                prev_flow_session_id = all_flow_sessions[i-1].id
                flow_page_data_i = FlowPageData.objects.get(
                    flow_session__id=prev_flow_session_id,
                    group_id=group_id,
                    page_id=page_id)
                prev_flow_session_ordinal = flow_page_data_i.ordinal
            if i + 1 < len(all_flow_sessions):
                next_flow_session_id = all_flow_sessions[i+1].id
                flow_page_data_i = FlowPageData.objects.get(
                    flow_session__id=next_flow_session_id,
                    group_id=group_id,
                    page_id=page_id)
                next_flow_session_ordinal = flow_page_data_i.ordinal

    # }}}

    prev_grades = (FlowPageVisitGrade.objects
            .filter(
                visit__flow_session=flow_session,
                visit__page_data__ordinal=page_ordinal,
                visit__is_submitted_answer=True)
            .order_by("-visit__visit_time", "-grade_time")
            .select_related("visit"))

    # {{{ reproduce student view

    form = None
    feedback = None
    answer_data = None
    grade_data = None
    shown_grade = None

    if fpctx.page.expects_answer():
        if fpctx.prev_answer_visit is not None and prev_grade_id is None:
            answer_data = fpctx.prev_answer_visit.answer

            shown_grade = fpctx.prev_answer_visit.get_most_recent_grade()
            if shown_grade is not None:
                feedback = get_feedback_for_grade(shown_grade)
                grade_data = shown_grade.grade_data
            else:
                feedback = None
                grade_data = None

            prev_grade_id = shown_grade.id

        elif prev_grade_id is not None:
            try:
                shown_grade = prev_grades.filter(id=prev_grade_id).get()
            except ObjectDoesNotExist:
                raise http.Http404()

            feedback = get_feedback_for_grade(shown_grade)
            grade_data = shown_grade.grade_data
            answer_data = shown_grade.visit.answer

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
            and not flow_session.in_progress
            and not viewing_prev_grade):
        request = pctx.request
        if pctx.request.method == "POST":
            if not pctx.has_permission(pperm.assign_grade):
                raise PermissionDenied(_("may not assign grades"))

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

                feedback_json = None  # type: Optional[Dict[Text, Any]]
                bulk_feedback_json = None  # type: Optional[Dict[Text, Any]]

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

                _save_grade(fpctx, flow_session, most_recent_grade,
                        bulk_feedback_json, now_datetime)
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
            flow_session, fpctx.flow_desc, get_now_or_fake_time(pctx.request))

    if grading_rule.grade_identifier is not None:
        grading_opportunity = get_flow_grading_opportunity(
                pctx.course, flow_session.flow_id, fpctx.flow_desc,
                grading_rule.grade_identifier,
                grading_rule.grade_aggregation_strategy
                )  # type: Optional[GradingOpportunity]
    else:
        grading_opportunity = None

    all_page_data = get_all_page_data(flow_session)

    all_page_grade_points= []
    all_expect_grade_page_data = []
    for i, pd in enumerate(all_page_data):
        fpctx_i = FlowPageContext(pctx.repo, pctx.course, flow_session.flow_id,
                                  pd.ordinal, participation=flow_session.participation,
                                flow_session=flow_session, request=pctx.request)
        if fpctx_i.page.expects_answer() and fpctx_i.page.is_answer_gradable():
            all_expect_grade_page_data.append(pd)
            feedback_i = None
            if fpctx_i.prev_answer_visit is not None:
                most_recent_grade_i = fpctx_i.prev_answer_visit.get_most_recent_grade()
                if most_recent_grade_i is not None:
                    feedback_i = get_feedback_for_grade(most_recent_grade_i)
                else:
                    feedback_i = None
                if feedback_i is not None and feedback_i.correctness is not None:
                    all_page_grade_points.append(feedback_i.correctness * 100)
                else:
                    all_page_grade_points.append(None)
            else:
                all_page_grade_points.append(None)

    assert len(all_expect_grade_page_data) == len(all_page_grade_points)

    grade_status_zip = zip(all_expect_grade_page_data, all_page_grade_points)

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
                "grade_status_zip": grade_status_zip,

                "body": fpctx.page.body(
                    fpctx.page_context, fpctx.page_data.data),
                "form": form,
                "form_html": form_html,
                "feedback": feedback,
                "max_points": max_points,
                "points_awarded": points_awarded,
                "shown_grade": shown_grade,
                "prev_grades": prev_grades,
                "prev_grade_id": prev_grade_id,

                "grading_opportunity": grading_opportunity,

                "prev_flow_session_id": prev_flow_session_id,
                'prev_flow_session_ordinal':prev_flow_session_ordinal,
                "next_flow_session_id": next_flow_session_id,
                'next_flow_session_ordinal': next_flow_session_ordinal,
                "all_flow_sessions_json": dumps(all_flow_sessions_json),

                "grading_form": grading_form,
                "grading_form_html": grading_form_html,
                "correct_answer": fpctx.page.correct_answer(
                    fpctx.page_context, fpctx.page_data.data,
                    answer_data, grade_data),
            })


@retry_transaction_decorator()
def _save_grade(
        fpctx,  # type: FlowPageContext
        flow_session,  # type: FlowSession
        most_recent_grade,  # type: FlowPageVisitGrade
        bulk_feedback_json,  # type: Any
        now_datetime,  # type: datetime.datetime
        ):
    # type: (...) -> None
    most_recent_grade.save()

    update_bulk_feedback(
            fpctx.prev_answer_visit.page_data,
            most_recent_grade,
            bulk_feedback_json)

    grading_rule = get_session_grading_rule(
            flow_session, fpctx.flow_desc, now_datetime)

    from course.flow import grade_flow_session
    grade_flow_session(fpctx, flow_session, grading_rule)

# }}}


# {{{ grader statistics

@course_view
def show_grader_statistics(pctx, flow_id):
    if not pctx.has_permission(pperm.view_grader_stats):
        raise PermissionDenied(_("may not view grader stats"))

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
                "pages_stats_counts": list(zip(pages, stats_table, page_counts)),
                "grader_counts": grader_counts,
            })

# }}}

# vim: foldmethod=marker
