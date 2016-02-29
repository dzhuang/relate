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

import re
import six

from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy, ugettext, string_concat)
from django.shortcuts import (  # noqa
        render, redirect, get_object_or_404)
from django.contrib import messages  # noqa
from django.core.exceptions import (
        PermissionDenied, SuspiciousOperation, ObjectDoesNotExist)
from django.db import connection
from django import forms
from django.db import transaction
from django.utils.timezone import now
from django import http

from django.core.urlresolvers import reverse
from relate.utils import StyledForm
from crispy_forms.layout import Submit

from course.utils import course_view, render_course_page
from course.models import (
        Participation, participation_role, participation_status,
        GradingOpportunity, GradeChange, GradeStateMachine,
        grade_state_change_types,
        FlowSession, FlowPageVisit)
from course.views import get_now_or_fake_time


# {{{ student grade book

@course_view
def view_participant_grades(pctx, participation_id=None):
    if pctx.participation is None:
        raise PermissionDenied(_("must be enrolled to view grades"))

    if participation_id is not None:
        grade_participation = Participation.objects.get(id=int(participation_id))
    else:
        grade_participation = pctx.participation

    if pctx.role in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        is_student_viewing = False
    elif pctx.role == participation_role.student:
        if grade_participation != pctx.participation:
            raise PermissionDenied(_("may not view other people's grades"))

        is_student_viewing = True
    else:
        raise PermissionDenied()

    # NOTE: It's important that these two queries are sorted consistently,
    # also consistently with the code below.
    grading_opps = list((GradingOpportunity.objects
            .filter(
                course=pctx.course,
                shown_in_grade_book=True,
                )
            .order_by("identifier")))

    grade_changes = list(GradeChange.objects
            .filter(
                participation=grade_participation,
                opportunity__course=pctx.course,
                opportunity__shown_in_grade_book=True)
            .order_by(
                "participation__id",
                "opportunity__identifier",
                "grade_time")
            .select_related("participation")
            .select_related("participation__user")
            .select_related("opportunity"))

    idx = 0

    grade_table = []
    for opp in grading_opps:
        if is_student_viewing:
            if not (opp.shown_in_grade_book
                    and opp.shown_in_participant_grade_book):
                continue
        else:
            if not opp.shown_in_grade_book:
                continue

        while (
                idx < len(grade_changes)
                and grade_changes[idx].opportunity.identifier < opp.identifier
                ):
            idx += 1

        my_grade_changes = []
        while (
                idx < len(grade_changes)
                and grade_changes[idx].opportunity.pk == opp.pk):
            my_grade_changes.append(grade_changes[idx])
            idx += 1

        state_machine = GradeStateMachine()
        state_machine.consume(my_grade_changes)

        grade_table.append(
                GradeInfo(
                    opportunity=opp,
                    grade_state_machine=state_machine))

    return render_course_page(pctx, "course/gradebook-participant.html", {
        "grade_table": grade_table,
        "grade_participation": grade_participation,
        "grading_opportunities": grading_opps,
        "grade_state_change_types": grade_state_change_types,
        "is_student_viewing": is_student_viewing,
        })

# }}}


# {{{ participant list

@course_view
def view_participant_list(pctx):
    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied(_("must be instructor or TA to view grades"))

    participations = list(Participation.objects
            .filter(
                course=pctx.course,
                status=participation_status.active)
            .order_by("id")
            .select_related("user"))
    
    from course.models import ParticipationPreapproval

    registered_inst_id = []
    registered_provided_name = []
        
    for parti in participations:
        registered_inst_id.append(parti.user.institutional_id)
        try:
            registered_preappr = ParticipationPreapproval.objects.get(institutional_id=parti.user.institutional_id)
            registered_provided_name.append(registered_preappr.provided_name)
        except ParticipationPreapproval.DoesNotExist:
            registered_provided_name.append(None)
        
    participations = zip(participations, registered_provided_name)

    unregistered = list(ParticipationPreapproval.objects
            .filter(course=pctx.course)
            .exclude(institutional_id__in=registered_inst_id)
            .exclude(provided_name__iexact=None)
            )

    return render_course_page(pctx, "course/gradebook-participant-list.html", {
        "participations": participations,
        "unregistered": unregistered,
        })

# }}}


# {{{ grading opportunity list

@course_view
def view_grading_opportunity_list(pctx):
    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied(_("must be instructor or TA to view grades"))

    grading_opps = list((GradingOpportunity.objects
            .filter(
                course=pctx.course,
                shown_in_grade_book=True,
                )
            .order_by("identifier")))

    return render_course_page(pctx, "course/gradebook-opp-list.html", {
        "grading_opps": grading_opps,
        })

