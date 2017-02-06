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


import six
from django.utils.translation import (
        ugettext_lazy as _, ugettext, string_concat)
from course.validation import validate_struct, ValidationError
import django.forms as forms

from relate.utils import StyledForm, Struct
from course.page.base import (
        AnswerFeedback, PageBaseWithTitle, PageBaseWithValue, markup_to_html,
        PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer,

        get_editor_interaction_mode)

import re
import sys


class TextAnswerForm(StyledForm):
    # prevents form submission with codemirror's empty textarea
    use_required_attribute = False

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

        elif widget_type.startswith("editor:"):
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
        for i, validator in enumerate(self.validators):
            try:
                validator.validate(answer)
            except forms.ValidationError:
                if i + 1 == len(self.validators):
                    # last one, and we flunked -> not valid
                    raise
            else:
                # Found one that will take the input. Good enough.
                break


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

            from course.validation import (
                    validate_flow_page, ValidationContext)
            vctx = ValidationContext(
                    # FIXME
                    repo=None,
                    commit_sha=None)

            validate_flow_page(vctx, "submitted page", page_desc)

            if page_desc.type != self.validator_desc.page_type:
                raise ValidationError(ugettext("page must be of type '%s'")
                        % self.validator_desc.page_type)

        except:
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


EXTRA_SPACES_RE = re.compile(r"\s\s+")


def multiple_to_single_spaces(s):
    return EXTRA_SPACES_RE.sub(" ", s).strip()


class CaseSensitivePlainMatcher(TextAnswerMatcher):
    type = "case_sens_plain"
    is_case_sensitive = True
    pattern_type = "string"

    def __init__(self, vctx, location, pattern):
        self.pattern = pattern

    def grade(self, s):
        return int(
                multiple_to_single_spaces(self.pattern)
                ==
                multiple_to_single_spaces(s))

    def correct_answer_text(self):
        return self.pattern


class PlainMatcher(CaseSensitivePlainMatcher):
    type = "plain"
    is_case_sensitive = False
    pattern_type = "string"

    def grade(self, s):
        return int(
            multiple_to_single_spaces(self.pattern.lower())
            ==
            multiple_to_single_spaces(s.lower()))


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
    if six.PY2:
        if isinstance(s, unicode):  # noqa -- has Py2/3 guard
            # Sympy is not spectacularly happy with unicode function names
            s = s.encode()

    from pymbolic import parse
    from pymbolic.interop.sympy import PymbolicToSympyMapper

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


def float_or_sympy_evalf(s):
    if isinstance(s, six.integer_types + (float,)):
        return s

    if not isinstance(s, six.string_types):
        raise TypeError("expected string, int or float for floating point "
                "literal")

    try:
        return float(s)
    except ValueError:
        pass

    # avoiding IO error if empty input when
    # the is field not required
    if s == "":
        return s

    # return a float type value, expression not allowed
    return float(parse_sympy(s).evalf())


def _is_valid_float(s):
    try:
        float_or_sympy_evalf(s)
    except:
        return False
    else:
        return True


class SetMatcherBase(TextAnswerMatcher):
    is_case_sensitive = False
    pattern_type = "struct"
    pass


class IntSetMatcher(SetMatcherBase):
    type = "int_set"

    pass


class FloatSetMatcher(SetMatcherBase):
    pass


