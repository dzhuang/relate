from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)

from nested_formset import nestedformset_factory

from course_statistics.models import Questionnaire



#
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Fieldset
#
# from course_statistics.models import StatisticsQuestion, QuestionPerParticipant
# from crowdsourcing.models import Survey
#
# class SurveyForm(ModelForm):
#     class Meta:
#         model = Survey
#         fields = ('name', )
#
#     @property
#     def helper(self):
#         helper = FormHelper()
#         helper.form_tag = False # This is crucial.
#
#         helper.layout = Layout(
#             Fieldset('Create new author', 'name'),
#         )
#
#         return helper
#
#
# class StatisticsQuestionFormHelper(FormHelper):
#     def __init__(self, *args, **kwargs):
#         super(StatisticsQuestionFormHelper, self).__init__(*args, **kwargs)
#         self.form_tag = False
#         self.layout = Layout(
#             Fieldset("Add author's book", 'title'),
#         )
#
#
# StatisticsQuestionFormset = inlineformset_factory(
#     Survey,
#     StatisticsQuestion,
#     fields=('title', ),
#     extra=2,
#     can_delete=False,
# )