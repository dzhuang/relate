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
import ply.lex
from hashlib import md5
from subprocess import Popen, PIPE

from django.utils.translation import (
    ugettext as _, string_concat)
from django.core.management.base import CommandError
from django.utils.encoding import (
    DEFAULT_LOCALE_ENCODING, force_text)


# {{{ Constants

ALLOWED_COMPILER = ['latex', 'pdflatex', 'xelatex']
ALLOWED_LATEX2IMG_FORMAT = ['png', 'svg']

ALLOWED_COMPILER_FORMAT_COMBINATION = (
    ("latex", "png"),
    ("latex", "svg"),
    ("pdflatex", "png"),
    ("xelatex", "png")
)

# }}}


# {{{ subprocess popen wrapper

def popen_wrapper(args, os_err_exc_type=CommandError,
                  stdout_encoding='utf-8', **kwargs):
    """
    Extended from django.core.management.utils.popen_wrapper.
    `**kwargs` is added so that more kwargs can be added.

    This method is especially to solve UnicodeDecodeError
    raised on Windows platform where the OS stdout is not utf-8.

    Friendly wrapper around Popen

    Returns stdout output, stderr output and OS status code.
    """

    try:
        p = Popen(args, stdout=PIPE,
                  stderr=PIPE, close_fds=os.name != 'nt', **kwargs)
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

# }}}


# {{{ file read and write

def get_basename_or_md5(filename, s):
    """
    :return: the basename of `filename` if `filename` is not empty,
    else, return the md5 of string `s`.
    """
    if filename:
        basename, ext = os.path.splitext(filename)
    else:
        if not s:
            return None
        basename = md5(s).hexdigest()
    return basename


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


# {{{ get error log abstracted

LATEX_ERR_LOG_BEGIN_LINE_STARTS = "\n! "
LATEX_ERR_LOG_END_LINE_STARTS = "\nHere is how much of TeX's memory"
LATEX_LOG_OMIT_LINE_STARTS = (
    "See the LaTeX manual or LaTeX",
    "Type  H <return>  for",
    " ...",
    # more
)

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

# }}}


# {{{ strip comments from source

def strip_comments(source):
    # copied from https://gist.github.com/amerberg/a273ca1e579ab573b499

    tokens = (
                'PERCENT', 'BEGINCOMMENT', 'ENDCOMMENT',
                'BACKSLASH', 'CHAR', 'BEGINVERBATIM',
                'ENDVERBATIM', 'NEWLINE', 'ESCPCT',
#                'MAKEATLETTER', 'MAKEATOTHER',
             )
    states = (
 #               ('makeatenv', 'exclusive'),
                ('linecomment', 'exclusive'),
                ('commentenv', 'exclusive'),
                ('verbatim', 'exclusive')
            )

    # def t_MAKEATLETTER(t):
    #     r"\\makeatletter"
    #     t.lexer.begin("makeatenv")
    #     return t
    #
    # def t_makeatenv_CHAR(t):
    #     r"."
    #     return t
    #
    # def t_makeatenv_NEWLINE(t):
    #     r"\n"
    #     return t
    #
    # def t_makeatenv_MAKEATOTHER(t):
    #     r"\\makeatother"
    #     t.lexer.begin('INITIAL')
    #     return t

    # Deal with escaped backslashes, so we don't think they're
    # escaping %.
    #def t_ANY_BACKSLASH(t):
    def t_BACKSLASH(t):
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

    # def t_linecomment_NEWLINE(t):
    #     r"\n"
    #     return t

    #Ignore anything after a % on a line
    def t_linecomment_CHAR(t):
        r"."
        pass

    lexer = ply.lex.lex()
    lexer.input(source)
    return u"".join([tok.value for tok in lexer])

# }}}


# {{{ remove redundant strings

def strip_spaces(s, allow_single_empty_line=False):
    """
    strip spaces in s, so that the result will be
    considered same although new empty lines or
    extra spaces are added. Especially for generating
    md5 of the string.
    :param s: string. The source code
    :param allow_single_empty_line: bool. If True,
    single empty line will be preserved, this is need
    for latex document body. If False, all empty line
    will be removed.
    :return: string.
    """

    # strip all lines
    s = "\n".join([l.strip() for l in s.split("\n")])

    if not allow_single_empty_line:
        while "\n\n" in s:
            s = s.replace('\n\n', '\n')
    else:
        while "\n\n\n" in s:
            s = s.replace('\n\n\n', '\n\n')

    # remove redundant white spaces and tabs
    pattern_list = ['  ', '\t ', '\t\t', ' \t']
    for pattern in pattern_list:
        while pattern in s:
            s = s.replace(pattern, ' ')

    return s

## }}}


def get_all_indirect_subclasses(cls):
    all_subcls = []

    for subcls in cls.__subclasses__():
        if not subcls.__subclasses__():
            # has no child
            all_subcls.append(subcls)
        all_subcls.extend(get_all_indirect_subclasses(subcls))

    return list(set(all_subcls))

def replace_seperator(s, sep):
    return s.replace(sep, "")

# vim: foldmethod=marker
