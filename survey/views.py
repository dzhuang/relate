# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

from crispy_forms.layout import Submit
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.db.models import Count
from django.core.exceptions import (
        PermissionDenied, SuspiciousOperation)
from django import forms
from django.urls import reverse
from django.views.generic import (
    FormView, TemplateView,
    CreateView, ListView, UpdateView)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from questionnaire.models import Question, Questionnaire
from questionnaire.forms import DisplayQuestionsForm, get_form_field
from questionnaire.views import QuestionnaireMixin, ThanksView as Tv

from course.constants import participation_permission as pperm
from course.models import Participation, participation_status
from course.utils import (
    CoursePageContext, ParticipationPermissionWrapper,
    course_view, render_course_page)

from relate.utils import StyledForm

from survey.models import (
    CourseSurvey, QuestionAnsweredStateMachine,
    ParticipationSurveyQuestionAnswer as Psqa
)


class CourseViewMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


@login_required
@course_view
def view_survey_list(pctx):
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view analytics"))

    survey_list = list(
        CourseSurvey.objects.filter(
            course=pctx.course)
        .distinct("pk")
        .order_by("-pk")
    )

    return render_course_page(pctx, "survey/survey_all.html", {
        "survey_list": survey_list,
        })


@login_required
@course_view
def view_survey_by_question(pctx, survey_pk, question_pk):
    # type: (CoursePageContext, Text) -> http.HttpResponse

    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view grade book"))

    survey = get_object_or_404(CourseSurvey, id=int(survey_pk))

    if pctx.course != survey.course:
        raise SuspiciousOperation(_("survey from wrong course"))

    survey_questions = survey.questionnaire.questions()
    question = get_object_or_404(Question, id=int(question_pk))

    if question not in survey_questions:
        raise SuspiciousOperation(_("question from wrong survey"))

    participations = list(
        Participation.objects.filter(
            course=pctx.course,
            status=participation_status.active)
        .annotate(null_id=Count('user__institutional_id'))
        .order_by("-null_id", "user__institutional_id")
        .select_related("user"))

    answers = list(
        Psqa.objects.filter(
            survey=survey,
            participation__course=pctx.course,
            question=question)
        .annotate(null_id=Count('participation__user__institutional_id'))
        .order_by(
            "-null_id",
            "participation__user__institutional_id")
        .select_related("participation")
        .select_related("participation__user")
        .select_related("question")
    )

    qanswer_idx = 0

    survey_table = []
    for idx, participation in enumerate(participations):
        while (
                qanswer_idx < len(answers)
                and answers[qanswer_idx].participation.pk < participation.pk):
            qanswer_idx += 1

        my_answer_status = []
        while (
                qanswer_idx < len(answers)
                and answers[qanswer_idx].participation.pk == participation.pk):
            my_answer_status.append(answers[qanswer_idx])
            qanswer_idx += 1

        state_machine = QuestionAnsweredStateMachine()
        state_machine.consume(my_answer_status)

        survey_table.append(
                (participation, SurveyQuestionAnsweredInfo(
                    question=question,
                    answer_state_machine=state_machine,
                )))

    return render_course_page(pctx, "survey/survey_book_by_question.html", {
        "question": question,
        "survey_table": survey_table,
        "survey_questions": survey_questions,
        "participations": participations,
        "survey": survey,
        })

# }}}


class ListQuestionnaireView(CourseViewMixin, ListView):
    model = Questionnaire
    template_name = "survey/list.html"

    def get_context_data(self, **kwargs):
        context = super(ListQuestionnaireView, self).get_context_data(**kwargs)
        context['questionnaires'] = Questionnaire.objects.order_by('id')
        return context


