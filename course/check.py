from django.core.checks import register, Tags as DjangoTags
from django.conf import settings

from course.latex.utils import get_all_indirect_subclasses
from course.latex.converter import CommandBase

class Tags(DjangoTags):
    relate_course_tag = 'relate_course_tag'

@register(Tags.relate_course_tag)
@register(Tags.relate_course_tag, deploy=True)
def latex2image_bin_check(app_configs, **kwargs):
    """
    Check if all tex compiler and image converter
    are correctly configured, if latex utility is
    enabled.
    """
    if not getattr(settings, "RELATE_LATEX_TO_IMAGE_ENABLED", False):
        return []
    klass = get_all_indirect_subclasses(CommandBase)
    instance_list = [cls() for cls in klass]
    errors = []
    for instance in instance_list:
        error = instance.check()
        if error:
            errors.append(error)
    return errors