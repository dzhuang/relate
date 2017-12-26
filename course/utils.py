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

from typing import cast, Iterable  # noqa

import six
import datetime  # noqa
import pytz

from django.shortcuts import (  # noqa
        render, get_object_or_404)
from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.utils.translation import (
        ugettext as _, pgettext_lazy)

from codemirror import CodeMirrorTextarea, CodeMirrorJavascript

from relate.utils import string_concat
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
    from typing import (  # noqa
        Tuple, List, Iterable, Any, Optional, Union, Dict, FrozenSet, Text)
    from relate.utils import Repo_ish  # noqa
    from course.models import (  # noqa
            Course,
            Participation,
            ExamTicket,
            FlowSession,
            FlowPageData,
            )

# }}}

import re
CODE_CELL_DIV_ATTRS_RE = re.compile('(<div class="[^>]*code_cell[^>"]*")(>)')


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

            sessions_available_count=None,  # type: Optional[int]  # added by zd
            default_expiration_mode=None,  # type: Optional[Text]
            ):
        # type: (...) -> None
        self.tag_session = tag_session
        self.may_start_new_session = may_start_new_session
        self.may_list_existing_sessions = may_list_existing_sessions
        self.default_expiration_mode = default_expiration_mode
        self.sessions_available_count = sessions_available_count


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
            permissions,  # type: FrozenSet[Text]
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


def get_participation_tag_cache_key(participation):
    # type: (Participation) -> Text

    from course.constants import PARTICIPATION_TAG_KEY_PATTERN
    return (
        PARTICIPATION_TAG_KEY_PATTERN % {"participation": str(participation.pk)})


def get_participation_tag_set_cached(participation):
    # type: (Participation) -> List[Text]
    from django.core.exceptions import ImproperlyConfigured
    try:
        import django.core.cache as cache
    except ImproperlyConfigured:
        cache_key = None
    else:
        cache_key = get_participation_tag_cache_key(participation)

    def_cache = cache.caches["default"]

    if cache_key is None:
        result = list(set(participation.tags.all().values_list("name", flat=True)))
        assert isinstance(result, list)
        return result

    if len(cache_key) < 240:
        result = def_cache.get(cache_key)
        if result is not None:
            assert isinstance(result, list), cache_key
            return result

    result = list(set(participation.tags.all().values_list("name", flat=True)))
    import sys
    from django.conf import settings
    if sys.getsizeof(result) <= getattr(settings, "RELATE_CACHE_MAX_BYTES", 0):
        def_cache.add(cache_key, result, None)

    assert isinstance(result, list)
    return result


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
        ptag_set = set(get_participation_tag_set_cached(participation))
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


def _get_session_start_rules(
        flow_desc,  # type: FlowDesc
        flow_id,  # type: Text
        now_datetime,  # type: datetime.datetime
        participation,  # type: Optional[Participation]
        ):
    # type: (...) -> List[Any]
    from relate.utils import dict_to_struct
    return get_flow_rules(flow_desc, flow_rule_kind.start,
                          participation, flow_id, now_datetime,
                          default_rules_desc=[
                              dict_to_struct(dict(
                                  may_start_new_session=True,
                                  may_list_existing_sessions=False))])


def get_session_start_rule(
        course,  # type: Course
        participation,  # type: Optional[Participation]
        flow_id,  # type: Text
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[FrozenSet[Text]]
        for_rollover=False,  # type: bool
        login_exam_ticket=None,  # type: Optional[ExamTicket]
        rules=[],  # type: List[Any]
        ):
    # type: (...) -> FlowSessionStartRule

    """Return a :class:`FlowSessionStartRule` if a new session is
    permitted or *None* if no new session is allowed.
    """

    if facilities is None:
        facilities = frozenset()

    if not rules:
        rules = _get_session_start_rules(
            flow_desc, flow_id, now_datetime, participation)

    # {{{ added by zd
    sessions_available_count = 0
    # }}}

    from course.models import FlowSession  # noqa
    for rule in rules:
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
            sessions_available_count = (
                    rule.if_has_fewer_sessions_than - session_count)
            # }}}

            if sessions_available_count <= 0:
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
                sessions_available_count=sessions_available_count,
                # }}}
                default_expiration_mode=getattr(
                    rule, "default_expiration_mode", None),
                )

    return FlowSessionStartRule(
            may_list_existing_sessions=False,
            may_start_new_session=False,
            )


