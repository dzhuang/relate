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

try:
    from unittest import mock
except:
    import mock
from copy import deepcopy
from django.conf import settings

from django.test.utils import (  # noqa
    isolate_apps, override_settings, override_system_checks,
)
from django.test import SimpleTestCase
from django.core.checks import Error, Warning  # noqa
from django.core.management import call_command  # noqa
from course.docker.config import (
    get_docker_client_config, get_relate_runpy_docker_client_config)

from django.core.exceptions import ImproperlyConfigured
import docker.tls
import warnings

from course.docker.config import (  # noqa
    DEFAULT_DOCKER_RUNPY_CONFIG_ALIAS,

    RELATE_RUNPY_DOCKER_ENABLED,
    RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME,

    RELATE_DOCKERS,
    RunpyClientForDockerConfigure,
    RunpyClientForDockerMachineConfigure,
    ClientForDockerConfigure,
    ClientForDockerMachineConfigure,

    RunpyDockerClientConfigNameIsNoneWarning
)


GITLAB_CI = "GITLAB_CI"
APPVEYOR_CI = "APPVEYOR"


def skip_real_docker_test():
    import os
    for skipped_ci in [GITLAB_CI, APPVEYOR_CI]:
        if os.environ.get(skipped_ci):
            print("Running on %s" % skipped_ci)
            return True

    return False


skip_read_docker_test = skip_real_docker_test()
print(skip_read_docker_test)

ORIGINAL_RELATE_DOCKER_TLS_CONFIG = docker.tls.TLSConfig()
ORIGINAL_RELATE_DOCKER_URL = "http://original.url.net"
ORIGINAL_RELATE_DOCKER_RUNPY_IMAGE = "runpy_original.image"

TEST_TLS = docker.tls.TLSConfig()


TEST_DOCKERS = {
    "runpy_test": {
        "docker_image": "runpy_test.image",
        "client_config": {
            "base_url": "http://some.url.net",
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
TEST_DOCKERS["no_image"].pop("docker_image")

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


@override_settings(RELATE_DOCKERS=TEST_DOCKERS)
@mock.patch(
    "course.docker.checks.check_docker_client_config",
    side_effect=skip_check_docker_client_config)
class DeprecationTests(SimpleTestCase):
    @mock.patch("relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_NOT_EXIST)
    def test_get_runpy_config_with_not_exist_config_name(self,
                                                    mocked_register,
                                                    mocked_sys):
        with override_settings(RELATE_RUNPY_DOCKER_ENABLED=True):
            expected_error_msg = (
                "RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME: RELATE_DOCKERS "
                "has no configuration named 'not_exist_config'")
            with self.assertRaises(ImproperlyConfigured) as cm:
                get_relate_runpy_docker_client_config(silence_for_none=False)
            self.assertEqual(str(cm.exception), expected_error_msg)

        with override_settings(RELATE_RUNPY_DOCKER_ENABLED=False):
            result = (
                get_relate_runpy_docker_client_config(silence_for_none=False))
            self.assertIsNone(result)
            result = (
                get_relate_runpy_docker_client_config(silence_for_none=True))
            self.assertIsNone(result)

            @override_settings(RELATE_DOCKERS=TEST_DOCKERS)
            @mock.patch(
                "course.docker.checks.check_docker_client_config",
                side_effect=skip_check_docker_client_config)
            class NotDefinedConfigClientConfigGetFunctionTests(SimpleTestCase):
                @mock.patch("relate.utils.is_windows_platform", return_value=True)
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


"""
--tlsverify --tlscacert=/home/travis/.docker/ca.pem --tlscert=/home/travis/.docker/server-cert.pem 
--tlskey=/home/travis/.docker/server-key.pem -H unix:///var/run/docker.sock -H=0.0.0.0:2376
"""

import docker.tls
REAL_DOCKER_TLS_CONFIG = docker.tls.TLSConfig(
    client_cert=(
        "/home/travis/.docker/server-cert.pem",
        "/home/travis/.docker/server-key.pem",
        ),
    ca_cert="/home/travis/.docker/ca.pem",
    verify=True)

REAL_DOCKERS = {
    "runpy": {
        "docker_image": "inducer/relate-runpy-i386",
        "client_config": {
            "base_url": "unix:///var/run/docker.sock",
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

REAL_RUNPY_CONFIG_NAME = "runpy"

@override_settings(
    RELATE_DOCKERS=REAL_DOCKERS,
    RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=REAL_RUNPY_CONFIG_NAME
)
class ReadDockerTests(SimpleTestCase):
    def test_get_real_docker_client_config(self):
        result = get_relate_runpy_docker_client_config(silence_for_none=False)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
    def test_real_docker_check(self):
        call_command('check')