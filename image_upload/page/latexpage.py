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

import os
import six
from copy import deepcopy
from io import BytesIO
import pickle
from hashlib import md5
from base64 import b64encode, b64decode
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from bson.errors import InvalidId
from traceback import format_exc

from plugins.latex.utils import get_latex_cache

# {{{ mypy
if False:
    from typing import Text, Any, Dict, Tuple, Union, Optional, List  # noqa
    from course.utils import PageContext  # noqa
    from pymongo import MongoClient  # noqa
    from pymongo.collection import Collection  # noqa
    from course.validation import ValidationContext  # noqa
# }}}


from django.utils.translation import ugettext as _, string_concat
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.conf import settings
from django.utils.html import escape

from relate.utils import local_now, Struct, struct_to_dict

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
from image_upload.utils import deep_eq, deep_convert_ordereddict, deep_np_to_string


def _debug_print(s):
    # type: (Text) -> None
    # debugging switch
    debug = False

    settings_debug = getattr(settings, "DEBUG", False)
    debug = debug or settings_debug

    if debug:
        print(s)


debug_print = _debug_print


CACHE_VERSION = "V0"
DB = get_mongo_db()


def make_latex_page_key(key_making_string_md5):
    # type: (Text) -> Text
    return ("latexpage:%s:%s"
            % (CACHE_VERSION,
               key_making_string_md5))


def get_key_making_string_md5_hash(template_hash, question_data):
    # type: (Text, Text) -> Text
    assert question_data is not None
    key_making_string = template_hash
    key_making_string += b64_pickled_bytes_to_data_string(question_data)
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


def b64_pickled_bytes_to_data(b64_string):
    # type: (Text) -> Any
    bio = BytesIO(b64decode(b64_string.encode()))
    data = pickle.load(bio, encoding="latin-1")
    try:
        import json
        data = json.loads(data)
    except:
        pass
    return data


def b64_pickled_bytes_to_data_string(p):
    # type: (Text) -> Text
    data = b64_pickled_bytes_to_data(p)
    data = deep_convert_ordereddict(data)

    # because the data might contains Numpy ndarray
    return str(deep_np_to_string(data))


def question_data_equal(data1, data2):
    # type: (Text, Text) -> bool
    if data1 == data2:
        return True
    else:
        data1_decode = b64_pickled_bytes_to_data(data1)
        data2_decode = b64_pickled_bytes_to_data(data2)
        return deep_eq(data1_decode, data2_decode)


