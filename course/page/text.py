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


from django.utils.translation import (
        ugettext_lazy as _, ugettext, string_concat)
from course.validation import validate_struct, ValidationError
import django.forms as forms

from relate.utils import StyledForm, Struct, StyledInlineForm
from course.page.base import (
        AnswerFeedback, PageBaseWithTitle, PageBaseWithValue, markup_to_html,
        PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer,

        get_editor_interaction_mode)

import re
import sys


class TextAnswerForm(StyledForm):
    @staticmethod
    def get_text_widget(widget_type, read_only=False, check_only=False,
            interaction_mode=None):
        """Returns None if no widget found."""

        if widget_type in [None, "text_input"]:
            if check_only:
                return True

            widget = forms.TextInput()
            widget.attrs["autofocus"] = None
            if read_only:
                widget.attrs["readonly"] = None
            return widget, None

        elif widget_type == "textarea":
            if check_only:
                return True

            widget = forms.Textarea()
            # widget.attrs["autofocus"] = None
            if read_only:
                widget.attrs["readonly"] = None
            return widget, None

        elif widget_type in ["editor:markdown", "editor:yaml"]:
            if check_only:
                return True

            from course.utils import get_codemirror_widget
            cm_widget, cm_help_text = get_codemirror_widget(
                    language_mode=widget_type[widget_type.find(":")+1:],
                    interaction_mode=interaction_mode,
                    read_only=read_only)

            return cm_widget, cm_help_text

        else:
            return None, None

    def __init__(self, read_only, interaction_mode, validators, *args, **kwargs):
        widget_type = kwargs.pop("widget_type", "text_input")

        super(TextAnswerForm, self).__init__(*args, **kwargs)
        widget, help_text = self.get_text_widget(
                    widget_type, read_only,
                    interaction_mode=interaction_mode)
        self.validators = validators
        self.fields["answer"] = forms.CharField(
                required=True,
                widget=widget,
                help_text=help_text,
                label=_("Answer"))

    def clean(self):
        cleaned_data = super(TextAnswerForm, self).clean()
        
        answer = cleaned_data.get("answer", "")
        for validator in self.validators:
            validator.validate(answer)


# {{{ validators

class RELATEPageValidator(object):
    type = "relate_page"

    def __init__(self, vctx, location, validator_desc):
        self.validator_desc = validator_desc

        validate_struct(
                vctx,
                location,
                validator_desc,
                required_attrs=(
                    ("type", str),
                    ),
                allowed_attrs=(
                    ("page_type", str),
                    ),
                )

    def validate(self, new_page_source):
        from relate.utils import dict_to_struct
        import yaml

        try:
            page_desc = dict_to_struct(yaml.load(new_page_source))

            from course.validation import validate_flow_page, ValidationContext
            vctx = ValidationContext(
                    # FIXME
                    repo=None,
                    commit_sha=None)

            validate_flow_page(vctx, "submitted page", page_desc)

            if page_desc.type != self.validator_desc.page_type:
                raise ValidationError(ugettext("page must be of type '%s'")
                        % self.validator_desc.page_type)

        except:
            import sys
            tp, e, _ = sys.exc_info()

            raise forms.ValidationError("%(err_type)s: %(err_str)s"
                    % {"err_type": tp.__name__, "err_str": str(e)})


TEXT_ANSWER_VALIDATOR_CLASSES = [
        RELATEPageValidator,
        ]


def get_validator_class(location, validator_type):
    for validator_class in TEXT_ANSWER_VALIDATOR_CLASSES:
        if validator_class.type == validator_type:
            return validator_class

    raise ValidationError(
            string_concat(
                "%(location)s: ",
                _("unknown validator type"),
                "'%(type)s'")
            % {'location': location, 'type': validator_type})


def parse_validator(vctx, location, validator_desc):
    if not isinstance(validator_desc, Struct):
        raise ValidationError(
                string_concat(
                    "%s: ",
                    _("must be struct or string"))
                % location)

    if not hasattr(validator_desc, "type"):
        raise ValidationError(
                string_concat(
                    "%s: ",
                    "matcher must supply 'type'")
                % location)

    return (get_validator_class(location, validator_desc.type)
        (vctx, location, validator_desc))

# }}}


# {{{ matchers

