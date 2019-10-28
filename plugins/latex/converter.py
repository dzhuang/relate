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
import shutil
import re
from hashlib import md5
from pymongo.errors import DuplicateKeyError
from wand.image import Image as wand_image

from django.core.management.base import CommandError
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escape
from django.utils.encoding import DEFAULT_LOCALE_ENCODING
from django.utils.translation import ugettext as _, string_concat
from django.conf import settings

from relate.utils import local_now
from relate.checks import RelateCriticalCheckMessage

from .utils import (
    get_mongo_db,
    popen_wrapper, get_basename_or_md5,
    file_read, file_write, get_abstract_latex_log,
    get_latex_cache
)

# mypy
if False:
    from typing import Text, Optional, Any, List  # noqa
    from pymongo import MongoClient  # noqa
    from pymongo.collection import Collection  # noqa
    from django.core.checks.messages import CheckMessage  # noqa

DB = get_mongo_db()
latex_settings = settings.RELATE_LATEX_SETTINGS
DATAURI_MONGO_COLLECTION_NAME = latex_settings["latex"].get(
    "RELATE_LATEX_DATAURI_MONGO_COLLECTION_NAME",
    "relate_latex_datauri")
ERROR_MONGO_COLLECTION_NAME = latex_settings["latex"].get(
    "RELATE_LATEX_ERROR_MONGO_COLLECTION_NAME",
    "relate_latex_error"
)


def get_latex_datauri_mongo_collection(name=None, db=DB, index_name="key"):
    # type: (Optional[Text], Optional[MongoClient], Optional[Text]) -> Collection
    if not name:
        name = DATAURI_MONGO_COLLECTION_NAME
    collection = db[name]
    if index_name:
        collection.ensure_index(index_name, unique=True)
    return collection


def get_latex_error_mongo_collection(name=None, db=DB, index_name="key"):
    # type: (Optional[Text], Optional[MongoClient], Optional[Text]) -> Collection
    if not name:
        name = ERROR_MONGO_COLLECTION_NAME
    collection = db[name]
    if index_name:
        collection.ensure_index(index_name, unique=True)
    return collection


# {{{ latex compiler classes and image converter classes


class CommandBase(object):
    @property
    def name(self):
        # type: () -> Text
        """
        The name of the command tool
        """
        raise NotImplementedError

    @property
    def cmd(self):
        # type: () -> Text
        """
        The string of the command
        """
        raise NotImplementedError

    min_version = None  # type: Optional[Text]
    max_version = None  # type: Optional[Text]
    bin_path = ""  # type: Text

    def __init__(self):
        # type: () -> None
        self.bin_path = self.get_bin_path()

    def get_bin_path(self, check_only=False):
        raise NotImplementedError

    def check(self):
        # type: () -> List[CheckMessage]
        errors = []

        self.bin_path = self.get_bin_path(check_only=True)

        try:
            out, err, status = popen_wrapper(
                [self.bin_path, '--version'],
                stdout_encoding=DEFAULT_LOCALE_ENCODING
            )
        except CommandError as e:
            errors.append(RelateCriticalCheckMessage(
                msg=e.__str__(),
                hint=("Unable to run '%(cmd)s with '--version'. Is "
                      "%(tool)s installed or has its "
                      "path correctly configured "
                      "in local_settings.py?") % {
                         "cmd": self.cmd,
                         "tool": self.name,
                     },
                obj=self.name,
                id="%s_E001" % self.name.lower()
            ))
            return errors

        m = re.search(r'(\d+)\.(\d+)\.?(\d+)?', out)

        if not m:
            errors.append(RelateCriticalCheckMessage(
                msg="\n".join([out, err]),
                hint=("Unable find the version of '%(cmd)s'. Is "
                      "%(tool)s installed with the correct version?"
                      ) % {
                         "cmd": self.cmd,
                         "tool": self.name,
                     },
                obj=self.name,
                id = "%s_E002" % self.name.lower()
            ))
        else:
            version = ".".join(d for d in m.groups() if d)
            from pkg_resources import parse_version
            if self.min_version:
                if parse_version(version) < parse_version(self.min_version):
                    errors.append(RelateCriticalCheckMessage(
                        "Version outdated",
                        hint=("'%(tool)s' with version "
                              ">=%(required)s is required, "
                              "current version is %(version)s"
                              ) % {
                                 "tool": self.name,
                                 "required": self.min_version,
                                 "version": version},
                        obj=self.name,
                        id="%s_E003" % self.name.lower()
                    ))
            elif self.max_version:
                if parse_version(version) >= parse_version(self.max_version):
                    errors.append(RelateCriticalCheckMessage(
                        "Version not supported",
                        hint=("'%(tool)s' with version "
                              "< %(max_version)s is required, "
                              "current version is %(version)s"
                              ) % {
                                 "tool": self.name,
                                 "max_version": self.max_version,
                                 "version": version},
                        obj=self.name,
                        id="%s_E004" % self.name.lower()
                    ))
        return errors


