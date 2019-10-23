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

import six
import datetime
import time
import functools
import operator
from six import BytesIO
from six.moves.urllib.parse import urlparse
from django.db.models import Transform, CharField, TextField
from django import forms
from django.template import Context
from django.template.loader import get_template
from django.contrib.admin import widgets
from django.urls import resolve
from course.constants import participation_permission as pperm
from course.utils import CoursePageContext
from image_upload.views import COURSE_STAFF_IMAGE_PERMISSION
import numpy as np
from numpy.core import numeric  # noqa


default_fudge = datetime.timedelta(seconds=0, microseconds=0, days=0)

import zipfile
import re

JINJA_TEX_TEMPLATE_COMMENT_RE = re.compile("\\\\#{[^}\n]*}")
JINJA_TEX_TEMPLATE_LINE_COMMENT_RE = re.compile("%#.*")
JINJA_TEX_TEMPLATE_INBLOCK_LATEX_CALL_RE = (
    re.compile("{%\s*call\s*latex[^}]*}((?:.|\n)*?){%\s*endcall"))

if False:
    from typing import Text, Any, Optional, Dict, Iterable, Union  # noqa
    from course.utils import PageContext  # noqa
    from course.models import Participation  # noqa


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
    # type: (PageContext) -> Any
    if page_context.in_sandbox:
        return None

    if not page_context.page_uri:
        return None

    relative_url = urlparse(page_context.page_uri).path
    func, args, kwargs = resolve(relative_url)
    assert kwargs["page_ordinal"]
    return kwargs["page_ordinal"]


def get_flow_page_ordinal_from_page_id(flow_session_id, page_id):
    from course.models import FlowPageData
    flow_page_data = FlowPageData.objects.get(
        flow_session__id=flow_session_id,
        page_id=page_id
    )
    return flow_page_data.page_ordinal


def minify_python_script(source):
    # type: (Text) -> Text
    from pyminifier import token_utils, minification
    from optparse import Values
    options = Values()
    options.tabs = False  #  type: ignore
    tokens = token_utils.listified_tokenizer(source)
    return minification.minify(tokens, options)


# {{{ strip comments from template, not that this is different
#     with course.latex.utils.strip_comments

def strip_template_comments(source):
    # type: (Text) -> Text
    from plugins.latex.utils import strip_spaces
    source = strip_spaces(source, allow_single_empty_line=True)
    source = re.sub(JINJA_TEX_TEMPLATE_COMMENT_RE, "", source)
    source = re.sub(JINJA_TEX_TEMPLATE_LINE_COMMENT_RE, "", source)

    in_block_tex_list = JINJA_TEX_TEMPLATE_INBLOCK_LATEX_CALL_RE.findall(source)
    if in_block_tex_list:
        from plugins.latex.utils import strip_comments
        for b in in_block_tex_list:
            source = source.replace(b, strip_comments(b))

    return source
# }}}


def is_course_staff_participation(participation):
    # type: (Optional[Participation]) -> bool
    if not participation:
        return False

    from course.enrollment import (
        get_participation_permissions)
    perms = get_participation_permissions(
        participation.course, participation)

    if all(perm in perms for perm in COURSE_STAFF_IMAGE_PERMISSION):
        return True

    return False


def is_course_staff_course_image_request(request, course):
    pctx = CoursePageContext(request, course.identifier)
    return pctx.has_permission(pperm.assign_grade)


def deep_np_to_string(layer):
    # type: (Any) -> Any
    # convert embeded numpy ndarray to string(bytes string)
    # while retain the original data structure
    to_ret = layer

    if isinstance(layer, np.ndarray):
        to_ret = layer.tostring()

    if isinstance(layer, list):
        for i, item in enumerate(layer):
            layer[i] = deep_np_to_string(item)

    if isinstance(layer, tuple):
        _layer = list(layer)
        for i, item in enumerate(layer):
            _layer[i] = deep_np_to_string(item)
        return tuple(_layer)

    try:
        for key, value in six.iteritems(to_ret):
            to_ret[key] = deep_np_to_string(value)
    except AttributeError:
        pass

    return to_ret


def deep_convert_ordereddict(layer):
    # type: (Any) -> Any
    to_ret = layer
    if isinstance(layer, dict):
        from collections import OrderedDict
        # because OrderedDict remembers the order in which the
        # elements have been inserted
        # https://stackoverflow.com/q/9001509/3437454
        to_ret = OrderedDict(sorted(six.iteritems(layer)))

    if isinstance(layer, list):
        for i, item in enumerate(layer):
            layer[i] = deep_convert_ordereddict(item)

    if isinstance(layer, tuple):
        _layer = list(layer)
        for i, item in enumerate(layer):
            _layer[i] = deep_convert_ordereddict(item)
        return tuple(_layer)

    try:
        for key, value in six.iteritems(to_ret):
            to_ret[key] = deep_convert_ordereddict(value)
    except AttributeError:
        pass

    # This doesn't gurantee the (embedded) dicts are converted to OrderedDict
    # but to ensure the data equals the original one
    try:
        assert deep_eq(layer, to_ret)
    except AssertionError:
        raise ValueError("%s and %s not equal" % (layer, to_ret))

    return to_ret


