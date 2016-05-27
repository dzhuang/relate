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

import six
import os
import sys
import re
import errno
from subprocess import Popen, PIPE
import shutil
from hashlib import md5

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import (
    ugettext as _, string_concat)
from django.conf import settings
from django.core.management.base import CommandError
from django.utils.encoding import (
    DEFAULT_LOCALE_ENCODING, force_text)
from django.utils.functional import cached_property

from .utils import popen_wrapper
from .parse import TexDoc

# {{{ Constants

from .utils import (
    LATEX_ERR_LOG_BEGIN_LINE_STARTS,
    LATEX_ERR_LOG_END_LINE_STARTS, DEFAULT_IMG_HTML_CLASS, prepend_bin_path_to_subprocess_env, _file_read, _file_write, get_abstract_latex_log)

CMD_NAME_DICT = {
    "latex": "latex",
    "xelatex": "latex",
    "pdflatexx": "latex",
    "latexmk": "latex",
    "convert": "ImageMagick",
    "dvipng": "latex",
    "dvisvgm": "latex"}

ALLOWED_COMPILER = ['latex', 'pdflatex', 'xelatex']
ALLOWED_LATEX2IMG_FORMAT = ['png', 'svg']

ALLOWED_COMPILER_FORMAT_COMBINATION = (
    ("latex", "png"),
    ("latex", "svg"),
    ("pdflatex", "png"),
    ("xelatex", "png")
)

DEFAULT_IMG_HTML_CLASS = "img-responsive"


# {{{ latex code re

PAGE_EMPTY_RE = re.compile(r"\n[^%]*\\pagestyle\{empty\}")
BEGIN_DOCUMENT_RE = re.compile(r"\n(\s*)(\\begin\{document\})")
TIKZ_PGF_RE = re.compile(r"\n[^%]*\\begin\{(?:tikzpicture|pgfpicture)\}")

IS_FULL_DOC_RE = re.compile(r"(?:^|\n)\s*\\documentclass(?:.|\n)*"
                            r"\n\s*\\begin\{document\}(?:.|\n)*"
                            r"\n\s*\\end\{document\}")

DOC_ELEMENT_RE_LIST = [(r"'\documentclass'", re.compile(r"(?:^|\n)\s*\\documentclass")),
                       (r"'\begin{document}'", re.compile(r"\n\s*\\begin\{document\}")),
                       (r"'\end{document}'", re.compile(r"\n\s*\\end\{document\}"))]

# }}}


# }}}


# {{{ convert file to data uri

def get_file_data_uri(file_path):
    '''Convert file to data URI'''
    if not file_path:
        return None

    from base64 import b64encode
    from mimetypes import guess_type
    buf = _file_read(file_path)
    mime_type = guess_type(file_path)[0]

    return "data:%(mime_type)s;base64,%(b64)s" % {
        "mime_type": mime_type,
        "b64": b64encode(buf).decode(),
    }

# }}}


# {{{ Base class