class TexCompilerBase(CommandBase):
    def get_bin_path(self, check_only=False):
        bin_path_dir = latex_settings["bin_path"].get(
            "RELATE_%s_BIN_DIR" % self.name.upper(),
            latex_settings["bin_path"].get("RELATE_LATEX_BIN_DIR", "")
        )
        return os.path.join(bin_path_dir, self.cmd.lower())


class Latexmk(TexCompilerBase):
    name = "latexmk"
    cmd = "latexmk"
    
    # This also require perl, ActivePerl is recommended
    min_version = "4.39"


class LatexCompiler(TexCompilerBase):
    latexmk_option = [
        '-latexoption="-no-shell-escape"',
        '-interaction=nonstopmode',
        '-halt-on-error'
    ]

    @property
    def output_format(self):
        # type: () -> Text
        raise NotImplementedError()

    def __init__(self):
        # type: () -> None
        super(LatexCompiler, self).__init__()
        self.latexmk_prog_repl = self._get_latexmk_prog_repl()

    def _get_latexmk_prog_repl(self):
        # type: () -> Text
        """
        Program replace when using "-pdflatex=" or "-latex="
        arg in latexmk, especially needed when compilers are
        not in system's default $PATH.
        :return: the latexmk arg "-pdflatex=/path/to/pdflatex" for
        # pdflatex or "-pdflatex=/path/to/xelatex" for xelatex
        """
        return (
            "-%s=%s" % (self.name.lower(), self.bin_path.lower())
        )

    def get_latexmk_subpro_cmdline(self, input_path):
        # type: (Text) -> List[Text]
        latexmk = Latexmk()
        args = [
            latexmk.bin_path,
            "-%s" % self.output_format,
            self.latexmk_prog_repl,
        ]
        args.extend(self.latexmk_option)
        args.append(input_path)

        return args


class Latex(LatexCompiler):
    name = "latex"
    cmd = "latex"
    output_format = "dvi"


class PdfLatex(LatexCompiler):
    name = "PdfLatex"
    cmd = "pdflatex"
    output_format = "pdf"


class LuaLatex(LatexCompiler):
    name = "LuaLatex"
    cmd = "lualatex"
    output_format = "pdf"

    def __init__(self):
        # type: () -> None
        super(LuaLatex, self).__init__()
        self.latexmk_prog_repl = "-%s=%s" % ("pdflatex", self.bin_path)


class XeLatex(LatexCompiler):
    name = "XeLatex"
    cmd = "xelatex"
    output_format = "pdf"

    def __init__(self):
        # type: () -> None
        super(XeLatex, self).__init__()
        self.latexmk_prog_repl = "-%s=%s" % ("pdflatex", self.bin_path)


