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

import os
import tempfile

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text

from proxy_storage.meta_backends.mongo import MongoMetaBackend
from proxy_storage.storages.base import (
    MultipleOriginalStoragesMixin, ProxyStorageBase)

from pymongo import MongoClient

# {{{ mypy

from typing import (Text, Optional, Any, Union)  # noqa
if False:
    from image_upload.models import FlowPageImage  # noqa

# }}}


@deconstructible
class SendFileStorage(FileSystemStorage):
    def __init__(self):
        # type: () -> None
        super(SendFileStorage, self).__init__(
                location=settings.SENDFILE_ROOT)


temp_image_storage_location = getattr(
    settings,
    "RELATE_TEMP_IMAGE_STORAGE_LOCATION",
    os.path.join(tempfile.gettempdir(), "relate_tmp_img"),
)


def get_mongo_db(database=None):
    # type: (Optional[Text]) -> MongoClient
    if not database:
        database = getattr(
            settings, "RELATE_MONGODB_IMG_META_DB_NAME",
            "learningwhat-image-meta-db")
    args = []
    uri = getattr(settings, "RELATE_MONGO_META_DATABASE_URI", None)
    if uri:
        args.append(uri)
    client = MongoClient(*args)
    db = client[database]
    return db


@deconstructible
class ProxyStorage(ProxyStorageBase):
    def save(self, name, content, max_length=None,
             original_storage_path=None, using=None):
        # type: (Text, Any, Optional[int], Optional[Text], Optional[Text]) -> Text
        """
        if original_storage is absent, name should be file.name,
        a relative path in location
        """

        # save file to original storage
        if not original_storage_path:
            original_storage_path = (
                self.get_original_storage()
                    .save(name, content, max_length=max_length))

        assert original_storage_path is not None

        # Get the proper name for the file,
        # as it will actually be saved to meta backend
        # possibility of race condition
        name = self.get_available_name(
            self.get_original_storage_full_path(original_storage_path)
        )

        # create meta backend info
        self.meta_backend.create(data=self.get_data_for_meta_backend_save(
            path=name,
            original_storage_path=original_storage_path,
            original_name=name,
            content=content,
        ))
        return force_text(name)

    def get_original_storage_full_path(self, path, meta_backend_obj=None):
        # type: (Text, Optional[object]) -> Text
        try:
            path = self.get_original_storage(
                meta_backend_obj=meta_backend_obj
            ).path(path)
        except NotImplementedError:
            pass
        print(path)
        print(safe_join('/', os.path.normpath(path)).lstrip('/'))
        print(os.path.normpath(path))
        return os.path.normpath(path)

    def size(self, name):
        # type: (Text) -> Union[int, float]
        meta_backend_obj = self.meta_backend.get(path=name)
        return self.get_original_storage(meta_backend_obj=meta_backend_obj)\
            .size(meta_backend_obj['path'])

    # def url(self, name):
    #     meta_backend_obj = self.meta_backend.get(path=name)
    #     return self.get_original_storage(meta_backend_obj=meta_backend_obj)\
    #         .url(meta_backend_obj['original_storage_path'])

    def path(self, name):
        # type: (Text) -> Text
        from proxy_storage.meta_backends.base import MetaBackendObjectDoesNotExist
        try:
            meta_backend_obj = self.meta_backend.get(path=name)
            return self.get_original_storage(meta_backend_obj=meta_backend_obj) \
                .path(meta_backend_obj['original_storage_path'])
        except MetaBackendObjectDoesNotExist:
            # fall back
            #print("fall backed")
            #print(name)
            return name

    def is_temp_image(self, path):
        # type: (Text) -> bool
        return self.meta_backend.get(path=path)['original_storage_name'] == "temp"


class UserImageStorage(MultipleOriginalStoragesMixin, ProxyStorage):
    #http://chibisov.github.io/django-proxy-storage/docs/
    original_storages = (
        ('temp', FileSystemStorage(location=temp_image_storage_location)),
        ('sendfile', SendFileStorage()),
    )
    meta_backend = MongoMetaBackend(
        database=get_mongo_db(),
        collection='meta_backend_collection'
    )

    def save(self, name, content, max_length=None,
             original_storage_path=None, using=None):
        # type: (Text, Any, Optional[int], Optional[Text], Optional[Text]) -> Text
        if not using:
            using = "temp"
        assert using in ["sendfile", "temp"]

        return super(UserImageStorage, self).save(
            name=name,
            content=content,
            original_storage_path=original_storage_path,
            using=using
        )

    def save_to_sendfile_storage_path(self, path, content):
        # type: (Text, Any) -> Text
        original_storage_path = (
            self.meta_backend.get(path=path)['original_storage_path'])
        if not self.is_temp_image(path=path):
            return original_storage_path
        return self.save(
            original_storage_path, content,
            original_storage_path=original_storage_path,
            using="sendfile")


def user_flowsession_img_path(instance, file_name):
    # type: (FlowPageImage, Text) -> Text
    if instance.creator.get_full_name() is not None:
        user_full_name = instance.creator.get_full_name().replace(' ', '_')
    else:
        user_full_name = instance.creator.pk
    return 'user_images/{0}(user_{1})/{2}'.format(
        user_full_name,
        instance.creator_id,
        file_name)
