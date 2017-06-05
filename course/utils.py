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

import six
import datetime  # noqa
import pytz

from typing import cast

from django.shortcuts import (  # noqa
        render, get_object_or_404)
from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import (
        ugettext as _, string_concat, pgettext_lazy)

from codemirror import CodeMirrorTextarea, CodeMirrorJavascript

from course.content import (
        get_course_repo, get_flow_desc,
        parse_date_spec, get_course_commit_sha)
from course.constants import (
        flow_permission, flow_rule_kind)
import dulwich.repo
from course.content import (  # noqa
        FlowDesc,
        FlowPageDesc,
        FlowSessionAccessRuleDesc
        )
from course.page.base import (  # noqa
        PageBase,
        PageContext,
        )

MIN_DATETIME = pytz.utc.localize(datetime.datetime.min)
MAX_DATETIME = pytz.utc.localize(datetime.datetime.max)

# {{{ mypy

if False:
    from typing import Tuple, List, Text, Iterable, Any, Optional, Union, Dict  # noqa
    from relate.utils import Repo_ish  # noqa
    from course.models import (  # noqa
            Course,
            Participation,
            ExamTicket,
            FlowSession,
            FlowPageData,
            )
    from course.content import FlowSessionNotifyRuleDesc  # noqa

# }}}


def getattr_with_fallback(aggregates, attr_name, default=None):
    # type: (Iterable[Any], Text, Any) -> Any
    for agg in aggregates:
        result = getattr(agg, attr_name, None)
        if result is not None:
            return result

    return default


# {{{ flow permissions

class FlowSessionRuleBase(object):
    pass


class FlowSessionStartRule(FlowSessionRuleBase):
    def __init__(
            self,
            tag_session=None,  # type: Optional[Text]
            may_start_new_session=None,  # type: Optional[bool]
            may_list_existing_sessions=None,  # type: Optional[bool]
            # {{{ added by zd
            latest_start_datetime=None,
            session_available_count=None,
            # }}}
            default_expiration_mode=None,  # type: Optional[Text]
            ):
        # type: (...) -> None
        self.tag_session = tag_session
        self.may_start_new_session = may_start_new_session
        self.may_list_existing_sessions = may_list_existing_sessions
        self.default_expiration_mode = default_expiration_mode
        self.latest_start_datetime = latest_start_datetime
        self.session_available_count = session_available_count


class FlowSessionNotifyRule(FlowSessionRuleBase):
    def __init__(
            self,
            may_send_notification=None,  # type: Optional[bool]
            message=None,  # type: Optional[Text]
            ):
        # type: (...) -> None
        self.may_send_notification = may_send_notification
        self.message = message


class FlowSessionAccessRule(FlowSessionRuleBase):
    def __init__(
            self,
            permissions,  # type: frozenset[Text]
            message=None,  # type: Optional[Text]
            ):
        # type: (...) -> None
        self.permissions = permissions
        self.message = message

    def human_readable_permissions(self):
        from course.models import FLOW_PERMISSION_CHOICES
        permission_dict = dict(FLOW_PERMISSION_CHOICES)
        return [permission_dict[p] for p in self.permissions]


class FlowSessionGradingRule(FlowSessionRuleBase):
    def __init__(
            self,
            grade_identifier,  # type: Optional[Text]
            grade_aggregation_strategy,  # type: Text

            # added by zd
            completed_before,  # type: Optional[datetime.datetime]
            due,  # type: Optional[datetime.datetime]
            generates_grade,  # type: bool
            description=None,  # type: Optional[Text]
            credit_percent=None,  # type: Optional[float]
            use_last_activity_as_completion_time=None,  # type: Optional[bool]
            max_points=None,  # type: Optional[float]
            max_points_enforced_cap=None,  # type: Optional[float]
            bonus_points=None,  # type: Optional[float]

            # credit precent of next rule, added by zd
            credit_next=None,  # type: Optional[float]
            # next rule is deadline # added by zd
            is_next_final=None,  # type: bool
            ):
        # type: (...) -> None

        self.grade_identifier = grade_identifier
        self.grade_aggregation_strategy = grade_aggregation_strategy
        self.due = due
        self.generates_grade = generates_grade
        self.description = description
        self.credit_percent = credit_percent
        self.use_last_activity_as_completion_time = \
                use_last_activity_as_completion_time
        self.max_points = max_points
        self.max_points_enforced_cap = max_points_enforced_cap
        self.bonus_points = bonus_points
        self.completed_before = completed_before
        self.credit_next = credit_next
        self.is_next_final = is_next_final

    def __eq__(self, other):
        return (
            self.generates_grade == other.generates_grade
            and
            self.credit_percent == other.credit_percent
            and
            self.max_points == other.max_points
            and
            self.max_points_enforced_cap == other.max_points_enforced_cap
            and
            self.bonus_points == other.bonus_points
        )


def _eval_generic_conditions(
        rule,  # type: Any
        course,  # type: Course
        participation,  # type: Optional[Participation]
        now_datetime,  # type: datetime.datetime
        flow_id,  # type: Text
        login_exam_ticket,  # type: Optional[ExamTicket]
        ):
    # type: (...) -> bool

    if hasattr(rule, "if_before"):
        ds = parse_date_spec(course, rule.if_before)
        if not (now_datetime <= ds):
            return False

    if hasattr(rule, "if_after"):
        ds = parse_date_spec(course, rule.if_after)
        if not (now_datetime >= ds):
            return False

    if hasattr(rule, "if_has_role"):
        from course.enrollment import get_participation_role_identifiers
        roles = get_participation_role_identifiers(course, participation)
        if all(role not in rule.if_has_role for role in roles):
            return False

    if (hasattr(rule, "if_signed_in_with_matching_exam_ticket")
            and rule.if_signed_in_with_matching_exam_ticket):
        if login_exam_ticket is None:
            return False
        if login_exam_ticket is None:
            return False
        if login_exam_ticket.exam.flow_id != flow_id:
            return False

    return True


def _eval_generic_session_conditions(
        rule,  # type: Any
        session,  # type: FlowSession
        now_datetime,  # type: datetime.datetime
        ):
    # type: (...) -> bool

    if hasattr(rule, "if_has_tag"):
        if session.access_rules_tag != rule.if_has_tag:
            return False

    if hasattr(rule, "if_started_before"):
        ds = parse_date_spec(session.course, rule.if_started_before)
        if not session.start_time < ds:
            return False

    return True