class Tex2ImgBase(object):
    """The abstract class of converting tex source to images.

    .. attribute:: tex_compiler

        A required string of the command for compiling tex
        source. Currently implemented: 'latex', 'pdflatex', 'xelatex'

    .. attribute:: mid_step_media_type:

        A required string representing the media type of
        the mid-step converting tex source to images. For example
        Tex --> DVI --> PNG, then 'dvi' is the attribute.
        Allowed values are 'dvi' and 'pdf'.

    .. attribute:: image_converter_name:

        A string representing the name of the tool for image
        conversion. Currently implemented: 'dvisvgm', 'dvipng'
        and 'imagemagick'. The string is used to generate exception
        information.

        The former 2 is used to convert DVI
        to images, with dvisvgm converting DVIs generated including
        tikz or pgf packages. imagemagick is used to convert
        PDFs to images (currently only PNG). The order of image quality
        of images is dvisvgm > dvipng > imagemagick, while better
        quality is at the cost of long computation/rendering time.


    .. automethod:: required_attrs
    .. automethod:: allowed_attrs

    """

    @property
    def tex_compiler(self):
        raise NotImplementedError()

    @property
    def image_converter(self):
        raise NotImplementedError()

    @property
    def mid_step_media_type(self):
        raise NotImplementedError()

    @property
    def image_converter_name(self):
        # the name of the tool for image conversion,
        # "dvisvgm" or "dvipng" or "imagemagick",
        # for exception raise.
        raise NotImplementedError()

    # 'shell=True' is strongly discouraged for python subprocess
    # but it is needed for imagemagick to work in a subprocess.
    # Will there be any security hazard for that? If yes, how to
    # avoid it?
    subprocess_enable_shell = False

    @staticmethod
    def _get_file_basename(filename, tex_source):
        if filename:
            basename, ext = os.path.splitext(filename)
        else:
            if not tex_source:
                return None
            basename = md5(tex_source).hexdigest()
        return basename

    @cached_property
    def _env(self):
        return prepend_bin_path_to_subprocess_env([self.latex_bin_path, self.imagemagick_bin_path])

    def __init__(self, tex_source, tex_filename, output_dir,
                 image_format, latex_bin_path,
                 imagemagick_bin_path):
        """
        :param tex_source: Required, a string representing the
        full tex source code.
        :param tex_filename: Optional, a string
        :param output_dir: Required, a string of the path where
        the images and error logs will be saved.
        :param image_format: Required, a string with allowed values
        'png' or 'svg'.
        :param latex_bin_path: Optional. A string representing
        the full directory path where the tex bins you want to use
        can be located. Specially important if you have multiple
        version of TexLive installed on the Linux server while the
        one you want to use is not in systems $PATH as a www-data
        user.
        :param imagemagick_bin_path: Optional. A string representing
        the directory when ImageMagick con be located for windows
        platform, where the default 'convert' command is not that
        of ImageMagick.
        """

        if tex_source:
            tex_source = tex_source.strip()
        if not tex_source:
            raise ValueError(
                _("Param tex_source must not be "
                  "an empty string"))
        assert isinstance(tex_source, unicode)
        self.tex_source = tex_source

        if output_dir:
            output_dir = output_dir.strip()
            print output_dir, '-------output_dir'
        if not output_dir:
            raise ValueError(
                _("Param output_dir must be specified"))
        else:
            try:
                if not os.path.exists(output_dir)\
                        or not os.path.isdir(output_dir):
                    os.makedirs(output_dir)
            except Exception:
                raise ValueError(
                    _("Param output_dir '%s' is not a valid path")
                    % output_dir)
        self.output_dir = output_dir
        
        if image_format:
            image_format = image_format.strip().\
                replace(".", "").lower()
        if not image_format:
            raise ValueError(
                _("Param image_format must be specified"))
        else:
            if not isinstance(image_format, six.string_types):
                raise ValueError(
                    _("Param image_format must be a string"))
            if not image_format in ALLOWED_LATEX2IMG_FORMAT:
                raise ValueError(
                    _("Unknow image_format '%(image_format)s',"
                      "allowed values are '%(allowd)s)") %
                    {"image_format": image_format,
                     "allowd": ",".join(ALLOWED_LATEX2IMG_FORMAT)
                     })
        self.image_format = image_format

        if latex_bin_path:
            self.latex_bin_path = latex_bin_path.strip()
        else:
            self.latex_bin_path = ""

        if imagemagick_bin_path:
            self.imagemagick_bin_path = imagemagick_bin_path.strip()
        else:
            self.imagemagick_bin_path = ""

        self.working_dir = None

        self.basename = self._get_file_basename(
                tex_filename, tex_source)
        self.compile_errlog_path = os.path.join(
                self.output_dir,
                "%s_%s.log" % (self.basename, self.tex_compiler)
        )

    def get_tex_compile_cmdline(self, tex_path):
        raise NotImplementedError()

    def get_image_convert_cmdline(
            self, input_filepath, output_filepath):
        raise NotImplementedError()

    def _get_mid_step_media(self):
        import tempfile
        self.working_dir = tempfile.mkdtemp(prefix="RELATE_LATEX_")

        tex_filename = self.basename + ".tex"
        tex_path = os.path.join(self.working_dir, tex_filename)
        _file_write(tex_path, self.tex_source.encode('UTF-8'))

        log_path = tex_path.replace(".tex", ".log")
        compiled_file_path = tex_path.replace(
            ".tex",
            "." + self.mid_step_media_type.replace(".", "").lower())

        cmdline = self.get_tex_compile_cmdline(tex_path)

        output, error, status = popen_wrapper(cmdline, enable_shell=self.subprocess_enable_shell, env=self._env)

        try:
            tex_compile_process = Popen(
                cmdline,
                stdout=PIPE,
                stderr=PIPE,
                cwd=self.working_dir,
                env=self._env,
            )
            [stdout, stderr] = tex_compile_process.communicate()
            tex_compile_process.wait()
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
            raise OSError(
                _("Failed to run '%s' cmdline. "
                  "Are you sure LaTeX is installed "
                  "or RELATE_LATEX_BIN_PATH is properly "
                  "configured in local_settings.py?")
                % cmdline
            )

        if tex_compile_process.returncode != 0:
            log = _file_read(log_path)
            try:
                log = get_abstract_latex_log(log)
                _file_write(self.compile_errlog_path, log)
                self._remove_working_dir()
            finally:
                from django.utils.html import escape
                raise ValueError(
                    "<pre>%s</pre>" % escape(log).strip())

        if os.path.isfile(compiled_file_path):
            return compiled_file_path
        else:
            raise RuntimeError(
                _('No %s file was produced.'),
                self.mid_step_media_type)

    def _get_converted_image(self):
        compiled_output_path = self._get_mid_step_media()
        if not compiled_output_path:
            return None
        image_path = compiled_output_path.replace(
            "." + self.mid_step_media_type, "." + self.image_format)

        cmdline = self.get_image_convert_cmdline(compiled_output_path, image_path)

        output, error, status = popen_wrapper(cmdline, enable_shell=self.subprocess_enable_shell, env=self._env)
        if status != 0:
            raise RuntimeError(error)
        output_image_path = os.path.join(
                self.output_dir,
                "%s.%s" % (self.basename, self.image_format))
        shutil.copyfile(image_path, output_image_path)
        self._remove_working_dir()
        return output_image_path

    def _get_compile_err_cached(self):
        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            err_cache_key = None
        else:
            def_cache = cache.caches["default"]
            err_cache_key = ("latex_err:%s:%s"
                             % (self.tex_compiler, self.basename))
            # Memcache is apparently limited to 250 characters.
            if len(err_cache_key) < 240:
                err_result = def_cache.get(err_cache_key)
                if err_result is not None:
                    assert \
                        isinstance(err_result, six.string_types),\
                        err_cache_key
                    return err_result

        err_result = None

        # read the saved err_log if it exists
        if os.path.isfile(self.compile_errlog_path):
            err_result = _file_read(self.compile_errlog_path)

        if err_result:
            assert isinstance(err_result, six.string_types)
            if err_cache_key:
                if len(err_result) <= getattr(
                        settings, "RELATE_CACHE_MAX_BYTES", 0):
                        def_cache.add(err_cache_key, err_result, None)

            from django.utils.html import escape
            raise ValueError(
                "<pre>%s</pre>" % escape(err_result).strip())

        return None

    def get_data_uri_cached(self, force_regenerate=False):
        if force_regenerate:
            image_path = self._get_converted_image()
            uri_result = get_file_data_uri(image_path)
            assert isinstance(uri_result, six.string_types)
            return uri_result

        err_result = self._get_compile_err_cached()
        if err_result:
            return None

        image_saving_path = os.path.join(
                self.output_dir,
                "%s.%s" % (self.basename, self.image_format))

        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            uri_cache_key = None
        else:
            def_cache = cache.caches["default"]
            uri_cache_key = (
                "latex2img:%s"
                % md5(image_saving_path.encode("utf-8")).hexdigest())
            uri_result = def_cache.get(uri_cache_key)
            if uri_result:
                return uri_result

        # read or generate the image
        if not os.path.isfile(image_saving_path):
            image_saving_path = self._get_converted_image()
        uri_result = get_file_data_uri(image_saving_path)
        assert isinstance(uri_result, six.string_types)

        # no cache configured
        if not uri_cache_key:
            return uri_result

        # cache configure, but image not cached
        if len(uri_result) <= getattr(
                settings, "RELATE_CACHE_MAX_BYTES", 0):
            def_cache.add(uri_cache_key, uri_result, None)
            return uri_result

    def _remove_working_dir(self):
        shutil.rmtree(self.working_dir)

