from crispy_forms.layout import Submit
from django.shortcuts import (  # noqa
        render, get_object_or_404, redirect, resolve_url)
from django.contrib import messages
from django import forms
from django.core.urlresolvers import reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from course_statistics.models import ParticipationSurvey
from questionnaire.models import Question, Questionnaire

from questionnaire.forms import DisplayQuestionsForm, get_form_field

from questionnaire.views import (
    QuestionnaireMixin, TakeQuestionnaire as TQ,
    ThanksView as TV
)

from course.utils import course_view

from django.views.generic import (
        CreateView, DeleteView, ListView, DetailView, UpdateView)
from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy, ugettext, string_concat)
from django.shortcuts import render
from django.db.models import Count

from django.core.exceptions import (
        PermissionDenied, SuspiciousOperation, ObjectDoesNotExist)

from course.utils import (
        course_view, render_course_page,
        get_session_access_rule)

from relate.utils import StyledForm

from course.constants import (
        participation_permission as pperm,
        flow_permission
        )

from course.models import (
        Participation, participation_status,
        Course,
        GradingOpportunity,
        grade_state_change_types,
        FlowSession, FlowPageVisit)

# from crowdsourcing.models import Question, Survey, Answer, Section

from course_statistics.models import (
    ParticipationSurvey, StatisticStateMachine, QuestionPerParticipant,
    ParticipationSurveyQuestionAnswer as PSQA
)
# Create your views here.


@login_required
@course_view
def view_survey_list(pctx):
    if not pctx.has_permission(pperm.view_analytics):
        raise PermissionDenied(_("may not view analytics"))

    survey_list = list(
        Questionnaire.objects.filter(
            survey__participation__course=pctx.course)
            .distinct("pk")
            .order_by("-pk"))

    return render_course_page(pctx, "course_statistics/survey_all.html", {
        "survey_list": survey_list,
        })

class ListQuestionnaireView(ListView):
    model = Questionnaire
    template_name = "course_statistics/list.html"

    def get_context_data(self, **kwargs):
        context = super(ListQuestionnaireView, self).get_context_data(**kwargs)
        context['questionnaires'] = Questionnaire.objects.order_by('id')
        return context


class DisplaySurveyForm(forms.Form):
    def __init__(self, questionnaire_id, participation_id, *args, **kwargs):
        super(DisplaySurveyForm, self).__init__(*args, **kwargs)
        self.participation_id = participation_id
        self.questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
        for index, question in enumerate(self.questionnaire.questions()):
            get_form_field(self, question)

    def save(self, user):
        for index, question in enumerate(self.questionnaire.questions()):
            answer_text = self.cleaned_data['question_{0}'.format(question.pk)]
            participation = Participation.objects.get(id=self.participation_id)

            if answer_text:
                try:
                    answer_save = PSQA.objects.get(
                        participation=participation,
                        user=user,
                        question=question
                    )
                except PSQA.DoesNotExist:
                    answer_save = PSQA(
                        user=user,
                        participation=participation,
                        question=question,
                        answer = answer_text
                    )
                answer_save.save()

# class DisplaySurveyForm(DisplaySurveyForm):
#     def __init__(self, questionnaire_id, *args, **kwargs):
#         participation_id = kwargs.pop("participation_id")
#         super(DisplaySurveyForm, self).__init__(*args, **kwargs)
#         participation = Participation.objects.get(id=int(participation_id))



class SurveyMixin(QuestionnaireMixin):
    template_name = 'course_statistics/create.html'
    model = Questionnaire
    # model = ParticipationSurvey


class CreateQuestionnaireView(QuestionnaireMixin, CreateView):
    template_name = "course_statistics/create.html"

    def get_success_url(self):
        return reverse('update-questionnaire', kwargs={'pk': self.object.id})


