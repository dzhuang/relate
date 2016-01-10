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


import django.forms as forms
from django.utils.translation import ugettext as _, ugettext_lazy, string_concat

from course.page.base import (
        PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback,
        PageBaseWithCorrectAnswer,
        markup_to_html)
from course.validation import ValidationError

from relate.utils import StyledForm
from relate.utils import StyledModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML

from course.models import Image


# {{{ upload question

class ImageUploadForm(StyledForm):
    uploaded_image = forms.CharField(required=True,
#                                     widget = forms.HiddenInput()
                                     )
    
    def __init__(self, maximum_megabytes, mime_types, page_context, 
                 page_behavior, page_data, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)

        self.max_file_size = maximum_megabytes * 1024**2
        self.mime_types = mime_types
        self.page_behavior = page_behavior
        
        jfu_button_control = ""
        
        if not self.page_behavior.may_change_answer:
            jfu_button_control = (
                "{% block UPLOAD_FORM_BUTTON_BAR %}{% endblock %}"
                "{% block JS_UPLOAD_TEMPLATE_CONTROLS %}{% endblock %}"
                "{% block JS_DOWNLOAD_TEMPLATE_DELETE %}{% endblock %}")
        
        self.helper.form_id = "fileupload"

        from django.core.urlresolvers import reverse
        self.helper.form_action = reverse(
                "jfu_upload",
                kwargs={'flow_session_id': page_context.flow_session.id, 
                    'ordinal': page_context.ordinal}
                )
        self.helper.form_method = "POST"
        
        self.helper.layout = Layout(
                Fieldset('This is it', 'uploaded_image'), 
                HTML(
                    "{% extends 'course/basic_upload_form.html' %}" 
                    + jfu_button_control
                    ),
                )

#    def clean_uploaded_image(self):
#        uploaded_image = self.cleaned_data['uploaded_image']
#
#        return uploaded_image


class ImageUploadQuestion(PageBaseWithTitle, PageBaseWithValue,
        PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer):
    """
    A page allowing the submission of a file upload that will be
    graded with text feedback by a human grader.

    .. attribute:: id

        |id-page-attr|

    .. attribute:: type

        ``Page``

    .. attribute:: access_rules

        |access-rules-page-attr|

    .. attribute:: title

        |title-page-attr|

    .. attribute:: value

        |value-page-attr|

    .. attribute:: prompt

        Required.
        The prompt for this question, in :ref:`markup`.

    .. attribute:: mime_types

        Required.
        A list of `MIME types <https://en.wikipedia.org/wiki/Internet_media_type>`_
        that the question will accept.
        Only ``application/pdf`` is allowed for the moment.

        The value ``"application/octet-stream"`` will allow any file at all
        to be uploaded.

    .. attribute:: maximum_megabytes

        Required.
        The largest file size
        (in `Mebibyte <https://en.wikipedia.org/wiki/Mebibyte>`)
        that the page will accept.

    .. attribute:: correct_answer

        Optional.
        Content that is revealed when answers are visible
        (see :ref:`flow-permissions`). Written in :ref:`markup`.

    .. attribute:: correct_answer

        Optional.
        Content that is revealed when answers are visible
        (see :ref:`flow-permissions`). Written in :ref:`markup`.

    .. attribute:: rubric

        Required.
        The grading guideline for this question, in :ref:`markup`.
    """

    ALLOWED_MIME_TYPES = [
            "image/jpeg",
            "image/png",
            "application/pdf",
            ]

    def __init__(self, vctx, location, page_desc):
        super(ImageUploadQuestion, self).__init__(vctx, location, page_desc)

        if not (set(page_desc.mime_types) <= set(self.ALLOWED_MIME_TYPES)):
            raise ValidationError(
                    string_concat(
                        "%(location)s: ",
                        _("unrecognized mime types"),
                        " '%(presenttype)s'")
                    % {
                        'location': location,
                        'presenttype': ", ".join(
                            set(page_desc.mime_types)
                            - set(self.ALLOWED_MIME_TYPES))})

        if vctx is not None:
            if not hasattr(page_desc, "value"):
                vctx.add_warning(location, _("upload question does not have "
                        "assigned point value"))

    def required_attrs(self):
        return super(ImageUploadQuestion, self).required_attrs() + (
                ("prompt", "markup"),
                ("maximum_megabytes", (int, float)),
                )

    def allowed_attrs(self):
        return super(ImageUploadQuestion, self).allowed_attrs() + (
                ("correct_answer", "markup"),
                ("mime_types", list),
                )

    def human_feedback_point_value(self, page_context, page_data):
        return self.max_points(page_data)

    def markup_body_for_title(self):
        return self.page_desc.prompt

    def body(self, page_context, page_data):
        return markup_to_html(page_context, self.page_desc.prompt)

    def make_form(self, page_context, page_data,
            answer_data, page_behavior):

        if page_data and len(page_data["image_pk"]) > 0:
            answer = {"uploaded_image": ",".join(str(e) for e in page_data["image_pk"])}

            form = ImageUploadForm(
                self.page_desc.maximum_megabytes, self.page_desc.mime_types,
                page_context, page_behavior, page_data, answer)
        else:
            answer = None
            form = ImageUploadForm(
                self.page_desc.maximum_megabytes, self.page_desc.mime_types,
                page_context, page_behavior, page_data)

        return form


    def process_form_post(self, page_context, page_data, post_data, files_data,
            page_behavior):
        
        form = ImageUploadForm(
                self.page_desc.maximum_megabytes, self.page_desc.mime_types,
                page_context, page_behavior, page_data,
                post_data, files_data)
        
        return form

    def form_to_html(self, request, page_context, form, answer_data):
        ctx = {"form": form}
        
        ctx["JQ_OPEN" ]= '{%'
        ctx['JQ_CLOSE' ]= '%}'
        ctx["accepted_mime_types"]= ['image/*']
        ctx["flow_session_id"]=page_context.flow_session.id
        ctx["ordinal"]=page_context.ordinal

        from django.template import RequestContext
        from django.template.loader import render_to_string
        return render_to_string(
                "course/image-upload-template.html",
                RequestContext(request, ctx))

    def answer_data(self, page_context, page_data, form, files_data):
        if page_data:
            if len(page_data["image_pk"]) > 0:                
                return {"answer": ",".join(str(e) for e in page_data["image_pk"])}
        else:
            return None

# }}}


# vim: foldmethod=marker