def _get_session_access_rules(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        ):
    # type: (...) -> List[FlowSessionAccessRuleDesc]
    from relate.utils import dict_to_struct
    return get_flow_rules(flow_desc, flow_rule_kind.access,
                           session.participation, session.flow_id, now_datetime,
                           default_rules_desc=[
                               dict_to_struct(dict(
                                   permissions=[flow_permission.view],
                               ))])


def get_session_access_rule(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[FrozenSet[Text]]
        login_exam_ticket=None,  # type: Optional[ExamTicket]
        rules=[],  # type: List[Any]
        ):
    # type: (...) -> FlowSessionAccessRule
    """Return a :class:`ExistingFlowSessionRule`` to describe
    how a flow may be accessed.
    """

    if facilities is None:
        facilities = frozenset()

    if not rules:
        rules = _get_session_access_rules(session, flow_desc, now_datetime)

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


def _get_session_grading_rules(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        ):
    # type: (...) -> List[Any]
    from relate.utils import dict_to_struct
    return get_flow_rules(flow_desc, flow_rule_kind.grading,
                          session.participation, session.flow_id, now_datetime,
                          default_rules_desc=[
                              dict_to_struct(dict(
                                  generates_grade=False,
                              ))])


def get_session_grading_rule(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        rules=[],  # type: List[Any]
        ):
    # type: (...) -> FlowSessionGradingRule

    flow_desc_rules = getattr(flow_desc, "rules", None)

    if not rules:
        rules = _get_session_grading_rules(session, flow_desc, now_datetime)

    from course.enrollment import get_participation_role_identifiers
    roles = get_participation_role_identifiers(session.course, session.participation)
    if_completed_before = None

    for rule in rules:
        if hasattr(rule, "if_has_role"):
            if all(role not in rule.if_has_role for role in roles):
                continue

        if not _eval_generic_session_conditions(rule, session, now_datetime):
            continue

        if not _eval_participation_tags_conditions(rule, session.participation):
            continue

        if hasattr(rule, "if_completed_before"):
            ds = parse_date_spec(session.course, rule.if_completed_before)

            use_last_activity_as_completion_time = False
            if hasattr(rule, "use_last_activity_as_completion_time"):
                use_last_activity_as_completion_time = \
                        rule.use_last_activity_as_completion_time

            if use_last_activity_as_completion_time:
                last_activity = session.last_activity()
                if last_activity is not None:
                    completion_time = last_activity
                else:
                    completion_time = now_datetime
            else:
                if session.in_progress:
                    completion_time = now_datetime
                else:
                    completion_time = session.completion_time

            if completion_time > ds:
                continue
            if_completed_before = ds

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

        try:
            from typing import Text  # noqa
        except ImportError:
            Text = None  # noqa

        grade_aggregation_strategy = cast(Text, grade_aggregation_strategy)  # type: ignore  # noqa

        return FlowSessionGradingRule(
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

                completed_before=if_completed_before,     # added by zd
                )

    raise RuntimeError(_("grading rule determination was unable to find "
            "a grading rule"))

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
        self._permissions_cache = None  # type: Optional[FrozenSet[Tuple[Text, Optional[Text]]]]  # noqa
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

                with get_course_repo(self.course) as repo:
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
                    finally:
                        true_repo.close()

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
        # type: () -> FrozenSet[Tuple[Text, Optional[Text]]]
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

    def _set_course_lang(self, action):
        # type: (Text) -> None
        from django.conf import settings
        if not getattr(settings, "RELATE_ENABLE_COURSE_SPECIFIC_LANG", False):
            return
        if self.course.force_lang is not None:
            if action == "activate":
                translation.activate(self.course.force_lang)
            else:
                translation.deactivate()

    def __enter__(self):
        self._set_course_lang(action="activate")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._set_course_lang(action="deactivate")
        self.repo.close()


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
            page_ordinal,  # type: int
            participation,  # type: Optional[Participation]
            flow_session,  # type: FlowSession
            request=None,  # type: Optional[http.HttpRequest]
            ):
        # type: (...) -> None
        super(FlowPageContext, self).__init__(repo, course, flow_id, participation)

        if page_ordinal >= flow_session.page_count:
            raise PageOrdinalOutOfRange()

        from course.models import FlowPageData  # noqa
        page_data = self.page_data = get_object_or_404(
                FlowPageData, flow_session=flow_session, page_ordinal=page_ordinal)

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
                    reverse(
                        "relate-view_flow_page",
                        args=(course.identifier, flow_session.id, page_ordinal)))

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
    def page_ordinal(self):
        return self.page_data.page_ordinal


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
        with CoursePageContext(request, course_identifier) as pctx:
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
    # type: (Optional[http.HttpRequest]) -> Optional[Dict[Text, Dict[Text, Any]]]
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
    from course.models import Participation  # noqa
    recepient_participations = (
        Participation.objects.filter(
            user__email__in=recipient_email
        ))
    from course.constants import participation_permission as pperm
    for part in recepient_participations:
        if part.has_permission(pperm.view_participant_masked_profile):
            return True
    return False


