# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2017 Dong Zhuang"

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

import sys
from six import StringIO

try:
    from unittest import mock
except:
    import mock

try:
    from test.support import EnvironmentVarGuard  # noqa
except:
    from test.test_support import EnvironmentVarGuard  # noqa

from unittest import skipIf
from copy import deepcopy
from django.conf import settings
from django.core import mail

from django.test.utils import (  # noqa
    isolate_apps, override_settings
)
from django.test import SimpleTestCase
from django.core.checks import Error, Warning  # noqa
from django.core import checks
from django.core.management import call_command  # noqa
from course.docker.config import (
    get_docker_client_config, get_relate_runpy_docker_client_config)

from django.core.exceptions import ImproperlyConfigured
from relate.utils import is_windows_platform, is_osx_platform
import docker.tls
import warnings

from course.docker.config import (  # noqa
    DEFAULT_DOCKER_RUNPY_CONFIG_ALIAS,

    RELATE_RUNPY_DOCKER_ENABLED,
    RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME,

    # items to be deprecated
    RELATE_DOCKER_TLS_CONFIG,
    RELATE_DOCKER_URL,
    RELATE_DOCKER_RUNPY_IMAGE,

    RELATEDeprecateWarning,

    RELATE_DOCKERS,
    ClientConfigBase,
    RunpyClientForDockerConfigure,
    RunpyClientForDockerMachineConfigure,
    ClientForDockerConfigure,
    ClientForDockerMachineConfigure,

    RunpyDockerClientConfigNameIsNoneWarning
)
from django.test import TestCase
from test_pages import SingleCoursePageTestMixin, QUIZ_FLOW_ID

# Switch for test locally
Debug = False

GITLAB_CI = "GITLAB_CI"
APPVEYOR_CI = "APPVEYOR"

# Controller in CI scripts
ENABLE_DOCKER_TEST = "ENABLE_DOCKER_TEST"


def _skip_real_docker_test():
    import os
    for skipped_ci in [GITLAB_CI, APPVEYOR_CI]:
        if os.environ.get(skipped_ci):
            print("Running on %s" % skipped_ci)
            return True

    enable_docker_test = os.environ.get(ENABLE_DOCKER_TEST)
    if enable_docker_test is None:
        return True

    if Debug:
        return False

    return False


skip_real_docker_test = _skip_real_docker_test()
SKIP_REAL_DOCKER_REASON = "These are tests for real docker"

ORIGINAL_RELATE_DOCKER_TLS_CONFIG = docker.tls.TLSConfig()
ORIGINAL_RELATE_DOCKER_URL = "http://original.url.net:2376"
ORIGINAL_RELATE_DOCKER_RUNPY_IMAGE = "runpy_original.image"

TEST_TLS = docker.tls.TLSConfig()


TEST_DOCKERS = {
    "runpy_test": {
        "docker_image": "runpy_test.image",
        "client_config": {
            "base_url": "http://some.url.net:2376",
            "tls": TEST_TLS,
            "timeout": 15,
            "version": "1.19"
        },
        "local_docker_machine_config": {
            "enabled": True,
            "config": {
                "shell": None,
                "name": "default",
            },
        },
        "private_public_ip_map_dict": {
            "192.168.1.100": "192.168.100.100"},
    },
}

TEST_DOCKERS["no_image"] = deepcopy(TEST_DOCKERS["runpy_test"])
del TEST_DOCKERS["no_image"]["docker_image"]

TEST_DOCKERS["no_base_url"] = deepcopy(TEST_DOCKERS["runpy_test"])
TEST_DOCKERS["no_base_url"]["client_config"].pop("base_url")

TEST_DOCKERS["no_tls"] = deepcopy(TEST_DOCKERS["runpy_test"])
del TEST_DOCKERS["no_tls"]["client_config"]["tls"]

TEST_DOCKERS["no_local_docker_machine_config"] = (
    deepcopy(TEST_DOCKERS["runpy_test"]))
TEST_DOCKERS["no_local_docker_machine_config"].pop("local_docker_machine_config")

