# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2016 Dong Zhuang, Andreas Kloeckner"

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

from django.db.models import FileField
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver

from course.models import FlowPageVisit

from image_upload.models import FlowPageImage

LOCAL_APPS = [
    'image_upload',
]


if False:
    from typing import List, Any  # noqa

# {{{ Delete temp image when it is saved to sendfile storage


def delete_files(files_list):
    # type: (List[Any]) -> None

    for file_ in files_list:
        if file_ and hasattr(file_, 'storage') and hasattr(file_, 'path'):
            # this accounts for different file storages
            # (e.g. when using django-storages)
            storage_, path_ = file_.storage, file_.path
            storage_.delete(path_)


@receiver(pre_save, sender=FlowPageImage)
def set_instance_cache(sender, instance, **kwargs):
    # type: (Any, FlowPageImage, **Any) -> None

    # stop if the object is not created.
    if instance.pk is None:
        return

    # preserve file if the temp image is cropped or rotated,
    # those file should be removed with the instances they belong to
    if instance.is_temp_image:
        return
    # prevent errors when loading files from fixtures
    from_fixture = 'raw' in kwargs and kwargs['raw']
    is_valid_app = sender._meta.app_label in LOCAL_APPS
    if is_valid_app and not from_fixture:
        old_instance = sender.objects.filter(pk=instance.id).first()
        if old_instance is not None:
            # for each FileField, we will keep
            # the original value inside an ephemeral `cache`
            instance.files_cache = {
                field_.name: getattr(old_instance, field_.name, None)
                for field_ in sender._meta.fields
                if isinstance(field_, FileField)
            }


@receiver(post_save, sender=FlowPageImage)
def handle_files_on_update(sender, instance, **kwargs):
    # type: (Any, FlowPageImage, **Any) -> None
    if hasattr(instance, 'files_cache') and instance.files_cache:
        deletables = []
        for field_name in instance.files_cache:
            old_file_value = instance.files_cache[field_name]
            new_file_value = getattr(instance, field_name, None)
            # only delete the files that have changed
            if old_file_value and old_file_value != new_file_value:
                deletables.append(old_file_value)
        delete_files(deletables)
        instance.files_cache = {
            field_name: getattr(instance, field_name, None)
            for field_name in instance.files_cache}

# }}}


# {{{ Save submiitted temp image objs to sendfild and remove unused temp objs

@receiver(pre_save, sender=FlowPageVisit)
def send_to_sendfile_on_page_save(sender, instance, **kwargs):
    if instance.answer is None:
        return

    if not isinstance(instance.answer, dict):
        return

    data = instance.answer.get("answer", [])

    if not isinstance(data, list):
        return

    # ignore when loading bad formatted answer_data
    # the data should be list containing only int
    try:
        data = [int(i) for i in data]
    except:
        return

    from image_upload.views import get_all_imageuploadpage_klass_names
    if instance.page_data.page_type not in get_all_imageuploadpage_klass_names():
        return

    saving_image_qs = FlowPageImage.objects.filter(
        pk__in=data, is_temp_image=True
    )

    for img in saving_image_qs:
        # notice that this will never happen in sandbox with ImageUploadQuestion
        # because those will never save a FlowPageVisit object
        img.save_to_protected_storage(
            delete_temp_storage_file=True,
            fail_silently_on_save=True)


@receiver(post_save, sender=FlowPageVisit)
def delete_temp_images_on_flowpage_answer_update(sender, instance, **kwargs):
    if instance.answer is None:
        return

    from image_upload.views import get_all_imageuploadpage_klass_names
    if instance.page_data.page_type not in get_all_imageuploadpage_klass_names():
        return

    fpi_qs = FlowPageImage.objects.filter(
        flow_session_id=instance.flow_session_id,
        image_page_id=instance.page_data.page_id,
        is_temp_image=True
    )
    for FPI in fpi_qs:
        FPI.refresh_from_db()
        if FPI.is_temp_image:
            FPI.delete()

# }}}

# vim: foldmethod=marker
