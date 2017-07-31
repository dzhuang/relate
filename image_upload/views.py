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
from django.shortcuts import get_object_or_404
from django.conf import settings
from django import forms, http
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.views.generic import (
        CreateView, DeleteView, ListView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import ugettext_lazy as _, string_concat, ugettext
from django.db import transaction

from course.utils import course_view, FlowPageContext, get_session_access_rule, \
    get_session_grading_rule, CoursePageContext
from course.constants import participation_permission as pperm

from image_upload.serialize import serialize
from image_upload.models import FlowPageImage, UserImageStorage

from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest
from braces.views import JSONResponseMixin
import json
from PIL import Image
from io import BytesIO
from sendfile import sendfile

storage = UserImageStorage()

# Define the permssion required for course staff to edit/upload/delete
# images uploaded by participants
COURSE_STAFF_IMAGE_PERMISSION = (
    (pperm.assign_grade, None),
)


def is_course_staff_participation(participation):
    if not participation:
        return False

    from course.enrollment import (
        get_participation_permissions)
    perms = get_participation_permissions(
        participation.course, participation)

    if all(perm in perms for perm in COURSE_STAFF_IMAGE_PERMISSION):
        return True

    return False


def is_course_staff_course_image_request(request, course):
    from course.enrollment import get_participation_for_request
    participation = get_participation_for_request(request, course)
    return is_course_staff_participation(participation)


class ImageOperationMixin(UserPassesTestMixin):
    # Mixin for determin if user can upload/delete/edit image
    raise_exception = True

    def test_func(self):
        from course.models import Course
        course_identifier = self.kwargs['course_identifier']
        course = Course.objects.get(identifier=course_identifier)
        if course:
            if is_course_staff_course_image_request(self.request, course):
                return True

        request = self.request
        flow_session_id = self.kwargs['flow_session_id']
        ordinal = self.kwargs['ordinal']

        pctx = CoursePageContext(request, course_identifier)

        try:
            return get_page_image_behavior(
                pctx, flow_session_id, ordinal).may_change_answer
        except ValueError:
            return True


class ImageCreateView(LoginRequiredMixin, ImageOperationMixin,
                      JSONResponseMixin, CreateView):
    # Prevent download Json response in IE 7-10
    # http://stackoverflow.com/a/13944206/3437454
    content_type = 'text/plain'
    model = FlowPageImage
    fields = ("image", "slug")

    def form_valid(self, form):
        image = form.cleaned_data.get('image')
        max_allowed_jfu_size = getattr(
            settings, "RELATE_JFU_MAX_IMAGE_SIZE", 2) * 1024**2

        if image._size > max_allowed_jfu_size:
            file_data = {
                    "files": [{
                        "name": form.cleaned_data.get('slug'),
                        "size": image._size,
                        "error": ugettext(
                            "The image is too big. Please use "
                            "Chrome/Firefox or mobile browser by "
                            "which images will be cropped "
                            "automatically before upload.")
                        },
                    ]}

            return self.render_json_response(file_data)

        self.object = form.save(commit=False)
        self.object.is_temp_image = True
        self.object.creator = self.request.user

        course_identifier = self.kwargs["course_identifier"]

        from course.models import Course
        course = get_object_or_404(Course, identifier=course_identifier)
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]

        from course.models import FlowPageData
        fpd = FlowPageData.objects.get(flow_session=flow_session_id, ordinal=ordinal)
        self.object.flow_session_id = flow_session_id
        self.object.image_page_id = fpd.page_id
        self.object.course = course
        self.object.save()

        try:
            files = [serialize(self.request, self.object, 'image')]
            data = {'files': files}
        except IOError:
            return self.render_json_response(
                {"success": False,
                 "error": ugettext(
                     "Sorry, the image is corrupted during "
                     "handling. That should be solved by "
                     "a re-uploading.")})

        return self.render_json_response(data)

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return self.render_json_response(data, status=400)


class ImageItemForm(forms.ModelForm):
    class Meta:
        model = FlowPageImage
        fields = ("image",)


