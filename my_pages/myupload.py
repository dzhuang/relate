# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2015 Dong Zhuang"

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

import django.forms as forms
from django.utils.translation import ugettext as _, string_concat

from course.page.base import (
    AnswerFeedback, markup_to_html, PageBaseWithTitle, PageBaseWithValue,
    PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer)
from course.validation import ValidationError
from course.content import get_repo_blob, get_repo_blob_data_cached
from course.constants import participation_permission as pperm
from course.page.upload import FileUploadForm, FileUploadQuestion
# {{{ mine customized

from relate.utils import StyledForm, dict_to_struct

from yaml import load as load_yaml
from bs4 import BeautifulSoup
import hashlib
import base64
import re
import os

from crispy_forms.layout import Layout, Field

COURSE_STAFF_PERMISSION = (
    (pperm.assign_grade, None),
)


MIMETYPE_EXT_MAP = {
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-word.document.macroEnabled.12": ".docm",
    "text/plain": ".txt",
    "application/vnd.ms-excel.sheet.macroEnabled.12": ".xlsm",
    "application/zip": ".zip",
    "application/pdf": ".pdf"
}


def correct_error_id(soup):
    if len(soup.find_all(id="reference")) > 1:
        ele1 = soup.findAll(id="reference")[0]
        ele1['id'] = 'crossreference'
    if len(soup.find_all(id="litermethod")) > 1:
        ele2 = soup.findAll(id="litermethod")[0]
        ele2['id'] = 'crosstime'


def id_list(soup):
    result = []
    for tag in soup.find_all(True, {'id': True}):
        result.append(tag['id'])
    return result


def idname(soup, the_id):
    items = soup.find_all(id=the_id)
    if len(items) == 1:
        item, = items
        content = item.contents[0]
        if u'\u2003\u2003' in content:
            li_ascii = content.split(u'\u2003\u2003')
            return li_ascii[0]
        else:
            return content
    elif len(items) > 1:
        result = []
        for item in items:
            content = item.contents[0]
            if u'\u2003\u2003' in content:
                li_ascii = content.split(u'\u2003\u2003')
                result.append(li_ascii[0])
            else:
                result.append(content)
        return result


def idvalue(soup, the_id):
    item = soup.find(id=the_id)
    if item:
        if len(item.contents) > 0:
            content = item.contents[0]
            if u'\u2003\u2003' in content:
                li_ascii = content.split(u'\u2003\u2003')

                # when the value is not a number
                if the_id in ['encrypt1', 'encrypt2', 'authcode', 'litermethod']:
                    return li_ascii[1]
                elif the_id == 'noevenodd':
                    if li_ascii[1] == u"无":
                        return 0
                    else:
                        string_noevenodd = li_ascii[1]
                        list_noevenodd = string_noevenodd.split(" ")
                        n_noevenodd = len(list_noevenodd)
                        return n_noevenodd
                elif li_ascii[1] == "True":
                    return True
                elif li_ascii[1] == "False":
                    return False
                elif re.match("^[-0-9]+$", li_ascii[1]):
                    return int(li_ascii[1])
                elif re.match("^[-0-9.]+$", li_ascii[1]):
                    return float(li_ascii[1])
                else:
                    return None
            else:
                if the_id == 'authcode':
                    return content
                elif the_id == 'checkfile_version':
                    return content
                else:
                    return None
        else:
            return None
    else:
        return None


def get_unmasked_answer_html(answer_data):
    masked_string = base64.b64decode(answer_data)
    return get_unmasked_string(masked_string)


def get_unmasked_string(masked_string):
    truestring = masked_string[1:-1]
    return base64.b64decode(truestring)

# }}}


# {{{ my upload question

