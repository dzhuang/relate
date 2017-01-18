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
from django.db import transaction
from django.contrib import messages

from image_upload.models import FlowPageImage

from course.page.base import (
    PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback,
    PageBaseWithCorrectAnswer, HumanTextFeedbackForm,
    markup_to_html)
from course.validation import ValidationError
from course.utils import course_view, render_course_page

from relate.utils import StyledForm

from crispy_forms.layout import Layout, HTML, Submit

import os


def is_course_staff_request(request, page_context):
    course = page_context.course
    from course.constants import participation_permission as pperm
    from course.enrollment import (
        get_participation_for_request,
        get_participation_permissions)

    participation = get_participation_for_request(request, course)

    perms = get_participation_permissions(course, participation)

    if (pperm.assign_grade, None) in perms:
        return True

    return False

# {{{ image upload question

class ImageUploadForm(StyledForm):
    show_save_button = False
    def __init__(self, page_context,
                 page_behavior, page_data, *args, **kwargs):
        require_image_for_submission = kwargs.pop("require_image_for_submission",True)
        super(ImageUploadForm, self).__init__(*args, **kwargs)

        self.page_behavior = page_behavior
        self.page_context = page_context
        self.page_data = page_data
        self.require_image_for_submission = require_image_for_submission

        jfu_button_control = ""

        if not self.page_behavior.may_change_answer:
            jfu_button_control = (
                # "{% block UPLOAD_FORM_BUTTON_BAR %}{% endblock %}"
                "{% block UPLOAD_FORM_BUTTON_BAR_ADD %}{% endblock %}"
                "{% block UPLOAD_FORM_BUTTON_BAR_CONTROL %}{% endblock %}"
                "{% block UPLOAD_FORM_PROGRESS_BAR %}{% endblock %}"
                "{% block JS_UPLOAD_TEMPLATE_CONTROLS %}{% endblock %}"
                "{% block JS_DOWNLOAD_TEMPLATE_DELETE %}{% endblock %}"
            )

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
        flow_owner = self.page_context.flow_session.participation.user

        if self.require_image_for_submission:
            from course.models import FlowPageData
            fpd = FlowPageData.objects.get(
                flow_session=flow_session_id, ordinal=ordinal)

            qs = FlowPageImage.objects.filter(
                creator=flow_owner
            ).filter(flow_session=flow_session_id
                     ).filter(image_page_id=fpd.page_id)

            qs_iter = qs.iterator()

            try:
                next(qs_iter)
            except StopIteration:
                raise forms.ValidationError(_("You have not upload image(s)!"))