class TextAnswerMatcher(object):
    """Abstract interface for matching text answers.

    .. attribute:: type
    .. attribute:: is_case_sensitive
    .. attribute:: pattern_type

        "struct" or "string"
    """

    def __init__(self, vctx, location, pattern):
        pass

    def validate(self, s):
        """Called to validate form input against simple input mistakes.

        Should raise :exc:`django.forms.ValidationError` on error.
        """

        pass

    def grade(self, s):
        raise NotImplementedError()

    def correct_answer_text(self):
        """May return *None* if not known."""
        raise NotImplementedError()


class CaseSensitivePlainMatcher(TextAnswerMatcher):
    type = "case_sens_plain"
    is_case_sensitive = True
    pattern_type = "string"

    def __init__(self, vctx, location, pattern):
        self.pattern = pattern

    def grade(self, s):
        return int(self.pattern == s)

    def correct_answer_text(self):
        return self.pattern


class PlainMatcher(CaseSensitivePlainMatcher):
    type = "plain"
    is_case_sensitive = False
    pattern_type = "string"

    def grade(self, s):
        return int(self.pattern.lower() == s.lower())


class RegexMatcher(TextAnswerMatcher):
    type = "regex"
    re_flags = re.I
    is_case_sensitive = False
    pattern_type = "string"

    def __init__(self, vctx, location, pattern):
        try:
            self.pattern = re.compile(pattern, self.re_flags)
        except:
            tp, e, _ = sys.exc_info()

            raise ValidationError(
                    string_concat(
                        "%(location)s: ",
                        _("regex '%(pattern)s' did not compile"),
                        ": %(err_type)s: %(err_str)s")
                    % {
                        "location": location,
                        "pattern": pattern,
                        "err_type": tp.__name__,
                        "err_str": str(e)})

    def grade(self, s):
        match = self.pattern.match(s)
        if match is not None:
            return 1
        else:
            return 0

    def correct_answer_text(self):
        return None


class CaseSensitiveRegexMatcher(RegexMatcher):
    type = "case_sens_regex"
    re_flags = 0
    is_case_sensitive = True
    pattern_type = "string"


def parse_sympy(s):
    if isinstance(s, unicode):
        # Sympy is not spectacularly happy with unicode function names
        s = s.encode()

    from pymbolic import parse
    from pymbolic.sympy_interface import PymbolicToSympyMapper

    # use pymbolic because it has a semi-secure parser
    return PymbolicToSympyMapper()(parse(s))


class SymbolicExpressionMatcher(TextAnswerMatcher):
    type = "sym_expr"
    is_case_sensitive = True
    pattern_type = "string"

    def __init__(self, vctx, location, pattern):
        self.pattern = pattern

        try:
            self.pattern_sym = parse_sympy(pattern)
        except ImportError:
            tp, e, _ = sys.exc_info()
            if vctx is not None:
                vctx.add_warning(
                        location,
                        string_concat(
                            "%(location)s: ",
                            _("unable to check symbolic expression"),
                            "(%(err_type)s: %(err_str)s)")
                        % {
                            'location': location,
                            "err_type": tp.__name__,
                            "err_str": str(e)
                            })

        except:
            tp, e, _ = sys.exc_info()
            raise ValidationError(
                    "%(location)s: %(err_type)s: %(err_str)s"
                    % {
                        "location": location,
                        "err_type": tp.__name__,
                        "err_str": str(e)
                        })

    def validate(self, s):
        try:
            parse_sympy(s)
        except:
            tp, e, _ = sys.exc_info()
            raise forms.ValidationError("%(err_type)s: %(err_str)s"
                    % {"err_type": tp.__name__, "err_str": str(e)})

    def grade(self, s):
        from sympy import simplify
        answer_sym = parse_sympy(s)

        try:
            simp_result = simplify(answer_sym - self.pattern_sym)
        except Exception:
            return 0

        if simp_result == 0:
            return 1
        else:
            return 0

    def correct_answer_text(self):
        return self.pattern


