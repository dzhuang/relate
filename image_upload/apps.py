from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ImageUploadConfig(AppConfig):
    name = 'image_upload'
    # for translation of the name of "Course" app displayed in admin.
    verbose_name = _("Image upload")

    def ready(self):
        import course.receivers  # noqa
