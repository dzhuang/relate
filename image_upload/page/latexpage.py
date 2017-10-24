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
from io import BytesIO
import pickle
from hashlib import md5
from base64 import b64encode
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from bson.errors import InvalidId
from plugins.latex.utils import get_latex_cache

# {{{ mypy
if False:
    from typing import Text, Callable, Any, Dict, Tuple, Union, Optional  # noqa
    from course.utils import PageContext  # noqa
    from pymongo import MongoClient  # noqa
    from pymongo.collection import Collection  # noqa
# }}}


from django.utils.translation import ugettext as _, string_concat
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.conf import settings
from django.utils.html import escape

from relate.utils import local_now, Struct, struct_to_dict

from course.content import markup_to_html as mth
from course.page.base import (
    PageBaseWithTitle, PageBaseWithValue,
    PageBaseWithCorrectAnswer)
from course.page import (  # type: ignore
    ChoiceQuestion, MultipleChoiceQuestion, TextQuestion,
    InlineMultiQuestion)
from course.validation import ValidationError
from course.content import get_repo_blob, get_repo_blob_data_cached
from plugins.latex.utils import get_mongo_db
from course.page.code import (
    PythonCodeQuestion, PythonCodeQuestionWithHumanTextFeedback,
    request_python_run_with_retries)

from image_upload.page.imgupload import ImageUploadQuestion


def _debug_print(s):

    # debugging switch
    debug = False

    settings_debug = getattr(settings, "DEBUG", False)
    debug = debug or settings_debug

    if debug:
        print(s)


debug_print = _debug_print


CACHE_VERSION = "V0"
# This should be 1, because request_python_run_with_retries already tried 3 times
MAX_JINJIA_RETRY = 1
DB = get_mongo_db()


def make_latex_page_key(key_making_string_md5):
    return ("latexpage:%s:%s"
            % (CACHE_VERSION,
               key_making_string_md5))


def get_key_making_string_md5_hash(template_hash, question_data):
    # type: (Text, Text) -> Text
    key_making_string = template_hash
    if question_data:
        key_making_string += question_data
    return md5(key_making_string.encode("utf-8")).hexdigest()


mong_latex_page_settings = settings.RELATE_LATEX_SETTINGS["latex_page"]
LATEX_PAGE_COLLECTION_NAME = mong_latex_page_settings.get(
    "RELATE_LATEX_PAGE_COLLECTION_NAME",
    "relate_latex_page")
LATEX_PAGE_PART_COLLECTION_NAME = mong_latex_page_settings.get(
    "RELATE_LATEX_PAGE_PART_COLLECTION_NAME",
    "relate_latex_page_part"
)
LATEX_PAGE_COMMITSHA_TEMPLATE_PAIR_COLLECTION = mong_latex_page_settings.get(
    "RELATE_LATEX_PAGE_COMMITSHA_TEMPLATE_PAIR_COLLECTION",
    "relate_latex_page_commitsha_template_pair"
)


def get_latex_page_mongo_collection(name=None, db=DB, index_name="key"):
    # type: (Optional[Text], Optional[MongoClient], Optional[Text]) -> Collection
    # return the collection storing the page
    if not name:
        name = LATEX_PAGE_COLLECTION_NAME
    collection = db[name]  # type: ignore
    if index_name:
        collection.ensure_index(index_name, unique=True)
    return collection


def get_latex_page_part_mongo_collection(name=None, db=DB, index_name="key"):
    # type: (Optional[Text], Optional[MongoClient], Optional[Text]) -> Collection
    # return the collection storing the page parts
    if not name:
        name = LATEX_PAGE_PART_COLLECTION_NAME
    collection = db[name]  # type: ignore
    if index_name:
        collection.ensure_index(index_name, unique=True)
    return collection


def get_latex_page_commitsha_template_pair_collection(
        name=None, db=DB, index_name="template_hash"):
    # type: (Optional[Text], Optional[MongoClient], Optional[Text]) -> Collection
    # return the collection storing the commit sha pairs
    if not name:
        name = LATEX_PAGE_COMMITSHA_TEMPLATE_PAIR_COLLECTION
    collection = db[name]  # type: ignore
    if index_name:
        collection.ensure_index(index_name, unique=True)
    return collection


def markup_to_html(
        page_context,  # type: PageContext
        text,  # type: Text
        warm_up_only=False,  # type: bool
        use_jinja=True,  # type: bool
        reverse_func=None,  # type: Callable
        ):
    # type: (...) -> Text

    return mth(
            page_context.course,
            page_context.repo,
            page_context.commit_sha,
            text,
            validate_only=warm_up_only,
            use_jinja=use_jinja,
            reverse_func=reverse_func)