class FloatMatcher(TextAnswerMatcher):
    type = "float"
    is_case_sensitive = False
    pattern_type = "struct"
    
    import math

    def __init__(self, vctx, location, matcher_desc):
        self.matcher_desc = matcher_desc

        validate_struct(
                vctx,
                location,
                matcher_desc,
                required_attrs=(
                    ("type", str),
                    ("value", (int, float, str)),
                    ),
                allowed_attrs=(
                    ("rtol", (int, float, str)),
                    ("atol", (int, float, str)),
                    ),
                )
        
        def validate_attr(attr):
            
            attr_value=self.matcher_desc.__getattribute__(attr)
            
            try:
                eval(attr_value)
            except:
                raise ValidationError(
                        string_concat(
                            "%(location)s: ",
                            _("attribute '%(attr)s' "
                              "should be an instances "
                              "of 'int', 'float' "
                              "or a caculable string"))
                        % {
                            'location': location,
                            'attr': attr})
        
        validate_attr("value")
        
        if hasattr(self.matcher_desc, "atol"):
            validate_attr("atol")
            
        if hasattr(self.matcher_desc, "rtol"):
            validate_attr("rtol")
            

    def validate(self, s):
        
        try:
            float(eval(s))
        except:
            tp, e, _ = sys.exc_info()
            raise forms.ValidationError("%(err_type)s: %(err_str)s"
                    % {"err_type": tp.__name__, "err_str": str(e)})

    def grade(self, s):
        answer_float = float(eval(s))
        
        default_atol = 0.01
        default_rtol = 0.01

        if hasattr(self.matcher_desc, "atol"):
            if (abs(answer_float - eval(self.matcher_desc.value))
                    >= eval(self.matcher_desc.atol)):
                return 0
            
        if hasattr(self.matcher_desc, "rtol"):
            if (abs(answer_float - eval(self.matcher_desc.value))
                    / abs(eval(self.matcher_desc.value))
                    >= eval(self.matcher_desc.rtol)):
                return 0

        return 1

    def correct_answer_text(self):
        return str(self.matcher_desc.value)


TEXT_ANSWER_MATCHER_CLASSES = [
        CaseSensitivePlainMatcher,
        PlainMatcher,
        RegexMatcher,
        CaseSensitiveRegexMatcher,
        SymbolicExpressionMatcher,
        FloatMatcher,
        ]


MATCHER_RE = re.compile(r"^\<([a-zA-Z0-9_:.]+)\>(.*)$")
MATCHER_RE_2 = re.compile(r"^([a-zA-Z0-9_.]+):(.*)$")


def get_matcher_class(location, matcher_type, pattern_type):
    for matcher_class in TEXT_ANSWER_MATCHER_CLASSES:
        if matcher_class.type == matcher_type:

            if matcher_class.pattern_type != pattern_type:
                raise ValidationError(
                    string_concat(
                        "%(location)s: ",
                        # Translators: a "matcher" is used to determine
                        # if the answer to text question (blank filling
                        # question) is correct.
                        _("%(matcherclassname)s only accepts "
                            "'%(matchertype)s' patterns"))
                        % {
                            'location': location,
                            'matcherclassname': matcher_class.__name__,
                            'matchertype': pattern_type})

            return matcher_class

    raise ValidationError(
            string_concat(
                "%(location)s: ",
                _("unknown match type '%(matchertype)s'"))
            % {
                'location': location,
                'matchertype': matcher_type})


def parse_matcher_string(vctx, location, matcher_desc):
    match = MATCHER_RE.match(matcher_desc)

    if match is not None:
        matcher_type = match.group(1)
        pattern = match.group(2)
    else:
        match = MATCHER_RE_2.match(matcher_desc)

        if match is None:
            raise ValidationError(
                    string_concat(
                        "%s: ",
                        _("does not specify match type"))
                    % location)

        matcher_type = match.group(1)
        pattern = match.group(2)

        if vctx is not None:
            vctx.add_warning(location,
                    _("uses deprecated 'matcher:answer' style"))

    return (get_matcher_class(location, matcher_type, "string")
            (vctx, location, pattern))


def parse_matcher(vctx, location, matcher_desc):
    if isinstance(matcher_desc, (str, unicode)):
        return parse_matcher_string(vctx, location, matcher_desc)
    else:
        if not isinstance(matcher_desc, Struct):
            raise ValidationError(
                    string_concat(
                        "%s: ",
                        _("must be struct or string"))
                    % location)

        if not hasattr(matcher_desc, "type"):
            raise ValidationError(
                    string_concat(
                        "%s: ",
                        _("matcher must supply 'type'"))
                    % location)

        return (get_matcher_class(location, matcher_desc.type, "struct")
            (vctx, location, matcher_desc))

# }}}


# {{{ text question base

