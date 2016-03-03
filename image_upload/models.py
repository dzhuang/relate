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

import six
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from relate.utils import format_datetime_local, as_local_time
from course.models import Course, FlowSession, FlowPageData

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

@deconstructible
class UserImageStorage(FileSystemStorage):
    def __init__(self):
        super(UserImageStorage, self).__init__(
                location=settings.SENDFILE_ROOT)


sendfile_storage = UserImageStorage()


def user_directory_path(instance, filename):
    if instance.creator.get_full_name() is not None:
        user_full_name = instance.creator.get_full_name().replace(' ', '_')
    else:
        user_full_name = instance.creator.pk
    return 'user_images/{0}(user_{1})/{2}'.format(
        user_full_name,
        instance.creator_id,
        file_name)

class UserImage(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
            verbose_name=_('Creator'), on_delete=models.CASCADE)
    file = models.ImageField(upload_to=user_directory_path, 
            storage=sendfile_storage)
    slug = models.SlugField(max_length=256, blank=True)
    creation_time = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.file.name
        super(UserImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(UserImage, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('user_image_download', [self.creator_id, self.pk], {})

    def get_random_filename(self):
        import os, uuid
        slug_path = self.file.path.replace(
                os.path.basename(self.file.path),
                self.slug)
        [file_no_ext, ext] = os.path.splitext(slug_path)
        while True:
            rand_str4 = str(uuid.uuid4())[-4:]
            rand_file_name = "".join([file_no_ext, rand_str4, ext])
#            print "ori_file_name", self.file.path
#            print "rand_file_name", rand_file_name
            if not os.path.isfile(rand_file_name):
                return rand_file_name

    class Meta:
        ordering = ("id", "creation_time")

    def __unicode__(self):
        return _("%(url)s uploaded by %(creator)s") % {
            'url': self.get_absolute_url(),
            'creator': self.creator}

    if six.PY3:
        __str__ = __unicode__


def user_flowsession_img_path(instance, file_name):
    if instance.creator.get_full_name() is not None:
        user_full_name = instance.creator.get_full_name().replace(' ', '_')
    else:
        user_full_name = instance.creator.pk
    return 'user_images/{0}(user_{1})/{2}'.format(
        user_full_name,
        instance.creator_id,
        file_name)

class FlowPageImage(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
            verbose_name=_('Creator'), on_delete=models.CASCADE)
    file = models.ImageField(upload_to=user_flowsession_img_path, 
            storage=sendfile_storage)
    slug = models.SlugField(max_length=256, blank=True)
    creation_time = models.DateTimeField(default=now)
    file_last_modified = models.DateTimeField(default=now)
    file_thumbnail = ImageSpecField(
            source='file',
            processors=[ResizeToFit(200, 200)],
            format='PNG',
            options={'quality': 85}
            )
    course = models.ForeignKey(
            Course, null=True,
            verbose_name=_('Course'), on_delete=models.CASCADE)
    flow_session = models.ForeignKey(
            FlowSession, null=True, related_name="page_image_data",
            verbose_name=_('Flow session'), on_delete=models.CASCADE)
    image_page_id = models.CharField(max_length=200, null=True)

    # The order of the img in a flow session page.
    order = models.SmallIntegerField(default=0)

    def get_page_ordinal(self):
        fpd = FlowPageData.objects.get(
            flow_session=self.flow_session_id, page_id=self.image_page_id)
        return fpd.ordinal

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.file.name
        super(FlowPageImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(FlowPageImage, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        import os
        file_name = os.path.basename(self.file.path)
        return ('flow_page_image_download', [
                self.course.identifier,
                self.flow_session_id,
                self.creator_id,
                self.pk,
                file_name], {}
                )

    def get_random_filename(self):
        import os, uuid
        slug_path = self.file.path.replace(
                os.path.basename(self.file.path),
                self.slug)
        [file_no_ext, ext] = os.path.splitext(slug_path)
        while True:
            rand_str4 = str(uuid.uuid4())[-4:]
            rand_file_name = "".join([file_no_ext, rand_str4, ext])
            if not os.path.isfile(rand_file_name):
                return rand_file_name

    class Meta:
        ordering = ("id", "creation_time")

    def __unicode__(self):
        return _("%(url)s uploaded by %(creator)s") % {
            'url': self.get_absolute_url(),
            'creator': self.creator}

    if six.PY3:
        __str__ = __unicode__

# vim: foldmethod=marker
