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
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DeleteView, ListView
from django.utils.translation import ugettext_lazy as _
from course.models import FlowPageData
from image_upload.serialize import serialize
from image_upload.models import Image, SessionPageImage

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

        files = [serialize(self.object, 'file', flow_session_id, ordinal)]
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
                serialize(p, 'file', flow_session_id, ordinal)
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
