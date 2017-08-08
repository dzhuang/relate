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

import os
import logging
from typing import Union
from django.core.exceptions import ImproperlyConfigured
from relate.utils import is_windows_platform, is_osx_platform
from .utils import (
    get_docker_program_version, run_cmd_line)
from pkg_resources import parse_version as pv
import docker

# {{{ for mypy

if False:
    from typing import Any, Text, Optional, Any, List, Dict, Tuple  # noqa

# }}}


Debug = False

logger = logging.getLogger("django.request")
REQUIRED_DOCKER_VERSION = '1.6.0'
REQUIRED_MACHINE_VERSION = '0.7.0'
LOCALHOST = '127.0.0.1'
DOCKER_MACHINE_RUNNING = 'Running'
DOCKER_HOST = 'DOCKER_HOST'
DOCKER_CERT_PATH = 'DOCKER_CERT_PATH'
DOCKER_TLS_VERIFY = 'DOCKER_TLS_VERIFY'
DEFAULT_MACHINE_NAME = "default"

RELATE_RUNPY_DOCKER_CONFIG = "RELATE_RUNPY_DOCKER_CONFIG"
RELATE_DOCKER_TLS_CONFIG = "RELATE_DOCKER_TLS_CONFIG"
RELATE_DOCKER_URL = "RELATE_DOCKER_URL"

RELATE_DOCKER_RUNPY_IMAGE = "RELATE_DOCKER_RUNPY_IMAGE"
RUNPY_BACKWARD_COMPAT_NOT_CONFIGURED_ERR_PATTERN = (  # noqa
    '"%(config_name)s" not configured for '
    'docker runpy in %(config_position)s')

RUNPY_BACKWARD_COMPAT_USED_OLD_CONFIG_MSG_PATTERN = (  # noqa
    RUNPY_BACKWARD_COMPAT_NOT_CONFIGURED_ERR_PATTERN.rstrip(".")
    + ', used %(original_config)s instead.')


class DockerNotEnabledError(Exception):
    pass


class DockerVariablesNotExportedError(Exception):
    pass


class DockerDependenciesNotInstalledError(Exception):
    pass


