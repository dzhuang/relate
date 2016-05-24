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
from django.core.management.base import CommandError
from django.utils.encoding import (
    DEFAULT_LOCALE_ENCODING, force_text)
from django.utils.functional import cached_property

# {{{ Constants

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

LATEX_ERR_LOG_BEGIN_LINE_STARTS = "\n! "
LATEX_ERR_LOG_END_LINE_STARTS = "\nHere is how much of TeX's memory"

DEFAULT_IMG_HTML_CLASS = "img-responsive"

# }}}


# {{{ subprocess popen wrapper

def popen_wrapper(args, env,
                  enable_shell=False, os_err_exc_type=CommandError,
                  stdout_encoding='utf-8'):
    """
    Extended from django.core.management.utils.popen_wrapper,
    especially to solve UnicodeDecodeError raised on Windows
    platform where the OS stdout is not utf-8.

    Friendly wrapper around Popen, with env and shell options

    Returns stdout output, stderr output and OS status code.
    """

    try:
        p = Popen(args, shell=enable_shell, stdout=PIPE,
                  stderr=PIPE, close_fds=os.name != 'nt', env=env)
    except OSError as e:
        strerror = force_text(e.strerror, DEFAULT_LOCALE_ENCODING,
                              strings_only=True)
        six.reraise(os_err_exc_type, os_err_exc_type(
                string_concat(_('Error executing'), ' %s: %s')
                % (args[0], strerror)), sys.exc_info()[2])

    output, errors = p.communicate()
    return (
        force_text(output, stdout_encoding, strings_only=True,
                   errors='strict'),
        force_text(errors, DEFAULT_LOCALE_ENCODING,
                   strings_only=True, errors='replace'),
        p.returncode
    )


def get_latex2img_env(bin_path_list):
    """
    Prepend latex_bin_path and imagemagick_bin_path to
    server system env $PATH for www-data user when execute
    a subprocess
    """
    env = dict(os.environ)
    for bin_path in bin_path_list:
        if bin_path:
            env["PATH"] = bin_path + os.pathsep + env["PATH"]
    return env


def get_version(tool_cmd, enable_shell, env):
    # This will output system-encoded bytestrings instead of UTF-8,
    # when looking up the version. It's especially a problem on Windows.
    out, err, status = popen_wrapper(
        [tool_cmd, '--version'],
        enable_shell=enable_shell,
        stdout_encoding=DEFAULT_LOCALE_ENCODING,
        env=env
    )
    m = re.search(r'(\d+)\.(\d+)\.?(\d+)?', out)
    if m:
        return tuple(int(d) for d in m.groups() if d is not None)
    else:
        raise CommandError(
            _("Unable to run %(cmd)s. Is %(tool)s installed "
              "or has its path correctly configured "
              "in local_settings.py?")
            % {"cmd": tool_cmd,
               "tool": CMD_NAME_DICT[tool_cmd],
               })

# }}}


# {{{ file read and write

def _file_read(filename):
    '''Read the content of a file and close it properly.'''
    f = file(filename, 'rb')
    content = f.read()
    f.close()
    return content


def _file_write(filename, content):
    '''Write into a file and close it properly.'''
    f = file(filename, 'wb')
    f.write(content)
    f.close()

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


# DEFAULT_LATEX_IMAGE_FOLDER_NAME = getattr(
#     settings, "RELATE_LATEX_IMAGE_FOLDER_NAME", "latex_image")

LATEX_LOG_OMIT_LINE_STARTS = (
    "See the LaTeX manual or LaTeX",
    "Type  H <return>  for",
    " ...",
    # more
)


# }}}

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


# {{{ assemble tex source

# def make_tex_source(tex_body, tex_preamble="",
#                     tex_preamble_extra=""):
#     '''
#         Assemble tex source code.
#
#         If tex_body contain all basic elements of a full
#         latex document (\documentclass \begin{document}
#         and \end{document}, it will be treated as full
#         document.This makes it convenient for pgf/tikz
#         settings in preamble.
#     '''
#     assert isinstance(tex_body, unicode)
#
#     if re.search(IS_FULL_DOC_RE, tex_body):
#         tex_source = tex_body
#
#     else:
#         missing_ele = []
#         for ele, ele_re in DOC_ELEMENT_RE_LIST:
#             if not re.search(ele_re, tex_body):
#                 missing_ele.append(ele)
#
#         if len(missing_ele) < 3:
#             raise ValueError("<pre>%s</pre>"
#                 % _("Your faied to submit a full latex document: "
#                     " missing %s.")
#                              % ", ".join(missing_ele) )
#         else:
#             if not tex_preamble:
#                 tex_preamble = getattr(
#                     settings, "RELATE_LATEX_PREAMBLE",
#                     DEFAULT_LATEX_PREAMBLE)
#
#             tex_begin_document =getattr(
#                 settings, "RELATE_LATEX_BEGIN_DOCUMENT",
#                 r"\begin{document}")
#
#             tex_end_document =getattr(
#                 settings, "RELATE_LATEX_END_DOCUMENT",
#                 r"\end{document}")
#
#             tex_source = "%s" * 5 % (
#                 tex_preamble, tex_preamble_extra,
#                 tex_begin_document, tex_body, tex_end_document)
#
#     # make sure the latex source use empty style (no page mark)
#     if not re.search(PAGE_EMPTY_RE, tex_source):
#         tex_source = re.sub(BEGIN_DOCUMENT_RE,
#                             r"\n\1\\pagestyle{empty}\n\1\2",
#                             tex_source)
#
#     return tex_source

