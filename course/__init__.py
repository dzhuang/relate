default_app_config = 'course.apps.CourseConfig'

# {{{ Override default GetCurrentLanguageNode

# In this way, do_get_current_language can return
# zh-cn if get_language() output zh-hans
from django.templatetags.i18n import GetCurrentLanguageNode
from django.utils import translation

old_render = GetCurrentLanguageNode.render

def new_render(cls, context):
    from relate.utils import LANG_MAP_EXTRA
    lang = translation.get_language()
    if lang in LANG_MAP_EXTRA:
        lang = LANG_MAP_EXTRA[lang].lower()
    context[cls.variable] = lang
    return ''

GetCurrentLanguageNode.render = new_render

# }}}