TEST_DOCKERS["local_docker_machine_config_not_enabled"] = (
    deepcopy(TEST_DOCKERS["runpy_test"]))
TEST_DOCKERS[
    "local_docker_machine_config_not_enabled"][
    "local_docker_machine_config"]["enabled"] = False

VALID_RUNPY_CONFIG_NAME = "runpy_test"
RUNPY_DOCKER_CONFIG_NAME_NO_IMAGE = "no_image"
RUNPY_DOCKER_CONFIG_NAME_NO_BASE_URL = "no_base_url"
RUNPY_DOCKER_CONFIG_NAME_NO_TLS = "no_tls"
RUNPY_DOCKER_CONFIG_NAME_NO_DOCKER_MACHINE = "no_local_docker_machine_config"
RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED = (
    "local_docker_machine_config_not_enabled")

RUNPY_DOCKER_CONFIG_NAME_NOT_EXIST = "not_exist_config"
TEST_DOCKERS.pop(RUNPY_DOCKER_CONFIG_NAME_NOT_EXIST, None)


TEST_DOCKERS_WITH_DEFAULT_CONFIG = {
    DEFAULT_DOCKER_RUNPY_CONFIG_ALIAS: {
        "docker_image": "runpy_default.image",
        "client_config": {
            "base_url": "http://default.url.net",
            "tls": docker.tls.TLSConfig(),
            "timeout": 15,
            "version": "1.19"
        }
    }
}


def skip_check_docker_client_config(app_configs, **kwargs):
    return []


@override_settings(RELATE_RUNPY_DOCKER_ENABLED=True,
                   RELATE_DOCKERS=TEST_DOCKERS,
                   RELATE_DOCKER_RUNPY_IMAGE="Original.image",
                   RELATE_DOCKER_TLS_CONFIG=docker.tls.TLSConfig(),
                   RELATE_DOCKER_URL="http://original.url")
@mock.patch(
    "course.docker.checks.check_docker_client_config",
    side_effect=skip_check_docker_client_config)
class ClientConfigGetFunctionTests(SimpleTestCase):
    """
    test course.docker.config.get_docker_client_config
    """
    @mock.patch("relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=VALID_RUNPY_CONFIG_NAME)
    def test_config_instance_windows(self, mocked_register, mocked_sys):
        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerMachineConfigure)
        self.assertEqual(result.image, "runpy_test.image")

        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerMachineConfigure)
        with self.assertRaises(AttributeError):
            result.image

        result = get_relate_runpy_docker_client_config(silence_for_none=False)
        self.assertIsInstance(result, RunpyClientForDockerMachineConfigure)
        self.assertEqual(result.image, "runpy_test.image")

    @mock.patch("relate.utils.is_windows_platform", return_value=False)
    @mock.patch("relate.utils.is_windows_platform", return_value=False)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=VALID_RUNPY_CONFIG_NAME)
    def test_config_instance_not_windows(
            self, mocked_register, mocked_sys1, mocked_sys2):
        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "runpy_test.image")

        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerConfigure)
        with self.assertRaises(AttributeError):
            result.image

        result = get_relate_runpy_docker_client_config(silence_for_none=False)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "runpy_test.image")

    @mock.patch("relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED)  # noqa
    def test_config_instance_docker_machine_not_enabled_windows(
            self, mocked_register, mocked_sys):
        result = get_docker_client_config(
            RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "runpy_test.image")

        result = get_docker_client_config(
            RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerConfigure)
        with self.assertRaises(AttributeError):
            result.image

        result = get_relate_runpy_docker_client_config(silence_for_none=False)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "runpy_test.image")

    @mock.patch("relate.utils.is_windows_platform", return_value=False)
    @mock.patch("relate.utils.is_osx_platform", return_value=False)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED)  # noqa
    def test_config_instance_docker_machine_not_enabled_not_windows(
            self, mocked_register, mocked_sys1, mocked_sys2):
        result = get_docker_client_config(
            RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED,
            for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "runpy_test.image")

        result = get_docker_client_config(
            RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED,
            for_runpy=False)
        self.assertIsInstance(result, ClientForDockerConfigure)
        with self.assertRaises(AttributeError):
            result.image

        result = get_relate_runpy_docker_client_config(silence_for_none=False)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "runpy_test.image")