def _eval_participation_tags_conditions(
        rule,  # type: Any
        participation,  # type: Optional[Participation]
        ):
    # type: (...) -> bool

    participation_tags_any_set = (
        set(getattr(rule, "if_has_participation_tags_any", [])))
    participation_tags_all_set = (
        set(getattr(rule, "if_has_participation_tags_all", [])))

    if participation_tags_any_set or participation_tags_all_set:
        if not participation:
            # Return False for anonymous users if only
            # if_has_participation_tags_any or if_has_participation_tags_all
            # is not empty.
            return False
        ptag_set = set(participation.tags.all().values_list("name", flat=True))
        if not ptag_set:
            return False
        if (participation_tags_any_set
            and
                not participation_tags_any_set & ptag_set):
            return False
        if (participation_tags_all_set
            and
                not participation_tags_all_set <= ptag_set):
            return False

    return True


def get_flow_rules(
        flow_desc,  # type: FlowDesc
        kind,  # type: Text
        participation,  # type: Optional[Participation]
        flow_id,  # type: Text
        now_datetime,  # type: datetime.datetime
        consider_exceptions=True,  # type: bool
        default_rules_desc=[]  # type: List[Any]
        ):
    # type: (...) -> List[Any]

    if (not hasattr(flow_desc, "rules")
            or not hasattr(flow_desc.rules, kind)):
        rules = default_rules_desc[:]
    else:
        rules = getattr(flow_desc.rules, kind)[:]

    from course.models import FlowRuleException
    if consider_exceptions:
        for exc in (
                FlowRuleException.objects
                .filter(
                    participation=participation,
                    active=True,
                    kind=kind,
                    flow_id=flow_id)
                # rules created first will get inserted first, and show up last
                .order_by("creation_time")):

            if exc.expiration is not None and now_datetime > exc.expiration:
                continue

            from relate.utils import dict_to_struct
            rules.insert(0, dict_to_struct(exc.rule))

    return rules

# {{{ added by zd

def get_flow_may_start_desc(
        course,  # type: Course
        participation,  # type: Optional[Participation]
        flow_id,  # type: Text
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[frozenset[Text]]
        for_rollover=False,  # type: bool
        login_exam_ticket=None,  # type: Optional[ExamTicket]
        rules_only=False,  # type: bool
    ):

    rules = get_session_start_rule(
        course,
        participation,
        flow_id,
        flow_desc,
        now_datetime,
        rules_only=True
    )

    assert isinstance(rules, list)

    time_point_set = set()
    time_point_set.add(MIN_DATETIME)
    for rule in rules:
        if hasattr(rule, "if_before"):
            time_point_set.add(parse_date_spec(course, rule.if_before))
        if hasattr(rule, "if_after"):
            time_point_set.add(parse_date_spec(course, rule.if_after))
    time_point_list = sorted(list(time_point_set))

    def check_may_start(test_datetime):
        start_rule = get_session_start_rule(
            course,
            participation,
            flow_id,
            flow_desc,
            now_datetime=test_datetime,
            facilities=facilities,
            for_rollover=for_rollover,
            login_exam_ticket=login_exam_ticket,
        )
        return start_rule.may_start_new_session

    may_start_list = []
    for t in time_point_list:
        test_time = t + datetime.timedelta(microseconds=1)
        may_start = check_may_start(test_time)
        may_start_list.append(may_start)

    may_start_zip = list(zip(may_start_list,time_point_list))
    may_start_zip_merged = []
    for i, z in enumerate(may_start_zip):
        try:
            if i == 0:
                may_start_zip_merged.append(z)
            elif z[0] != may_start_zip[i-1][0]:
                may_start_zip_merged.append(z)
        except IndexError:
            may_start_zip_merged.append(z)

    time_range_list = []
    for i, z in enumerate(may_start_zip_merged):
        if z[0] == True:
            start = may_start_zip_merged[i][1]
            try:
                end = may_start_zip_merged[i + 1][1]
            except IndexError:
                end = MAX_DATETIME

            rule_is_active = False
            if start <= now_datetime <= end:
                rule_is_active = True

            time_range_list.append((start, end, rule_is_active))

    trl_full_str = ""
    if time_range_list:
        from relate.utils import dict_to_struct, compact_local_datetime_str
        for trl in time_range_list:
            trl_str = ""
            start = trl[0]
            end = trl[1]
            rule_is_active = trl[2]
            if start != MIN_DATETIME and end != MAX_DATETIME:
                trl_str += _("From %(start)s to %(end)s") % {
                    "start": compact_local_datetime_str(start, now_datetime),
                    "end": compact_local_datetime_str(end, now_datetime)
                }
            elif start == MIN_DATETIME and end != MAX_DATETIME:
                trl_str += _("Before %(end)s") % {
                    "end": compact_local_datetime_str(end, now_datetime)
                }
            elif start != MIN_DATETIME and end == MAX_DATETIME:
                trl_str += _("After %(start)s") % {
                    "start": compact_local_datetime_str(start, now_datetime)
                }
            else:
                continue

            if rule_is_active:
                trl_str = "<strong class='text-danger'>%s</strong>" % trl_str

            trl_full_str += "<li>%s</li>" % trl_str

    if trl_full_str:
        trl_full_str = (
            string_concat(
                "<li><span class='h4'>",
                _("When sessions might start"),
                "</span><ul>%s</ul></li>"
            ) % trl_full_str)

    return trl_full_str