# {{{ ipynb utilities


def render_notebook_from_source(
        ipynb_source, clear_output=False, indices=None, clear_markdown=False):
    """
    Get HTML format of ipython notebook so as to be rendered in RELATE flow pages.
    Note: code fences are unconverted, If converted, the result often looked wired,
    e.g., https://stackoverflow.com/a/22285406/3437454, because RELATE will reprocess
    the result again by python-markdown.
    :param ipynb_source: the :class:`text` read from a ipython notebook.
    :param clear_output: a :class:`bool` instance, indicating whether existing
    execution output of code cells should be removed.
    :param indices: a :class:`list` instance, 0-based indices of notebook cells
    which are expected to be rendered.
    :param clear_markdown: a :class:`bool` instance, indicating whether markdown
    cells will be ignored..
    :return:
    """
    import nbformat
    from nbformat.reader import parse_json
    nb_source_dict = parse_json(ipynb_source)

    if indices:
        nb_source_dict.update(
            {"cells": [nb_source_dict["cells"][idx] for idx in indices]})

    if clear_markdown:
        nb_source_dict.update(
            {"cells": [cell for cell in nb_source_dict["cells"]
                       if cell['cell_type'] != "markdown"]})

    nb_source_dict.update({"cells": nb_source_dict["cells"]})

    import json
    ipynb_source = json.dumps(nb_source_dict)
    notebook = nbformat.reads(ipynb_source, as_version=4)

    from traitlets.config import Config
    c = Config()

    # This is to prevent execution of arbitrary code from note book
    c.ExecutePreprocessor.enabled = False
    if clear_output:
        c.ClearOutputPreprocessor.enabled = True

    c.CSSHTMLHeaderPreprocessor.enabled = False
    c.HighlightMagicsPreprocessor.enabled = False

    import os
    from django.conf import settings

    # Place the template in course template dir
    template_path = os.path.join(
        settings.BASE_DIR, "course", "templates", "course", "jinja2")
    c.TemplateExporter.template_path.append(template_path)

    from nbconvert import HTMLExporter
    html_exporter = HTMLExporter(
        config=c,
        template_file="nbconvert_template.tpl"
    )

    (body, resources) = html_exporter.from_notebook_node(notebook)

    return body

# }}}

# {{{ added by zd


class HumanReadableSessionRuleBase(object):
    def __init__(
            self,
            human_readable_rule,  # type: Text
            is_active,  # type: bool
            has_expired=False,  # type: Optional[bool]
            is_dangerous=False  # type: Optional[bool]
    ):
        # type: (...) -> None
        self.human_readable_rule = human_readable_rule
        self.is_active = is_active
        self.has_expired = has_expired
        self.is_dangerous = is_dangerous


class HumanReadableSessionGradingRuleDesc(HumanReadableSessionRuleBase):
    pass


class HumanReadableSessionStartRuleDesc(HumanReadableSessionRuleBase):
    pass


