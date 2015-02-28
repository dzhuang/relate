# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2014 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
    url(r"^login/$",
        "course.auth.sign_in_by_user_pw"),
    url(r"^login/sign-up/$",
        "course.auth.sign_up"),
    url(r"^login/reset-password/$",
        "course.auth.reset_password"),
    url(r"^login/reset-password/stage-2"
        "/(?P<user_id>[0-9]+)"
        "/(?P<sign_in_key>[a-zA-Z0-9]+)",
        "course.auth.reset_password_stage2"),
    url(r"^login/by-email/$",
        "course.auth.sign_in_by_email"),
    url(r"^login/token"
        "/(?P<user_id>[0-9]+)"
        "/(?P<sign_in_key>[a-zA-Z0-9]+)"
        "/$",
        "course.auth.sign_in_stage2_with_token"),
    url(r"^logout/$",
        "django.contrib.auth.views.logout",
        {"next_page": "course.views.home"}),
    url(r"^profile/$",
        "course.auth.user_profile",
        ),

    # {{{ troubleshooting

    url(r'^user/impersonate/$', 'course.auth.impersonate'),
    url(r'^user/stop_impersonating/$', 'course.auth.stop_impersonating'),

    url(r'^time/set-fake-time/$', 'course.views.set_fake_time'),

    # }}}

    # {{{ course

    url(r'^$', 'course.views.home', name='home'),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/$",
        "course.views.course_page",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/instant-message/$",
        "course.im.send_instant_message",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/sandbox/markup/$",
        "course.sandbox.view_markup_sandbox",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/sandbox/page/$",
        "course.sandbox.view_page_sandbox",),

    # }}}

    # {{{ grading

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/my/$",
        "course.grades.view_participant_grades",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/participant"
        "/(?P<participation_id>[0-9]+)"
        "/$",
        "course.grades.view_participant_grades",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/participants/$",
        "course.grades.view_participant_list",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/opportunities/$",
        "course.grades.view_grading_opportunity_list",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/overview/$",
        "course.grades.view_gradebook",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/overview/csv/$",
        "course.grades.export_gradebook_csv",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/by-opportunity"
        "/(?P<opp_id>[0-9]+)"
        "/$",
        "course.grades.view_grades_by_opportunity",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/single-grade"
        "/(?P<participation_id>[0-9]+)"
        "/(?P<opportunity_id>[0-9]+)"
        "/$",
        "course.grades.view_single_grade",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading"
        "/csv-import"
        "/$",
        "course.grades.import_grades",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading"
        "/flow-page"
        "/(?P<flow_session_id>[0-9]+)"
        "/(?P<page_ordinal>[0-9]+)"
        "/$",
        "course.grading.grade_flow_page",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grading/statistics"
        "/(?P<flow_id>[-a-zA-Z0-9]+)"
        "/$",
        "course.grading.show_grading_statistics",),
    # }}}

    # {{{ enrollment

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/enroll/$",
        "course.enrollment.enroll",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/preapprove"
        "/$",
        "course.enrollment.create_preapprovals",),

    # }}}

    # {{{ media

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/media/(?P<commit_sha>[a-f0-9]+)"
        "/(?P<media_path>.*)$",
        "course.views.get_media",),

    # }}}

    # {{{ calendar

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/check-events/$",
        "course.calendar.check_events",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/create-recurring-events/$",
        "course.calendar.create_recurring_events",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/renumber-events/$",
        "course.calendar.renumber_events",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/calendar/$",
        "course.calendar.view_calendar",),

    # }}}

    # {{{ versioning

    url(r"^new-course/$",
        "course.versioning.set_up_new_course"),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/update/$",
        "course.versioning.update_course",),

    # }}}

    # {{{ flow-related

    url(r"^course"
         "/(?P<course_identifier>[-a-zA-Z0-9]+)"
         "/flow"
         "/(?P<flow_identifier>[-_a-zA-Z0-9]+)"
         "/start"
         "/$",
         "course.flow.view_start_flow",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/flow-session"
        "/(?P<flow_session_id>[0-9]+)"
        "/(?P<ordinal>[0-9]+)"
        "/$",
        "course.flow.view_flow_page",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/flow-session"
        "/(?P<flow_session_id>[-0-9]+)"
        "/update-expiration-mode"
        "/$",
        "course.flow.update_expiration_mode",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/flow-session"
        "/(?P<flow_session_id>[0-9]+)"
        "/finish"
        "/$",
        "course.flow.finish_flow_session_view",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/test-flow"
        "/$",
        "course.views.test_flow",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/instant-flow"
        "/$",
        "course.views.manage_instant_flow_requests",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/regrade-not-for-credit-flows"
        "/$",
        "course.flow.regrade_not_for_credit_flows_view",),

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grant-exception"
        "/$",
        "course.views.grant_exception",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grant-exception"
        "/(?P<participation_id>[0-9]+)"
        "/(?P<flow_id>[-a-zA-Z0-9]+)"
        "/$",
        "course.views.grant_exception_stage_2",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/grant-exception"
        "/(?P<participation_id>[0-9]+)"
        "/(?P<flow_id>[-a-zA-Z0-9]+)"
        "/(?P<session_id>[0-9]+)"
        "/$",
        "course.views.grant_exception_stage_3",),

    # }}}

    # {{{ analytics

    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/flow-analytics"
        "/$",
        "course.analytics.flow_list",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/flow-analytics"
        "/(?P<flow_identifier>[-_a-zA-Z0-9]+)"
        "/$",
        "course.analytics.flow_analytics",),
    url(r"^course"
        "/(?P<course_identifier>[-a-zA-Z0-9]+)"
        "/flow-analytics"
        "/(?P<flow_identifier>[-_a-zA-Z0-9]+)"
        "/page"
        "/(?P<group_id>[-_a-zA-Z0-9]+)"
        "/(?P<page_id>[-_a-zA-Z0-9]+)"
        "/$",
        "course.analytics.page_analytics",),

    # }}}

    url(r'^admin/', include(admin.site.urls)),
)

if settings.RELATE_MAINTENANCE_MODE:
    urlpatterns = patterns('',
        # course
        url(r'^.*$', 'course.views.maintenance'),
    )

# vim: fdm=marker