def get_session_grading_desc(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        generate_full_desc=False,  # type: bool
    ):

    rules = get_session_grading_rule(
        session,
        flow_desc,
        now_datetime,
        rules_only=True
    )

    assert isinstance(rules, list)

    time_point_set = set()
    time_point_set.add(MIN_DATETIME)
    for rule in rules:
        if hasattr(rule, "if_before"):
            time_point_set.add(parse_date_spec(session.course, rule.if_before))
        if hasattr(rule, "if_after"):
            time_point_set.add(parse_date_spec(session.course, rule.if_after))
        if hasattr(rule, "if_started_before"):
            time_point_set.add(parse_date_spec(session.course, rule.if_started_before))
        if hasattr(rule, "if_completed_before"):
            time_point_set.add(parse_date_spec(session.course, rule.if_completed_before))
    time_point_list = sorted(list(time_point_set))

    def get_test_grading_rule(test_datetime):
        grading_rule = get_session_grading_rule(
            session,  # type: FlowSession
            flow_desc,  # type: FlowDesc
            test_datetime,  # type: datetime.datetime
        )
        return grading_rule

    grading_rule_list = []
    for t in time_point_list:
        test_time = t + datetime.timedelta(microseconds=1)
        g_rule = get_test_grading_rule(test_time)
        grading_rule_list.append(g_rule)

    g_rule_zip = list(zip(grading_rule_list,time_point_list))
    g_rule_zip_merged = []
    for i, z in enumerate(g_rule_zip):
        try:
            if i == 0:
                g_rule_zip_merged.append(z)
            elif z[0] != g_rule_zip[i-1][0]:
                g_rule_zip_merged.append(z)
        except IndexError:
            g_rule_zip_merged.append(z)

    g_rule_time_range_list = []
    for i, z in enumerate(g_rule_zip_merged):
        if z[0].generates_grade:
            start = g_rule_zip_merged[i][1]
            if now_datetime < start and not generate_full_desc:
                continue
            try:
                end = g_rule_zip_merged[i + 1][1]
                next_rule = g_rule_zip_merged[i + 1][0]
            except IndexError:
                end = MAX_DATETIME
                next_rule = FlowSessionGradingRule(
                    grade_identifier=None,
                    grade_aggregation_strategy="",
                    completed_before=None,
                    due=None,
                    generates_grade=False,
                    credit_percent=0,
                )

            rule_is_active = False
            if start <= now_datetime <= end:
                rule_is_active = True
            if (
                    (not generate_full_desc and rule_is_active)
                or
                    generate_full_desc):
                g_rule_time_range_list.append(
                    (start, end, z[0], next_rule, rule_is_active))

    g_rule_trl_full_str = ""
    if g_rule_time_range_list:
        flow_page_grading_info = ""
        from relate.utils import dict_to_struct, compact_local_datetime_str
        from django.utils.timesince import timeuntil
        for trl in g_rule_time_range_list:
            trl_str = ""
            start = trl[0]
            end = trl[1]
            g_rule = trl[2]
            next_rule = trl[3]
            rule_is_active = trl[4]

            started_before = getattr(g_rule, "if_started_before", "")
            if started_before:
                started_before = (
                    string_concat(
                        "(",
                        _("started before %s"),
                        ")"
                    ) % compact_local_datetime_str(
                        started_before, now_datetime))

            credit_expected = None

            if g_rule.credit_percent:
                credit_expected = (
                    _("<b>%(credit_percent)d%%</b> of the grade")
                    % {"credit_percent": g_rule.credit_percent}
                )
            if g_rule.max_points:
                max_points = g_rule.max_points
                if g_rule.max_points_enforced_cap:
                    max_points = min(max_points, g_rule.max_points_enforced_cap)
                credit_expected = (
                    _(" at most <b>%(max_points)d%</b> points")
                    % {"max_points": max_points}
                )
            if g_rule.bonus_points:
                credit_expected += (
                    _("(including %(bonus_points)s bonus points)")
                    % {"bonus_points": g_rule.bonus_points}
                )

            if end != MAX_DATETIME:
                if not credit_expected:
                    if not generate_full_desc:
                        flow_page_grading_info = (
                            string_concat(
                                _("You will <b>NOT</b> "
                                  "receive grade for this session "
                                  "if completed before "
                                  "%(completed_before)s."), " ")
                            %  {
                                "completed_before": compact_local_datetime_str(
                                    end, now_datetime)})
                    else:
                        flow_page_grading_info = (
                            string_concat(
                                _("You will <b>NOT</b> "
                                  "receive grade for the new session"
                                  "%(started_before)s "
                                  "if completed before "
                                  "%(completed_before)s."), " ")
                            %  {
                                "started_before": started_before,
                                "completed_before": compact_local_datetime_str(
                                    end, now_datetime)})
                else:
                    if not generate_full_desc:
                        flow_page_grading_info = (
                            string_concat(
                                _("You have <b>%(time_remain)s</b> (before <b>"
                                  "%(completed_before)s</b>) to submit "
                                  "this session to "
                                  "get %(credit_expected)s."), " ") %
                            {
                                "time_remain": timeuntil(end, now_datetime),
                                "completed_before": compact_local_datetime_str(
                                    end, now_datetime),
                                "credit_expected": credit_expected})
                    else:
                        flow_page_grading_info = (
                            string_concat(
                                _("You will get %(credit_expected)s "
                                  "if the new session"
                                  "%(started_before)s "
                                  "is submmited before <b>"
                                  "%(completed_before)s</b>."), " ") %
                            {
                                "started_before": started_before,
                                "completed_before": compact_local_datetime_str(
                                    end, now_datetime),
                                "credit_expected": credit_expected})
            else:
                if not credit_expected:
                    if not generate_full_desc:
                        flow_page_grading_info = (
                            string_concat(
                                _("You will <b>NOT</b> "
                                  "receive grade for this session."), " ")
                        )
                    else:
                        flow_page_grading_info = (
                            string_concat(
                                _("You will <b>NOT</b> "
                                  "receive grade for the new session "
                                  "%(started_before)s "
                                  "since %(start_time)s."), " ")
                            % {
                                "started_before": started_before,
                                "start_time": compact_local_datetime_str(
                                    start, now_datetime)}
                        )
                else:
                    if not generate_full_desc:
                        flow_page_grading_info = (
                            string_concat(
                                _("You are supposed to get "
                                  "<b>%(credit_expected)s</b> "
                                  "by submitting this session."), " ") %
                            {
                                "credit_expected": credit_expected})
                    else:
                        flow_page_grading_info = (
                            string_concat(
                                _("You are supposed to get "
                                  "<b>%(credit_expected)s</b> "
                                  "by submitting the new session"
                                  "%(started_before)s"
                                  "."), " ") %
                            {
                                "started_before": started_before,
                                "credit_expected": credit_expected})

            if (not next_rule.generates_grade
                or
                        next_rule.credit_percent == 0
                or
                        next_rule.max_points == 0
                or
                        next_rule.max_points_enforced_cap == 0):
                if not generate_full_desc:
                    flow_page_grading_info += (
                        _("Afterward, this session will <b>NOT</b> receive grade.")
                        + " ")
                    return flow_page_grading_info

            else:
                if not generate_full_desc:
                    credit_expected_next = None

                    if next_rule.credit_percent:
                        credit_expected_next = (
                            _("<b>%(credit_percent)d%%</b> of the grade")
                            % {"credit_percent": next_rule.credit_percent}
                        )
                    if next_rule.max_points:
                        max_points_next = g_rule.max_points
                        if g_rule.max_points_enforced_cap:
                            max_points_next = min(max_points_next, g_rule.max_points_enforced_cap)
                            credit_expected_next = (
                            _(" at most <b>%(max_points)d%</b> points")
                            % {"max_points": max_points_next}
                        )
                    if next_rule.bonus_points:
                        credit_expected_next += (
                            _("(including %(bonus_points)s bonus points)")
                            % {"bonus_points": next_rule.bonus_points}
                        )

                    flow_page_grading_info += (
                        string_concat(_("Afterward this session will receive no "
                                        "more than %(credit_expected_next)s."),
                                      " ")
                        % {"credit_expected_next": credit_expected_next})

                    return flow_page_grading_info

            if rule_is_active and generate_full_desc:
                flow_page_grading_info = (
                    "<strong class='text-danger'>%s</strong>"
                    % flow_page_grading_info)

            g_rule_trl_full_str += "<li>%s</li>" % flow_page_grading_info

    if g_rule_trl_full_str and generate_full_desc:
        g_rule_trl_full_str = (
            string_concat(
                "<li><span class='h4'>",
                _("The expected gradings for a new session"),
                "</span><ul>%s</ul></li>"
            ) % g_rule_trl_full_str)

    print(g_rule_trl_full_str.encode('utf-8'))
    return g_rule_trl_full_str

