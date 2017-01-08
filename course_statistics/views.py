
from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy, ugettext, string_concat)
from django.shortcuts import render

from django.core.exceptions import (
        PermissionDenied, SuspiciousOperation, ObjectDoesNotExist)

from course.utils import (
        course_view, render_course_page,
        get_session_access_rule)
from course.constants import (
        participation_permission as pperm,
        flow_permission
        )
# Create your views here.

@course_view
def view_stat_book(pctx):
    request = pctx.request
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view statistics"))
    return render_course_page(pctx, "course_statistics/statistic_book.html",
                              {})


@course_view
def view_stat_by_question(pctx, question_id):
    request = pctx.request
    if not pctx.has_permission(pperm.view_gradebook):
        raise PermissionDenied(_("may not view statistics"))
    return render_course_page(pctx, "course_statistics/statistic_book.html",
                              {})