@override_settings(RELATE_DOCKERS=TEST_DOCKERS_WITH_DEFAULT_CONFIG)
@mock.patch(
    "course.docker.checks.check_docker_client_config",
    side_effect=skip_check_docker_client_config)
class DefaultConfigClientConfigGetFunctionTests(SimpleTestCase):
    """
    Test RELATE_DOCKS contains a configure named "default"
    (DEFAULT_DOCKER_RUNPY_CONFIG_ALIAS)
    """
    @override_settings(RELATE_RUNPY_DOCKER_ENABLED=True,

                       # Explicitly set to None
                       RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=None)
    def test_get_runpy_config_explicitly_named_none(self, mocked_register):
        self.assertTrue(hasattr(settings, RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME))

        expected_msg = ("%s can not be None when %s is True"
               % (RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME,
                  RELATE_RUNPY_DOCKER_ENABLED))
        with self.assertRaisesMessage(ImproperlyConfigured, expected_msg):
            get_relate_runpy_docker_client_config(silence_for_none=False)

        with warnings.catch_warnings(record=True) as warns:
            self.assertIsNone(
                get_relate_runpy_docker_client_config(silence_for_none=True))
            self.assertEqual(len(warns), 1)
            self.assertIsInstance(
                warns[0].message, RunpyDockerClientConfigNameIsNoneWarning)
            self.assertEqual(str(warns[0].message), expected_msg)

    @override_settings(RELATE_RUNPY_DOCKER_ENABLED=True)
    def test_get_runpy_config_not_named(self, mocked_register):
        with self.settings():
            self.assertTrue(
                hasattr(settings, RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME))
            # simulate RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME is not configured
            del settings.RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME
            self.assertRaises(AttributeError, getattr,
                              settings, RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME)
            result = get_relate_runpy_docker_client_config(silence_for_none=False)
            self.assertEqual(result.image, "runpy_default.image")

    @override_settings(RELATE_RUNPY_DOCKER_ENABLED=False,
                       RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=None)
    def test_get_runpy_config_not_named_not_enabled(self, mocked_register):

        with self.settings():
            # simulate RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME is not configured
            del settings.RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME
            self.assertRaises(AttributeError, getattr,
                              settings,
                              RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME)
            result = get_relate_runpy_docker_client_config(
                silence_for_none=False)
            self.assertIsNone(result)


@override_settings(RELATE_DOCKERS=TEST_DOCKERS, RELATE_RUNPY_DOCKER_ENABLED=True)
@mock.patch(
    "course.docker.checks.check_docker_client_config",
    side_effect=skip_check_docker_client_config)
