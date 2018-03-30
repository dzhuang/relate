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

import os

import django.forms as forms
from django.utils.translation import ugettext as _, string_concat
from django.template.loader import render_to_string
from django.db import transaction
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ObjectDoesNotExist

from relate.utils import StyledForm

from course.page.base import (
    PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback,
    PageBaseWithCorrectAnswer, HumanTextFeedbackForm,
    markup_to_html)
from course.utils import FlowPageContext
from course.constants import participation_status

from image_upload.models import UserImageStorage
from image_upload.models import FlowPageImage
from image_upload.utils import get_ordinal_from_page_context, \
    is_course_staff_participation, is_course_staff_course_image_request

from crispy_forms.layout import Layout, HTML

storage = UserImageStorage()

# {{{  mypy

if False:
    from typing import Any  # noqa
    from django import http  # noqa
    from course.utils import PageContext  # noqa

# }}}

# {{{ image upload question


class ImageUploadForm(StyledForm):
    show_save_button = False

    def __init__(self, page_context,
                 page_behavior, page_data, *args, **kwargs):
        require_image_for_submission = kwargs.pop(
            "require_image_for_submission", True)
        max_number_of_files = kwargs.pop("max_number_of_files", None)
        super(ImageUploadForm, self).__init__(*args, **kwargs)

        self.fields["hidden_answer"] = forms.CharField(
                required=False,
                widget=forms.TextInput(),
        )
        self.page_behavior = page_behavior
        self.page_context = page_context
        self.page_data = page_data
        self.require_image_for_submission = require_image_for_submission
        self.max_number_of_files = max_number_of_files

        jfu_button_control = ""

        if not self.page_behavior.may_change_answer:
            jfu_button_control = (
                ""
                "{% block UPLOAD_FORM_BUTTON_BAR %}{% endblock %}"
                "{% block UPLOAD_FORM_BUTTON_BAR_ADD %}{% endblock %}"
                "{% block UPLOAD_FORM_BUTTON_BAR_CONTROL %}{% endblock %}"
                "{% block UPLOAD_FORM_PROGRESS_BAR %}{% endblock %}"
                "{% block JS_UPLOAD_TEMPLATE_CONTROLS %}{% endblock %}"
                "{% block JS_DOWNLOAD_TEMPLATE_DELETE %}{% endblock %}"
            )

        self.helper.form_id = "fileupload"

        if not page_context.in_sandbox:
            self.helper.form_action = reverse(
                "jfu_upload",
                kwargs={'course_identifier': page_context.course,
                        'flow_session_id': page_context.flow_session.id,
                        'page_ordinal': get_ordinal_from_page_context(page_context)
                        }
            )
        else:
            self.helper.form_action = reverse(
                "jfu_upload",
                kwargs={'course_identifier': page_context.course}
            )
        self.helper.form_method = "POST"

        self.helper.layout = Layout(
            HTML(
                "{% extends 'image_upload/jfu-form.html' %}"
                + jfu_button_control
            ),
        )

    def clean(self):
        cleaned_data = super(ImageUploadForm, self).clean()
        pk_list_str = cleaned_data["hidden_answer"]

        if not pk_list_str:
            if self.require_image_for_submission:
                raise forms.ValidationError(
                    _("You have not upload image(s)!"))
            return cleaned_data

        try:
            pk_list = [int(i.strip()) for i in pk_list_str.split(",")]
        except ValueError:
            raise forms.ValidationError(
                string_concat(
                    _("The form data is broken. "),
                    _("please refresh the page and "
                      "redo the upload and submission.")
                ))

        user_image_pk_qs = (FlowPageImage.objects
            .filter(
                course=self.page_context.course,
                creator=self.page_context.flow_session.participation.user))

        user_image_pk_list = user_image_pk_qs.values_list("pk", flat=True)

        for i in pk_list:
            if i not in user_image_pk_list:

                # remove no-exist image objects
                try:
                    image_i = FlowPageImage.objects.get(pk=i)
                except ObjectDoesNotExist:
                    pk_list.pop(pk_list.index(i))
                    continue

                # remove image uploaded by participations not in the course
                from course.models import Participation
                creator_participations = (Participation.objects.filter(
                    user=image_i.creator,
                    course=self.page_context.course,
                    status=participation_status.active
                ))
                if not creator_participations.count():
                    pk_list.pop(pk_list.index(i))
                    continue

                # preserve images created by course staff
                # i.e., course staff is allowed to upload images to
                # the participations' flow page
                if is_course_staff_participation(creator_participations[0]):
                    continue

                raise forms.ValidationError(
                    string_concat(
                        _("There're some image(s) which don't belong "
                          "to this session. "),
                        _("Please make sure you are the owner of this "
                          "session and all images are uploaded by you. "),
                        _("please refresh the page and "
                          "redo the upload and submission.")
                    ))

        # validate file existance only for images uploaded by requested user
        # whether this visit or before
        saving_image_qs = user_image_pk_qs.filter(pk__in=pk_list)

        image_path_failed = []
        for img in saving_image_qs:
            if not os.path.isfile(img.image.path):
                image_path_failed.append(img)
                continue

        if image_path_failed:
            raise forms.ValidationError(
                string_concat(
                    _("Some of you uploaded images just failed "
                      "for unknown reasons"),
                    ": %s. " % ", ".join([img.slug for img in image_path_failed]),
                    _("please redo the upload and submission.")
                ))

        if (self.max_number_of_files is not None
                and len(pk_list) > self.max_number_of_files):
            raise forms.ValidationError(
                string_concat(
                    _("You are only allowed to upload %(allowed)i images,"
                      " got %(uploaded)i instead")
                    % {"allowed": self.max_number_of_files,
                       "uploaded": len(pk_list)}),
                )

        cleaned_data["hidden_answer"] = pk_list
        return cleaned_data