# }}}


# {{{ teacher grade book

class GradeInfo:
    def __init__(self, opportunity, grade_state_machine):
        self.opportunity = opportunity
        self.grade_state_machine = grade_state_machine


def get_grade_table(course):
    # NOTE: It's important that these queries are sorted consistently,
    # also consistently with the code below.
    grading_opps = list((GradingOpportunity.objects
            .filter(
                course=course,
                shown_in_grade_book=True,
                )
            .order_by("identifier")))

    participations = list(Participation.objects
            .filter(
                course=course,
                status=participation_status.active)
            .order_by("id")
            .select_related("user"))

    grade_changes = list(GradeChange.objects
            .filter(
                opportunity__course=course,
                opportunity__shown_in_grade_book=True)
            .order_by(
                "participation__id",
                "opportunity__identifier",
                "grade_time")
            .select_related("participation")
            .select_related("participation__user")
            .select_related("opportunity"))

    idx = 0

    grade_table = []
    for participation in participations:
        while (
                idx < len(grade_changes)
                and grade_changes[idx].participation.id < participation.id):
            idx += 1

        grade_row = []
        for opp in grading_opps:
            while (
                    idx < len(grade_changes)
                    and grade_changes[idx].participation.pk == participation.pk
                    and grade_changes[idx].opportunity.identifier < opp.identifier
                    ):
                idx += 1

            my_grade_changes = []
            while (
                    idx < len(grade_changes)
                    and grade_changes[idx].opportunity.pk == opp.pk
                    and grade_changes[idx].participation.pk == participation.pk):
                my_grade_changes.append(grade_changes[idx])
                idx += 1

            state_machine = GradeStateMachine()
            state_machine.consume(my_grade_changes)

            grade_row.append(
                    GradeInfo(
                        opportunity=opp,
                        grade_state_machine=state_machine))

        grade_table.append(grade_row)

    return participations, grading_opps, grade_table


@course_view
def view_gradebook(pctx):
    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied(_("must be instructor or TA to view grades"))

    participations, grading_opps, grade_table = get_grade_table(pctx.course)

    def grade_key(entry):
        (participation, grades) = entry
        return (participation.user.last_name.lower(),
                    participation.user.first_name.lower())

    grade_table = sorted(zip(participations, grade_table), key=grade_key)

    return render_course_page(pctx, "course/gradebook.html", {
        "grade_table": grade_table,
        "grading_opportunities": grading_opps,
        "participations": participations,
        "grade_state_change_types": grade_state_change_types,
        })


@course_view
def export_gradebook_csv(pctx):
    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied(_("must be instructor or TA to export grades"))

    participations, grading_opps, grade_table = get_grade_table(pctx.course)

    from six import StringIO
    csvfile = StringIO()

    if six.PY2:
        import unicodecsv as csv
    else:
        import csv

    fieldnames = ['user_name', 'last_name', 'first_name'] + [
            gopp.identifier for gopp in grading_opps]

    writer = csv.writer(csvfile)

    writer.writerow(fieldnames)

    for participation, grades in zip(participations, grade_table):
        writer.writerow([
            participation.user.username,
            participation.user.last_name,
            participation.user.first_name,
            ] + [grade_info.grade_state_machine.stringify_machine_readable_state()
                for grade_info in grades])

    response = http.HttpResponse(
            csvfile.getvalue().encode("utf-8"),
            content_type="text/plain; charset=utf-8")
    response['Content-Disposition'] = (
            'attachment; filename="grades-%s.csv"'
            % pctx.course.identifier)
    return response

# }}}


# {{{ grades by grading opportunity

class OpportunityGradeInfo(object):
    def __init__(self, grade_state_machine, flow_sessions):
        self.grade_state_machine = grade_state_machine
        self.flow_sessions = flow_sessions


class ModifySessionsForm(StyledForm):
    def __init__(self, session_rule_tags, *args, **kwargs):
        super(ModifySessionsForm, self).__init__(*args, **kwargs)

        self.fields["rule_tag"] = forms.ChoiceField(
                choices=tuple(
                    (rule_tag, str(rule_tag))
                    for rule_tag in session_rule_tags),
                label=_("Session tag"))
        self.fields["past_due_only"] = forms.BooleanField(
                required=False,
                initial=True,
                help_text=_("Only act on in-progress sessions that are past "
                "their access rule's due date (applies to 'expire')"),
                # Translators: see help text above.
                label=_("Past due only"))

        self.helper.add_input(
                Submit("expire", _("Impose deadline (Expire sessions)")))
        # self.helper.add_input(
        # Submit("end", _("End and grade all sessions")))
        self.helper.add_input(
                Submit("regrade", _("Regrade ended sessions")))
        self.helper.add_input(
                Submit("recalculate", _("Recalculate grades of ended sessions")))