class DeprecationWarningsTests(SimpleTestCase):
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_NO_IMAGE
    )
    def test_no_image(self, mocked_register):
        with override_settings(
                RELATE_DOCKER_RUNPY_IMAGE=ORIGINAL_RELATE_DOCKER_RUNPY_IMAGE):
            with warnings.catch_warnings(record=True) as warns:
                self.assertIsNotNone(
                    get_relate_runpy_docker_client_config())
                self.assertEqual(len(warns), 1)
                self.assertIsInstance(
                    warns[0].message, RELATEDeprecateWarning)

            with self.settings():
                del settings.RELATE_DOCKER_RUNPY_IMAGE
                with self.assertRaises(ImproperlyConfigured):
                    get_relate_runpy_docker_client_config()

    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_NO_BASE_URL
    )
    def test_no_base_url(self, mocked_register):
        with override_settings(
                RELATE_DOCKER_URL=ORIGINAL_RELATE_DOCKER_URL):
            with warnings.catch_warnings(
                    record=True) as warns:
                self.assertIsNotNone(
                    get_relate_runpy_docker_client_config())
                if is_windows_platform() or is_osx_platform():
                    # because local_docker_machine_config is enabled
                    self.assertEqual(len(warns), 0)
                else:
                    self.assertEqual(len(warns), 1)
                    self.assertIsInstance(
                        warns[0].message,
                        RELATEDeprecateWarning)

            with self.settings():
                del settings.RELATE_DOCKER_URL
                if is_windows_platform() or is_osx_platform():
                    self.assertIsNotNone(
                        get_relate_runpy_docker_client_config())
                else:
                    with self.assertRaises(
                            ImproperlyConfigured):
                        get_relate_runpy_docker_client_config()

    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_NO_TLS
    )
    def test_no_tls(self, mocked_register):
        with override_settings(
                RELATE_DOCKER_TLS_CONFIG=ORIGINAL_RELATE_DOCKER_TLS_CONFIG):
            with warnings.catch_warnings(
                    record=True) as warns:
                self.assertIsNotNone(
                    get_relate_runpy_docker_client_config())
                if is_windows_platform() or is_osx_platform():
                    # because local_docker_machine_config is enabled
                    self.assertEqual(len(warns), 0)
                else:
                    self.assertEqual(len(warns), 1)
                    self.assertIsInstance(
                        warns[0].message,
                        RELATEDeprecateWarning)


@override_settings(RELATE_DOCKERS=TEST_DOCKERS)
@mock.patch(
    "course.docker.checks.check_docker_client_config",
    side_effect=skip_check_docker_client_config)
class NotDefinedConfigClientConfigGetFunctionTests(SimpleTestCase):
    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_NOT_EXIST)  # noqa
    def test_get_runpy_config_with_not_exist_config_name(self,
                                                         mocked_register,
                                                         mocked_sys):
        with override_settings(RELATE_RUNPY_DOCKER_ENABLED=True):
            expected_error_msg = (
                "RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME: "
                "RELATE_DOCKERS "
                "has no configuration named 'not_exist_config'")
            with self.assertRaises(ImproperlyConfigured) as cm:
                get_relate_runpy_docker_client_config(
                    silence_for_none=False)
            self.assertEqual(str(cm.exception), expected_error_msg)

        with override_settings(RELATE_RUNPY_DOCKER_ENABLED=False):
            result = (
                get_relate_runpy_docker_client_config(
                    silence_for_none=False))
            self.assertIsNone(result)
            result = (
                get_relate_runpy_docker_client_config(
                    silence_for_none=True))
            self.assertIsNone(result)


REAL_DOCKERS = {
    "runpy": {
        "docker_image": "inducer/relate-runpy-i386",
        "client_config": {
            "base_url": "unix:///var/run/docker.sock",
            "tls": None,
            "timeout": 15,
            "version": "1.19"
        },
        "local_docker_machine_config": {
            "enabled": True,
            "config": {
                "shell": None,
                "name": "default",
            },
        },
        "private_public_ip_map_dict": {
            "192.168.1.100": "192.168.100.100"},
    },
}

REAL_RUNPY_CONFIG_NAME = "runpy"


@skipIf(skip_real_docker_test, SKIP_REAL_DOCKER_REASON)
@override_settings(
    RELATE_RUNPY_DOCKER_ENABLED=True,
    RELATE_DOCKERS=REAL_DOCKERS,
    RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=REAL_RUNPY_CONFIG_NAME
)
class ReadDockerTests(SimpleTestCase):
    def test_get_real_docker_client_config(self):
        result = get_relate_runpy_docker_client_config(silence_for_none=False)
        self.assertIsInstance(
            result,
            (RunpyClientForDockerConfigure,
             RunpyClientForDockerMachineConfigure)
        )


