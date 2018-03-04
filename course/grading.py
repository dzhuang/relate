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
from django.db import connection
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import (  # noqa
        get_object_or_404, redirect)
from relate.utils import (
        retry_transaction_decorator, StyledForm, string_concat,
        as_local_time, format_datetime_local)
from django.contrib import messages
from django.core.exceptions import (  # noqa
        PermissionDenied, SuspiciousOperation,
        ObjectDoesNotExist)
from django import http

from course.models import (  # noqa
        Course, Participation, FlowPageData,
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

from course.constants import (
        participation_permission as pperm,
        )
from django_select2.forms import ModelSelect2Widget
from django_select2.views import AutoResponseView

# {{{ for mypy

from typing import cast
if False:
    from typing import Text, Any, Optional, Dict, Tuple, Union, List  # noqa
    import datetime
    from course.models import (  # noqa
            GradingOpportunity)
    from course.utils import (  # noqa
            CoursePageContext, FlowSessionGradingRule)
    import datetime  # noqa
    from django.db.models import query  # noqa

# }}}


def get_prev_visit_grades(
            course_identifier,  # type: Text
            flow_session_id,  # type: int
            page_ordinal,  # type: int
            reversed_on_visit_time_and_grade_time=False  # type: Optional[bool]
        ):
    # type: (...) -> query.QuerySet
    order_by_args = []  # type: List[Text]
    if reversed_on_visit_time_and_grade_time:
        order_by_args = ["-visit__visit_time", "-grade_time"]
    return (FlowPageVisitGrade.objects
            .filter(
                visit__flow_session_id=flow_session_id,
                visit__page_data__page_ordinal=page_ordinal,
                visit__is_submitted_answer=True,
                visit__flow_session__course__identifier=course_identifier)
            .order_by(*order_by_args)
            .select_related("visit"))


@course_view
def get_prev_grades_dropdown_content(pctx, flow_session_id, page_ordinal):
    """
    :return: serialized prev_grades items for rendering past-grades-dropdown
    """
    request = pctx.request
    if not request.is_ajax() or request.method != "GET":
        raise PermissionDenied()

    if not pctx.participation:
        raise PermissionDenied(_("may not view grade book"))
    if not pctx.participation.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view grade book"))

    page_ordinal = int(page_ordinal)
    flow_session_id = int(flow_session_id)

    prev_grades = get_prev_visit_grades(pctx.course_identifier,
                                        flow_session_id, page_ordinal, True)

    def serialize(obj):
        return {
            "id": obj.id,
            "visit_time": (
                format_datetime_local(as_local_time(obj.visit.visit_time))),
            "grade_time": format_datetime_local(as_local_time(obj.grade_time)),
            "value": obj.value(),
        }

    return http.JsonResponse(
        {"result": [serialize(pgrade) for pgrade in prev_grades]})


class GradingAutoResponseView(AutoResponseView):
    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get('term', request.GET.get('term', ''))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return http.JsonResponse({
            'results': [
                {
                    'text': self.widget.label_from_instance(obj),
                    'id': obj.pk,
                    'uri': self.get_obj_url(obj)
                }
                for obj in context['object_list']
                ],
            'more': context['page_obj'].has_next()
        })

    def get_obj_url(self, obj):
        if isinstance(obj, FlowPageData):
            flow_session = obj.flow_session
            page_ordinal = obj.page_ordinal
        else:
            assert isinstance(obj, FlowPageVisitGrade)
            flow_session = obj.visit.flow_session
            page_ordinal = obj.visit.page_data.page_ordinal

        return reverse("relate-grade_flow_page",
                      args=(
                          flow_session.course.identifier,
                          flow_session.id,
                          page_ordinal))


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

    def __init__(self, *args, **kwargs):
        # type: (...) -> None
        super(PageGradedInfoSearchWidget, self).__init__(*args, **kwargs)
        self.data_view = "grading_select2-json"

    def label_from_instance(self, obj):
        flow_session = obj.visit.flow_session
        user = flow_session.user
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
                "grade_time": format_datetime_local(
                    as_local_time(obj.grade_time)
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

    def __init__(self, *args, **kwargs):
        # type: (...) -> None
        super(PageUnGradedInfoSearchWidget, self).__init__(*args, **kwargs)
        self.data_view = "grading_select2-json"

    def label_from_instance(self, obj):
        flow_session = obj.flow_session
        user = flow_session.user
        return (
            (
                _("%(full_name)s (%(username)s) session %(flow_session_pk)s")
                % {
                    "full_name": (
                        user.get_full_name()
                        if (user.first_name
                            and user.last_name)
                        else user.username
                    ),
                    "username": user.username,
                    "flow_session_pk": flow_session.pk,
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


@course_view
def get_navi_box_grading_page_url(pctx, flow_id, data_type, data_pk):
    """
    An AJAX handler when an items is clicked in select2 widget.
    :param pctx:
    :param flow_id:
    :param data_type: a :class:`string`, can be 'visitgrade' or 'pagedata'
    :param pk:  a :class:`int`, the pk of the clicked instance.
    :return: the grade_flow_page url of the clicked item
    """
    request = pctx.request
    if not request.is_ajax() or request.method != "GET":
        raise PermissionDenied()

    if data_type not in ["visitgrade", "pagedata"]:
        raise http.Http404()

    if not pctx.participation:
        raise PermissionDenied(_("may not view grade book"))
    if not pctx.participation.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view grade book"))

    if data_type == "visitgrade":
        visitgrade = get_object_or_404(
                FlowPageVisitGrade,
                visit__flow_session__flow_id=flow_id, pk=data_pk)
        pagedata = visitgrade.visit.page_data
    else:
        pagedata = get_object_or_404(
                FlowPageData, flow_session__flow_id=flow_id, pk=data_pk)

    uri = reverse("relate-grade_flow_page",
                  args=(
                      pctx.course_identifier,
                      pagedata.flow_session.id,
                      pagedata.page_ordinal))

    response = http.JsonResponse({
        "uri": uri
    })
    return response


def get_excluded_participation_qset(course, re_included_participation=None):
    # type: (Course, Optional[Participation]) -> query.QuerySet
    """
    :param course: a :class:`Course` instance.
    :param re_included_participation:  a :class:`Participation` instance.
    :return: a :class:`Participation` queryset which will be skipped during
     manual grading but exclude the re_included_participation object.
    """
    skip_pperm = pperm.skip_during_manual_grading

    kwargs = {"course": course}
    args = [
        Q(roles__permissions__permission=skip_pperm)
        |
        Q(individual_permissions__permission=skip_pperm)]

    if re_included_participation:
        args.append(~Q(pk=re_included_participation.pk))

    return Participation.objects.filter(*args, **kwargs)


def get_all_graded_visitgrade_qset(
        all_flow_session_pks,  # type: List[int]
        page_id,  # type: Text
        group_id,  # type: Text
        need_manual_grading=True,  # type: Optional[bool]
        ):
    # type: (...) -> query.QuerySet

    return _get_all_latest_graded_visitgrade_qset(
        all_flow_session_pks,
        group_id, page_id,
        need_manual_grading=need_manual_grading,
        sort_result_and_select_related=False)


def get_ordered_pagedata_qset(all_pagedata_qset, exluded_pagedata_pks=None):
    # type: (query.QuerySet, Optional[List[int]]) -> query.QuerySet
    if exluded_pagedata_pks is None:
        return all_pagedata_qset
    else:
        return all_pagedata_qset.exclude(pk__in=exluded_pagedata_pks)


def get_ungraded_pagedata_qset(
        all_flow_session_pks,  # type: List[int]
        all_pagedata_qset,  # type: query.QuerySet
        page_id,  # type: Text
        group_id  # type: Text
        ):
    # type: (...) -> query.QuerySet
    graded_visitgrades_qset_unordered = (
        _get_all_latest_graded_visitgrade_qset(
            all_flow_session_pks,
            group_id, page_id,
            need_manual_grading=True,
            sort_result_and_select_related=True)
    )

    graded_pagedata_pks = list(
        graded_visitgrades_qset_unordered.values_list(
            "visit__page_data__pk", flat=True))

    return get_ordered_pagedata_qset(
                all_pagedata_qset, exluded_pagedata_pks=graded_pagedata_pks)


def _get_all_latest_graded_visitgrade_qset(
        all_flow_session_pks,  # type: List[int]
        group_id,  # type: Text
        page_id,  # type: Text
        need_manual_grading=True,  # type: Optional[bool]
        sort_result_and_select_related=False,  # type: Optional[bool]
        ):
    # type: (...) -> query.QuerySet
    """
    :param all_flow_session_pks:
    :param group_id:
    :param page_id:
    :param need_manual_grading:
    :param sort_result_and_select_related: a :class:`bool` instance.
     If True, the resulting queryset will used as filter args in other queries,
     so we don't need to order the result because that will bring more complexity
     and consequently more load in db operation.
     If False, the result will be directly passed to graded page navigation box,
     we need to order the result.
    :return:
    """
    # {{{ Extract pks of latest FlowPageVisitGrade objects
    # of all flow_session of interest
    if connection.features.can_distinct_on_fields:
        # for PostGreSql only
        all_visitgrade_qset = (
            FlowPageVisitGrade.objects.filter(
                visit__flow_session__pk__in=all_flow_session_pks,
                visit__page_data__group_id=group_id,
                visit__page_data__page_id=page_id)
            .select_related("visit__flow_session")
            .order_by("visit__flow_session__pk", "-grade_time")
            .distinct("visit__flow_session__pk")
        )

        exist_visitgrade_pks = list(
            all_visitgrade_qset.values_list("pk", flat=True))

    else:
        # for db other than PostGreSql
        # Get the latest visitgrade of the page in each flow_sessions
        # Ref: GROUP BY and Select MAX from each group via 2 queries
        # https://gist.github.com/ryanpitts/1304725#gistcomment-1417399
        all_visitgrade_qset = (
            FlowPageVisitGrade.objects.filter(
                visit__flow_session__pk__in=all_flow_session_pks,
                visit__page_data__group_id=group_id,
                visit__page_data__page_id=page_id)
            .select_related("visit__flow_session")
        )

        from django.db.models import Max
        latest_visitgrades = (
            all_visitgrade_qset.values(
                "visit__flow_session_id"
            )
            # This is assuming visitgrade with max pk is latest visitgrade
            .annotate(latest_visit=Max("pk"))
        )

        exist_visitgrade_pks = list(
            all_visitgrade_qset.filter(
                pk__in=latest_visitgrades.values('latest_visit'))
            .order_by('-pk')
            .values_list("pk", flat=True)
        )
    # }}}

    order_by_args = []  # type: List[Text]

    if not sort_result_and_select_related:
        if not need_manual_grading:
            # For autograded pages, group by users while sorting
            order_by_args = [
                "visit__flow_session__user__last_name",
                "visit__flow_session__user__first_name",
                "visit__flow_session__user__username",
                "-grade_time"]
        else:
            # For human-graded pages, we care more about when the page is
            # graded, thus order by grade_time
            order_by_args = ["-grade_time"]

    qset = (
        FlowPageVisitGrade.objects.filter(
            pk__in=exist_visitgrade_pks,

            # This excluded those which are graded with grades not released.
            correctness__isnull=False)
        .order_by(*order_by_args)
        .select_related("visit__page_data"))

    if not sort_result_and_select_related:
        qset = (
            qset.select_related("visit__flow_session__user")
                .select_related("visit__flow_session")
                .select_related("grader")
        )

    return qset


def get_related_sessions_and_pagedata_qset_from_session(
        flow_session,  # type: FlowSession
        page_id,  # type: Text
        group_id,  # type: Text
        grading_rule,  # type: FlowSessionGradingRule
        fpctx,  # type: FlowPageContext
        need_manual_grading=True  # type: bool
        ):
    # type: (...) -> Tuple[List[int], query.QuerySet]
    """
    :return: two queryset: all_flow_session_pks, all_pagedata_qset
    """

    all_flow_session_pks = get_all_flow_session_pks(flow_session, grading_rule,
                                                    need_manual_grading)

    filter_kwargs = {
        "flow_session__pk__in": all_flow_session_pks,
        "flow_session__flow_id": flow_session.flow_id,
        "group_id": group_id,
        "page_id": page_id,
        "flow_session__participation__isnull": False,
        "flow_session__in_progress": flow_session.in_progress
    }

    order_by_args = [
        "flow_session__user__last_name",
        "flow_session__user__first_name",
        "flow_session__user"
    ]

    if getattr(fpctx.page, "grading_sort_by_page_data", False):
        order_by_args.insert(0, "data_stringfied")

    all_pagedata_qset = (
        FlowPageData.objects
        .filter(**filter_kwargs)
        .order_by(*order_by_args)
        .select_related("flow_session")
        .select_related("flow_session__participation")
        .select_related("flow_session__user"))

    if getattr(fpctx.page, "grading_sort_by_page_data", False):
        all_flow_session_pks = list(
            all_pagedata_qset.values_list("flow_session__pk", flat=True))

    return all_flow_session_pks, all_pagedata_qset


def get_all_flow_session_pks(flow_session, grading_rule, need_manual_grading):
    # type: (FlowSession, FlowSessionGradingRule, bool) -> List[int]

    # For those who are skip_during_manual_grading, we need to
    # include their session(s) back only when we are visiting
    # their session page(s).
    re_included_participation = None  # type: Optional[Participation]
    if (flow_session.participation.has_permission(
            pperm.skip_during_manual_grading)):
        re_included_participation = flow_session.participation
    excluded_participations = (
        get_excluded_participation_qset(
            course=flow_session.course,
            re_included_participation=re_included_participation))

    filter_kwargs = {}
    exclude_kwargs = {"participation__in": excluded_participations}

    if need_manual_grading:
        if connection.features.can_distinct_on_fields:
            distinct_order_by_args = ["user"]
            gstrategy = grading_rule.grade_aggregation_strategy
            if gstrategy == grade_aggregation_strategy.use_earliest:
                distinct_order_by_args.append('start_time')
            elif gstrategy == grade_aggregation_strategy.use_latest:
                distinct_order_by_args.append('-start_time')
            unique_session_pks = (
                FlowSession.objects.filter(
                    course=flow_session.course,
                    flow_id=flow_session.flow_id,
                    participation__isnull=False,
                    in_progress=flow_session.in_progress)
                .exclude(participation__in=excluded_participations)
                .order_by(*distinct_order_by_args).distinct("user")
                .values_list("pk", flat=True)
            )
            exclude_kwargs = {}
            filter_kwargs["pk__in"] = unique_session_pks

    if not filter_kwargs:
        filter_kwargs = {
            "course": flow_session.course,
            "flow_id":  flow_session.flow_id,
            "participation__isnull": False,
            "in_progress": flow_session.in_progress
        }

    all_flow_session_pks = list(
        FlowSession.objects.filter(**filter_kwargs)
        .exclude(**exclude_kwargs)
        .order_by("user__last_name",
                  "user__first_name",
                  "user__username")
        .select_related("user")
        .values_list("pk", flat=True)
    )

    return all_flow_session_pks


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

    prev_grades = get_prev_visit_grades(pctx.course_identifier, flow_session_id,
                                        page_ordinal)

    # {{{ reproduce student view

    form = None
    feedback = None
    answer_data = None
    grade_data = None
    shown_grade = None

    page_expects_answer = fpctx.page.expects_answer()

    if page_expects_answer:
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

    page_expects_grade = (
        page_expects_answer
        and fpctx.page.is_answer_gradable()
        and fpctx.prev_answer_visit is not None
        and not flow_session.in_progress
        and not viewing_prev_grade)

    if page_expects_grade:
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
                from course.utils import LanguageOverride
                with LanguageOverride(pctx.course):
                    feedback = fpctx.page.grade(
                            fpctx.page_context, fpctx.page_data.data,
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

                prev_grade_id = _save_grade(fpctx, flow_session, most_recent_grade,
                        bulk_feedback_json, now_datetime)
        else:
            grading_form = fpctx.page.make_grading_form(
                    fpctx.page_context, fpctx.page_data, grade_data)

    else:
        grading_form = None

    grading_form_html = None  # type: Optional[Text]
    need_manual_grading = False
    if grading_form is not None:
        need_manual_grading = True
        from crispy_forms.layout import Submit
        grading_form.helper.form_class += " relate-grading-form"
        grading_form.helper.add_input(
                Submit(
                    "submit", _("Submit"),
                    accesskey="s",
                    css_class="relate-grading-save-button"))

        grading_form_html = fpctx.page.grading_form_to_html(
                pctx.request, fpctx.page_context, grading_form, grade_data)

    # }}}

    # {{{ compute points_awarded

    max_points = None  # type: Optional[Union[int, float]]
    points_awarded = None  # type: Optional[Union[int, float]]
    if (page_expects_answer
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

    flowpagedata = FlowPageData.objects.get(
        flow_session=flow_session, page_ordinal=page_ordinal)
    page_id = flowpagedata.page_id
    group_id = flowpagedata.group_id

    all_flow_session_pks, all_pagedata_qset = (
        get_related_sessions_and_pagedata_qset_from_session(
            flow_session=flow_session,
            page_id=page_id,
            group_id=group_id,
            grading_rule=grading_rule,
            need_manual_grading=need_manual_grading,
            fpctx=fpctx,
        )
    )

    navigation_box_graded = navigation_box_ungraded = None  # type: Optional[StyledForm]  # noqa

    ungraded_flow_session_pks = []  # type: List[int]

    may_view_participant_full_profile = (
        not pctx.has_permission(pperm.view_participant_masked_profile))

    is_survey_page = (
        not page_expects_grade
        and fpctx.page.expects_answer()
        and fpctx.prev_answer_visit is not None
        and not flow_session.in_progress
        and not viewing_prev_grade)

    if may_view_participant_full_profile:
        if page_expects_grade:
            graded_visitgrade_qset = (
                get_all_graded_visitgrade_qset(
                    all_flow_session_pks, page_id, group_id,
                    need_manual_grading=need_manual_grading))

            graded_box_widget_placeholder = (
                _("Graded pages, ordered by grade time")
                if need_manual_grading
                else _("Graded pages, ordered by last_name, "
                      "first_name and grade time")
            )

            navigation_box_graded = PageGradingNaviBox(
                "graded_pages",
                graded_visitgrade_qset,
                PageGradedInfoSearchWidget(
                    attrs={
                        'data-placeholder': graded_box_widget_placeholder}),
            )

            if need_manual_grading:
                ungraded_pagedata_qset = (
                    get_ungraded_pagedata_qset(
                        all_flow_session_pks,
                        all_pagedata_qset, page_id, group_id))

                ungraded_flow_session_pks = list(
                    ungraded_pagedata_qset.values_list(
                        "flow_session__pk", flat=True))

                if len(ungraded_flow_session_pks):
                    navigation_box_ungraded = PageGradingNaviBox(
                        "ungraded_pages",
                        ungraded_pagedata_qset,
                        PageUnGradedInfoSearchWidget(
                            attrs={
                                'data-placeholder':
                                    _("Pages ungraded or graded but not released, "
                                      "ordered by user's last name.")}),
                    )

        elif is_survey_page:
            pagedata_qset = (
                get_ordered_pagedata_qset(all_pagedata_qset))

            navigation_box_ungraded = PageGradingNaviBox(
                "pages",
                pagedata_qset,
                PageUnGradedInfoSearchWidget(
                    attrs={
                        'data-placeholder':
                            _("Pages, "
                              "ordered by user's last name.")}),
            )

    navigation_boxes = tuple(
        [navigation_box_graded, navigation_box_ungraded])  # type: ignore
    # }}}

    # {{{ enable flow session zapping by navigatioin button
    next_flow_session_id = None  # type: Optional[int]
    next_flow_session_ordinal = None  # type: Optional[int]
    prev_flow_session_id = None  # type: Optional[int]
    prev_flow_session_ordinal = None  # type: Optional[int]
    next_ungraded_flow_session_id = None  # type: Optional[int]
    next_ungraded_flow_session_ordinal = None  # type: Optional[int]

    def get_session_page_ordinal(flow_session_pk, group_id, page_id):
        # type:(int, Text, Text) -> int
        return (
            FlowPageData.objects.get(
                flow_session__pk=flow_session_pk,
                group_id=group_id,
                page_id=page_id,
                page_ordinal__isnull=False,
            ).page_ordinal)

    for i, other_flow_session_pk in enumerate(all_flow_session_pks):
        if other_flow_session_pk == flow_session.pk:
            if i > 0:
                prev_flow_session_id = cast(int, all_flow_session_pks[i-1])
                try:
                    prev_flow_session_ordinal = (
                        get_session_page_ordinal(
                            prev_flow_session_id, group_id, page_id))
                except ObjectDoesNotExist:
                    prev_flow_session_ordinal = page_ordinal
            if i + 1 < len(all_flow_session_pks):
                next_flow_session_id = cast(int, all_flow_session_pks[i+1])
                try:
                    next_flow_session_ordinal = (
                        get_session_page_ordinal(
                            next_flow_session_id, group_id, page_id))
                except ObjectDoesNotExist:
                    next_flow_session_ordinal = page_ordinal

            if grading_form:
                from itertools import chain
                next_ungraded_flow_session_id = None
                for j in chain(
                        range(i + 1, len(all_flow_session_pks)), range(i)):
                    if all_flow_session_pks[j] in ungraded_flow_session_pks:
                        next_ungraded_flow_session_id = (
                            cast(int, all_flow_session_pks[j]))
                        next_ungraded_flow_session_ordinal = (
                            get_session_page_ordinal(
                                next_ungraded_flow_session_id,
                                group_id, page_id))
                        break
            break

    # }}}

    # {{{ Warn if the viewed page/session will not be counted in the
    # final score of the flow.due to distinct and
    # grade_aggregation_strategy.use_latest/use_earliest

    session_not_for_grading_warning_html = None

    if (grading_form
        and
                flow_session.pk not in all_flow_session_pks):

        available_pagedata = FlowPageData.objects.get(
            flow_session_id__in=all_flow_session_pks,
            page_id=page_id,
            flow_session__user=flow_session.user
        )
        from django.urls import reverse
        uri = reverse("relate-grade_flow_page",
                      args=(
                          pctx.course_identifier,
                          available_pagedata.flow_session.id,
                          available_pagedata.page_ordinal))

        user = flow_session.user
        if may_view_participant_full_profile:
            username = (
                user.get_full_name()
                if (user.first_name
                    and user.last_name)
                else user.username)
        else:
            username = user.get_masked_profile()

        from django.utils.safestring import mark_safe
        session_not_for_grading_warning_html = mark_safe(
            _("This page and session will not be counted into %(username)s's "
              "grading of this flow, see %(url)s instead.")
            % {
                "username": username,
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
                "page_ordinal": fpctx.page_ordinal,
                "page_data": fpctx.page_data,

                "body": fpctx.page.body(
                    fpctx.page_context, fpctx.page_data.data),
                "form": form,
                "form_html": form_html,
                "feedback": feedback,
                "max_points": max_points,
                "points_awarded": points_awarded,
                "shown_grade": shown_grade,
                "prev_grade_id": prev_grade_id,
                "expects_answer": page_expects_answer,

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


                # Wrappers used by JavaScript template (tmpl) so as not to
                # conflict with Django template's tag wrapper
                "JQ_OPEN": '{%',
                'JQ_CLOSE': '%}',
            })


@retry_transaction_decorator()
def _save_grade(
        fpctx,  # type: FlowPageContext
        flow_session,  # type: FlowSession
        most_recent_grade,  # type: FlowPageVisitGrade
        bulk_feedback_json,  # type: Any
        now_datetime,  # type: datetime.datetime
        ):
    # type: (...) -> int
    most_recent_grade.save()
    most_recent_grade_id = most_recent_grade.id

    update_bulk_feedback(
            fpctx.prev_answer_visit.page_data,
            most_recent_grade,
            bulk_feedback_json)

    grading_rule = get_session_grading_rule(
            flow_session, fpctx.flow_desc, now_datetime)

    from course.flow import grade_flow_session
    grade_flow_session(fpctx, flow_session, grading_rule)

    return most_recent_grade_id

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

    # tuples: (page_ordinal, id)
    pages = set()

    counts = {}
    grader_counts = {}
    page_counts = {}

    def commit_grade_info(grade):
        grader = grade.grader
        page = (grade.visit.page_data.page_ordinal,
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
