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

from django.shortcuts import get_object_or_404
from django import forms, http
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import (
        CreateView, DeleteView, ListView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _, string_concat, ugettext
from django.db import transaction

from course.models import Course, FlowPageData, Participation
from course.constants import participation_role
from course.utils import course_view

from image_upload.serialize import serialize
from image_upload.utils import get_page_image_behavior, ImageOperationMixin
from image_upload.models import FlowPageImage

from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest
from braces.views import JSONResponseMixin
import json
from PIL import Image

def is_course_staff(pctx):
    request = pctx.request
    course = pctx.course
    from course.constants import participation_role
    from course.auth import get_role_and_participation
    role, participation = get_role_and_participation(request, course)
    if role in [participation_role.teaching_assistant,
            participation_role.instructor]:
        return True
    else:
        return False

class ImageCreateView(LoginRequiredMixin, ImageOperationMixin, JSONResponseMixin, CreateView):
    # Prevent download Json response in IE 7-10
    # http://stackoverflow.com/a/13944206/3437454
    content_type = 'text/plain'
    model = FlowPageImage
    fields = ("file", "slug")

    def form_valid(self, form):
        file = form.cleaned_data.get('file')
        from django.conf import settings

        max_allowed_jfu_size = getattr(
			settings, "RELATE_JFU_MAX_IMAGE_SIZE", 2) * 1024**2

        if file._size > max_allowed_jfu_size:
            file_data = {
                    "files": [{
                        "name": form.cleaned_data.get('slug'),
                        "size": file._size,
                        "error": ugettext(
                            "The file is too big. Please use "
                            "Chrome/Firefox or mobile browser by "
                            "which images will be cropped "
                            "automatically before upload.")
                        },]
                    }

            return self.render_json_response(file_data)

        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()

        course_identifier = self.kwargs["course_identifier"]
        course = get_object_or_404(Course, identifier=course_identifier)
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]

        fpd=FlowPageData.objects.get(
            flow_session=flow_session_id, ordinal=ordinal)
        self.object.flow_session_id = flow_session_id
        self.object.image_page_id = fpd.page_id
        self.object.course = course
        try:
            last_order = self.model.objects\
                .filter(flow_session=flow_session_id)\
                .filter(image_page_id=fpd.page_id)\
                .order_by('-order')[0].order
            self.object.order = last_order + 1
        except IndexError:
            pass
        self.object.save()

        files = [serialize(self.request, self.object, 'file')]
        data = {'files': files}
        return self.render_json_response(data)

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return self.render_json_response(data, status=400)

class ImageItemForm(forms.ModelForm):
    class Meta:
        model = FlowPageImage
        fields = ("file",)


class ImageDeleteView(LoginRequiredMixin, ImageOperationMixin, DeleteView):
    model = FlowPageImage

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.creator:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_("may not delete other people's image"))
        else:
            self.object.delete()
            response = http.JsonResponse(True, safe=False)
            response['Content-Disposition'] = 'inline; filename=files.json'
            response['Content-Type'] = 'text/plain'
            return response


class ImageListView(LoginRequiredMixin, JSONResponseMixin, ListView):
    # Prevent download Json response in IE 7-10
    # http://stackoverflow.com/a/13944206/3437454):
    model = FlowPageImage

    def get_queryset(self):
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]
        fpd = FlowPageData.objects.get(
                flow_session=flow_session_id, ordinal=ordinal)

        return FlowPageImage.objects\
                .filter(flow_session=flow_session_id)\
                .filter(image_page_id=fpd.page_id)\
                .order_by("order","pk")

    def render_to_response(self, context, **response_kwargs):
        files = [serialize(self.request, p, 'file')
                for p in self.get_queryset()]
        data = {'files': files}
        return self.render_json_response(data)

# }}}


# {{{ sendfile
from sendfile import sendfile

@login_required
def user_image_download(request, creator_id, download_id):
    # refer to the following method to allow staff download
    download_object = get_object_or_404(Image, pk=download_id)
    return _auth_download(request, download_object)

@login_required
@course_view
def flow_page_image_download(pctx, flow_session_id, creator_id, 
                             download_id, file_name):
    request = pctx.request
    download_object = get_object_or_404(FlowPageImage, pk=download_id)
    
    privilege = False
    # whether the user is allowed to view the private image
    participation = Participation.objects.get(
        course=pctx.course, user=request.user)
    if (
        participation.role in (
            [participation_role.instructor,
             participation_role.teaching_assistant,
             participation_role.auditor])
        or request.user.is_staff):
        privilege = True
    
    return _auth_download(request, download_object, privilege)

