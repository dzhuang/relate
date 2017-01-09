from django.views.generic import (
        CreateView, DeleteView, ListView, DetailView)
from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy, ugettext, string_concat)
from django.shortcuts import render
from django.db.models import Count

from django.core.exceptions import (
        PermissionDenied, SuspiciousOperation, ObjectDoesNotExist)

from course.utils import (
        course_view, render_course_page,
        get_session_access_rule)
from course.constants import (
        participation_permission as pperm,
        flow_permission
        )

from course.models import (
        Participation, participation_status,
        GradingOpportunity,
        grade_state_change_types,
        FlowSession, FlowPageVisit)

from course_statistics.models import (
    StatisticsQuestion, StatisticStateMachine, QuestionPerParticipant
)
# Create your views here.

class QuestionListView(ListView):
    # Prevent download Json response in IE 7-10
    # http://stackoverflow.com/a/13944206/3437454):
    model = StatisticsQuestion

    def get_queryset(self):
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]

        try:
            fpd = FlowPageData.objects.get(
                    flow_session=flow_session_id, ordinal=ordinal)
        except ValueError:

            # in sandbox
            if flow_session_id == "None" or ordinal == "None":
                return None

        return FlowPageImage.objects\
                .filter(flow_session=flow_session_id)\
                .filter(image_page_id=fpd.page_id)\
                .order_by("order","pk")


class StatInfo:
    def __init__(self, question, stat_state_machine):
        # type: (SurveyQuestion, StatStateMachine) -> None
        self.question = question
        self.stat_state_machine = stat_state_machine
    def __str__(self):
        return repr(self.question) + "---" + repr(self.stat_state_machine)


def get_stat_table(course):
    # type: (Course) -> Tuple[List[Participation], List[SurveyQuestion], List[List[StatInfo]]]  # noqa

    # NOTE: It's important that these queries are sorted consistently,
    # also consistently with the code below.
    stat_questions = list((StatisticsQuestion.objects
            .filter(
                course=course,
                )
            .order_by("fieldname")))

    participations = list(Participation.objects
            .filter(
                course=course,
                status=participation_status.active)
            .annotate(null_id=Count('user__institutional_id'))
            .order_by("-null_id","user__institutional_id")
            .select_related("user"))

    question_status = list(QuestionPerParticipant.objects
            .filter(
                question__course=course,
                )
            .annotate(null_id=Count('participation__user__institutional_id'))
            .order_by(
                "-null_id",
                "participation__user__institutional_id",
                "question__fieldname",
                )
            .select_related("participation")
            .select_related("participation__user")
            .select_related("question"))

    idx = 0

    # for participation in participations:
    #     while (
    #             idx < len(grade_changes)
    #             and grade_changes[idx].participation.id < participation.id):
    #         idx += 1
    #
    #     grade_row = []
    #     for opp in grading_opps:
    #         while (
    #                 idx < len(grade_changes)
    #                 and grade_changes[idx].participation.pk == participation.pk
    #                 and grade_changes[idx].opportunity.identifier < opp.identifier
    #                 ):
    #             idx += 1
    #
    #         my_grade_changes = []
    #         while (
    #                 idx < len(grade_changes)
    #                 and grade_changes[idx].opportunity.pk == opp.pk
    #                 and grade_changes[idx].participation.pk == participation.pk):
    #             my_grade_changes.append(grade_changes[idx])
    #             idx += 1
    #
    #         state_machine = GradeStateMachine()
    #         state_machine.consume(my_grade_changes)
    #
    #         grade_row.append(
    #                 GradeInfo(
    #                     opportunity=opp,
    #                     grade_state_machine=state_machine))
    #
    #     grade_table.append(grade_row)

    stat_table = []
    for participation in participations:
        while (
                idx < len(question_status)
                and question_status[idx].participation.id < participation.id):
            idx += 1

        stat_row = []
        for ques in stat_questions:
            while (
                    idx < len(question_status)
                    and question_status[idx].participation.pk == participation.pk
                    and question_status[idx].question.pk < ques.pk
                    ):
                idx += 1

            my_question_status = []
            while (
                    idx < len(question_status)
                    and question_status[idx].question.pk == ques.pk
                    and question_status[idx].participation.pk == participation.pk):
                my_question_status.append(question_status[idx])
                idx += 1

            state_machine = StatisticStateMachine()
            state_machine.consume(my_question_status)

            print(
                StatInfo(
                    question=ques,
                    stat_state_machine=state_machine)
            )

            stat_row.append(
                    StatInfo(
                        question=ques,
                        stat_state_machine=state_machine))

        stat_table.append(stat_row)

    return participations, stat_questions, stat_table

@course_view
def view_stat_book(pctx):
    request = pctx.request
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view course statistics"))

    participations, stat_questions, stat_table = get_stat_table(pctx.course)

    def sort_key(entry):
        (participation, question) = entry
        return (participation.user.institutional_id,)

    stat_table = sorted(zip(participations, stat_table), key=sort_key)

    #participations, stat_questions, stat_table

    return render_course_page(pctx, "course_statistics/statistic_book.html", {
        "stat_table": stat_table,
        "stat_questions": stat_questions,
        "participations": participations,
        #"grade_state_change_types": grade_state_change_types,
        })


@course_view
def view_stat_by_question(pctx, question_id):
    request = pctx.request
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view course statistics"))
    return render_course_page(pctx, "course_statistics/statistic_book.html",
                              {})
