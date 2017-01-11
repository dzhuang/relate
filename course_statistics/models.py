import six
from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy, string_concat)
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError, ObjectDoesNotExist
# from crowdsourcing.models import Question, Survey

from questionnaire.models import Question, Questionnaire, AnswerQuerySet
from django.conf import settings

from course.models import (
    Course, Participation
)

from jsonfield import JSONField
# Create your models here.

class ParticipationSurvey(models.Model):
    participation = models.ForeignKey(
        Participation,
        verbose_name=_('Participation'), on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(
        Questionnaire,
        related_name="survey",
        verbose_name=_("Survey"),
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Course Statistics Survey")
        verbose_name_plural = _("Course Statistics Surveys")
        ordering = ("participation__course", "questionnaire__title")
        unique_together = (("participation", ),)

    def __unicode__(self):
        return (
                # Translators: For GradingOpportunity
                _("Survey '(%(title)s)' for %(participation)s")
                % {
                    "title": self.questionnaire.title,
                    "participation": self.participation})

    if six.PY3:
        __str__ = __unicode__


class ParticipationSurveyQuestionAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             help_text=_('The user who lastly supplied this answer'),
                             )
    participation = models.ForeignKey(
        Participation,
        verbose_name=_('Participation'), on_delete=models.CASCADE)
    question = models.ForeignKey(Question,
                                 help_text=_('The question that this is an answer to'),
                                 )
    answer = JSONField(verbose_name=_('Answer'),
                       blank=True,
                       help_text=_('The text answer related to the question'),
                       )
    date = models.DateTimeField(default=now, db_index=True,
                         verbose_name=_('Creation time'))

    objects = AnswerQuerySet.as_manager()

    def __unicode__(self):
        return u'Qsaire-%s-Qst-%s-Ans-%s-by-%s' % (
            self.question.questionnaire.title,
            self.question.id,
            self.id,
            self.participation
        )

    if six.PY3:
        __str__ = __unicode__

    class Meta:
        unique_together = ('participation', 'question')


class StatisticStateMachine(object):
    def __init__(self):
        # type: () -> None
        self.question = None

        self.state = None

    def _consume_status(self, qstatus):
        # type: (Question, bool) -> None

        if self.question is None:
            ques = self.question = qstatus.question
            assert ques is not None
        else:
            assert self.question.pk == qstatus.question.pk

        assert self.question is not None

        self.state = qstatus.state

    def consume(self, iterable):
        # type: (Iterable[QuestionPerParticipant], bool) -> StatisticStateMachine

        for qperpar in iterable:
            self._consume_status(qperpar)
        print(self.state)
        return self

    def stringify_state(self):
        if self.state is None:
            return u"- ∅ -"
        elif self.state == question_state_types.unfilled:
            return "_((Unfilled))"
        else:
            return "_((Filled))"

    def stringify_machine_readable_state(self):
        if self.state is None:
            return u"NONE"
        elif self.state == question_state_types.unfilled:
            return u"UNFILLED"
        else:
            return u"FILLED"

    def __str__(self):
        return self.stringify_machine_readable_state()

# }}}

class question_state_types:  # noqa
    filled = "filled"
    unfilled = "unfilled"

QUESTION_STATE_CHOICES = (
        (question_state_types.filled,
         pgettext_lazy("Survey question state", "Filled")),
        (question_state_types.unfilled,
         pgettext_lazy("Survey question state", "Unfilled")),
        )

class QuestionPerParticipant(models.Model):
    """Per 'grading opportunity', each participant may accumulate multiple grades
    that are aggregated according to :attr:`GradingOpportunity.aggregation_strategy`.

    In addition, for each opportunity, grade changes are grouped by their 'attempt'
    identifier, where later grades with the same :attr:`attempt_id` supersede earlier
    ones.
    """
    question = models.ForeignKey(Question,
            verbose_name=_('Statistics Question'), on_delete=models.CASCADE)

    participation = models.ForeignKey(Participation,
            verbose_name=_('Participation'), on_delete=models.CASCADE)

    state = models.CharField(max_length=50,
                             choices=QUESTION_STATE_CHOICES,
                             # Translators: something like 'status'.
            verbose_name=_('State'))

    class Meta:
        verbose_name = _("Survey Question Status")
        verbose_name_plural = _("Survey Question Status")
        ordering = ("question__pk", "participation__user__institutional_id",)

    def __unicode__(self):
        # Translators: information for GradeChange
        return _("%(participation)s %(state)s on %(question)s") % {
            'participation': self.participation,
            'state': self.state,
            'question': self.question.question}

    if six.PY3:
        __str__ = __unicode__

    def clean(self):
        super(QuestionPerParticipant, self).clean()

        if self.question.course != self.participation.course:
            raise ValidationError(_("Participation and question must live "
                    "in the same course"))

    def get_state_desc(self):
        return dict(QUESTION_STATE_CHOICES).get(
                self.state)

# }}}