@skipIf(skip_real_docker_test, SKIP_REAL_DOCKER_REASON)
@override_settings(
    RELATE_RUNPY_DOCKER_ENABLED=True,
    RELATE_DOCKERS=REAL_DOCKERS,
    RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=REAL_RUNPY_CONFIG_NAME
)
class TLSNotConfiguredWarnCheck(SimpleTestCase):
    def setUp(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.stdout, self.stderr = StringIO(), StringIO()
        sys.stdout, sys.stderr = self.stdout, self.stderr

    def tearDown(self):
        sys.stdout, sys.stderr = self.old_stdout, self.old_stderr

    @override_settings(SILENCED_SYSTEM_CHECKS=["docker_config_client_tls.W001"])
    def test_silence_tls_not_configured_warning(self):
        out = StringIO()
        err = StringIO()
        call_command('check', stdout=out, stderr=err)
        self.assertEqual(out.getvalue(),
                         'System check identified no issues (1 silenced).\n')
        self.assertEqual(err.getvalue(), '')

    def test_tls_not_configured_warning(self):
        result = checks.run_checks()
        self.assertEqual([r.id for r in result], ["docker_config_client_tls.W001"])


@skipIf(skip_real_docker_test, SKIP_REAL_DOCKER_REASON)
@override_settings(
    RELATE_RUNPY_DOCKER_ENABLED=True,
    RELATE_DOCKERS=REAL_DOCKERS,
    RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=REAL_RUNPY_CONFIG_NAME
)
class RealDockerCodePageTest(SingleCoursePageTestMixin, TestCase):
    flow_id = QUIZ_FLOW_ID
    page_id = "addition"

    def test_code_page_correct_answer(self):
        answer_data = {"answer": "c = a + b"}
        expected_str = (
            "It looks like you submitted code that is identical to "
            "the reference solution. This is not allowed.")
        resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
        self.assertContains(resp, expected_str, count=1)
        self.assertEqual(resp.status_code, 200)
        self.assertSessionScoreEqual(1)

    def test_code_page_wrong_answer(self):
        answer_data = {"answer": "c = a - b"}
        resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
        self.assertEqual(resp.status_code, 200)
        self.assertSessionScoreEqual(0)

    def test_code_page_user_code_exception_raise(self):
        answer_data = {"answer": "c = a ^ b"}
        from django.utils.html import escape
        expected_error_str1 = escape(
            "Your code failed with an exception. "
            "A traceback is below.")
        expected_error_str2 = escape(
            "TypeError: unsupported operand type(s) for ^: "
            "'float' and 'float'")
        resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, expected_error_str1, count=1)
        self.assertContains(resp, expected_error_str2, count=1)
        self.assertSessionScoreEqual(0)

    # @override_settings(
    #     EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    # def test_code_with_uncaught_exception(self):
    #     mail.outbox = []
    #     answer_data = {"answer": "c = a ^ b"}
    #     resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertEqual(len(mail.outbox), 1)
    #     resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertSessionScoreEqual(0)
    #     self.assertEqual(len(mail.outbox), 2)


# @override_settings(
#     RELATE_RUNPY_DOCKER_ENABLED=True,
#     RELATE_DOCKERS=TEST_DOCKERS,
#     RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=REAL_RUNPY_CONFIG_NAME
# )
# class CodePageTestOther(SingleCoursePageTestMixin, TestCase):
#     flow_id = QUIZ_FLOW_ID
#     page_id = "addition"
#
#     def test_code_page(self):
#         answer_data = {"answer": "c = a + b"}
#         resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
#         self.assertEqual(resp.status_code, 200)
#
#         answer_data = {"answer": "d = a + b"}
#         resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
#         self.assertEqual(resp.status_code, 200)
#         self.assertSessionScoreEqual(0)
#
#     @override_settings(
#         EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
#     def test_code_with_uncaught_exception(self):
#         mail.outbox = []
#         answer_data = {"answer": "c = a ^ b"}
#         resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(len(mail.outbox), 1)
#         resp = self.client_post_answer_by_page_id(self.page_id, answer_data)
#         self.assertEqual(resp.status_code, 200)
#         self.assertSessionScoreEqual(0)
#         self.assertEqual(len(mail.outbox), 2)