class myFileUploadForm(StyledForm):
    show_save_button = False
    uploaded_file = forms.FileField(required=True, label=_('Uploaded file'))

    def __init__(self, maximum_megabytes, mime_types, *args, **kwargs):
        super(myFileUploadForm, self).__init__(*args, **kwargs)
        self.max_file_size = maximum_megabytes * 1024**2
        self.mime_types = list(set(mime_types))

        # 'accept=' doesn't work right for at least application/octet-stream.
        # We'll start with a blacklist.
        allow_accept = True
        if "application/octet-stream" in mime_types:
            allow_accept = False

        field_kwargs = {}
        if allow_accept:
            field_kwargs["accept"] = ",".join(self.mime_types)

        self.helper.layout = Layout(
                Field("uploaded_file", **field_kwargs))

    def clean_uploaded_file(self):
        uploaded_file = self.cleaned_data['uploaded_file']
        from django.template.defaultfilters import filesizeformat

        if uploaded_file._size > self.max_file_size:
            raise forms.ValidationError(
                _("Please keep file size under %(allowedsize)s. "
                  "Current filesize is %(uploadedsize)s.")
                % {'allowedsize': filesizeformat(self.max_file_size),
                   'uploadedsize': filesizeformat(uploaded_file._size)})

        if self.mime_types == ["application/pdf"]:
            if uploaded_file.read()[:4] != "%PDF":
                raise forms.ValidationError(_("Uploaded file is not a PDF."))
        elif "application/octet-stream" in self.mime_types:
            pass
        else:
            accept_ext_list = [
                v.lower() for (k ,v) in MIMETYPE_EXT_MAP.items()
                if k in self.mime_types]
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext and ext not in accept_ext_list:
                raise forms.ValidationError(
                    "文件类型不支持！请上传后缀为%s的文档！"
                    % ", ".join(accept_ext_list)
                )
        return uploaded_file


