# -*- coding: UTF-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms import layout, bootstrap

from models import Image


class ImageForm(forms.ModelForm):
    image_path = forms.CharField(
        max_length=255,
        widget=forms.HiddenInput(),
        required=True,
    )
#    delete_image = forms.BooleanField(
#        widget=forms.HiddenInput(),
#        required=False,
#    )

    class Meta:
        model = Image
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id="fileupload"
        self.helper.form_action = "jfu_upload"
        self.helper.form_method = "POST"

        self.helper.layout = layout.Layout(
            layout.Fieldset(
                u"表格",
                layout.HTML(u"""{% load i18n %}
                        <noscript>
                            <input type="hidden" name="redirect" value="{{ request.path }}">
                        </noscript>


                        {% block UPLOAD_FORM_BUTTON_BAR %}
                        <div class="row fileupload-buttonbar">
                        {% comment %}
                         The fileupload-buttonbar contains buttons to add/delete files and
                         start/cancel the upload 
                        {% endcomment %}

                            <div class="col-lg-7">

                                {% comment %}
                                 The fileinput-button span is used to style the file input field as button 
                                {% endcomment %}

                                {% block UPLOAD_FORM_BUTTON_BAR_ADD %}
                                <span class="btn btn-success fileinput-button">
                                    <i class="glyphicon glyphicon-plus"></i>
                                    <span>{% trans "Add files..." %}</span>


                                    {% block UPLOAD_FORM_BUTTON_BAR_ADD_FILE_INPUT %}
                                    {% comment %}
                                        UPLOAD_FORM_BUTTON_BAR_ADD_FILE_INPUT and FILE_INPUT
                                        control the same block. 

                                        FILE_INPUT is the original and shorter block name that has
                                        been kept to function as a convenient alias as well as to
                                        allow backward-compatibility with dependent projects. 

                                        Note: Only one should be overriden in the inheriting templates.
                                    {% endcomment %}
                                    {% block FILE_INPUT %}
                                    {% comment %}
                                        The file input for the upload form.
                                    {% endcomment %}
                                    <input 
                                        type="file" name="files[]" multiple

                                        {% if accepted_mime_types %}
                                            accept = '{{ accepted_mime_types|join:"," }}'
                                        {% endif %}
                                    >
                                    {% endblock %}
                                    {% endblock %}

                                </span>

                                {% block UPLOAD_FORM_BUTTON_BAR_ADD_EXTRA %}
                                {% endblock %}

                                {% endblock %}


                                {% block UPLOAD_FORM_BUTTON_BAR_CONTROL %}
                                <button type="submit" class="btn btn-primary start">
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
                                {% endblock %}

                                {% block UPLOAD_FORM_BUTTON_BAR_EXTRA %}
                                {% endblock %}

                            </div>

                            {% block UPLOAD_FORM_PROGRESS_BAR %}
                            {% comment %}
                             The global progress information 
                            {% endcomment %}
                            <div class="col-lg-5 fileupload-progress fade">
                                {% comment %}
                                 The global progress bar 
                                {% endcomment %}
                                <div 
                                    class="progress progress-striped active" 
                                    role="progressbar" 
                                    aria-valuemin="0" aria-valuemax="100"
                                >
                                    <div class="progress-bar progress-bar-success" style="width:0%;">
                                    </div>
                                </div>
                                {% comment %}
                                 The extended global progress information 
                                {% endcomment %}
                                <div class="progress-extended">&nbsp;</div>
                            </div>
                            {% endblock %}

                        </div>
                        {% endblock %}

                        {% comment %}
                         The loading indicator is shown during file processing 
                        {% endcomment %}

                        {% block UPLOAD_FORM_LINDICATOR %}
                        <div class="fileupload-loading"></div>
                        <br>
                        {% endblock %}

                        {% block UPLOAD_FORM_LISTING %}
                        {% comment %}
                         The table listing the files available for upload/download 
                        {% endcomment %}
                        <table role="presentation" class="table table-striped">
                            <tbody class="files"></tbody>
                        </table>
                        {% endblock %}

                """),
                
#                layout.HTML("""
#                
#                <div class="row fileupload-buttonbar">
#                
#                <button type="submit" class="btn btn-primary start"> <i class="glyphicon glyphicon-upload"></i> <span>start</span> </button>
#                
#                </div>
#                
#                """),
                
                #"image_path",
                #"delete_image",
            ),
#            bootstrap.FormActions(
#                layout.Submit('submit', _('Save'), css_class="btn btn-primary"),
#            )
        )