# }}}


# {{{ added by zd to generate stringified rules in flow start page

def get_flow_rules_str(
        course,  # type: Course
        participation,  # type: Optional[Participation]
        flow_id,  # type: Text
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        ):
    # type: (...) -> Text

    from relate.utils import dict_to_struct, compact_local_datetime_str
    # {{{ get stringified latest_start_datetime
    start_rules = get_flow_rules(flow_desc, flow_rule_kind.start,
            participation, flow_id, now_datetime,
            default_rules_desc=[
                dict_to_struct(dict(
                    may_start_new_session=True,
                    may_list_existing_sessions=False))])

    latest_start_datetime = None

    for rule in start_rules:
        if (hasattr(rule, "if_before")
            and
                hasattr(rule, "may_start_new_session")):
            if getattr(rule, "may_start_new_session"):
                # {{{ temp solution
                if not _eval_participation_tags_conditions(rule, participation):
                    continue
                # }}}
                latest_start_datetime = parse_date_spec(course, rule.if_before)

    latest_start_datetime_str = None

    if latest_start_datetime:
        latest_start_datetime_str = compact_local_datetime_str(
                latest_start_datetime, now_datetime)

    if latest_start_datetime_str:
        latest_start_datetime_str = (
            string_concat("<li><span class='h4'>",
                          _("Latest start time"),
                          "</span><ul><li class='text-danger'><strong>",
                          _("Session(s) must start before %s."),
                          "</strong></li></ul></li>")
            % latest_start_datetime_str)
    # }}}

    # {{{ get stringified grade_rule
    grade_rules = get_flow_rules(flow_desc, flow_rule_kind.grading,
        participation, flow_id, now_datetime,
        default_rules_desc=[
            dict_to_struct(dict(
                grade_identifier=None,
                ))])

    date_grading_tuple = tuple()  # type: Tuple[Dict[Any, Any], ...]

    for rule in grade_rules:
        if hasattr(rule, "if_completed_before"):
            # {{{ temp solution
            if hasattr(rule, "if_has_participation_tags_any"):
                if not _eval_participation_tags_conditions(rule, participation):
                    continue
            # }}}
            ds = parse_date_spec(course, rule.if_completed_before)
            due = parse_date_spec(course, getattr(rule, "due", None))
            credit_percent = getattr(rule, "credit_percent", 100)
            date_grading_tuple = (
                date_grading_tuple + (
                    {"complete_before": ds,
                     "due": due,
                     "credit_percent": credit_percent
                     },))

    grade_rule_str = ""
    datetime_str = ""

    for rule in date_grading_tuple:
        datetime_str = compact_local_datetime_str(
                rule["complete_before"],
                now_datetime)
        grade_rule_str += string_concat(
                "<li>",
                _("If completed before %(time)s, you'll get "
                "%(credit_percent)s%% of your grade."),
                "</li>") % {
                        "time": datetime_str,
                        "credit_percent": rule["credit_percent"]}

    if grade_rule_str:
        grade_rule_str = (
            string_concat("<li><span class='h4'>",
                          _("Submission time and Grading"),
                          "</span><ul>")
            + grade_rule_str
            + string_concat("<li class='text-danger'><strong>",
                            _("No grade will be granted for "
                            "submision later than %s."),
                            "</strong></li></ul></li>") % datetime_str)

    flow_rule_str = ""

    if latest_start_datetime_str:
        flow_rule_str += latest_start_datetime_str
    if grade_rule_str:
        flow_rule_str += grade_rule_str

    if flow_rule_str:
        flow_rule_str = "<ul>" + flow_rule_str + "</ul>"

    return flow_rule_str

# }}}


