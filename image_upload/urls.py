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

from django.conf.urls import patterns, url
from django.views.i18n import javascript_catalog

from image_upload.views import (
    ImageCreateView, ImageUpdateView, ImageDeleteView, ImageListView,
    image_crop_modal, image_crop,
    image_download)

js_info_dict_image_upload = {
    'packages': ('image_upload',),
}

js_info_dict_other_app = {
    'packages': ('your.other.app.package',),
}

urlpatterns = [
    
    url(r'^jsi18n/other_app/$', javascript_catalog, js_info_dict_other_app),
]

urlpatterns = [
    url(r"^user"
        "/flow-session"
        "/(?P<flow_session_id>[0-9]+)"
        "/(?P<ordinal>[0-9]+)"
        "/image/upload/$",
        ImageCreateView.as_view(),
        name='jfu_upload'),

    url(r"^user"
        "/image/update"
        "/(?P<pk>\d+)$",
        image_crop_modal,
        name='jfu_update'),

    url(r"^user"
        "/image"
        "/(?P<pk>\d+)$",
        ImageDeleteView.as_view(), 
        name='jfu_delete'),

    url(r"^user"
        "/flow-session"
        "/(?P<flow_session_id>[0-9]+)"
        "/(?P<ordinal>[0-9]+)"
        "/image/view/$",
        ImageListView.as_view(),
        name='jfu_view'),

    url(r"^course"
        "/userfiles"
        "/(?P<creator_id>\d+)"
        "/(?P<download_id>\d+)/$",
        image_download,
        name='image_download'),

    url(r"^user"
        "/image/crop"
        "/(?P<pk>\d+)$",
        image_crop,
        name='image_crop'),
    
    url(r"^jsi18n"
        "/image_upload/$",
        javascript_catalog,
        js_info_dict_image_upload,
        name='javascript-catalog-image-upload'),
    
    ]
