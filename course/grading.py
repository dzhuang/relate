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
from django.db.models import Q
from django.shortcuts import (  # noqa
        get_object_or_404, redirect)
from relate.utils import (
    retry_transaction_decorator, StyledForm,
    as_local_time, format_datetime_local)
from django.contrib import messages
from django.core.exceptions import (  # noqa
        PermissionDenied, SuspiciousOperation,
        ObjectDoesNotExist)
from django import http

from course.models import (  # noqa
        Course, Participation, FlowPageData, FlowPageVisit,
        FlowSession, FlowPageVisitGrade,
        get_flow_grading_opportunity,
        get_feedback_for_grade,
        update_bulk_feedback)
from course.constants import (
        grade_aggregation_strategy)
from course.utils import (
        course_view, render_course_page,
        get_session_grading_rule,
        FlowPageContext)
from course.views import get_now_or_fake_time
from course.page import InvalidPageData

from django.conf import settings
from django.utils import translation
from course.constants import (
        participation_permission as pperm,
        )
from django_select2.forms import ModelSelect2Widget

# {{{ for mypy

if False:
    from typing import Text, Any, Optional, Dict, Iterable, Union, List  # noqa
    import datetime
    from course.models import (  # noqa
            GradingOpportunity)
    from course.utils import (  # noqa
            CoursePageContext)
    import datetime  # noqa
    from django.db import query  # noqa

# }}}


class PageGradedInfoSearchWidget(ModelSelect2Widget):
    model = FlowPageVisitGrade
    search_fields = [
        'grader__username__icontains',
        'grader__first_name__icontains',
        'grader__last_name__icontains',
        'visit__flow_session__pk__contains',
        'visit__flow_session__user__username__icontains',
        'visit__flow_session__user__first_name__icontains',
        'visit__flow_session__user__last_name__icontains',
        ]

    def label_from_instance(self, obj):
        flow_session = obj.visit.flow_session
        user = flow_session.user

        from relate.utils import compact_local_datetime_str
        from django.utils.timezone import now
        now_datetime = as_local_time(now())

        return (
            _("%(full_name)s (%(username)s) session %(flow_session_pk)s, "
                "graded at %(grade_time)s (%(grader)s)"
              )
            % {
                "full_name": (
                    user.get_full_name()
                    if (user.first_name
                        and user.last_name)
                    else user.username
                ),
                "username": user.username,
                "grade_time": compact_local_datetime_str(
                    as_local_time(obj.grade_time), now_datetime,
                    in_python=True
                ),
                "flow_session_pk": flow_session.pk,
                "grader": (
                    string_concat(
                        _("by %(grader)s") %
                        {"grader": (
                            obj.grader.get_full_name()
                            if obj.grader.first_name and obj.grader.last_name
                            else obj.grader.username
                        )},
                        " ")
                    if obj.grader is not None else _("autograded"))
            })


class PageUnGradedInfoSearchWidget(ModelSelect2Widget):
    model = FlowPageData
    search_fields = [
            'flow_session__pk__contains',
            'flow_session__user__username__icontains',
            'flow_session__user__first_name__icontains',
            'flow_session__user__last_name__icontains',
            ]

    def label_from_instance(self, obj):
        return (
            (
                _("%(full_name)s session %(flow_session_pk)s")
                % {
                    "full_name": (
                        obj.flow_session.user.get_full_name()
                        if (obj.flow_session.user.first_name
                            and obj.flow_session.user.last_name)
                        else obj.flow_session.user.username
                    ),
                    "flow_session_pk": obj.flow_session.pk,
                }))


class PageGradingNaviBox(StyledForm):
    def __init__(self, field_name, qset, widget, *args, **kwargs):
        # type:(Text, Any, Any, *Any, **Any) -> None
        label = kwargs.pop("label", None)
        super(PageGradingNaviBox, self).__init__(*args, **kwargs)

        self.helper.label_class = "sr-only"
        self.helper.field_class = "col-lg-10"

        from django import forms
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


def get_session_grading_page_url(request, course_identifier,
                                 grade_status, pk):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    course = get_object_or_404(Course, identifier=course_identifier)

    from course.enrollment import get_participation_for_request
    participation = get_participation_for_request(request, course)

    if not participation.has_permission(pperm.view_gradebook):
            raise PermissionDenied(_("may not view grade book"))

    if grade_status == "graded":
        visitgrade = FlowPageVisitGrade.objects.get(pk=pk)
        pagedata = visitgrade.visit.page_data
    else:
        pagedata = FlowPageData.objects.get(pk=pk)
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