def get_session_start_rule(
        course,  # type: Course
        participation,  # type: Optional[Participation]
        flow_id,  # type: Text
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[frozenset[Text]]
        for_rollover=False,  # type: bool
        login_exam_ticket=None,  # type: Optional[ExamTicket]
        rules_only=False,  # type: bool
        ):
    # type: (...) -> Union[List[Any], FlowSessionStartRule]

    """Return a :class:`FlowSessionStartRule` if a new session is
    permitted or *None* if no new session is allowed.
    """

    if facilities is None:
        facilities = frozenset()

    from relate.utils import dict_to_struct
    rules = get_flow_rules(flow_desc, flow_rule_kind.start,
            participation, flow_id, now_datetime,
            default_rules_desc=[
                dict_to_struct(dict(
                    may_start_new_session=True,
                    may_list_existing_sessions=False))])

    if rules_only:
        return rules

    # {{{ added by zd
    latest_start_datetime = None
    session_available_count = 0
    # }}}

    from course.models import FlowSession  # noqa
    for rule in rules:

        # {{{ added by zd
        if (hasattr(rule, "if_before")
            and
                hasattr(rule, "may_start_new_session")):
            if getattr(rule, "may_start_new_session"):
                latest_start_datetime = parse_date_spec(course, rule.if_before)
        # }}}
        if not _eval_generic_conditions(rule, course, participation,
                now_datetime, flow_id=flow_id,
                login_exam_ticket=login_exam_ticket):
            continue

        if not _eval_participation_tags_conditions(rule, participation):
            continue

        if not for_rollover and hasattr(rule, "if_in_facility"):
            if rule.if_in_facility not in facilities:
                continue

        if not for_rollover and hasattr(rule, "if_has_in_progress_session"):
            session_count = FlowSession.objects.filter(
                    participation=participation,
                    course=course,
                    flow_id=flow_id,
                    in_progress=True).count()

            if bool(session_count) != rule.if_has_in_progress_session:
                continue

        if not for_rollover and hasattr(rule, "if_has_session_tagged"):
            tagged_session_count = FlowSession.objects.filter(
                    participation=participation,
                    course=course,
                    access_rules_tag=rule.if_has_session_tagged,
                    flow_id=flow_id).count()

            if not tagged_session_count:
                continue

        if not for_rollover and hasattr(rule, "if_has_fewer_sessions_than"):
            session_count = FlowSession.objects.filter(
                    participation=participation,
                    course=course,
                    flow_id=flow_id).count()

            # {{{ added by zd
            session_available_count = (
                    rule.if_has_fewer_sessions_than - session_count)
            # }}}

            if session_count >= rule.if_has_fewer_sessions_than:
                continue

        if not for_rollover and hasattr(rule, "if_has_fewer_tagged_sessions_than"):
            tagged_session_count = FlowSession.objects.filter(
                    participation=participation,
                    course=course,
                    access_rules_tag__isnull=False,
                    flow_id=flow_id).count()

            if tagged_session_count >= rule.if_has_fewer_tagged_sessions_than:
                continue

        return FlowSessionStartRule(
                tag_session=getattr(rule, "tag_session", None),
                may_start_new_session=getattr(
                    rule, "may_start_new_session", True),
                may_list_existing_sessions=getattr(
                    rule, "may_list_existing_sessions", True),
                # {{{ added by zd
                latest_start_datetime=latest_start_datetime,
                session_available_count=session_available_count,
                # }}}
                default_expiration_mode=getattr(
                    rule, "default_expiration_mode", None),
                )

    return FlowSessionStartRule(
            may_list_existing_sessions=False,
            may_start_new_session=False,
            latest_start_datetime=latest_start_datetime)     # added by zd


def get_session_access_rule(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[frozenset[Text]]
        login_exam_ticket=None,  # type: Optional[ExamTicket]
        rules_only=False,  # type: bool
        ):
    # type: (...) -> Union[List[Any], FlowSessionAccessRule]
    """Return a :class:`ExistingFlowSessionRule`` to describe
    how a flow may be accessed.
    """

    if facilities is None:
        facilities = frozenset()

    from relate.utils import dict_to_struct
    rules = get_flow_rules(flow_desc, flow_rule_kind.access,
            session.participation, session.flow_id, now_datetime,
            default_rules_desc=[
                dict_to_struct(dict(
                    permissions=[flow_permission.view],
                    ))])  # type: List[FlowSessionAccessRuleDesc]

    if rules_only:
        return rules

    for rule in rules:
        if not _eval_generic_conditions(
                rule, session.course, session.participation,
                now_datetime, flow_id=session.flow_id,
                login_exam_ticket=login_exam_ticket):
            continue

        if not _eval_participation_tags_conditions(rule, session.participation):
            continue

        if not _eval_generic_session_conditions(rule, session, now_datetime):
            continue

        if hasattr(rule, "if_in_facility"):
            if rule.if_in_facility not in facilities:
                continue

        if hasattr(rule, "if_in_progress"):
            if session.in_progress != rule.if_in_progress:
                continue

        if hasattr(rule, "if_expiration_mode"):
            if session.expiration_mode != rule.if_expiration_mode:
                continue

        if hasattr(rule, "if_session_duration_shorter_than_minutes"):
            duration_min = (now_datetime - session.start_time).total_seconds() / 60

            if session.participation is not None:
                duration_min /= float(session.participation.time_factor)

            if duration_min > rule.if_session_duration_shorter_than_minutes:
                continue

        permissions = set(rule.permissions)

        # {{{ deal with deprecated permissions

        if "modify" in permissions:
            permissions.remove("modify")
            permissions.update([
                flow_permission.submit_answer,
                flow_permission.end_session,
                ])

        if "see_answer" in permissions:
            permissions.remove("see_answer")
            permissions.add(flow_permission.see_answer_after_submission)

        # }}}

        # Remove 'modify' permission from not-in-progress sessions
        if not session.in_progress:
            for perm in [
                    flow_permission.submit_answer,
                    flow_permission.end_session,
                    ]:
                if perm in permissions:
                    permissions.remove(perm)

        return FlowSessionAccessRule(
                permissions=frozenset(permissions),
                message=getattr(rule, "message", None)
                )

    return FlowSessionAccessRule(permissions=frozenset())


def get_session_notify_rule(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[frozenset[Text]]
        login_exam_ticket=None,  # type: Optional[ExamTicket]
        ):
    # type: (...) -> FlowSessionNotifyRule
    """Return a :class:`FlowSessionNotifyRule` if submission of
    a session is expected to send notification else *None*.
    """

    if facilities is None:
        facilities = frozenset()

    from relate.utils import dict_to_struct
    rules = get_flow_rules(flow_desc, flow_rule_kind.notify,
            session.participation, session.flow_id, now_datetime,
            default_rules_desc=[
                dict_to_struct(dict(
                    notify=False,
                    ))])  # type: List[FlowSessionNotifyRuleDesc]

    from course.enrollment import get_participation_role_identifiers
    roles = get_participation_role_identifiers(session.course, session.participation)
    session_notify_rule = None

    for rule in rules:
        if not _eval_generic_conditions(
                rule, session.course, session.participation,
                now_datetime, flow_id=session.flow_id,
                login_exam_ticket=login_exam_ticket):
            continue

        if not _eval_generic_session_conditions(rule, session, now_datetime):
            continue

        if hasattr(rule, "if_has_role"):
            if all(role not in rule.if_has_role for role in roles):
                continue

        if hasattr(rule, "if_in_facility"):
            if rule.if_in_facility not in facilities:
                continue

        if not getattr(rule, "will_notify", False):
            continue

        if session_notify_rule is None:
            return FlowSessionNotifyRule(
                    may_send_notification=True,
                    message=getattr(rule, "message", None)
                    )

    return FlowSessionNotifyRule(may_send_notification=False,
                                 message=None)


