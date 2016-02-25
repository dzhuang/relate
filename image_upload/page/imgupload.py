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

import django.forms as forms
from django.utils.translation import ugettext as _, string_concat

from image_upload.models import FlowPageImage

from course.page.base import (
        PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback,
        PageBaseWithCorrectAnswer,
        markup_to_html)
from course.models import FlowPageData
from course.validation import ValidationError

from relate.utils import StyledForm

from crispy_forms.layout import Layout, HTML


# {{{ image upload question

class ImageUploadForm(StyledForm):
    
    def __init__(self, maximum_megabytes, mime_types, page_context, 
                 page_behavior, page_data, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)

        self.max_file_size = maximum_megabytes * 1024**2
        self.mime_types = mime_types
        self.page_behavior = page_behavior
        self.page_context = page_context
        
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
                kwargs={'course_identifier': page_context.course,
                        'flow_session_id': page_context.flow_session.id,
                        'ordinal': page_context.ordinal
                       }
                )
        self.helper.form_method = "POST"
        
        self.helper.layout = Layout(
                HTML(
                    "{% extends 'image_upload/jfu-form.html' %}"
                    + jfu_button_control
                    ),
                )

    def clean(self):
        flow_session_id = self.page_context.flow_session.id
        ordinal = self.page_context.ordinal
        user = self.page_context.flow_session.user
        fpd=FlowPageData.objects.get(
            flow_session=flow_session_id, ordinal=ordinal)

        qs = FlowPageImage.objects.filter(
                creator=user
                ).filter(flow_session=flow_session_id
                ).filter(image_page_id=fpd.page_id)
        
        if len(qs) == 0:
            raise forms.ValidationError(_("You have not upload image(s)!"))

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

    def __init__(self, vctx, location, page_desc):
        super(ImageUploadQuestion, self).__init__(vctx, location, page_desc)

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
                ("imageMaxWidth", (int, float)),
                ("imageMaxHeight", (int, float)),
                ("ImageMaxFileSizeByte", (int, float)),
                ("previewMaxWidth", (int, float)),
                ("previewMaxHeight", (int, float)),
                ("maxNumberOfFiles", (int, float)),
                )

    def human_feedback_point_value(self, page_context, page_data):
        return self.max_points(page_data)

    def markup_body_for_title(self):
        return self.page_desc.prompt

    def body(self, page_context, page_data):
        return markup_to_html(page_context, self.page_desc.prompt)

    def make_form(self, page_context, page_data,
            answer_data, page_behavior):

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
        ctx = {"form": form, 
               "JQ_OPEN": '{%',
               'JQ_CLOSE': '%}',
               "accepted_mime_types": ['image/*'],
               'course_identifier': page_context.course,
               "flow_session_id": page_context.flow_session.id,
               "ordinal": page_context.ordinal,
               "SHOW_CREATION_TIME": True,

               "imageMaxWidth": getattr(self.page_desc, "imageMaxWidth", 1000),
               "imageMaxHeight": getattr(self.page_desc, "imageMaxHeight", 1000),
               "maxFileSize": getattr(self.page_desc, "maxFileSize", 1) * 1024**2,
               "minFileSize": getattr(self.page_desc, "minFileSize", 0.1) * 1024**2,
               "previewMaxWidth": getattr(self.page_desc, "previewMaxWidth", 200),
               "previewMaxHeight": getattr(self.page_desc, "previewMaxHeight", 200),
               "maxNumberOfFiles": getattr(self.page_desc, "maxNumberOfFiles", 3)
               }

        from django.template import RequestContext
        from django.template.loader import render_to_string
        return render_to_string(
            "image_upload/imgupload-page-tmpl.html",
            RequestContext(request, ctx))

    def answer_data(self, page_context, page_data, form, files_data):
        flow_session_id = page_context.flow_session.id
        ordinal = page_context.ordinal
        user = page_context.flow_session.user
        fpd=FlowPageData.objects.get(
            flow_session=flow_session_id, ordinal=ordinal)

        qs = FlowPageImage.objects.filter(
                creator=user
                ).filter(flow_session=flow_session_id
                ).filter(image_page_id=fpd.page_id)
        
        if len(qs) > 0:
            import json
            return json.dumps(repr(qs))
        else:
            return None

# }}}


# vim: foldmethod=marker