RULE_TAG_NONE_STRING = "<<<NONE>>>"


def mangle_session_access_rule_tag(rule_tag):
    if rule_tag is None:
        return RULE_TAG_NONE_STRING
    else:
        return rule_tag


@course_view
def view_grades_by_opportunity(pctx, opp_id):
    from course.views import get_now_or_fake_time
    now_datetime = get_now_or_fake_time(pctx.request)

    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied(_("must be instructor or TA to view grades"))

    opportunity = get_object_or_404(GradingOpportunity, id=int(opp_id))

    if pctx.course != opportunity.course:
        raise SuspiciousOperation(_("opportunity from wrong course"))

    # {{{ batch sessions form

    batch_session_ops_form = None
    if pctx.role == participation_role.instructor and opportunity.flow_id:
        cursor = connection.cursor()
        cursor.execute("select distinct access_rules_tag from course_flowsession "
                "where course_id = %s and flow_id = %s "
                "order by access_rules_tag", (pctx.course.id, opportunity.flow_id))
        session_rule_tags = [
                mangle_session_access_rule_tag(row[0]) for row in cursor.fetchall()]

        request = pctx.request
        if request.method == "POST":
            batch_session_ops_form = ModifySessionsForm(
                    session_rule_tags, request.POST, request.FILES)
            if "expire" in request.POST:
                op = "expire"
            elif "end" in request.POST:
                op = "end"
            elif "regrade" in request.POST:
                op = "regrade"
            elif "recalculate" in request.POST:
                op = "recalculate"
            else:
                raise SuspiciousOperation(_("invalid operation"))

            if batch_session_ops_form.is_valid():
                rule_tag = batch_session_ops_form.cleaned_data["rule_tag"]
                past_due_only = batch_session_ops_form.cleaned_data["past_due_only"]

                if rule_tag == RULE_TAG_NONE_STRING:
                    rule_tag = None

                from course.tasks import (
                        expire_in_progress_sessions,
                        finish_in_progress_sessions,
                        regrade_flow_sessions,
                        recalculate_ended_sessions)

                if op == "expire":
                    async_res = expire_in_progress_sessions.delay(
                            pctx.course.id, opportunity.flow_id,
                            rule_tag, now_datetime,
                            past_due_only=past_due_only)

                    return redirect("relate-monitor_task", async_res.id)

                elif op == "end":
                    async_res = finish_in_progress_sessions.delay(
                            pctx.course.id, opportunity.flow_id,
                            rule_tag, now_datetime,
                            past_due_only=past_due_only)

                    return redirect("relate-monitor_task", async_res.id)

                elif op == "regrade":
                    async_res = regrade_flow_sessions.delay(
                            pctx.course.id, opportunity.flow_id,
                            rule_tag, inprog_value=False)

                    return redirect("relate-monitor_task", async_res.id)

                elif op == "recalculate":
                    async_res = recalculate_ended_sessions.delay(
                            pctx.course.id, opportunity.flow_id,
                            rule_tag)

                    return redirect("relate-monitor_task", async_res.id)

                else:
                    raise SuspiciousOperation("invalid operation")

        else:
            batch_session_ops_form = ModifySessionsForm(session_rule_tags)

    # }}}

    # NOTE: It's important that these queries are sorted consistently,
    # also consistently with the code below.

    participations = list(Participation.objects
            .filter(
                course=pctx.course,
                status=participation_status.active)
            .order_by("id")
            .select_related("user"))

    grade_changes = list(GradeChange.objects
            .filter(opportunity=opportunity)
            .order_by(
                "participation__id",
                "grade_time")
            .select_related("participation")
            .select_related("participation__user")
            .select_related("opportunity"))

    idx = 0

    finished_sessions = 0
    total_sessions = 0

    grade_table = []
    for participation in participations:
        while (
                idx < len(grade_changes)
                and grade_changes[idx].participation.id < participation.id):
            idx += 1

        my_grade_changes = []
        while (
                idx < len(grade_changes)
                and grade_changes[idx].participation.pk == participation.pk):
            my_grade_changes.append(grade_changes[idx])
            idx += 1

        state_machine = GradeStateMachine()
        state_machine.consume(my_grade_changes)

        if opportunity.flow_id:
            flow_sessions = (FlowSession.objects
                    .filter(
                        participation=participation,
                        flow_id=opportunity.flow_id,
                        )
                    .order_by("start_time"))

            for fsession in flow_sessions:
                total_sessions += 1
                if not fsession.in_progress:
                    finished_sessions += 1

        else:
            flow_sessions = None

        grade_table.append(
                OpportunityGradeInfo(
                    grade_state_machine=state_machine,
                    flow_sessions=flow_sessions))

    def grade_key(entry):
        (participation, grades) = entry
        return (participation.user.last_name.lower(),
                    participation.user.first_name.lower())

    grade_table = sorted(zip(participations, grade_table),
            key=grade_key)

    return render_course_page(pctx, "course/gradebook-by-opp.html", {
        "opportunity": opportunity,
        "participations": participations,
        "grade_state_change_types": grade_state_change_types,
        "grade_table": grade_table,
        "batch_session_ops_form": batch_session_ops_form,

        "total_sessions": total_sessions,
        "finished_sessions": finished_sessions,
        })

