from django.contrib import admin
from course_statistics.models import Question, ParticipationSurvey
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