class ImgUploadHumanTextFeedbackForm(HumanTextFeedbackForm):
    show_save_button = False
    def __init__(self, *args, **kwargs):
        use_access_rules_tag = kwargs.pop("use_access_rules_tag", False)
        super(ImgUploadHumanTextFeedbackForm, self).__init__(*args, **kwargs)

        if use_access_rules_tag:
            self.fields["access_rules_tag"] = forms.CharField(
                required=False,
                help_text=_("Manually set the access_rules_tag of the session, if necessary."),
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
            if not hasattr(page_desc, "value"):
                vctx.add_warning(location, _("upload question does not have "
                                             "assigned point value"))
        self.maxNumberOfFiles = getattr(page_desc, "maxNumberOfFiles", 1)

        self.imageMaxWidth = getattr(self.page_desc, "imageMaxWidth", 1000)
        if self.imageMaxWidth > 1500:
            self.imageMaxWidth = 1500
        elif self.imageMaxWidth < 200:
            self.imageMaxWidth = 400

        self.imageMaxHeight = getattr(self.page_desc, "imageMaxHeight", 1000)
        if self.imageMaxHeight > 1500:
            self.imageMaxHeight = 1500
        elif self.imageMaxHeight < 200:
            self.imageMaxHeight = 400

        self.maxFileSize = getattr(self.page_desc, "maxFileSize", 1) * 1024 ** 2
        if self.maxFileSize >= 2 * 1024 ** 2:
            self.maxFileSize = 1.5 * 1024 ** 2
        elif self.maxFileSize < 0.5 * 1024 ** 2:
            self.maxFileSize = 0.5 * 1024 ** 2

        # disable minFileSize
        self.minFileSize = getattr(self.page_desc, "minFileSize", 0.0005) * 1024 ** 2
        self.minFileSize = 0.0005 * 1024 ** 2

        self.use_access_rules_tag = getattr(self.page_desc, "use_access_rules_tag", False)

        self.require_image_for_submission = getattr(self.page_desc, "require_image_for_submission", True)

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
            + string_concat("<br/><p class='text-info'><strong><small>(", _("Note: Maxmum number of images: %d"),
                            ")</small></strong></p>") % (self.maxNumberOfFiles,))

    def make_form(self, page_context, page_data,
                  answer_data, page_behavior):

        form = ImageUploadForm(
            page_context, page_behavior, page_data,
            require_image_for_submission=self.require_image_for_submission)

        return form

    def process_form_post(self, page_context, page_data, post_data, files_data,
                          page_behavior):
        form = ImageUploadForm(
            page_context, page_behavior, page_data,
            post_data, files_data,
            require_image_for_submission=self.require_image_for_submission)

        return form

    def form_to_html(self, request, page_context, form, answer_data):

        request_path = request.get_full_path()

        in_grading_page = False

        from django.core.urlresolvers import NoReverseMatch
        from django.core.urlresolvers import reverse
        try:
            grading_page_uri = reverse(
                "relate-grade_flow_page",
                args=(
                    page_context.course.identifier,
                    page_context.flow_session.id,
                    page_context.ordinal)
            )

            in_grading_page = grading_page_uri == request_path
        except NoReverseMatch:
            if page_context.in_sandbox:
                pass
            else:
                raise

        ctx = {"form": form,
               "JQ_OPEN": '{%',
               'JQ_CLOSE': '%}',
               "accepted_mime_types": ['image/*'],
               'course_identifier': page_context.course,
               "flow_session_id": page_context.flow_session.id,
               "ordinal": page_context.ordinal,
               "IS_COURSE_STAFF": is_course_staff_request(request, page_context),
               "MAY_CHANGE_ANSWER": form.page_behavior.may_change_answer,
               "SHOW_CREATION_TIME": True,
               "ALLOW_ROTATE_TUNE": True,
               "IN_GRADE_PAGE": in_grading_page,

               "imageMaxWidth": self.imageMaxWidth,
               "imageMaxHeight": self.imageMaxHeight,
               "maxFileSize": self.maxFileSize,
               "minFileSize": self.minFileSize,
               "previewMaxWidth": self.previewMaxWidth,
               "previewMaxHeight": self.previewMaxHeight,
               "maxNumberOfFiles": self.maxNumberOfFiles
               }

        from django.template.loader import render_to_string
        return render_to_string(
                "image_upload/imgupload-page-tmpl.html", ctx, request)

    def answer_data(self, page_context, page_data, form, files_data):
        flow_session_id = page_context.flow_session.id
        ordinal = page_context.ordinal
        flow_owner = page_context.flow_session.participation.user
        from course.models import FlowPageData
        fpd = FlowPageData.objects.get(
            flow_session=flow_session_id, ordinal=ordinal)

        qs = FlowPageImage.objects\
            .filter(creator=flow_owner)\
            .filter(flow_session=flow_session_id)\
            .filter(image_page_id=fpd.page_id)

        if len(qs) > 0:
            import json
            return json.dumps(repr(qs))
        else:
            return None

    def normalized_bytes_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None

        flow_session_id = page_context.flow_session.id
        ordinal = page_context.ordinal
        flow_owner = page_context.flow_session.participation.user
        from course.models import FlowPageData
        fpd = FlowPageData.objects.get(
            flow_session=flow_session_id, ordinal=ordinal)

        image_qs = FlowPageImage.objects.filter(
            flow_session=flow_session_id,
            image_page_id=fpd.page_id).order_by("order")

        if image_qs.exists():
            from image_upload.utils import InMemoryZip
            in_mem_zipfile = InMemoryZip()
            for i, image in enumerate(image_qs):
                image_file = image.file
                if not os.path.isfile(image_file.path):
                    continue

                file_name, ext = os.path.splitext(image_file.path)

                thefile = open(image_file.path, 'rb')
                thefile.seek(0)
                buf = image_file.read()
                thefile.close()
                in_mem_zipfile.append(str(i+1) + ext, buf)

            return (".zip", in_mem_zipfile.read())

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
                human_feedback_point_value, form_data, use_access_rules_tag=use_access_rules_tag)
        else:
            return ImgUploadHumanTextFeedbackForm(
                human_feedback_point_value, use_access_rules_tag=use_access_rules_tag)

    def post_grading_form(self, page_context, page_data, grade_data,
                          post_data, files_data):

        human_feedback_point_value = self.human_feedback_point_value(
            page_context, page_data)

        return ImgUploadHumanTextFeedbackForm(
            human_feedback_point_value, post_data, files_data, use_access_rules_tag=self.use_access_rules_tag)

    @transaction.atomic
    def update_grade_data_from_grading_form_v2(
            self,
            request,  # type: http.HttpRequest
            page_context,  # type: PageContext
            page_data,  # type: Any
            grade_data,  # type: Any
            grading_form,  # type: Any
            files_data  # type: Any
            ):

        grade_data = super(ImageUploadQuestion,self).update_grade_data_from_grading_form_v2(
                request, page_context, page_data, grade_data, grading_form, files_data)

        if self.use_access_rules_tag:
            if grading_form.cleaned_data["access_rules_tag"] is not None and page_context.flow_session:
                if not grading_form.cleaned_data["access_rules_tag"] == page_context.flow_session.access_rules_tag:
                    the_flow_session = page_context.flow_session
                    the_flow_session.access_rules_tag = grading_form.cleaned_data["access_rules_tag"]
                    the_flow_session.save()

        return grade_data