class ImageConverter(CommandBase):

    @property
    def output_format(self):
        # type: () -> Text
        raise NotImplementedError

    def get_bin_path(self, check_only=False):
        bin_path_dir = latex_settings["bin_path"].get(
            "RELATE_%s_BIN_DIR" % self.name.upper(),
            "")
        return os.path.join(bin_path_dir, self.cmd.lower())

    def do_convert(self, compiled_file_path, image_path, working_dir):
        cmdline = self._get_convert_cmdline(
            compiled_file_path, image_path)

        _output, error, status = popen_wrapper(
            cmdline,
            cwd=working_dir
        )

        return status == 0, error

    def _get_convert_cmdline(
            self, input_filepath, output_filepath):
        # type: (Text, Text) -> List[Text]
        raise NotImplementedError


class Dvipng(TexCompilerBase, ImageConverter):
    # Inheritate TexCompilerBase's bin_path
    # since dvipng is usually installed in
    # latex compilers' bin dir.
    name = "dvipng"
    cmd = "dvipng"
    output_format = "png"

    def _get_convert_cmdline(
            self, input_filepath, output_filepath):
        # type: (Text, Text) -> List[Text]
        return [self.bin_path,
                '-o', output_filepath,
                '-pp', '1',
                '-T', 'tight',
                '-z9',
                input_filepath]


class Dvisvg(TexCompilerBase, ImageConverter):
    # Inheritate TexCompilerBase's bin_path
    # since dvisvgm is usually installed in
    # latex compilers' bin dir.
    name = "dvisvg"
    cmd = "dvisvgm"
    output_format = "svg"

    def _get_convert_cmdline(
            self, input_filepath, output_filepath):
        # type: (Text, Text) -> List[Text]
        return[self.bin_path,
            '--no-fonts',
            '-o', output_filepath,
            input_filepath]


class ImageMagick(ImageConverter):
    name = "ImageMagick"
    cmd = "convert"
    output_format = "png"

    # https://github.com/dahlia/wand/issues/316
    max_version = "7"

    def get_bin_path(self, check_only=False):
        bin_path_dir = latex_settings["bin_path"].get(
            "RELATE_%s_BIN_DIR" % self.name.upper(), "")
        if bin_path_dir:
            os.environ.setdefault("MAGICK_HOME", bin_path_dir)
        else:
            if check_only and sys.platform.startswith("win"):
                from wand.api import library_paths
                for p in library_paths():
                    if p[0]:
                        bin_path_dir = os.path.dirname(p[0])
                        break

        return os.path.join(bin_path_dir, self.cmd.lower())

    def do_convert(self, compiled_file_path, image_path, working_dir):
        success = True
        error = ""
        try:
            # resolution is density in ImageMagick, density=96 and quality=85
            # is google image resolution for images.
            with wand_image(filename=compiled_file_path, resolution=96) as original:
                with original.convert(self.output_format) as converted:
                    # converted.compression_quality = 85
                    converted.trim()
                    converted.save(filename=image_path)
        except Exception as e:
            success = False
            error = "%s: %s" % (type(e).__name__, str(e))

        return success, error

# }}}


# {{{ convert file to data uri

def get_image_datauri(file_path):
    # type: (Text) -> Optional[Text]
    """
    Convert file to data URI
    """
    if not file_path:
        return None

    try:
        buf = file_read(file_path)
    except OSError:
        raise

    from mimetypes import guess_type
    mime_type = guess_type(file_path)[0]

    from base64 import b64encode
    return "data:%(mime_type)s;base64,%(b64)s" % {
        "mime_type": mime_type,
        "b64": b64encode(buf).decode(),
    }

# }}}


# {{{ Base tex2img class

