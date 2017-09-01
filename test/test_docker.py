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

TEST_DOCKER_TLS_CONFIG = docker.tls.TLSConfig()
SOME_TLS = docker.tls.TLSConfig()


TEST_DOCKERS = {
    "runpy": {
        "docker_image": "Some.image",
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
        "private_public_ip_map_dict": {"192.168.1.100", "192.168.100.100"},
    },
}


TEST_DOCKERS["no_image"] = deepcopy(TEST_DOCKERS["runpy"])
TEST_DOCKERS["no_image"].pop("docker_image")

TEST_DOCKERS["no_base_url"] = deepcopy(TEST_DOCKERS["runpy"])
TEST_DOCKERS["no_base_url"]["client_config"].pop("base_url")

TEST_DOCKERS["no_tls"] = deepcopy(TEST_DOCKERS["runpy"])
TEST_DOCKERS["no_tls"]["client_config"].pop("tls")

TEST_DOCKERS["no_local_docker_machine_config"] = deepcopy(TEST_DOCKERS["runpy"])
TEST_DOCKERS["no_local_docker_machine_config"].pop("local_docker_machine_config")

TEST_DOCKERS["local_docker_machine_config_not_enabled"] = (
    deepcopy(TEST_DOCKERS["runpy"]))
TEST_DOCKERS["local_docker_machine_config_not_enabled"]["enabled"] = False

VALID_RUNPY_CONFIG_NAME = "runpy"
RUNPY_DOCKER_CONFIG_NAME_NO_IMAGE = "no_image"
RUNPY_DOCKER_CONFIG_NAME_NO_BASE_URL = "no_base_url"
RUNPY_DOCKER_CONFIG_NAME_NO_TLS = "no_tls"
RUNPY_DOCKER_CONFIG_NAME_NO_DOCKER_MACHINE = "no_local_docker_machine_config"
RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED = (
    "local_docker_machine_config_not_enabled")


def get_test_dockers_copy():
    """
    prevent TEST_DOCKERS modified across tests
    """
    return deepcopy(TEST_DOCKERS)


def don_not_register_docker_startup_checks():
    return


#{{{ test course.docker.config.get_docker_client_config

@override_settings(RELATE_RUNPY_DOCKER_ENABLED=True,
                   RELATE_DOCKERS=TEST_DOCKERS,
                   RELATE_DOCKER_RUNPY_IMAGE="Original.image",
                   RELATE_DOCKER_TLS_CONFIG=docker.tls.TLSConfig(),
                   RELATE_DOCKER_URL="http://original.url"
                   )
@mock.patch(
    "course.docker.checks.register_docker_client_config_checks",
    side_effect=don_not_register_docker_startup_checks)
class GetDockerClientConfigTests(SimpleTestCase):

    # {{{ instance check
    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=VALID_RUNPY_CONFIG_NAME)
    def test_runpy_client_docker_machine_conf(self, mocked_register, mocked_sys):
        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerMachineConfigure)
        self.assertEqual(result.image, TEST_DOCKERS["docker_image"])

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=VALID_RUNPY_CONFIG_NAME)
    def test_client_docker_machine_conf(self, mocked_register, mocked_sys):
        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerMachineConfigure)
        with self.assertRaises(AttributeError):
            result.image

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=False)
    @mock.patch(
        "relate.utils.is_windows_platform", return_value=False)
    @override_settings(RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=VALID_RUNPY_CONFIG_NAME)
    def test_runpy_client_docker_conf(self, mocked_register, mocked_sys1, mocked_sys2):
        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "Some.image")

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=False)
    @mock.patch(
        "relate.utils.is_osx_platform", return_value=False)
    @override_settings(RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=VALID_RUNPY_CONFIG_NAME)
    def test_client_docker_conf(self, mocked_register, mocked_sys1, mocked_sys2):
        result = get_docker_client_config(VALID_RUNPY_CONFIG_NAME, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerConfigure)
        with self.assertRaises(AttributeError):
            result.image

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED)
    def test_runpy_client_docker_machine_conf_not_enabled(
            self, mocked_register, mocked_sys):
        result = get_docker_client_config(
            RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED, for_runpy=True)
        self.assertIsInstance(result, RunpyClientForDockerConfigure)
        self.assertEqual(result.image, "Some.image")

    @mock.patch(
        "relate.utils.is_windows_platform", return_value=True)
    @override_settings(
        RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME=RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED)
    def test_runpy_client_docker_machine_conf_not_enabled_not_runpy(
            self, mocked_register, mocked_sys):
        result = get_docker_client_config(
            RUNPY_DOCKER_CONFIG_NAME_DOCKER_MACHINE_NOT_ENABLED, for_runpy=False)
        self.assertIsInstance(result, ClientForDockerConfigure)
        with self.assertRaises(AttributeError):
            result.image
    # }}}
    # @mock.patch(
    #     "relate.utils.is_windows_platform", return_value=True)
    # @override_settings(RELATE_DOCKERS=TEST_DOCKERS,
    #                    RELATE_DOCKER_RUNPY_IMAGE=None,
    #                    RELATE_RUNPY_DOCKER_ENABLED=True)
    # def test_relate_docker_runpy_image_not_configure1(self, mocked_register):
    #     with self.assertRaises(ImproperlyConfigured):
    #         get_docker_client_config(TEST_DOCKERS, for_runpy=True)

    # @override_settings(RELATE_DOCKERS=TEST_DOCKER_CONFIG,
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
    # @override_settings(RELATE_DOCKERS=TEST_DOCKER_CONFIG,
    #                    RELATE_DOCKER_RUNPY_IMAGE=None,
    #                    RELATE_RUNPY_DOCKER_ENABLED=True)
    # def test_relate_docker_runpy_image_not_configure(self, mocked_register):
    #     from django.core.exceptions import ImproperlyConfigured
    #     with self.assertRaises(ImproperlyConfigured):
    #         get_docker_client_config(TEST_DOCKER_CONFIG)

# }}}