# -*- coding: utf-8 -*-

import copy
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from .models import (Questionnaire, Question, Choice, Answer)


class AnswerAdmin(admin.ModelAdmin):
    list_filter = ('user', )


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ('questionnaire',)
    list_display = (
            "id",
            "text",
            "__str__",
            "questionnaire",
            "type",
            "order",
            )


def duplicate_questionnaire(modeladmin, request, queryset):

    if queryset.count() > 1:
        messages.add_message(
            request, messages.ERROR,
            _("Only one questionnaire is allowed to be copied per request"))
        return

    questionnare = queryset[0]

    q_copy = copy.copy(questionnare)
    q_copy.id = None
    q_copy.save()
    for question in questionnare.questions():
        question_copy = copy.copy(question)
        question_copy.id = None
        question_copy.questionnaire = q_copy
        question_copy.save()

        choice_set = Choice.objects.filter(question=question).order_by("pk")
        for choice in choice_set:
            choice_copy = copy.copy(choice)
            choice_copy.id = None
            choice_copy.question = question_copy
            choice_copy.save()

duplicate_questionnaire.shoort_description = _("Make a copy of this questionnaire")


class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = (
            "id",
            "__str__",
            )
    actions = [duplicate_questionnaire]
    list_filter = ("questionnaire", "questionnaire__course")


admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Answer, AnswerAdmin)