class TextQuestionBase(PageBaseWithTitle):
    """
    A page asking for a textual answer

    .. attribute:: id

        |id-page-attr|

    .. attribute:: type

        ``TextQuestion``

    .. attribute:: access_rules

        |access-rules-page-attr|

    .. attribute:: title

        |title-page-attr|

    .. attribute:: prompt

        The page's prompt, written in :ref:`markup`.

    .. attribute:: widget

        |text-widget-page-attr|

    """
    def __init__(self, vctx, location, page_desc):
        super(TextQuestionBase, self).__init__(vctx, location, page_desc)

        widget = TextAnswerForm.get_text_widget(
                getattr(page_desc, "widget", None),
                check_only=True)

        if widget is None:
            raise ValidationError(
                    string_concat(
                        "%(location)s: ",
                        _("unrecognized widget type"),
                        "'%(type)s'")
                    % {
                        'location': location,
                        'type': getattr(page_desc, "widget")})

    def required_attrs(self):
        return super(TextQuestionBase, self).required_attrs() + (
                ("prompt", "markup"),
                )

    def allowed_attrs(self):
        return super(TextQuestionBase, self).allowed_attrs() + (
                ("widget", str),
                )

    def markup_body_for_title(self):
        return self.page_desc.prompt

    def body(self, page_context, page_data):
        return markup_to_html(page_context, self.page_desc.prompt)

    def make_form(self, page_context, page_data,
            answer_data, answer_is_final):
        read_only = answer_is_final

        if answer_data is not None:
            answer = {"answer": answer_data["answer"]}
            form = TextAnswerForm(
                    read_only,
                    get_editor_interaction_mode(page_context),
                    self.get_validators(), answer,
                    widget_type=getattr(self.page_desc, "widget", None))
        else:
            answer = None
            form = TextAnswerForm(
                    read_only,
                    get_editor_interaction_mode(page_context),
                    self.get_validators(),
                    widget_type=getattr(self.page_desc, "widget", None))

        return form

    def post_form(self, page_context, page_data, post_data, files_data):
        read_only = False
        return TextAnswerForm(
                read_only,
                get_editor_interaction_mode(page_context),
                self.get_validators(), post_data, files_data,
                widget_type=getattr(self.page_desc, "widget", None))

    def answer_data(self, page_context, page_data, form, files_data):
        return {"answer": form.cleaned_data["answer"].strip()}

    def is_case_sensitive(self):
        return True

    def normalized_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None

        normalized_answer = answer_data["answer"]

        if not self.is_case_sensitive():
            normalized_answer = normalized_answer.lower()

        from django.utils.html import escape
        return escape(normalized_answer)

# }}}


# {{{ survey text question

class SurveyTextQuestion(TextQuestionBase):
    """
    A page asking for a textual answer, without any notion of 'correctness'

    .. attribute:: id

        |id-page-attr|

    .. attribute:: type

        ``TextQuestion``

    .. attribute:: access_rules

        |access-rules-page-attr|

    .. attribute:: title

        |title-page-attr|

    .. attribute:: prompt

        The page's prompt, written in :ref:`markup`.

    .. attribute:: widget

        |text-widget-page-attr|

    .. attribute:: answer_comment

        A comment that is shown in the same situations a 'correct answer' would
        be.
    """

    def get_validators(self):
        return []

    def allowed_attrs(self):
        return super(SurveyTextQuestion, self).allowed_attrs() + (
                ("answer_comment", "markup"),
                )

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        if hasattr(self.page_desc, "answer_comment"):
            return markup_to_html(page_context, self.page_desc.answer_comment)
        else:
            return None

    def expects_answer(self):
        return True

    def is_answer_gradable(self):
        return False

# }}}


# {{{ text question