# }}}


#{{{

class ImageUploadQuestionWithAnswer(ImageUploadQuestion):
    grading_sort_by_page_data = True

    def __init__(self, vctx, location, page_desc):
        super(ImageUploadQuestionWithAnswer, self).__init__(vctx, location, page_desc)
        self.refered_course_id = getattr(page_desc, "refered_course_id")
        self.refered_flow_id = getattr(page_desc, "refered_flow_id")
        self.refered_page_id = getattr(page_desc, "refered_page_id")

        self.exclude_parti_tag = getattr(page_desc, "exclude_parti_tag", None)
        self.exclude_username = getattr(page_desc, "exclude_username", None)
        self.exclude_session_tag = getattr(page_desc, "exclude_session_tag", None)
        self.include_session_tag = getattr(page_desc, "include_session_tag", None)
        self.attempt_included = getattr(page_desc, "attempt_included", "last")
        self.exclude_grade_percentage_lower_than = getattr(page_desc, "exclude_grade_percentage_lower_than", None)
        self.only_graded_pages = getattr(page_desc, "only_graded_pages", True)
        self.allow_report_correct_answer_false = getattr(page_desc,"allow_report_correct_answer_false", True)

        self.question_requirement = getattr(page_desc, "question_requirement", None)

        if self.attempt_included not in ["last", "first", "all"]:
            raise ValidationError(
                string_concat(
                    "%(location)s: ",
                    _("\"attempt_included\" must be one of "
                      "\"last\", \"first\", \"all\""))
                % {
                    'location': location})

        from course.models import FlowPageVisit
        from course.constants import participation_permission as pperm
        fpv_qs = FlowPageVisit.objects.filter(
            flow_session__course__identifier=self.refered_course_id,
            flow_session__flow_id=self.refered_flow_id,
            page_data__page_id=self.refered_page_id,
            is_submitted_answer=True,
            flow_session__in_progress=False, )\
            .exclude(
            # FIXME!!
            flow_session__participation__roles__permissions__permission=pperm.assign_grade
        )\
            .select_related("flow_session")\
            .select_related("flow_session__course")\
            .prefetch_related("flow_session__participation__roles__permissions")\
            .select_related("page_data")

        fpv_qs_iter = fpv_qs.iterator()
        try:
            next(fpv_qs_iter)
        except StopIteration:
            raise ValidationError(
                    _("no existing flow page visit found named \"%(refered_page_id)s\" "
                      "in flow \"%(refered_flow_id)s\" "
                      "in course \"%(refered_course_id)s\""
                      )
                    % {
                        'refered_course_id': self.refered_course_id,
                        'refered_flow_id':self.refered_flow_id,
                        'refered_page_id': self.refered_page_id})

        if self.exclude_parti_tag:
            for tag in self.exclude_parti_tag:
                parti_tag_qs = fpv_qs.filter(flow_session__participation__tags__name__in=self.exclude_parti_tag)
                if vctx is not None:
                    parti_tag_qs_iter = parti_tag_qs.iterator()
                    try:
                        next(parti_tag_qs_iter)
                    except StopIteration:
                        vctx.add_warning(location,
                            _("no participation tag named \"%(tag)s\" "
                              "in course \"%(refered_course_id)s\""
                              )
                            % {
                                'refered_course_id': self.refered_course_id,
                                'tag': tag,
                                         })
        if self.exclude_username:
            for name in self.exclude_username:
                username_qs = fpv_qs.filter(
                    flow_session__participation__user__username__exact=name)
                if vctx is not None:
                    username_qs_iter = username_qs.iterator()
                    try:
                        next(username_qs_iter)
                    except StopIteration:
                        vctx.add_warning(location,
                                         _("no user with username \"%(name)s\" submitted sessions "
                                           "in flow \"%(refered_flow_id)s\" "
                                           "in course \"%(refered_course_id)s\""
                                           )
                                         % {
                                             'refered_course_id': self.refered_course_id,
                                             'refered_flow_id': self.refered_flow_id,
                                             'name': name,
                                         })

        if self.exclude_session_tag:
            for session_tag in self.exclude_session_tag:
                stag_qs = fpv_qs.filter(
                    flow_session__access_rules_tag__exact=session_tag)
                if vctx is not None:
                    stag_qs_iter = stag_qs.iterator()
                    try:
                        next(stag_qs_iter)
                    except StopIteration:
                        vctx.add_warning(location,
                                         _("no flow session is taged \"%(session_tag)s\" is submitted "
                                           "in flow \"%(refered_flow_id)s\" "
                                           "in course \"%(refered_course_id)s\""
                                           )
                                         % {
                                             'refered_course_id': self.refered_course_id,
                                             'refered_flow_id': self.refered_flow_id,
                                             'session_tag': session_tag,
                                         })

        if self.include_session_tag:
            for session_tag in self.include_session_tag:
                stag_qs = fpv_qs.filter(
                    flow_session__access_rules_tag__exact=session_tag)
                if vctx is not None:
                    stag_qs_iter = stag_qs.iterator()
                    try:
                        next(stag_qs_iter)
                    except StopIteration:
                        vctx.add_warning(location,
                                         _("no flow session is taged \"%(session_tag)s\" is submitted "
                                           "in flow \"%(refered_flow_id)s\" "
                                           "in course \"%(refered_course_id)s\""
                                           )
                                         % {
                                             'refered_course_id': self.refered_course_id,
                                             'refered_flow_id': self.refered_flow_id,
                                             'session_tag': session_tag,
                                         })

        if self.exclude_grade_percentage_lower_than:
            try:
                grade_percentage = float(self.exclude_grade_percentage_lower_than)
                if grade_percentage > 1 or grade_percentage < 0:
                    vctx.add_warning(location,
                                     _("attribute \"exclude_grade_percentage_lower_than\" "
                                       "should between 0 and 1")
                                     )
            except Exception as e:
                raise ValidationError(
                      string_concat(
                          location,
                          ": %(err_type)s: %(err_str)s.")
                      % {
                          "err_type": type(e).__name__,
                          "err_str": str(e)}
                )

    def required_attrs(self):
        return super(ImageUploadQuestionWithAnswer, self).required_attrs() + (
            ("refered_course_id", str),
            ("refered_flow_id", str),
            ("refered_page_id", str),
        )

    def allowed_attrs(self):
        return super(ImageUploadQuestionWithAnswer, self).allowed_attrs() + (
            ("question_requirement", "markup"),
            ("attempt_included", str),
            ("exclude_parti_tag", (str, list)),
            ("exclude_username", (str, list)),
            ("exclude_session_tag", (str, list)),
            ("include_session_tag", (str, list)),
            ("exclude_grade_percentage_lower_than", (str, float)),
            ("only_graded_pages", bool),
        )

    def initialize_page_data(self, page_context):

        from course.models import FlowPageVisit
        from course.constants import participation_permission as pperm
        visits = (FlowPageVisit.objects
                  .filter(
            flow_session__course__identifier=self.refered_course_id,
            flow_session__flow_id=self.refered_flow_id,
            page_data__page_id=self.refered_page_id,
            is_submitted_answer=True,
            flow_session__in_progress=False,)
                  .exclude(
                    # FIXME!!
                    flow_session__participation__roles__permissions__permission=pperm.assign_grade
            ).select_related("flow_session")
                  .select_related("flow_session__course")
                  .prefetch_related("flow_session__participation__roles__permissions")
                  .select_related("page_data")

                  # We overwrite earlier submissions with later ones
                  # in a dictionary below.
                  .order_by("visit_time"))

        if self.exclude_parti_tag is not None:
            visits = visits.exclude(
                flow_session__participation__tags__name__in=self.exclude_parti_tag)

        if self.exclude_username is not None:
            visits = visits.exclude(
                flow_session__participation__user__username__in=self.exclude_username)

        if self.exclude_session_tag is not None:
            visits = visits.exclude(
                flow_session__access_rules_tag__in=self.exclude_session_tag)

        if self.include_session_tag is not None:
            visits = visits.filter(
                flow_session__access_rules_tag__in=self.include_session_tag)

        # visits that are not submitted and not im progress has been filtered
        if self.attempt_included == "first":
            visits = visits.order_by('flow_session__participation__user__username', 'visit_time')\
                .distinct('flow_session__participation__user__username')
        elif self.attempt_included == "last":
            visits = visits.order_by('flow_session__participation__user__username', '-visit_time')\
                .distinct('flow_session__participation__user__username')

        if visits.exists():
            import random
            import json

            page_id = None
            flow_session = None
            visits_list = list(visits)
            while len(visits_list) > 0:
                random.shuffle(visits_list)
                visit = visits_list[0]
                if self.only_graded_pages or self.exclude_grade_percentage_lower_than:
                    most_recent_grade = visit.get_most_recent_grade()
                    if (self.only_graded_pages and not most_recent_grade.correctness)\
                            or\
                            (self.exclude_grade_percentage_lower_than
                             and
                             most_recent_grade.correctness < float(self.exclude_grade_percentage_lower_than)):
                        visits_list.pop (0)
                        continue

                page_id = visit.page_data.page_id
                flow_session = visit.flow_session
                qs = FlowPageImage.objects.filter(flow_session=flow_session, image_page_id=page_id)

                if len(qs) > 1:
                    all_file_exist = True
                    for fpi in qs:
                        if not os.path.exists(fpi.file.path):
                            all_file_exist = False
                            break
                    if not all_file_exist:
                        visits_list.pop(0)
                        continue
                    else:
                        break
                else:
                    visits_list.pop(0)
            
            if len(visits_list) == 0:
                return {}

            if page_id and flow_session:
                return {"course": self.refered_course_id,
                        "flow_pk": flow_session.pk,
                        "page_id": page_id}
            else:
                return {}

        return {}

    def get_flowpageimage_qs(self, page_context, page_data, included_order_list=None, excluded_order_list=None):
        if included_order_list:
            assert isinstance(included_order_list, list)
        if excluded_order_list:
            assert isinstance(excluded_order_list, list)

        if page_context.in_sandbox or page_data is None:
            page_data = self.initialize_page_data(page_context)

        qs = FlowPageImage.objects.none()

        if page_data:
            try:
                flow_pk = page_data["flow_pk"]
                page_id = page_data["page_id"]
                qs = FlowPageImage.objects.filter(
                    flow_session__id=flow_pk, image_page_id=page_id)\
                    .order_by("order")
                if included_order_list:
                    qs.filter(order__in=included_order_list)
                if excluded_order_list:
                    qs.exlude(order__in=excluded_order_list)

                return qs
            except:
                pass

        return qs

    def get_question_img(self, page_context, page_data):
        qs = self.get_flowpageimage_qs(page_context, page_data, included_order_list=[0])

        if qs.exists():
            return qs[0]
        else:
            return None

    def body(self, page_context, page_data):
        body_html =  markup_to_html(page_context, self.page_desc.prompt)
        img = self.get_question_img(page_context, page_data)
        if img:
            if img.is_image_textify and img.image_text:
                img_text = img.image_text
                try:
                    body_html += markup_to_html(page_context, img_text)
                except:
                    pass
            else:
                question_img_url = img.get_absolute_url(private=False)

                body_html += (
                    '<div id="question_img">'
                    '<style> #question_img img {max-width:40vw;}</style>'
                    '<p>'
                    '<a href="%s" data-gallery="#question">'
                    '<img src="%s" onmouseover="magnify(this)" data-zoom-image="%s">'
                    '</a>'
                    '</p>'
                    '</div>' % (question_img_url, question_img_url, question_img_url)
                )

            if self.question_requirement:
                body_html += markup_to_html(page_context, self.question_requirement)

            body_html += string_concat("<br/><p class='text-info'><strong><small>"
                                     "(", _("Note: Maxmum number of images: %d"),
                                     ")</small></strong></p>")\
                       % (self.maxNumberOfFiles,)

        return body_html

    def form_to_html(self, request, page_context, form, answer_data):
        html = super(ImageUploadQuestionWithAnswer,self).form_to_html(request, page_context, form, answer_data)

        if is_course_staff_request(request, page_context):

            from image_upload.serialize import get_image_page_data_str, get_image_admin_url

            question_img = self.get_question_img(page_context,form.page_data)
            answer_qs = self.get_correct_answer_qs(page_context, form.page_data)

            first_row = ""
            second_row = ""

            full_qs_list = []

            if question_img:
                full_qs_list.append(question_img)
            if answer_qs:
                full_qs_list += list(answer_qs)

            if full_qs_list:
                for answer_img in full_qs_list:
                    i_thumbnail_url = answer_img.file_thumbnail.url
                    i_img_url = answer_img.get_absolute_url(private=False, key=True)
                    first_row += '<td><a href="%s" class="adminimage"><img src="%s"></a></td>' \
                                 % (i_img_url, i_thumbnail_url)

                    image_data_dict = get_image_page_data_str(answer_img)
                    imageAdminUrl = get_image_admin_url(answer_img)

                    second_row += '<td><a class="btn-data-copy" data-clipboard-text=\'%s\'>' \
                                  '<i class="fa fa-clipboard" aria-hidden="true"></i>' \
                                  '</a><a href="%s" target="_blank"><i class="fa fa-user"></i></a></td>' \
                                  % (image_data_dict, imageAdminUrl)

            js = """<script>
                document.getElementById('adminonly').onclick = function (event) {
                    event = event || window.event;
                    var target = event.target || event.srcElement,
                    link = target.src ? target.parentNode : target,
                    options = {index: link, event: event},
                    links = this.getElementsByClassName('adminimage');
                    blueimp.Gallery(links, options);
                    };
            </script>"""

            html += "<div><table>" + "<tr id='adminonly'>" + \
                   first_row + "</tr>" + "<tr>" + second_row + "</tr>" + "</table></div>" + js

        return html

    def get_correct_answer_qs(self,page_context, page_data):
        qs = self.get_flowpageimage_qs(page_context, page_data)
        answer_qs = FlowPageImage.objects.none()
        qs_iter = qs.iterator()
        try:
            # 如果题目图片使用了image_data，则用image_data
            img_0 = next(qs_iter)
            if img_0.use_image_data and img_0.image_data:
                try:
                    flow_pk = img_0.image_data["flow_pk"]
                    page_id = img_0.image_data["page_id"]
                    order_set = img_0.image_data["order_set"]
                    answer_qs = FlowPageImage.objects.filter(
                        flow_session__id=flow_pk, image_page_id=page_id,
                        order__in=order_set)
                except:
                    pass

            # 图片未关联到外部的图片（即答案，则使用order在1之后的所有图片
            # 作为答案.
            if not answer_qs:
                answer_qs = qs[1:]
        except StopIteration:
            pass

        return answer_qs

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        answer_qs = self.get_correct_answer_qs(page_context, page_data)
        ca = "\n"

        answer_qs_iter = answer_qs.iterator()

        try:
            first_image = next(answer_qs_iter)
            if first_image.is_image_textify and first_image.image_text:
                try:
                    ca += markup_to_html(page_context, first_image.image_text)
                except:
                    pass
            else:
                for answer in answer_qs:
                    key_img_url = answer.get_absolute_url(private=False, key=True)
                    ca = ca + ('<a href="%s">'
                               '<img src="%s" onmouseover="magnify(this)" data-zoom-image="%s">'
                               '</a>\n'
                               % (key_img_url, key_img_url, key_img_url))

                js = """<br/><script>
                        document.getElementById('key').onclick = function (event) {
                            event = event || window.event;
                            var target = event.target || event.srcElement,
                            link = target.src ? target.parentNode : target,
                            options = {index: link, event: event},
                            links = this.getElementsByTagName('a');
                            blueimp.Gallery(links, options);
                            };
                    </script>"""
                ca += js
        except StopIteration:
            pass

        if hasattr(self.page_desc, "answer_explanation"):
            ca += markup_to_html(page_context, self.page_desc.answer_explanation)

        student_feedback = ""
        if self.allow_report_correct_answer_false:

            from django.core.urlresolvers import reverse
            email_page_url = reverse(
                "feedBackEmail",
                kwargs={'course_identifier': page_context.course.identifier,
                        'flow_session_id': page_context.flow_session.id,
                        'ordinal': page_context.ordinal
                        }
            )
            feedbackbutton = (
                "<a href='%(url)s'"
                "class='btn btn-primary btn-xs relate-btn-xs-vert-spaced'>"
                "%(send_email)s </a>"
                % {"url": email_page_url, "send_email": _("Send Email")})

            student_feedback_message = (
                string_concat(_("Find the given correct answer wrong? Please feel easy to "
                                "contact the instructor(s) "))
            )

            student_feedback_message += feedbackbutton
            student_feedback = "<br/> <div style='float:right'>%s </div>"  % student_feedback_message

        CA_PATTERN = string_concat (_ ("A correct answer is"),
                                    ": <br/> <div id='key'>"
                                    "<style> #key img {max-width:40vw;}</style> %s</div> %s")  # noqa

        return CA_PATTERN % (ca, student_feedback)


