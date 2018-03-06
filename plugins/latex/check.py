# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2016 Dong Zhuang, Andreas Kloeckner"

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

from django.conf import settings
from django.core.checks import Tags as DjangoTags, register

from .converter import CommandBase
from .utils import get_all_indirect_subclasses
from relate.checks import RelateCriticalCheckMessage

# class PluginTags(DjangoTags):
#     latex_jinja2_tag = 'latex_jinja2_tag'


#@register(PluginTags.latex_jinja2_tag)
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
        check_errors = instance.check()
        if check_errors:
            errors.extend(check_errors)
    return errors