# }}}


# {{{ reopen session UI

NONE_SESSION_TAG = "<<<NONE>>>"  # noqa


class ReopenSessionForm(StyledForm):
    def __init__(self, flow_desc, current_tag, *args, **kwargs):
        super(ReopenSessionForm, self).__init__(*args, **kwargs)

        rules = getattr(flow_desc, "rules", object())
        tags = getattr(rules, "tags", [])

        tags = [NONE_SESSION_TAG] + tags
        self.fields["set_access_rules_tag"] = forms.ChoiceField(
                [(tag, tag) for tag in tags],
                initial=(current_tag
                    if current_tag is not None
                    else NONE_SESSION_TAG),
                label=_("Set access rules tag"))

        self.fields["comment"] = forms.CharField(
                widget=forms.Textarea, required=True,
                label=_("Comment"))

        self.helper.add_input(
                Submit(
                    "reopen", _("Reopen")))


@course_view
@transaction.atomic
def view_reopen_session(pctx, flow_session_id, opportunity_id):
    if pctx.role not in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        raise PermissionDenied()

    request = pctx.request

    session = get_object_or_404(FlowSession, id=int(flow_session_id))

    from course.content import get_flow_desc
    try:
        flow_desc = get_flow_desc(pctx.repo, pctx.course, session.flow_id,
                pctx.course_commit_sha)
    except ObjectDoesNotExist:
        raise http.Http404()

    if request.method == "POST":
        form = ReopenSessionForm(flow_desc, session.access_rules_tag,
            request.POST, request.FILES)

        may_reopen = True
        if session.in_progress:
            messages.add_message(pctx.request, messages.ERROR,
                    _("Cannot reopen a session that's already in progress."))
            may_reopen = False

        if form.is_valid() and may_reopen:
            new_access_rules_tag = form.cleaned_data["set_access_rules_tag"]
            if new_access_rules_tag == NONE_SESSION_TAG:
                new_access_rules_tag = None

            session.access_rules_tag = new_access_rules_tag

            from relate.utils import (
                    local_now, as_local_time,
                    format_datetime_local)
            session.append_comment(
                    ugettext("Session reopened at %(now)s by %(user)s, "
                        "previous completion time was '%(completion_time)s': "
                        "%(comment)s.") % {
                            "now": format_datetime_local(local_now()),
                            "user": pctx.request.user,
                            "completion_time": format_datetime_local(
                                as_local_time(session.completion_time)),
                            "comment": form.cleaned_data["comment"]
                            })
            session.save()

            from course.flow import reopen_session
            reopen_session(session, suppress_log=True)

            return redirect("relate-view_single_grade",
                    pctx.course.identifier,
                    session.participation.id,
                    opportunity_id)

    else:
        form = ReopenSessionForm(flow_desc, session.access_rules_tag)

    return render(request, "generic-form.html", {
        "form": form,
        "form_description": _("Reopen session")
        })

# }}}


# {{{ view single grade

def average_grade(opportunity):
    grade_changes = (GradeChange.objects
            .filter(opportunity=opportunity)
            .order_by(
                "participation__id",
                "grade_time")
            .select_related("participation")
            .select_related("opportunity"))

    grades = []
    my_grade_changes = []

    def finalize():
        if not my_grade_changes:
            return

        state_machine = GradeStateMachine()
        state_machine.consume(my_grade_changes)

        percentage = state_machine.percentage()
        if percentage is not None:
            grades.append(percentage)

        del my_grade_changes[:]

    last_participation = None
    for gchange in grade_changes:
        if last_participation != gchange.participation:
            finalize()
            last_participation = gchange.participation

        my_grade_changes.append(gchange)

    finalize()

    if grades:
        return sum(grades)/len(grades), len(grades)
    else:
        return None, 0


