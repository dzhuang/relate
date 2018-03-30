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
from django.urls import reverse
from django.utils.translation import ugettext as _, string_concat

from relate.utils import (
    as_local_time, format_datetime_local,
    compact_local_datetime_str)

from datetime import timedelta
import mimetypes
import re
import os
import json

from image_upload.models import FlowPageImage


def get_truncated_name(name):
    """get_truncated_name
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
    if not image.flow_session:
        return None
    if image.flow_session.in_progress:
        return None

    image_data_dict = {
        'flow_pk': image.flow_session.id,
        'page_id': image.image_page_id,
    }

    return str(json.dumps(image_data_dict).encode("utf-8"))


def get_image_admin_url(image):
    if not isinstance(image, FlowPageImage):
        return None
    if not image.flow_session:
        return None
    if image.flow_session.in_progress:
        return None
    return reverse(
        'admin:image_upload_flowpageimage_change',
        args=(image.pk,))


def serialize(request, instance, file_attr='image'):
    """serialize -- Serialize a FlowPageImage instance into a dict.

    instance -- Image instance
    file_attr -- attribute name that contains the FileField or ImageField

    """
    obj = getattr(instance, file_attr)
    error = None
    size = 0
    try:
        size = obj.size
    except:
        pass

    obj_name = obj.name
    img_type = mimetypes.guess_type(obj.name)[0] or 'image/png'

    # use slug by default
    name = getattr(instance, 'slug', obj_name)
    name_truncated = get_truncated_name(name)

    handler_kwargs ={
        'course_identifier': instance.course.identifier,
        'pk': instance.pk,
    }

    if instance.flow_session_id:
        # else is in sandbox
        handler_kwargs.update({
            'flow_session_id': instance.flow_session_id,
            'page_ordinal': instance.get_page_ordinal()})

    delete_url = reverse('jfu_delete',
            kwargs=handler_kwargs
        )

    crop_handler_url = reverse('image_crop',
            kwargs=handler_kwargs
            )

    # {{{ creation time string

    creation_time = format_datetime_local(
            as_local_time(instance.creation_time))

    from course.views import get_now_or_fake_time
    creation_time_short = compact_local_datetime_str(
            as_local_time(instance.creation_time),
            get_now_or_fake_time(request),
            in_python=True)

    show_modified_time = False
    modified_time = None
    modified_time_short = None
    # Only display file_last_modified time when modification is
    # within 5 minutes on creation.
    if instance.file_last_modified > (
            instance.creation_time + timedelta(minutes=5)):
        show_modified_time = True

        modified_time = format_datetime_local(
            as_local_time(instance.file_last_modified))

        modified_time_short = compact_local_datetime_str(
                            as_local_time(instance.file_last_modified),
                            get_now_or_fake_time(request),
                            in_python=True)

    modified_by_course_staff = False
    if instance.flow_session:
        if instance.creator != instance.flow_session.participation.user:
            from course.models import Participation
            creator_participation = None
            try:
                creator_participation = Participation.objects.get(
                    user=instance.creator, course=instance.course)
            except Participation.DoesNotExist:
                pass
            if creator_participation:
                from image_upload.utils import is_course_staff_participation
                modified_by_course_staff = (
                    is_course_staff_participation(creator_participation))

    timestr_title = string_concat(
        _("Created at %s") % creation_time,
        string_concat(
            ", ",
            _("modified at %s") % modified_time
        ) if show_modified_time else "",
        string_concat(
            " ",
            _("by course staff.")
        ) if modified_by_course_staff else ".",
    )

    timestr_short = string_concat(
        creation_time_short,
        " (%s" % modified_time_short if show_modified_time else "",
        "*" if modified_by_course_staff else "",
        ")" if show_modified_time else ""
    )

    # }}}

    return {
        'url': instance.get_absolute_url(),
        'name': name,
        'name_truncated': name_truncated,
        'type': img_type,
        'thumbnailUrl': instance.image_thumbnail.url,
        'timestr_title': timestr_title,
        'timestr_short': timestr_short,
        'size': size,
        'error': error,
        'pk': instance.pk,
        'deleteUrl': delete_url,
        'crop_handler_url': crop_handler_url,
        'imageAdminUrl': get_image_admin_url(instance),
        'image_data_dict': get_image_page_data_str(instance),
        'deleteType': 'POST',
    }
