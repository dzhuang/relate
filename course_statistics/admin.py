from django.contrib import admin
from course_statistics.models import Question, StatisticsQuestion

# Register your models here.


class StatisticsQuestionAdmin(admin.ModelAdmin):
    list_filter = (
        "survey",
    )

    list_display = (
        'id',
    )
    list_display_links = ('id',)

    save_on_top = True

admin.site.register(StatisticsQuestion, StatisticsQuestionAdmin)