class DisplaySurveyForm(forms.Form):
    def __init__(self, survey_pk, participation_id, *args, **kwargs):
        super(DisplaySurveyForm, self).__init__(*args, **kwargs)
        self.participation = Participation.objects.get(id=participation_id)
        self.survey = get_object_or_404(CourseSurvey, id=survey_pk)
        self.questionnaire = self.survey.questionnaire
        for index, question in enumerate(self.questionnaire.questions()):
            get_form_field(self, question)

    def save(self, user):
        for index, question in enumerate(self.questionnaire.questions()):
            answer_text = self.cleaned_data['question_{0}'.format(question.pk)]
            if answer_text:
                try:
                    answer_save = Psqa.objects.get(
                        survey=self.survey,
                        participation=self.participation,
                        question=question
                    )
                except Psqa.DoesNotExist:
                    answer_save = Psqa(
                        survey=self.survey,
                        user=user,
                        participation=self.participation,
                        question=question,
                    )
                answer_save.answer = answer_text
                answer_save.save()


class SurveyMixin(CourseViewMixin, QuestionnaireMixin):
    template_name = 'survey/create.html'
    model = Questionnaire


class CreateQuestionnaireView(SurveyMixin, CreateView, CourseViewMixin):
    template_name = "survey/create.html"

    def get_success_url(self):
        return reverse('update-questionnaire', kwargs={'pk': self.object.id})


class UpdateQuestionnaireView(SurveyMixin, UpdateView, CourseViewMixin):

    def get_initial(self):
        return {'pk': self.kwargs['pk']}

    def get_success_url(self):
        return reverse('update-questionnaire', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(UpdateQuestionnaireView, self).get_context_data()
        context['display_questions'] =\
            DisplayQuestionsForm(questionnaire_pk=self.kwargs['pk'])

        return context


class SurveyQuestionAnsweredInfo:
    def __init__(self, question, answer_state_machine):
        self.question = question
        self.answer_state_machine = answer_state_machine

    def __str__(self):
        return repr(self.question) + "---" + repr(self.answer_state_machine)


def get_survey_table(course, questionnaire_pk):

    # NOTE: It's important that these queries are sorted consistently,
    # also consistently with the code below.
    questionnaire = get_object_or_404(Questionnaire, pk=int(questionnaire_pk))

    survey_questions = list(
        (Question.objects.filter(questionnaire__pk=questionnaire.pk)
         .select_related("questionnaire")
         .order_by("order", "pk")
         ))

    participations = list(Participation.objects
            .filter(
                course=course,
                status=participation_status.active)
            .annotate(null_id=Count('user__institutional_id'))
            .order_by("-null_id", "user__institutional_id")
            .select_related("user"))

    answers = list(
        Psqa.objects.filter(participation__course=course, )
        .annotate(
            null_id=Count('participation__user__institutional_id'))
        .order_by(
            "-null_id",
            "participation__user__institutional_id",
            "question__pk",
            )
        .select_related("participation")
        .select_related("participation__user")
        .select_related("question"))

    idx = 0

    survey_table = []
    for participation in participations:
        while (
                idx < len(answers)
                and answers[idx].participation.id < participation.id):
            idx += 1

        stat_row = []
        for ques in survey_questions:
            while (
                    idx < len(answers)
                    and answers[idx].participation.pk == participation.pk
                    and answers[idx].question.pk < ques.pk
                    ):
                idx += 1
            my_answer_status = []
            while (
                    idx < len(answers)
                    and answers[idx].question.pk == ques.pk
                    and answers[idx].participation.pk == participation.pk):
                my_answer_status.append(answers[idx])
                idx += 1

            state_machine = QuestionAnsweredStateMachine()
            state_machine.consume(my_answer_status)

            stat_row.append(
                    SurveyQuestionAnsweredInfo(
                        question=ques,
                        answer_state_machine=state_machine))

        survey_table.append(stat_row)

    return participations, survey_questions, survey_table


@login_required
@course_view
def view_single_survey_book(pctx, survey_pk):
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view course statistics"))

    survey = get_object_or_404(CourseSurvey, pk=int(survey_pk))
    questionnaire_pk = survey.questionnaire.pk
    participations, survey_questions, survey_table = \
        get_survey_table(pctx.course, questionnaire_pk)

    def sort_key(entry):
        (participation, question) = entry
        return (participation.user.institutional_id,)

    survey_table = sorted(zip(participations, survey_table),
                          key=lambda x: float('inf')
                          if x[0].user.institutional_id is None
                          else float(x[0].user.institutional_id))

    return render_course_page(pctx, "survey/survey_book.html", {
        "survey_table": survey_table,
        "survey_questions": survey_questions,
        "participations": participations,
        "survey": survey,
        })


class CreateSurveyForm(StyledForm):
    def __init__(self, course, *args, **kwargs):
        # type:(*Any, **Any) -> None
        super(CreateSurveyForm, self).__init__(*args, **kwargs)
        self.course = course

        self.fields['title'] = forms.CharField(
            required=True,
            help_text=_("Title of the survey."),
            label=_("Title")
        )

        self.fields["questionnaire"] = forms.ModelChoiceField(
                queryset=Questionnaire.objects.order_by("pk"),
                required=True,
                help_text=_("Select a questionnare to link "
                            "to this course."),
                label=_("Questionnaire"))

        self.fields['force_create'] = forms.BooleanField(
            required=False,
            initial=False,
            help_text=_("Force recreate a survey if exist "
                        "another survey with the same "
                        "questionnaire?"),
            label=_("Force create")
        )

        self.helper.add_input(Submit("submit", _("Link")))

    def clean(self):
        force_create = self.cleaned_data["force_create"]
        if not force_create:
            qs = CourseSurvey.objects.filter(
                course=self.course,
                questionnaire=self.cleaned_data["questionnaire"]
            )
            if qs.exists():
                titles_list = qs.values_list("title", flat=True)
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    _("There already exists survey(s) "
                      "using the same questionnaire: %s."
                      ) % ", ".join(titles_list)
                )