class UpdateQuestionnaireView(QuestionnaireMixin, UpdateView):

    def get_initial(self):
        return {'pk': self.kwargs['pk']}

    def get_success_url(self):
        return reverse('update-questionnaire', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(UpdateQuestionnaireView, self).get_context_data()
        context['display_questions'] =\
            DisplaySurveyForm(questionnaire_id=self.kwargs['pk'])
        return context

class CourseViewMixin(UserPassesTestMixin):
    # Mixin for determin if user can upload/delete/modify image in flow_page
    raise_exception = True

    def test_func(self):
        request = self.request
        flow_session_id = self.kwargs['flow_session_id']
        ordinal = self.kwargs['ordinal']
        course_identifier = self.kwargs['course_identifier']

        from course.utils import CoursePageContext
        pctx = CoursePageContext(request, course_identifier)

# class ListBlocksView(ListView):
#     model = Block
#     fields = '__all__'
#
# class QuestionListView(ListView):
#     # Prevent download Json response in IE 7-10
#     # http://stackoverflow.com/a/13944206/3437454):
#     model = StatisticsQuestion
#
#     def get_queryset(self):
#         flow_session_id = self.kwargs["flow_session_id"]
#         ordinal = self.kwargs["ordinal"]
#
#         try:
#             fpd = FlowPageData.objects.get(
#                     flow_session=flow_session_id, ordinal=ordinal)
#         except ValueError:
#
#             # in sandbox
#             if flow_session_id == "None" or ordinal == "None":
#                 return None
#
#         return FlowPageImage.objects\
#                 .filter(flow_session=flow_session_id)\
#                 .filter(image_page_id=fpd.page_id)\
#                 .order_by("order","pk")


class SurveyInfo:
    def __init__(self, question, stat_state_machine):
        ## type: (SurveyQuestion, StatStateMachine) -> None
        self.question = question
        self.stat_state_machine = stat_state_machine
    def __str__(self):
        return repr(self.question) + "---" + repr(self.stat_state_machine)


def get_survey_table(course, survey_pk):
    ## type: (Course) -> Tuple[List[Participation], List[SurveyQuestion], List[List[SurveyInfo]]]  # noqa

    # NOTE: It's important that these queries are sorted consistently,
    # also consistently with the code below.

    survey_questions = list(
        (Question.objects
         .filter(
            questionnaire__pk=survey_pk,
        )
         .select_related("questionnaire")
         .order_by("order", "pk")
         )
    )

    participations = list(Participation.objects
            .filter(
                course=course,
                status=participation_status.active)
            .annotate(null_id=Count('user__institutional_id'))
            .order_by("-null_id","user__institutional_id")
            .select_related("user"))

    question_status = list(QuestionPerParticipant.objects
            .filter(
                participation__course=course,
                )
            .annotate(null_id=Count('participation__user__institutional_id'))
            .order_by(
                "-null_id",
                "participation__user__institutional_id",
                "question__pk",
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
        for ques in survey_questions:
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
                SurveyInfo(
                    question=ques,
                    stat_state_machine=state_machine)
            )

            stat_row.append(
                    SurveyInfo(
                        question=ques,
                        stat_state_machine=state_machine))

        stat_table.append(stat_row)

    return participations, survey_questions, stat_table


@login_required
@course_view
def view_single_survey_book(pctx, survey_pk):
    request = pctx.request
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view course statistics"))

    participations, survey_questions, survey_table = get_survey_table(pctx.course, survey_pk)

    def sort_key(entry):
        (participation, question) = entry
        return (participation.user.institutional_id,)

    survey_table = sorted(zip(participations, survey_table), key=sort_key)
    print(survey_table)

    return render_course_page(pctx, "course_statistics/statistic_book.html", {
        "survey_table": survey_table,
        "survey_questions": survey_questions,
        "participations": participations,
        "survey_pk": survey_pk
        #"grade_state_change_types": grade_state_change_types,
        })

@login_required
@course_view
def view_participant_single_survey(pctx, participation, survey_pk):
    request = pctx.request
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view course statistics"))

    part_survey, created =  ParticipationSurvey.objects.get_or_create(
                    participation=participation,
                    questionnaire__pk=survey_pk
                    )

    return render_course_page(pctx, "course_statistics/statistic_book.html", {
        "survey_table": survey_table,
        "survey_questions": survey_questions,
        "participations": participations,
        #"grade_state_change_types": grade_state_change_types,
        })




class LinkSurveyForm(StyledForm):
    def __init__(self, *args, **kwargs):
        # type:(*Any, **Any) -> None

        super(LinkSurveyForm, self).__init__(*args, **kwargs)

        self.fields["survey"] = forms.ModelChoiceField(
                queryset=Questionnaire.objects.order_by("pk"),
                required=True,
                help_text=_("Select survey to link to this course."),
                label=_("Survey"))

        self.helper.add_input(Submit("submit", _("Link")))

@login_required
@course_view
def link_survey_with_course(pctx):
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not create course statistics"))
    request = pctx.request
    if request.method == 'POST':
        form = LinkSurveyForm(request.POST)
        if form.is_valid():
            survey = form.cleaned_data["survey"]
            for participation in (
                    Participation.objects.filter(
                        course=pctx.course,
                        status=participation_status.active)
                            .order_by("user__last_name")
            ):
                ParticipationSurvey.objects.get_or_create(
                    participation=participation,
                    questionnaire=survey
                    )
            messages.add_message(request, messages.INFO,
                                 _("The survey is linked to the course."))
    else:
        form = LinkSurveyForm()

    return render(request, "generic-form.html", {
        "form_description": _("Link survey to course"),
        "form": form
        })

#CourseViewMixin

class FillParticipationSurvey(TQ):
    form_class = DisplaySurveyForm
    template_name = 'course_statistics/display.html'

    def get_form_kwargs(self):
        kwargs = super(FillParticipationSurvey, self).get_form_kwargs()
        pk = self.kwargs['pk']
        participation_id = self.kwargs['participation_id']
        kwargs.update({
            'questionnaire_id': pk,
            'participation_id': participation_id
        })

        questionnaire = Questionnaire.objects.get(pk=pk)
        exist_answer = {}
        for index, question in enumerate(questionnaire.questions()):
            try:
                answer = PSQA.objects.get(
                        participation__id=participation_id,
                        question=question
                    )
                exist_answer['question_{0}'.format(question.pk)] = answer.answer
                #print(answer.answer)
            except PSQA.DoesNotExist:
                pass
        kwargs.update(initial=exist_answer)
        return kwargs

    def get_success_url(self):
        return reverse('thanks-page', self.kwargs['course_identifier'])

    def get_context_data(self, **kwargs):
        context = super(FillParticipationSurvey, self).get_context_data(**kwargs)

        participation_id = self.kwargs['participation_id']
        context["participation"] = Participation.objects.get(id=participation_id)
        context["course"] = Course.objects.get(identifier=self.kwargs['course_identifier'])

        return context

class ThanksView(TV):
    template_name = "course_statistics/thanks.html"

    def get_context_data(self, **kwargs):
        context = super(ThanksView, self).get_context_data(**kwargs)
        print(self.kwargs)
        context["course_identifier"] = self.kwargs['course_identifier']
        return context


# @course_view
# def view_stat_by_question(pctx, question_id):
#     request = pctx.request
#     if not pctx.has_permission(pperm.view_gradebook):
#         raise PermissionDenied(_("may not view course statistics"))
#     return render_course_page(pctx, "course_statistics/statistic_book.html",
#                               {})


# class SurveyUpdateView(UpdateView):
#     model = ParticipationSurvey
#     fields = '__all__'
#
#     def get_template_names(self):
#         return ['course_statistics/question_form.html']
#
#     def get_form_class(self):
#         return nestedformset_factory(
#             ParticipationSurvey,
#             Section,
#             nested_formset=inlineformset_factory(
#                 Section,
#                 Question,
#                 fields='__all__'
#             )
#         )
#
#     def get_success_url(self):
#         return reverse('blocks-list')