class ImageDeleteView(LoginRequiredMixin, ImageOperationMixin, DeleteView):
    model = FlowPageImage

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user == self.object.creator:
            may_delete = True
        elif self.request.user == self.object.flow_session.participation.user:
            may_delete = True
        else:
            may_delete = False

            # Course staff may delete user images
            if is_course_staff_course_image_request(
                    self.request, self.object.course):
                may_delete = True
            else:
                # User may delete image uploaded by course staff
                if (self.object.flow_session.id == self.kwargs['flow_session_id']
                    and
                        is_course_staff_participation(self.object.participation)):
                    may_delete = True

        if not may_delete:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_("may not delete other people's image"))
        else:
            if self.object.is_in_temp_storage():
                self.object.delete()
                response = http.JsonResponse(True, safe=False)
            else:
                response = http.JsonResponse(False, safe=False)

            response['Content-Disposition'] = 'inline; filename=files.json'
            response['Content-Type'] = 'text/plain'
            return response


class ImageListView(LoginRequiredMixin, JSONResponseMixin, ListView):
    # Prevent download Json response in IE 7-10
    # http://stackoverflow.com/a/13944206/3437454):
    model = FlowPageImage

    def get_queryset(self):
        flow_session_id = self.kwargs["flow_session_id"]

        from course.models import FlowSession
        try:
            flow_session = get_object_or_404(FlowSession, id=int(flow_session_id))
        except ValueError:
            # in sandbox
            return None
        ordinal = self.kwargs["ordinal"]
        course_identifier = self.kwargs["course_identifier"]
        from course.utils import CoursePageContext
        pctx = CoursePageContext(self.request, course_identifier)
        prev_visit_id = self.request.GET.get("visit_id")

        if prev_visit_id is not None:
            try:
                prev_visit_id = int(prev_visit_id)
            except ValueError:
                from django.core.exceptions import SuspiciousOperation
                raise SuspiciousOperation("non-integer passed for 'visit_id'")
        from course.utils import FlowPageContext
        from course.flow import get_prev_answer_visits_qset
        fpctx = FlowPageContext(
            repo=pctx.repo,
            course=pctx.course,
            flow_id=flow_session.flow_id,
            ordinal=int(ordinal),
            flow_session=flow_session,
            participation=flow_session.participation,
            request=self.request
        )

        prev_answer_visits = list(
                get_prev_answer_visits_qset(fpctx.page_data))

        # {{{ fish out previous answer_visit

        if prev_answer_visits and prev_visit_id is not None:
            answer_visit = prev_answer_visits[0]

            for pvisit in prev_answer_visits:
                if pvisit.id == prev_visit_id:
                    answer_visit = pvisit
                    break

        elif prev_answer_visits:
            answer_visit = prev_answer_visits[0]

        else:
            answer_visit = None

        # }}}

        if not answer_visit:
            return None

        answer_data = answer_visit.answer

        if not answer_data:
            return None

        if not isinstance(answer_data, dict):
            return None

        pk_list = answer_data.get("answer", None)
        if not pk_list:
            return None

        # Creating a QuerySet from a list while preserving order using Django
        # https://codybonney.com/creating-a-queryset-from-a-list-while-preserving-order-using-django/
        clauses = (
            ' '.join(['WHEN id=%s THEN %s' % (pk, i)
                      for i, pk in enumerate(pk_list)]))
        ordering = 'CASE %s END' % clauses
        queryset = FlowPageImage.objects.filter(pk__in=pk_list).extra(
            select={'ordering': ordering}, order_by=('ordering',))

        return queryset

    def render_to_response(self, context, **response_kwargs):
        queryset = self.get_queryset()
        if queryset:
            files = [serialize(self.request, p, 'image')
                    for p in self.get_queryset()]
            data = {'files': files}
        else:
            data = {}
        return self.render_json_response(data)

# }}}


# {{{ sendfile


