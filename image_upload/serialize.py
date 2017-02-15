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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from course.views import get_now_or_fake_time
from relate.utils import (
    as_local_time, format_datetime_local,
    compact_local_datetime_str)

from datetime import timedelta
import mimetypes
import re
import os
import json

from image_upload.models import FlowPageImage

def order_name(name):
    """order_name
    -- Limit a text to 20 chars length, if necessary strips the middle
       of the text and substitute it for an ellipsis.

    name -- text to be limited.
    """
    name = os.path.basename(name)
    [name, ext] = os.path.splitext(name)
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 25:
        return name
    return name[:15] + "..." + name[-7:]

def get_image_page_data_str(image):
    if not isinstance(image, FlowPageImage):
        return None
    if image.flow_session.in_progress:
        return None

    image_data_dict = {
        'flow_pk': image.flow_session.id,
        'page_id': image.image_page_id,
        'order_set': list((image.order,)),
    }

    return str(json.dumps(image_data_dict).encode("utf-8"))

def get_image_admin_url(image):
    if not isinstance(image, FlowPageImage):
        return None
    if image.flow_session.in_progress:
        return None
    return reverse('admin:image_upload_flowpageimage_change', args=(image.pk,))

def serialize(request, instance, file_attr='file'):
    """serialize -- Serialize a Picture instance into a dict.

    instance -- Image instance
    file_attr -- attribute name that contains the FileField or ImageField

    """

    obj = getattr(instance, file_attr)

    error = None

    try:
        IsFile = os.path.isfile(obj.path)
        size = obj.size
        obj_name = obj.name
        img_type = mimetypes.guess_type(obj.path)[0] or 'image/png'
    except Exception as e:
        obj_name = None
        size = 0
        img_type = None
        if isinstance(e, (OSError, IOError)):
            error = ugettext("The image file does not exist!")

    # use slug by default
    name_field = getattr(instance, 'slug', obj_name)
    name = order_name(name_field)

    deleteUrl = reverse('jfu_delete',
            kwargs={
                'course_identifier': instance.course.identifier,
                'flow_session_id': instance.flow_session_id,
                'ordinal': instance.get_page_ordinal(),
                'pk': instance.pk,
                }
        )

    updateUrl = reverse('jfu_update',
            kwargs={
                'course_identifier': instance.course.identifier,
                'flow_session_id': instance.flow_session_id,
                'ordinal': instance.get_page_ordinal(),
                'pk': instance.pk,
                }
            )

    cropHandlerUrl = reverse('image_crop',
            kwargs={
                'course_identifier': instance.course.identifier,
                'flow_session_id': instance.flow_session_id,
                'ordinal': instance.get_page_ordinal(),
                'pk': instance.pk,
                }
            )

    creationTime = format_datetime_local(
            as_local_time(instance.creation_time))

    creationTimeShort = compact_local_datetime_str(
            as_local_time(instance.creation_time),
            get_now_or_fake_time(request),
            in_python=True)

    timestr_title = ugettext("Created at") + " " + creationTime
    timestr_short = creationTimeShort

    show_modifiedTime = False
    # Only display file_last_modified time when modification is 
    # within 5 minutes on creation.
    if instance.file_last_modified > (
            instance.creation_time + timedelta(minutes=5)):
        show_modifiedTime = True


    modifiedTime = ""
    modifiedTimeShort = ""

    if show_modifiedTime:
        modifiedTime = format_datetime_local(
                as_local_time(instance.file_last_modified))

        modifiedTimeShort = compact_local_datetime_str(
                            as_local_time(instance.file_last_modified),
                            get_now_or_fake_time(request),
                            in_python=True)
        timestr_title = timestr_title + ", " + ugettext("modified at") + " " + modifiedTime
        timestr_short = timestr_short + " (" + modifiedTimeShort + ")"

    return {
        'url': instance.get_absolute_url(),
        'name': name,
        'type': img_type,
        'thumbnailUrl': instance.file_thumbnail.url,
        'timestr_title': timestr_title,
        'timestr_short': timestr_short,
        'size': size,
        'error': error,
        'pk': instance.pk,
        'order': instance.order,
        'updateUrl': updateUrl,
        'deleteUrl': deleteUrl,
        'cropHandlerUrl': cropHandlerUrl,
        'imageAdminUrl': get_image_admin_url(instance),
        'image_data_dict': get_image_page_data_str(instance),
        'deleteType': 'POST',
    }
