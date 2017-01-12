from django.contrib import admin
from course_statistics.models import ParticipationSurvey, ParticipationSurveyQuestionAnswer
from questionnaire.models import Question, Questionnaire, Answer, Choice
from questionnaire.admin import QuestionAdmin, QuestionnaireAdmin, AnswerAdmin
# from crowdsourcing.admin import (
#     SurveyAdmin, SurveyAdminForm, submissions_as, SectionInline, QuestionInline
# )

# Register your models here.

class ParticipationSurveyAdmin(admin.ModelAdmin):
    save_as = True
    list_display = (
        "id",
        "__str__",
    )

admin.site.register(ParticipationSurvey, ParticipationSurveyAdmin)
admin.site.register(ParticipationSurveyQuestionAnswer)
#admin.site.unregister(Question)
#admin.site.unregister(Questionnaire)
#admin.site.unregister(Answer)
#admin.site.unregister(Choice)

# admin.site.register(Questionnaire, QuestionnaireAdmin)
# admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice)
# admin.site.register(Answer, AnswerAdmin)

