from django.core.checks import Error, Warning, Critical, Info, register
from django.core.checks import Tags as DjangoTags
from django.conf import settings
from course.latex.latex import Tex2ImgBase
from course import latex

class Tags(DjangoTags):
    relate_course_tag = 'relate_course_tag'

@register(Tags.relate_course_tag)
def latex2image_bin_check(app_configs, **kwargs):
    errors = []

    imagemagick_bin_path = getattr(settings, "RELATE_IMAGEMAGICK_BIN_PATH", "")
    latex_bin_path = getattr(settings, "RELATE_LATEX_BIN_PATH", "")

    from course.latex.utils import (
        CMD_NAME_DICT, get_latex2img_env, get_version)
    from django.core.management.base import CommandError, SystemCheckError

    RELATE_LATEX_TO_IMAGE_ENV = get_latex2img_env(
        [imagemagick_bin_path, latex_bin_path])

    for cmd in CMD_NAME_DICT:

        # ImageMagick need shell=True
        enable_shell = False
        if cmd == "convert":
            enable_shell = True

        try:
            get_version(tool_cmd=cmd, enable_shell=enable_shell, env=RELATE_LATEX_TO_IMAGE_ENV)
        except CommandError:
            errors.append (
                Info(
                    "failed",
                    #hint=("install latex"),
                    obj="latex",
                ))
        #except CommandError as e:
        # #     pass
        # except SystemCheckError as e:
        #     pass
        # except Exception as e:
        #     errors.append (
        #         Warning(
        #             str(e),
        #             #hint=("install latex"),
        #             obj="latex",
        #         ))
        #     continue
            #pass
    #
    #
    # check_failed = True
    # if check_failed:
    #     errors.append(
    #         Warning(
    #             "this is a try",
    #             hint=("install latex"),
    #             obj=None,
    #         )
    #         # Error(
    #         #     'an error',
    #         #     hint=None,
    #         #     obj=checked_object,
    #         #     id='myapp.E001',
    #         # )
    #     )
    return errors