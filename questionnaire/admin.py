# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import (Questionnaire, Question,
                     Choice, Answer)


class AnswerAdmin(admin.ModelAdmin):
    list_filter = ('user', )

class QuestionAdmin(admin.ModelAdmin):
    list_display = (
            "id",
            "__str__",
            "questionnaire",
            "type",
            "order",
            )

class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = (
            "id",
            "__str__",
            )


admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Answer, AnswerAdmin)