class TextQuestion(TextQuestionBase, PageBaseWithValue):
    """
    A page asking for a textual answer

    .. attribute:: id

        |id-page-attr|

    .. attribute:: type

        ``TextQuestion``

    .. attribute:: access_rules

        |access-rules-page-attr|

    .. attribute:: title

        |title-page-attr|

    .. attribute:: value

        |value-page-attr|

    .. attribute:: prompt

        The page's prompt, written in :ref:`markup`.

    .. attribute:: widget

        |text-widget-page-attr|

    .. attribute:: answers

        A list of answers. If the participant's response matches one of these
        answers, it is considered fully correct. Each answer consists of a 'matcher'
        and an answer template for that matcher to use. Each type of matcher
        requires one of two syntax variants to be used. The
        'simple/abbreviated' syntax::

            - <plain>some_text

        or the 'structured' syntax::

            - type: float
              value: 1.25
              rtol: 0.2

        Here are examples of all the supported simple/abbreviated matchers:

        - ``<plain>some_text`` Matches exactly ``some_text``, in a
          case-insensitive manner.
          (i.e. capitalization does not matter)

        - ``<case_sens_plain>some_text`` Matches exactly ``some_text``, in a
          case-sensitive manner.
          (i.e. capitalization matters)

        - ``<regex>[a-z]+`` Matches anything matched by the given
          (Python-style) regular expression that
          follows. Case-insensitive, i.e. capitalization does not matter.

        - ``<case_sens_regex>[a-z]+`` Matches anything matched by the given
          (Python-style) regular expression that
          follows. Case-sensitive, i.e. capitalization matters.

        - ``<sym_expr>x+2*y`` Matches anything that :mod:`sympy` considers
          equivalent to the given expression. Equivalence is determined
          by simplifying ``user_answer - given_expr`` and testing the result
          against 0 using :mod:`sympy`.

        Here are examples of all the supported structured matchers:

        - Floating point. Example::

              -   type: float
                  value: 1.25
                  rtol: 0.2  # relative tolerance
                  atol: 0.2  # absolute tolerance

          One of ``rtol`` or ``atol`` must be given.
    """

    def __init__(self, vctx, location, page_desc):
        super(TextQuestion, self).__init__(vctx, location, page_desc)

        if len(page_desc.answers) == 0:
            raise ValidationError(
                    string_concat(
                        "%s: ",
                        _("at least one answer must be provided"))
                    % location)

        self.matchers = [
                parse_matcher(
                    vctx,
                    "%s, answer %d" % (location, i+1),
                    answer)
                for i, answer in enumerate(page_desc.answers)]
        

        if not any(matcher.correct_answer_text() is not None
                for matcher in self.matchers):
            raise ValidationError(
                    string_concat(
                        "%s: ",
                        _("no matcher is able to provide a plain-text "
                        "correct answer"))
                    % location)

    def required_attrs(self):
        return super(TextQuestion, self).required_attrs() + (
                ("answers", list),
                )

    def get_validators(self):
        return self.matchers

    def grade(self, page_context, page_data, answer_data, grade_data):
        if answer_data is None:
            return AnswerFeedback(correctness=0,
                    feedback=ugettext("No answer provided."))

        answer = answer_data["answer"]
        
        #print max((matcher.grade(answer), matcher.correct_answer_text()) for matcher in self.matchers)
        #print [(matcher.grade(answer), matcher.correct_answer_text()) for matcher in self.matchers]

        correctness, correct_answer_text = max(
                (matcher.grade(answer), matcher.correct_answer_text())
                for matcher in self.matchers)

        return AnswerFeedback(correctness=correctness)

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        # FIXME: Could use 'best' match to answer

        CA_PATTERN = _("A correct answer is: '%s'.")  # noqa

        for matcher in self.matchers:
            unspec_correct_answer_text = matcher.correct_answer_text()
            if unspec_correct_answer_text is not None:
                break

        assert unspec_correct_answer_text

        return CA_PATTERN % unspec_correct_answer_text

    def is_case_sensitive(self):
        return any(matcher.is_case_sensitive for matcher in self.matchers)

# }}}


# {{{ human-graded text question

class HumanGradedTextQuestion(TextQuestionBase, PageBaseWithValue,
        PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer):
    """
    A page asking for a textual answer

    .. attribute:: id

        |id-page-attr|

    .. attribute:: type

        ``HumanGradedTextQuestion``

    .. attribute:: access_rules

        |access-rules-page-attr|

    .. attribute:: title

        |title-page-attr|

    .. attribute:: value

        |value-page-attr|

    .. attribute:: prompt

        The page's prompt, written in :ref:`markup`.

    .. attribute:: widget

        |text-widget-page-attr|

    .. attribute:: validators

        Optional.
        TODO

    .. attribute:: correct_answer

        Optional.
        Content that is revealed when answers are visible
        (see :ref:`flow-permissions`). Written in :ref:`markup`.

    .. attribute:: rubric

        Required.
        The grading guideline for this question, in :ref:`markup`.
    """

    def __init__(self, vctx, location, page_desc):
        super(HumanGradedTextQuestion, self).__init__(vctx, location, page_desc)

        self.validators = [
                parse_validator(
                    vctx,
                    "%s, validator %d" % (location, i+1),
                    answer)
                for i, answer in enumerate(
                    getattr(page_desc, "validators", []))]

    def allowed_attrs(self):
        return super(HumanGradedTextQuestion, self).allowed_attrs() + (
                ("validators", list),
                )

    def human_feedback_point_value(self, page_context, page_data):
        return self.max_points(page_data)

    def get_validators(self):
        return self.validators