class FloatListWithWrapperMatcher(TextAnswerMatcher):
    type = "float_list_with_wrapper"
    is_case_sensitive = False
    pattern_type = "struct"

    def __init__(self, vctx, location, matcher_desc):
        self.matcher_desc = matcher_desc

        validate_struct(
                vctx,
                location,
                matcher_desc,
                required_attrs=(
                    ("type", str),
                    ("value", str),

                    # atol is added to required_attrs because there maybe
                    # elements in value which are zeros.
                    ("atol", six.integer_types + (float, str)),
                    ),
                allowed_attrs=(
                    ("rtol", six.integer_types + (float, str)),
                    ("allowed_left_wrapper_list", list),
                    ("allowed_right_wrapper_list", list),
                    ("forced_left_wrapper", list),
                    ("forced_right_wrapper", list),
                    ("force_wrapper_percentage_list", list),
                    ("forced_left_wrapper_percentage", float),
                    ("forced_right_wrapper_percentage", float),
                    ("list_item_average_percentage", bool),
                    ("as_set", bool),
                    ("set_allowed_range", (list, tuple, set)),
                ),
                )

        self.validate_value(vctx, location)

        if hasattr(matcher_desc, "rtol"):
            try:
                self.matcher_desc.rtol = \
                        float_or_sympy_evalf(matcher_desc.rtol)
            except:
                raise ValidationError(
                        string_concat(
                            "%s: 'rtol' ",
                            _("does not provide a valid float literal"))
                        % location)

            if matcher_desc.value == 0:
                raise ValidationError(
                        string_concat(
                            "%s: 'rtol' ",
                            _("not allowed when 'value' is zero"))
                        % location)

        if hasattr(matcher_desc, "atol"):
            try:
                self.matcher_desc.atol = \
                        float_or_sympy_evalf(matcher_desc.atol)
            except:
                raise ValidationError(
                        string_concat(
                            "%s: 'atol' ",
                            _("does not provide a valid float literal"))
                        % location)

        if (
                not hasattr(matcher_desc, "atol")
                and
                not hasattr(matcher_desc, "rtol")
                and
                vctx is not None):
            vctx.add_warning(location,
                    _("Float match should have either rtol or atol--"
                        "otherwise it will match any number"))

    def validate_value(self, vctx, location):
        value = self.matcher_desc.value.strip()
        if hasattr(self.matcher_desc, "forced_left_wrapper"):
            has_valid_lwrapper = False
            for lwrapper in self.matcher_desc.forced_left_wrapper:
                if not value.startswith(lwrapper):
                    continue
                else:
                    has_valid_lwrapper = True
                    value = value[len(lwrapper):]
                    break
            if not has_valid_lwrapper:
                raise ValidationError(
                    string_concat(
                        "%s: 'value' ",
                        _("does not provide a valid left wrapper"))
                    % location)

        if hasattr(self.matcher_desc, "forced_right_wrapper"):
            has_valid_rwrapper = False
            for rwrapper in self.matcher_desc.forced_right_wrapper:
                if not value.endswith(rwrapper):
                    continue
                else:
                    has_valid_rwrapper = True
                    value = value[:-len(rwrapper)]
                    break
            if not has_valid_rwrapper:
                raise ValidationError(
                    string_concat(
                        "%s: 'value' ",
                        _("does not provide a valid right wrapper"))
                    % location)

        if hasattr(self.matcher_desc, "force_wrapper_percentage_list"):
            for w in self.matcher_desc.force_wrapper_percentage_list:
                if not isinstance(w, (float,int)):
                    raise ValidationError(
                        string_concat(
                            "%s: 'force_wrapper_percentage_list' ",
                            _("must be an integar or float"),
                            "%s"
                        )
                        % (location, w))
            if len(self.matcher_desc.force_wrapper_percentage_list) != 2:
                raise ValidationError(
                    string_concat(
                        "%s: 'force_wrapper_percentage_list' ",
                        _("lenght of this list must be 2"),
                    )
                    % (location, ))
            if sum(self.matcher_desc.force_wrapper_percentage_list) > 1:
                vctx.add_warning(location,
                                 _("sum of force_wrapper_percentage_list should not exceed 1."))

        if hasattr(self.matcher_desc, "forced_left_wrapper_percentage"):
            if self.matcher_desc.forced_left_wrapper_percentage > 1:
                vctx.add_warning(location,
                                 _("forced_left_wrapper_percentage should not exceed 1."))

        if hasattr(self.matcher_desc, "forced_right_wrapper_percentage"):
            if self.matcher_desc.forced_right_wrapper_percentage > 1:
                vctx.add_warning(location,
                                 _("forced_right_wrapper_percentage should not exceed 1."))

        if (hasattr(self.matcher_desc, "forced_left_wrapper_percentage")
            and
            hasattr(self.matcher_desc, "forced_right_wrapper_percentage")):
            if (self.matcher_desc.forced_left_wrapper_percentage
                    +
                    self.matcher_desc.forced_right_wrapper_percentage > 1):
                vctx.add_warning(location,
                                 _("sum of forced_left_wrapper_percentage "
                                   "and forced_right_wrapper_percentage "
                                   "should not exceed 1."))

        if hasattr(self.matcher_desc, "allowed_left_wrapper"):
            for lwrapper in self.matcher_desc.allowed_left_wrapper:
                if not value.startswith(lwrapper):
                    continue
                else:
                    value = value[len(lwrapper):]
                    break

        if hasattr(self.matcher_desc, "allowed_right_wrapper"):
            for rwrapper in self.matcher_desc.allowed_right_wrapper:
                if not value.endswith(rwrapper):
                    continue
                else:
                    value = value[:-len(rwrapper)]
                    break

        try:
            value_list = value.split(",")
        except:
            raise ValidationError(
                string_concat(
                    "%s: 'value' ",
                    _("cannot be converted into a list"))
                % location)

        for v in value_list:
            if len(v) == 0:
                raise ValidationError(
                    string_concat(
                        "%s: 'value' ",
                        _("cannot be converted into a list"))
                    % location)
            try:
                float_or_sympy_evalf(v)
            except:
                raise ValidationError(
                    string_concat(
                        "%s: 'value' ",
                        "%s",
                        _("is not a valid math number"))
                    % (location,v))

    def validate(self, s):
        value = s
        used_forced_left_wrapper = ""
        used_forced_right_wrapper = ""
        if hasattr(self.matcher_desc, "forced_left_wrapper"):
            has_valid_lwrapper = False
            for lwrapper in self.matcher_desc.forced_left_wrapper:
                if not value.startswith(lwrapper):
                    continue
                else:
                    used_forced_left_wrapper = lwrapper
                    has_valid_lwrapper = True
                    value = value[len(lwrapper):]
                    break
            if not has_valid_lwrapper:
                raise forms.ValidationError(
                    string_concat(
                        ugettext("Error"), ": ",
                        ugettext("answer provided does not have a "
                          "required left wrapper, allowed "
                          "left wrappers are %s")
                    )
                    % ", ".join("'%s'" % s for s in self.matcher_desc.forced_left_wrapper)
                )

        if hasattr(self.matcher_desc, "forced_right_wrapper"):
            has_valid_rwrapper = False
            for rwrapper in self.matcher_desc.forced_right_wrapper:
                if not value.endswith(rwrapper):
                    continue
                else:
                    used_forced_right_wrapper = rwrapper
                    has_valid_rwrapper = True
                    value = value[:-len(rwrapper)]
                    break
            if not has_valid_rwrapper:
                raise forms.ValidationError(
                    string_concat(
                        ugettext("Error"), ": ",
                        ugettext("answer provided does not have a "
                          "required right wrapper, allowed "
                          "right wrappers are %s")
                    )
                    % ", ".join("'%s'" % s for s in self.matcher_desc.forced_right_wrapper)
                )

        if hasattr(self.matcher_desc, "allowed_left_wrapper"):
            for lwrapper in self.matcher_desc.allowed_left_wrapper:
                if not value.startswith(lwrapper):
                    continue
                else:
                    value = value[len(lwrapper):]
                    break

        if hasattr(self.matcher_desc, "allowed_right_wrapper"):
            for rwrapper in self.matcher_desc.allowed_right_wrapper:
                if not value.endswith(rwrapper):
                    continue
                else:
                    value = value[:-len(rwrapper)]
                    break

        try:
            value_list = value.split(",")
        except:
            raise forms.ValidationError(
                string_concat(
                    ugettext("Error"), ": ",
                    ugettext("'%s' cannot be converted into a list"))
                % value
                )

        for v in value_list:
            if len(v.strip()) == 0:
                raise forms.ValidationError(
                    string_concat(
                        ugettext("Error"), ": ",
                        "'%s' ",
                        ugettext("cannot be converted into a list"))
                    % value)
            try:
                float_or_sympy_evalf(v)
            except:
                tp, e, _ = sys.exc_info()
                if tp.__name__ == "TypeError" and str(e) == u"can't convert expression to float":
                    raise forms.ValidationError(
                        string_concat(
                            ugettext("Error"), ": ",
                            ugettext("TypeError"), ": ",
                            ugettext("can't convert '%s' to a valid math number")
                            % str(v))
                    )
                else:
                    raise forms.ValidationError("%(err_type)s: %(err_str)s"
                                                % {"err_type": tp.__name__, "err_str": str(e)})

        if getattr(self.matcher_desc, "as_set", False):
            if hasattr(self.matcher_desc, "set_allowed_range"):
                for v in value_list:
                    if float(v) not in self.matcher_desc.set_allowed_range:
                        raise forms.ValidationError(
                            string_concat(
                                ugettext("Error"), ": ",
                                ugettext("'%s' is not in the allwed range")
                                % str(v))
                        )

        return value_list, used_forced_left_wrapper, used_forced_right_wrapper

    def grade(self, s):
        if s == "":
            return 0

        answer_list, answer_lwrapper, answer_rwrapper = self.validate(s)
        corr_list, corr_lwrapper, corr_rwrapper = self.validate(self.matcher_desc.value)

        total_percentage = 1
        scored_percentage = 1
        wrapper_percentage = 0

        if hasattr(self.matcher_desc, "force_wrapper_percentage_list"):
            if answer_lwrapper != corr_lwrapper:
                scored_percentage -= self.matcher_desc.force_wrapper_percentage_list[0]
            if answer_rwrapper != corr_rwrapper:
                scored_percentage -= self.matcher_desc.force_wrapper_percentage_list[1]
            wrapper_percentage += sum(self.matcher_desc.force_wrapper_percentage_list)
        else:
            if answer_lwrapper != corr_lwrapper:
                if hasattr(self.matcher_desc, "forced_left_wrapper_percentage"):
                    scored_percentage -= self.matcher_desc.forced_left_wrapper_percentage
                    wrapper_percentage += self.matcher_desc.forced_left_wrapper_percentage
                else:
                    return 0

            if answer_rwrapper != corr_rwrapper:
                if hasattr(self.matcher_desc, "forced_right_wrapper_percentage"):
                    scored_percentage -= self.matcher_desc.forced_right_wrapper_percentage
                    wrapper_percentage += self.matcher_desc.forced_right_wrapper_percentage
                else:
                    return 0

        if len(answer_list) != len(corr_list):
            return 0

        if getattr(self.matcher_desc, "as_set", False):
            answer_list_evalf=[float_or_sympy_evalf(item) for item in answer_list]
            corr_list_evalf=[float_or_sympy_evalf(item) for item in corr_list]
            if set(answer_list_evalf) == set(corr_list_evalf):
                return 1
            else:
                return 0

        list_percentage = total_percentage - wrapper_percentage
        each_percent = None
        if hasattr(self.matcher_desc, "list_item_average_percentage"):
            each_percent = list_percentage / len(corr_list)

        for i, number_str in enumerate(answer_list):
            answer_float = float_or_sympy_evalf(number_str)
            corr_float = float_or_sympy_evalf(corr_list[i])

            if hasattr(self.matcher_desc, "atol"):
                if (abs(answer_float - corr_float)
                        > self.matcher_desc.atol):
                    if each_percent:
                        scored_percentage -= each_percent
                    else:
                        return 0
            if hasattr(self.matcher_desc, "rtol"):
                if corr_float != 0:
                    if (abs(answer_float - corr_float)
                            / abs(corr_float)
                            > self.matcher_desc.rtol):
                        if each_percent:
                            scored_percentage -= each_percent
                        else:
                            return 0
                else:
                    if (abs(answer_float - corr_float)
                            > self.matcher_desc.atol):
                        if each_percent:
                            scored_percentage -= each_percent
                        else:
                            return 0

        if scored_percentage > 0:
            return scored_percentage
        else:
            return 0

    def correct_answer_text(self):
        return str(self.matcher_desc.value)