@login_required
@course_view
def create_survey_with_questionnaire(pctx):
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not create course statistics"))
    request = pctx.request
    if request.method == 'POST':
        form = CreateSurveyForm(pctx.course, request.POST)
        if form.is_valid():
            questionnaire = form.cleaned_data["questionnaire"]
            title = form.cleaned_data["title"]

            CourseSurvey.objects.create(
                title=title,
                course=pctx.course,
                questionnaire=questionnaire
            )
            messages.add_message(
                request, messages.INFO,
                _("The questionnare is successfully linked to the course."))
    else:
        form = CreateSurveyForm(pctx.course)

    return render(request, "generic-form.html", {
        "form_description": _("Link questionnare to course"),
        "form": form
        })


class FillParticipationSurvey(FormView):
    form_class = DisplaySurveyForm
    template_name = 'survey/display.html'

    def __init__(self, **kwargs):
        super(FillParticipationSurvey, self).__init__(**kwargs)
        self.questionnaire_pk = None
        self.survey_pk = None
        self.participation_id = None
        self.course_identifier = None
        self.questionnaire = None

    def get_form_kwargs(self):
        kwargs = super(FillParticipationSurvey, self).get_form_kwargs()
        self.survey_pk = self.kwargs['survey_pk']
        self.survey = get_object_or_404(CourseSurvey, pk=self.survey_pk)
        self.questionnaire_pk = self.survey.questionnaire.pk
        self.participation_id = self.kwargs['participation_id']
        self.participation = Participation.objects.get(id=self.participation_id)
        self.course_identifier = self.kwargs['course_identifier']
        kwargs.update({
            'survey_pk': self.survey_pk,
            'participation_id': self.participation_id
        })

        self.questionnaire = questionnaire = self.survey.questionnaire
        exist_answer = {}
        for index, question in enumerate(questionnaire.questions()):
            try:
                answer = Psqa.objects.get(
                    survey=self.survey,
                    participation__id=self.participation_id,
                    question=question
                )
                exist_answer['question_{0}'.format(question.pk)] = answer.answer
            except Psqa.DoesNotExist:
                pass
        kwargs.update(initial=exist_answer)
        return kwargs

    def form_valid(self, form):
        filler_participations = Participation.objects.filter(
            course=self.participation.course,
            user=self.request.user
        )
        has_perm = False
        for part in filler_participations:
            if part.has_permission(pperm.assign_grade):
                has_perm = True
                break

        if not has_perm:
            raise PermissionDenied("Not allowed to save form")

        form.save(user=self.request.user)
        messages.add_message(self.request, messages.INFO,
                             _("The answer is saved."))
        return super(FillParticipationSurvey, self).form_valid(form=form)

    def get_success_url(self):
        return reverse(
            'survey-finish-page',
            args=(self.course_identifier, self.survey.pk, self.participation_id))

    def get_context_data(self, **kwargs):
        context = super(FillParticipationSurvey, self).get_context_data(**kwargs)
        pctx = CoursePageContext(self.request, self.course_identifier)
        context.update(
            participation=self.participation,
            course=self.participation.course,
            pperm=ParticipationPermissionWrapper(pctx),
            survey=self.survey
        )
        return context


