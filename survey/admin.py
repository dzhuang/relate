# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

from django.contrib import admin
from survey.models import CourseSurvey, ParticipationSurveyQuestionAnswer
from questionnaire.models import Questionnaire, Choice
from copy import deepcopy


class ParticipationSurveyAdmin(admin.ModelAdmin):
    list_filter = ('course',)
    save_as = True
    list_display = (
        "id",
        "__str__",
    )


admin.site.register(CourseSurvey, ParticipationSurveyAdmin)
admin.site.register(ParticipationSurveyQuestionAnswer)