class LatexRandomQuestionBase(PageBaseWithTitle, PageBaseWithValue,
                          PageBaseWithCorrectAnswer):
    grading_sort_by_page_data = True

    @property
    def required_attrs_if_runpy_or_full_code_missing(self):
        # if runpy_file or full_process_code is missing, the following
        # attribute must present in page_desc
        return ["question_process_code"]

    def __init__(self, vctx, location, page_desc):
        super(LatexRandomQuestionBase, self).__init__(vctx, location, page_desc)

        if vctx is not None and hasattr(page_desc, "data_files"):
            # {{{ validate random_question_data_file
            if page_desc.random_question_data_file not in page_desc.data_files:
                raise ValidationError(
                    string_concat(
                        "%s: " % location,
                        _("'%s' should be listed in 'data_files'")
                        % page_desc.random_question_data_file))

            repo_bytes_data = get_repo_blob_data_cached(
                vctx.repo,
                page_desc.random_question_data_file,
                vctx.commit_sha)
            bio = BytesIO(repo_bytes_data)
            try:
                # py3
                repo_data_loaded = pickle.load(bio, encoding="latin-1")
            except TypeError:
                # py2
                repo_data_loaded = pickle.load(bio)
            if not isinstance(repo_data_loaded, (list, tuple)):
                raise ValidationError(
                    string_concat(
                        "%s: " % location,
                        _("'%s' must be dumped from a list or tuple")
                        % page_desc.random_question_data_file))
            n_data = len(repo_data_loaded)
            if n_data == 0:
                raise ValidationError(
                    string_concat(
                        "%s: " % location,
                        _("'%s' seems to be empty, that's not valid")
                        % page_desc.random_question_data_file))
            # }}}

            if hasattr(page_desc, "runpy_file"):
                if page_desc.runpy_file not in page_desc.data_files:
                    raise ValidationError(
                        string_concat(
                            "%s: " % location,
                            _("'%s' should be listed in 'data_files'")
                            % page_desc.runpy_file))

            if hasattr(page_desc, "cache_key_files"):
                for cf in page_desc.cache_key_files:
                    if cf not in page_desc.data_files:
                        raise ValidationError(
                            string_concat(
                                location,
                                ": ",
                                _("'%s' should be listed in 'data_files'")
                                % cf))

            if hasattr(page_desc, "excluded_cache_key_files"):
                for cf in page_desc.excluded_cache_key_files:
                    if cf not in page_desc.data_files:
                        vctx.add_warning(location, "'%s' is not in 'data_files'"
                                              % cf)

            for data_file in page_desc.data_files:
                try:
                    if not isinstance(data_file, str):
                        # This seems never happened
                        raise ObjectDoesNotExist()

                    get_repo_blob(vctx.repo, data_file, vctx.commit_sha)
                except ObjectDoesNotExist:
                    raise ValidationError("%s: data file '%s' not found"
                            % (location, data_file))

            if not hasattr(page_desc, "runpy_file"):
                if self.__class__.__name__ != "LatexRandomCodeQuestion":
                    if not hasattr(page_desc, "full_process_code"):
                        missing_part = []
                        for part in (
                                self.required_attrs_if_runpy_or_full_code_missing):
                            if not hasattr(page_desc, part):
                                missing_part.append(part)
                        if missing_part:
                            raise ValidationError(
                                string_concat(
                                    location,
                                    ": ",
                                    _("'%s' must be configured when neiher "
                                      "'runpy_file' nor 'full_processing_code'"
                                      " is configured.")
                                    % ", ".join(missing_part)))

                    vctx.add_warning(
                        location,
                        _("%s not using attribute "
                          "'runpy_file' is for debug only, it should not "
                          "be used in production.")
                        % self.__class__.__name__
                    )
            else:
                try:
                    runpy_file = get_repo_blob_data_cached(
                        vctx.repo, page_desc.runpy_file,
                        vctx.commit_sha)
                    compile(runpy_file, '<runpy file>', 'exec')
                    del runpy_file
                except SyntaxError:
                    raise ValidationError(
                        string_concat("%s: " % location,
                                      _("'%s' is not a valid Python script file.")
                                      % page_desc.runpy_file))

            if hasattr(page_desc, "cache_key_attrs"):
                for attr in page_desc.cache_key_attrs:
                    if not hasattr(page_desc, attr):
                        raise ValidationError("%s: attribute '%s' not found"
                                              % (location, attr))

        self.docker_run_timeout = getattr(page_desc, "docker_timeout", 5)

        # These files/attrs are used to generate rendered body and correct answer

        # Whether use question data file as cache
        use_question_data_file_as_cache = getattr(
            page_desc, "use_question_data_file_as_cache", False)
        self.cache_key_files = getattr(
            page_desc, "cache_key_files", getattr(page_desc, "data_files"))
        excluded_cache_key_files = getattr(
            page_desc, "excluded_cache_key_files", None)
        if excluded_cache_key_files:
            self.cache_key_files = (
                [f for f in self.cache_key_files
                 if f not in excluded_cache_key_files])
        if not use_question_data_file_as_cache:
            self.cache_key_files = (
                [f for f in self.cache_key_files
                 if f != page_desc.random_question_data_file])
        self.cache_key_attrs = getattr(page_desc, "cache_key_attrs", [])

        self.runpy_context = {}
        if getattr(page_desc, "runpy_context", None):
            self.runpy_context = struct_to_dict(page_desc.runpy_context)

        if not self.cache_key_attrs:
            all_process_attributes = [
                attr for attr in dir(self.page_desc)
                if attr.endswith("_process_code")]
            all_process_attributes.append("background_code")
            for attr in all_process_attributes:
                if hasattr(page_desc, attr):
                    self.cache_key_attrs.append(attr)

        self.will_receive_grade = getattr(page_desc, "will_receive_grade", True)
        self.updated_full_desc = None
        self.is_full_desc_updated = False
        self.error_getting_updated_full_desc = None
        self.error_updating_page_desc = None

    def update_page_full_desc(self, page_context, page_data):
        if self.updated_full_desc is None and not self.is_full_desc_updated:
            self._update_page_full_desc(page_context, page_data)
            self.is_full_desc_updated = True

    def _update_page_full_desc(self, page_context, page_data):
        if (hasattr(self.page_desc, "full_process_code")
            or
                hasattr(self.page_desc, "runpy_file")):
            success, result = (
                self.get_full_desc_from_full_process(
                    page_context, page_data))
            if success:
                self.updated_full_desc = result
            else:
                self.updated_full_desc = {}
                self.error_getting_updated_full_desc = result

    def make_form(
            self,
            page_context,  # type: PageContext
            page_data,  # type: Any
            answer_data,  # type: Any
            page_behavior,  # type: Any
            ):

        self.update_page_full_desc(page_context, page_data)

        if self.error_getting_updated_full_desc:
            return None

        if self.error_updating_page_desc:
            return None
        return super(LatexRandomQuestionBase, self).make_form(
            page_context, page_data, answer_data, page_behavior
        )

    def get_full_desc_from_full_process(self, page_context, page_data):
        # type: (PageContext, Dict) -> Tuple[bool, Union[Dict, Text]]
        success = False  # type: bool
        result = None  # type: Any

        try:
            for i in range(MAX_JINJIA_RETRY):
                success, result = self.get_cached_result(
                    page_context, page_data, part="full")
                if success:
                    assert isinstance(result, dict)
                    break
        except KeyError:
            pass

        return success, result

    def required_attrs(self):
        return super(LatexRandomQuestionBase, self).required_attrs() + (
            ("data_files", (list, str)),
            ("random_question_data_file", str),
        )

    def allowed_attrs(self):
        return super(LatexRandomQuestionBase, self).allowed_attrs() + (
            ("background_code", str),
            ('runpy_file', str),
            ('runpy_context', Struct),
            ("question_process_code", str),
            ("answer_process_code", str),
            ("full_process_code", str),
            ("docker_timeout", (int, float)),
            ("excluded_cache_key_files", list),
            ("cache_key_files", list),
            ("cache_key_attrs", list),
            ("use_question_data_file_as_cache", bool),
            ("warm_up_by_sandbox", bool),
            ("will_receive_grade", bool),
            ("answer_explanation_process_code", str),
        )

    def is_answer_gradable(self):
        return self.will_receive_grade

    def generate_new_page_data(self, page_context, question_data):
        commit_sha = page_context.commit_sha.decode()
        new_template_hash = self.generate_template_hash(page_context)
        new_hash_id = (
            self.get_or_create_template_hash_id(commit_sha, new_template_hash)
        )
        new_key_making_string_md5 = get_key_making_string_md5_hash(
            new_template_hash, question_data)
        return {
            "template_hash": new_template_hash,
            "template_hash_id": str(new_hash_id),
            "key_making_string_md5": new_key_making_string_md5}

    def update_page_data(self, page_context, page_data):
        # type: (PageContext, Dict) -> Tuple[bool, Dict]

        """
        This happened only when course commit sha changed.

        The page is cached using `key_making_string_md5` as md5 key making string.
        While `key_making_string_md5` is generated by
        `get_key_making_string_md5_hash(template_hash, question_data)`

        We store question_data in page_data, when the self.initialize_page_data()
        is called.
        We store template_hash in page_data, so that we don't need to calculate it
        each time when updating course content with the latexpage content unchanged.

        If question_data is not None, it should always be the same, no matter what
        the course commit sha is. However, template_hash is generated by
        `self.generate_template_hash(page_context), that means the template_hash
        will change when `self.cache_key_files`, `self.cache_key_attrs` and
        `self.runpy_context` changed. If those attributes are not changed,
        `template_hash` should remain the same no matter how course commit sha
        varies.

        To get the template_hash, we first need to query template_hash_id in
        page_commitsha_template_pair_collection (a mongo collection), which is used
        to store document containing info of template_hash for different commit sha,
        and with possible redirect template_hash_id (with the format
        (old_commit_sha)_next) to other documents which store other template_hash
        when content of the rendered part changed from old_commit_sha.
        """

        question_data = page_data.get("question_data", None)
        template_hash = page_data.get("template_hash", None)
        key_making_string_md5 = page_data.get("key_making_string_md5", None)
        template_hash_id = page_data.get("template_hash_id", None)

        if question_data is None:
            new_page_data = self.initialize_page_data(page_context)
            return True, new_page_data

        commit_sha = page_context.commit_sha.decode()
        if not (template_hash and template_hash_id and key_making_string_md5):
            return True, self.generate_new_page_data(page_context, question_data)

        try:
            exist_entry = (
                get_latex_page_commitsha_template_pair_collection().find_one(
                    {"_id": ObjectId(template_hash_id)}))
        except InvalidId:
            exist_entry = None

        # mongo data is broken
        if not exist_entry:
            return True, self.generate_new_page_data(page_context, question_data)

        # mongo data found
        else:
            # hash found in the entry
            match_template_hash = exist_entry.get(commit_sha, None)

            # hash not found in the entry, but there's a redirect "(commit_sha)_next"
            # which give the ObjectId of the new template hash which don't match the
            # one in the page_data
            match_template_hash_redirect_id = exist_entry.get(
                "%s_next" % commit_sha, None)

            # that above two don't coexist
            assert not (match_template_hash and match_template_hash_redirect_id)

            if match_template_hash:
                if match_template_hash == template_hash:
                    return False, {}
                else:
                    new_page_data = (
                        self.generate_new_page_data(page_context, question_data))

                    # the template_hash don't belong to this entry
                    # so we generate a redirect field "(commit_sha)_next",
                    # for the new template_hash, with that new entry's id
                    # in the field
                    get_latex_page_commitsha_template_pair_collection().update_one(
                        {"_id": ObjectId(template_hash_id),
                         commit_sha: {"$exists": False},
                         "%s_next" % commit_sha: {"$exists": False}},
                        {"$set": {
                            "%s_next" % commit_sha:
                                new_page_data["template_hash_id"]}}
                    )
                    return True, new_page_data

            if match_template_hash_redirect_id:
                redirect_entry = (
                    get_latex_page_commitsha_template_pair_collection().find_one(
                        {"_id": ObjectId(match_template_hash_redirect_id)}))

                # in case the entry is broken
                if not redirect_entry:
                    new_page_data = (
                        self.generate_new_page_data(page_context, question_data))

                    # the entry is broken, so we need to update where the source
                    # who told us to redirect here
                    get_latex_page_commitsha_template_pair_collection().update_one(
                        {"_id": ObjectId(template_hash_id),
                         commit_sha: {"$exists": False},
                        "%s_next" % commit_sha: {"$exists": True}},
                        {"$set": {"%s_next" % commit_sha:
                                      new_page_data["template_hash_id"]}}
                    )
                    return True, new_page_data

                # the entry exists
                else:
                    new_template_hash = redirect_entry.get(commit_sha, None)
                    if new_template_hash:
                        new_key_making_string_md5 = (
                            get_key_making_string_md5_hash(
                                new_template_hash, question_data))
                        return True, {
                            "template_hash": new_template_hash,
                            "template_hash_id": match_template_hash_redirect_id,
                            "key_making_string_md5": new_key_making_string_md5
                        }

            assert not (match_template_hash or match_template_hash_redirect_id)
            # Neither match_template_hash nor match_template_hash_redirect_id

            new_page_data = self.generate_new_page_data(page_context, question_data)
            if new_page_data["template_hash"] == template_hash:
                get_latex_page_commitsha_template_pair_collection().update_one(
                    {"_id": ObjectId(template_hash_id),
                     commit_sha: {"$exists": False}},
                    {"$set": {commit_sha: template_hash}}
                )
                return False, {}
            else:
                get_latex_page_commitsha_template_pair_collection().update_one(
                    {"_id": ObjectId(template_hash_id),
                     commit_sha: {"$exists": False}},
                    {"$set": {"%s_next" % commit_sha:
                                  new_page_data["template_hash_id"]}}
                )
                return True, new_page_data

    def generate_template_hash(self, page_context):
        # type: (PageContext) -> Text
        from image_upload.utils import (
            minify_python_script, strip_template_comments)
        template_string = ""
        if self.cache_key_files:
            for cfile in self.cache_key_files:
                cfile_data = get_repo_blob_data_cached(
                    page_context.repo,
                    cfile,
                    page_context.commit_sha).decode("utf-8")
                if cfile.endswith(".py"):
                    cfile_data = minify_python_script(cfile_data)
                elif cfile.endswith(".tex"):
                    cfile_data = strip_template_comments(cfile_data)
                template_string += cfile_data

        if self.cache_key_attrs:
            for cattr in self.cache_key_attrs:
                cattr_string = repr(getattr(self.page_desc, cattr)).strip()
                if (cattr.endswith("_code")
                    and
                        # this is to avoid imported jinja macro in the attribute
                        not cattr_string.startswith("{")):
                    cattr_string = minify_python_script(cattr_string)
                template_string += cattr_string

        if self.runpy_context:
            # runpy_context is a dict, which may have different repr
            sorted_runpy_context_str = repr(sorted(
                list((k, self.runpy_context[k]) for k in self.runpy_context.keys()),
                key=lambda x: x[0]))
            template_string += sorted_runpy_context_str

        return md5(template_string.encode("utf-8")).hexdigest()

    def initialize_page_data(self, page_context):
        # type: (PageContext) -> Dict

        # This should never happen
        if not hasattr(self.page_desc, "random_question_data_file"):
            return {}

        commit_sha = page_context.commit_sha.decode()
        warm_up_by_sandbox = False
        if page_context.in_sandbox:
            warm_up_by_sandbox = getattr(
                self.page_desc, "warm_up_by_sandbox", True)

        # get random question_data
        repo_bytes_data = get_repo_blob_data_cached(
            page_context.repo,
            self.page_desc.random_question_data_file,
            page_context.commit_sha)
        bio = BytesIO(repo_bytes_data)
        try:
            # py3
            repo_data_loaded = pickle.load(bio, encoding="latin-1")
        except TypeError:
            # py2
            repo_data_loaded = pickle.load(bio)

        assert isinstance(repo_data_loaded, (list, tuple))
        all_data = list(repo_data_loaded)

        from random import choice

        question_data = None
        key_making_string_md5 = None

        # template_string is the string independent of data
        template_hash = self.generate_template_hash(page_context)
        _id = self.get_or_create_template_hash_id(commit_sha, template_hash)

        for i in range(len(all_data)):
            if not page_context.in_sandbox or not warm_up_by_sandbox:
                random_data = choice(all_data)
            else:
                random_data = all_data[i]
            selected_data_bytes = BytesIO()
            pickle.dump(random_data, selected_data_bytes)

            # question_data is the original data
            # key_making_string is going to be deprecated, which is now used
            # by referring cache key
            question_data = b64encode(selected_data_bytes.getvalue()).decode()
            key_making_string_md5 = get_key_making_string_md5_hash(
                    template_hash, question_data)

            # this is used to let sandbox do the warm up job for
            # sequentially ordered data(not random)
            if not page_context.in_sandbox:
                break

            if not warm_up_by_sandbox:
                break

            page_data = {
                "question_data": question_data,
                "template_hash": template_hash,
                "key_making_string_md5": key_making_string_md5
            }

            # let all processing code run to get the cache
            all_process_attribute_parts = [
                attr.replace("_process_code", "")
                for attr in dir(self.page_desc)
                if attr.endswith("_process_code")]

            if "full" in all_process_attribute_parts:
                all_process_attribute_parts = ["full"]

            for part in all_process_attribute_parts:
                try:
                    key_exist, result = self.get_cached_result(
                            page_context, page_data, part=part,
                            warm_up_only=True)
                    if key_exist:
                        # when result is full or by run_py
                        if isinstance(result, dict):
                            for k, v in result.items():
                                markup_to_html(page_context, v,
                                               warm_up_only=True)
                        else:
                            markup_to_html(page_context, result, warm_up_only=True)

                except KeyError:
                    continue

        return {"question_data": question_data,
                "template_hash": template_hash,
                "template_hash_id": _id,
                "key_making_string_md5": key_making_string_md5
                }

    def get_or_create_template_hash_id(self, commit_sha, template_hash):
        # type: (Text, Text) -> Text
        # TODO: find or insert
        info = get_latex_page_commitsha_template_pair_collection().find_one(
            {commit_sha: template_hash})
        _id = None
        if info:
            _id = str(info.get("_id"))
        else:
            try:
                info = (
                    get_latex_page_commitsha_template_pair_collection().update_one(
                        {"template_hash": template_hash},
                        {"$setOnInsert":
                             {"template_hash": template_hash,
                              "creation_time": local_now()
                              },
                         "$set": {commit_sha: template_hash}},
                        upsert=True,
                    ))
                if info.upserted_id:
                    _id = str(info.upserted_id)
            except DuplicateKeyError:
                pass
            if not _id:
                info = get_latex_page_commitsha_template_pair_collection().find_one(
                    {commit_sha: template_hash})
                assert info
                _id = str(info.get("_id"))
        assert (_id)
        return _id

    def get_cached_result(self, page_context,
                          page_data, part="", warm_up_only=False):
        # type: (PageContext, Dict, Optional[Text], Optional[bool]) -> Tuple[bool, Optional[Union[Text, Dict]]]  # noqa

        try:
            key_making_string_md5 = page_data["key_making_string_md5"]
        except KeyError:
            # the page can be rendered even key_making_string_md5 and template_hash
            # and template_hash_id is not available
            if page_data.get("question_data") is None:
                from course.page import InvalidPageData
                error = string_concat(
                    _("The page data stored in the database was found "
                      "to be invalid for the page as given in the "
                      "course content. Likely the course content was "
                      "changed in an incompatible way (say, by adding "
                      "an option to a choice question) without changing "
                      "the question ID. The precise error encountered "
                      "was the following: "),
                      _("'question_data' is missing in page_data."))
                return False, error
            updated_page_data = self.update_page_data(page_context, page_data)[1]
            key_making_string_md5 = (
                updated_page_data["key_making_string_md5"])

        page_key = make_latex_page_key(key_making_string_md5)
        part_key = ("%s:%s" % (page_key, part))

        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            cache_key = None
        else:
            cache_key = part_key
            def_cache = get_latex_cache(cache)
            result = def_cache.get(cache_key)
            if result is not None:
                if part == "full":
                    assert isinstance(result, dict)
                else:
                    assert isinstance(result, six.text_type)
                if warm_up_only:
                    return True, result
                debug_print("===result is in cache===")
                return True, result

            debug_print("result is None when loading from cache")

        # cache_key is None means cache is not enabled
        result = None
        success = False

        # read from part collection
        mongo_page_part_result = get_latex_page_part_mongo_collection().find_one(
            {"key": part_key}
        )
        if mongo_page_part_result:
            part_result = mongo_page_part_result["source"].decode("utf-8")
            if part_result:
                result = mongo_page_part_result["source"].decode("utf-8")
                get_latex_page_part_mongo_collection().delete_one({"key": part_key})
            else:
                raise RuntimeError(
                    "Page part result %s null in Mongo with key %s"
                    % (part, page_key))

        if result is not None:
            debug_print("===result is find in part mongo===")
            try:
                get_latex_page_mongo_collection().update_one(
                    {"key": page_key, part: {"$exists": False}},
                    {"$setOnInsert":
                         {"key": page_key,
                          "creation_time": local_now()
                          },
                     "$set": {part: result.encode('utf-8')}},
                    upsert=True,
                )
            except DuplicateKeyError:
                pass
            success = True
        else:
            debug_print("result is None in mongo part result")
            # read from page collection
            mongo_page_result = get_latex_page_mongo_collection().find_one(
                {"key": page_key, part: {"$exists": True}}
            )
            if mongo_page_result:
                if part == "full":
                    page_result = mongo_page_result[part]
                else:
                    page_result = mongo_page_result[part].decode("utf-8")
                if page_result:
                    result = page_result
                    debug_print("===result is find in page mongo===!")
                    success = True
                else:
                    raise RuntimeError(
                        "Page result %s null in Mongo with key %s"
                        % (part, page_key))

        if result is None:
            debug_print("!!!!!! runpy !!!!!!")
            try:
                runpy_kwargs = {}
                if (not hasattr(self.page_desc, "runpy_file")
                    or
                            part != "full"):
                    runpy_kwargs["common_code_name"] = "background_code"
                success, result = self.jinja_runpy(
                    page_context,
                    page_data["question_data"],
                    "%s_process_code" % part,
                    **runpy_kwargs)
            except TypeError:
                return False, result

            if isinstance(result, six.binary_type):
                result = result.decode("utf-8")

            if success and result is not None:
                if part == "full":
                    to_set = dict(
                        (pt, result[pt].encode('utf-8'))
                        for pt in result.keys())
                    to_set.update({"full": result})
                    try:
                        get_latex_page_mongo_collection().update_one(
                            {"key": page_key, part: {"$exists": False}},
                            {"$setOnInsert":
                                 {"key": page_key,
                                  "creation_time": local_now()
                                  },
                             "$set": to_set},
                            upsert=True,
                        )
                    except DuplicateKeyError:
                        pass

                else:
                    try:
                        get_latex_page_mongo_collection().update_one(
                            {"key": page_key, part: {"$exists": False}},
                            {"$setOnInsert":
                                 {"key": page_key,
                                  "creation_time": local_now()
                                  },
                             "$set": {part: result.encode('utf-8')}},
                            upsert=True,
                        )
                    except DuplicateKeyError:
                        pass
        else:
            debug_print("===result is find in page mongo===")

        if cache_key is None:
            return success, result

        assert result

        def_cache = get_latex_cache(cache)
        if isinstance(result, dict):
            for pt, v in result.items():
                if not isinstance(v, six.text_type):
                    v = six.text_type(v)
                    part_key = "%s:%s" % (page_key, pt)
                    if (len(v) <= (
                            getattr(settings, "RELATE_CACHE_MAX_BYTES", 0))):
                        def_cache.add(part_key, v)
            part_key = "%s:%s" % (page_key, "full")
            if (len(result) <= (
                    getattr(settings, "RELATE_CACHE_MAX_BYTES", 0))):
                def_cache.add(part_key, result)
        else:
            assert isinstance(result, six.text_type), cache_key
            if (success
                and len(result) <= (
                        getattr(settings, "RELATE_CACHE_MAX_BYTES", 0))):
                if def_cache.get(cache_key) is None:
                    def_cache.delete(cache_key)
                def_cache.add(cache_key, result)
        return success, result

    def body(self, page_context, page_data):
        self.update_page_full_desc(page_context, page_data)
        if self.error_getting_updated_full_desc:
            return markup_to_html(page_context, self.error_getting_updated_full_desc)
        if self.error_updating_page_desc:
            return markup_to_html(page_context, self.error_updating_page_desc)

        if self.updated_full_desc:
            question_str = self.updated_full_desc.get("question", "")
        else:
            question_str = ""
            success = False
            question_str_tmp = ""
            answer_str = ""
            for i in range(MAX_JINJIA_RETRY):
                success, question_str_tmp = self.get_cached_result(
                        page_context, page_data, part="question")
                if success:
                    question_str = question_str_tmp
                    break

            if not success:
                if page_context.in_sandbox:
                    question_str = question_str_tmp

            if page_context.in_sandbox:
                # generate correct answer at the same time
                if hasattr(self.page_desc, "answer_process_code"):
                    for i in range(MAX_JINJIA_RETRY):
                        success, answer_str_tmp = self.get_cached_result(
                                           page_context, page_data, part="answer")
                        if success:
                            # markup_to_html(
                            #     page_context, answer_str_tmp, warm_up_only=True)
                            break

                        if page_context.in_sandbox:
                            answer_str = markup_to_html(page_context, answer_str)

        return super(LatexRandomQuestionBase, self).body(page_context, page_data)\
               + markup_to_html(page_context, question_str)

    def jinja_runpy(
            self, page_context, question_data, code_name, common_code_name=""):
        # type: (Any, Any, Text, Text) -> Tuple[bool, Any]
        # {{{ request run

        assert question_data
        run_jinja_req = {"compile_only": False}

        def transfer_attr_to(name, from_name=None):
            if from_name:
                if (from_name == "full_process_code"
                    and
                        hasattr(self.page_desc, "runpy_file")):
                    run_jinja_req[name] = (
                        "runpy_context = %s\n" % repr(self.runpy_context))
                    run_jinja_req[name] += (
                        "exec(data_files['%s'].decode('utf-8'))"
                        % self.page_desc.runpy_file)
                elif hasattr(self.page_desc, from_name):
                    run_jinja_req[name] = getattr(self.page_desc, from_name)
            else:
                assert hasattr(self.page_desc, name)
                run_jinja_req[name] = getattr(self.page_desc, name)

        run_jinja_req["user_code"] = ""

        transfer_attr_to("setup_code", from_name=code_name)
        assert run_jinja_req["setup_code"]
        if common_code_name and getattr(self.page_desc, common_code_name, ""):
            run_jinja_req["setup_code"] = (
                u"%s\n%s" % (
                    getattr(self.page_desc, common_code_name, ""),
                    run_jinja_req["setup_code"]))

        if hasattr(self.page_desc, "data_files"):
            run_jinja_req["data_files"] = {}

            for data_file in self.page_desc.data_files:
                run_jinja_req["data_files"][data_file] = \
                        b64encode(
                                get_repo_blob_data_cached(
                                    page_context.repo, data_file,
                                    page_context.commit_sha)).decode()

            run_jinja_req["data_files"]["question_data"] = question_data

        try:
            response_dict = request_python_run_with_retries(run_jinja_req,
                    run_timeout=self.docker_run_timeout)
        except:
            from traceback import format_exc
            response_dict = {
                    "result": "uncaught_error",
                    "message": "Error connecting to container",
                    "traceback": "".join(format_exc()),
                    }

        success = True
        feedback_bits = []

        if response_dict["result"] in [
                "uncaught_error",
                "setup_compile_error",
                "setup_error",
                "test_compile_error",
                "test_error"]:
            error_msg_parts = ["RESULT: %s" % response_dict["result"]]
            success = False
            for key, val in sorted(response_dict.items()):
                if (key not in ["result", "figures"]
                        and val
                        and isinstance(val, six.string_types)):
                    error_msg_parts.append(
                        "-------------------------------------")
                    error_msg_parts.append(key)
                    error_msg_parts.append(
                        "-------------------------------------")
                    error_msg_parts.append(val)
            error_msg_parts.append(
                "-------------------------------------")
            error_msg_parts.append("code")
            error_msg_parts.append(
                "-------------------------------------")
            error_msg_parts.append(run_jinja_req["setup_code"])
            error_msg_parts.append(
                "-------------------------------------")

            error_msg = "\n".join(error_msg_parts)
            if getattr(settings, "DEBUG"):
                pass
                #response_dict["stdout"] = error_msg
            #else:

            from course.page.code import is_nuisance_failure
            from django.utils import translation
            from relate.utils import local_now, format_datetime_local
            with translation.override(settings.RELATE_ADMIN_EMAIL_LOCALE):
                from django.template.loader import render_to_string
                message = render_to_string(
                    "image_upload/broken-random-latex-question-email.txt",
                    {
                        "site": getattr(settings, "RELATE_BASE_URL"),
                        "username":
                            page_context.flow_session.participation.user.username,
                        "page_id": self.page_desc.id,
                        "course": page_context.course,
                        "error_message": error_msg,
                        "review_uri": page_context.page_uri,
                        "time": format_datetime_local(local_now())
                    })

                if (not page_context.in_sandbox
                    and
                        not is_nuisance_failure(response_dict)):
                    try:
                        from django.core.mail import EmailMessage
                        msg = EmailMessage(
                            "".join(["[%(course)s] ",
                                     _("LaTex page failed in "
                                       "user %(user)s's session")])
                            % {"course": page_context.course.identifier,
                               "user":
                                   (page_context.flow_session.participation
                                    .user.username),
                               },
                            message,
                            settings.ROBOT_EMAIL_FROM,
                            [page_context.course.notify_email])

                        from relate.utils import get_outbound_mail_connection
                        msg.connection = get_outbound_mail_connection("robot")
                        if not getattr(settings, "DEBUG"):
                            msg.send()

                    except Exception:
                        from traceback import format_exc
                        feedback_bits.append(
                            six.text_type(string_concat(
                                "<p>",
                                _(
                                    "Both the code and the attempt to "
                                    "notify course staff about the issue "
                                    "failed. "
                                    "Please contact the course or site staff "
                                    "and inform them of this issue, "
                                    "mentioning this "
                                    "entire error message:"),
                                "</p>",
                                "<p>",
                                _(
                                    "Sending an email to the course staff "
                                    "about the following failure failed with "
                                    "the following error message:"),
                                "<pre>",
                                "".join(format_exc()),
                                "</pre>",
                                _("The original failure message follows:"),
                                "</p>")))

                        # }}}

        from relate.utils import dict_to_struct
        response = dict_to_struct(response_dict)

        if response.result == "success":
            pass
        elif response.result in [
                "uncaught_error",
                "setup_compile_error",
                "setup_error",
                "test_compile_error",
                "test_error"]:
            success = False
            feedback_bits.append("".join([
                "<p>",
                _(
                    "The page failed to be rendered. Sorry about that. "
                    "The staff has been informed, and "
                    "it will be fixed as soon as possible."
                ),
                "</p>"]))

            from image_upload.utils import is_course_staff_participation
            if is_course_staff_participation(
                    page_context.flow_session.participation):
                feedback_bits.append("".join([
                    "<p>",
                    _("This is the problematic code"),
                    ":"
                    "<pre>%s</pre></p>"]) % escape(run_jinja_req["setup_code"]))
                if hasattr(response, "traceback") and response.traceback:
                    feedback_bits.append("".join([
                        "<p>",
                        _("This is the exception traceback"),
                        ":"
                        "<pre>%s</pre></p>"]) % escape(response.traceback))

        elif response.result == "timeout":
            success = False
            feedback_bits.append("".join([
                "<p>",
                _(
                    "The page failed to be rendered due to timeout, "
                    "please try to reload the page in a while."
                    ),
                "</p>"])
            )
        else:
            success = False
            raise RuntimeError("invalid runpy result: %s" % response.result)

        if hasattr(response, "figures") and response.figures:
            fig_lines = ["".join(
                ["<p>",
                 _("Your code produced the following plots"),
                 ":</p>"]),
                '<dl class="result-figure-list">',
            ]

            for nr, mime_type, b64data in response.figures:
                fig_lines.extend(
                    ["".join(
                        ["<dt>", _("Figure"), "%d<dt>"]) % nr,
                     '<dd>'
                     '<img alt="Figure %d" src="data:%s;base64,%s">'
                     '</dd>'
                     % (nr, mime_type, b64data)])

            fig_lines.append("</dl>")

        if success:
            # > 1 because there will be execution time
            if (code_name == "full_process_code"
                and
                    hasattr(response, "feedback")
                and
                        len(response.feedback) > 1):

                try:
                    import json
                    result_dict = json.loads(response.feedback[0])
                except:
                    raise

                assert result_dict
                return success, result_dict

            elif hasattr(response, "stdout") and response.stdout:
                return success, response.stdout
        else:
            return (success,
                    '<div class="latexpage-error alert alert-danger">%s'
                    '</div>' % "\n".join(feedback_bits))

        # }}}

    def correct_answer(self, page_context, page_data, answer_data, grade_data):
        if self.error_getting_updated_full_desc:
            return markup_to_html(page_context, self.error_getting_updated_full_desc)

        CA_PATTERN = string_concat(_("A correct answer is"), ": %s.")  # noqa
        answer_str = ""
        if self.updated_full_desc:
            answer_str = self.updated_full_desc.get("answer", "")
        elif hasattr(self.page_desc, "answer_process_code"):
            answer_str = ""
            for i in range(MAX_JINJIA_RETRY):
                success, answer_str_tmp = self.get_cached_result(
                                   page_context, page_data, part="answer")
                if success:
                    answer_str = answer_str_tmp
                    break

        super_correct_answer = super(LatexRandomQuestionBase, self)\
                .correct_answer(page_context, page_data, answer_data, grade_data)
        if super_correct_answer:
            return super_correct_answer + markup_to_html(page_context, answer_str)
        else:
            return CA_PATTERN % markup_to_html(page_context, answer_str)