@login_required
def _auth_download(request, download_object, privilege=False):
    if not (
        request.user==download_object.creator or privilege):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(_("may not view other people's resource"))
    return sendfile(request, download_object.file.path)

# }}}


# {{{ crop image

class CropImageError(BadRequest):
    pass


@login_required
@course_view
def image_crop_modal(pctx, flow_session_id, ordinal, pk):
    request = pctx.request
    try:
        file = FlowPageImage.objects.get(id=pk)
    except FlowPageImage.DoesNotExist:
        raise CropImageError(
            string_concat(_('File not found.'),
                          _('Please upload the image first.')))
    course_staff_status = is_course_staff(pctx)
    staff_edit_warnning = False
    if (
        course_staff_status
        and
        request.user != file.creator
        ):
        staff_edit_warnning = True
    return render(
            request,
            'image_upload/cropper-modal.html',
            {'file': file,
             'STAFF_EDIT_WARNNING': staff_edit_warnning,
             'owner': file.creator
            })

@json_view
@login_required
@transaction.atomic
@course_view
def image_crop(pctx, flow_session_id, ordinal, pk):
    page_image_behavior = get_page_image_behavior(pctx, flow_session_id, ordinal)
    may_change_answer = page_image_behavior.may_change_answer

    course_staff_status = is_course_staff(pctx)
    request = pctx.request

    if not (may_change_answer or course_staff_status):
        raise CropImageError(_('Not allowd to modify answer.'))
    try:
        crop_instance = FlowPageImage.objects.get(pk=pk)
    except FlowPageImage.DoesNotExist:
        raise CropImageError(_('Please upload the image first.'))

    image_orig_path = crop_instance.file.path
    if not image_orig_path:
        raise CropImageError(
            string_concat(_('File not found.'),
                          _('Please upload the image first.')))

    image_modified_path = crop_instance.get_random_filename()
    
    if not request.is_ajax():
        raise CropImageError(_('Only Ajax Post is allowed.'))

    try:
        x = int(float(request.POST['x']))
        y = int(float(request.POST['y']))
        width = int(float(request.POST['width']))
        height = int(float(request.POST['height']))
        rotate = int(float(request.POST['rotate']))
    except:
        raise CropImageError(_('There are errors, please refresh the page or try again later'))

    try:
        image_orig = Image.open(image_orig_path)
    except IOError:
        raise CropImageError(_('There are errors，please re-upload the image'))

    image_orig = image_orig.rotate(-rotate, expand=True)
    box =  (x, y, x+width, y+height)
    image_orig = image_orig.crop(box)

    try:
        image_orig.save(image_modified_path)
    except IOError:
        raise CropImageError(_('There are errors, please refresh the page or try again later'))

    from relate.utils import as_local_time, local_now
    import datetime

    if not course_staff_status:
        if local_now() < as_local_time(
                crop_instance.creation_time + datetime.timedelta(minutes=5)):
            crop_instance.file_last_modified = crop_instance.creation_time = local_now()

        else:
            crop_instance.file_last_modified = local_now()

    crop_instance.file = image_modified_path
    crop_instance.save()

    try:
        import os
        os.remove(image_orig_path)
    except:
        pass

    new_instance = FlowPageImage.objects.get(id=pk)

    response_file = serialize(request, new_instance, 'file')

    data = {'file': response_file}
    return data

# }}}


class ImgTableOrderError(BadRequest):
    pass

@json_view
@login_required
@transaction.atomic
@course_view
def image_order(pctx, flow_session_id, ordinal):
    page_image_behavior = get_page_image_behavior(pctx, flow_session_id, ordinal)
    may_change_answer = page_image_behavior.may_change_answer
    course_staff_status = is_course_staff(pctx)
    if not (may_change_answer or course_staff_status):
        raise ImgTableOrderError(_('Not allowd to modify answer.'))
    request = pctx.request
    if not request.is_ajax():
        raise ImgTableOrderError(_('Only Ajax Post is allowed.'))

    chg_data_list = json.loads(request.POST['chg_data'])

    for chg_data in chg_data_list:
        try:
            chg_instance = FlowPageImage.objects.get(pk=chg_data['pk'])
        except FlowPageImage.DoesNotExist:
            raise ImgTableOrderError(_('Please upload the image first.'))
        try:
            chg_instance.order = chg_data['new_ord']
            chg_instance.save()
        except:
            raise ImgTableOrderError(_('There are errors, please refresh the page or try again later'))

    response = {'message': ugettext('Done')}

    #raise ImgTableOrderError("Failed")
    
    return response
