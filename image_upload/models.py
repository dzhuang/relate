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
import os
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from jsonfield import JSONField

# {{{ mypy

if False:
    from typing import Text, Optional  # noqa

# }}}


@deconstructible
class UserImageStorage(FileSystemStorage):
    def __init__(self):
        # type: () -> None
        super(UserImageStorage, self).__init__(
                location=settings.SENDFILE_ROOT)


storage = UserImageStorage()


def user_flowsession_img_path(instance, filename):
    if instance.creator.get_full_name() is not None:
        user_full_name = instance.creator.get_full_name().replace(' ', '_')
    else:
        user_full_name = instance.creator.pk

    if instance.is_temp_image:
        if instance.flow_session is None:
            return 'user_images/{0}(user_{1})/temp/sandbox/{2}'.format(
                user_full_name,
                instance.creator_id,
                filename)
        return 'user_images/{0}(user_{1})/temp/{2}'.format(
            user_full_name,
            instance.creator_id,
            filename)

    if instance.flow_session is None:
        return 'user_images/{0}(user_{1})/sandbox/{2}'.format(
            user_full_name,
            instance.creator_id,
            filename)

    return 'user_images/{0}(user_{1})/{2}'.format(
        user_full_name,
        instance.creator_id,
        filename)


class FlowPageImageFileNotFoundError(OSError):
    pass


class TempFlowPageImageFileNotFoundError(OSError):
    pass


class FlowPageImage(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
            verbose_name=_('Creator'), on_delete=models.SET_NULL)
    image = models.ImageField(upload_to=user_flowsession_img_path,
                              storage=storage,
                              max_length=500)
    slug = models.SlugField(max_length=256, blank=True)
    creation_time = models.DateTimeField(default=now)
    file_last_modified = models.DateTimeField(default=now)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(100, 100)],
        format='PNG',
        options={'quality': 50})

    is_temp_image = models.BooleanField(
        default=False, verbose_name=_("Is the image for temporary use?"),
    )

    course = models.ForeignKey(
        "course.Course", null=True,
        verbose_name=_('Course'), on_delete=models.SET_NULL)
    flow_session = models.ForeignKey(
        "course.FlowSession", null=True, related_name="page_image_data",
        verbose_name=_('Flow session'), on_delete=models.SET_NULL)

    # This is not redundant, because the permission on image
    # should be same with page_behavior, we use this to connect
    # to page_behavior
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

    def get_page_ordinal(self):
        from course.models import FlowPageData
        fpd = FlowPageData.objects.get(
            flow_session=self.flow_session_id, page_id=self.image_page_id)
        return fpd.page_ordinal

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.image.name
        super(FlowPageImage, self).save(*args, **kwargs)

    def is_in_temp_storage(self, raise_on_oserror=False):
        return self.is_temp_image

    def save_to_protected_storage(
            self,
            delete_temp_storage_file=False,
            fail_silently_on_save=False):

        if not self.is_in_temp_storage():
            return

        # temp_image_path = self.image.path
        filename = os.path.split(self.image.name)[-1]
        self.is_temp_image = False
        name = user_flowsession_img_path(self, filename)

        try:
            new_img_name = storage.save(
                name=name,
                content=self.image
            )
            self.image = new_img_name
            self.save(update_fields=["image", "is_temp_image"])
        except OSError:
            raise
            # if not fail_silently_on_save:
            #     raise
            #
            # # The temp file is removed before/during handling, for
            # # cases when user are submitting pages,
            # # we have to fail silently.
            # return

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave image."""
        self.image.delete(False)
        super(FlowPageImage, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        # type: () -> Text
        import os
        file_name = os.path.basename(self.image.path)
        from django.urls import reverse
        if self.flow_session_id:
            return reverse('flow_page_image_download', args=[
                    self.course.identifier,
                    self.flow_session_id,
                    self.creator_id,
                    self.pk,
                    file_name]
                    )
        else:
            # in sandbox
            return reverse('flow_page_image_download', args=[
                    self.course.identifier,
                    self.creator_id,
                    self.pk,
                    file_name]
                    )

    def admin_image(self):
        # type: () -> Optional[Text]
        img_url = self.get_absolute_url()
        if img_url:
            return ("<img src='%s' "
                    "class='img-responsive' "
                    "style='max-height:300pt'/>" % img_url)
        return None

    admin_image.short_description = 'Image'  # type: ignore
    admin_image.allow_tags = True  # type: ignore

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
