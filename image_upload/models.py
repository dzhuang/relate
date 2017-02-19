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
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from image_upload.storages import (
    user_flowsession_img_path, UserImageStorage)

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from jsonfield import JSONField

# {{{ mypy

from typing import Text, Optional  # noqa


# }}}


multiple_image_storage = UserImageStorage()


class FlowPageImage(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
            verbose_name=_('Creator'), on_delete=models.SET_NULL)
    file = models.ImageField(upload_to=user_flowsession_img_path,
                             storage=multiple_image_storage)
    slug = models.SlugField(max_length=256, blank=True)
    creation_time = models.DateTimeField(default=now)
    file_last_modified = models.DateTimeField(default=now)
    file_thumbnail = ImageSpecField(
        source='file',
        processors=[ResizeToFit(100, 100)],
        format='PNG',
        options={'quality': 50})
    course = models.ForeignKey(
        "course.Course", null=True,
        verbose_name=_('Course'), on_delete=models.SET_NULL)
    flow_session = models.ForeignKey(
        "course.FlowSession", null=True, related_name="page_image_data",
        verbose_name=_('Flow session'), on_delete=models.SET_NULL)
    image_page_id = models.CharField(max_length=200, null=True)

    is_image_textify = models.BooleanField(
        default=False, verbose_name=_("Load textified Image?"))
    image_text = models.TextField(
        verbose_name=_("Related Html"),
        help_text=_("The html for the FlowPageImage"),
        blank=True, null=True
    )
    image_data = JSONField(
        null=True, blank=True,

        # Show correct characters in admin for non ascii languages.
        dump_kwargs={'ensure_ascii': False},
        verbose_name=_('External image data'))
    use_image_data = models.BooleanField(
        default=False, verbose_name=_("Use external Image data?"))

    # The order of the img in a flow session page.
    order = models.SmallIntegerField(default=0)

    def get_page_ordinal(self):
        from course.models import FlowPageData
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
    def get_absolute_url(self, private=True, key=False):
        import os
        file_name = os.path.basename(self.file.path)
        if private:
            return ('flow_page_image_download', [
                    self.course.identifier,
                    self.flow_session_id,
                    self.creator_id,
                    self.pk,
                    file_name], {}
                    )
        elif key is False:
            return ('flow_page_image_problem',
                    [self.pk, file_name], {})
        elif key is True:
            return ('flow_page_image_key',
                    [self.pk, self.creator_id, file_name], {})

    def admin_image(self):
        # type: () -> Optional[Text]
        if self.order == 0:
            img_url = self.get_absolute_url(private=False)
        else:
            img_url = self.get_absolute_url(key=True)
        if img_url:
            return ("<img src='%s' "
                    "class='img-responsive' "
                    "style='max-height:300pt'/>" % img_url)
        return None

    admin_image.short_description = 'Image'  # type:ignore
    admin_image.allow_tags = True  # type:ignore

    def get_image_text(self):
        if self.is_image_textify:
            if self.image_text:
                return self.image_text
            else:
                return None
        return None

    class Meta:
        ordering = ("id", "creation_time")

    def __unicode__(self):
        try:
            return _("%(url)s uploaded by %(creator)s") % {
                'url': self.get_absolute_url(),
                'creator': self.creator}
        except:
            return ""

    if six.PY3:
        __str__ = __unicode__

# vim: foldmethod=marker
