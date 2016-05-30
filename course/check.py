from django.core.checks import Error, Warning, Critical, Info, register
from django.core.checks import Tags as DjangoTags
from django.conf import settings
from course.latex.utils import (
    CMD_NAME_DICT, prepend_bin_path_to_subprocess_env, popen_wrapper)
from django.core.management.base import CommandError
from django.utils.encoding import (
    DEFAULT_LOCALE_ENCODING, force_text)
import re
import os

class Tags(DjangoTags):
    relate_course_tag = 'relate_course_tag'

@register(Tags.relate_course_tag)
@register(Tags.relate_course_tag, deploy=True)
def latex2image_bin_check(app_configs, **kwargs):
    if not getattr(settings, "RELATE_LATEX_TO_IMAGE_ENABLED", False):
        return []

    errors = []

    imagemagick_bin_path = getattr(settings, "RELATE_IMAGEMAGICK_BIN_PATH", "")
    latex_bin_path = getattr(settings, "RELATE_LATEX_BIN_PATH", "")

    #RELATE_LATEX_TO_IMAGE_ENV = prepend_bin_path_to_subprocess_env([imagemagick_bin_path, latex_bin_path])

    for cmd in CMD_NAME_DICT:

        # ImageMagick need shell=True
        # enable_shell = False
        # if cmd == "convert":
        #     enable_shell = True

        out = ""
        strerror = ""
        cmd_with_path = cmd
        if cmd == "convert":
            if imagemagick_bin_path:
                cmd_with_path = os.path.join(imagemagick_bin_path, cmd)
        else:
            if latex_bin_path:
                cmd_with_path = os.path.join(latex_bin_path, cmd)
        try:
            out, err, status = popen_wrapper([cmd_with_path, '--version'], stdout_encoding=DEFAULT_LOCALE_ENCODING)
        # except KeyError as e:
        #     strerror = str(e)
        except CommandError as e:
            strerror = e.__str__()

        m = re.search(r'(\d+)\.(\d+)\.?(\d+)?', out)
        if not m:
            errors.append(
                Critical(
                    strerror,
                    hint=("Unable to run %(cmd)s. Is %(tool)s installed "
                          "or has its path correctly configured "
                          "in local_settings.py?")
                         % {"cmd": cmd_with_path,
                            "tool": CMD_NAME_DICT[cmd],
                            },
                    obj=CMD_NAME_DICT[cmd]
                ))

    return errors