class LatexRandomQuestionBase(PageBaseWithTitle, PageBaseWithValue,
                          PageBaseWithCorrectAnswer):
    grading_sort_by_page_data = True

    @property
    def required_attrs_if_runpy_or_full_code_missing(self):
        # if runpy_file or full_process_code is missing, the following
        # attributes must present in page_desc
        return []

    def __init__(self, vctx, location, page_desc):
        # type: (Optional[ValidationContext], Optional[Text], Struct) -> None
        super(LatexRandomQuestionBase, self).__init__(vctx, location, page_desc)

        if vctx is not None and hasattr(page_desc, "data_files"):
            # {{{ validate random_question_data_file
            if page_desc.random_question_data_file not in page_desc.data_files:  # type: ignore  # noqa
                raise ValidationError(
                    string_concat(
                        "%s: " % location,
                        _("'%s' should be listed in 'data_files'")
                        % page_desc.random_question_data_file))  # type: ignore

            repo_bytes_data = get_repo_blob_data_cached(
                vctx.repo,
                page_desc.random_question_data_file,  # type: ignore
                vctx.commit_sha)
            bio = BytesIO(repo_bytes_data)
            try:
                # py3
                repo_data_loaded = pickle.load(bio, encoding="latin-1")
            except TypeError:
                # py2
                repo_data_loaded = pickle.load(bio)
            except Exception as e:
                if isinstance(e, ValueError):
                    if six.PY2 and "unsupported pickle protocol: 3" in str(e):
                        raise ValidationError(
                            string_concat(
                                "%s: " % location,
                                _("'%s' was pickle dumped using protocol 3 "
                                  "(under python3), it should be dumped with "
                                  "'protocol=2' parameters")
                                % page_desc.random_question_data_file))  # type: ignore  # noqa
                raise ValidationError(
                    "%s: %s: %s" % (location, type(e).__name__, str(e)))
            if not isinstance(repo_data_loaded, (list, tuple)):
                raise ValidationError(
                    string_concat(
                        "%s: " % location,
                        _("'%s' must be dumped from a list or tuple")
                        % page_desc.random_question_data_file))  # type: ignore
            n_data = len(repo_data_loaded)
            if n_data == 0:
                raise ValidationError(
                    string_concat(
                        "%s: " % location,
                        _("'%s' seems to be empty, that's not valid")
                        % page_desc.random_question_data_file))  # type: ignore
            # }}}

            if hasattr(page_desc, "cache_key_files"):
                for cf in page_desc.cache_key_files:  # type: ignore
                    if cf not in page_desc.data_files:  # type: ignore
                        raise ValidationError(
                            string_concat(
                                location,
                                ": ",
                                _("'%s' should be listed in 'data_files'")
                                % cf))
                    if (page_desc.random_question_data_file  # type: ignore
                            in page_desc.cache_key_files):  # type: ignore
                        vctx.add_warning(
                            location,
                            _("'%s' is not expected in "
                              "'cache_key_files' as it will not "
                              "be used for building cache")
                            % page_desc.random_question_data_file)  # type: ignore

            if hasattr(page_desc, "excluded_cache_key_files"):
                for cf in page_desc.excluded_cache_key_files:  # type: ignore
                    if cf not in page_desc.data_files:  # type: ignore
                        vctx.add_warning(location, "'%s' is not in 'data_files'"
                                              % cf)

            for data_file in page_desc.data_files:  # type: ignore
                try:
                    if not isinstance(data_file, str):
                        # This seems never happened
                        raise ObjectDoesNotExist()

                    get_repo_blob(vctx.repo, data_file, vctx.commit_sha)
                except ObjectDoesNotExist:
                    raise ValidationError("%s: data file '%s' not found"
                            % (location, data_file))

            if not hasattr(page_desc, "runpy_file"):
                if not hasattr(page_desc, "full_process_code"):
                    if hasattr(page_desc, "runpy_context"):
                        vctx.add_warning(
                            location,
                            _("'runpy_context' is configured with neither "
                              "'runpy_file' nor 'full_process_code' configured "
                              "it will be neglected.")
                        )

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
                                _("'%s' must be configured when neither "
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
                if page_desc.runpy_file not in page_desc.data_files:  # type: ignore
                    raise ValidationError(
                        string_concat(
                            "%s: " % location,
                            _("'%s' should be listed in 'data_files'")
                            % page_desc.runpy_file))  # type: ignore

                try:
                    runpy_file = get_repo_blob_data_cached(
                        vctx.repo, page_desc.runpy_file,  # type: ignore
                        vctx.commit_sha)
                    compile(runpy_file, '<runpy file>', 'exec')
                    del runpy_file
                except SyntaxError:
                    raise ValidationError(
                        string_concat("%s: " % location,
                                      _("'%s' is not a valid Python script file.")
                                      % page_desc.runpy_file))  # type: ignore

            if hasattr(page_desc, "cache_key_attrs"):  # type: ignore
                for attr in page_desc.cache_key_attrs:  # type: ignore
                    if not hasattr(page_desc, attr):
                        raise ValidationError("%s: attribute '%s' not found"
                                              % (location, attr))

        self.original_page_desc_prompt = getattr(page_desc, "prompt", "")
        self.docker_run_timeout = getattr(page_desc, "docker_timeout", 5)

        # These files/attrs are used to generate rendered body and correct answer

        self.cache_key_files = self.initialize_cache_key_file_attrs(page_desc)  # type: ignore  # noqa
        self.cache_key_attrs = self.initialize_cache_key_attrs(page_desc)

        self.runpy_context = {}  # type: Dict
        if (hasattr(page_desc, "runpy_file")
                or hasattr(page_desc, "full_process_code")):
            if getattr(page_desc, "runpy_context", None):
                self.runpy_context = struct_to_dict(page_desc.runpy_context)  # type: ignore  # noqa

        self.will_receive_grade = getattr(page_desc, "will_receive_grade", True)
        self.is_page_desc_updated = False
        self.error_updating_page_desc = None
        self.is_warming_up = False

    def initialize_cache_key_file_attrs(self, page_desc):
        # type: (Struct) -> List
        # generate file lists that will be used to make cache key
        cache_key_files_set = set(getattr(
            page_desc, "cache_key_files", getattr(page_desc, "data_files")))
        excluded_cache_key_file_set = set(getattr(
            page_desc, "excluded_cache_key_files", []))

        # Exclude question data file for building cache
        excluded_cache_key_file_set.update([page_desc.random_question_data_file])  # type: ignore  # noqa
        cache_key_files_set.difference_update(excluded_cache_key_file_set)

        # In case order changed across repo and across runs
        return sorted(list(cache_key_files_set))

    def initialize_cache_key_attrs(self, page_desc):
        # type: (Struct) -> List
        # generate attribute list that will be used to make cache key
        cache_key_attrs = getattr(page_desc, "cache_key_attrs", [])

        if not cache_key_attrs:
            all_process_attributes = [
                attr for attr in dir(self.page_desc)
                if attr.endswith("_process_code")]
            all_process_attributes.append("background_code")
            for attr in all_process_attributes:
                if hasattr(page_desc, attr):
                    cache_key_attrs.append(attr)

        # sorted because python dict is not ordered, and update_page_desc can
        # result in different result across runs
        return sorted(cache_key_attrs)

    def get_updated_page_desc(self, page_context, new_page_desc_dict):
        # type: (PageContext, Dict) -> Struct
        if self.is_page_desc_updated:
            return self.page_desc

        page_desc_dict = struct_to_dict(self.page_desc)
        new_page_desc_dict["prompt"] = (
            self.original_page_desc_prompt + "\n" + new_page_desc_dict["prompt"])
        page_desc_dict.update(new_page_desc_dict)

        from relate.utils import dict_to_struct
        return dict_to_struct(page_desc_dict)

    def update_page_desc(self, page_context, page_data):
        # type: (PageContext, Dict) -> None
        if self.is_page_desc_updated:
            return
        if self.error_updating_page_desc is not None:
            return

        success, result = self.get_updated_page_desc_dict_cached(
            page_context, page_data)

        if success:
            assert isinstance(result, dict)
            new_desc = self.get_updated_page_desc(page_context,
                                                  new_page_desc_dict=result)

            super(LatexRandomQuestionBase, self).__init__(None, None, new_desc)
            self.is_page_desc_updated = True
        else:
            assert result is not None
            assert not self.is_page_desc_updated
            self.error_updating_page_desc = string_concat(
                "<p class='latexpage-error alert alert-danger'>",
                _("Error: "),
                _(
                    "The page failed to be rendered. Sorry about that. "
                    "The staff has been informed, and "
                    "it will be fixed as soon as possible."
                ),
                "</p>",
                "<div class='latexpage-error alert alert-danger'>"
                "<pre>%s</pre></div>"
                % result)

    def make_form(
            self,
            page_context,  # type: PageContext
            page_data,  # type: Any
            answer_data,  # type: Any
            page_behavior,  # type: Any
            ):

        self.update_page_desc(page_context, page_data)

        if self.error_updating_page_desc:
            return None

        return super(LatexRandomQuestionBase, self).make_form(
            page_context, page_data, answer_data, page_behavior
        )

    def required_attrs(self):
        return super(LatexRandomQuestionBase, self).required_attrs() + (
            ("data_files", (list, str)),
            ("random_question_data_file", str),
        )

    def allowed_runpy_attrs(self):
        runpy_attrs = [
            ("background_code", str),
            ('runpy_file', str),
            ('runpy_context', Struct),
            ("full_process_code", str),
            ("docker_timeout", (int, float)),
            ("excluded_cache_key_files", list),
            ("cache_key_files", list),
            ("cache_key_attrs", list),
            ("warm_up_by_sandbox", bool),
        ]
        for attr in (super(LatexRandomQuestionBase, self).allowed_attrs()
                         + super(LatexRandomQuestionBase, self).required_attrs()):
            if attr[0] not in ["type", "access_rules", "value", "title",
                            "widget", "id", "is_optional_page"]:
                runpy_attrs.append(("%s_process_code" % attr[0], str))
        return runpy_attrs

    def allowed_attrs(self):
        return (
            super(LatexRandomQuestionBase, self).allowed_attrs()
            + tuple(self.allowed_runpy_attrs()))

    def is_answer_gradable(self):
        return self.will_receive_grade

    def generate_new_page_data(self, page_context, question_data):
        # type: (PageContext, Text) -> Dict[Text, Text]
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
            "key_making_string_md5": new_key_making_string_md5,
            "question_data": question_data
        }

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
            new_page_data = self.generate_new_page_data(page_context, question_data)
            assert question_data_equal(
                new_page_data["question_data"], question_data)
            return True, new_page_data

        try:
            exist_entry = (
                get_latex_page_commitsha_template_pair_collection().find_one(
                    {"_id": ObjectId(template_hash_id)}))
        except InvalidId:
            exist_entry = None

        # mongo data is broken
        if not exist_entry:
            new_page_data = self.generate_new_page_data(page_context, question_data)
            assert question_data_equal(
                new_page_data["question_data"], question_data)
            return True, new_page_data

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
                    # This happen only when manually changed the template_hash field
                    # in the mongo entry or manually changed page_data
                    new_page_data = self.generate_new_page_data(page_context,
                                                                question_data)
                    assert question_data_equal(new_page_data["question_data"],
                                               question_data)

                    manually_changed_page_data = False
                    for k in ["template_hash_id", "template_hash"]:
                        if page_data[k] != new_page_data[k]:
                            manually_changed_page_data = True

                    manually_changed_mongo_template_hash = False
                    if new_page_data["template_hash"] != match_template_hash:
                        manually_changed_mongo_template_hash = True

                    if manually_changed_mongo_template_hash:
                        get_latex_page_commitsha_template_pair_collection().update_one(
                            {"_id": ObjectId(template_hash_id)},
                            {"$set": {
                                commit_sha:
                                    new_page_data["template_hash"]}}
                        )

                    if manually_changed_page_data:
                        assert question_data_equal(new_page_data["question_data"],
                                                   question_data)
                        return True, new_page_data

                if new_page_data["question_data"] != question_data:
                    assert question_data_equal(
                        new_page_data["question_data"], question_data)
                    return True, new_page_data

                return False, {}

            if match_template_hash_redirect_id:
                target_entry = (
                    get_latex_page_commitsha_template_pair_collection().find_one(
                        {"_id": ObjectId(match_template_hash_redirect_id)}))

                # in case the entry is broken
                if not target_entry:
                    new_page_data = (
                        self.generate_new_page_data(page_context, question_data))

                    # the entry is broken, so we need to update where the source
                    # who told us to redirect here
                    get_latex_page_commitsha_template_pair_collection().update_one(
                        {"_id": ObjectId(template_hash_id),
                        "%s_next" % commit_sha: {"$exists": True}},
                        {"$set": {"%s_next" % commit_sha:
                                      new_page_data["template_hash_id"]}}
                    )
                    assert question_data_equal(new_page_data["question_data"],
                                               question_data)
                    return True, new_page_data

                # the redirect entry exists
                else:
                    new_template_hash = target_entry.get(commit_sha, None)
                    if new_template_hash:
                        if new_template_hash == template_hash:
                            # will this happen?
                            return False, {}

                        new_key_making_string_md5 = (
                            get_key_making_string_md5_hash(
                                new_template_hash, question_data))
                        return True, {
                            "template_hash": new_template_hash,
                            "template_hash_id": match_template_hash_redirect_id,
                            "key_making_string_md5": new_key_making_string_md5,
                            "question_data": question_data
                        }
                    else:
                        # new_template_hash is empty, remove the redirect
                        get_latex_page_commitsha_template_pair_collection().update_one(
                            {"_id": ObjectId(template_hash_id)},
                            {"$unset": {"%s_next" % commit_sha: ""}}
                        )
                        match_template_hash_redirect_id = None

            assert not (match_template_hash or match_template_hash_redirect_id)
            # Neither match_template_hash nor match_template_hash_redirect_id

            new_page_data = self.generate_new_page_data(page_context, question_data)
            if new_page_data["template_hash"] == template_hash:
                get_latex_page_commitsha_template_pair_collection().update_one(
                    {"_id": ObjectId(template_hash_id),
                     commit_sha: {"$exists": False}},
                    {"$set": {commit_sha: template_hash}}
                )
                if new_page_data["question_data"] != question_data:
                    assert question_data_equal(
                        new_page_data["question_data"], question_data)
                    return True, new_page_data
                return False, {}
            else:
                get_latex_page_commitsha_template_pair_collection().update_one(
                    {"_id": ObjectId(template_hash_id),
                     commit_sha: {"$exists": False}},
                    {"$set": {"%s_next" % commit_sha:
                                  new_page_data["template_hash_id"]}}
                )
                assert question_data_equal(new_page_data["question_data"],
                                           question_data)
                return True, new_page_data

    def generate_template_hash(self, page_context):
        # type: (PageContext) -> Text
        from image_upload.utils import (
            minify_python_script, strip_template_comments)
        template_string = ""
        if self.cache_key_files:
            for cfile in sorted(self.cache_key_files):
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
            for cattr in sorted(self.cache_key_attrs):
                cattr_string = repr(getattr(self.page_desc, cattr)).strip()
                if (cattr.endswith("_code")
                    and
                        # this is to avoid imported jinja macro in the attribute
                        not cattr_string.startswith("{")):
                    cattr_string = getattr(self.page_desc, cattr)
                    cattr_string = minify_python_script(cattr_string)
                template_string += cattr_string

        if self.runpy_context:
            # runpy_context is a dict, convert to OrderedDict
            sorted_runpy_context_str = repr(sorted(
                list((k, self.runpy_context[k]) for k in self.runpy_context.keys()),
                key=lambda x: x[0]))
            template_string += sorted_runpy_context_str

        return md5(template_string.encode("utf-8")).hexdigest()

    def initialize_page_data(self, page_context):
        # type: (PageContext) -> Dict
        commit_sha = page_context.commit_sha.decode()
        warm_up_by_sandbox = False
        if page_context.in_sandbox:
            warm_up_by_sandbox = getattr(
                self.page_desc, "warm_up_by_sandbox", True)

        # get random question_data
        repo_bytes_data = get_repo_blob_data_cached(
            page_context.repo,
            self.page_desc.random_question_data_file,  # type: ignore
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
            if isinstance(random_data, dict):
                random_data = deep_convert_ordereddict(random_data)

            selected_data_bytes = BytesIO()
            pickle.dump(random_data, selected_data_bytes)
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

            # try to do markup_to_html in warmup
            self.is_page_desc_updated = False
            self.is_warming_up = True

            self.update_page_desc(page_context, page_data)

            self.body(page_context, page_data)  # type: ignore
            self.correct_answer(page_context, page_data,  # type: ignore
                                answer_data=None, grade_data=None)

        self.is_warming_up = False
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

    def validate_updated_page_desc(self, page_context, new_desc_dict):
        new_desc_dict_copy = deepcopy(new_desc_dict)
        new_desc = self.get_updated_page_desc(page_context,
                                              new_page_desc_dict=new_desc_dict_copy)

        from course.validation import ValidationContext
        vctx = ValidationContext(
            repo=page_context.repo,
            commit_sha=page_context.commit_sha)
        super(LatexRandomQuestionBase, self).__init__(vctx, None, new_desc)
        return new_desc

    def get_updated_page_desc_dict_cached(self, page_context, page_data):
        # type: (PageContext, Dict) -> Tuple[bool, Union[Dict, Text]]

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

        try:
            import django.core.cache as cache
        except ImproperlyConfigured:
            cache_key = None
        else:
            cache_key = page_key
            def_cache = get_latex_cache(cache)
            if not self.is_warming_up:
                result = def_cache.get(cache_key)
                if result is not None:
                    assert isinstance(result, dict)
                    debug_print("===result is in cache===")
                    return True, result

                debug_print("result is None when loading from cache")

        # cache_key is None means cache is not enabled
        result = None
        success = False

        # read from page collection
        mongo_page_result = get_latex_page_mongo_collection().find_one(
            {"key": page_key}
        )
        if mongo_page_result:
            result = mongo_page_result["content"]
            assert result is not None
            debug_print("===result is found in page mongo===!")
            success = True

        from image_upload.utils import is_course_staff_participation

        if result is None:
            debug_print("!!!!!! runpy !!!!!!")
            try:
                runpy_kwargs = {}

                all_process_attribute_parts = [
                    attr.replace("_process_code", "")
                    for attr in dir(self.page_desc)
                    if attr.endswith("_process_code")]

                if ("full" in all_process_attribute_parts
                        or hasattr(self.page_desc, "runpy_file")):
                    all_process_attribute_parts = ["full"]
                else:
                    runpy_kwargs["common_code_name"] = "background_code"

                assert all_process_attribute_parts

                new_page_desc_dict = {}  # type: Dict
                for part in all_process_attribute_parts:
                    success, result = self.jinja_runpy(
                        page_context,
                        page_data["question_data"],
                        "%s_process_code" % part,
                        **runpy_kwargs)
                    if success:
                        assert result is not None
                        if isinstance(result, dict):
                            for k in result.keys():
                                # this should result from the full part
                                if isinstance(result[k], six.binary_type):
                                    result[k] = result[k].decode("utf-8")
                            new_page_desc_dict = result
                        else:
                            if isinstance(result, six.binary_type):
                                result = result.decode("utf-8")
                            new_page_desc_dict[part] = result
                    else:
                        if isinstance(result, six.binary_type):
                            result = result.decode("utf-8")
                        assert isinstance(result, six.text_type)
                        raise RuntimeError(result)
                result = new_page_desc_dict
            except Exception as e:
                if page_context.in_sandbox or is_course_staff_participation(
                        page_context.flow_session.participation):
                    error_msg = "".join(format_exc())
                else:
                    error_msg = "%s: %s" % (type(e).__name__, str(e))

                if not error_msg.strip():
                    error_msg = _("Failed for unkown reason.")

                return False, error_msg

        assert result is not None
        assert success

        # {{{ save in mongodb
        if not mongo_page_result:
            # make sure the result is not re-inserted if there already exists
            # an entry

            try:
                self.validate_updated_page_desc(page_context, result)
                self.is_page_desc_updated = True
            except Exception as e:
                error_msg = ""
                extra_error_msg = (
                    "<div class='latexpage-error alert alert-danger'>"
                    "<pre>%s</pre></div>"
                    % "".join(format_exc()))

                if page_context.in_sandbox or is_course_staff_participation(
                        page_context.flow_session.participation):
                    error_msg += extra_error_msg

                self.error_updating_page_desc = error_msg

                message = self.get_error_notification_email_messages(
                    page_context, extra_error_msg)
                self.send_error_notification_email(page_context, message)
                return False, self.error_updating_page_desc

            assert success

            try:
                get_latex_page_mongo_collection().update_one(
                    {"key": page_key, "content": {"$exists": False}},
                    {"$setOnInsert":
                         {"key": page_key,
                          "creation_time": local_now()
                          },
                     "$set": {"content": result}},
                    upsert=True,
                )
            except DuplicateKeyError:
                pass

        # }}}

        # {{{ cache the result
        if cache_key is None or self.is_warming_up:
            return success, result

        assert result is not None

        def_cache = get_latex_cache(cache)
        assert isinstance(result, dict)
        import sys
        if (sys.getsizeof(result)
                <= (getattr(settings, "RELATE_CACHE_MAX_BYTES", 0))):
            if not def_cache.get(page_key):
                def_cache.add(page_key, result)
        # }}}

        return success, result

    def body(self, page_context, page_data):
        self.update_page_desc(page_context, page_data)
        if self.error_updating_page_desc:
            return self.error_updating_page_desc
        return super(LatexRandomQuestionBase, self).body(page_context, page_data)

    def send_error_notification_email(self, page_context, message):
        # type: (PageContext, Text) -> None
        if not (getattr(settings, "DEBUG") or not page_context.in_sandbox):
            return
        from django.core.mail import EmailMessage
        from course.utils import LanguageOverride
        with LanguageOverride(page_context.course):
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
            msg.send()

    def get_error_notification_email_messages(self, page_context, error_msg):
        # type: (PageContext, Text) -> Text
        from relate.utils import local_now, format_datetime_local
        from course.utils import LanguageOverride
        with LanguageOverride(page_context.course):
            from relate.utils import render_email_template
            message = render_email_template(
                "image_upload/broken-random-latex-question-email.txt",
                {
                    "site": getattr(settings, "RELATE_BASE_URL"),
                    "username":
                        page_context.flow_session.participation.user.username,
                    "page_id": self.page_desc.id,  # type: ignore
                    "course": page_context.course,
                    "error_message": error_msg,
                    "review_uri": page_context.page_uri,
                    "time": format_datetime_local(local_now())
                })
            return message

    def get_run_jinja_req(self, page_context, question_data, code_name, **kwargs):
        # type: (PageContext, Any, Text, **Any) -> Dict

        assert question_data
        run_jinja_req = {"compile_only": False}

        def transfer_attr_to(name, from_name=None):
            # type: (Text, Optional[Text]) -> None
            if from_name:
                if (from_name == "full_process_code"
                    and
                        hasattr(self.page_desc, "runpy_file")):
                    run_jinja_req[name] = (  # type: ignore
                        "runpy_context = %s\n" % repr(self.runpy_context))
                    run_jinja_req[name] += (  # type: ignore
                        "exec(data_files['%s'].decode('utf-8'))"
                        % self.page_desc.runpy_file)  # type: ignore
                elif hasattr(self.page_desc, from_name):
                    run_jinja_req[name] = getattr(self.page_desc, from_name)
            else:
                assert hasattr(self.page_desc, name)
                run_jinja_req[name] = getattr(self.page_desc, name)

        run_jinja_req["user_code"] = ""  # type: ignore
        transfer_attr_to("setup_code", from_name=code_name)
        assert run_jinja_req["setup_code"]

        common_code_name = kwargs.pop("common_code_name", None)
        common_code = None

        if common_code_name is not None:
            common_code = getattr(self.page_desc, common_code_name, "")

        if common_code is not None:
            run_jinja_req["setup_code"] = (  # type: ignore
                u"%s\n%s" % (common_code, run_jinja_req["setup_code"]))

        run_jinja_req["data_files"] = {}  # type: ignore

        for data_file in self.page_desc.data_files:  # type: ignore
            if data_file != self.page_desc.random_question_data_file:  # type: ignore  # noqa
                run_jinja_req["data_files"][data_file] = (  # type: ignore
                    b64encode(
                        get_repo_blob_data_cached(
                            page_context.repo, data_file,
                            page_context.commit_sha)).decode())

        run_jinja_req["data_files"]["question_data"] = question_data  # type: ignore  # noqa
        return run_jinja_req

    def jinja_runpy(
            self, page_context, question_data, code_name, **kwargs):
        # type: (Any, Any, Text, **Any) -> Tuple[bool, Any]
        # {{{ request run

        # print("------------------runpy--------------------")

        run_jinja_req = self.get_run_jinja_req(page_context, question_data,
                                               code_name, **kwargs)

        try:
            response_dict = request_python_run_with_retries(
                run_jinja_req,
                run_timeout=self.docker_run_timeout,
                spawn_containers_for_runpy=not bool(six.PY3))
        except:
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

            from course.page.code import is_nuisance_failure

            if (not page_context.in_sandbox
                and
                    not is_nuisance_failure(response_dict)):  # type: ignore

                message = self.get_error_notification_email_messages(page_context,
                                                                     error_msg)

                try:
                    self.send_error_notification_email(page_context, message)

                except Exception:
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

        if response.result == "success":  # type:ignore
            # > 1 because there will be execution time
            if (code_name == "full_process_code"
                and
                    hasattr(response, "feedback")
                and
                        len(response.feedback) > 1):  # type:ignore

                try:
                    import json
                    result_dict = json.loads(response.feedback[0])  # type:ignore
                except Exception as e:
                    error_msg = "".join(format_exc())
                    response.result = "uncaught_error"  # type:ignore
                    response.traceback = error_msg  # type:ignore
                else:
                    assert result_dict
                    return True, result_dict

            elif hasattr(response, "stdout") and response.stdout:  # type:ignore
                return True, response.stdout  # type:ignore
            else:
                response.result = "uncaught_error"  # type:ignore
                response.traceback = (  # type:ignore
                    _("'%s' expects output, while got None") % code_name)

        if response.result in [  # type:ignore
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
                if hasattr(response, "traceback") and response.traceback:  # type:ignore  # noqa
                    feedback_bits.append("".join([
                        "<p>",
                        _("This is the exception traceback"),
                        ":"
                        "<pre>%s</pre></p>"]) % escape(response.traceback))  # type:ignore  # noqa

        elif response.result == "timeout":  # type:ignore
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
            error_msg = repr(response.result)  # type:ignore
            feedback_bits.append("".join([
                "<p>",
                error_msg,
                "</p>"])
            )
            message = self.get_error_notification_email_messages(page_context,
                                                                 error_msg)
            self.send_error_notification_email(page_context, message)

        return (success,
                '<div class="latexpage-error alert alert-danger">%s'
                '</div>' % "\n".join(feedback_bits))

        # }}}

    def normalized_bytes_answer(
            self,
            page_context,  # type: PageContext
            page_data,  # type: Any
            answer_data,  # type: Any
            ):
        if answer_data is None:
            return None

        self.update_page_desc(page_context, page_data)
        question = self.analytic_view_body(page_context, page_data)
        extension, bytes_answer = (
            super(LatexRandomQuestionBase, self). normalized_bytes_answer(
                page_context, page_data, answer_data))

        from six import BytesIO
        from zipfile import ZipFile
        bio = BytesIO()
        with ZipFile(bio, "w") as question_answer_zip:
            question_answer_zip.writestr(
                "question.html", question)
            question_answer_zip.writestr(
                "answers" + extension,
                bytes_answer)

        return (".zip", bio.getvalue())


class LatexRandomQuestion(LatexRandomQuestionBase):
    pass


class LatexRandomImageUploadQuestion(LatexRandomQuestion, ImageUploadQuestion):
    pass


class LatexRandomCodeQuestion(LatexRandomQuestion, PythonCodeQuestion):
    pass


class LatexRandomCodeTextQuestion(LatexRandomQuestion, TextQuestion):
    pass


class LatexRandomCodeInlineMultiQuestion(LatexRandomQuestion, InlineMultiQuestion):
    @property
    def required_attrs_if_runpy_or_full_code_missing(self):
        return (
            super(LatexRandomCodeInlineMultiQuestion, self)
            .required_attrs_if_runpy_or_full_code_missing
            + ["question_process_code", "answers_process_code"])

    def get_updated_page_desc(self, page_context, new_page_desc_dict):
        new_desc = (
            super(LatexRandomCodeInlineMultiQuestion, self)
                .get_updated_page_desc(page_context, new_page_desc_dict))
        if hasattr(new_desc, "answers"):
            if not isinstance(new_desc.answers, Struct):
                from relate.utils import dict_to_struct
                import yaml
                new_desc.answers = dict_to_struct(yaml.load(new_desc.answers))
        return new_desc

    def get_question(self, page_context, page_data):
        # template error is supposed to be raised here
        self.update_page_desc(page_context, page_data)
        return super(LatexRandomCodeInlineMultiQuestion, self) \
            .get_question(page_context, page_data)

    def allowed_attrs(self):
        return super(LatexRandomCodeInlineMultiQuestion, self).allowed_attrs() + (
            ("blank_process_code", str),
            ("blank_answer_process_code", str)
        )

    def grade(self, page_context, page_data, answer_data, grade_data):
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


class RandomQuestionFollowedImageUploadQuestion(LatexRandomQuestion, ImageUploadQuestion):

    def __init__(self, vctx, location, page_desc):
        ImageUploadQuestion.__init__(self, vctx, location, page_desc)
        required_ends = "_followed_imgupload"
        if vctx is not None:
            if not self.page_desc.id.endswith("required_ends"):
                raise ValidationError(
                    string_concat(
                        "%s: " % location,
                        _("'page id' should ends with '%s'"
                          ) % required_ends))  # type: ignore
        self.followed_page_id = self.page_desc.id[:len(required_ends)]

    def initialize_page_data(self, page_context):
        from course.models import FlowPageData
        fpd = FlowPageData.objects.get(
            flow_session=page_context.flow_session,
            course=page_context.course,
            page_id=self.followed_page_id
        )
        assert fpd is not None
        return fpd.data


class RandomInlineMultiQuestionFollowedImageUploadQuestion(RandomQuestionFollowedImageUploadQuestion):
    pass