def get_human_readable_flow_may_start_desc_list(
        course,  # type: Course
        participation,  # type: Optional[Participation]
        flow_id,  # type: Text
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[Frozenset[Text]]
        for_rollover=False,  # type: bool
        login_exam_ticket=None,  # type: Optional[ExamTicket]
        ):

    rules = _get_session_start_rules(
        flow_desc,
        flow_id,
        now_datetime,
        participation
    )

    time_point_set = set()
    time_point_set.add(MIN_DATETIME)
    for rule in rules:
        if hasattr(rule, "if_before"):
            time_point_set.add(parse_date_spec(course, rule.if_before))
        if hasattr(rule, "if_after"):
            time_point_set.add(parse_date_spec(course, rule.if_after))
    time_point_list = sorted(list(time_point_set))

    def check_may_start(test_datetime):
        # type: (datetime.datetime) -> Optional[bool]
        start_rule = get_session_start_rule(
            course,
            participation,
            flow_id,
            flow_desc,
            now_datetime=test_datetime,
            facilities=facilities,
            for_rollover=for_rollover,
            login_exam_ticket=login_exam_ticket,
            rules=rules
        )
        return start_rule.may_start_new_session

    # TODO: list comp
    may_start_time_check_list = []
    for t in time_point_list:
        test_time = t + datetime.timedelta(microseconds=1)
        may_start = check_may_start(test_time)
        may_start_time_check_list.append(may_start)

    may_start_time_check_list_zip = list(
        zip(may_start_time_check_list, time_point_list))
    may_start_time_check_list_zip_merged = []
    for i, z in enumerate(may_start_time_check_list_zip):
        try:
            if i == 0:
                may_start_time_check_list_zip_merged.append(z)
            elif z[0] != may_start_time_check_list_zip[i - 1][0]:
                may_start_time_check_list_zip_merged.append(z)
        except IndexError:
            may_start_time_check_list_zip_merged.append(z)

    srule_time_range_list = []
    for i, z in enumerate(may_start_time_check_list_zip_merged):
        if z[0] is True:
            start = may_start_time_check_list_zip_merged[i][1]
            try:
                end = may_start_time_check_list_zip_merged[i + 1][1]
            except IndexError:
                end = MAX_DATETIME

            rule_is_active = False
            if start <= now_datetime <= end:
                rule_is_active = True
            srule_time_range_list.append((start, end, rule_is_active))

    human_readable_srule_list = []
    if srule_time_range_list:
        from relate.utils import compact_local_datetime_str
        for srule_tuple in srule_time_range_list:
            srule_str = ""
            start = srule_tuple[0]
            end = srule_tuple[1]
            rule_is_active = srule_tuple[2]
            if start != MIN_DATETIME and end != MAX_DATETIME:
                if now_datetime > start:
                    srule_str = _("Before <b>%(end)s</b>.") % {
                        "end": compact_local_datetime_str(end, now_datetime)
                    }
                else:
                    srule_str = _("From <b>%(start)s</b> to <b>%(end)s</b>.") % {
                        "start": compact_local_datetime_str(start, now_datetime),
                        "end": compact_local_datetime_str(end, now_datetime)
                    }
            elif start == MIN_DATETIME and end != MAX_DATETIME:
                srule_str = _("Before <b>%(end)s</b>.") % {
                    "end": compact_local_datetime_str(end, now_datetime)
                }
            elif start != MIN_DATETIME and end == MAX_DATETIME:
                srule_str = _("After <b>%(start)s</b>.") % {
                    "start": compact_local_datetime_str(start, now_datetime)
                }
            else:
                continue

            if srule_str:
                human_readable_srule_list.append(
                    HumanReadableSessionStartRuleDesc(
                        human_readable_rule=srule_str,
                        is_active=rule_is_active,
                        has_expired=now_datetime > end,
                    )
                )

        last_srule = srule_time_range_list[-1]
        last_end = last_srule[1]
        if last_end != MAX_DATETIME:
            human_readable_srule_list.append(
                HumanReadableSessionStartRuleDesc(
                    human_readable_rule=(
                        _("No new sessions are allowed to be started "
                          "since <b>%s</b>.")
                        % compact_local_datetime_str(last_end, now_datetime)),
                    is_active=now_datetime > last_end,
                    has_expired=False,
                    is_dangerous=True
                )
            )

    return human_readable_srule_list