# }}}

# {{{ derived classes

class TexDviImageBase(Tex2ImgBase):
    tex_compiler = "latex"
    mid_step_media_type = "dvi"

    def get_tex_compile_cmdline(self, tex_path):
        return ['latexmk',
                '-e',
                '$latex=q/latex -no-shell-escape '
                '-interaction=batchmode '
                '-halt-on-error %O %S/',
                '-dvi',
                tex_path
                ]


class Latex2Svg(TexDviImageBase):
    image_converter = 'dvisvgm'
    image_converter_name = 'dvisvg'

    def get_image_convert_cmdline(
            self, input_filepath, output_filepath):
        return ['dvisvgm',
                '--no-fonts',
                '-o', output_filepath,
                input_filepath]


class Latex2Png(TexDviImageBase):
    image_converter = 'dvisvgm'
    image_converter_name = 'dvipng'

    def get_image_convert_cmdline(
            self, input_filepath, output_filepath):
        return ['dvipng',
                '-o', output_filepath,
                '-pp', '1',
                '-T', 'tight',
                '-z9',
                input_filepath]


class TexPdfImageBase(Tex2ImgBase):
    mid_step_media_type = "pdf"
    image_converter = 'convert'
    image_converter_name = 'imagemagick'
    subprocess_enable_shell = True

    def get_image_convert_cmdline(
            self, input_filepath, output_filepath):

        # the following setting return image with gmail quality image with
        # exactly printed size
        return ['convert', '-density', '96', '-quality', '85', '-trim',
                input_filepath,
                output_filepath
                ]


