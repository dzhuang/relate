from django.shortcuts import render

from course.utils import course_view
# Create your views here.

@course_view
def view_stat_book(pctx):
    pass

@course_view
def view_stat_by_question(pctx, question_id):
    pass