class Tex2ImgBase(object):
    """The abstract class of converting tex source to images.
    """

    @property
    def compiler(self):
        # type: () -> LatexCompiler
        """
        :return: an instance of `LatexCompiler`
        """
        raise NotImplementedError()

    @property
    def converter(self):
        # type: () -> ImageConverter
        """
        :return: an instance of `Imageconverter`
        """
        raise NotImplementedError()

    def __init__(self, tex_source, tex_filename):
        # type: (...) -> None
        """
        :param tex_source: Required, a string representing the
        full tex source code.
        :param tex_filename: Optional, a string
        """

        if tex_source:
            tex_source = tex_source.strip()
        if not tex_source:
            raise ValueError(
                _("Param 'tex_source' can not be an empty string")
            )
        assert isinstance(tex_source, six.text_type)
        self.tex_source = tex_source

        self.working_dir = None

        self.basename = get_basename_or_md5(
            tex_filename, tex_source)

        self.image_format = self.converter.output_format \
            .replace(".", "").lower()
        self.image_ext = ".%s" % self.image_format

        self.compiled_ext = ".%s" % self.compiler.output_format\
            .replace(".", "").lower()

        self.datauri_basename = (
            "%s_%s_%s_datauri" % (self.basename,
                          self.compiler.cmd,
                          self.image_format)
        )

    def get_compiler_cmdline(self, tex_path):
        # type: (Text) -> List[Text]
        return self.compiler.get_latexmk_subpro_cmdline(tex_path)

    def _remove_working_dir(self):
        # type: () -> None
        if self.working_dir:
            shutil.rmtree(self.working_dir)

    def get_compiled_file(self):
        # type: () -> Optional[Text]
        """
        Compile latex source.
        :return: string, the path of the compiled file if succeeded.
        """
        from tempfile import mkdtemp

        # https://github.com/python/mypy/issues/1833
        self.working_dir = mkdtemp(prefix="RELATE_LATEX_")  # type: ignore

        assert self.basename is not None
        assert self.working_dir is not None
        tex_filename = self.basename + ".tex"
        tex_path = os.path.join(self.working_dir, tex_filename)
        file_write(tex_path, self.tex_source.encode('UTF-8'))

        assert tex_path is not None
        log_path = tex_path.replace(".tex", ".log")
        compiled_file_path = tex_path.replace(
            ".tex", self.compiled_ext)

        cmdline = self.get_compiler_cmdline(tex_path)
        output, error, status = popen_wrapper(
            cmdline, cwd=self.working_dir)

        if status != 0:
            try:
                log = file_read(log_path).decode("utf-8")
            except OSError:
                # no log file is generated
                self._remove_working_dir()
                raise RuntimeError(error)

            try:
                log = get_abstract_latex_log(log)

                err_key = ("latex_err:%s:%s"
                           % (self.compiler.cmd, self.basename))

                try:
                    import django.core.cache as cache
                except ImproperlyConfigured:
                    err_cache_key = None
                else:
                    def_cache = get_latex_cache(cache)
                    err_cache_key = err_key

                if not isinstance(log, six.text_type):
                    log = six.text_type(log)

                try:
                    get_latex_error_mongo_collection().update_one(
                        {"key": err_key},
                        {"$setOnInsert":
                             {"key": err_key,
                              "errorlog": log.encode('utf-8'),
                              "source": self.tex_source.encode('utf-8'),
                              "creation_time": local_now()
                              }},
                        upsert=True,
                    )
                except DuplicateKeyError:
                    pass

                if err_cache_key:
                    assert isinstance(log, six.text_type)
                    if len(log) <= getattr(
                            settings, "RELATE_CACHE_MAX_BYTES", 0):
                        def_cache.add(err_cache_key, log)

            except:
                raise
            finally:
                self._remove_working_dir()
                raise ValueError(
                    "<pre>%s</pre>" % escape(log).strip())

        if os.path.isfile(compiled_file_path):
            return compiled_file_path
        else:
            self._remove_working_dir()
            raise RuntimeError(
                string_concat(
                    "%s." % error,
                    _('No %s file was produced.')
                    % self.compiler.output_format)
            )

    def get_converted_image_datauri(self):
        # type: () -> Optional[Text]
        """
        Convert compiled file into image.
        :return: string, the datauri
        """
        compiled_file_path = self.get_compiled_file()
        if not compiled_file_path:
            return None
        image_path = compiled_file_path.replace(
            self.compiled_ext,
            self.image_ext)

        convert_sucess, error = self.converter.do_convert(
            compiled_file_path, image_path, self.working_dir)

        if not convert_sucess:
            self._remove_working_dir()
            raise RuntimeError(error)

        n_images = get_number_of_images(image_path, self.image_ext)
        if n_images == 0:
            raise ValueError(
                _("No image was generated."))
        elif n_images > 1:
            raise ValueError(
                string_concat(
                    "%s images are generated while expecting 1, "
                    "possibly due to long pdf file."
                    % (n_images, )
                ))

        try:
            datauri = get_image_datauri(image_path)
        finally:
            self._remove_working_dir()

        return datauri

    def get_compile_err_cached(self, force_regenerate=False):
        # type: (Optional[bool]) -> Optional[Text]
        """
        If the problematic latex source is not modified, check
        whether there is error log both in cache or mongo.
        If it exists, raise the error.
        :return: None if no error log find.
        """
        err_result = None
        err_key = ("latex_err:%s:%s"
                         % (self.compiler.cmd, self.basename))

        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            err_cache_key = None
        else:
            def_cache = get_latex_cache(cache)
            err_cache_key = err_key
            # Memcache is apparently limited to 250 characters.
            if len(err_cache_key) < 240:
                if not force_regenerate:
                    err_result = def_cache.get(err_cache_key)
                else:
                    def_cache.delete(err_cache_key)
                    get_latex_error_mongo_collection().delete_one({"key": err_key})
            if err_result is not None:
                raise ValueError(
                    "<pre>%s</pre>" % escape(err_result).strip())

        if err_result is None:
            # read the saved err_log if it exists
            mongo_result = get_latex_error_mongo_collection().find_one(
                {"key": err_key}
            )
            if mongo_result:
                err_result = mongo_result["errorlog"].decode("utf-8")

        if err_result:
            if err_cache_key:
                assert isinstance(err_result, six.text_type)
                if len(err_result) <= getattr(
                        settings, "RELATE_CACHE_MAX_BYTES", 0):
                        def_cache.add(err_cache_key, err_result)

            raise ValueError(
                "<pre>%s</pre>" % escape(err_result).strip())

        return None

    def get_data_uri_cached(self, force_regenerate=False):
        # type: (Optional[bool]) -> Text
        """
        :param force_regenerate: :class:`Bool', if True, the tex file
        will be recompiled and re-convert the image, regardless of
        existing file or cached result.
        :return: string, data uri of the coverted image.
        """
        result = None

        if force_regenerate:
            # first remove cached error results and files
            self.get_compile_err_cached(force_regenerate)
            result = self.get_converted_image_datauri()
            if not isinstance(result, six.text_type):
                result = six.text_type(result)

        if not result:
            err_result = self.get_compile_err_cached(force_regenerate)
            if err_result:
                raise ValueError(
                    "<pre>%s</pre>" % escape(err_result).strip())

        # we make the key so that it can be used when cache is not configured
        # and it can be used by mongo
        uri_key = (
            "latex2img:%s:%s" % (
                self.compiler.cmd,
                md5(
                    self.datauri_basename.encode("utf-8")
                ).hexdigest()
            )
        )
        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            uri_cache_key = None
        else:
            def_cache = get_latex_cache(cache)
            uri_cache_key = uri_key

            if force_regenerate:
                def_cache.delete(uri_cache_key)
                get_latex_datauri_mongo_collection().delete_one({"key": uri_key})
            elif not result:
                # Memcache is apparently limited to 250 characters.
                if len(uri_cache_key) < 240:
                    result = def_cache.get(uri_cache_key)
                    if result:
                        if not isinstance(result, six.text_type):
                            result = six.text_type(result)
                        return result

        # Neighter regenerated nor cached,
        # then read from mongo
        if not result:
            mongo_result = get_latex_datauri_mongo_collection().find_one(
                {"key": uri_key}
            )
            if mongo_result:
                result = mongo_result["datauri"].decode("utf-8")
                if not isinstance(result, six.text_type):
                    result = six.text_type(result)

        # Not found in mongo, regenerate it
        if not result:
            result = self.get_converted_image_datauri()
            if not isinstance(result, six.text_type):
                result = six.text_type(result)
            try:
                get_latex_datauri_mongo_collection().update_one(
                    {"key": uri_key},
                    {"$setOnInsert":
                         {"key": uri_key,
                          "datauri": result.encode('utf-8'),
                          "creation_time": local_now()
                          }},
                    upsert=True,
                )
            except DuplicateKeyError:
                pass

        assert result

        # no cache configured
        if not uri_cache_key:
            return result

        # cache configure, but image not cached
        allowed_max_bytes = getattr(
            settings, "RELATE_IMAGECACHE_MAX_BYTES",
            getattr(
                settings, "RELATE_CACHE_MAX_BYTES",
            )
        )

        if len(result) <= allowed_max_bytes:
            # image size larger than allowed_max_bytes
            # won't be cached, espeically for svgs.
            assert isinstance(result, six.text_type), \
                uri_cache_key
            def_cache.add(uri_cache_key, result)
        return result

