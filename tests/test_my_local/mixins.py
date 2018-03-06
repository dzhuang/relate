import os
from django.test import override_settings
from django.conf import settings

from relate.utils import force_remove_path

from tests.test_my_local.utils import get_test_media_folder


class ImageUploadStorageTestMixin(object):
    def setUp(self):  # noqa
        self.media_root = get_test_media_folder()
        self.image_storage_settings_override = override_settings(
            MEDIA_ROOT=self.media_root
        )
        self.image_storage_settings_override.enable()

    def tearDown(self):  # noqa
        self.image_storage_settings_override.disable()
        force_remove_path(self.media_root)
        sendfile_root_dir_name = os.path.split(settings.SENDFILE_ROOT)[-1]
        if sendfile_root_dir_name == "test_protected":
            try:
                force_remove_path(settings.SENDFILE_ROOT)
            except OSError:
                pass