# }}}

# vim: foldmethod=marker


# {{{ multiple text question

from crispy_forms.layout import Layout, Div, Fieldset, MultiField, HTML

from crispy_forms.bootstrap import InlineField

class MultipleTextAnswerForm(StyledInlineForm):

    def __init__(self, read_only, interaction_mode, validators, tuple_for_form, *args, **kwargs):
        widget_type = kwargs.pop("widget_type", "text_input")


        super(MultipleTextAnswerForm, self).__init__(*args, **kwargs)
        widget, help_text = None, None
        self.tuple_for_form = tuple_for_form
        self.validators = validators
        self.HTML_list = tuple_for_form[0]
        self.field_list = tuple_for_form[1]
        self.field_width_list = tuple_for_form[2]
        self.helper.layout=(Layout())

        i = 0
        for idx, blank in enumerate(self.HTML_list):

            if self.HTML_list[idx] <> "":
                self.helper.layout.extend([
                        HTML(self.HTML_list[idx])])

            if self.field_list[idx] <> "":
                i = i + 1
                self.fields["blank"+str(idx+1)] = forms.CharField(
                    required=False,
                    widget=None,
                    help_text=None,
                    label=""
                    #label=string_concat(_("Blank"), str(i))
                )

                self.helper.layout.extend([                            
                        #InlineField("blank"+str(i))]
                        InlineField("blank"+str(i), style="width: "+self.field_width_list[i-1])]
                )

        self.helper.layout.extend([                            
                        HTML("<br/><br/>")]
                )


    def clean(self):
        cleaned_data = super(MultipleTextAnswerForm, self).clean()
        
        answer = cleaned_data.get("answer", "")
        print self.validators
        for validator in self.validators:
            validator.validate(answer)
        


ALLOWED_LENGTH_UNIT = ["%", "em", "px", "pt", "cm", "mm"]

def length_to_em(vctx, location, length_tuple, default_width, minimun_width):
    length, unit = length_tuple
        
    if not unit in ALLOWED_LENGTH_UNIT:
        raise ValidationError(
                string_concat(
                    "%s: ",
                    _("unsupported length unit '%s'"))
                % (location, unit))
    elif unit == "%":
        return str(max(float(length)*default_width/100, minimun_width)) + "em"
    elif unit == "em":
        return str(max(float(length), minimun_width)) + "em"
    elif unit == "px":
        return str(max(float(length)/12, minimun_width)) + "em"
    elif unit == "pt":
        return str(max(float(length)/16, minimun_width)) + "em"
    elif unit == "cm":
        return str(max(float(length)/0.1513, minimun_width)) + "em"
    elif unit == "mm":
        return str(max(float(length)/3.5146, minimun_width)) + "em"
    
    
    