# }}}


# {{{ derived tex2img converter

class Latex2Svg(Tex2ImgBase):
    compiler = Latex()
    converter = Dvisvg()


class Lualatex2Png(Tex2ImgBase):
    compiler = LuaLatex()
    converter = ImageMagick()


class Latex2Png(Tex2ImgBase):
    compiler = Latex()
    converter = Dvipng()


class Pdflatex2Png(Tex2ImgBase):
    compiler = PdfLatex()
    converter = ImageMagick()


class Xelatex2Png(Tex2ImgBase):
    compiler = XeLatex()
    converter = ImageMagick()

# }}}


# {{{ get tex2img class

ALLOWED_COMPILER = ['latex', 'pdflatex', 'xelatex', 'lualatex']
ALLOWED_LATEX2IMG_FORMAT = ['png', 'svg']
ALLOWED_COMPILER_FORMAT_COMBINATION = (
    ("latex", "png"),
    ("latex", "svg"),
    ("lualatex", "png"),
    ("pdflatex", "png"),
    ("xelatex", "png")
)


def get_tex2img_class(compiler, image_format):
    # type: (Text, Text) -> Any
    image_format = image_format.replace(".", "").lower()
    compiler = compiler.lower()
    if image_format not in ALLOWED_LATEX2IMG_FORMAT:
        raise ValueError(
            _("Unsupported image format '%s'") % image_format)

    if compiler not in ALLOWED_COMPILER:
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


