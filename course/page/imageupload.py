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
from crispy_forms import layout, bootstrap

from course.models import Image


# {{{ upload question

class ImageUploadForm(StyledForm):
    uploaded_image = forms.ImageField(required=False)
    
#    class Meta:
#        model = Image
#        fields = "__all__"

    def __init__(self, maximum_megabytes, mime_types, page_context, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)

        self.max_file_size = maximum_megabytes * 1024**2
        self.mime_types = mime_types
        self.page_context = page_context
        print type(page_context)
        print dir(page_context)
        print page_context.page_uri
        self.helper.form_id="fileupload"
        self.helper.form_action = "jfu_upload"
        #self.helper.attrs={'onsubmit': 'return onsubmitform();'}

        from django.core.urlresolvers import reverse
#        self.helper.form_action = reverse("relate-view_flow_page",
#                            args=(course.identifier, flow_session.id, ordinal))
        #self.helper.form_action = "/course/trytrytry/flow-session/74/1/"
        self.helper.form_method = "POST"
        self.helper.layout = layout.Layout(
            layout.Fieldset(
                u"图片上传",
                layout.HTML(u"""{% load i18n %}
                        <noscript>
                            <input type="hidden" name="redirect" value="{{ request.path }}">
                        </noscript>

                        <div class="row fileupload-buttonbar">

                            <div class="col-lg-7">
                                <span class="btn btn-success fileinput-button">
                                    <i class="glyphicon glyphicon-plus"></i>
                                    <span>{% trans "Add files..." %}</span>

                                    <input 
                                        type="file" name="files[]" multiple

                                        {% if accepted_mime_types %}
                                            accept = '{{ accepted_mime_types|join:"," }}'
                                        {% endif %}
                                    >

                                </span>

                                <button type="submit" class="btn btn-primary start" name="upload_all_image">
                                    <i class="glyphicon glyphicon-upload"></i>
                                    <span>{% trans "Start upload" %}</span>
                                </button>
                                <button type="reset" class="btn btn-warning cancel">
                                    <i class="glyphicon glyphicon-ban-circle"></i>
                                    <span>{% trans "Cancel upload" %}</span>
                                </button>
                                <button type="button" class="btn btn-danger delete">
                                    <i class="glyphicon glyphicon-trash"></i>
                                    <span>{% trans "Delete" %}</span>
                                </button>
                                <input type="checkbox" class="toggle">

                            </div>

                            <div class="col-lg-5 fileupload-progress fade">
                                <div 
                                    class="progress progress-striped active" 
                                    role="progressbar" 
                                    aria-valuemin="0" aria-valuemax="100"
                                >
                                    <div class="progress-bar progress-bar-success" style="width:0%;">
                                    </div>
                                </div>

                                <div class="progress-extended">&nbsp;</div>
                            </div>


                        </div>
                        <div class="fileupload-loading"></div>
                        <br>
                        <table role="presentation" class="table table-striped">
                            <tbody class="files"></tbody>
                        </table>

                """),
                
#                layout.HTML("""
#                
#                <div class="row fileupload-buttonbar">
#                
#                <button type="submit" class="btn btn-primary start" name="save_image"> <i class="glyphicon glyphicon-upload"></i> <span>{% trans "Start upload" %}</span> </button>
#                
#                </div>
#                
#                """),
                
#                layout.HTML("""
#
#                <a data-toggle="modal" href="/image_upload/" data-target="#myModal">Click me !</a>
#
#                <!-- Modal -->
#                <div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
#                    <div class="modal-dialog">
#                        <div class="modal-content">
#                            <div class="modal-header">
#                                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
#
#                            </div>
#                            <div class="modal-body"><div class="te"></div></div>
#                            <div class="modal-footer">
#                                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
#                                <button type="button" class="btn btn-primary">Save changes</button>
#                            </div>
#                        </div>
#                        <!-- /.modal-content -->
#                    </div>
#                    <!-- /.modal-dialog -->
#                </div>
#                <!-- /.modal -->                
#                """)
                
                #"image_path",
                #"delete_image",
            ),
            bootstrap.FormActions(
                layout.Submit('submit', _('Save'), css_class="btn btn-primary"),
            )
        )

    def clean_uploaded_image(self):
        uploaded_image = self.cleaned_data['uploaded_image']

        return uploaded_image


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

    def files_data_to_answer_data(self, files_data):
        print "files_data:", files_data
        pass
#        files_data["uploaded_image"].seek(0)
#        buf = files_data["uploaded_image"].read()
#
#        if len(self.page_desc.mime_types) == 1:
#            mime_type, = self.page_desc.mime_types
#        else:
#            mime_type = files_data["uploaded_image"].content_type
#        from base64 import b64encode
#        return {
#                "base64_data": b64encode(buf).decode(),
#                "mime_type": mime_type,
#                }

    def make_form(self, page_context, page_data,
            answer_data, page_behavior):
        form = ImageUploadForm(
                self.page_desc.maximum_megabytes, self.page_desc.mime_types,
                page_context)
        #print page_context
        #print page_context.page_uri
        
        
        
        return form

    def process_form_post(self, page_context, page_data, post_data, files_data,
            page_behavior):
        form = ImageUploadForm(
                self.page_desc.maximum_megabytes, self.page_desc.mime_types,
                page_context,
                post_data, files_data)
        
        print form.as_p()
        
        return form

    def form_to_html(self, request, page_context, form, answer_data):
        ctx = {"form": form}
        if answer_data is not None:
            ctx["mime_type"] = answer_data["mime_type"]
            ctx["data_url"] = "data:%s;base64,%s" % (
                answer_data["mime_type"],
                answer_data["base64_data"],
                )
        
        ctx["JQ_OPEN" ]= '{%'
        ctx['JQ_CLOSE' ]= '%}'
        ctx["accepted_mime_types"]= ['image/*']

        from django.template import RequestContext
        from django.template.loader import render_to_string
        return render_to_string(
                "course/image-upload-template.html",
                RequestContext(request, ctx))

    def answer_data(self, page_context, page_data, form, files_data):
        return self.files_data_to_answer_data(files_data)

# }}}


# vim: foldmethod=marker