def get_session_grading_rule(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        rules_only = False,  # type: bool
        ):
    # type: (...) -> Union[List[Any], FlowSessionGradingRule]

    flow_desc_rules = getattr(flow_desc, "rules", None)

    from relate.utils import dict_to_struct
    rules = get_flow_rules(flow_desc, flow_rule_kind.grading,
            session.participation, session.flow_id, now_datetime,
            default_rules_desc=[
                dict_to_struct(dict(
                    generates_grade=False,
                    ))])

    if rules_only:
        return rules

    from course.enrollment import get_participation_role_identifiers
    roles = get_participation_role_identifiers(session.course, session.participation)
    session_grading_rule = None
    ds = None

    for i, rule in enumerate(rules):
        credit_next = 100
        is_next_final = False
        if i < len(rules) - 2:
            credit_next = getattr(rules[i+1], "credit_percent", 100)
            is_next_final = False
        else:
            credit_next = 0
            is_next_final = True

        if hasattr(rule, "if_has_role"):
            if all(role not in rule.if_has_role for role in roles):
                continue

        if not _eval_generic_session_conditions(rule, session, now_datetime):
            continue

        if not _eval_participation_tags_conditions(rule, session.participation):
            continue

        if hasattr(rule, "if_completed_before"):
            ds = parse_date_spec(session.course, rule.if_completed_before)
            if session.in_progress and now_datetime > ds:
                continue
            if not session.in_progress and session.completion_time > ds:
                continue

        due = parse_date_spec(session.course, getattr(rule, "due", None))
        if due is not None:
            assert due.tzinfo is not None

        generates_grade = getattr(rule, "generates_grade", True)

        grade_identifier = None
        grade_aggregation_strategy = None
        if flow_desc_rules is not None:
            grade_identifier = flow_desc_rules.grade_identifier
            grade_aggregation_strategy = getattr(
                    flow_desc_rules, "grade_aggregation_strategy", None)

        bonus_points = getattr_with_fallback((rule, flow_desc), "bonus_points", 0)
        max_points = getattr_with_fallback((rule, flow_desc), "max_points", None)
        max_points_enforced_cap = getattr_with_fallback(
                (rule, flow_desc), "max_points_enforced_cap", None)

        if session_grading_rule is None:
            session_grading_rule = FlowSessionGradingRule(
                grade_identifier=grade_identifier,
                grade_aggregation_strategy=grade_aggregation_strategy,
                due=due,
                generates_grade=generates_grade,
                description=getattr(rule, "description", None),
                credit_percent=getattr(rule, "credit_percent", 100),
                use_last_activity_as_completion_time=getattr(
                    rule, "use_last_activity_as_completion_time", False),

                bonus_points=bonus_points,
                max_points=max_points,
                max_points_enforced_cap=max_points_enforced_cap,

                completed_before=ds,     # added by zd
                credit_next=credit_next,    # added by zd
                is_next_final=is_next_final,    # added by zd
                )

    if session_grading_rule is None:
        raise RuntimeError(_("grading rule determination was unable to find "
                "a grading rule"))

    return session_grading_rule

# }}}


# {{{ contexts

class AnyArgumentType:  # noqa
    pass


ANY_ARGUMENT = AnyArgumentType()


class CoursePageContext(object):
    def __init__(self, request, course_identifier):
        # type: (http.HttpRequest, Text) -> None

        self.request = request
        self.course_identifier = course_identifier
        self._permissions_cache = None  # type: Optional[frozenset[Tuple[Text, Optional[Text]]]]  # noqa
        self._role_identifiers_cache = None  # type: Optional[List[Text]]

        from course.models import Course  # noqa
        self.course = get_object_or_404(Course, identifier=course_identifier)

        from course.enrollment import get_participation_for_request
        self.participation = get_participation_for_request(
                request, self.course)

        from course.views import check_course_state
        check_course_state(self.course, self.participation)

        self.course_commit_sha = get_course_commit_sha(
                self.course, self.participation)

        self.repo = get_course_repo(self.course)

        # logic duplicated in course.content.get_course_commit_sha
        sha = self.course.active_git_commit_sha.encode()

        if self.participation is not None:
            if self.participation.preview_git_commit_sha:
                preview_sha = self.participation.preview_git_commit_sha.encode()

                repo = get_course_repo(self.course)

                from relate.utils import SubdirRepoWrapper
                if isinstance(repo, SubdirRepoWrapper):
                    true_repo = repo.repo
                else:
                    true_repo = cast(dulwich.repo.Repo, repo)

                try:
                    true_repo[preview_sha]
                except KeyError:
                    from django.contrib import messages
                    messages.add_message(request, messages.ERROR,
                            _("Preview revision '%s' does not exist--"
                            "showing active course content instead.")
                            % preview_sha.decode())

                    preview_sha = None

                if preview_sha is not None:
                    sha = preview_sha

        self.course_commit_sha = sha

    def role_identifiers(self):
        # type: () -> List[Text]
        if self._role_identifiers_cache is not None:
            return self._role_identifiers_cache

        from course.enrollment import get_participation_role_identifiers
        self._role_identifiers_cache = get_participation_role_identifiers(
                self.course, self.participation)
        return self._role_identifiers_cache

    def permissions(self):
        # type: () -> frozenset[Tuple[Text, Optional[Text]]]
        if self.participation is None:
            if self._permissions_cache is not None:
                return self._permissions_cache

            from course.enrollment import get_participation_permissions
            perm = get_participation_permissions(self.course, self.participation)

            self._permissions_cache = perm

            return perm
        else:
            return self.participation.permissions()

    def has_permission(self, perm, argument=None):
        # type: (Text, Union[Text, AnyArgumentType, None]) -> bool
        if argument is ANY_ARGUMENT:
            return any(perm == p
                    for p, arg in self.permissions())
        else:
            return (perm, argument) in self.permissions()