# }}}


def get_abstract_latex_log(log):
    '''abstract error msg from log'''

    msg = log.split(LATEX_ERR_LOG_BEGIN_LINE_STARTS)[1]\
        .split(LATEX_ERR_LOG_END_LINE_STARTS)[0]

    if LATEX_LOG_OMIT_LINE_STARTS:
        msg = "\n".join(
            line for line in msg.splitlines()
            if (not line.startswith(LATEX_LOG_OMIT_LINE_STARTS)
                and
                line.strip() != ""))
    return msg


# {{{ covert tex to dvi format

# def tex2dvi(tex_source, output_dir, basename, overwrite=False,
#             max_runs=5):
#     '''Convert LaTeX  source to DVI.'''
#
#     if max_runs < 2:
#         raise ValueError(_('Compilation must be ran at least twice.'))
#
#     tex_path = os.path.join(output_dir, basename) + '.tex'
#     dvi_path = tex_path.replace('.tex', '.dvi')
#     log_path = tex_path.replace('.tex', '.log')
#     aux_path = tex_path.replace('.tex', '.aux')
#
#     if not overwrite:
#         if os.path.isfile(dvi_path):
#             return dvi_path
#
#     _file_write(tex_path, tex_source.encode('UTF-8'))
#
#     aux_old = None
#     for i in xrange(max_runs):
#         try:
#             tex_process = Popen(
#                 ['latex', '-interaction=batchmode',
#                  '-halt-on-error', '-no-shell-escape',
#                  tex_path,],
#                 stdout=PIPE,
#                 stderr=PIPE,
#                 cwd=output_dir,
#             )
#             tex_process.wait()
#         except OSError, err:
#             if err.errno != errno.ENOENT:
#                 raise
#             raise OSError(_("Failed to run 'latex' cmd. "
#                             "Are you sure LaTeX is installed?"))
#
#         if tex_process.returncode != 0:
#             log = _file_read(log_path)
#             try:
#                 log = get_abstract_latex_log(log)
#                 _file_write(log_path, log)
#             finally:
#                 from django.utils.html import escape
#                 raise ValueError(
#                     "<pre>%s</pre>" % escape(log).strip())
#
#         aux = _file_read(aux_path)
#
#         # aux file stabilized
#         if aux == aux_old:
#             if os.path.isfile(dvi_path):
#                 return dvi_path
#             else:
#                 raise RuntimeError(_('No dvi file was produced.'))
#         aux_old = aux
#     raise RuntimeError(
#         _("LaTex Compilation didn't stabilize after %i max_runs")
#         % max_runs)

# }}}


# {{{ covert DVI to dataURI