@course_view
def feedBackEmail(pctx, flow_session_id, ordinal):
    from django.shortcuts import get_object_or_404, redirect

    request = pctx.request
    if request.method == "POST":
        form = ImgUPloadAnswerEmailFeedbackForm(request.POST)

        if form.is_valid():
            from django.utils import translation
            from django.conf import settings
            from course.models import Participation
            from course.models import FlowSession

            flow_session = get_object_or_404(FlowSession, id=int(flow_session_id))
            from course.models import FlowPageData
            page_id = FlowPageData.objects.get(flow_session=flow_session_id, ordinal=ordinal).page_id
            from course.constants import participation_permission as pperm
            tutor_qs = Participation.objects.filter(
                    course=pctx.course,
                    # FIXME!!
                    participations__roles__permissions__permission=pperm.assign_grade
            )
            tutor_email_list = [tutor.user.email for tutor in tutor_qs]

            from django.core.urlresolvers import reverse
            review_url = reverse(
                "relate-view_flow_page",
                kwargs={'course_identifier': pctx.course.identifier,
                        'flow_session_id': flow_session_id,
                        'ordinal': ordinal
                        }
            )

            from six.moves.urllib.parse import urljoin
            review_uri = urljoin(getattr(settings, "RELATE_BASE_URL"),
                                 review_url)

            from_email = getattr(settings, "STUDENT_FEEDBACK_FROM_EMAIL", settings.SERVER_EMAIL)
            student_email = flow_session.participation.user.email

            with translation.override(settings.RELATE_ADMIN_EMAIL_LOCALE):
                from django.template.loader import render_to_string
                message = render_to_string("image_upload/report-correct-answer-error-email.txt", {
                    "page_id": page_id,
                    "flow_session_id": flow_session_id,
                    "course": pctx.course,
                    "feedback_text": form.cleaned_data["feedback"],
                    "review_uri": review_uri,
                    "username": pctx.participation.user.get_full_name()
                })

                from django.core.mail import EmailMessage
                msg = EmailMessage(
                    subject=string_concat("[%(identifier)s:%(flow_id)s--%(page_id)s] ",
                                          _("Feedback from %(username)s"))
                            % {'identifier': pctx.course_identifier,
                               'flow_id': flow_session_id,
                               'page_id': page_id,
                               'username': pctx.participation.user.get_full_name()
                               },
                    body=message,
                    from_email=from_email,
                    to=tutor_email_list,
                )
                msg.bcc = [student_email]
                msg.reply_to = [student_email]

                from relate.utils import get_outbound_mail_connection
                msg.connection = get_outbound_mail_connection("student_feedback")
                msg.send()

                messages.add_message(
                    request, messages.SUCCESS,
                    _("Thank you for your feedback, and notice that you will "
                      "also receive a copy of the email."))
            return redirect("relate-view_flow_page", pctx.course.identifier,flow_session_id, ordinal)

    else:
        form = ImgUPloadAnswerEmailFeedbackForm()

    return render_course_page(pctx, "course/generic-course-form.html", {
         "form": form,
         "form_description": _("Send feedback email"),
     })

#}}}


class ImgUPloadAnswerEmailFeedbackForm(StyledForm):
    def __init__(self, *args, **kwargs):
        super(ImgUPloadAnswerEmailFeedbackForm, self).__init__(*args, **kwargs)
        self.fields["feedback"] = forms.CharField(
                required=True,
                widget=forms.Textarea,
                help_text=_("Please input directly your feedback messages <strong>(no email appelation and welcome is required)</strong>. If you are proved to be right, you'll "
                  "get bonus for the contribution."),
                label=_("Feedback"))
        self.helper.add_input(
            Submit(
                "submit", _("Send Email"),
                css_class="relate-submit-button"))

    def clean_feedback(self):
        cleaned_data = super(ImgUPloadAnswerEmailFeedbackForm, self).clean()
        feedback = cleaned_data.get("feedback")
        if len(feedback) < 20:
            raise forms.ValidationError(_("At least 20 characters are required for submission."))
        return feedback

# vim: foldmethod=marker
