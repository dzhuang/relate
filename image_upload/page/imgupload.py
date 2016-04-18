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
from django.db.models import Q

from image_upload.models import FlowPageImage

from course.page.base import (
    PageBaseWithTitle, PageBaseWithValue, PageBaseWithHumanTextFeedback,
    PageBaseWithCorrectAnswer,
    markup_to_html)
from course.models import FlowPageData, FlowSession, FlowPageVisit
from course.validation import ValidationError

from relate.utils import StyledForm

from crispy_forms.layout import Layout, HTML


# {{{ image upload question

class ImageUploadForm(StyledForm):
    def __init__(self, page_context,
                 page_behavior, page_data, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)

        self.page_behavior = page_behavior
        self.page_context = page_context

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
        user = self.page_context.flow_session.user
        fpd = FlowPageData.objects.get(
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

        self.minFileSize = getattr(self.page_desc, "minFileSize", 0.03) * 1024 ** 2
        if self.minFileSize >= 0.05 * 1024 ** 2:
            self.minFileSize = 0.05 * 1024 ** 2

        if self.minFileSize > self.maxFileSize:
            vctx.add_warning(location, _("minFileSize should not be greater than "
                                         "maxFileSize, better do not set those 2 "
                                         "attributes."
                                         ))
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

    def is_course_staff(self, request, page_context):
        user = request.user
        course = page_context.course
        from course.constants import participation_role
        from course.auth import get_role_and_participation
        role, participation = get_role_and_participation(request, course)
        if role in [participation_role.teaching_assistant,
                    participation_role.instructor]:
            return True
        return False

    def make_form(self, page_context, page_data,
                  answer_data, page_behavior):

        form = ImageUploadForm(
            page_context, page_behavior, page_data)

        return form

    def process_form_post(self, page_context, page_data, post_data, files_data,
                          page_behavior):
        form = ImageUploadForm(
            page_context, page_behavior, page_data,
            post_data, files_data)

        return form

    def form_to_html(self, request, page_context, form, answer_data):
        IS_COURSE_STAFF = (
            self.is_course_staff(request, page_context)
            or
            form.page_behavior.may_change_answer)

        ctx = {"form": form,
               "JQ_OPEN": '{%',
               'JQ_CLOSE': '%}',
               "accepted_mime_types": ['image/*'],
               'course_identifier': page_context.course,
               "flow_session_id": page_context.flow_session.id,
               "ordinal": page_context.ordinal,
               "IS_COURSE_STAFF": IS_COURSE_STAFF,
               "SHOW_CREATION_TIME": True,
               "ALLOW_ROTATE_TUNE": True,

               "imageMaxWidth": self.imageMaxWidth,
               "imageMaxHeight": self.imageMaxHeight,
               "maxFileSize": self.maxFileSize,
               "minFileSize": self.minFileSize,
               "previewMaxWidth": self.previewMaxWidth,
               "previewMaxHeight": self.previewMaxHeight,
               "maxNumberOfFiles": self.maxNumberOfFiles
               }

        from django.template import RequestContext, loader
        from django import VERSION as DJANGO_VERSION
        if DJANGO_VERSION >= (1, 9):
            return loader.render_to_string(
                "image_upload/imgupload-page-tmpl.html",
                context=ctx,
                request=request)
        else:
            context = RequestContext(request)
            context.update({"form": form})
            return loader.render_to_string(
                "image_upload/imgupload-page-tmpl.html",
                RequestContext(request, ctx))

    def answer_data(self, page_context, page_data, form, files_data):
        flow_session_id = page_context.flow_session.id
        ordinal = page_context.ordinal
        user = page_context.flow_session.user
        fpd = FlowPageData.objects.get(
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


#{{{

class ImageUploadQuestionWithAnswer(ImageUploadQuestion):

    # def __init__(self, vctx, location, page_desc):
    #     super(ImageUploadQuestionWithAnswer, self).__init__(vctx, location, page_desc)
    #     self.refered_course_id = getattr(self.page_desc, "refered_course_id")
    #     self.refered_page_id = getattr(self.page_desc, "refered_page_id")
    #     self.excluded_parti_TAG = getattr(self.page_desc, "excluded_parti_TAG", None)


    # def required_attrs(self):
    #     return super(ImageUploadQuestionWithAnswer, self).required_attrs() + (
    #         ("refered_course_id", str),
    #         ("refered_page_id", str)
    #     )
    #
    # def allowed_attrs(self):
    #     return super(ImageUploadQuestionWithAnswer, self).allowed_attrs() + (
    #         ("excluded_parti_TAG", (list, str)),
    #     )

    def make_page_data(self):
        #import random

        # perm = list(range(len(self.page_desc.choices)))
        # if getattr(self.page_desc, "shuffle", False):
        #     random.shuffle(perm)
        #
        # return {"flowpage_img": perm}

        exclude_parti_tag = ["Foreign"]

        exclude_username = ["Miss.Chen"]

        attempts_included = "last"

        refered_course_id = "Graduate-ORI-16"
        refered_flow_id = "design-assignmment1-lpmodel"
        refered_page_id = "designLPModel1"

        # qs_flow = FlowSession.objects.filter(
        #      course__identifier=refered_course_id, flow_id=refered_flow_id
        #  )
        #
        # print("========================")
        # print(refered_page_id)
        # print("========================")
        # # fpd = FlowPageData.objects.filter(
        # #     flow_session__course__identifier=refered_course_id, page_id=refered_page_id
        # # )
        # # print len(fpd)
        # #
        # # try_page = fpd[0]
        # # print(dir(try_page))
        # fpi = FlowPageImage.objects.filter()

        # from course.utils import PageInstanceCache
        # page_cache = PageInstanceCache(pctx.repo, pctx.course, flow_id)

        visits = (FlowPageVisit.objects
                  .filter(
            flow_session__course__identifier=refered_course_id,
            flow_session__flow_id=refered_flow_id,
            page_data__page_id=refered_page_id,
            is_submitted_answer=True,
            flow_session__in_progress=False,
        )
                  .select_related("flow_session")
                  .select_related("flow_session__participation__user")
                  .select_related("page_data")

                  # We overwrite earlier submissions with later ones
                  # in a dictionary below.
                  .order_by("visit_time"))

        if exclude_parti_tag is not None:
            visits = visits.exclude(
                flow_session__participation__tags__name__in=exclude_parti_tag)

        if exclude_username is not None:
            visits = visits.exclude(
                flow_session__participation__user__username__in=exclude_username)

        if attempts_included == "first":
            visits = visits.order_by('flow_session__participation__user__username', 'visit_time').distinct('flow_session__participation__user__username')
        elif attempts_included == "last":
            visits = visits.order_by('flow_session__participation__user__username', '-visit_time').distinct('flow_session__participation__user__username')

        if len(visits) > 0:
            import random
            import json
            while True:
                visits_list = list(visits)
                #print len(visits_list)
                random.shuffle(visits_list)
                #print visit.visit_time, visit.answer

                answer = json.loads(visits_list[0].answer)
                pid = visits_list[0].page_data.page_id
                fs = visits_list[0].flow_session
                print pid, fs
                print answer

                qs = FlowPageImage.objects.filter(flow_session=fs, image_page_id=pid)

                if len(qs) > 0:
                    break

        print qs[0].file
        print qs[1].file
        page_data = '{"question": [%(question)s], "answers": [%(answers)s]}' % {
            "question": qs[0].file.path,
            "answers": ", ".join([a.file.path for a in qs[1:]])
        }
        print json.dumps(page_data)



                    #
        # print(len(visits))
        # for visit in visits:
        #     print visit.visit_time
 #           print visit.answer
    def body(self, page_context, page_data):
        answerdata1, answerdata2 = make_page_data()
        return (
            markup_to_html(page_context, self.page_desc.prompt)
            + string_concat("<br/><p class='text-info'><strong><small>"
                            "(", _("Note: Maxmum number of images: %d"),
                            ")</small></strong></p>") % (self.maxNumberOfFiles,)
            + "<p><img src=\""  + answerdata1 + "\"></p>"
            + "<p><img src=\"" + answerdata2 + "\"></p>"

        )
    #
    #
    #
    # def correct_answer(self, page_context, page_data, answer_data, grade_data):
    #     if hasattr(self.page_desc, "answer_comment"):
    #         return markup_to_html(page_context, self.page_desc.answer_comment)
    #     else:
    #         return None
#}}}


def make_page_data():
    exclude_parti_tag = ["Foreign"]

    exclude_username = ["Miss.Chen"]

    attempts_included = "last"

    refered_course_id = "Graduate-ORI-16"
    refered_flow_id = "design-assignmment1-lpmodel"
    refered_page_id = "designLPModel1"

    # qs_flow = FlowSession.objects.filter(
    #      course__identifier=refered_course_id, flow_id=refered_flow_id
    #  )
    #
    # print("========================")
    # print(refered_page_id)
    # print("========================")
    # # fpd = FlowPageData.objects.filter(
    # #     flow_session__course__identifier=refered_course_id, page_id=refered_page_id
    # # )
    # # print len(fpd)
    # #
    # # try_page = fpd[0]
    # # print(dir(try_page))
    # fpi = FlowPageImage.objects.filter()

    # from course.utils import PageInstanceCache
    # page_cache = PageInstanceCache(pctx.repo, pctx.course, flow_id)

    visits = (FlowPageVisit.objects
              .filter(
        flow_session__course__identifier=refered_course_id,
        flow_session__flow_id=refered_flow_id,
        page_data__page_id=refered_page_id,
        is_submitted_answer=True,
        flow_session__in_progress=False,
    )
              .select_related("flow_session")
              .select_related("flow_session__participation__user")
              .select_related("page_data")

              # We overwrite earlier submissions with later ones
              # in a dictionary below.
              .order_by("visit_time"))

    if exclude_parti_tag is not None:
        visits = visits.exclude(
            flow_session__participation__tags__name__in=exclude_parti_tag)

    if exclude_username is not None:
        visits = visits.exclude(
            flow_session__participation__user__username__in=exclude_username)

    if attempts_included == "first":
        visits = visits.order_by('flow_session__participation__user__username', 'visit_time').distinct(
            'flow_session__participation__user__username')
    elif attempts_included == "last":
        visits = visits.order_by('flow_session__participation__user__username', '-visit_time').distinct(
            'flow_session__participation__user__username')

    if len(visits) > 0:
        import random
        import json
        while True:
            visits_list = list(visits)
            # print len(visits_list)
            random.shuffle(visits_list)
            # print visit.visit_time, visit.answer

            answer = json.loads(visits_list[0].answer)
            pid = visits_list[0].page_data.page_id
            fs = visits_list[0].flow_session
            print pid, fs
            print answer

            qs = FlowPageImage.objects.filter(flow_session=fs, image_page_id=pid)

            if len(qs) > 0:
                break

    print qs[0].file
    print qs[1].file
    page_data = '{"question": [%(question)s], "answers": [%(answers)s]}' % {
        "question": qs[0].file.path,
        "answers": ", ".join([a.file.path for a in qs[1:]])
    }

    return qs[0].get_absolute_url(), qs[1].get_absolute_url()
    #return json.dumps(page_data)

# vim: foldmethod=marker