# def tex_to_data_uri(
#         tex_body, output_dir=None, tex_filename="",
#         image_format="", tex_preamble="", tex_preamble_extra="",
#         overwrite=False):
#     '''Convert LaTex body to data uri'''
#
#     if not output_dir:
#         output_dir = getattr(
#             settings, "RELATE_LATEX_OUTPUT_PATH", None)
#     if not output_dir:
#         output_dir = os.path.join(
#             getattr(settings, "MEDIA_ROOT"),
#             DEFAULT_LATEX_IMAGE_FOLDER_NAME)
#
#     if not os.path.isdir(output_dir):
#         try:
#             os.makedirs(output_dir)
#         except OSError:
#             raise
#
#     tex_source = make_tex_source(
#         tex_body, tex_preamble, tex_preamble_extra)
#
#     if tex_filename:
#         # In case a filename with extension is given,
#         # use only the basename
#         basename, ext = os.path.splitext(tex_filename)
#     else:
#         basename = md5(tex_source).hexdigest()
#
#     if not image_format:
#         image_format = getattr(
#             settings, "RELATE_LATEX_TO_IMAGE_FORMAT", "svg")
#
#     # dvipng fails to covert DVI with tikz in many cases
#     # if code contains tikz or pgf, use svg as output format
#     if image_format == "png" and re.search(TIKZ_PGF_RE, tex_source):
#         image_format = "svg"
#
#     if not image_format.lower() in ALLOWED_LATEX2IMG_FORMAT:
#         raise ValueError(_('Unable to convert LaTex to %s, only '
#                            '"png" and "svg" are supported.')
#                          % image_format)
#
#     tex_path = os.path.join(output_dir, basename) + '.tex'
#     image_path = tex_path.replace('.tex', '.' + image_format)
#     log_path = tex_path.replace('.tex', '.log')
#     dvi_path = tex_path.replace('.tex', '.dvi')
#     aux_path = tex_path.replace('.tex', '.aux')
#
#     if not overwrite:
#         if os.path.isfile(image_path):
#             return get_image_data_uri(image_path)
#         if not os.path.isfile(dvi_path) and os.path.isfile(log_path):
#             log = _file_read(log_path)
#             from django.utils.html import escape
#             raise RuntimeError("<pre>%s</pre>" % escape(log).strip())
#
#     # {{{ do the conversion
#
#     if image_format == 'png':
#         cmd = 'dvipng'
#         cmd_args = [
#             cmd, '-o',
#             image_path,
#             '-pp', '1',
#             '-T', 'tight',
#             '-z9',
#         ]
#     elif image_format == 'svg':
#         cmd = 'dvisvgm'
#         cmd_args = [
#             cmd,
#             '-o', image_path,
#             '--no-fonts']
#     else:
#         raise ValueError(
#             _('output_suffix must be either "png" or "svg"'))
#
#     cmd_args.append(dvi_path)
#
#     old_workingdir = os.getcwd()
#
#     try:
#         tex2dvi(tex_source, output_dir, basename, overwrite)
#
#         os.chdir(output_dir)
#         try:
#             p = Popen(cmd_args, stdout=PIPE, stderr=PIPE)
#         except OSError, err:
#             if err.errno != errno.ENOENT:
#                 raise
#             else:
#                 raise OSError(
#                     _("%s command cannot be run, but is needed "
#                       "for converting images.")
#                     % cmd)
#
#         [stdout, stderr] = p.communicate()
#
#         if p.returncode != 0:
#             raise RuntimeError(
#                 _('%(cmd)s command exited with error: '
#                   '\n[stderr]\n%(error)s\n[stdout]\n%(output)s')
#                 % {'cmd': cmd,
#                    'error': stderr,
#                    'output': stdout})
#
#     finally:
#         os.chdir(old_workingdir)
#         try:
#             # remove tmp files
#             os.unlink(tex_path)
#             os.unlink(aux_path)
#             os.unlink(dvi_path)
#
#             # For file with name generated by md5, if image not generated
#             # preserve the error log, so that not need to recompile
#             # the tex problematic tex file.
#             if os.path.isfile(image_path) and not tex_filename:
#                 os.unlink(log_path)
#         except:
#             pass
#
#     # }}}
#
#     return get_image_data_uri(image_path)

# }}}


#{{{ covert tex to <img> tag

# def tex_to_img_tag(tex_source, *args, **kwargs):
#     '''Convert LaTex to IMG tag'''
#
#     output_dir = kwargs.get("output_idr", None)
#     tex_filename = kwargs.get("tex_filename", None)
#     image_format = kwargs.get("image_format", "svg")
#     tex_preamble = kwargs.get("tex_preamble", "")
#     tex_preamble_extra = kwargs.get("tex_preamble_extra", "")
#     overwrite = kwargs.get("overwrite", False)
#     html_class_extra = kwargs.get("html_class_extra", "")
#     alt = kwargs.get("alt", "")
#
#     # make rendered image responsive by default
#     html_class = "img-responsive"
#
#     if html_class_extra:
#         if isinstance (html_class_extra, list):
#             html_extra_class = " ".join (html_class_extra)
#         elif not isinstance(html_class_extra, six.string_types):
#             raise ValueError(
#                 _('"html_class_extra" must be a string or a list'))
#
#         html_class = "%s %s" %(html_class, html_extra_class)
#
#     # remove source_code because mathjax will render it.
#     # if alt is None:
#     #     alt = tex_source
#
#     if alt:
#         alt = "alt='%s'" % alt.strip()
#
#     try:
#         src = tex_to_data_uri(tex_source, output_dir, tex_filename,
#                           image_format, tex_preamble, tex_preamble_extra,
#                           overwrite)
#     except Exception:
#         raise
#
#     return (
#         "<img src='%(src)s' "
#         "class='%(html_class)s' %(alt)s>"
#         % {
#             "src": src,
#             "html_class": html_class,
#             "alt": alt,
#         })

# }}}


# vim: foldmethod=marker
