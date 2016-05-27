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
    "pdflatex": "latex",
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


def prepend_bin_path_to_subprocess_env(bin_path):
    """
    Prepend bin path to server env $PATH for www-data
    user when execute a subprocess
    """
    env = dict(os.environ)
    if isinstance(bin_path, six.string_types):
        env["PATH"] = bin_path + os.pathsep + env["PATH"]

    if isinstance(list, bin_path):
        for bin_path in bin_path:
            if bin_path:
                env["PATH"] = bin_path + os.pathsep + env["PATH"]

    return env

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


def get_abstract_latex_log(log):
    '''abstract error msg from latex compilation log'''

    msg = log.split(LATEX_ERR_LOG_BEGIN_LINE_STARTS)[1]\
        .split(LATEX_ERR_LOG_END_LINE_STARTS)[0]

    if LATEX_LOG_OMIT_LINE_STARTS:
        msg = "\n".join(
            line for line in msg.splitlines()
            if (not line.startswith(LATEX_LOG_OMIT_LINE_STARTS)
                and
                line.strip() != ""))
    return msg



import ply.lex

# {{{ strip comments from source

def strip_comments(source):
    # copied from https://gist.github.com/amerberg/a273ca1e579ab573b499

    tokens = (
                'PERCENT', 'BEGINCOMMENT', 'ENDCOMMENT', 'BACKSLASH',
                'CHAR', 'BEGINVERBATIM', 'ENDVERBATIM', 'NEWLINE', 'ESCPCT',
             )
    states = (
                ('linecomment', 'exclusive'),
                ('commentenv', 'exclusive'),
                ('verbatim', 'exclusive')
            )

    #Deal with escaped backslashes, so we don't think they're escaping %.
    def t_ANY_BACKSLASH(t):
        r"\\\\"
        return t

    #One-line comments
    def t_PERCENT(t):
        r"\%"
        t.lexer.begin("linecomment")

    #Escaped percent signs
    def t_ESCPCT(t):
        r"\\\%"
        return t

    #Comment environment, as defined by verbatim package
    def t_BEGINCOMMENT(t):
        r"\\begin\s*{\s*comment\s*}"
        t.lexer.begin("commentenv")

    #Verbatim environment (different treatment of comments within)
    def t_BEGINVERBATIM(t):
        r"\\begin\s*{\s*verbatim\s*}"
        t.lexer.begin("verbatim")
        return t

    #Any other character in initial state we leave alone
    def t_CHAR(t):
        r"."
        return t

    def t_NEWLINE(t):
        r"\n"
        return t

    #End comment environment
    def t_commentenv_ENDCOMMENT(t):
        r"\\end\s*{\s*comment\s*}"
        #Anything after \end{comment} on a line is ignored!
        t.lexer.begin('linecomment')

    #Ignore comments of comment environment
    def t_commentenv_CHAR(t):
        r"."
        pass

    def t_commentenv_NEWLINE(t):
        r"\n"
        pass

    #End of verbatim environment
    def t_verbatim_ENDVERBATIM(t):
        r"\\end\s*{\s*verbatim\s*}"
        t.lexer.begin('INITIAL')
        return t

    #Leave contents of verbatim environment alone
    def t_verbatim_CHAR(t):
        r"."
        return t

    def t_verbatim_NEWLINE(t):
        r"\n"
        return t

    #End a % comment when we get to a new line
    def t_linecomment_ENDCOMMENT(t):
        r"\n"
        t.lexer.begin("INITIAL")
        #Newline at the end of a line comment is stripped.

    #Ignore anything after a % on a line
    def t_linecomment_CHAR(t):
        r"."
        pass

    lexer = ply.lex.lex()
    lexer.input(source)
    return u"".join([tok.value for tok in lexer])

# }}}


# vim: foldmethod=marker