@course_view
def view_single_grade(pctx, participation_id, opportunity_id):
    now_datetime = get_now_or_fake_time(pctx.request)

    participation = get_object_or_404(Participation,
            id=int(participation_id))

    if participation.course != pctx.course:
        raise SuspiciousOperation(_("participation does not match course"))

    opportunity = get_object_or_404(GradingOpportunity, id=int(opportunity_id))

    if pctx.role in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        if not opportunity.shown_in_grade_book:
            messages.add_message(pctx.request, messages.INFO,
                    _("This grade is not shown in the grade book."))
        if not opportunity.shown_in_participant_grade_book:
            messages.add_message(pctx.request, messages.INFO,
                    _("This grade is not shown in the student grade book."))

    elif pctx.role == participation_role.student:
        if participation != pctx.participation:
            raise PermissionDenied(_("may not view other people's grades"))
        if not (opportunity.shown_in_grade_book
                and opportunity.shown_in_participant_grade_book):
            raise PermissionDenied(_("grade has not been released"))
    else:
        raise PermissionDenied()

    # {{{ modify sessions buttons

    if pctx.role in [
            participation_role.instructor,
            participation_role.teaching_assistant]:
        allow_session_actions = True

        request = pctx.request
        if pctx.request.method == "POST":
            action_re = re.compile("^([a-z]+)_([0-9]+)$")
            for key in request.POST.keys():
                action_match = action_re.match(key)
                if action_match:
                    break

            if not action_match:
                raise SuspiciousOperation(_("unknown action"))

            session = FlowSession.objects.get(id=int(action_match.group(2)))
            op = action_match.group(1)

            from course.flow import (
                    regrade_session,
                    recalculate_session_grade,
                    expire_flow_session_standalone,
                    finish_flow_session_standalone)

            try:
                if op == "expire":
                    expire_flow_session_standalone(
                            pctx.repo, pctx.course, session, now_datetime)
                    messages.add_message(pctx.request, messages.SUCCESS,
                            _("Session expired."))

                elif op == "end":
                    finish_flow_session_standalone(
                            pctx.repo, pctx.course, session,
                            now_datetime=now_datetime)
                    messages.add_message(pctx.request, messages.SUCCESS,
                            _("Session ended."))

                elif op == "regrade":
                    regrade_session(
                            pctx.repo, pctx.course, session)
                    messages.add_message(pctx.request, messages.SUCCESS,
                            _("Session regraded."))

                elif op == "recalculate":
                    recalculate_session_grade(
                            pctx.repo, pctx.course, session)
                    messages.add_message(pctx.request, messages.SUCCESS,
                            _("Session grade recalculated."))

                else:
                    raise SuspiciousOperation(_("invalid session operation"))

            except Exception as e:
                messages.add_message(pctx.request, messages.ERROR,
                        string_concat(
                            pgettext_lazy("Starting of Error message",
                                "Error"),
                            ": %(err_type)s %(err_str)s")
                        % {
                            "err_type": type(e).__name__,
                            "err_str": str(e)})
    else:
        allow_session_actions = False

    # }}}

    grade_changes = list(GradeChange.objects
            .filter(
                opportunity=opportunity,
                participation=participation)
            .order_by("grade_time")
            .select_related("participation")
            .select_related("participation__user")
            .select_related("creator")
            .select_related("opportunity"))

    state_machine = GradeStateMachine()
    state_machine.consume(grade_changes, set_is_superseded=True)

    if opportunity.flow_id:
        flow_sessions = list(FlowSession.objects
                .filter(
                    participation=participation,
                    flow_id=opportunity.flow_id,
                    )
                .order_by("start_time"))

        from collections import namedtuple
        SessionProperties = namedtuple(  # noqa
                "SessionProperties",
                ["due", "grade_description"])

        from course.utils import get_session_grading_rule
        from course.content import get_flow_desc

        try:
            flow_desc = get_flow_desc(pctx.repo, pctx.course,
                    opportunity.flow_id, pctx.course_commit_sha)
        except ObjectDoesNotExist:
            flow_sessions_and_session_properties = None
        else:
            flow_sessions_and_session_properties = []
            for session in flow_sessions:
                grading_rule = get_session_grading_rule(
                        session, pctx.role, flow_desc, now_datetime)

                session_properties = SessionProperties(
                        due=grading_rule.due,
                        grade_description=grading_rule.description)
                flow_sessions_and_session_properties.append(
                        (session, session_properties))

    else:
        flow_sessions_and_session_properties = None

    avg_grade_percentage, avg_grade_population = average_grade(opportunity)

    show_privileged_info = pctx.role in [
            participation_role.instructor,
            participation_role.teaching_assistant
            ]
    show_page_grades = (
            show_privileged_info
            or opportunity.page_scores_in_participant_gradebook)

    return render_course_page(pctx, "course/gradebook-single.html", {
        "opportunity": opportunity,
        "avg_grade_percentage": avg_grade_percentage,
        "avg_grade_population": avg_grade_population,
        "grade_participation": participation,
        "grade_state_change_types": grade_state_change_types,
        "grade_changes": grade_changes,
        "state_machine": state_machine,
        "flow_sessions_and_session_properties": flow_sessions_and_session_properties,
        "allow_session_actions": allow_session_actions,
        "show_privileged_info": show_privileged_info,
        "show_page_grades": show_page_grades,
        })