def get_human_readable_session_grading_rule_desc_or_list(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        generate_grule_full_list=False,  # type: bool
        ):

    rules = _get_session_grading_rules(
        session,
        flow_desc,
        now_datetime,
    )

    time_point_set = set()
    time_point_set.add(MIN_DATETIME)
    for rule in rules:
        if hasattr(rule, "if_before"):
            time_point_set.add(
                parse_date_spec(session.course, rule.if_before))
        if hasattr(rule, "if_after"):
            time_point_set.add(
                parse_date_spec(session.course, rule.if_after))
        if hasattr(rule, "if_started_before"):
            time_point_set.add(
                parse_date_spec(session.course, rule.if_started_before))
        if hasattr(rule, "if_completed_before"):
            time_point_set.add(
                parse_date_spec(session.course, rule.if_completed_before))
    time_point_list = sorted(list(time_point_set))

    def get_test_grading_rule(test_datetime):
        # type: (datetime.datetime) -> FlowSessionGradingRule
        grading_rule = get_session_grading_rule(
            session=session,
            flow_desc=flow_desc,
            now_datetime=test_datetime,
            rules=rules
        )
        return grading_rule

    grule_list = []
    for t in time_point_list:
        test_time = t + datetime.timedelta(microseconds=1)
        grule = get_test_grading_rule(test_time)
        grule_list.append(grule)

    grule_zip = list(zip(grule_list, time_point_list))
    grule_zip_merged = []
    for i, z in enumerate(grule_zip):
        try:
            if i == 0:
                grule_zip_merged.append(z)
            elif z[0] != grule_zip[i-1][0]:
                grule_zip_merged.append(z)
        except IndexError:
            grule_zip_merged.append(z)

    grule_time_range_list = []
    for i, z in enumerate(grule_zip_merged):
        if z[0].generates_grade:
            start = grule_zip_merged[i][1]
            if now_datetime < start and not generate_grule_full_list:
                continue
            try:
                end = grule_zip_merged[i + 1][1]
                next_rule = grule_zip_merged[i + 1][0]
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
            if ((not generate_grule_full_list and rule_is_active)
                or
                    generate_grule_full_list):
                grule_time_range_list.append(
                    (start, end, z[0], next_rule, rule_is_active))

    human_readable_grule_list = []
    if grule_time_range_list:
        from relate.utils import compact_local_datetime_str
        from django.utils.timesince import timeuntil
        for grule_tuple in grule_time_range_list:
            start = grule_tuple[0]
            end = grule_tuple[1]
            grule = grule_tuple[2]
            next_rule = grule_tuple[3]
            rule_is_active = grule_tuple[4]
            is_dangerous = False
            has_expired = False

            started_before = getattr(grule, "if_started_before", "")
            if started_before:
                started_before = (
                    string_concat(
                        "(",
                        _("started before %s"),
                        ")"
                    ) % compact_local_datetime_str(
                        started_before, now_datetime))

            credit_expected = None

            if grule.credit_percent:
                credit_expected = (
                    _("<b>%(credit_percent)d%%</b> of the grade")
                    % {"credit_percent": grule.credit_percent}
                )
            if grule.max_points:
                max_points = grule.max_points
                if grule.max_points_enforced_cap:
                    max_points = min(max_points, grule.max_points_enforced_cap)
                credit_expected = (
                    _(" at most <b>%(max_points)d</b> points")
                    % {"max_points": max_points}
                )
            if grule.bonus_points:
                credit_expected += (
                    _("(including %(bonus_points)s bonus points)")
                    % {"bonus_points": grule.bonus_points}
                )

            if end != MAX_DATETIME:
                if now_datetime > end:
                    has_expired = True
                if not credit_expected:
                    if not generate_grule_full_list:
                        flow_page_grading_info = (
                            string_concat(
                                _("This session will <b>NOT</b> "
                                  "receive grade "
                                  "if submitted before "
                                  "%(completed_before)s."), " ")
                            % {
                                "completed_before": compact_local_datetime_str(
                                    end, now_datetime)})
                    else:
                        flow_page_grading_info = (
                            string_concat(
                                _("A new session"
                                  "%(started_before)s "
                                  "will <b>NOT</b> "
                                  "receive grade "
                                  "if submitted before "
                                  "<b>%(completed_before)s</b>."), " ")
                            % {
                                "started_before": started_before,
                                "completed_before": compact_local_datetime_str(
                                    end, now_datetime)})
                else:
                    if not generate_grule_full_list:
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
                                _("A new session"
                                  "%(started_before)s "
                                  "will get %(credit_expected)s"
                                  "if submmited before <b>"
                                  "%(completed_before)s</b>."),
                                " ") %
                            {
                                "started_before": started_before,
                                "completed_before": compact_local_datetime_str(
                                    end, now_datetime),
                                "credit_expected": credit_expected})
            else:
                if not credit_expected:
                    is_dangerous = True
                    if not generate_grule_full_list:
                        flow_page_grading_info = (
                            string_concat(
                                _("This session will <b>NOT</b> "
                                  "receive grade."), " ")
                        )
                    else:
                        if start != MIN_DATETIME:
                            flow_page_grading_info = (
                                string_concat(
                                    _("A new session"
                                      "%(started_before)s will <b>NOT</b> "
                                      "receive grade "
                                      "since <b>%(start_time)s</b>."), " ")
                                % {
                                    "started_before": started_before,
                                    "start_time": compact_local_datetime_str(
                                        start, now_datetime)}
                            )
                        else:
                            flow_page_grading_info = (
                                string_concat(
                                    _("A new session"
                                      "%(started_before)s will <b>NOT</b> "
                                      "receive grade."
                                      ), " ")
                                % {
                                    "started_before": started_before}
                            )
                else:
                    if not generate_grule_full_list:
                        flow_page_grading_info = (
                            string_concat(
                                _("This session will get "
                                  "<b>%(credit_expected)s</b> "
                                  "if submitted."), " ") %
                            {
                                "credit_expected": credit_expected})
                    else:
                        if start != MIN_DATETIME:
                            flow_page_grading_info = (
                                string_concat(
                                    _("A new session"
                                      "%(started_before)s submitted "
                                      "after <b>%(start_time)s</b> "
                                      "will get "
                                      "<b>%(credit_expected)s</b>"
                                      "."), " ") %
                                {
                                    "started_before": started_before,
                                    "credit_expected": credit_expected,
                                    "start_time": compact_local_datetime_str(
                                        start, now_datetime)})
                        else:
                            flow_page_grading_info = (
                                string_concat(
                                    _("A new session"
                                      "%(started_before)s submitted will get "
                                      "<b>%(credit_expected)s</b>."
                                      ),
                                    " ") %
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
                if not generate_grule_full_list:
                    flow_page_grading_info += (
                        _("Afterward, this session will <b>NOT</b> receive grade.")
                        + " ")
                    return flow_page_grading_info

            else:
                if not generate_grule_full_list:
                    credit_expected_next = None

                    if next_rule.credit_percent:
                        credit_expected_next = (
                            _("<b>%(credit_percent)d%%</b> of the grade")
                            % {"credit_percent": next_rule.credit_percent}
                        )
                    if next_rule.max_points:
                        max_points_next = grule.max_points
                        if grule.max_points_enforced_cap:
                            max_points_next = min(
                                max_points_next, grule.max_points_enforced_cap)
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

            if flow_page_grading_info:
                human_readable_grule_list.append(
                    HumanReadableSessionGradingRuleDesc(
                        human_readable_rule=flow_page_grading_info,
                        is_active=rule_is_active,
                        has_expired=has_expired,
                        is_dangerous=is_dangerous)
                )

    return human_readable_grule_list

# }}}


# {{{ added by zd to generate stringified rules in flow start page
def get_session_notify_rule(
        session,  # type: FlowSession
        flow_desc,  # type: FlowDesc
        now_datetime,  # type: datetime.datetime
        facilities=None,  # type: Optional[Frozenset[Text]]
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
                    ))])

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

# }}}


def get_valiated_custom_page_import_exec_str(klass, validate_only=False):
    # type: (Union[Text, List, Tuple], Optional[bool]) -> Optional[Text]
    if isinstance(klass, (list, tuple)) and len(klass) == 1:
        klass, = cast(Iterable, klass)
    if isinstance(klass, str):
        dotted_path = klass
        klass_name = klass.rsplit('.', 1)[1]
    elif isinstance(klass, (list, tuple)):
        try:
            klass_name, dotted_path = cast(Iterable, klass)
        except ValueError:
            raise ValueError("The length of %s should be 2" % repr(klass))
    else:
        raise ValueError(
            "'%s' is not an instance of str, list or tuple" % str(klass))
    if not klass_name == dotted_path.rsplit(".", 1)[1]:
        raise ValueError('"%s" is not included in the full path of "%s"' % (
            klass_name, dotted_path))

    exec_string = compile(
        "%s = import_string('%s')" % (klass_name, dotted_path),
        '<string>', 'exec')

    if not validate_only:
        return exec_string

    from django.utils.module_loading import import_string  # noqa
    exec(exec_string)
    return


# vim: foldmethod=marker