class FlowContext(object):
    def __init__(self, repo, course, flow_id, participation=None):
        # type: (Repo_ish, Course, Text, Optional[Participation]) -> None

        """*participation* and *flow_session* are not stored and only used
        to figure out versioning of the flow content.
        """

        self.repo = repo
        self.course = course
        self.flow_id = flow_id

        from django.core.exceptions import ObjectDoesNotExist

        self.course_commit_sha = get_course_commit_sha(
                self.course, participation)

        try:
            self.flow_desc = get_flow_desc(self.repo, self.course,
                    flow_id, self.course_commit_sha)
        except ObjectDoesNotExist:
            raise http.Http404()


class PageOrdinalOutOfRange(http.Http404):
    pass


class FlowPageContext(FlowContext):
    """This object acts as a container for all the information that a flow page
    may need to render itself or respond to a POST.

    Note that this is different from :class:`course.page.PageContext`,
    which is used for in the page API.
    """

    def __init__(
            self,
            repo,  # type: Repo_ish
            course,  # type: Course
            flow_id,  # type: Text
            ordinal,  # type: int
            participation,  # type: Optional[Participation]
            flow_session,  # type: FlowSession
            request=None,  # type: Optional[http.HttpRequest]
            ):
        # type: (...) -> None
        super(FlowPageContext, self).__init__(repo, course, flow_id, participation)

        if ordinal >= flow_session.page_count:
            raise PageOrdinalOutOfRange()

        from course.models import FlowPageData  # noqa
        page_data = self.page_data = get_object_or_404(
                FlowPageData, flow_session=flow_session, ordinal=ordinal)

        from course.content import get_flow_page_desc
        try:
            self.page_desc = get_flow_page_desc(
                    flow_session, self.flow_desc, page_data.group_id,
                    page_data.page_id)  # type: Optional[FlowPageDesc]
        except ObjectDoesNotExist:
            self.page_desc = None
            self.page = None  # type: Optional[PageBase]
            self.page_context = None  # type: Optional[PageContext]
        else:
            self.page = instantiate_flow_page_with_ctx(self, page_data)

            page_uri = None
            if request is not None:
                from django.urls import reverse
                page_uri = request.build_absolute_uri(
                        reverse("relate-view_flow_page",
                            args=(course.identifier, flow_session.id, ordinal)))

            self.page_context = PageContext(
                    course=self.course, repo=self.repo,
                    commit_sha=self.course_commit_sha,
                    flow_session=flow_session,
                    page_uri=page_uri)

        self._prev_answer_visit = False

    @property
    def prev_answer_visit(self):
        if self._prev_answer_visit is False:
            from course.flow import get_prev_answer_visit
            self._prev_answer_visit = get_prev_answer_visit(self.page_data)

        return self._prev_answer_visit

    @property
    def ordinal(self):
        return self.page_data.ordinal


def instantiate_flow_page_with_ctx(fctx, page_data):
    # type: (FlowContext, FlowPageData) -> PageBase

    from course.content import get_flow_page_desc
    page_desc = get_flow_page_desc(
            fctx.flow_id, fctx.flow_desc,
            page_data.group_id, page_data.page_id)

    from course.content import instantiate_flow_page
    return instantiate_flow_page(
            "course '%s', flow '%s', page '%s/%s'"
            % (fctx.course.identifier, fctx.flow_id,
                page_data.group_id, page_data.page_id),
            fctx.repo, page_desc, fctx.course_commit_sha)

# }}}


# {{{ utilties for course-based views
def course_view(f):
    def wrapper(request, course_identifier, *args, **kwargs):
        pctx = CoursePageContext(request, course_identifier)
        response = f(pctx, *args, **kwargs)
        pctx.repo.close()
        return response

    from functools import update_wrapper
    update_wrapper(wrapper, f)

    return wrapper


class ParticipationPermissionWrapper(object):
    def __init__(self, pctx):
        # type: (CoursePageContext) -> None
        self.pctx = pctx

    def __getitem__(self, perm):
        # type: (Text) -> bool

        from course.constants import participation_permission
        try:
            getattr(participation_permission, perm)
        except AttributeError:
            raise ValueError("permission name '%s' not valid" % perm)

        return self.pctx.has_permission(perm, ANY_ARGUMENT)

    def __iter__(self):
        raise TypeError("ParticipationPermissionWrapper is not iterable.")


def render_course_page(pctx, template_name, args,
        allow_instant_flow_requests=True):
    # type: (CoursePageContext, Text, Dict[Text, Any], bool) -> http.HttpResponse

    args = args.copy()

    from course.views import get_now_or_fake_time
    now_datetime = get_now_or_fake_time(pctx.request)

    if allow_instant_flow_requests:
        from course.models import InstantFlowRequest
        instant_flow_requests = list((InstantFlowRequest.objects
                .filter(
                    course=pctx.course,
                    start_time__lte=now_datetime,
                    end_time__gte=now_datetime,
                    cancelled=False)
                .order_by("start_time")))
    else:
        instant_flow_requests = []

    args.update({
        "course": pctx.course,
        "pperm": ParticipationPermissionWrapper(pctx),
        "participation": pctx.participation,
        "num_instant_flow_requests": len(instant_flow_requests),
        "instant_flow_requests":
        [(i+1, r) for i, r in enumerate(instant_flow_requests)],
        })

    return render(pctx.request, template_name, args)

# }}}


# {{{ page cache

class PageInstanceCache(object):
    """Caches instances of :class:`course.page.Page`."""

    def __init__(self, repo, course, flow_id):
        self.repo = repo
        self.course = course
        self.flow_id = flow_id
        self.flow_desc_cache = {}
        self.page_cache = {}

    def get_flow_desc_from_cache(self, commit_sha):
        try:
            return self.flow_desc_cache[commit_sha]
        except KeyError:
            flow_desc = get_flow_desc(self.repo, self.course,
                    self.flow_id, commit_sha)
            self.flow_desc_cache[commit_sha] = flow_desc
            return flow_desc

    def get_page(self, group_id, page_id, commit_sha):
        key = (group_id, page_id, commit_sha)
        try:
            return self.page_cache[key]
        except KeyError:

            from course.content import get_flow_page_desc, instantiate_flow_page
            page_desc = get_flow_page_desc(
                    self.flow_id,
                    self.get_flow_desc_from_cache(commit_sha),
                    group_id, page_id)

            page = instantiate_flow_page(
                    location="flow '%s', group, '%s', page '%s'"
                    % (self.flow_id, group_id, page_id),
                    repo=self.repo, page_desc=page_desc,
                    commit_sha=commit_sha)

            self.page_cache[key] = page
            return page