@login_required
@course_view
def flow_page_image_download(pctx, flow_session_id, creator_id,
                             download_id, file_name):
    request = pctx.request
    download_object = get_object_or_404(FlowPageImage, pk=download_id)

    privilege = False

    # whether the user is allowed to view the private image
    # First, course staff are allow to view participants image.
    if is_course_staff_course_image_request(pctx.request, pctx.course):
        privilege = True

    # Participants are allowed to view images in their pages, even uploaded
    # by course staffs
    elif pctx.request.user == download_object.flow_session.participation.user:
        return sendfile(request, download_object.image.path)

    return _auth_download(request, download_object, privilege)


@login_required
def _auth_download(request, download_object, privilege=False):
    if (not request.user == download_object.creator
        and
            not request.user.is_staff
        or
            not privilege):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(_("may not view other people's resource"))

    return sendfile(request, download_object.image.path)


@login_required
def _non_auth_download(request, download_object):
    if (not request.user == download_object.creator
        and
            not request.user.is_staff):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(_("may not view other people's resource"))

    from sendfile.backends.development import sendfile
    return sendfile(request, download_object.image.path)

# }}}


# {{{ crop image

class CropImageError(BadRequest):
    pass


@json_view
@login_required
@transaction.atomic
@course_view
def image_crop(pctx, flow_session_id, ordinal, pk):
    try:
        page_image_behavior = get_page_image_behavior(
            pctx, flow_session_id, ordinal)
        may_change_answer = page_image_behavior.may_change_answer
    except ValueError:
        may_change_answer = True

    course_staff_status = (
        is_course_staff_course_image_request(pctx.request, pctx.course))
    request = pctx.request

    if not (may_change_answer or course_staff_status):
        raise CropImageError(ugettext('Not allowd to modify answer.'))
    try:
        crop_instance = FlowPageImage.objects.get(pk=pk)
    except FlowPageImage.DoesNotExist:
        raise CropImageError(ugettext('Please upload the image first.'))

    image_orig_path = crop_instance.image.path
    if not image_orig_path:
        raise CropImageError(
            string_concat(ugettext('File not found.'),
                          ugettext('Please upload the image first.')))

    if not request.POST:
        return {}

    if not request.is_ajax():
        raise CropImageError(ugettext('Only Ajax Post is allowed.'))

    json_data = json.loads(request.body.decode("utf-8"))

    try:
        x = int(float(json_data['x']))
        y = int(float(json_data['y']))
        width = int(float(json_data['width']))
        height = int(float(json_data['height']))
        rotate = int(float(json_data['rotate']))
    except KeyError:
        raise CropImageError(
            ugettext('There are errors, please refresh the page '
              'or try again later'))

    try:
        new_image = Image.open(image_orig_path)
    except IOError:
        raise CropImageError(
            ugettext('There are errors，please re-upload the image'))
    image_format = new_image.format

    if rotate != 0:
        # or it will raise "AttributeError: 'NoneType' object has no attribute
        # 'mode' error in pillow 3.3.0
        new_image = new_image.rotate(-rotate, expand=True)

    box = (x, y, x+width, y+height)
    new_image = new_image.crop(box)

    if new_image.mode != "RGB":
        new_image = new_image.convert("RGB")

    new_image_io = BytesIO()
    new_image.save(new_image_io, format=image_format)

    new_instance = crop_instance
    new_instance.pk = None
    new_instance.creator = request.user

    new_instance.is_temp_image = True
    new_instance.image.save(
        name=get_sendfile_storage_available_name(crop_instance),
        content=ContentFile(new_image_io.getvalue()),
        save=False
    )

    new_image_last_modified = crop_instance.creation_time

    from relate.utils import as_local_time, local_now
    import datetime
    if local_now() > as_local_time(
                    crop_instance.creation_time
                    + datetime.timedelta(minutes=5)):
        new_image_last_modified = local_now()
    new_instance.file_last_modified = new_image_last_modified

    # the other attribute of the new image doen't have to be the same
    # with the original one.
    if (crop_instance.course != pctx.course
        or
                int(crop_instance.flow_session_id) != int(flow_session_id)):
        from course.models import FlowPageData
        fpd = FlowPageData.objects.get(flow_session=flow_session_id, ordinal=ordinal)
        new_instance.flow_session_id = flow_session_id
        new_instance.image_page_id = fpd.page_id
        new_instance.course = pctx.course
        new_instance.creation_time = local_now()
        new_instance.file_last_modified = local_now()

    try:
        new_instance.save()
    except (OSError, IOError) as e:
        raise BadRequest(string_concat(
            ugettext("Error"), ": ",
            ugettext('There are errors, please refresh the page or try again later'),
            "--%s:%s." % (type(e).__name__, str(e))
        ))
    finally:
        new_image.close()

    try:
        response_file = serialize(request, new_instance, 'image')
    except IOError:
        raise BadRequest(string_concat(
            ugettext("Error"), ": ",
            ugettext("Sorry, the image is corrupted during "
              "handling. That should be solved by "
              "a re-uploading."))
        )
    data = {'message': ugettext('Done!'), 'file': response_file}
    return data

