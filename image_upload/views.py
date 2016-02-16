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
from django import http
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.utils.translation import ugettext_lazy as _
from course.models import FlowPageData
from image_upload.serialize import serialize
from image_upload.models import Image, SessionPageImage
from PIL import Image as IMG
from django.db import transaction

import json

class ImageCreateView(CreateView):
    model = SessionPageImage
    fields = ("file", "slug")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()

        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]

        fpd=FlowPageData.objects.get(
            flow_session=flow_session_id, ordinal=ordinal)
        self.object.flow_session_id = flow_session_id
        self.object.image_page_id = fpd.page_id
        self.object.save()

        files = [serialize(self.request, self.object, 'file', flow_session_id, ordinal)]
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


import django.forms as forms
class ImageItemForm(forms.ModelForm):
    class Meta:
        model = SessionPageImage
        fields = ("file",)

class ImageUpdateView(UpdateView):
    model = SessionPageImage
    form_class = ImageItemForm
    template_name = 'image_upload/image_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.pk = kwargs['pk']
        print "self", self
        return super(ImageUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        file = SessionPageImage.objects.get(id=self.pk)
        print file.pk
        from django.template.loader import render_to_string
        return http.HttpResponse(render_to_string('image_upload/image_edit_form_success.html', {'file': file}))

def image_crop_modal(request, pk):
    file = SessionPageImage.objects.get(id=pk)
    #from django.template.loader import render_to_string
    return render(request, 'image_upload/cropper_modal.html', {'file': file})


class ImageDeleteView(DeleteView):
    model = SessionPageImage

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = http.JsonResponse(True, safe=False)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class ImageListView(ListView):
    model = SessionPageImage

    def get_queryset(self):
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]
        fpd = FlowPageData.objects.get(
                flow_session=flow_session_id, ordinal=ordinal)

        return SessionPageImage.objects\
                .filter(creator=self.request.user)\
                .filter(flow_session=flow_session_id)\
                .filter(image_page_id=fpd.page_id)

    def render_to_response(self, context, **response_kwargs):
        
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]
        
        files = [
                serialize(self.request, p, 'file', flow_session_id, ordinal)
                for p in self.get_queryset()]
        data = {'files': files}
        response = http.JsonResponse(data)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

# }}}


# {{{ sendfile
from sendfile import sendfile

@login_required
def image_download(request, creator_id, download_id):
    download_object = get_object_or_404(Image, pk=download_id)
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

@transaction.atomic
@login_required
def image_crop(request, pk):
    from django.conf import settings
    try:
        crop_img = SessionPageImage.objects.get(pk=pk)
    except SessionPageImage.DoesNotExist:
        raise CropImageError('请先上传图片')

    image_orig = crop_img.file.path
    image_modified = crop_img.get_random_filename()
    print image_modified
    if not image_orig:
        raise CropImageError('File not found, 请先上传图片')
        
    print request.POST

    try:
        x = int(float(request.POST['x']))
        y = int(float(request.POST['y']))
        width = int(float(request.POST['width']))
        height = int(float(request.POST['height']))
        rotate = int(float(request.POST['rotate']))
#        scaleX = int(float(request.POST['scalex']))
#        scaleY = int(float(request.POST['scaley']))
    except:
        raise CropImageError('发生错误，稍后再试')
#        
    print x, y, width, height, rotate
#
#
    try:
        orig = IMG.open(image_orig)
    except IOError:
        raise CropImageError('发生错误，请重新上传图片')
    
    orig=orig.rotate(rotate)
    try:
        orig.save(image_modified)
    except IOError:
        print image_orig
        print image_modified
        raise CropImageError('发生错误，稍后再试')

    from relate.utils import local_now
    crop_img.file = image_modified
    crop_img.file_last_modified = local_now()
    crop_img.save()
    
    try:
        import os
        os.remove(image_orig)
    except:
        pass
    
#
#    orig_w, orig_h = orig.size
#    if orig_w <= border_size and orig_h <= border_size:
#        ratio = 1
#    else:
#        if orig_w > orig_h:
#            ratio = float(orig_w) / border_size
#        else:
#            ratio = float(orig_h) / border_size
#
#    box = [int(x * ratio) for x in [x1, y1, x2, y2]]
#    avatar = orig.crop(box)
#    avatar_name, _ = os.path.splitext(crop_img.image)
#
#
#    size = AVATAR_RESIZE_SIZE
#    try:
#        res = avatar.resize((size, size), Image.ANTIALIAS)
#        res_name = '%s-%d.%s' % (avatar_name, size, AVATAR_SAVE_FORMAT)
#        res_path = os.path.join(AVATAR_DIR, res_name)
#        res.save(res_path, AVATAR_SAVE_FORMAT, quality=AVATAR_SAVE_QUALITY)
#    except:
#        raise CropImageError('发生错误，请稍后重试')
#
#
#    avatar_crop_done.send(sender = None,
#                          uid = get_uid(request),
#                          avatar_name = res_name,
#                          dispatch_uid = 'siteuser_avatar_crop_done'
#                          )
#
    return http.HttpResponse(
        "<script>window.parent.crop_success('%s')</script>"  % '成功'
    )

# }}}