# }}}


# {{{ codemirror config

def get_codemirror_widget(
        language_mode,  # type: Text
        interaction_mode,  # type: Text
        config=None,  # type: Optional[Dict]
        addon_css=(),  # type: Tuple
        addon_js=(),  # type: Tuple
        dependencies=(),  # type: Tuple
        read_only=False,  # type: bool
        ):
    # type: (...) ->  CodeMirrorTextarea
    theme = "default"
    if read_only:
        theme += " relate-readonly"

    from django.urls import reverse
    help_text = (_("Press F9 to toggle full-screen mode. ")
            + _("Set editor mode in <a href='%s'>user profile</a>.")
            % reverse("relate-user_profile"))

    actual_addon_css = (
        "dialog/dialog",
        "display/fullscreen",
        ) + addon_css
    actual_addon_js = (
        "search/searchcursor",
        "dialog/dialog",
        "search/search",
        "comment/comment",
        "edit/matchbrackets",
        "display/fullscreen",
        "selection/active-line",
        "edit/trailingspace",
        ) + addon_js

    if language_mode == "python":
        indent_unit = 4
    else:
        indent_unit = 2

    actual_config = {
            "fixedGutter": True,
            #"autofocus": True,
            "matchBrackets": True,
            "styleActiveLine": True,
            "showTrailingSpace": True,
            "indentUnit": indent_unit,
            "readOnly": read_only,
            "extraKeys": CodeMirrorJavascript("""
                {
                  "Ctrl-/": "toggleComment",
                  "Tab": function(cm)
                  {
                    // from https://github.com/codemirror/CodeMirror/issues/988

                    if (cm.doc.somethingSelected()) {
                        return CodeMirror.Pass;
                    }
                    var spacesPerTab = cm.getOption("indentUnit");
                    var spacesToInsert = (
                        spacesPerTab
                        - (cm.doc.getCursor("start").ch % spacesPerTab));
                    var spaces = Array(spacesToInsert + 1).join(" ");
                    cm.replaceSelection(spaces, "end", "+input");
                  },
                  "Shift-Tab": "indentLess",
                  "F9": function(cm) {
                      cm.setOption("fullScreen",
                        !cm.getOption("fullScreen"));
                  }
                }
            """)
            }

    if interaction_mode == "vim":
        actual_config["vimMode"] = True
        actual_addon_js += ('../keymap/vim',)
    elif interaction_mode == "emacs":
        actual_config["keyMap"] = "emacs"
        actual_addon_js += ('../keymap/emacs',)
    elif interaction_mode == "sublime":
        actual_config["keyMap"] = "sublime"
        actual_addon_js += ('../keymap/sublime',)
    # every other interaction mode goes to default

    if config is not None:
        actual_config.update(config)

    return CodeMirrorTextarea(
                    mode=language_mode,
                    dependencies=dependencies,
                    theme=theme,
                    addon_css=actual_addon_css,
                    addon_js=actual_addon_js,
                    config=actual_config), help_text

# }}}


# {{{ facility processing

def get_facilities_config(request=None):
    # type: (Optional[http.HttpRequest]) -> Dict[Text, Dict[Text, Any]]
    from django.conf import settings

    # This is called during offline validation, where Django isn't really set up.
    # The getattr makes this usable.
    facilities = getattr(settings, "RELATE_FACILITIES", None)
    if facilities is None:
        # Only happens during offline validation. Suppresses errors there.
        return None

    if callable(facilities):
        from course.views import get_now_or_fake_time
        now_datetime = get_now_or_fake_time(request)

        result = facilities(now_datetime)
        if not isinstance(result, dict):
            raise RuntimeError("RELATE_FACILITIES must return a dictionary")
        return result
    else:
        return facilities


class FacilityFindingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        pretend_facilities = request.session.get("relate_pretend_facilities")

        if pretend_facilities is not None:
            facilities = pretend_facilities
        else:
            import ipaddress
            remote_address = ipaddress.ip_address(
                    six.text_type(request.META['REMOTE_ADDR']))

            facilities = set()

            for name, props in six.iteritems(get_facilities_config(request)):
                ip_ranges = props.get("ip_ranges", [])
                for ir in ip_ranges:
                    if remote_address in ipaddress.ip_network(six.text_type(ir)):
                        facilities.add(name)

        request.relate_facilities = frozenset(facilities)

        return self.get_response(request)

# }}}


def csv_data_importable(file_contents, column_idx_list, header_count):
    import csv
    spamreader = csv.reader(file_contents)
    n_header_row = 0
    for row in spamreader:
        n_header_row += 1
        if n_header_row <= header_count:
            continue
        try:
            for column_idx in column_idx_list:
                if column_idx is not None:
                    six.text_type(row[column_idx-1])
        except UnicodeDecodeError:
            return False, (
                    _("Error: Columns to be imported contain "
                        "non-ASCII characters. "
                        "Please save your CSV file as utf-8 encoded "
                        "and import again.")
            )
        except Exception as e:
            return False, (
                    string_concat(
                        pgettext_lazy("Starting of Error message",
                            "Error"),
                        ": %(err_type)s: %(err_str)s")
                    % {
                        "err_type": type(e).__name__,
                        "err_str": str(e)}
                    )

    return True, ""


def will_use_masked_profile_for_email(recipient_email):
    # type: (Union[Text, List[Text]]) -> bool
    if not recipient_email:
        return False
    if not isinstance(recipient_email, list):
        recipient_email = [recipient_email]
    recepient_participations = (
        Participation.objects.filter(
            user__email__in=recipient_email
        ))
    from course.constants import participation_permission as pperm
    for part in recepient_participations:
        if part.has_permission(pperm.view_participant_masked_profile):
            return True
    return False

# vim: foldmethod=marker