class Pdflatex2Png(TexPdfImageBase):
    tex_compiler = "pdflatexx"
    def get_tex_compile_cmdline(self, tex_path):
        return ['latexmk',
                '-pdf',
                '-pdflatex=pdflatex %O '
                '-no-shell-escape '
                '-interaction=batchmode '
                '-halt-on-error '
                '%S',
                tex_path
                ]


class Xelatex2Png(TexPdfImageBase):
    tex_compiler = "xelatex"
    def get_tex_compile_cmdline(self, tex_path):
        return ['latexmk',
                '-e',
                '$pdflatex=q/xelatex %O -no-shell-escape '
                '-interaction=batchmode '
                '-halt-on-error %S/',
                '-pdf',
                tex_path
                ]

# }}}

# {{{ get tex2img class

def get_tex2img_class(compiler, image_fomrat):
    image_format = image_fomrat.replace(".", "").lower()
    compiler = compiler.lower()
    if not image_format in ALLOWED_LATEX2IMG_FORMAT:
        raise ValueError(
            _("Unsupported image format '%s'") % image_format)

    if not compiler in ALLOWED_COMPILER:
        raise ValueError(
            _("Unsupported tex compiler '%s'") % compiler)

    if not (compiler, image_format) in ALLOWED_COMPILER_FORMAT_COMBINATION:
        raise ValueError(
            _("Unsupported combination: "
              "('%(compiler)s', '%(format)s'). "
              "Currently support %(supported)s.")
              % {"compiler": compiler,
                 "format": image_format,
                 "supported": ", ".join(
                     str(e) for e in ALLOWED_COMPILER_FORMAT_COMBINATION)}
        )

    class_name = "%s2%s" % (compiler.title(), image_format.title())

    return getattr(sys.modules[__name__], class_name)

# }}}



def tex_to_img_tag(tex_source, *args, **kwargs):
    '''Convert LaTex to IMG tag'''

    output_dir = kwargs.get("output_dir")
    tex_filename = kwargs.get("tex_filename", None)
    compiler = kwargs.get("compiler", "latex")
    image_format = kwargs.get("image_format", "")
    if not image_format:
        raise ValueError(_("'image_format' must be specified."))
    tex_preamble = kwargs.get("tex_preamble", "")
    tex_preamble_extra = kwargs.get("tex_preamble_extra", "")
    overwrite = kwargs.get("overwrite", False)
    html_class_extra = kwargs.get("html_class_extra", "")
    standalone = kwargs.get("standalone", True)
    alt = kwargs.get("alt", "")
    imagemagick_bin_path = kwargs.get("imagemagick_bin_path", "")
    latex_bin_path = kwargs.get("latex_bin_path", "")

    if html_class_extra:
        if isinstance(html_class_extra, list):
            html_class_extra = " ".join (html_class_extra)
        elif not isinstance(html_class_extra, six.string_types):
            raise ValueError(
                _('"html_class_extra" must be a string or a list'))
        html_class = "%s %s" %(DEFAULT_IMG_HTML_CLASS, html_class_extra)
    else: html_class = DEFAULT_IMG_HTML_CLASS

    tex2img_class = get_tex2img_class(compiler, image_format)

    texdoc = TexDoc(tex_source, preamble=tex_preamble, preamble_extra=tex_preamble_extra, empty_pagestyle=standalone)

    # remove source_code because mathjax will render it.
    # if not alt:
    #     alt = texdoc.document
    #
    # if alt:
    #     from django.utils.html import escape
    #     alt = "alt='<pre>%s</pre>'" % alt.strip().replace("\n","")

    latex2img = tex2img_class(
        tex_source=texdoc.as_latex(),
        tex_filename=tex_filename,
        output_dir=output_dir,
        image_format=image_format,
        latex_bin_path=latex_bin_path,
        imagemagick_bin_path=imagemagick_bin_path,
        )

    return (
        "<img src='%(src)s' "
        "class='%(html_class)s' %(alt)s>"
        % {
            "src": latex2img.get_data_uri_cached(overwrite),
            "html_class": html_class,
            "alt": alt,
        })


# vim: foldmethod=marker
