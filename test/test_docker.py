from unittest import mock
from copy import deepcopy
from django.conf import settings

from django.db import connections, models
from django.test import TestCase
from django.core import checks
from django.test.utils import isolate_apps, override_settings
from django.test.utils import (
    isolate_apps, override_settings, override_system_checks,
)
from django.test import SimpleTestCase
from django.core.checks import Error, Warning
from django.core.management import call_command
from course.docker.config import get_docker_client_config

from course.apps import CourseConfig
from django.core.exceptions import ImproperlyConfigured
import docker.tls

from course.checks import INSTANCE_ERROR_PATTERN

from course.docker.config import (
    RunpyClientForDockerConfigure,
    RunpyClientForDockerMachineConfigure,
    ClientForDockerConfigure,
    ClientForDockerMachineConfigure
)


SOME_TLS = docker.tls.TLSConfig()

TEST_CONFIG = {
    "docker_image": "some.image",
    "client_config": {
        "base_url": "http://some.url.net",
        "tls": SOME_TLS,
        "timeout": 15,
        "version": "1.19"
    },

    "local_docker_machine_config": {
        "enabled": True,
        "config":{
            "shell": None,
            "name": "default",
        },
    },

    "private_public_ip_map_dict": {},
}

TEST_CONFIG_NO_DOCKER_IMAGE = deepcopy(TEST_CONFIG)
TEST_CONFIG_NO_DOCKER_IMAGE.pop("docker_image")

TEST_CONFIG_DOCKER_MACHINE_NOT_ENABLED = deepcopy(TEST_CONFIG)
TEST_CONFIG_DOCKER_MACHINE_NOT_ENABLED["local_docker_machine_config"]["enabled"] = False

TEST_DOCKER_RUNPY_IMAGE = "some.image2"

SOME_TLS = docker.tls.TLSConfig()
TEST_DOCKER_TLS_CONFIG = docker.tls.TLSConfig()


def don_not_register_docker_startup_checks():
    return


#{{{ test course.docker.config.get_docker_client_config

@override_settings(RELATE_RUNPY_DOCKER_ENABLED=True)
@mock.patch(
    "course.docker.checks.register_docker_client_config_checks",
    side_effect=don_not_register_docker_startup_checks)
class GetDockerClientConfigTests(SimpleTestCase):

    # {{{ instance check
    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(RELATE_RUNPY_DOCKER_CONFIG=TEST_CONFIG)
    def test_runpy_client_docker_machine_conf(self, mocked_register, mocked_sys):
        result = get_docker_client_config(TEST_CONFIG, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerMachineConfigure)
        self.assertEqual(result.image, TEST_CONFIG["docker_image"])

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(RELATE_RUNPY_DOCKER_CONFIG=TEST_CONFIG)
    def test_client_docker_machine_conf(self, mocked_register, mocked_sys):
        result = get_docker_client_config(TEST_CONFIG, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerMachineConfigure)
        with self.assertRaises(AttributeError):
            result.image

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=False)
    @mock.patch(
        "relate.utils.is_windows_platform", return_value=False)
    @override_settings(RELATE_RUNPY_DOCKER_CONFIG=TEST_CONFIG)
    def test_runpy_client_docker_conf(self, mocked_register, mocked_sys1, mocked_sys2):
        result = get_docker_client_config(TEST_CONFIG, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, TEST_CONFIG["docker_image"])

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=False)
    @mock.patch(
        "relate.utils.is_osx_platform", return_value=False)
    @override_settings(RELATE_RUNPY_DOCKER_CONFIG=TEST_CONFIG)
    def test_client_docker_conf(self, mocked_register, mocked_sys1, mocked_sys2):
        result = get_docker_client_config(TEST_CONFIG, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerConfigure)
        with self.assertRaises(AttributeError):
            result.image

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CONFIG=TEST_CONFIG_DOCKER_MACHINE_NOT_ENABLED)
    def test_runpy_client_docker_machine_conf_not_enabled(
            self, mocked_register, mocked_sys):
        result = get_docker_client_config(
            TEST_CONFIG_DOCKER_MACHINE_NOT_ENABLED, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(
            result.image, TEST_CONFIG_DOCKER_MACHINE_NOT_ENABLED["docker_image"])

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CONFIG=TEST_CONFIG_DOCKER_MACHINE_NOT_ENABLED)
    def test_runpy_client_docker_machine_conf_not_enabled_not_runpy(
            self, mocked_register, mocked_sys):
        result = get_docker_client_config(
            TEST_CONFIG_DOCKER_MACHINE_NOT_ENABLED, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerConfigure)
        with self.assertRaises(AttributeError):
            result.image
    # }}}
    # @mock.patch(
    #     "relate.utils.is_windows_platform", return_value=True)
    # @override_settings(RELATE_RUNPY_DOCKER_CONFIG=TEST_CONFIG,
    #                    RELATE_DOCKER_RUNPY_IMAGE=None,
    #                    RELATE_RUNPY_DOCKER_ENABLED=True)
    # def test_relate_docker_runpy_image_not_configure1(self, mocked_register):
    #     with self.assertRaises(ImproperlyConfigured):
    #         get_docker_client_config(TEST_CONFIG, for_runpy=True)

    # @override_settings(RELATE_RUNPY_DOCKER_CONFIG=TEST_DOCKER_CONFIG,
    #                    RELATE_DOCKER_RUNPY_IMAGE=TEST_DOCKER_RUNPY_IMAGE,
    #                    RELATE_RUNPY_DOCKER_ENABLED=True)
    # def test_relate_docker_runpy_image_not_configure2(self, mocked_register):
    #     with not self.assertRaises(ImproperlyConfigured):
    #         client_config = get_docker_client_config(
    #             TEST_DOCKER_CONFIG, for_runpy=True)
    #         self.assertTrue(isinstance(client_config, ))
    #
    #
    #     with self.assertRaises(ImproperlyConfigured):
    #         get_docker_client_config(TEST_DOCKER_CONFIG, for_runpy=True)
    #
    #
    # @override_settings(RELATE_RUNPY_DOCKER_CONFIG=TEST_DOCKER_CONFIG,
    #                    RELATE_DOCKER_RUNPY_IMAGE=None,
    #                    RELATE_RUNPY_DOCKER_ENABLED=True)
    # def test_relate_docker_runpy_image_not_configure(self, mocked_register):
    #     from django.core.exceptions import ImproperlyConfigured
    #     with self.assertRaises(ImproperlyConfigured):
    #         get_docker_client_config(TEST_DOCKER_CONFIG)

# }}}