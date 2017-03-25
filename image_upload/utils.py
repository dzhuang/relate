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

from six import BytesIO
from six.moves.urllib.parse import urlparse
from django.db.models import Transform, CharField, TextField
from django import forms
from django.template import Context
from django.template.loader import get_template
from django.contrib.admin import widgets
from django.urls import resolve

import zipfile
import re

JINJA_TEX_TEMPLATE_COMMENT_RE = re.compile("\\\\#{[^}\n]*}")
JINJA_TEX_TEMPLATE_LINE_COMMENT_RE = re.compile("%#.*")
JINJA_TEX_TEMPLATE_INBLOCK_LATEX_CALL_RE =  re.compile("{%\s*call\s*latex[^}]*}((?:.|\n)*?){%\s*endcall")

# extracted from course.flow


# {{{  widget used in admin

class MarkdownWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        if 'class' in attrs:
            attrs['class'] += ' markdown-editor'
        else:
            attrs.update({'class': 'markdown-editor'})
        attrs.update(
            {
                #'id': "marked-mathjax-input",
                'onkeyup': "Preview.Update()",
                'name': "comment",
                })

        # attrs.update({"autofocus": ""})

        widget = super(MarkdownWidget, self).render(name, value, attrs)

        t = get_template('image_upload/widget.html')
        c = Context({
            'markdown_editor': widget,
        })

        return t.render(c)

    class Media:
        js = (
            "/static/marked/marked.min.js",
        )


class AdminMarkdownWidget(MarkdownWidget, widgets.AdminTextareaWidget):
    class Media:
        css = {
            'all': ('/static/css/markdown-mathjax.css',)
        }
        js = (
            "/static/marked/marked.min.js",
              )

# }}}


#{{{ enable query filter charfield by 'len'

class CharacterLength(Transform):
    lookup_name = 'len'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "LENGTH(%s)" % lhs, params


CharField.register_lookup(CharacterLength)
TextField.register_lookup(CharacterLength)

# }}}


# {{{ zip as file-like object

class InMemoryZip(object):
    def __init__(self):
        # Create the in-memory file-like object
        self.in_memory_zip = BytesIO()

    def append(self, filename_in_zip, file_contents):
        '''Appends a file with name filename_in_zip and contents of
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0

        return self

    def read(self):
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writetofile(self, filename):
        '''Writes the in-memory zip to a file.'''
        from django.core.files import File
        with open(filename, 'w') as f:
            ff = File(f)
            ff.write(self.read())

# }}}


def get_ordinal_from_page_context(page_context):
    if page_context.in_sandbox:
        return None

    relative_url = urlparse(page_context.page_uri).path

    func, args, kwargs = resolve(relative_url)
    assert kwargs["ordinal"]
    return kwargs["ordinal"]


def minify_python_script(source):
    from pyminifier import token_utils, minification
    from optparse import Values
    options = Values()
    options.tabs = False
    tokens = token_utils.listified_tokenizer(source)
    return minification.minify(tokens, options)


# {{{ strip comments from template, not that this is different
#     with course.latex.utils.strip_comments

def strip_template_comments(source):
    from course.latex.utils import strip_spaces
    source = strip_spaces(source, allow_single_empty_line=True)
    source = re.sub(JINJA_TEX_TEMPLATE_COMMENT_RE, "", source)
    source = re.sub(JINJA_TEX_TEMPLATE_LINE_COMMENT_RE, "", source)

    in_block_tex_list = JINJA_TEX_TEMPLATE_INBLOCK_LATEX_CALL_RE.findall(source)
    if in_block_tex_list:
        from course.latex.utils import strip_comments
        for b in in_block_tex_list:
            source = source.replace(b,strip_comments(b))

    return source
# }}}