class ClientConfigBase(object):
    def __init__(self, image, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        self.image = image
        self.client_config = client_config

    def update_client_creation_kwargs(self):
        # type: () -> None
        raise NotImplementedError()

    def check_client_tls(self):
        # type: () -> None
        if not self.client_config.get("tls", False):
            logger.warning("SecurityWarning: TLS is not enabled "
                           "for Docker client.")

    def create_client(self):
        # type: () -> docker.Client
        self.update_client_creation_kwargs()
        self.check_client_tls()
        return docker.Client(**self.client_config)

    def validate(self):
        # type: () -> None
        self.create_client()


class ClientForDockerMixin(object):
    def update_client_creation_kwargs(self):
        # type: () -> None
        return


class ClientForDockerMachineMixin(object):
    def __init__(self, image, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        docker_machine_config = kwargs.pop("docker_machine_config")

        super(ClientForDockerMachineMixin, self).__init__(  # type: ignore # noqa
                image, client_config, **kwargs)
        self.docker_running_shell = (
                docker_machine_config.get("shell", None))
        self.docker_machine_name = (
                docker_machine_config.get("name", DEFAULT_MACHINE_NAME))


class ClientForDockerConfigure(ClientForDockerMixin, ClientConfigBase):
    def update_client_creation_kwargs(self):
        # type: () -> None
        return


class ClientForDockerMachineConfigure(ClientForDockerMachineMixin, ClientConfigBase):
    def update_client_creation_kwargs(self):
        # type: () -> None
        from docker.utils import kwargs_from_env
        self.client_config.update(kwargs_from_env())


class RunpyDockerMixin(object):
    def __init__(self, image, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        super(RunpyDockerMixin, self).__init__(image, client_config, **kwargs)  # type: ignore # noqa
        self.private_public_ip_map_dict = (
            kwargs.get("private_public_ip_map_dict", {}))

    def get_client_and_container_connection_info(
                self, default_port, default_connect_host_ip):
        # type: (int, Text) -> Tuple[docker.Client, Text, Text, int]
        client = self.create_client()  # type: ignore # noqa
        dresult = client.create_container(
                image=self.image,  # type: ignore # noqa
                command=[
                    "/opt/runpy/runpy",
                    "-1"],
                host_config={
                    "Memory": 384*10**6,
                    "MemorySwap": -1,
                    "PublishAllPorts": True,
                    # Do not enable: matplotlib stops working if enabled.
                    # "ReadonlyRootfs": True,
                    },
                user="runpy")

        container_id = dresult["Id"]

        # FIXME: Prohibit networking

        connect_host_ip = default_connect_host_ip
        client.start(container_id)
        container_props = client.inspect_container(container_id)
        (port_info,) = (container_props
                        ["NetworkSettings"]["Ports"]["%d/tcp" % default_port])
        port_host_ip = port_info.get("HostIp")

        if port_host_ip != "0.0.0.0":
            connect_host_ip = port_host_ip
        connect_host_ip = self.get_connect_ip(connect_host_ip)
        port = int(port_info["HostPort"])

        return (client, container_id,
                self.get_public_accessible_ip(connect_host_ip), port)

    def get_connect_ip(self, connect_host_ip):
        # type: (Text) -> Text
        return connect_host_ip

    def get_public_accessible_ip(self, ip):
        # type: (Text) -> Text
        """
        RELATE_RUNPY_DOCKER_CONFIG['private_public_ip_map_dict'] need to be
        configured in cases when your RELATE instance and (runpy) docker-running
        instances are not on the same subnet.
        See: discussion https://github.com/inducer/relate/issues/268
        :param ip: the private ip
        :return: the corresponding public ip which can be visited by
        RELATE instance.
        """

        if self.private_public_ip_map_dict:
            return self.private_public_ip_map_dict.get(ip, ip)
        return ip


class RunpyDockerMachineMixin(RunpyDockerMixin):
    def get_connect_ip(self, connect_host_ip):
        # type: (Text) -> Text
        container_ip = self._get_container_ip()
        return container_ip if container_ip else connect_host_ip

    def _get_container_ip(self):
        # type: () -> Optional[Text]
        args = ['docker-machine', 'ip']
        container_ip = run_cmd_line(args, print_output=Debug)
        return container_ip.strip() if container_ip else None


class RunpyClientForDockerConfigure(RunpyDockerMixin, ClientForDockerConfigure):
    def get_connect_ip(self, connect_host_ip):
        # type: (Text) -> Text
        return connect_host_ip


class RunpyClientForDockerMachineConfigure(
        RunpyDockerMachineMixin, ClientForDockerMachineConfigure):
    def validate(self):
        # type: () -> None
        self.validate_docker_installed_and_version_supported()
        self.docker_machine_setup()
        self.create_client()

    def initialize_docker(self, env=os.environ):
        # type: (Optional[Any]) -> None
        self.docker_machine_setup(env)

    def docker_machine_setup(self, env=os.environ):
        # type: (Optional[Any]) -> None
        if not self._is_docker_machine_running():
            try:
                self._start_docker_machine()
            except:
                raise

        logger.info("docker-machine '%s' is running."
                    % self.docker_machine_name)

        # If env variables are not set, generate the cmdline for user to set them
        if (DOCKER_HOST not in env
            or DOCKER_CERT_PATH not in env
            or
                    DOCKER_TLS_VERIFY not in env):
            self._get_docker_machine_env_cmdline()

        logger.info("Environment variables for docker-machine '%s' have "
                    "been exported." % self.docker_machine_name)

    def _is_docker_machine_running(self):
        # type: () -> bool
        return self._get_docker_machine_status() == DOCKER_MACHINE_RUNNING

    def _get_docker_machine_status(self):
        # type: () -> Text
        status = run_cmd_line(
            ['docker-machine', 'status', self.docker_machine_name],
            print_output=Debug)
        assert status
        return status.strip()

    def _start_docker_machine(self):
        # type: () -> None
        logger.info("Docker-machine '%s' is not running. Starting"
                    % self.docker_machine_name)
        run_cmd_line(
            ['docker-machine', 'start', self.docker_machine_name],
            print_output=True)

    def _get_docker_machine_env_cmdline(self):
        # type: () -> None
        logger.info("Environment variables for docker-machine '%s' have "
                    "not been exported."
                    % self.docker_machine_name)
        args = ['docker-machine', 'env', self.docker_machine_name]
        if self.docker_running_shell:
            args += ["--shell", self.docker_running_shell]

        def output_process_func(output_list):
            # type: (List[Text]) -> List[Text]
            if not output_list:
                return []
            if (output_list[0].strip() == (
                    "You can further specify your shell with either "
                    "'cmd' or 'powershell' with the --shell flag.")):
                output_list.pop(0)
            return output_list

        output = run_cmd_line(args, output_process_func=output_process_func,
                              print_output=Debug)
        msg = ("You need to export DOCKER variables to the system "
               "environments to enable RELATE Docker functionalities. "
               "Please following the instructions below and try to start "
               "the server again: \n%s%s\n%s" % ("-" * 50, output, "-" * 50))
        if not self.docker_running_shell:
            if is_windows_platform():
                msg += ("\nThe above export script is for 'cmd' shell, "
                        "you can specify your shell via "
                        "RELATE_RUNPY_DOCKER_CONFIG['local_docker_machine']"
                        "['config']['shell'], see "
                        "https://docs.docker.com/machine/reference/env/.")

        raise DockerVariablesNotExportedError(msg)

    def validate_docker_installed_and_version_supported(self):
        # type:() -> None
        err_msg = None

        docker_machine_version = (
            get_docker_program_version("docker-machine", print_output=Debug))
        if (not docker_machine_version
                or pv(docker_machine_version) < pv(REQUIRED_MACHINE_VERSION)):
            err_msg = (
                "You must install docker-machine version "
                "%(machine_version)s, to enable RELATE Docker"
                " functionalities."
                % {"machine_version": REQUIRED_MACHINE_VERSION})

        if err_msg:
            raise DockerDependenciesNotInstalledError(err_msg)


Docker_Client_ish = Union[
        ClientForDockerConfigure, ClientForDockerMachineConfigure,
        RunpyClientForDockerConfigure, RunpyClientForDockerMachineConfigure]


def update_runpy_docker_client_config_kwargs(
        docker_image, docker_config, client_config,
        use_local_docker_machine, **kwargs):
    # type: (Text, Dict, Dict, bool, **Any) -> Tuple[Text, Dict, Dict]
    if not docker_image:
        original_relate_docker_runpy_image = (
            kwargs.get("original_relate_docker_runpy_image"))
        if original_relate_docker_runpy_image:
            docker_image = original_relate_docker_runpy_image
            logger.warning(
                RUNPY_BACKWARD_COMPAT_USED_OLD_CONFIG_MSG_PATTERN
                % {
                    'config_name': "docker_image",
                    'config_position': '%s'
                                       % RELATE_RUNPY_DOCKER_CONFIG,
                    'original_config': RELATE_DOCKER_RUNPY_IMAGE, })
        else:
            raise ImproperlyConfigured(
                RUNPY_BACKWARD_COMPAT_NOT_CONFIGURED_ERR_PATTERN
                % {
                    'config_name': "docker_image",
                    'config_position': '%s'
                                       % RELATE_RUNPY_DOCKER_CONFIG})

    if not client_config.get("timeout"):
        client_config.update({"timeout": 15})

    if not client_config.get("version"):
        client_config.update({"version": "1.19"})

    # When use_local_docker_machine, base_url and tls will be
    # generated by docker_utils.kwargs_from_env()
    if not use_local_docker_machine:
        if not client_config.get("base_url"):
            original_relate_docker_url = (
                kwargs.get("original_relate_docker_url"))
            if original_relate_docker_url:
                client_config.update(
                    {"base_url": original_relate_docker_url})
                logger.warning(
                    '[Warning]ImproperlyConfigured: ' +
                    RUNPY_BACKWARD_COMPAT_USED_OLD_CONFIG_MSG_PATTERN
                    % {
                        'config_name': "base_url",
                        'config_position': '%s'
                                           % RELATE_RUNPY_DOCKER_CONFIG,
                        'original_config': RELATE_DOCKER_URL})
            else:
                raise ImproperlyConfigured(
                    RUNPY_BACKWARD_COMPAT_NOT_CONFIGURED_ERR_PATTERN
                    % {
                        'config_name': "base_url",
                        'config_position': '%s["client"]["tls"]'
                                           % RELATE_RUNPY_DOCKER_CONFIG,
                    }
                )
        if not client_config.get("tls"):
            original_relate_docker_tls_config = (
                kwargs.get("original_relate_docker_tls_config"))
            if original_relate_docker_tls_config:
                client_config.update(
                    {"tls": original_relate_docker_tls_config})
                logger.warning(
                    '[Warning]ImproperlyConfigured: ' +
                    RUNPY_BACKWARD_COMPAT_NOT_CONFIGURED_ERR_PATTERN
                    % {
                        'config_name': "tls",
                        'config_position': '%s["client"]["tls"]'
                                           % RELATE_RUNPY_DOCKER_CONFIG,
                        'original_config': RELATE_DOCKER_TLS_CONFIG})
            else:
                logger.warning(
                    '[Warning]ImproperlyConfigured: ' +
                    RUNPY_BACKWARD_COMPAT_NOT_CONFIGURED_ERR_PATTERN
                    % {
                        'config_name': "tls",
                        'config_position': '%s["client"]["tls"]'
                                           % RELATE_RUNPY_DOCKER_CONFIG})

    return docker_image, docker_config, client_config


def get_docker_client_config(docker_config, for_runpy=False, **kwargs):
    # type: (Dict, bool, **Any) -> Optional[Docker_Client_ish]

    docker_config = docker_config.copy()
    docker_image = docker_config.pop("docker_image", None)
    client_config = docker_config.pop("client_config", {})
    use_local_docker_machine = False
    local_docker_machine_config = docker_config.pop("local_docker_machine", None)
    if local_docker_machine_config:
        if (local_docker_machine_config.get("enabled", False)
            and
                (is_windows_platform() or is_osx_platform())):
            use_local_docker_machine = True

    if for_runpy:
        # backward compatibility
        docker_image, docker_config, client_config = (
            update_runpy_docker_client_config_kwargs(
                docker_image, docker_config, client_config,
                use_local_docker_machine, **kwargs))

    if not docker_image:
        raise ImproperlyConfigured(
            RUNPY_BACKWARD_COMPAT_NOT_CONFIGURED_ERR_PATTERN
            % {
                'config_desc': "docker image",
                'config_name': "docker_image",
                'config_position': '"image"'})

    if use_local_docker_machine:
        docker_machine_config = local_docker_machine_config.get("config", {})
        docker_config.update({"docker_machine_config": docker_machine_config})

        if for_runpy:
            return RunpyClientForDockerMachineConfigure(
                docker_image, client_config, **docker_config)
        else:
            return ClientForDockerMachineConfigure(
                docker_image, client_config, **docker_config)

    if for_runpy:
        return RunpyClientForDockerConfigure(
            docker_image, client_config, **docker_config)
    else:
        return ClientForDockerConfigure(
            docker_image, client_config, **docker_config)