class BaseTextAnswerItem(object):
    """Basice class for answer items.

    .. attribute:: type
    .. attribute:: value
    .. attribute:: width
    .. attribute:: correct_answer

    """

    def __init__(self, vctx, location, name, answer_set):
        
        self.name = name
        
        try:
            self.value = answer_set.__getattribute__("value")
        except AttributeError:
            raise ValidationError(
                string_concat(
                    "%s: ",
                    _("should have a point value assigned to  %s."))
                % (location, name))
            
        try:
            self.value=float(self.value)

        except ValueError:
            raise ValidationError(
                string_concat(
                    "%s %s: ",
                    _("point value is invalid."))
                % (location, name))
            
        try:
            self.width = answer_set.__getattribute__("width")
        except AttributeError:
            self.width = None

        
        self.RE_PATTERN = "^(\d*\.\d+|\d+)\s*(.*)$"
        width_pattern=re.compile(self.RE_PATTERN)
        
        # unit is "em"
        self.default_width=10
        self.minimun_width=4
        
        if self.width is not None:
            if isinstance(self.width, (int, float)):
                self.width = str(self.width) + "em"
                
            else:
                width_match = width_pattern.match(self.width)
                if width_match:
                    length_tuple=(
                        width_match.group(1),
                        width_match.group(2))
                    self.width=length_to_em(
                        vctx, location,length_tuple,
                        self.default_width, self.minimun_width)
        else:
            self.width = str(self.default_width) + "em"
            
        
            
        try:
            self.correct_answer = answer_set.__getattribute__("correct_answer")
            #print self.correct_answer
            if self.correct_answer is None:
                raise ValidationError(
                    string_concat(
                        "%s %s: ",
                        _("at least one answer must be provided"))
                    % (location, name))
        except AttributeError:
            raise ValidationError(
                string_concat(
                    "%s %s: ",
                    _("at least one answer must be provided"))
                % (location, name))
        
        
        
        self.matchers = [
                parse_matcher(
                    vctx,
                    "%s, answer %d" % (location, i+1),
                    answer)
                for i, answer in enumerate(self.correct_answer)]
        
        if not any(matcher.correct_answer_text() is not None
                for matcher in self.matchers):
            raise ValidationError(
                    string_concat(
                        "%s: ",
                        _("no matcher is able to provide a plain-text "
                        "correct answer"))
                    % location)


    def get_correct_answer_text(self):

        for matcher in self.matchers:
            unspec_correct_answer_text = matcher.correct_answer_text()
            if unspec_correct_answer_text is not None:
                break

        assert unspec_correct_answer_text
        
        return unspec_correct_answer_text

    def get_correctness(self, answer):

        correctness, correct_answer_text = max(
                (matcher.grade(answer), matcher.correct_answer_text())
                for matcher in self.matchers)        
        return correctness
    
    def get_single_q_credit(self, answer):
        
        return self.value * self.get_correctness(answer)
    
    