class ImgUploadHumanTextFeedbackForm(HumanTextFeedbackForm):
    show_save_button = False

    def __init__(self, *args, **kwargs):
        use_access_rules_tag = kwargs.pop("use_access_rules_tag", False)
        super(ImgUploadHumanTextFeedbackForm, self).__init__(*args, **kwargs)

        if use_access_rules_tag:
            self.fields["access_rules_tag"] = forms.CharField(
                required=False,
                help_text=_(
                    "Manually set the access_rules_tag of "
                    "the session, if necessary."),
                label=_('Access rules tag'))


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
            if not hasattr(page_desc, "value") and not self.is_optional_page:
                vctx.add_warning(location, _("upload question does not have "
                                             "assigned point value"))
        self.maxNumberOfFiles = getattr(page_desc, "maxNumberOfFiles", 1)

        self.imageMaxWidth = getattr(
            self.page_desc, "imageMaxWidth", 1000)
        if self.imageMaxWidth > 1500:
            self.imageMaxWidth = 1500
        elif self.imageMaxWidth < 200:
            self.imageMaxWidth = 400

        self.imageMaxHeight = getattr(
            self.page_desc, "imageMaxHeight", 1000)
        if self.imageMaxHeight > 1500:
            self.imageMaxHeight = 1500
        elif self.imageMaxHeight < 200:
            self.imageMaxHeight = 400

        self.maxFileSize = getattr(
            self.page_desc, "maxFileSize", 1) * 1024 ** 2
        if self.maxFileSize >= 2 * 1024 ** 2:
            self.maxFileSize = 1.5 * 1024 ** 2
        elif self.maxFileSize < 0.5 * 1024 ** 2:
            self.maxFileSize = 0.5 * 1024 ** 2

        # disable minFileSize
        self.minFileSize = getattr(
            self.page_desc, "minFileSize", 0.0005) * 1024 ** 2
        self.minFileSize = 0.0005 * 1024 ** 2

        self.use_access_rules_tag = getattr(
            self.page_desc, "use_access_rules_tag", False)

        self.require_image_for_submission = getattr(
            self.page_desc, "require_image_for_submission", True)

        #if self.minFileSize >= 0.05 * 1024 ** 2:
        #    self.minFileSize = 0.05 * 1024 ** 2

        # self.minFileSize = getattr(self.page_desc, "minFileSize", 0.03) * 1024 ** 2
        # if self.minFileSize >= 0.05 * 1024 ** 2:
        #     self.minFileSize = 0.05 * 1024 ** 2
        #
        # if self.minFileSize > self.maxFileSize:
        #     vctx.add_warning(location, _("minFileSize should not be greater than "
        #                                  "maxFileSize, better do not set those 2 "
        #                                  "attributes."
        #                                  ))

        self.previewMaxWidth = getattr(self.page_desc, "previewMaxWidth", 200)
        self.previewMaxHeight = getattr(self.page_desc, "previewMaxHeight", 200)

    def required_attrs(self):
        return super(ImageUploadQuestion, self).required_attrs() + (
            ("prompt", "markup"),
        )

    def allowed_attrs(self):
        return super(ImageUploadQuestion, self).allowed_attrs() + (
            ("correct_answer", "markup"),
            ("imageMaxWidth", (int, float)),
            ("imageMaxHeight", (int, float)),
            ("maxFileSize", (int, float)),
            ("minFileSize", (int, float)),
            ("previewMaxWidth", (int, float)),
            ("previewMaxHeight", (int, float)),
            ("maxNumberOfFiles", (int, float)),
            ("use_access_rules_tag", bool),
            ("require_image_for_submission", bool),
            ("answer_explanation", "markup"),
        )

    def human_feedback_point_value(self, page_context, page_data):
        return self.max_points(page_data)

    def markup_body_for_title(self):
        return self.page_desc.prompt

    def body(self, page_context, page_data):
        return (
            markup_to_html(page_context, self.page_desc.prompt)
            + string_concat(
                "<br/><p class='text-info'><strong><small>(",
                _("Note: Maxmum number of images: %d"),
                ")</small></strong></p>")
            % (self.maxNumberOfFiles,))

    def make_form(self, page_context, page_data,
                  answer_data, page_behavior):

        form = ImageUploadForm(
            page_context, page_behavior, page_data,
            require_image_for_submission=self.require_image_for_submission,
            max_number_of_files=self.maxNumberOfFiles
        )

        return form

    def process_form_post(self, page_context, page_data, post_data, files_data,
                          page_behavior):
        form = ImageUploadForm(
            page_context, page_behavior, page_data,
            post_data, files_data,
            require_image_for_submission=self.require_image_for_submission,
            max_number_of_files = self.maxNumberOfFiles
        )
        return form

    def form_to_html(self, request, page_context, form, answer_data):

        page_ordinal = None
        in_grading_page = False
        prev_visit_id = None

        if not page_context.in_sandbox:
            page_ordinal = get_ordinal_from_page_context(page_context)

            prev_visit_id = request.GET.get("visit_id", None)
            if prev_visit_id is not None:
                try:
                    prev_visit_id = int(prev_visit_id)
                except ValueError:
                    from django.core.exceptions import SuspiciousOperation
                    raise SuspiciousOperation("non-integer passed for 'visit_id'")

            from course.flow import get_prev_answer_visits_qset
            fpctx = FlowPageContext(
                repo=page_context.repo,
                course=page_context.course,
                flow_id=page_context.flow_session.flow_id,
                page_ordinal=int(page_ordinal),
                flow_session=page_context.flow_session,
                participation=page_context.flow_session.participation,
                request=request
            )

            prev_answer_visits = list(
                    get_prev_answer_visits_qset(fpctx.page_data))

            # {{{ fish out previous answer_visit

            if prev_answer_visits and prev_visit_id is not None:
                answer_visit = prev_answer_visits[0]

                for ivisit, pvisit in enumerate(prev_answer_visits):
                    if pvisit.id == prev_visit_id:
                        answer_visit = pvisit
                        break

                prev_visit_id = answer_visit.id

            elif prev_answer_visits:
                answer_visit = prev_answer_visits[0]
                prev_visit_id = answer_visit.id

            else:
                answer_visit = None

            # }}}

            if answer_visit is not None:
                answer_data = answer_visit.answer

            in_grading_page = False
            try:
                grading_page_uri = reverse(
                    "relate-grade_flow_page",
                    args=(
                        page_context.course.identifier,
                        page_context.flow_session.id,
                        page_ordinal)
                )

                in_grading_page = grading_page_uri == request.path
            except NoReverseMatch:
                if page_context.in_sandbox:
                    pass
                else:
                    raise

        ctx = {"form": form,
               "JQ_OPEN": '{%',
               'JQ_CLOSE': '%}',
               "accepted_mime_types":
                   ['image/jpeg', 'image/jpg', 'image/png'],
               'course_identifier': page_context.course,
               "flow_session_id": page_context.flow_session.id,
               "page_ordinal": page_ordinal,
               "IS_COURSE_STAFF":
                   is_course_staff_course_image_request(
                       request, page_context.course),
               "MAY_CHANGE_ANSWER": form.page_behavior.may_change_answer,
               "SHOW_CREATION_TIME": True,

               # This is not implemented
               # "ALLOW_ROTATE_TUNE": True,

               "IN_GRADE_PAGE": in_grading_page,

               "imageMaxWidth": self.imageMaxWidth,
               "imageMaxHeight": self.imageMaxHeight,
               "maxFileSize": self.maxFileSize,
               "minFileSize": self.minFileSize,
               "previewMaxWidth": self.previewMaxWidth,
               "previewMaxHeight": self.previewMaxHeight,
               "maxNumberOfFiles": self.maxNumberOfFiles
               }

        pk_list_str = None
        if answer_data:
            try:
                pk_list_str = answer_data.get("answer", None)
            except:
                pass

        if pk_list_str:
            ctx["pk_list_str"] = pk_list_str

        if prev_visit_id:
            ctx["prev_visit_id"] = prev_visit_id

        if page_context.in_sandbox:
            ctx["in_sandbox"] = True

        return render_to_string(
                "image_upload/imgupload-page-tmpl.html", ctx, request)

    def answer_data(self, page_context, page_data, form, files_data):
        answers = form.cleaned_data["hidden_answer"]

        # this is necessary when no images are submitted
        # for pages which do not require submission.
        if not answers:
            return None

        return {"answer": answers}

    def normalized_bytes_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None

        try:
            pk_list = answer_data.get("answer")
        except:
            return None

        if not len(pk_list):
            return None

        clauses = (
            ' '.join(['WHEN id=%s THEN %s' % (pk, i)
                      for i, pk in enumerate(pk_list)]))
        ordering = 'CASE %s END' % clauses
        image_qs = FlowPageImage.objects.filter(pk__in=pk_list).extra(
            select={'ordering': ordering}, order_by=('ordering',))

        if image_qs.exists():
            from image_upload.utils import InMemoryZip
            in_mem_zipfile = InMemoryZip()
            image_count = 0
            for i, img in enumerate(image_qs):
                if not os.path.isfile(img.image.path):
                    continue
                file_name, ext = os.path.splitext(str(img.image))

                try:
                    f = open(img.image.path, 'rb')
                except (IOError, OSError) as e:
                    continue

                f.seek(0)
                buf = img.image.read()
                f.close()
                in_mem_zipfile.append(str(i + 1) + ext, buf)
                image_count += 1

            if image_count:
                return (".zip", in_mem_zipfile.read())
            return None

        return None

    # def correct_answer(self, page_context, page_data, answer_data, grade_data):
    #     if answer_data is None:
    #         return None

    def make_grading_form(self, page_context, page_data, grade_data):
        human_feedback_point_value = self.human_feedback_point_value(
            page_context, page_data)
        access_rules_tag = page_context.flow_session.access_rules_tag
        form_data = {}
        if not self.use_access_rules_tag:
            use_access_rules_tag = False
        else:
            use_access_rules_tag = True
            form_data["access_rules_tag"] = access_rules_tag
        if grade_data is not None or access_rules_tag:
            form_data = {}
            if grade_data is not None:
                for k in self.grade_data_attrs:
                    form_data[k] = grade_data[k]
            if use_access_rules_tag:
                if access_rules_tag is not None:
                    form_data["access_rules_tag"] = access_rules_tag
            return ImgUploadHumanTextFeedbackForm(
                human_feedback_point_value, form_data,
                use_access_rules_tag=use_access_rules_tag)
        else:
            return ImgUploadHumanTextFeedbackForm(
                human_feedback_point_value,
                use_access_rules_tag=use_access_rules_tag)

    def post_grading_form(self, page_context, page_data, grade_data,
                          post_data, files_data):

        human_feedback_point_value = self.human_feedback_point_value(
            page_context, page_data)

        return ImgUploadHumanTextFeedbackForm(
                human_feedback_point_value, post_data,
                files_data, use_access_rules_tag=self.use_access_rules_tag)

    @transaction.atomic
    def update_grade_data_from_grading_form_v2(self, request, page_context,
            page_data, grade_data, grading_form, files_data):

        grade_data = (super(ImageUploadQuestion, self)
            .update_grade_data_from_grading_form_v2(
                request, page_context, page_data,
                grade_data, grading_form, files_data))

        if self.use_access_rules_tag:
            if (grading_form.cleaned_data["access_rules_tag"]
                    is not None and page_context.flow_session):
                if (not grading_form.cleaned_data["access_rules_tag"]
                        == page_context.flow_session.access_rules_tag):
                    the_flow_session = page_context.flow_session
                    the_flow_session.access_rules_tag = \
                        grading_form.cleaned_data["access_rules_tag"]
                    the_flow_session.save()

        return grade_data

# }}}

# vim: foldmethod=marker
