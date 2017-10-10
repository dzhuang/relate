from django.test import override_settings
from .utils import get_test_media_folder
from ..base_test_mixins import force_remove_path
from image_upload.models import FlowPageImage


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


class ImageUploaderMixin(object):
    def tearDown(self):
        # Delete all uploaded files created during testing
        for image in FlowPageImage.objects.all():
            try:
                if image.image.path:
                    image.file.delete()
            except:
                pass
            image.delete()