class LatexRandomQuestion(LatexRandomQuestionBase):
    pass


class LatexRandomImageUploadQuestion(LatexRandomQuestion, ImageUploadQuestion):
    pass


class LatexRandomCodeQuestion(LatexRandomQuestion, PythonCodeQuestion):
    pass


class LatexRandomCodeTextQuestion(LatexRandomQuestion, TextQuestion):
    pass


class LatexRandomCodeInlineMultiQuestion(LatexRandomQuestion, InlineMultiQuestion):
    need_update_page_desc = True

    @property
    def required_attrs_if_runpy_or_full_code_missing(self):
        return (
            super(LatexRandomCodeInlineMultiQuestion, self)
            .required_attrs_if_runpy_or_full_code_missing
            + ["blank_process_code", "blank_answer_process_code"])

    def update_page_desc(self, page_context, page_data):
        self.update_page_full_desc(page_context, page_data)
        if self.error_getting_updated_full_desc:
            return

        from course.page.inline import WRAPPED_NAME_RE, NAME_RE

        blank_str = ""
        blank_answers_str = ""
        answer_explanation_str = ""

        if self.updated_full_desc:
            blank_str = self.updated_full_desc.get("blank")
            blank_answers_str = self.updated_full_desc.get("blank_answer")
            answer_explanation_str = self.updated_full_desc.get("answer_explanation")
        else:
            success = False
            for i in range(MAX_JINJIA_RETRY):
                success, blank_str_tmp = self.get_cached_result(
                    page_context, page_data, part="blank")
                if success:
                    blank_str = blank_str_tmp
                    break

            if not success:
                raise RuntimeError(blank_str_tmp)

            success = False
            for i in range(MAX_JINJIA_RETRY):
                success, blank_answer_str_tmp = self.get_cached_result(
                    page_context, page_data, part="blank_answer")
                if success:
                    blank_answers_str = blank_answer_str_tmp
                    break

            if not success:
                raise RuntimeError(blank_answer_str_tmp)

            if hasattr(self.page_desc, "answer_explanation_process_code"):
                success = False
                answer_explanation_str = ""
                for i in range(MAX_JINJIA_RETRY):
                    success, answer_explanation_tmp = self.get_cached_result(
                        page_context, page_data, part="answer_explanation")
                    if success:
                        answer_explanation_str = answer_explanation_tmp
                        break

                if not success:
                    raise RuntimeError(answer_explanation_tmp)

        if answer_explanation_str:
            self.page_desc.answer_explanation = answer_explanation_str

        if not self.error_getting_updated_full_desc:
            try:
                question = markup_to_html(page_context, blank_str)
                from relate.utils import dict_to_struct
                import yaml
                answers = dict_to_struct(yaml.load(blank_answers_str))
                self.page_desc.question = question
                self.page_desc.answers = answers
                self.embedded_wrapped_name_list = WRAPPED_NAME_RE.findall(
                        self.page_desc.question)
                self.embedded_name_list = NAME_RE.findall(self.page_desc.question)
                answer_instance_list = []

                for idx, name in enumerate(self.embedded_name_list):
                    answers_desc = getattr(self.page_desc.answers, name)

                    from course.page.inline import parse_question
                    from course.validation import ValidationContext
                    vctx = ValidationContext(
                        repo=page_context.repo,
                        commit_sha=page_context.commit_sha)

                    parsed_answer = parse_question(
                            vctx, "<runpy error>", name, answers_desc)
                    answer_instance_list.append(parsed_answer)

                self.answer_instance_list = answer_instance_list
            except Exception as e:
                from yaml.scanner import ScannerError
                if isinstance(e, ScannerError):
                    from traceback import format_exc
                    self.error_updating_page_desc = string_concat(
                        "<p class='latexpage-error alert alert-danger'><strong>",
                        _("Error: "),
                        _("The template failed to render, the log follows:"),
                        "</strong></p>",
                        "<div class='latexpage-error alert alert-danger'>"
                        "<pre>%s</pre></div>"
                        % (
                            "".join(format_exc())))
                else:
                    raise

    def get_question(self, page_context, page_data):
        # template error is supposed to be raised here
        self.update_page_full_desc(page_context, page_data)
        self.update_page_desc(page_context, page_data)
        return super(LatexRandomCodeInlineMultiQuestion, self) \
            .get_question(page_context, page_data)

    def allowed_attrs(self):
        return super(LatexRandomCodeInlineMultiQuestion, self).allowed_attrs() + (
            ("blank_process_code", str),
            ("blank_answer_process_code", str)
        )

    def grade(self, page_context, page_data, answer_data, grade_data):
        self.update_page_full_desc(page_context, page_data)
        self.update_page_desc(page_context, page_data)
        return super(LatexRandomCodeInlineMultiQuestion, self).grade(
            page_context, page_data, answer_data, grade_data)


class LatexRandomCodeQuestionWithHumanTextFeedback(
        LatexRandomQuestion,
        PythonCodeQuestionWithHumanTextFeedback):
    pass


class LatexRandomMultipleChoiceQuestion(LatexRandomQuestion, MultipleChoiceQuestion):

    def initialize_page_data(self, page_context):
        # type: (PageContext) -> Dict
        page_data = {}  # type: Dict
        m_page_data = MultipleChoiceQuestion.initialize_page_data(self, page_context)
        l_page_data = LatexRandomQuestion.initialize_page_data(self, page_context)
        page_data.update(m_page_data)
        page_data.update(l_page_data)
        return page_data


class LatexRandomChoiceQuestion(LatexRandomQuestion, ChoiceQuestion):

    def initialize_page_data(self, page_context):
        page_data = {}
        m_page_data = ChoiceQuestion.initialize_page_data(self, page_context)
        l_page_data = LatexRandomQuestion.initialize_page_data(self, page_context)
        page_data.update(m_page_data)
        page_data.update(l_page_data)
        return page_data
