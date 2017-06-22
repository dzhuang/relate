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


from django.utils.translation import ugettext as _, string_concat
from django.db import connection
from django.shortcuts import (  # noqa
        get_object_or_404, redirect)
from relate.utils import retry_transaction_decorator
from django.contrib import messages
from django.core.exceptions import (  # noqa
        PermissionDenied, SuspiciousOperation,
        ObjectDoesNotExist)
from django import http

from relate.utils import as_local_time, compact_local_datetime_str

from course.models import (
        Participation, FlowPageData, FlowPageVisit,
        FlowSession, FlowPageVisitGrade,
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
from course.page import InvalidPageData

from django.conf import settings
from django.utils import translation
from course.constants import (
        participation_permission as pperm,
        )

# {{{ for mypy

if False:
    from typing import Text, Any, Optional, Dict, Union, List  # noqa
    import datetime
    from course.models import (  # noqa
            GradingOpportunity)
    from course.utils import (  # noqa
            CoursePageContext)
    import datetime  # noqa

# }}}

from django_select2.forms import ModelSelect2Widget
from relate.utils import StyledForm, StyledModelForm


class GradeInfoSearchWidgetBase(ModelSelect2Widget):
    model = FlowPageData
    search_fields = [
            'flow_session__user__username__icontains',
            'flow_session__user__first_name__icontains',
            'flow_session__user__last_name__icontains',
            ]


class PageGradedInfoSearchWidget(GradeInfoSearchWidgetBase):
    def label_from_instance(self, obj):
        visit = FlowPageVisit.objects.filter(
            flow_session=obj.flow_session,
            page_data=obj,
            is_submitted_answer=True
        ).last()
        if not visit:
            return None

        most_recent_grade = visit.get_most_recent_grade()
        from django.utils.timezone import now
        now_datetime = as_local_time(now())
        return (
            _("%(full_name)s, graded at %(grade_time)s %(grader)s"
              "(started at %(start_time)s).")
            % {
                "full_name": obj.flow_session.user.get_full_name(),
                "grade_time": compact_local_datetime_str(
                    as_local_time(most_recent_grade.grade_time),
                    now_datetime,
                    in_python=True
                ),
                "start_time": compact_local_datetime_str(
                    as_local_time(obj.flow_session.start_time),
                    now_datetime,
                    in_python=True
                ),
                "grader": (
                    string_concat(
                        _("by %(grader)s") %
                        {"grader": most_recent_grade.grader.get_full_name()},
                        " ")
                    if most_recent_grade.grader is not None else "")
            })


class PageUnGradedInfoSearchWidget(GradeInfoSearchWidgetBase):
    def label_from_instance(self, obj):
        from django.utils.timezone import now
        now_datetime = as_local_time(now())
        return (
            (
                _("%(full_name)s, started at %(time)s")
                % {
                    "full_name": obj.flow_session.user.get_full_name(),
                    "time": compact_local_datetime_str(
                        as_local_time(obj.flow_session.start_time),
                        now_datetime,
                        in_python=True
                    ),
                }))


class PageGradingInfoForm(StyledForm):
    def __init__(self, field_name, qset, widget, *args, **kwargs):
        # type:(Any, Text, Any, *Any, **Any) -> None
        label = kwargs.pop("label", None)
        super(PageGradingInfoForm, self).__init__(*args, **kwargs)

        self.helper.label_class = "sr-only"
        self.helper.field_class = ""

        import django.forms as forms
        select2_kwargs = {
            "queryset": qset,
            "required": False,
            "widget": widget,
        }
        if label:
            select2_kwargs["label"] = label.title()
        self.fields[field_name] = forms.ModelChoiceField(
            **select2_kwargs
        )


def get_session_grading_page_url(request, course_identifier, pagedata_pk):
    pagedata = FlowPageData.objects.get(pk=pagedata_pk)
    from django.urls import reverse
    uri = reverse("relate-grade_flow_page",
                  args=(
                      course_identifier,
                      pagedata.flow_session.id,
                      pagedata.ordinal))

    response = http.JsonResponse({
        "uri": uri
    })
    return response

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

    from course.flow import adjust_flow_session_page_data
    adjust_flow_session_page_data(pctx.repo, flow_session,
            pctx.course.identifier, respect_preview=False)

    fpctx = FlowPageContext(pctx.repo, pctx.course, flow_session.flow_id,
            page_ordinal, participation=flow_session.participation,
            flow_session=flow_session, request=pctx.request)

    if fpctx.page_desc is None:
        raise http.Http404()

    assert fpctx.page is not None
    assert fpctx.page_context is not None

    grading_rule = get_session_grading_rule(
            flow_session, fpctx.flow_desc, now_datetime)

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

            if shown_grade is not None:
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

        try:
            form = fpctx.page.make_form(
                    fpctx.page_context, fpctx.page_data.data,
                    answer_data, page_behavior)
        except InvalidPageData as e:
            messages.add_message(pctx.request, messages.ERROR,
                    _(
                        "The page data stored in the database was found "
                        "to be invalid for the page as given in the "
                        "course content. Likely the course content was "
                        "changed in an incompatible way (say, by adding "
                        "an option to a choice question) without changing "
                        "the question ID. The precise error encountered "
                        "was the following: ")+str(e))

            return render_course_page(pctx, "course/course-base.html", {})

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
                grade_data = fpctx.page.update_grade_data_from_grading_form_v2(
                        request,
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

    if grading_rule.grade_identifier is not None:
        grading_opportunity = get_flow_grading_opportunity(
                pctx.course, flow_session.flow_id, fpctx.flow_desc,
                grading_rule.grade_identifier,
                grading_rule.grade_aggregation_strategy
                )  # type: Optional[GradingOpportunity]
    else:
        grading_opportunity = None

    # {{{ enable flow session zapping

    this_flow_page_data = FlowPageData.objects.get(
        flow_session=flow_session, ordinal=page_ordinal)

    page_id = this_flow_page_data.page_id
    group_id = this_flow_page_data.group_id

    all_pagedata_qs = (
        FlowPageData.objects.filter(
            flow_session__course=flow_session.course,
            flow_session__flow_id=flow_session.flow_id,
            group_id=group_id,
            page_id=page_id,
            flow_session__participation__isnull=False,
            flow_session__in_progress=flow_session.in_progress
        )
            .select_related("flow_session")
            .select_related("flow_session__participation")
            .select_related("flow_session__user")
    )

    qs_order_by_list = ["flow_session__user"]
    qs_distinct_list = None
    if connection.features.can_distinct_on_fields:
        qs_distinct_list = []

    if (grading_rule.grade_aggregation_strategy
        in
            [grade_aggregation_strategy.use_earliest,
             grade_aggregation_strategy.use_latest]):
        if (grading_rule.grade_aggregation_strategy
                == grade_aggregation_strategy.use_earliest):
            qs_order_by_list.append('flow_session__start_time')
        else:
            qs_order_by_list.append('-flow_session__start_time')
        if qs_distinct_list is not None:
            qs_distinct_list.insert(0, 'flow_session__user')

    all_pagedata_qs = all_pagedata_qs.order_by(*qs_order_by_list)

    if qs_distinct_list:
        all_pagedata_qs = all_pagedata_qs.distinct(*qs_distinct_list)

    if getattr(fpctx.page, "grading_sort_by_page_data", False):
        from json import dumps
        all_flow_session_pks = list(
            (page_data.flow_session.pk
             for page_data in sorted(
                list(all_pagedata_qs),
                key=lambda x: (dumps(x.data), x.flow_session.user.last_name, x.flow_session.pk))))
    else:
        all_flow_session_pks = list(
            all_pagedata_qs.values_list("flow_session", flat=True))

    select2_graded_form = select2_ungraded_form = None

    if fpctx.page.expects_answer():
        # Filter out most recent visitgrade of each page.
        # For db without distinct(*fields), raw sql is needed.
        if True:
            with connection.cursor() as c:
                c.execute(
                    "SELECT DISTINCT ON (course_flowpagevisit.flow_session_id) * "
                    "FROM course_flowpagevisitgrade "
                    "INNER JOIN course_flowpagevisit "
                    "ON course_flowpagevisitgrade.visit_id = course_flowpagevisit.id "
                    "INNER JOIN course_flowpagedata "
                    "ON course_flowpagevisit.page_data_id = course_flowpagedata.id "
                    "WHERE course_flowpagevisit.flow_session_id IN %s "
                    "AND course_flowpagedata.group_id = %s "
                    "AND course_flowpagedata.page_id = %s "
                    "ORDER BY course_flowpagevisit.flow_session_id ASC, "
                    "course_flowpagevisitgrade.grade_time DESC",
                    [tuple(all_flow_session_pks), group_id, page_id]
                )
                exist_visitgrade_pks = [row[0] for row in c.fetchall()]

        from django.db.models import Max

        # {{{ Filter out the latest visitgrade of given flowsessions

        # Ref: GROUP BY and Select MAX from each group in Django, 2 queries
        # https: // gist.github.com / ryanpitts / 1304725  # gistcomment-1417399
        exist_visitgrade_qs = (
            FlowPageVisitGrade.objects.filter(
                visit__flow_session__pk__in=all_flow_session_pks,
                visit__page_data__group_id=group_id,
                visit__page_data__page_id=page_id,
            )
        )

        latest_visitgrade = exist_visitgrade_qs.values(
            "visit__flow_session_id"
        ).annotate(latest_visit=Max("pk"))

        exist_visitgrade_pks = (
            exist_visitgrade_qs.filter(
                pk__in=latest_visitgrade.values('latest_visit'))
            .order_by('-pk')
            .values_list("pk", flat=True)
        )

        # }}}

        not_null_graded_visit_pagedata_pks = (
            FlowPageVisitGrade.objects.filter(
                pk__in=exist_visitgrade_pks,
                correctness__isnull=False,
            )
                .order_by("-grade_time")
                .values_list("visit__page_data__pk", flat=True)
        )

        def get_queryset_preserving_order(name, order_list):
            clauses = (
                ' '.join(['WHEN %s=%s THEN %s' % (name, pk, i)
                          for i, pk in enumerate(order_list)]))
            ordering = 'CASE %s END' % clauses
            return ordering

        select2_graded_pagedata_qs = (
            FlowPageData.objects.filter(
                pk__in=not_null_graded_visit_pagedata_pks
            )
                .extra(
                select={
                    'ordering':
                        get_queryset_preserving_order(
                            "course_flowpagedata.id",
                            not_null_graded_visit_pagedata_pks)},
                order_by=('ordering',))
        )

        select2_ungraded_pagedata_qs = (
            FlowPageData.objects.filter(
                pk__in=all_pagedata_qs.values_list("pk", flat=True)
            )
                .exclude(
                pk__in=not_null_graded_visit_pagedata_pks
            )
        )

        if select2_graded_pagedata_qs.count():
            select2_graded_form = PageGradingInfoForm(
                "graded_pages",
                select2_graded_pagedata_qs,
                PageGradedInfoSearchWidget(
                    attrs={
                        'data-placeholder':
                            _("Graded pages, ordered by grade time.")}),
            )

        if select2_ungraded_pagedata_qs.count():
            select2_ungraded_form = PageGradingInfoForm(
                "ungraded_pages",
                select2_ungraded_pagedata_qs,
                PageUnGradedInfoSearchWidget(
                    attrs={'data-placeholder':
                               _("Pages ungraded or graded but not released, "
                                 "ordered by user's first name.")}),
            )

    next_flow_session_id = None
    next_flow_session_ordinal = None
    prev_flow_session_id = None
    prev_flow_session_ordinal = None

    # This is used to ensure prev and next session button navigate to
    # pages with the same page_id, when shuffled.
    all_pagedata_with_same_page_id_pk_ordinal_dict = (
        dict((k, v) for (k, v) in list(
            FlowPageData.objects.filter(
                group_id=group_id,
                page_id=page_id)
            .values_list("flow_session__pk", "ordinal")))
    )

    for i, other_flow_session_pk in enumerate(all_flow_session_pks):
        if other_flow_session_pk == flow_session.pk:
            if i > 0:
                prev_flow_session_id = all_flow_session_pks[i-1]
                prev_flow_session_ordinal = (
                    all_pagedata_with_same_page_id_pk_ordinal_dict.get(
                        prev_flow_session_id, page_ordinal))
            if i + 1 < len(all_flow_session_pks):
                next_flow_session_id = all_flow_session_pks[i+1]
                next_flow_session_ordinal = (
                    all_pagedata_with_same_page_id_pk_ordinal_dict.get(
                        next_flow_session_id, page_ordinal))

    # }}}


    # all_page_data = get_all_page_data(flow_session)
    # #assert all_page_data.count()
    #
    # all_page_grade_points = []  # type: List[Union[float, None]]
    # all_expect_grade_page_data = []
    # for i, pd in enumerate(all_page_data):
    #     fpctx_i = FlowPageContext(
    #         pctx.repo, pctx.course, flow_session.flow_id,
    #         pd.ordinal, participation=flow_session.participation,
    #         flow_session=flow_session, request=pctx.request)
    #
    #     assert fpctx_i.page is not None
    #
    #     if fpctx_i.page.expects_answer() and fpctx_i.page.is_answer_gradable():
    #         all_expect_grade_page_data.append(pd)
    #         if fpctx_i.prev_answer_visit is not None:
    #             most_recent_grade_i = (
    #                 fpctx_i.prev_answer_visit.get_most_recent_grade())
    #             if most_recent_grade_i is not None:
    #                 feedback_i = get_feedback_for_grade(most_recent_grade_i)
    #             else:
    #                 feedback_i = None
    #             if feedback_i is not None and feedback_i.correctness is not None:
    #                 all_page_grade_points.append(feedback_i.correctness * 100)
    #             else:
    #                 all_page_grade_points.append(None)
    #         else:
    #             all_page_grade_points.append(None)
    #
    # assert len(all_expect_grade_page_data) == len(all_page_grade_points)
    #
    # grade_status_zip = zip(all_expect_grade_page_data, all_page_grade_points)
    # grade_status_zip = zip(all_expect_grade_page_data, all_page_grade_points)
    grade_status_zip = None

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
                'prev_flow_session_ordinal': prev_flow_session_ordinal,
                "next_flow_session_id": next_flow_session_id,
                'next_flow_session_ordinal': next_flow_session_ordinal,
                "select2_graded_form":select2_graded_form,
                "select2_ungraded_form": select2_ungraded_form,

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