class FloatMatcher(TextAnswerMatcher):
    type = "float"
    is_case_sensitive = False
    pattern_type = "struct"

    def __init__(self, vctx, location, matcher_desc):
        self.matcher_desc = matcher_desc

        validate_struct(
                vctx,
                location,
                matcher_desc,
                required_attrs=(
                    ("type", str),
                    ("value", six.integer_types + (float, str)),
                    ),
                allowed_attrs=(
                    ("rtol", six.integer_types + (float, str)),
                    ("atol", six.integer_types + (float, str)),
                    ),
                )

        try:
            self.matcher_desc.value = \
                    float_or_sympy_evalf(matcher_desc.value)
        except:
            raise ValidationError(
                    string_concat(
                        "%s: 'value' ",
                        _("does not provide a valid float literal"))
                    % location)

        if hasattr(matcher_desc, "rtol"):
            try:
                self.matcher_desc.rtol = \
                        float_or_sympy_evalf(matcher_desc.rtol)
            except:
                raise ValidationError(
                        string_concat(
                            "%s: 'rtol' ",
                            _("does not provide a valid float literal"))
                        % location)

            if matcher_desc.value == 0:
                raise ValidationError(
                        string_concat(
                            "%s: 'rtol' ",
                            _("not allowed when 'value' is zero"))
                        % location)

        if hasattr(matcher_desc, "atol"):
            try:
                self.matcher_desc.atol = \
                        float_or_sympy_evalf(matcher_desc.atol)
            except:
                raise ValidationError(
                        string_concat(
                            "%s: 'atol' ",
                            _("does not provide a valid float literal"))
                        % location)
        else:
            if matcher_desc.value == 0:
                vctx.add_warning(location,
                         _("Float match for 'value' zero should have atol--"
                           "otherwise it will match any number"))

        if (
                not matcher_desc.value == 0
                and
                not hasattr(matcher_desc, "atol")
                and
                not hasattr(matcher_desc, "rtol")
                and
                vctx is not None):
            vctx.add_warning(location,
                    _("Float match should have either rtol or atol--"
                        "otherwise it will match any number"))

    def validate(self, s):
        try:
            float_or_sympy_evalf(s)
        except:
            tp, e, _ = sys.exc_info()
            raise forms.ValidationError("%(err_type)s: %(err_str)s"
                    % {"err_type": tp.__name__, "err_str": str(e)})

    def grade(self, s):
        if s == "":
            return 0

        answer_float = float_or_sympy_evalf(s)

        if hasattr(self.matcher_desc, "atol"):
            if (abs(answer_float - self.matcher_desc.value)
                    > self.matcher_desc.atol):
                return 0
        if hasattr(self.matcher_desc, "rtol"):
            if self.matcher_desc.value !=0:
                if (abs(answer_float - self.matcher_desc.value)
                        / abs(self.matcher_desc.value)
                        > self.matcher_desc.rtol):
                    return 0
            else:
                if (abs(answer_float - self.matcher_desc.value)
                        > self.matcher_desc.rtol):
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
        FloatListWithWrapperMatcher,
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
                            'matchertype': matcher_class.pattern_type})

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
    if isinstance(matcher_desc, six.string_types):
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

    .. attribute:: is_optional_page

        |is-optional-page-attr|

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
            answer_data, page_behavior):
        read_only = not page_behavior.may_change_answer

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

    def process_form_post(self, page_context, page_data, post_data, files_data,
            page_behavior):
        return TextAnswerForm(
                not page_behavior.may_change_answer,
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

    def normalized_bytes_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None

        return (".txt", answer_data["answer"].encode("utf-8"))
# }}}


# {{{ survey text question

class SurveyTextQuestion(TextQuestionBase):
    """
    A page asking for a textual answer, without any notion of 'correctness'

    .. attribute:: id

        |id-page-attr|

    .. attribute:: type

        ``TextQuestion``

    .. attribute:: is_optional_page

        |is-optional-page-attr|

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

    .. attribute:: is_optional_page

        |is-optional-page-attr|

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

    .. attribute:: answer_explanation

        Text justifying the answer, written in :ref:`markup`.
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

    def allowed_attrs(self):
        return super(TextQuestion, self).allowed_attrs() + (
                ("answer_explanation", "markup"),
                )

    def get_validators(self):
        return self.matchers

    def grade(self, page_context, page_data, answer_data, grade_data):
        if answer_data is None:
            return AnswerFeedback(correctness=0,
                    feedback=ugettext("No answer provided."))

        answer = answer_data["answer"]

        correctness = 0

        for matcher in self.matchers:
            try:
                matcher.validate(answer)
            except forms.ValidationError:
                continue

            matcher_correctness = matcher.grade(answer)
            if (matcher_correctness is not None
                    and matcher_correctness >= correctness):
                correctness = matcher_correctness

        return AnswerFeedback(correctness=correctness)

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        # FIXME: Could use 'best' match to answer

        CA_PATTERN = string_concat(_("A correct answer is"), ": '%s'.")  # noqa

        for matcher in self.matchers:
            unspec_correct_answer_text = matcher.correct_answer_text()
            if unspec_correct_answer_text is not None:
                break

        assert unspec_correct_answer_text

        result = CA_PATTERN % unspec_correct_answer_text

        if hasattr(self.page_desc, "answer_explanation"):
            result += markup_to_html(page_context, self.page_desc.answer_explanation)

        return result

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

    .. attribute:: is_optional_page

        |is-optional-page-attr|

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