# }}}


# {{{ import grades

class ImportGradesForm(StyledForm):
    def __init__(self, course, *args, **kwargs):
        super(ImportGradesForm, self).__init__(*args, **kwargs)

        self.fields["grading_opportunity"] = forms.ModelChoiceField(
            queryset=(GradingOpportunity.objects
                .filter(course=course)
                .order_by("identifier")),
            help_text=_("Click to <a href='%s' target='_blank'>create</a> "
            "a new grading opportunity. Reload this form when done.")
            % reverse("admin:course_gradingopportunity_add"),
            label=pgettext_lazy("Field name in Import grades form",
                                "Grading opportunity"))

        self.fields["attempt_id"] = forms.CharField(
                initial="main",
                required=True,
                label=_("Attempt ID"))
        self.fields["file"] = forms.FileField(
                label=_("File"))

        self.fields["format"] = forms.ChoiceField(
                choices=(
                    ("csvhead", _("CSV with Header")),
                    ("csv", "CSV"),
                    ),
                label=_("Format"))

        self.fields["id_column"] = forms.IntegerField(
                # Translators: the following strings are for the format
                # informatioin for a CSV file to be imported.
                help_text=_("1-based column index for the Email or NetID "
                "used to locate student record"),
                min_value=1,
                label=_("User ID column"))
        self.fields["points_column"] = forms.IntegerField(
                help_text=_("1-based column index for the (numerical) grade"),
                min_value=1,
                label=_("Points column"))
        self.fields["feedback_column"] = forms.IntegerField(
                help_text=_("1-based column index for further (textual) feedback"),
                min_value=1, required=False,
                label=_("Feedback column"))
        self.fields["max_points"] = forms.DecimalField(
                initial=100,
                # Translators: "Max point" refers to full credit in points.
                label=_("Max points"))

        self.helper.add_input(Submit("preview", _("Preview")))
        self.helper.add_input(Submit("import", _("Import")))


class ParticipantNotFound(ValueError):
    pass


def find_participant_from_id(course, id_str):
    id_str = id_str.strip().lower()

    matches = (Participation.objects
            .filter(
                course=course,
                status=participation_status.active,
                user__email__istartswith=id_str)
            .select_related("user"))

    surviving_matches = []
    for match in matches:
        if match.user.email.lower() == id_str:
            surviving_matches.append(match)
            continue

        email = match.user.email.lower()
        at_index = email.index("@")
        assert at_index > 0
        uid = email[:at_index]

        if uid == id_str:
            surviving_matches.append(match)
            continue

    if not surviving_matches:
        raise ParticipantNotFound(
                # Translators: use id_string to find user (participant).
                _("no participant found for '%(id_string)s'") % {
                    "id_string": id_str})
    if len(surviving_matches) > 1:
        raise ParticipantNotFound(
                _("more than one participant found for '%(id_string)s'") % {
                    "id_string": id_str})

    return surviving_matches[0]


def fix_decimal(s):
    if "," in s and "." not in s:
        comma_count = len([c for c in s if c == ","])
        if comma_count == 1:
            return s.replace(",", ".")
        else:
            return s

    else:
        return s


def csv_to_grade_changes(
        log_lines,
        course, grading_opportunity, attempt_id, file_contents,
        id_column, points_column, feedback_column, max_points,
        creator, grade_time, has_header):
    result = []

    import csv

    total_count = 0
    spamreader = csv.reader(file_contents)
    for row in spamreader:
        if has_header:
            has_header = False
            continue

        gchange = GradeChange()
        gchange.opportunity = grading_opportunity
        try:
            gchange.participation = find_participant_from_id(
                    course, row[id_column-1])
        except ParticipantNotFound as e:
            log_lines.append(e)
            continue

        gchange.state = grade_state_change_types.graded
        gchange.attempt_id = attempt_id

        points_str = row[points_column-1].strip()
        # Moodle's "NULL" grades look like this.
        if points_str in ["-", ""]:
            gchange.points = None
        else:
            gchange.points = float(fix_decimal(points_str))

        gchange.max_points = max_points
        if feedback_column is not None:
            gchange.comment = row[feedback_column-1]

        gchange.creator = creator
        gchange.grade_time = grade_time

        last_grades = (GradeChange.objects
                .filter(
                    opportunity=grading_opportunity,
                    participation=gchange.participation,
                    attempt_id=gchange.attempt_id)
                .order_by("-grade_time")[:1])

        if last_grades.count():
            last_grade, = last_grades

            if last_grade.state == grade_state_change_types.graded:

                updated = []
                if last_grade.points != gchange.points:
                    updated.append("points")
                if last_grade.max_points != gchange.max_points:
                    updated.append("max_points")
                if last_grade.comment != gchange.comment:
                    updated.append("comment")

                if updated:
                    log_lines.append(
                            "%(participation)s: %(updated)s "
                            "updated" % {
                                'participation': gchange.participation,
                                'updated': ", ".join(updated)})

                    result.append(gchange)
            else:
                result.append(gchange)

        else:
            result.append(gchange)

        total_count += 1

    return total_count, result


