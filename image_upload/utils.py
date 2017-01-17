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

from django.contrib.auth.mixins import UserPassesTestMixin

from course.flow import (
        get_page_behavior, get_and_check_flow_session,
        get_prev_answer_visits_qset)
from course.utils import (
        FlowPageContext, get_session_access_rule,
        get_session_grading_rule)
from course.views import get_now_or_fake_time
from course.utils import CoursePageContext

import zipfile

# extracted from course.flow
def get_page_image_behavior(pctx, flow_session_id, ordinal):
    
    if ordinal == "None" and flow_session_id == "None":
        from course.page.base import PageBehavior
        return PageBehavior(
            show_correctness=True,
            show_answer=True,
            may_change_answer=True,
        )

    request = pctx.request

    ordinal = int(ordinal)

    flow_session_id = int(flow_session_id)
    flow_session = get_and_check_flow_session(pctx, flow_session_id)
    flow_id = flow_session.flow_id

    fpctx = FlowPageContext(pctx.repo, pctx.course, flow_id, ordinal,
            participation=pctx.participation,
            flow_session=flow_session,
            request=pctx.request)

    now_datetime = get_now_or_fake_time(request)
    access_rule = get_session_access_rule(
            flow_session, fpctx.flow_desc, now_datetime,
            facilities=pctx.request.relate_facilities)

    grading_rule = get_session_grading_rule(
            flow_session, fpctx.flow_desc, now_datetime)
    generates_grade = (
            grading_rule.grade_identifier is not None
            and
            grading_rule.generates_grade)

    del grading_rule

    permissions = fpctx.page.get_modified_permissions_for_page(
            access_rule.permissions)

    answer_visit = None
    prev_visit_id = None

    prev_answer_visits = list(
            get_prev_answer_visits_qset(fpctx.page_data))

    # {{{ fish out previous answer_visit

    prev_visit_id = pctx.request.GET.get("visit_id")
    if prev_visit_id is not None:
        prev_visit_id = int(prev_visit_id)

    viewing_prior_version = False
    if prev_answer_visits and prev_visit_id is not None:
        answer_visit = prev_answer_visits[0]

        for ivisit, pvisit in enumerate(prev_answer_visits):
            if pvisit.id == prev_visit_id:
                answer_visit = pvisit
                if ivisit > 0:
                    viewing_prior_version = True

                break

        prev_visit_id = answer_visit.id

    elif prev_answer_visits:
        answer_visit = prev_answer_visits[0]
        prev_visit_id = answer_visit.id

    else:
        answer_visit = None

    # }}}

    if answer_visit is not None:
        answer_was_graded = answer_visit.is_submitted_answer
    else:
        answer_was_graded = False

    page_behavior = get_page_behavior(
            page=fpctx.page,
            permissions=permissions,
            session_in_progress=flow_session.in_progress,
            answer_was_graded=answer_was_graded,
            generates_grade=generates_grade,
            is_unenrolled_session=flow_session.participation is None,
            viewing_prior_version=viewing_prior_version)

    return page_behavior


class ImageOperationMixin(UserPassesTestMixin):
    # Mixin for determin if user can upload/delete/modify image in flow_page
    raise_exception = True

    def test_func(self):
        request = self.request
        flow_session_id = self.kwargs['flow_session_id']
        ordinal = self.kwargs['ordinal']
        course_identifier = self.kwargs['course_identifier']

        pctx = CoursePageContext(request, course_identifier)
        
        try:
            return get_page_image_behavior(pctx, flow_session_id, ordinal).may_change_answer
        except ValueError:
            return True

# {{{

from django import forms
from django.template import Context
from django.template.loader import get_template
from django.contrib.admin import widgets

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
                #'name': "comment",
             }
        )
        #attrs.update({"autofocus": ""})

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
from django.db.models import Transform
from django.db.models import CharField, TextField

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
        f = file(filename, "w")
        f.write(self.read())
        f.close()

# }}}