class MultipleTextQuestion(TextQuestionBase):
    
    def __init__(self, vctx, location, page_desc):
        super(MultipleTextQuestion, self).__init__(vctx, location, page_desc)
        
        self.value = 0
        
        self.question = page_desc.question
        
        
        from relate.utils import dict_to_struct, struct_to_dict
        
        answer_struct = page_desc.answers
    
        q_list = struct_to_dict(page_desc.answers).keys()
        
        self.embeded_q_list_with_brackets = re.findall(
                r"[^{](?=(\[\[[^\[\]]*\]\]))[^}]", self.question)
        embeded_q_list = re.findall(
                r"[^{](?=\[\[([^\[\]]*)\]\])[^}]", self.question)
        
        
        if len(set(embeded_q_list)) < len(embeded_q_list):
               duplicated = list(
                    set([x for x in embeded_q_list 
                         if embeded_q_list.count(x) > 1]))
               raise ValidationError(
                    string_concat(
                        "%s: ", 
                        _("embeded question name %s not unique."))
                    % (location, ", ".join(duplicated)))
            
        no_answer_set = set(embeded_q_list) - set(q_list)
        
        if len(no_answer_set) > 0:
           raise ValidationError(
                string_concat(
                    "%s: ", 
                    _("answers not provided for %s."))
                % (location, ", ".join(list(no_answer_set))))

        no_question_set = set(q_list) - set(embeded_q_list)
        
        if len(no_question_set) > 0:
           raise ValidationError(
                string_concat(
                    "%s: ", 
                    _("answers provided for non-exist question(s) %s."))
                % (location, ", ".join(list(no_question_set))))
        
        
        embeded_q_removed = self.question
        for embeded in self.embeded_q_list_with_brackets:
            embeded_q_removed = embeded_q_removed.replace(embeded, "")
        
        for bracket in ["[[", "]]"]:
            if bracket in embeded_q_removed:
                raise ValidationError(
                    string_concat(
                        "%s: ",
                        _("have unclosed "),
                        " '%s'.")
                    % (location, bracket))

        self.answer_group = []
        self.correct_answer_list=[]
        self.width_list=[]
        
        for idx, name in enumerate(embeded_q_list):
            
            question_i = getattr(page_desc.answers, name)
            self.answer_group.append(BaseTextAnswerItem(vctx, location, name, question_i))
            self.correct_answer_list.append(self.answer_group[idx].get_correct_answer_text())
            self.value += self.answer_group[idx].value
            self.width_list.append(self.answer_group[idx].width)
            
    

    def get_validators(self):
        return []

    def required_attrs(self):
        return super(MultipleTextQuestion, self).required_attrs() + (
                ("question", "markup"), ("answers", Struct),
                )

    def max_points(self, page_data):
        return self.value

    def allowed_attrs(self):
        return super(MultipleTextQuestion, self).allowed_attrs() + (
                ("answer_comment", "markup"), ("question", "markup")
                )

    def get_question_HTML(self, page_context):

        question_HTML = markup_to_html(page_context, self.question)

        # for correct render of question with more tha on paragraph
        # remove heading <p> tags and change </p> to line break.        
        question_HTML = question_HTML \
                .replace("<p>","").replace("</p>","<br/>")
        
        return question_HTML
                


    def body(self, page_context, page_data):
        return markup_to_html(page_context, self.page_desc.prompt)

    def get_tuple_for_form(self, page_context):

        question_str_remainder = self.get_question_HTML(page_context)

        html_list = []
        field_list = []        
        while question_str_remainder <> "":

            temp_array = question_str_remainder.split("]]",1)
            [string_i, question_str_remainder] = temp_array

            array_i = string_i.split("[[")

            html_list.append(array_i[0])
            field_list.append(array_i[1])
            
            if "]]" not in question_str_remainder:
                html_list.append(question_str_remainder)
                field_list.append("")
                break
        
        
        
        return (html_list, field_list, self.width_list)
        
        
    def make_form(self, page_context, page_data,
            answer_data, answer_is_final):
        read_only = answer_is_final
        
        tuple_for_form = self.get_tuple_for_form(page_context)
        
        #print "answer_data", answer_data

        if answer_data is not None:
            #print "answer_data", answer_data
            answer = answer_data["answer"]
            form = MultipleTextAnswerForm(
                    read_only,
                    get_editor_interaction_mode(page_context),
                    self.get_validators(),
                    tuple_for_form,
                    answer,
                    widget_type=None)
        else:
            answer = None
            form = MultipleTextAnswerForm(
                    read_only,
                    get_editor_interaction_mode(page_context),
                    self.get_validators(),
                    tuple_for_form,
                    widget_type=None)

        return form

    def post_form(self, page_context, page_data, post_data, files_data):
        read_only = False
        tuple_for_form = self.get_tuple_for_form(page_context)
        
        #print post_data
        return MultipleTextAnswerForm(
                read_only,
                get_editor_interaction_mode(page_context),
                self.get_validators(), 
                tuple_for_form,
                post_data, files_data,
                widget_type=None)


    def form_to_html(self, request, page_context, form, answer_data):
        """Returns an HTML rendering of *form*."""

        from django.template import loader, RequestContext
        from django import VERSION as django_version

        if django_version >= (1, 9):
            return loader.render_to_string(
                    "course/crispy-form2.html",
                    context={"form": form},
                    request=request)
        else:
            context = RequestContext(request)
            context.update({"form": form})
            return loader.render_to_string(
                    "course/crispy-form2.html",
                    context_instance=context)
        
        
    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        # FIXME: Could use 'best' match to answer
        
        cor_answer_output = self.question
        
        for idx, bracket in enumerate(self.embeded_q_list_with_brackets):
            cor_answer_output = cor_answer_output.replace(
                bracket,
                "<strong>" + self.correct_answer_list[idx] + "</strong>")

        CA_PATTERN = string_concat(_("A correct answer is"), ": <br/> %s")  # noqa

        return CA_PATTERN % cor_answer_output

        
    def answer_data(self, page_context, page_data, form, files_data):
        return {"answer": form.cleaned_data}

    def expects_answer(self):
        return True

    def is_answer_gradable(self):
        return True
    
    def grade(self, page_context, page_data, answer_data, grade_data):
        if answer_data is None:
            return AnswerFeedback(correctness=0,
                    feedback=ugettext("No answer provided."))
        
        print "answer_data", answer_data        

        answer = answer_data["answer"]
        
        total_credit = 0
        
        for idx, q in enumerate(self.answer_group):
            print q.name
            print answer[q.name]
            print q.get_single_q_credit(answer[q.name])
            total_credit += q.get_single_q_credit(answer[q.name])
            print total_credit
            
        correctness = total_credit/self.value

        return AnswerFeedback(correctness=correctness)
    
    def normalized_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None
        
        print answer_data

        nml_answer_output = self.question

        return None
#        for idx, bracket in enumerate(self.embeded_q_list_with_brackets):
#            nml_answer_output = nml_answer_output.replace(
#                bracket,
#                "<strong>" + answer_data[idx] + "</strong>")
#
#        CA_PATTERN = string_concat(_("A correct answer is"), ": <br/> %s")  # noqa

         

# }}}