@course_view
@transaction.atomic
def import_grades(pctx):
    if pctx.role != participation_role.instructor:
        raise PermissionDenied()

    form_text = ""

    log_lines = []

    request = pctx.request
    if request.method == "POST":
        form = ImportGradesForm(
                pctx.course, request.POST, request.FILES)

        is_import = "import" in request.POST
        if form.is_valid():
            try:
                total_count, grade_changes = csv_to_grade_changes(
                        log_lines=log_lines,
                        course=pctx.course,
                        grading_opportunity=form.cleaned_data["grading_opportunity"],
                        attempt_id=form.cleaned_data["attempt_id"],
                        file_contents=request.FILES["file"],
                        id_column=form.cleaned_data["id_column"],
                        points_column=form.cleaned_data["points_column"],
                        feedback_column=form.cleaned_data["feedback_column"],
                        max_points=form.cleaned_data["max_points"],
                        creator=request.user,
                        grade_time=now(),
                        has_header=form.cleaned_data["format"] == "csvhead")
            except Exception as e:
                messages.add_message(pctx.request, messages.ERROR,
                        string_concat(
                            pgettext_lazy("Starting of Error message",
                                "Error"),
                            ": %(err_type)s %(err_str)s")
                        % {
                            "err_type": type(e).__name__,
                            "err_str": str(e)})
            else:
                if total_count != len(grade_changes):
                    messages.add_message(pctx.request, messages.INFO,
                            _("%(total)d grades found, %(unchaged)d unchanged.")
                            % {'total': total_count,
                               'unchaged': total_count - len(grade_changes)})

                from django.template.loader import render_to_string

                if is_import:
                    GradeChange.objects.bulk_create(grade_changes)
                    form_text = render_to_string(
                            "course/grade-import-preview.html", {
                                "show_grade_changes": False,
                                "log_lines": log_lines,
                                })
                    messages.add_message(pctx.request, messages.SUCCESS,
                            _("%d grades imported.") % len(grade_changes))
                else:
                    form_text = render_to_string(
                            "course/grade-import-preview.html", {
                                "show_grade_changes": True,
                                "grade_changes": grade_changes,
                                "log_lines": log_lines,
                                })

    else:
        form = ImportGradesForm(pctx.course)

    return render_course_page(pctx, "course/generic-course-form.html", {
        "form_description": _("Import Grade Data"),
        "form": form,
        "form_text": form_text,
        })

# }}}


# {{{ download all submissions

class DownloadAllSubmissionsForm(StyledForm):
    def __init__(self, page_ids, session_tag_choices, *args, **kwargs):
        super(DownloadAllSubmissionsForm, self).__init__(*args, **kwargs)

        self.fields["page_id"] = forms.ChoiceField(
                choices=tuple(
                    (pid, pid)
                    for pid in page_ids),
                label=_("Page ID"))
        self.fields["which_attempt"] = forms.ChoiceField(
                choices=(
                    ("first", _("Least recent attempt")),
                    ("last", _("Most recent attempt")),
                    ("all", _("All attempts")),
                    ),
                label=_("Attempts to include."),
                help_text=_(
                    "Every submission to the page counts as an attempt."),
                initial="last")
        self.fields["restrict_to_rules_tag"] = forms.ChoiceField(
                choices=session_tag_choices,
                help_text=_("Only download sessions tagged with this rules tag."),
                label=_("Restrict to rules tag"))
        self.fields["non_in_progress_only"] = forms.BooleanField(
                required=False,
                initial=True,
                help_text=_("Only download submissions from non-in-progress "
                    "sessions"),
                label=_("Non-in-progress only"))
        self.fields["extra_file"] = forms.FileField(
                label=_("Additional File"),
                help_text=_(
                    "If given, the uploaded file will be included "
                    "in the zip archive. "
                    "If the produced archive is to be used for plagiarism "
                    "detection, then this may be used to include the reference "
                    "solution."),
                required=False)

        self.helper.add_input(
                Submit("download", _("Download")))


