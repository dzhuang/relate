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
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.utils.translation import ugettext_lazy as _
from django.db import transaction

import json

from PIL import Image as IMG
from braces.views import LoginRequiredMixin

from course.models import Course, FlowPageData
from course.flow import (
        get_page_behavior, get_and_check_flow_session,
        get_prev_answer_visits_qset)
from course.utils import (
        FlowPageContext, get_session_access_rule,
        get_session_grading_rule)
          
from course.views import get_now_or_fake_time

from image_upload.serialize import serialize
from image_upload.models import UserImage, FlowPageImage


def get_image_behavor(pctx, flow_session_id, ordinal):

    request = pctx.request

    ordinal = int(ordinal)

    flow_session_id = int(flow_session_id)
    flow_session = get_and_check_flow_session(pctx, flow_session_id)
    flow_id = flow_session.flow_id

    fpctx = FlowPageContext(pctx.repo, pctx.course, flow_id, ordinal,
            participation=pctx.participation,
            flow_session=flow_session,
            request=pctx.request)

    now_datetime = get_now_or_fake_time(request)
    access_rule = get_session_access_rule(
            flow_session, pctx.role, fpctx.flow_desc, now_datetime,
            facilities=pctx.request.relate_facilities)

    grading_rule = get_session_grading_rule(
            flow_session, pctx.role, fpctx.flow_desc, now_datetime)
    generates_grade = (
            grading_rule.grade_identifier is not None
            and
            grading_rule.generates_grade)

    #del grading_rule

    permissions = fpctx.page.get_modified_permissions_for_page(
            access_rule.permissions)

    answer_visit = None
    prev_visit_id = None

    prev_answer_visits = list(
            get_prev_answer_visits_qset(fpctx.page_data))

    # {{{ fish out previous answer_visit

    prev_visit_id = pctx.request.GET.get("visit_id")
    if prev_visit_id is not None:
        prev_visit_id = int(prev_visit_id)

    viewing_prior_version = False
    if prev_answer_visits and prev_visit_id is not None:
        answer_visit = prev_answer_visits[0]

        for ivisit, pvisit in enumerate(prev_answer_visits):
            if pvisit.id == prev_visit_id:
                answer_visit = pvisit
                if ivisit > 0:
                    viewing_prior_version = True

                break

        prev_visit_id = answer_visit.id

    elif prev_answer_visits:
        answer_visit = prev_answer_visits[0]
        prev_visit_id = answer_visit.id

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
            is_unenrolled_session=flow_session.participation is None,
            viewing_prior_version=viewing_prior_version)

    return page_behavior

class ImageCreateView(LoginRequiredMixin, CreateView):
    model = FlowPageImage
    fields = ("file", "slug")

    def form_valid(self, form):
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
        self.object.save()

        files = [serialize(self.request, self.object, 'file')]
        data = {'files': files}
        response = http.JsonResponse(data)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return http.HttpResponse(
                content=data, 
                status=400, 
                content_type='application/json')

class ImageItemForm(forms.ModelForm):
    class Meta:
        model = FlowPageImage
        fields = ("file",)

class ImageUpdateView(UpdateView):
    pass
#    model = FlowPageImage
#    form_class = ImageItemForm
#    template_name = 'image_upload/image_edit_form.html'
#
#    def dispatch(self, *args, **kwargs):
#        self.pk = kwargs['pk']
#        print "self", self
#        return super(ImageUpdateView, self).dispatch(*args, **kwargs)
#
    def form_valid(self, form):
        pass
#        form.save()
#        file = FlowPageImage.objects.get(id=self.pk)
#        print file.pk
#        from django.template.loader import render_to_string
#        return http.HttpResponse(render_to_string('image_upload/image_edit_form_success.html', {'file': file}))

class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = FlowPageImage

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = http.JsonResponse(True, safe=False)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class ImageListView(LoginRequiredMixin, ListView):
    model = FlowPageImage

    def get_queryset(self):
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]
        fpd = FlowPageData.objects.get(
                flow_session=flow_session_id, ordinal=ordinal)

        return FlowPageImage.objects\
                .filter(creator=self.request.user)\
                .filter(flow_session=flow_session_id)\
                .filter(image_page_id=fpd.page_id)

    def render_to_response(self, context, **response_kwargs):
        
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]
        
        files = [
                serialize(self.request, p, 'file')
                for p in self.get_queryset()]
        data = {'files': files}
        response = http.JsonResponse(data)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

# }}}


# {{{ sendfile
from sendfile import sendfile

@login_required
def user_image_download(request, creator_id, download_id):
    download_object = get_object_or_404(Image, pk=download_id)
    return _auth_download(request, download_object)

@login_required
def flow_page_image_download(request, creator_id, download_id):
    download_object = get_object_or_404(FlowPageImage, pk=download_id)
    return _auth_download(request, download_object)

@login_required
def _auth_download(request, download_object):
    if not (
        request.user==download_object.creator or request.user.is_staff):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(_("may not view other people's resource"))
    return sendfile(request, download_object.file.path)

# }}}


# {{{ crop image

class CropImageError(Exception):
    pass

from course.utils import course_view


@login_required
@course_view
def image_crop_modal(pctx, flow_session_id, ordinal, pk):
    request = pctx.request
    file = FlowPageImage.objects.get(id=pk)
    return render(request, 'image_upload/cropper-modal.html', {'file': file})

@login_required
@transaction.atomic
@course_view
def image_crop(pctx, flow_session_id, ordinal, pk):
    page_behavior = get_image_behavor(pctx, flow_session_id, ordinal)
    may_change_answer = page_behavior.may_change_answer
    if not may_change_answer:
        raise CropImageError(_('Not allowd to modify answer!'))
    request = pctx.request
    from django.conf import settings
    try:
        crop_instance = FlowPageImage.objects.get(pk=pk)
    except FlowPageImage.DoesNotExist:
        raise CropImageError('请先上传图片')

    image_orig_path = crop_instance.file.path
    if not image_orig_path:
        raise CropImageError('File not found, 请先上传图片')

    image_modified_path = crop_instance.get_random_filename()
    
    if request.is_ajax():

        try:
            x = int(float(request.POST['x']))
            y = int(float(request.POST['y']))
            width = int(float(request.POST['width']))
            height = int(float(request.POST['height']))
            rotate = int(float(request.POST['rotate']))
        except:
            raise CropImageError('发生错误，稍后再试')

        try:
            image_orig = IMG.open(image_orig_path)
        except IOError:
            raise CropImageError('发生错误，请重新上传图片')

        image_orig = image_orig.rotate(-rotate, expand=True)
        box =  (x, y, x+width, y+height)
        image_orig = image_orig.crop(box)

        try:
            image_orig.save(image_modified_path)
        except IOError:
            raise CropImageError('发生错误，稍后再试')

        from relate.utils import local_now
        crop_instance.file = image_modified_path
        crop_instance.file_last_modified = local_now()
        crop_instance.save()

        try:
            import os
            os.remove(image_orig_path)
        except:
            pass

        new_instance = FlowPageImage.objects.get(id=pk)

        response = None
        response_file = serialize(request, new_instance, 'file')

        data = {'file': response_file}
        response = http.JsonResponse(data)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    
    else:
        raise CropImageError(_('Only Ajax Post is allowed.'))

# }}}
