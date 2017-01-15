# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

from django.contrib import admin
from survey.models import CourseSurvey, ParticipationSurveyQuestionAnswer
from questionnaire.models import Question, Questionnaire, Answer, Choice
from questionnaire.admin import QuestionAdmin, AnswerAdmin
# from crowdsourcing.admin import (
#     SurveyAdmin, SurveyAdminForm, submissions_as, SectionInline, QuestionInline
# )

from copy import deepcopy

# Register your models here.

class ParticipationSurveyAdmin(admin.ModelAdmin):
    save_as = True
    list_display = (
        "id",
        "__str__",
    )

admin.site.register(CourseSurvey, ParticipationSurveyAdmin)
admin.site.register(ParticipationSurveyQuestionAnswer)
#admin.site.unregister(Question)
#admin.site.unregister(Questionnaire)
#admin.site.unregister(Answer)
#admin.site.unregister(Choice)

# admin.site.register(Questionnaire, QuestionnaireAdmin)
# admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice)
# admin.site.register(Answer, AnswerAdmin)



def duplicate(questionnaire_id):
    questionnare = Questionnaire.objects.get(id=questionnaire_id)

    q_copy = deepcopy(questionnare)
    q_copy.id = None
    q_copy.save()
    for question in questionnare.questions():
        question_copy = deepcopy(question)
        question_copy.id = None
        question_copy.questionnaire = q_copy
        question_copy.save()

        choice_set = Choice.objects.filter(question=question).order_by("pk")
        for choice in choice_set:
            choice_copy = deepcopy(choice)
            choice_copy.id = None
            choice_copy.question = question_copy
            choice_copy.save()