@course_view
def download_all_submissions(pctx, flow_id):
    if pctx.role not in [
            participation_role.teaching_assistant,
            participation_role.instructor,
            participation_role.observer,
            ]:
        raise PermissionDenied(_("must be at least TA to download submissions"))

    from course.content import get_flow_desc
    flow_desc = get_flow_desc(pctx.repo, pctx.course, flow_id,
            pctx.course_commit_sha)

    # {{{ find access rules tag

    if hasattr(flow_desc, "rules"):
        access_rules_tags = getattr(flow_desc.rules, "tags", [])
    else:
        access_rules_tags = []

    ALL_SESSION_TAG = string_concat("<<<", _("ALL"), ">>>")  # noqa
    session_tag_choices = [
            (tag, tag)
            for tag in access_rules_tags] + [(ALL_SESSION_TAG,
                    string_concat("(", _("ALL"), ")"))]

    # }}}

    page_ids = [
            "%s/%s" % (group_desc.id, page_desc.id)
            for group_desc in flow_desc.groups
            for page_desc in group_desc.pages]

    request = pctx.request
    if request.method == "POST":
        form = DownloadAllSubmissionsForm(page_ids, session_tag_choices,
                request.POST)

        if form.is_valid():
            which_attempt = form.cleaned_data["which_attempt"]

            slash_index = form.cleaned_data["page_id"].index("/")
            group_id = form.cleaned_data["page_id"][:slash_index]
            page_id = form.cleaned_data["page_id"][slash_index+1:]

            from course.utils import PageInstanceCache
            page_cache = PageInstanceCache(pctx.repo, pctx.course, flow_id)

            visits = (FlowPageVisit.objects
                    .filter(
                        flow_session__course=pctx.course,
                        flow_session__flow_id=flow_id,
                        page_data__group_id=group_id,
                        page_data__page_id=page_id,
                        is_submitted_answer=True,
                        )
                    .select_related("flow_session")
                    .select_related("flow_session__participation__user")
                    .select_related("page_data")

                    # We overwrite earlier submissions with later ones
                    # in a dictionary below.
                    .order_by("visit_time"))

            if form.cleaned_data["non_in_progress_only"]:
                visits = visits.filter(flow_session__in_progress=False)

            if form.cleaned_data["restrict_to_rules_tag"] != ALL_SESSION_TAG:
                visits = visits.filter(
                        flow_session__access_rules_tag=(
                            form.cleaned_data["restrict_to_rules_tag"]))

            submissions = {}

            for visit in visits:
                page = page_cache.get_page(group_id, page_id,
                        pctx.course_commit_sha)

                from course.page import PageContext
                grading_page_context = PageContext(
                        course=pctx.course,
                        repo=pctx.repo,
                        commit_sha=pctx.course_commit_sha,
                        flow_session=visit.flow_session)

                bytes_answer = page.normalized_bytes_answer(
                        grading_page_context, visit.page_data.data,
                        visit.answer)

                if which_attempt in ["first", "last"]:
                    key = (visit.flow_session.participation.user.username,)
                elif which_attempt == "all":
                    key = (visit.flow_session.participation.user.username,
                            str(visit.flow_session.id))
                else:
                    raise NotImplementedError()

                if bytes_answer is not None:
                    if (which_attempt == "first"
                            and key in submissions):
                        # Already there, disregard further ones
                        continue

                    submissions[key] = bytes_answer

            from six import BytesIO
            from zipfile import ZipFile
            bio = BytesIO()
            with ZipFile(bio, "w") as subm_zip:
                for key, (extension, bytes_answer) in \
                        six.iteritems(submissions):
                    subm_zip.writestr(
                            "-".join(key) + extension,
                            bytes_answer)

                extra_file = request.FILES.get("extra_file")
                if extra_file is not None:
                    subm_zip.writestr(extra_file.name, extra_file.read())

            response = http.HttpResponse(
                    bio.getvalue(),
                    content_type="application/zip")
            response['Content-Disposition'] = (
                    'attachment; filename="submissions_%s_%s_%s_%s_%s.zip"'
                    % (pctx.course.identifier, flow_id, group_id, page_id,
                        now().date().strftime("%Y-%m-%d")))
            return response

    else:
        form = DownloadAllSubmissionsForm(page_ids, session_tag_choices)

    return render_course_page(pctx, "course/generic-course-form.html", {
        "form": form,
        "form_description": _("Download All Submissions in Zip file")
        })

# }}}

# vim: foldmethod=marker