def get_excluded_participations(course_identifier, re_included_participation=None):
    # type: (Text, Optional[Participation]) -> query.QuerySet
    # Get queryset of participations which will be skipped during manual grading
    # but exclude the exception_obj

    if not re_included_participation:
        return (
            Participation.objects.filter(
                course__identifier=course_identifier,
                roles__permissions__permission=(
                    pperm.skip_during_manual_grading))
        )

    return (
        Participation.objects.filter(
            Q(course__identifier=course_identifier,
               roles__permissions__permission=(
                   pperm.skip_during_manual_grading))
            &
            ~Q(pk=re_included_participation.pk)))


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

    prev_grades = (
        FlowPageVisitGrade.objects.filter(
            visit__flow_session=flow_session,
            visit__page_data__ordinal=page_ordinal,
            visit__is_submitted_answer=True)
        .exclude(
            visit__flow_session__participation__roles__permissions__permission=(
                pperm.skip_during_manual_grading),
        )
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

    current_page_expects_grade = (
        fpctx.page.expects_answer()
        and fpctx.page.is_answer_gradable()
        and fpctx.prev_answer_visit is not None
        and not flow_session.in_progress
        and not viewing_prev_grade)

    if current_page_expects_grade:
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

    max_points = None  # type: Optional[Union[int, float]]
    points_awarded = None  # type: Optional[Union[int, float]]
    if (fpctx.page.expects_answer()
            and fpctx.page.is_answer_gradable()):
        max_points = fpctx.page.max_points(fpctx.page_data)
        if feedback is not None and feedback.correctness is not None:
            points_awarded = max_points * feedback.correctness

    # }}}

    grading_rule = get_session_grading_rule(
            flow_session, fpctx.flow_desc, now_datetime)

    if grading_rule.grade_identifier is not None:
        grading_opportunity = get_flow_grading_opportunity(
                pctx.course, flow_session.flow_id, fpctx.flow_desc,
                grading_rule.grade_identifier,
                grading_rule.grade_aggregation_strategy
                )  # type: Optional[GradingOpportunity]
    else:
        grading_opportunity = None

    # {{{ enable flow session zapping by select2

    current_flowpagedata = FlowPageData.objects.get(
        flow_session=flow_session, ordinal=page_ordinal)

    page_id = current_flowpagedata.page_id
    group_id = current_flowpagedata.group_id

    all_pagedata_qset = (
        FlowPageData.objects.filter(
            flow_session__course=flow_session.course,
            flow_session__flow_id=flow_session.flow_id,
            group_id=group_id,
            page_id=page_id,
            flow_session__participation__isnull=False,
            flow_session__in_progress=flow_session.in_progress)
    )

    re_included_pagedata_pk = None  # type: Optional[int]
    if (flow_session.participation.has_permission(
            pperm.skip_during_manual_grading)):
        # We are now viewing a page owned by a participation which will be
        # skipped during manual grading. It's page_data is now included back
        # into all_pagedata_qset, otherwise we cannot navigate to other pages
        # with the same page_id.
        re_included_pagedata_pk = current_flowpagedata.pk
        excluded_participations = (
            get_excluded_participations(
                course_identifier=pctx.course.identifier,
                re_included_participation=flow_session.participation))
        all_pagedata_qset = all_pagedata_qset.exclude(
            flow_session__participation__in=excluded_participations)
    else:
        all_pagedata_qset = (
            all_pagedata_qset.exclude(
                flow_session__participation__roles__permissions__permission=(
                    pperm.skip_during_manual_grading))
        )

    all_pagedata_qset = (all_pagedata_qset
        .select_related("flow_session")
        .select_related("flow_session__participation")
        .select_related("flow_session__user"))

    order_by_list = [
        "flow_session__user__last_name",
        "flow_session__user__first_name"]

    distinct_list = None  # type: Optional[Any]
    if connection.features.can_distinct_on_fields and grading_form:
        # No need to distinct for autograded page
        distinct_list = []

    if (grading_rule.grade_aggregation_strategy
        in
            [grade_aggregation_strategy.use_earliest,
             grade_aggregation_strategy.use_latest]):
        if (grading_rule.grade_aggregation_strategy
                == grade_aggregation_strategy.use_earliest):
            order_by_list.append('flow_session__start_time')
        else:
            order_by_list.append('-flow_session__start_time')

        # View only one session if use_latest or use_earliest for human graded pages
        if distinct_list is not None:
            # distinct should have the same order_by, however, last_name
            # can be duplicate, use user to distinct instead.
            order_by_list.insert(0, "flow_session__user")
            distinct_list.insert(0, 'flow_session__user')

    all_pagedata_qset = all_pagedata_qset.order_by(*order_by_list)

    if distinct_list:
        all_pagedata_qset = all_pagedata_qset.distinct(*distinct_list)

    if all_pagedata_qset.count():
        if getattr(fpctx.page, "grading_sort_by_page_data", False):
            from json import dumps
            all_flow_session_pks = (
                list(
                    page_data.flow_session.pk
                    for page_data in sorted(
                        list(all_pagedata_qset), key=lambda x: (
                            dumps(x.data),
                            x.flow_session.user.last_name,
                            x.flow_session.pk))
                )
            )
        else:
            all_flow_session_pks = (
                all_pagedata_qset.values_list("flow_session", flat=True))
    else:
        # When visiting a page which won't be included in statistics
        all_flow_session_pks = []

    all_pagedata_pks = all_pagedata_qset.values_list("pk", flat=True)

    navigation_box_graded = navigation_box_ungraded = None

    ungraded_flow_session_pks = []  # type: List[int]

    if all_flow_session_pks:
        may_view_participant_full_profile = (
            not pctx.has_permission(pperm.view_participant_masked_profile))

        if current_page_expects_grade and may_view_participant_full_profile:

            # {{{ Make the navigation_box_graded

            # Get the latest visitgrade of the page in each flow_sessions
            # Ref: GROUP BY and Select MAX from each group via 2 queries
            # https://gist.github.com/ryanpitts/1304725#gistcomment-1417399
            exist_visitgrade_qset = (
                FlowPageVisitGrade.objects.filter(
                    visit__flow_session__pk__in=all_flow_session_pks,
                    visit__page_data__group_id=group_id,
                    visit__page_data__page_id=page_id)
                    .select_related("visit")
                    .select_related("visit__page_data")
                    .select_related("visit__flow_session")
            )

            from django.db.models import Max
            latest_visitgrades = (
                exist_visitgrade_qset.values(
                    "visit__flow_session_id"
                )
                    # assuming visitgrade with max pk is latest visitgrade
                    .annotate(latest_visit=Max("pk"))
            )

            exist_visitgrade_pks = (
                exist_visitgrade_qset.filter(
                    pk__in=latest_visitgrades.values('latest_visit'))
                    .order_by('-pk')
                    .values_list("pk", flat=True)
            )

            if not grading_form:
                # For autograded pages, group by users while sorting
                graded_qset_order_by_list = [
                    "visit__flow_session__user__last_name",
                    "visit__flow_session__user__first_name",
                    "visit__flow_session__user__username",
                    "-grade_time"]
                graded_box_widget_placeholder = (
                    _("Graded pages, ordered by last_name, "
                      "first_name and grade time"))
            else:
                # For human-graded pages, we care more about when the page is
                # graded, thus order by grade_time
                graded_qset_order_by_list = ["-grade_time"]
                graded_box_widget_placeholder = (
                    _("Graded pages, ordered by grade time")
                )

            latest_visitgrades_qset = (
                FlowPageVisitGrade.objects.filter(
                    pk__in=exist_visitgrade_pks,
                    correctness__isnull=False)
                .order_by(*graded_qset_order_by_list)
                .select_related("visit__flow_session")
                .select_related("visit__flow_session__user")
                .select_related("visit__page_data")
                .select_related("grader")
            )

            navigation_box_graded = PageGradingNaviBox(
                "graded_pages",
                latest_visitgrades_qset,
                PageGradedInfoSearchWidget(
                    attrs={
                        'data-placeholder': graded_box_widget_placeholder}),
            )

            # }}}

            # {{{ Make the navigation_box_ungraded
            if grading_form:
                graded_pagedata_pks = (
                    latest_visitgrades_qset.values_list(
                        "visit__page_data__pk", flat=True))

                ungraded_pagedata_qset = (
                    FlowPageData.objects.filter(
                        Q(pk__in=all_pagedata_pks)
                        &
                        ~Q(pk__in=graded_pagedata_pks)
                        &
                        ~Q(pk=re_included_pagedata_pk)
                    )
                    .order_by(
                        "flow_session__user__last_name",
                        "flow_session__user__first_name",
                        "flow_session__user__pk"
                    )
                    .select_related("flow_session")
                    .select_related("flow_session__user")
                )

                if ungraded_pagedata_qset.count():
                    navigation_box_ungraded = PageGradingNaviBox(
                        "ungraded_pages",
                        ungraded_pagedata_qset,
                        PageUnGradedInfoSearchWidget(
                            attrs={
                                'data-placeholder':
                                    _("Pages ungraded or graded but not released, "
                                      "ordered by user's last name.")}),
                    )
                    ungraded_flow_session_pks = list(
                        ungraded_pagedata_qset.values_list(
                            "flow_session__pk", flat=True))

            # }}}

    navigation_boxes = []  # type: List[Any]
    for box in [navigation_box_graded, navigation_box_ungraded]:
        if box:
            navigation_boxes.append(box)
    # }}}

    # {{{ enable flow session zapping by navigatioin button
    next_flow_session_id = None
    next_flow_session_ordinal = None
    prev_flow_session_id = None
    prev_flow_session_ordinal = None
    next_ungraded_flow_session_id = None
    next_ungraded_flow_session_ordinal = None

    for i, other_flow_session_pk in enumerate(all_flow_session_pks):
        if other_flow_session_pk == flow_session.pk:
            if i > 0:
                prev_flow_session_id = all_flow_session_pks[i-1]
                try:
                    prev_flow_session_ordinal = (
                        FlowPageData.objects.get(
                            flow_session__id=prev_flow_session_id,
                            page_id=page_id
                        ).ordinal
                    )
                except ObjectDoesNotExist:
                    prev_flow_session_id = page_ordinal
            if i + 1 < len(all_flow_session_pks):
                next_flow_session_id = all_flow_session_pks[i+1]
                try:
                    next_flow_session_ordinal = (
                        FlowPageData.objects.get(
                            flow_session__id=next_flow_session_id,
                            page_id=page_id
                        ).ordinal
                    )
                except ObjectDoesNotExist:
                    next_flow_session_ordinal = page_ordinal

            if grading_form:
                from itertools import chain
                next_ungraded_flow_session_id = None
                for j in chain(range(i + 1, len(all_flow_session_pks)), range(i)):
                    if all_flow_session_pks[j] in ungraded_flow_session_pks:
                        next_ungraded_flow_session_id = all_flow_session_pks[j]
                        next_ungraded_flow_session_ordinal = (
                            FlowPageData.objects.get(
                                flow_session__pk=next_ungraded_flow_session_id,
                                page_id=page_id
                            ).ordinal
                        )
                        break

    # }}}

    # {{{ Warn if the viewed page/session will not be counted in the
    # final score of the flow.due to distinct and
    # grade_aggregation_strategy.use_latest/use_earliest

    session_not_for_grading_warning_html = None

    if (grading_form
        and distinct_list
        and
                current_flowpagedata.pk not in all_pagedata_pks):

        available_pagedata = FlowPageData.objects.get(
            pk__in=all_pagedata_pks,
            flow_session__user=flow_session.user
        )
        from django.urls import reverse
        uri = reverse("relate-grade_flow_page",
                      args=(
                          pctx.course_identifier,
                          available_pagedata.flow_session.id,
                          available_pagedata.ordinal))

        from django.utils.safestring import mark_safe
        session_not_for_grading_warning_html = mark_safe(
            _("This page and session will not be counted into %(user)s's "
              "grading of this flow, see %(url)s instead.")
            % {
                "user": current_flowpagedata.flow_session.user,
                "url": "<a href='%s'>%s</a>"
                       % (uri, _("this session"))
            }
        )
    # }}}

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
                "next_ungraded_flow_session_id": next_ungraded_flow_session_id,
                "next_ungraded_flow_session_ordinal":
                    next_ungraded_flow_session_ordinal,
                "navigation_boxes": navigation_boxes,
                "session_not_for_grading_warning_html":
                    session_not_for_grading_warning_html,

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
