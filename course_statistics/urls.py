# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2016 Dong Zhuang"

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

from django.conf.urls import url, include
from django.views.i18n import javascript_catalog

from course.constants import COURSE_ID_REGEX

from course_statistics.views import (
    view_single_survey_book,
    # view_stat_by_question,
    view_survey_list,
    link_survey_with_course,
)

from course_statistics.views import (
    ListQuestionnaireView,
    CreateQuestionnaireView,
    UpdateQuestionnaireView,
    FillParticipationSurvey,
    ThanksView
)


js_info_dict_image_upload = {
    'packages': ('image_upload',),
}

urlpatterns = [
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/all-surveys"
        "/$",
        view_survey_list,
        name="relate-survey_list"),
#relate-survey_create
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey/"
        "$",
        link_survey_with_course,
        name="relate-survey_create"),
#relate-survey_create_generic
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey/"
        "$",
        link_survey_with_course,
        name="relate-survey_create_generic"),
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey-book/"
        "/(?P<survey_pk>[0-9_]+)"
        "$",
        view_single_survey_book,
        name="relate-view_survey_by_pk"),
    # url(r"^course"
    #     "/" + COURSE_ID_REGEX +
    #     "/statistics/stat-by-ques"
    #     "/(?P<question_id>[a-zA-Z0-9_]+)"
    #     "/$",
    #     view_stat_by_question,
    #     name="relate-view_course_statistics_by_question"),
    # url(r'^crowdsourcing/', include(crowdsourcing.urls)),
    # url('^statistics/(?P<pk>\d+)/$', SurveyUpdateView.as_view(),
    #     name='stat'),

    # url(r"^course"
    #     "/" + COURSE_ID_REGEX +
    #     "/survey/stat-by-ques"
    #     "/(?P<question_id>[a-zA-Z0-9_]+)"
    #     "/$",
    #     view_stat_by_question,
    #     name="relate-view_course_statistics_by_question"),
#"relate-view_participant_statistics" course.identifier participation.id statistics.id
    # url(r"^course"
    #     "/" + COURSE_ID_REGEX +
    #     "/survey/participant"
    #     "/(?P<participation_id>[0-9]+)"
    #     "/(?P<survey_id>[a-zA-Z0-9_]+)"
    #     "/$",
    #     view_stat_by_question,
    #     name="relate-view_participant_statistics"),

    # url(r'^create-questionnaire/$', CreateQuestionnaireView.as_view(),
    #     name='add-questionnaire'),

    url(r'^questionnaire/$',
        ListQuestionnaireView.as_view(),
        name='list-questionnaire'),

    url(r'^create-questionnaire/$', CreateQuestionnaireView.as_view(),
        name='add-questionnaire'),

    url(r'create-questionnaire/(?P<pk>\d+)/$',
        UpdateQuestionnaireView.as_view(),
        name='update-questionnaire'),

    url(r'^$',
        ListQuestionnaireView.as_view(),
        name='list-questionnaire'),

    # Creation of questionnaire (Back-end user)
    url(r'^create-questionnaire/$', CreateQuestionnaireView.as_view(),
        name='add-questionnaire'),

    # Updates and displays the questionnaire (Back-end User)
    url(r'create-questionnaire/(?P<pk>\d+)/$',
        UpdateQuestionnaireView.as_view(),
        name='update-questionnaire'),

    # Displays the statistics of questionnaire (Back-end User)

    # Displays the questionnaire (Participant User)
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey/participant"
        "/(?P<participation_id>[0-9]+)"
        "/(?P<pk>[0-9_]+)"
        "/$",
        FillParticipationSurvey.as_view(),
        name='relate-show_questionnaire'),

    # # Displays single question
    # url(r'^question/(?P<pk>[0-9]+)/$',
    #     SingleQuestionView.as_view(),
    #     name='show-question'),

    # Thanks Message and sharing of the link of questionnaire
    #  (Both Back-end and Participant )
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        '/thanks/$',
        ThanksView.as_view(),
        name='thanks-page')

    #url(r'^questionnaires/', include('questionnaire.urls'))
]