class ThanksView(Tv):
    template_name = "survey/thanks.html"


class SurveyFinishView(TemplateView):
    template_name = "survey/thanks.html"

    def get_context_data(self, **kwargs):
        context = super(SurveyFinishView, self).get_context_data(**kwargs)

        participation_id = self.kwargs['participation_id']
        participation = Participation.objects.get(id=participation_id)
        course_identifier = self.kwargs['course_identifier']

        survey_pk = self.kwargs['survey_pk']
        survey = CourseSurvey.objects.get(pk=survey_pk)

        all_participation_id = list(
            Participation.objects.filter(
                course=participation.course,
                status=participation_status.active)
            .annotate(null_id=Count('user__institutional_id'))
            .order_by("-null_id", "user__institutional_id")
            .select_related("user")
            .values_list("id", flat=True)
        )
        this_participation_id = participation.id
        next_participation_id = None
        prev_participation_id = None
        for i, other_participation_id in enumerate(all_participation_id):
            if other_participation_id == this_participation_id:
                if i > 0:
                    prev_participation_id = all_participation_id[i - 1]
                if i + 1 < len(all_participation_id):
                    next_participation_id = all_participation_id[i + 1]

        context.update(
            course=participation.course,
            participation=participation,
            survey=survey,

            pperm=ParticipationPermissionWrapper(
                CoursePageContext(self.request, course_identifier)),
            this_participation_id=this_participation_id,
            next_participation_id=next_participation_id,
            prev_participation_id=prev_participation_id,
        )

        return context


class SingleSurveyQuestionForm(forms.Form):
    def __init__(self, survey_pk, question_pk, participation_id, *args, **kwargs):
        """
        Get list of questions and generate the form related to each question's type
        :param questionnaire_pk: Id questionnaire
        """
        super(SingleSurveyQuestionForm, self).__init__(*args, **kwargs)
        self.survey_pk = survey_pk
        self.survey = get_object_or_404(CourseSurvey, id=survey_pk)
        self.question = get_object_or_404(Question, id=question_pk)
        self.participation = Participation.objects.get(id=participation_id)
        get_form_field(self, self.question)

    def save(self, user):
        question = self.question
        answer_text = self.cleaned_data['question_{0}'.format(question.pk)]

        exist_answer_text = None

        if answer_text:
            try:
                answer_save = Psqa.objects.get(
                    survey=self.survey,
                    participation=self.participation,
                    question=question
                )
                exist_answer_text = answer_save.answer
            except Psqa.DoesNotExist:
                answer_save = Psqa(
                    user=user,
                    survey=self.survey,
                    participation=self.participation,
                    question=question,
                )

            if answer_text != exist_answer_text:
                answer_save.user = user
                answer_save.answer = answer_text
                answer_save.save()
                return True
            else:
                return False

        return False