# }}}


class ImgTableOrderError(BadRequest):
    pass


def get_page_image_behavior(pctx, flow_session_id, ordinal):
    if ordinal == "None" and flow_session_id == "None":
        from course.page.base import PageBehavior
        return PageBehavior(
            show_correctness=True,
            show_answer=True,
            may_change_answer=True,
        )

    from course.flow import (
        get_page_behavior, get_and_check_flow_session,
        get_prev_answer_visits_qset)

    request = pctx.request

    ordinal = int(ordinal)

    flow_session_id = int(flow_session_id)
    flow_session = get_and_check_flow_session(pctx, flow_session_id)
    flow_id = flow_session.flow_id

    fpctx = FlowPageContext(pctx.repo, pctx.course, flow_id, ordinal,
            participation=pctx.participation,
            flow_session=flow_session,
            request=pctx.request)

    from course.views import get_now_or_fake_time

    now_datetime = get_now_or_fake_time(request)
    access_rule = get_session_access_rule(
            flow_session, fpctx.flow_desc, now_datetime,
            facilities=pctx.request.relate_facilities)

    grading_rule = get_session_grading_rule(
            flow_session, fpctx.flow_desc, now_datetime)
    generates_grade = (
            grading_rule.grade_identifier is not None
            and
            grading_rule.generates_grade)

    del grading_rule

    permissions = fpctx.page.get_modified_permissions_for_page(
            access_rule.permissions)

    prev_answer_visits = list(
            get_prev_answer_visits_qset(fpctx.page_data))

    # {{{ fish out previous answer_visit

    prev_visit_id = pctx.request.GET.get("visit_id")
    if prev_visit_id is not None:
        prev_visit_id = int(prev_visit_id)

    if prev_answer_visits and prev_visit_id is not None:
        answer_visit = prev_answer_visits[0]

        for ivisit, pvisit in enumerate(prev_answer_visits):
            if pvisit.id == prev_visit_id:
                answer_visit = pvisit
                break

    elif prev_answer_visits:
        answer_visit = prev_answer_visits[0]

    else:
        answer_visit = None

    # }}}

    if answer_visit is not None:
        answer_was_graded = answer_visit.is_submitted_answer
    else:
        answer_was_graded = False

    page_behavior = get_page_behavior(
            page=fpctx.page,
            permissions=permissions,
            session_in_progress=flow_session.in_progress,
            answer_was_graded=answer_was_graded,
            generates_grade=generates_grade,
            is_unenrolled_session=flow_session.participation is None)

    return page_behavior


def get_sendfile_storage_available_name(img):
    # this is used by django-imagekit to generate
    # new name when /temp dir is empty, avoiding use name
    # already in use
    original_source_name = (
        img.image.name
        .replace(os.path.basename(img.image.name), img.slug)
        .replace("\\", "/")
        .replace("/temp/", "/"))
    new_name = storage.get_available_name(original_source_name)
    return os.path.split(new_name)[-1]
