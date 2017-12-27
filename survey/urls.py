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

from django.conf.urls import url
from course.constants import COURSE_ID_REGEX

from survey.views import (
    view_single_survey_book,
    # view_stat_by_question,
    view_survey_list,
    create_survey_with_questionnaire,
    view_survey_by_question,
    SurveyFinishView,
)

from survey.views import (
    ListQuestionnaireView,
    CreateQuestionnaireView,
    UpdateQuestionnaireView,
    FillParticipationSurvey,
    ThanksView,
    SingleSurveyQuestionView
)


urlpatterns = [
    # generic questionnaire operations

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

    # course survey operations

    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/all-surveys"
        "/$",
        view_survey_list,
        name="relate-survey_list"),

    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey/link/"
        "$",
        create_survey_with_questionnaire,
        name="relate-survey_create"),

    # url(r"^course"
    #     "/" + COURSE_ID_REGEX +
    #     "/survey/"
    #     "$",
    #     create_survey_with_questionnaire,
    #     name="relate-survey_create_generic"),

    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey-book"
        "/survey"
        "/(?P<survey_pk>[0-9_]+)"
        "$",
        view_single_survey_book,
        name="relate-view_survey_by_pk"),

    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey-by-question"
        "/survey"
        "/(?P<survey_pk>[0-9_]+)"
        "/question"
        "/(?P<question_pk>[0-9_]+)"
        "$",
        view_survey_by_question,
        name="relate-view_survey_by_question_pk"),

    # Displays the questionnaire (Participant User)
    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey"
        "/(?P<survey_pk>[0-9_]+)"
        "/participant"
        "/(?P<participation_id>[0-9]+)"
        "/$",
        FillParticipationSurvey.as_view(),
        name='relate-view_single_user_survey'),

    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey"
        "/(?P<survey_pk>[0-9_]+)"
        "/question"
        "/(?P<question_pk>[0-9_]+)"
        "/participant"
        "/(?P<participation_id>[0-9]+)"
        "/$",
        SingleSurveyQuestionView.as_view(),
        name='relate-view_single_question'),

    url(r"^course"
        '/thanks/$',
        ThanksView.as_view(),
        name='thanks-page'),

    url(r"^course"
        "/" + COURSE_ID_REGEX +
        "/survey"
        "/(?P<survey_pk>[0-9_]+)"
        "/participant"
        "/(?P<participation_id>[0-9]+)"
        '/finish/$',
        SurveyFinishView.as_view(),
        name='survey-finish-page')
]
