import six
from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy, string_concat)
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from crowdsourcing.models import Question

from course.models import (
    Course, Participation
)

# Create your models here.

class StatisticsQuestion(Question):
    course = models.ForeignKey(Course,
            verbose_name=_('Course'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Statistics Question")
        verbose_name_plural = _("Statistics Questions")
        ordering = ("course", "fieldname")
        unique_together = (("course", ),)

    def __unicode__(self):
        return (
                # Translators: For GradingOpportunity
                _("%(question_name)s (%(question_id)s) in statistic %(survey_name)s of %(course)s")
                % {
                    "question_name": self.question,
                    "question_id": self.fieldname,
                    "survey_name": repr(self.survey),
                    "course": self.course})

    if six.PY3:
        __str__ = __unicode__


class StatisticStateMachine(object):
    def __init__(self):
        # type: () -> None
        self.question = None

        self.state = None

    def _consume_status(self, qstatus):
        # type: (GradeChange, bool) -> None

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
    question = models.ForeignKey(StatisticsQuestion,
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
        ordering = ("question__fieldname", "participation__user__institutional_id",)

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