class CustomFileUploadQuestion(FileUploadQuestion):
    # Override default FileUploadQuestion to allow more mime-type

    ALLOWED_MIME_TYPES = [
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel.sheet.macroEnabled.12",
        "application/vnd.ms-word.document.macroEnabled.12",
        "application/octet-stream",
        "application/zip",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    def __init__(self, vctx, location, page_desc):
        super(CustomFileUploadQuestion, self).__init__(vctx, location, page_desc)

        if not (set(page_desc.mime_types) <= set(self.ALLOWED_MIME_TYPES)):
            raise ValidationError(
                string_concat(
                    "%(location)s: ",
                    _("unrecognized mime types"),
                    " '%(presenttype)s'")
                % {
                    'location': location,
                    'presenttype': ", ".join(
                        set(page_desc.mime_types)
                        - set(self.ALLOWED_MIME_TYPES))})

    def make_form(self, page_context, page_data,
                  answer_data, page_behavior):
        form = myFileUploadForm(
            self.page_desc.maximum_megabytes, self.page_desc.mime_types)
        return form

    def process_form_post(self, page_context, page_data, post_data, files_data,
                          page_behavior):
        form = myFileUploadForm(
            self.page_desc.maximum_megabytes, self.page_desc.mime_types,
            post_data, files_data)
        return form

    def normalized_bytes_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None

        ext = None
        if len(self.page_desc.mime_types) == 1:
            mtype, = self.page_desc.mime_types
            from mimetypes import guess_extension
            ext = guess_extension(mtype)
            if ext is None:
                ext = MIMETYPE_EXT_MAP.get(mtype, None)

        if ext is None:
            ext = ".dat"

        from base64 import b64decode
        return (ext, b64decode(answer_data["base64_data"]))

# }}}


class WordUploadPreviewQuestion(CustomFileUploadQuestion):
    ALLOWED_MIME_TYPES = [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    def doc_data_to_pdf_b64_data(self, word_data):
        from plugins.latex.converter import convert_doc_to_pdf_blob
        from base64 import b64encode
        pdf_data = convert_doc_to_pdf_blob(word_data)
        if pdf_data:
            return b64encode(pdf_data).decode()
        return None

    def files_data_to_answer_data(self, files_data):
        files_data = super(WordUploadPreviewQuestion, self
                           ).files_data_to_answer_data(files_data)
        from base64 import b64decode
        word_data = b64decode(files_data["base64_data"])
        pdf_b64_data = self.doc_data_to_pdf_b64_data(word_data)
        if pdf_b64_data:
            files_data["pdf_base64_data"] = self.doc_data_to_pdf_b64_data(word_data)
        # for linux
        # https://serverfault.com/questions/338087/making-libmagic-file-detect-docx-files
        try:
            # windows
            from winmagic import magic
        except ImportError:
            import magic

        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(word_data)
        if mime_type == "application/msword":
            files_data["mime_type"] = "application/msword"
        elif mime_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            # https://serverfault.com/questions/338087/making-libmagic-file-detect-docx-files
            "application/zip"]:
            files_data["mime_type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return files_data

    def form_to_html(self, request, page_context, form, answer_data):
        ctx = {"form": form}
        if answer_data is not None:
            ctx["mime_type"] = answer_data["mime_type"]
            ctx["data_url"] = "data:%s;base64,%s" % (
                answer_data["mime_type"],
                answer_data["base64_data"],
                )
            if (answer_data.get("pdf_base64_data")
                    and answer_data["mime_type"] != "application/pdf"):
                ctx["pdf_data_url"] = "data:%s;base64,%s" % (
                    "application/pdf",
                    answer_data["pdf_base64_data"],
                    )

                # generate pdf preview

                page_ordinal = None
                if not page_context.in_sandbox:
                    from image_upload.utils import get_ordinal_from_page_context
                    page_ordinal = get_ordinal_from_page_context(page_context)

                in_grading_page = False
                try:
                    from django.urls import reverse, NoReverseMatch
                    grading_page_uri = reverse(
                        "relate-grade_flow_page",
                        args=(
                            page_context.course.identifier,
                            page_context.flow_session.id,
                            page_ordinal)
                    )

                    in_grading_page = grading_page_uri == request.path
                except NoReverseMatch:
                    if page_context.in_sandbox:
                        pass
                    else:
                        raise

                if in_grading_page:
                    ctx["in_grading_page"] = True

        from django.template.loader import render_to_string
        return render_to_string(
                "course/file-upload-form-with-pdf-preview.html", ctx, request)


    def normalized_bytes_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None

        mtype = page_data["mime_types"]
        from mimetypes import guess_extension
        ext = guess_extension(mtype)

        if ext is None:
            ext = ".dat"

        from base64 import b64decode
        return (ext, b64decode(answer_data["base64_data"]))


class WordUploadQuestion(PageBaseWithTitle, PageBaseWithValue,
        PageBaseWithHumanTextFeedback, PageBaseWithCorrectAnswer):
    ALLOWED_MIME_TYPES = [
        "text/plain",
        "application/msword",
        "application/vnd.ms-word.document.macroEnabled.12",
    ]

    def __init__(self, vctx, location, page_desc):
        super(WordUploadQuestion, self).__init__(vctx, location, page_desc)

        self.word_mime_type = getattr(
            page_desc, "word_mime_type",
            "application/vnd.ms-word.document.macroEnabled.12")
        self.txt_mime_type = getattr(
            page_desc, "txt_mime_type", "text/plain")

        from django.core.exceptions import ObjectDoesNotExist

        if vctx is not None:
            if hasattr(page_desc, "criteria"):
                try:
                    if not isinstance(page_desc.criteria, str):
                        raise ObjectDoesNotExist()
                    get_repo_blob(vctx.repo, page_desc.criteria, vctx.commit_sha)
                except ObjectDoesNotExist:
                    raise ValidationError("%s: criteria file '%s' not found"
                                          % (location, page_desc.criteria))

            if hasattr(page_desc, "demo_html"):
                try:
                    if not isinstance(page_desc.demo_html, str):
                        raise ObjectDoesNotExist()
                    get_repo_blob(vctx.repo, page_desc.demo_html, vctx.commit_sha)
                except ObjectDoesNotExist:
                    raise ValidationError("%s: demo_html file '%s' not found"
                                          % (location, page_desc.demo_html))

            if hasattr(page_desc, "mime_types"):
                vctx.add_warning(
                    location,
                    _("%s had deprecate the attribute 'mime_types',"
                      "use 'word_mime_type' and 'txt_mime_type' instead")
                      % self.__class__.__name__)

            if hasattr(page_desc, "maximum_megabytes"):
                vctx.add_warning(
                    location,
                    _("%s had deprecate the attribute 'maximum_megabytes',"
                      "use 'word_maximum_megabytes'instead")
                      % self.__class__.__name__)

            if hasattr(page_desc, "txt_maximum_megabytes"):
                vctx.add_warning(
                    location,
                    _("%s had deprecate the attribute 'txt_maximum_megabytes',"
                      "use 'txt_maximum_megabytes'instead")
                      % self.__class__.__name__)

            for mime_type in [self.word_mime_type, self.txt_mime_type]:
                if mime_type not in self.ALLOWED_MIME_TYPES:
                    raise ValidationError(
                        string_concat(
                            "%(location)s: ",
                            _("unrecognized mime types"),
                            " '%(presenttype)s'")
                        % {
                            'location': location,
                            'presenttype': mime_type,
                        })

            if not hasattr(page_desc, "value"):
                vctx.add_warning(location, _("upload question does not have "
                                             "assigned point value"))

        self.word_maximum_megabytes = getattr(
            page_desc, "word_maximum_megabytes", 2
        )
        self.txt_maximum_megabytes = getattr(
            page_desc, "txt_maximum_megabytes", 0.5
        )

        self.display_criteria = ""
        self.display_feedback = ""

    def required_attrs(self):
        return super(WordUploadQuestion, self).required_attrs() + (
                ("prompt", "markup"),
                )

    def allowed_attrs(self):
        return super(WordUploadQuestion, self).allowed_attrs() + (
            ("show_my_word_file", bool),
            ("criteria", str),
            ("demo_html", str),
            ("txt_maximum_megabytes", (int, float)),
            ("same_as_sample", bool),
            ("word_mime_type", str),
            ("txt_mime_type", str),
            ("word_maximum_megabytes", (int, float)),
            ("txt_maximum_megabytes", (int, float)),
        )

    def markup_body_for_title(self):
        return self.page_desc.prompt

    def body(self, page_context, page_data):
        body_temp = markup_to_html(page_context, self.page_desc.prompt)

        show_my_word_file = getattr(self.page_desc, "show_my_word_file", False)

        if show_my_word_file:

            if page_context.flow_session.participation.user.institutional_id:
                filename = page_context.flow_session.participation.user.institutional_id + ".docm"
                file_html = (
                    u"<div><p class='h3'>待排版文档下载"
                    u"<a href='repo:resource/docs/my_word_file/%s'>"
                    u"<i class='fa fa-download'></i>下载</a></p>"
                    u"<p class='warning'>"
                    u"如果没有待排版文档（404错误），请尽快与老师联系."
                    u"</p></div>" % filename)
            else:
                file_html = (
                    u"<div><p class='h3'>待排版文档下载"
                    u"<a href='repo:resource/docs/my_word_file/none.docm'>"
                    u"<i class='fa fa-download'></i>下载</a></p>"
                    u"<p class='warning'>"
                    u"如果没有待排版文档（404错误），请尽快与老师联系."
                    u"</p></div>")

            body_temp += markup_to_html(page_context, file_html)

        if (hasattr(self.page_desc, "criteria")
            and
                hasattr(self.page_desc, "demo_html")):
            body_temp += (
                u"<div class='accordion'>"
                u"<h3>评分标准</h3>"
                u"<div><ol>%s</ol></div> </div><br/>"
                % self.body_append(page_context)
            )

        return body_temp

    def body_append(self, page_context):
        demo_html = get_repo_blob_data_cached(
            page_context.repo,
            self.page_desc.demo_html,
            page_context.commit_sha)

        soup = BeautifulSoup(demo_html, "html5lib")
        correct_error_id(soup)
        all_id = id_list(soup)

        all_criteria = dict_to_struct(
            load_yaml(
                get_repo_blob_data_cached(
                    page_context.repo,
                    self.page_desc.criteria,
                    page_context.commit_sha)
            )
        )

        for the_id in all_id:
            attrib = getattr(all_criteria, the_id, None)
            if not attrib:
                continue
            if not attrib.use:
                continue
            if not getattr(attrib, "type", None):
                continue
            if attrib.type == "boolean":
                self.append_display(attrib, u"标准:" + str(
                    attrib.standard) + u", 否则扣分:" + str(-attrib.credit))
            elif attrib.type == "max":
                if attrib.per == True:
                    self.append_display(attrib, u"标准:不超过" + str(
                        attrib.standard) + u"处, 每超1处扣分:" + str(
                        -attrib.credit))
                else:
                    self.append_display(attrib, u"标准:不超过" + str(
                        attrib.standard) + u"处, 超出扣分:" + str(
                        -attrib.credit))
            elif attrib.type == "min":
                if attrib.per == True:
                    self.append_display(attrib, u"标准:不少于" + str(
                        attrib.standard) + u"处, 每少1处扣分:" + str(
                        -attrib.credit))
                else:
                    self.append_display(attrib, u"标准:不少于" + str(
                        attrib.standard) + u"处, 不足扣分:" + str(
                        -attrib.credit))
            elif attrib.type == "text":
                if attrib.per == True:
                    self.append_display(attrib, u"标准:" + str(
                        attrib.standard) + u", 每错1处扣分:" + str(
                        -attrib.credit))
                else:
                    self.append_display(attrib, u"标准:" + str(
                        attrib.standard) + u", 否则扣分:" + str(
                        -attrib.credit))
        return self.display_criteria

    def append_display(self, attrib, append_str):
        if attrib.display == True:
            self.display_criteria += (
                u"<li><b>%s</b> %s</li>" % (attrib.fullname, append_str))

    def append_feedback(self, attrib, append_str):
        if attrib.display == True:
            self.display_feedback += (
                u"<li><b>%s</b> %s</li>" % (attrib.fullname, append_str))

    def files_data_to_answer_data(self, files_data):
        files_data["word_file"].seek(0)
        buf = files_data["word_file"].read()
        files_data["check_file"].seek(0)
        buf2 = files_data["check_file"].read()

        md5string = hashlib.md5(buf).hexdigest()
        md5string2 = hashlib.md5(buf).hexdigest()
        sha1string = hashlib.sha1(buf).hexdigest()
        sha1string2 = hashlib.sha1(buf).hexdigest()

        from base64 import b64encode
        return {
            "base64_data": b64encode(buf).decode(),
            "mime_type": self.word_mime_type,
            "md5": md5string,
            "sha1": sha1string,
            "base64_data2": b64encode(buf2).decode(),
            "txt_mime_type": self.txt_mime_type,
            "md52": md5string2,
            "sha12": sha1string2,
        }

    def make_form(self, page_context, page_data,
                  answer_data, page_behavior):
        form = WordUploadForm(
            self.word_maximum_megabytes,
            self.word_mime_type,
            self.txt_maximum_megabytes,
            self.txt_mime_type,
            page_context.flow_session.participation.user.institutional_id,
            self._get_version(page_context),
            page_context.flow_session.participation.user.is_superuser
        )
        return form

    def process_form_post(self, page_context, page_data, post_data, files_data,
                          page_behavior):
        form = WordUploadForm(
            self.word_maximum_megabytes,
            self.word_mime_type,
            self.txt_maximum_megabytes,
            self.txt_mime_type,
            page_context.flow_session.participation.user.institutional_id,
            self._get_version(page_context),
            page_context.flow_session.participation.user.is_superuser,
            post_data,
            files_data
        )
        return form

    def form_to_html(self, request, page_context, form, answer_data):
        ctx = {"form": form}
        if answer_data is not None:
            ctx["mime_type"] = answer_data["mime_type"]
            ctx["data_url"] = "data:%s;base64,%s" % (
                answer_data["mime_type"],
                answer_data["base64_data"],
            )

        from django.template.loader import render_to_string
        return render_to_string(
            "course/file-upload-form.html",
            ctx, request)

    def _get_all_criteria(self, page_context):
        all_criteria = dict_to_struct(
            load_yaml(
                get_repo_blob_data_cached(
                    page_context.repo,
                    self.page_desc.criteria,
                    page_context.commit_sha)
            )
        )

        return all_criteria

    def _get_version(self, page_context):
        all_criteria = self._get_all_criteria(page_context)
        version_offset = all_criteria.checkfile_version.standard
        return version_offset

    def get_edit_grade(self, page_context, page_data, answer_data):
        edit_grade = {}
        if get_unmasked_answer_html(answer_data["base64_data2"]) is None:
            edit_grade["correctness"] = 0
            edit_grade["bulk_feedback"] = (
                u"<p>上传的文件不是自动生成的校验码</p>")
            return dict_to_struct(edit_grade)

        same_as_sample = getattr(self.page_desc, "same_as_sample", False)
        if same_as_sample:
            demo_html = get_repo_blob_data_cached(
                page_context.repo,
                self.page_desc.demo_html,
                page_context.commit_sha)
            soup_id = BeautifulSoup(demo_html, "html5lib")
            correct_error_id(soup_id)
            all_id = id_list(soup_id)
        else:
            soup = BeautifulSoup(
                get_unmasked_answer_html(answer_data["base64_data2"]),
                "html5lib")
            all_id = id_list(soup)

        soup = BeautifulSoup(
            get_unmasked_answer_html(answer_data["base64_data2"]), "html5lib")
        correct_error_id(soup)
        total_percent = 100
        minus_points = 0
        all_criteria = self._get_all_criteria(page_context)

        for the_id in all_id:
            attrib = getattr(all_criteria, the_id, None)
            if not attrib:
                continue
            real_value = idvalue(soup, the_id)
            if real_value is None:
                continue
            if not attrib.use:
                continue
            if not hasattr(attrib, "type"):
                continue
            if attrib.type == "boolean":
                if real_value != attrib.standard:
                    minus_points += abs(attrib.credit)
                    self.append_feedback(
                        attrib,
                        u"标准:%s, 扣分:%s; "
                        u"<tag style='color:red'>结果: 扣%s分</tag>."
                        % (attrib.standard, abs(attrib.credit), abs(attrib.credit)))
            elif attrib.type == "max":
                if real_value > attrib.standard:
                    if attrib.per:
                        minus_points += abs(
                            (real_value - attrib.standard) * attrib.credit)
                        self.append_feedback(
                            attrib,
                            u"标准:不超过%s处, 每超1处扣分:%s; "
                            u"<tag style='color:red'>结果: 扣%s分</tag>."
                            % (
                                attrib.standard,
                                abs(attrib.credit),
                                abs((
                                    real_value - attrib.standard) * attrib.credit))
                        )
                    else:
                        minus_points += abs(attrib.credit)
                        self.append_feedback(
                            attrib,
                            u"标准:不超过%s处, 超出扣分:%s; "
                            u"<tag style='color:red'>结果: 扣%s分</tag>."
                            % (
                                attrib.standard,
                                abs(attrib.credit),
                                abs(attrib.credit)
                            )
                        )
            elif attrib.type == "min":
                if real_value < attrib.standard:
                    if attrib.per:
                        minus_points += abs(
                            (real_value - attrib.standard) * attrib.credit)
                        self.append_feedback(
                            attrib,
                            u"标准:不少于%s处, 每少1处扣分:%s; "
                            u"<tag style='color:red'>结果: 扣%s分</tag>."
                            % (
                                attrib.standard,
                                abs(attrib.credit),
                                abs((real_value - attrib.standard) * attrib.credit))
                        )
                    else:
                        minus_points += abs(attrib.credit)
                        self.append_feedback(
                            attrib,
                            u"标准:不少于%s处, 不足扣分:%s; "
                            u"<tag style='color:red'>结果: 扣%s分</tag>."
                            % (
                                attrib.standard,
                                abs(attrib.credit),
                                abs(attrib.credit)
                            )
                        )
            elif attrib.type == "text":
                if real_value == attrib.standard:
                    continue

                # there's no per for "参考文献"
                minus_points += abs(attrib.credit)
                self.append_feedback(
                    attrib,
                    u"标准:%s, 否则扣分:%s; "
                    u"<tag style='color:red'>结果: 扣%s分</tag>."
                    % (
                        attrib.standard,
                        abs(attrib.credit),
                        abs(attrib.credit)
                    )
                )
        correctness = (total_percent - minus_points) / 100
        if correctness < 0:
            correctness = 0

        edit_grade["correctness"] = correctness
        edit_grade["bulk_feedback"] = self.display_feedback

        return dict_to_struct(edit_grade)

    def get_nonhuman_feedback(self, page_context, page_data, answer_data):
        correctness = None
        feedback = None

        if answer_data is not None:
            nonhuman_feedback = self.get_edit_grade(page_context, page_data,
                                                    answer_data)
            correctness = nonhuman_feedback.correctness
            bulk_feedback = nonhuman_feedback.bulk_feedback
            auto_feedback = u"<p>你得到了总分数的 %.1f %% .</p>" % (correctness * 100)
            if correctness == 1:
                feedback = auto_feedback
            else:
                feedback = "".join(
                    [auto_feedback, u"<p>以下是扣分的情况(百分制)：</p>", bulk_feedback])

        return AnswerFeedback(
            correctness=correctness,
            feedback=feedback
        )

    def grade(self, page_context, page_data, answer_data, grade_data):
        if answer_data is None:
            return AnswerFeedback(correctness=0,
                                  feedback=_("No answer provided."))

        if grade_data is not None and not grade_data["released"]:
            grade_data = None

        code_feedback = self.get_nonhuman_feedback(page_context, page_data,
                                                   answer_data)

        total_points = self.page_desc.value
        human_points = total_points
        code_points = total_points

        correctness = None
        percentage = None
        if (code_feedback is not None
            and code_feedback.correctness is not None
            and grade_data is not None
            and grade_data["grade_percent"] is not None):
            correctness = (
                              code_feedback.correctness * total_points
                              + grade_data["grade_percent"] / 100
                              * total_points
                          ) / total_points
            percentage = correctness * 100
        elif (code_feedback is not None
              and code_feedback.correctness is not None
              and grade_data is None):
            correctness = code_feedback.correctness
            percentage = correctness * 100

        human_feedback_percentage = None
        human_feedback_text = None

        human_feedback_points = None
        if grade_data is not None:
            if grade_data["feedback_text"] is not None:
                human_feedback_text = markup_to_html(
                    page_context, grade_data["feedback_text"])

            human_feedback_percentage = grade_data["grade_percent"]
            if human_feedback_percentage is not None:
                human_feedback_points = (human_feedback_percentage / 100.
                                         * human_points)

        code_feedback_points = None
        if (code_feedback is not None
            and code_feedback.correctness is not None):
            code_feedback_points = code_feedback.correctness * code_points

        from django.template.loader import render_to_string
        feedback = render_to_string(
            "course/feedback-code-with-human.html",
            {
                "percentage": percentage,
                "code_feedback": code_feedback,
                "code_feedback_points": code_feedback_points,
                "code_points": code_points,
                "human_feedback_text": human_feedback_text,
                "human_feedback_points": human_feedback_points,
                "human_points": human_points,
            })

        return AnswerFeedback(
            correctness=correctness,
            feedback=feedback,
        )

    def answer_data(self, page_context, page_data, form, files_data):
        return self.files_data_to_answer_data(files_data)

    def human_feedback_point_value(self, page_context, page_data):
        return self.max_points(page_data)

    def normalized_bytes_answer(self, page_context, page_data, answer_data):
        if answer_data is None:
            return None

        mtype = self.word_mime_type
        from mimetypes import guess_extension
        ext = guess_extension(mtype)

        if ext is None:
            ext = MIMETYPE_EXT_MAP.get(self.word_mime_type, ".dat")

        from base64 import b64decode
        return (ext, b64decode(answer_data["base64_data"]))

# }}}


class WordUploadForm(StyledForm):
    show_save_button = False
    word_file = forms.FileField(required=True, label='.docm排版文档')
    check_file = forms.FileField(required=True, label='txt校验文档')

    def __init__(self, word_maximum_megabytes, word_mime_type,
                 txt_maximum_megabytes, txt_mime_type,
                 institutional_id, base_version, is_course_staff, *args,
                 **kwargs):
        super(WordUploadForm, self).__init__(*args, **kwargs)

        self.word_max_file_size = word_maximum_megabytes * 1024 ** 2
        self.word_mime_type = word_mime_type
        if word_mime_type is None:
            self.word_mime_type = (
                "application/vnd.ms-word.document.macroEnabled.12")
        self.txt_max_file_size = txt_maximum_megabytes * 1024 ** 2
        self.txt_mime_type = txt_mime_type
        if txt_mime_type is None:
            self.txt_mime_type = "text/plain"
        self.institutional_id = institutional_id
        self.base_version = base_version
        self.is_course_staff = is_course_staff

        self.helper.layout = Layout(
            Field("word_file", accept=word_mime_type),
            Field("check_file", accept=txt_mime_type),
        )

    def clean_word_file(self):
        word_file = self.cleaned_data.get('word_file')
        from django.template.defaultfilters import filesizeformat

        if word_file._size > self.word_max_file_size:
            raise forms.ValidationError(
                _("Please keep file size under %(allowedsize)s. "
                  "Current filesize is %(uploadedsize)s.")
                % {'allowedsize': filesizeformat(self.word_max_file_size),
                   'uploadedsize': filesizeformat(word_file._size)})

        ext = os.path.splitext(word_file.name)[1].lower()
        expected_ext = MIMETYPE_EXT_MAP.get(self.word_mime_type, "").lower()
        if ext != expected_ext:
            raise forms.ValidationError(
                "文件类型不支持！请上传后缀为%s的文档！" % expected_ext)
        return word_file

    def clean_check_file(self):
        check_file = self.cleaned_data['check_file']
        from django.template.defaultfilters import filesizeformat

        if check_file._size > self.txt_max_file_size:
            raise forms.ValidationError(
                _("Please keep file size under %(allowedsize)s. "
                  "Current filesize is %(uploadedsize)s.")
                % {'allowedsize': filesizeformat(self.txt_max_file_size),
                   'uploadedsize': filesizeformat(check_file._size)})

        ext = os.path.splitext(check_file.name)[1].lower()
        expected_ext = MIMETYPE_EXT_MAP.get(self.txt_mime_type, "").lower()
        if ext != expected_ext:
            raise forms.ValidationError(
                "文件类型不支持！请上传后缀为%s的文档！" % expected_ext)

        from binascii import Error as binError
        try:
            string = check_file.read()
            truestring = get_unmasked_string(string)
        except (TypeError, binError):
            raise forms.ValidationError(
                "文件无效，请上传自动生成的校验文件！")

        soup = BeautifulSoup(truestring, "html5lib")

        if not self.institutional_id and not self.is_course_staff:
            raise forms.ValidationError(
                u"请在您的<a href='/profile/'>个人信息</a>"
                u"中添加学号后再提交作业！")
        if idvalue(soup, 'authcode') != self.institutional_id:
            if not self.is_course_staff:
                raise forms.ValidationError(
                    u"学号不符，请确认验证文档由你自己编辑的文档生成的！")

        word_file = self.cleaned_data.get('word_file')
        if word_file is None:
            raise forms.ValidationError(
                "找不到word文件，请确定表单中上传了word文件！")
        buf = word_file.read()
        md5string = hashlib.md5(buf).hexdigest()
        sha1string = hashlib.sha1(buf).hexdigest()
        parsed_md5 = idvalue(soup, 'encrypt1')
        parsed_sha1 = idvalue(soup, 'encrypt2')
        checkfile_version = idvalue(soup, 'checkfile_version')

        try:
            checkfile_version = float(checkfile_version)
        except TypeError:
            raise forms.ValidationError(
                "文件无效，请上传自动生成的校验文件！")

        if (not checkfile_version
            or
                checkfile_version < self.base_version
            ):
            raise forms.ValidationError(
                u"文档检查工具版本过低，"
                u"请使用%s以上的版本生成校验文件！"
                % self.base_version
            )

        if not (parsed_md5 == md5string or parsed_sha1 == sha1string):
            raise forms.ValidationError("校验文件与上传的word文档不匹配！")

        return check_file

# vim: foldmethod=marker