# {{{ check if multiple images are generated due to long pdf

def get_number_of_images(image_path, image_ext):
    # type: (Text, Text) -> int
    if os.path.isfile(image_path):
        return 1
    count = 0
    while True:
        try_path = (
            "%(image_path)s-%(number)d%(ext)s"
            % {"image_path": image_path.replace(image_ext, ""),
               "number": count,
               "ext": image_ext
               }
        )
        if not os.path.isfile(try_path):
            break
        count += 1

    return count

# }}}


def convert_doc_to_pdf_blob(word_data):
    # Use soffice to convert doc/docx to pdf file

    from tempfile import mkdtemp
    from os import path

    soffice_path = getattr(settings, "SOFFICE_PATH")

    try:
        # windows
        from winmagic import magic
    except ImportError:
        import magic

    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(word_data)

    print(mime_type)

    if mime_type not in [
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return None

    # https://github.com/python/mypy/issues/1833
    working_dir = mkdtemp(prefix="RELATE_DOC_TO_PDF")  # type: ignore
    file_name = "word_file"
    file_path = path.join(working_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(word_data)

    out, err, status = popen_wrapper(
        [soffice_path, '--headless', '--convert-to', 'pdf',
         '--outdir', working_dir, file_path],
        cwd=working_dir)

    print(out)
    print(err)
    print(status)

    pdf_path = file_path + ".pdf"
    if not path.exists(pdf_path):
        return None

    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
    finally:
        shutil.rmtree(working_dir)

    return pdf_data


# vim: foldmethod=marker