class SingleSurveyQuestionView(FormView):
    form_class = SingleSurveyQuestionForm
    template_name = 'survey/display_question.html'

    def __init__(self, **kwargs):
        super(SingleSurveyQuestionView, self).__init__(**kwargs)
        self.survey = None
        self.participation_id = None
        self.course = None
        self.course_identifier = None
        self.survey = None
        self.next_participation_id = None
        self.prev_participation_id = None

    def get_form_kwargs(self):
        kwargs = super(SingleSurveyQuestionView, self).get_form_kwargs()
        self.course_identifier = self.kwargs['course_identifier']
        self.survey_pk = self.kwargs['survey_pk']
        self.participation_id = participation_id = self.kwargs['participation_id']
        question_pk = self.kwargs['question_pk']

        self.survey = get_object_or_404(CourseSurvey, pk=self.survey_pk)
        self.question = Question.objects.get(pk=question_pk)
        self.participation = Participation.objects.get(id=self.participation_id)

        exist_answer = {}
        try:
            answer = Psqa.objects.get(
                survey=self.survey,
                participation__id=participation_id,
                question__pk=question_pk
            )
            exist_answer['question_{0}'.format(question_pk)] = answer.answer
        except Psqa.DoesNotExist:
            pass

        kwargs.update({
            'question_pk': question_pk,
            'survey_pk': self.survey_pk,
            'participation_id': participation_id,

            'initial': exist_answer
        })
        return kwargs

    def get_success_url(self):
        if "next_user_answer" in self.request:
            participation_id = self.next_participation_id
        elif "prev_user_answer" in self.request:
            participation_id = self.prev_participation_id
        else:
            participation_id = self.participation_id
        return reverse('relate-view_single_question', kwargs={
            "course_identifier": self.course_identifier,
            "survey_pk": self.survey_pk,
            "participation_id": participation_id,
            "question_pk": self.question.pk
        })

    def form_valid(self, form):
        filler_participations = Participation.objects.filter(
            course=self.participation.course,
            user=self.request.user
        )
        has_perm = False
        for part in filler_participations:
            if part.has_permission(pperm.assign_grade):
                has_perm = True
                break

        if not has_perm:
            raise PermissionDenied("Not allowed to save form")

        saved = form.save(user=self.request.user)
        if not saved:
            messages.add_message(
                self.request, messages.WARNING,
                _("The answer is not saved because it is not changed."))
        else:
            messages.add_message(self.request, messages.INFO,
                                 _("The answer is saved."))
        return super(SingleSurveyQuestionView, self).form_valid(form=form)

    def get_context_data(self, **kwargs):
        context = super(SingleSurveyQuestionView, self).get_context_data(**kwargs)

        all_participation_id = list(
            Participation.objects.filter(
                course=self.participation.course,
                status=participation_status.active)
            .annotate(null_id=Count('user__institutional_id'))
            .order_by("-null_id", "user__institutional_id")
            .select_related("user")
            .values_list("id", flat=True)
        )
        this_participation_id = self.participation.id
        for i, other_participation_id in enumerate(all_participation_id):
            if other_participation_id == this_participation_id:
                if i > 0:
                    self.prev_participation_id = all_participation_id[i - 1]
                if i + 1 < len(all_participation_id):
                    self.next_participation_id = all_participation_id[i + 1]

        context.update(
            course=self.participation.course,
            participation=self.participation,
            survey=self.survey,
            question=self.question,
            pperm=ParticipationPermissionWrapper(
                CoursePageContext(self.request, self.course_identifier)),
            next_participation_id=self.next_participation_id,
            prev_participation_id=self.prev_participation_id,
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SingleSurveyQuestionView, self).dispatch(*args, **kwargs)
