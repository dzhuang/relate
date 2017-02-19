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


@deconstructible
class SendFileStorage(FileSystemStorage):
    def __init__(self):
        super(SendFileStorage, self).__init__(
                location=settings.SENDFILE_ROOT)


temp_image_storage_location = getattr(
    settings,
    "RELATE_TEMP_IMAGE_STORAGE_LOCATION",
    os.path.join(tempfile.gettempdir(), "relate_tmp_img"),
)


def get_mongo_db(database="learningwhat-image-meta-db"):
    args = []
    uri = getattr(settings, "RELATE_MONGO_META_DATABASE_URI", None)
    if uri:
        args.append(uri)
    client = MongoClient(*args)
    db = client[database]
    return db


@deconstructible
class ProxyStorage(ProxyStorageBase):
    def save(self, name, content, max_length=None, original_storage_path=None):
        """
        if original_storage is absent, name should be file.name,
        a relative path in location
        """

        # save file to original storage
        if not original_storage_path:
            original_storage_path = (
                self.get_original_storage()
                    .save(name, content, max_length=max_length))

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
        try:
            path = self.get_original_storage(
                meta_backend_obj=meta_backend_obj
            ).path(path)
        except NotImplementedError:
            pass
        return safe_join('/', os.path.normpath(path)).lstrip('/')

    def size(self, name):
        meta_backend_obj = self.meta_backend.get(path=name)
        return self.get_original_storage(meta_backend_obj=meta_backend_obj)\
            .size(meta_backend_obj['path'])

    # def url(self, name):
    #     meta_backend_obj = self.meta_backend.get(path=name)
    #     return self.get_original_storage(meta_backend_obj=meta_backend_obj)\
    #         .url(meta_backend_obj['original_storage_path'])

    def path(self, name):
        meta_backend_obj = self.meta_backend.get(path=name)
        return self.get_original_storage(meta_backend_obj=meta_backend_obj) \
            .path(meta_backend_obj['original_storage_path'])

    def is_temp_image(self, path):
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
        if not using:
            using = "temp"
        assert using in ["sendfile", "temp"]

        return super(UserImageStorage, self).save(
            name=name,
            content=content,
            original_storage_path=original_storage_path,
            using=using
        )

    def save_to_sendfile_storage_path(self, path, content, **kwargs):
        original_storage_path = (
            self.meta_backend.get(path=path)['original_storage_path'])
        if not self.is_temp_image(path=path):
            return original_storage_path
        return self.save(
            original_storage_path, content,
            original_storage_path=original_storage_path,
            using="sendfile")


def user_flowsession_img_path(instance, file_name):
    if instance.creator.get_full_name() is not None:
        user_full_name = instance.creator.get_full_name().replace(' ', '_')
    else:
        user_full_name = instance.creator.pk
    return 'user_images/{0}(user_{1})/{2}'.format(
        user_full_name,
        instance.creator_id,
        file_name)
