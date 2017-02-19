# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import six
from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy)
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from questionnaire.models import Question, Questionnaire, AnswerQuerySet
from django.conf import settings

from course.models import Course, Participation

from jsonfield import JSONField


class CourseSurvey(models.Model):
    title = models.CharField(max_length=100,
                             blank=False,
                             null=False,
                             verbose_name=_('Survey Title'))
    course = models.ForeignKey(
        Course,
        verbose_name=_('Course'), on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(
        Questionnaire,
        related_name="questionnaire",
        verbose_name=_("Questionnaire"),
        on_delete=models.CASCADE)
    creation_time = models.DateTimeField(default=now, db_index=True,
                         verbose_name=_('Creation time'))

    class Meta:
        verbose_name = _("Course Statistics Survey")
        verbose_name_plural = _("Course Statistics Surveys")
        ordering = ("course", "questionnaire__title")

    def __unicode__(self):
        return (
            _("Survey '(%(title)s)' for %(course)s using "
              "%(questionnare_title)s created at %(time)s")
            % {
                "title": self.title,
                "questionnare_title": self.questionnaire.title,
                "course": self.course,
                "time": self.creation_time
            }
        )

    if six.PY3:
        __str__ = __unicode__


class question_answered_state_types:  # noqa
    filled = "filled"
    unfilled = "unfilled"


QUESTION_ANSWERED_STATE_CHOICES = (
        (question_answered_state_types.filled,
         pgettext_lazy("Survey question state", "Filled")),
        (question_answered_state_types.unfilled,
         pgettext_lazy("Survey question state", "Unfilled")),
        )


class ParticipationSurveyQuestionAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             help_text=_('The user who lastly supplied this answer'),
                             on_delete=models.CASCADE
                             )
    survey = models.ForeignKey(CourseSurvey,
                               help_text=_('The survey'),
                               null=True,
                               on_delete=models.CASCADE
                               )
    participation = models.ForeignKey(
        Participation,
        verbose_name=_('Participation'), on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question,
        help_text=_('The question that this is an answer to'),
        on_delete=models.CASCADE)
    answer = JSONField(
        verbose_name=_('Answer'),
        blank=True,
        help_text=_('The text answer related to the question'),)
    date = models.DateTimeField(default=now, db_index=True,
                         verbose_name=_('Creation time'))

    state = models.CharField(max_length=50,
                             choices=QUESTION_ANSWERED_STATE_CHOICES,
                             default=question_answered_state_types.unfilled,
                             # Translators: something like 'status'.
            verbose_name=_('State'))

    objects = AnswerQuerySet.as_manager()

    def __unicode__(self):
        return u'Qsaire-%s-Qst-%s-Ans-%s-by-%s-Survey-%s' % (
            self.question.questionnaire.title,
            self.question.id,
            self.id,
            self.participation,
            self.survey
        )

    if six.PY3:
        __str__ = __unicode__

    class Meta:
        unique_together = ('survey', 'participation', 'question')

    def clean(self):
        super(ParticipationSurveyQuestionAnswer, self).clean()

        qs = CourseSurvey.objects.filter(
            participation=self.participation
        )

        if self.question.questionnaire not in qs:
            raise ValidationError(_("Participation and answered "
                                    "question must live in the "
                                    "same course"))

    def get_state_desc(self):
        return dict(QUESTION_ANSWERED_STATE_CHOICES).get(
                self.state)

    def get_answer_str(self):
        if self.answer is None:
            return None
        if self.question.type not in ['yesNoQuestion',
                                      'MultiChoices',
                                      'MultiChoiceWithAnswer']:
            return self.answer
        if self.question.type == 'yesNoQuestion':
            choices_yes_no = (("yes", _("Yes")),
                              ("no", _("No")),)
            return dict(choices_yes_no).get(self.answer)
        else:
            choices_text = self.question.choices()\
                .order_by("pk").values_list('text', flat=True)
            choices = ((0, "----"),
                       (1, u"完全正确"),
                       (2, u"未回答(基本未回答)"),
                       (3, u"未掌握原理")) \
                      + tuple((i + 4, text)
                              for i, text in enumerate(choices_text))
            if isinstance(self.answer, list):
                return "; ".join([dict(choices).get(int(a)) for a in self.answer])
            else:
                return dict(choices).get(int(self.answer))

    def save(self, *args, **kwargs):
        if self.survey is None:  # Set default reference
            self.survey = ParticipationSurveyQuestionAnswer.objects.get(id=1)
        if self.get_answer_str() in ["--", "---", "----"]:
            self.state = question_answered_state_types.unfilled
        else:
            self.state = question_answered_state_types.filled
        super(ParticipationSurveyQuestionAnswer, self).save(*args, **kwargs)


class QuestionAnsweredStateMachine(object):
    def __init__(self):
        # type: () -> None
        self.question = None
        self.answer = None
        self.state = None

    def _consume_status(self, answer_for_ques):
        # type: (ParticipationSurveyQuestionAnswer, bool) -> None
        if answer_for_ques is None:
            self.state = question_answered_state_types.unfilled
        elif answer_for_ques.state == question_answered_state_types.unfilled:
            self.state = question_answered_state_types.unfilled
        else:
            self.answer = answer_for_ques
            self.question = self.answer.question
            self.state = question_answered_state_types.filled

    def consume(self, iterable):
        for answer_for_quest in iterable:
            self._consume_status(answer_for_quest)
        return self

    def stringify_state(self):
        if self.state is None:
            return u"- ∅ -"
        elif self.state == question_answered_state_types.unfilled:
            return u"- ∅ -"
        else:
            return self.answer.get_answer_str()

    def stringify_machine_readable_state(self):
        if self.state is None:
            return u"NONE"
        elif self.state == question_answered_state_types.unfilled:
            return u"UNFILLED"
        else:
            return u"FILLED"

    def __str__(self):
        return self.stringify_machine_readable_state()

# }}}
