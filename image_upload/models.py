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
from course.models import FlowSession

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

@deconstructible
class UserImageStorage(FileSystemStorage):    
    def __init__(self):
        super(UserImageStorage, self).__init__(
                location=settings.SENDFILE_ROOT)


sendfile_storage = UserImageStorage()


def user_directory_path(instance, filename):
    return 'userimages/user_{0}/{1}'.format(instance.creator_id, filename)


class Image(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
            verbose_name=_('Creator'), on_delete=models.CASCADE)
    file = models.ImageField(upload_to=user_directory_path, 
            storage=sendfile_storage)
    slug = models.SlugField(max_length=256, blank=True)
    creation_time = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(Image, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(Image, self).delete(*args, **kwargs)
        
    def get_creation_time(self):

        return format_datetime_local(
                as_local_time(self.creation_time))

    @models.permalink
    def get_absolute_url(self):
        return ('image_download', [self.creator_id, self.pk], {})

    class Meta:
        ordering = ("id", "creation_time")

    def __unicode__(self):
        return _("%(url)s uploaded by %(creator)s") % {
            'url': self.get_absolute_url(),
            'creator': self.creator}

    if six.PY3:
        __str__ = __unicode__


class SessionPageImage(Image):
    file_thumbnail = ImageSpecField(
            source='file',
            processors=[ResizeToFit(200, 200)],
            format='PNG',
            options={'quality': 60}
            )
    flow_session = models.ForeignKey(
            FlowSession, null=True, related_name="page_image_data",
            verbose_name=_('Flow session'), on_delete=models.CASCADE)
    image_page_id = models.CharField(max_length=200, null=True)


# vim: foldmethod=marker