def deep_eq(_v1, _v2, datetime_fudge=default_fudge, _assert=False):
    # type: (Any, Any, Any, bool) -> bool

    """
    Modified from https://gist.github.com/samuraisam/901117
    Tests for deep equality between two python data structures recursing
    into sub-structures if necessary. Works with all python types including
    iterators and generators. This function was dreampt up to test API responses
    but could be used for anything. Be careful. With deeply nested structures
    you may blow the stack.

    Options:
              datetime_fudge => this is a datetime.timedelta object which, when
                                comparing dates, will accept values that differ
                                by the number of seconds specified
              _assert        => passing yes for this will raise an assertion error
                                when values do not match, instead of returning
                                false (very useful in combination with pdb)

    """
    _deep_eq = functools.partial(deep_eq, datetime_fudge=datetime_fudge,
                                 _assert=_assert)

    def _check_assert(R, a, b, reason=''):
        # type: (Any, Any, Any, Optional[Text]) -> bool
        if _assert and not R:
            assert 0, "an assertion has failed in deep_eq (%s) %s != %s" % (
                reason, str(a), str(b))
        return R

    def _deep_dict_eq(d1, d2):
        # type: ignore
        k1, k2 = (sorted(d1.keys()), sorted(d2.keys()))
        if k1 != k2:  # keys should be exactly equal
            return _check_assert(False, k1, k2, "keys")

        return _check_assert(operator.eq(sum(_deep_eq(d1[k], d2[k])
                                             for k in k1),
                                         len(k1)), d1, d2, "dictionaries")

    def _deep_iter_eq(l1, l2):
        # type: ignore
        if len(l1) != len(l2):
            return _check_assert(False, l1, l2, "lengths")
        return _check_assert(operator.eq(sum(_deep_eq(v1, v2)
                                             for v1, v2 in zip(l1, l2)),
                                         len(l1)), l1, l2, "iterables")

    def _deep_nd_eq(np1, np2):
        # type: ignore
        if isinstance(np1, np.matrix) or isinstance(np2, np.matrix):
            if not (isinstance(np1, np.matrix)
                    and isinstance(np2, np.matrix)):
                reason = ("the two numpy object have different "
                          "type (np.ndarray vs. np.matrix)")
                return _check_assert(False, np1.shape, np2.shape, reason)

        if np1.shape != np2.shape:
            return _check_assert(False, np1.shape, np2.shape, "shape not equal")

        reason = ""
        try:
            result = np.allclose(np1, np2, equal_nan=True)
            if not result:
                reason = "numpy ndarrays not equal"
            return _check_assert(result, np1, np2, reason)
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                # for cases when the objects are np.matrix instances with nan
                # https://stackoverflow.com/a/28029145/3437454
                np1array = np.asarray(np1)
                np2array = np.asarray(np2)
                result = np.allclose(np1array, np2array, equal_nan=True)
                if not result:
                    reason = "numpy matrices not equal"
                return _check_assert(result, np1, np2, reason)
            else:
                raise

    def op(a, b):
        # type: (Any, Any) -> bool
        _op = operator.eq
        if type(a) == datetime.datetime and type(b) == datetime.datetime:
            s = datetime_fudge.seconds
            t1, t2 = (time.mktime(a.timetuple()), time.mktime(b.timetuple()))
            l = t1 - t2
            l = -l if l > 0 else l
            return _check_assert((-s if s > 0 else s) <= l, a, b, "dates")
        return _check_assert(_op(a, b), a, b, "values")

    c1, c2 = (_v1, _v2)

    # guard against strings because they are iterable and their
    # elements yield iterables infinitely.
    # I N C E P T I O N
    if isinstance(_v1, six.string_types):
        pass
    else:
        if isinstance(_v1, dict):
            op = _deep_dict_eq  # type: ignore
        else:
            if isinstance(_v1, np.ndarray):
                c1, c2 = _v1, _v2
                op = _deep_nd_eq  # type: ignore
            else:
                try:
                    c1, c2 = (list(iter(_v1)), list(iter(_v2)))
                except TypeError:
                    c1, c2 = _v1, _v2
                else:
                    op = _deep_iter_eq  # type: ignore

    return op(c1, c2)
