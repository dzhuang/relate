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
import six
from django.core.checks import CheckMessage, Warning, Critical
from django.core.management.base import CommandError
import logging
import warnings
from typing import Union
from django.core.exceptions import ImproperlyConfigured
from relate.utils import RELATEDeprecateWarning
from .utils import (
    get_docker_program_version, run_cmd_line)
from distutils.version import LooseVersion as lv
from course.checks import (
    GENERIC_ERROR_PATTERN, INSTANCE_ERROR_PATTERN,
    RelateCriticalCheckMessage)
import docker

# {{{ for mypy

if False:
    from typing import Any, Text, Optional, Any, List, Dict, Tuple  # noqa

# }}}

REQUIRED_DOCKER_VERSION = '1.6.0'
REQUIRED_MACHINE_VERSION = '0.7.0'
LOCALHOST = '127.0.0.1'
DOCKER_MACHINE_RUNNING = 'Running'
DOCKER_HOST = 'DOCKER_HOST'
DOCKER_CERT_PATH = 'DOCKER_CERT_PATH'
DOCKER_TLS_VERIFY = 'DOCKER_TLS_VERIFY'
DEFAULT_MACHINE_NAME = "default"

RELATE_RUNPY_DOCKER_CONFIG = "RELATE_RUNPY_DOCKER_CONFIG"
RELATE_RUNPY_DOCKER_CONFIG_ITEM_DOCKER_IMAGE = '%s["docker_image]'
RELATE_DOCKER_TLS_CONFIG = "RELATE_DOCKER_TLS_CONFIG"
RELATE_DOCKER_URL = "RELATE_DOCKER_URL"

RELATE_DOCKER_RUNPY_IMAGE = "RELATE_DOCKER_RUNPY_IMAGE"
RUNPY_ATTR_NOT_CONFIGURED_PATTERN = (  # noqa
    '%(location)s not configured for docker runpy')
RUNPY_CONFIGURED_ERR_PATTERN = (  # noqa
    '"%(config_name)s" not configured for '
    'docker runpy in %(location)s')

RUNPY_BACKWARD_COMPAT_USED_OLD_CONFIG_MSG_PATTERN = (  # noqa
    RUNPY_CONFIGURED_ERR_PATTERN.rstrip(".")
    + ', used %(deprecated_location)s instead.')

RUNPY_DEPRECATED_SETTINGS_PATTERN = (
    "%(deprecated_location)s is deprecated, use %(location)s instead"
)

DOCKER_MACHINE_GENERIC_ERROR_PATTERN = (
    "%(error_type)s: %(error_str)s")

# default values
DOCKER_RUNPY_CLIENT_VERSION_DEFAULT = "1.19"
DOCKER_RUNPY_CLIENT_TIMEOUT_DEFAULT = 15

# Debuging switch
Debug = False
logger = logging.getLogger("django.request")


def _show_log():
    # typo: (None) -> bool
    from django.conf import settings
    return Debug or getattr(settings, "DEBUG")


show_log = _show_log()


def get_ip_address(ip_range):
    import ipaddress
    return ipaddress.ip_address(six.text_type(ip_range))


class RelateDockMachineCheckMessageBase(CheckMessage):
    def __init__(self, *args, **kwargs):
        super(RelateDockMachineCheckMessageBase, self).__init__(*args, **kwargs)
        if not self.obj:
            self.obj = "docker-machine"


class RelateDockMachineDebugMessage(RelateDockMachineCheckMessageBase):
    def __init__(self, *args, **kwargs):
        from django.core.checks import DEBUG
        super(RelateDockMachineDebugMessage, self).__init__(
            DEBUG, *args, **kwargs)


class RelateDockMachineCritical(RelateDockMachineCheckMessageBase):
    def __init__(self, *args, **kwargs):
        from django.core.checks import CRITICAL
        super(RelateDockMachineCritical, self).__init__(
            CRITICAL, *args, **kwargs)


class RelateDockMachineWarning(RelateDockMachineCheckMessageBase):
    def __init__(self, *args, **kwargs):
        from django.core.checks import WARNING
        super(RelateDockMachineWarning, self).__init__(
            WARNING, *args, **kwargs)


class DockerError(Exception):
    pass


class DockerNotEnabledError(Exception):
    pass


class DockerVersionNotSupportedError(DockerError):
    pass


class DockerMachineError(Exception):
    pass


class DockerMachineVersionNotSupportedError(DockerMachineError):
    pass


class DockerMachineVariablesNotExportedError(DockerMachineError):
    pass



def has_error(errors):
    # type: (list[CheckMessage]) -> bool
    from django.core.checks import WARNING
    for error in errors:
        if error.level > WARNING:
            return True
    return False


class ClientConfigBase(object):
    def __init__(self, client_config, **kwargs):
        # type: (Dict, **Any) -> None
        self.client_config = client_config

    def create_client(self):
        # type: () -> docker.Client
        self.update_client_creation_kwargs()
        return docker.Client(**self.client_config)

    def update_client_creation_kwargs(self):
        # type: () -> None
        raise NotImplementedError()

    def checks(self):
        # type: () -> list[CheckMessage]
        errors = self.check_docker_installed_and_version_supported()
        if has_error(errors):
            return errors

        errors.extend(self.check_config_validaty())
        if has_error(errors):
            return errors

        errors.extend(self.check_docker_status())
        if has_error(errors):
            return errors

        errors.extend(self.check_client())
        return errors

    def check_docker_installed_and_version_supported(self):
        # type: () -> list[CheckMessage]
        errors = []

        try:
            docker_version = (
                get_docker_program_version("docker", print_output=Debug))
        except Exception as e:
            return [
                Critical(
                    msg=DOCKER_MACHINE_GENERIC_ERROR_PATTERN
                        %{
                            "error_type": type(e).__name__,
                            "error_str": str(e)
                        },
                    id="docker_version_exception_unknown.E001",
                    obj=RuntimeError
                )]

        if (docker_version is None
                or lv(docker_version) < lv(REQUIRED_DOCKER_VERSION)):
            errors.append(
                Critical(
                    msg=(
                        "You must install docker with version >="
                        "%(version)s, to enable RELATE Docker"
                        " functionalities."
                        % {"version": REQUIRED_DOCKER_VERSION}),
                    obj=DockerVersionNotSupportedError,
                    id="docker_program.E001"
                )
            )

        return errors

    def check_client_tls(self):
        # type: () -> list[CheckMessage]
        errors = []
        if not self.client_config.get("tls", False):
            errors.append(
                Warning(
                    msg="SecurityWarning: TLS is not enabled "
                        "for Docker client at %s."
                        % RELATE_RUNPY_DOCKER_CONFIG,
                    id="docker_config.W001"
                )
            )
        return errors

    def check_config_validaty(self):
        # type: () -> list[CheckMessage]
        return []

    def check_docker_status(self):
        # type: () -> list[CheckMessage]
        return []

    def check_engine(self):
        # type: () -> list[CheckMessage]
        return self.check_docker_installed_and_version_supported()

    def check_client(self):
        # type: () -> list[CheckMessage]
        errors = self.check_client_tls()
        if has_error(errors):
            return errors
        try:
            self.create_client()
        except Exception as e:
            errors.append(
                RelateCriticalCheckMessage(
                    msg=GENERIC_ERROR_PATTERN
                        %{"location": RELATE_RUNPY_DOCKER_CONFIG,
                          "error_type": type(e).__name__,
                          "error_str": str(e)
                          },
                    id="runpy_docker_config.E002"
                )
            )
        return errors


class ClientForDockerMixin(object):
    def update_client_creation_kwargs(self):
        # type: () -> None
        return


class ClientForDockerMachineMixin(object):
    def __init__(self, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        docker_machine_config = kwargs.pop("docker_machine_config", None)
        super(ClientForDockerMachineMixin, self).__init__(  # type: ignore # noqa
                client_config, **kwargs)
        self.docker_running_shell = (
                docker_machine_config.get("shell", None))
        self.docker_machine_name = (
                docker_machine_config.get("name", DEFAULT_MACHINE_NAME))

    def check_docker_installed_and_version_supported(self):
        # type: () -> list[CheckMessage]
        errors = (
            super(ClientForDockerMachineMixin, self)
                .check_docker_installed_and_version_supported())

        try:
            docker_machine_version = (
                get_docker_program_version("docker-machine", print_output=Debug))
        except Exception as e:
            return [
                RelateCriticalCheckMessage(
                    msg=GENERIC_ERROR_PATTERN
                        %{"location": RELATE_RUNPY_DOCKER_CONFIG,
                          "error_type": type(e).__name__,
                          "error_str": str(e)
                          },
                    id="docker_machine_config.E002"
                )]

        err_msg = None
        if (not docker_machine_version
                or lv(docker_machine_version) < lv(REQUIRED_MACHINE_VERSION)):
            err_msg = (
                "You must install docker-machine with version >="
                "%(machine_version)s, to enable RELATE Docker"
                " functionalities."
                % {"machine_version": REQUIRED_MACHINE_VERSION})

        if err_msg:
            return [
                RelateCriticalCheckMessage(
                    msg=err_msg,
                    id="runpy_docker_machine_config.E002",
                    obj=DockerMachineVersionNotSupportedError.__name__
                )]

        return errors


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
    def __init__(self, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        image = kwargs.pop("docker_image", None)
        super(RunpyDockerMixin, self).__init__(client_config, **kwargs)  # type: ignore # noqa

        if not image:
            from django.conf import settings
            deprecated_image_setting = (
                getattr(settings, RELATE_DOCKER_RUNPY_IMAGE, None))
            if not deprecated_image_setting:
                raise ImproperlyConfigured(
                    RUNPY_ATTR_NOT_CONFIGURED_PATTERN
                    % {'location':
                           "%s['docker_image']" % RELATE_RUNPY_DOCKER_CONFIG})
            else:
                warnings.warn(
                    RUNPY_DEPRECATED_SETTINGS_PATTERN
                    % {
                        'location': (
                            '%s["docker_image]' % RELATE_RUNPY_DOCKER_CONFIG),
                        'deprecated_location': RELATE_DOCKER_RUNPY_IMAGE
                    },
                    RELATEDeprecateWarning,
                    stacklevel=2
                )
                image = deprecated_image_setting
        assert image
        self.image = image

        if not self.client_config.get("timout"):
            self.client_config["timeout"] = DOCKER_RUNPY_CLIENT_TIMEOUT_DEFAULT
        if not self.client_config.get("version"):
            self.client_config["version"] = DOCKER_RUNPY_CLIENT_VERSION_DEFAULT
        if not self.client_config.get("tls"):
            from django.conf import settings
            deprecated_tls_setting = (
                getattr(settings, RELATE_DOCKER_TLS_CONFIG, None))
            if deprecated_tls_setting:
                warnings.warn(
                    RUNPY_DEPRECATED_SETTINGS_PATTERN
                    % {
                        'location': (
                            '%s["client_config"]["tls"]'
                            % RELATE_RUNPY_DOCKER_CONFIG),
                        'deprecated_location': RELATE_DOCKER_TLS_CONFIG
                    },
                    RELATEDeprecateWarning,
                    stacklevel=2
                )
                self.client_config["tls"] = deprecated_tls_setting
        else:
            from docker.tls import TLSConfig
            if not isinstance(self.client_config["tls"], TLSConfig):
                raise ImproperlyConfigured(
                    INSTANCE_ERROR_PATTERN
                    %{
                        "location": (
                            '%s["client_config"]["tls"]'
                            % RELATE_RUNPY_DOCKER_CONFIG),
                        "types": TLSConfig.__name__
                    }
                )

        self.private_public_ip_map_dict = (
            kwargs.get("private_public_ip_map_dict", {}))

    def check_config_validaty(self):
        # type: () -> list[CheckMessage]
        errors = (
            super(RunpyDockerMixin, self)
                .check_config_validaty())

        if has_error(errors):
            return errors

        if self.private_public_ip_map_dict:
            if not isinstance(self.private_public_ip_map_dict, dict):
                errors.append(
                    RelateCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {'location':
                                    "%s in %s"
                                    % ("private_public_ip_map_dict",
                                       RELATE_RUNPY_DOCKER_CONFIG),
                                "types": "str"}),
                        id="private_public_ip_map_dict.E001"))
            else:
                for private_ip, public_ip in (
                        six.iteritems(self.private_public_ip_map_dict)):
                    import ipaddress
                    try:
                        get_ip_address(six.text_type(private_ip))
                        get_ip_address(six.text_type(public_ip))
                    except Exception as e:
                        errors.append(RelateCriticalCheckMessage(
                            msg=(
                                GENERIC_ERROR_PATTERN
                                % {'location':
                                       "%s in %s"
                                       % ("private_public_ip_map_dict",
                                          RELATE_RUNPY_DOCKER_CONFIG),
                                   "error_type": type(e).__name__,
                                   "error_str": str(e)
                                   }),
                            id="private_public_ip_map_dict.E002"))

        return errors

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
    def check_docker_status(self):
        # type: () -> list[CheckMessage]
        errors = self.check_docker_machine_setup()
        return errors

    def check_docker_machine_setup(self, env=os.environ):
        # type: () -> list[CheckMessage]
        errors = []
        if not self._is_docker_machine_running():
            if show_log:
                logger.info("'%s' is not running. Starting..."
                             % self.docker_machine_name)
            try:
                self._start_docker_machine()
            except Exception as e:
                errors.append(
                    RelateDockMachineCritical(
                        msg=(DOCKER_MACHINE_GENERIC_ERROR_PATTERN
                             % {
                                 "error_type": type(e).__name__,
                                 "error_str": str(e)
                             }),
                        id="runpy_docker_machine.E002"
                    )
                )
                return errors
        else:
            if show_log:
                logger.info("'%s' is running." % self.docker_machine_name)

        # If env variables are not set, generate the cmdline for user to set them
        if (DOCKER_HOST not in env
                or DOCKER_CERT_PATH not in env
                or DOCKER_TLS_VERIFY not in env):
            if show_log:
                logger.info("Environment variables for machine '%s' have "
                             "not been exported."
                             % self.docker_machine_name)
            try:
                docker_machine_env_cmdline_msg = (
                    self._get_docker_machine_env_cmdline_msg())
            except Exception as e:
                errors.append(
                    RelateDockMachineCritical(
                        msg=(DOCKER_MACHINE_GENERIC_ERROR_PATTERN
                             % {
                                 "error_type": type(e).__name__,
                                 "error_str": str(e)
                             }),
                        id="runpy_docker_machine.E002"
                    )
                )
                return errors
            else:
                errors.append(
                    RelateDockMachineCritical(
                        msg=docker_machine_env_cmdline_msg,
                        obj=DockerMachineVariablesNotExportedError,
                        id="runpy_docker_machine_state.E001"
                        )
                    )
        else:
            if show_log:
                logger.info("Environment variables for machine '%s' have "
                             "been exported."
                             % self.docker_machine_name)

        return errors

    def _is_docker_machine_running(self):
        # type: () -> bool
        return self._get_docker_machine_status() == DOCKER_MACHINE_RUNNING

    def _get_docker_machine_status(self):
        # type: () -> Text
        status = run_cmd_line(
            ['docker-machine', 'status', self.docker_machine_name])
        assert status
        return status.strip()

    def _start_docker_machine(self):
        # type: () -> None
        run_cmd_line(
            ['docker-machine', 'start', self.docker_machine_name],
            print_output=True)

    def _get_docker_machine_env_cmdline_msg(self):
        # type: () -> Text
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
            from relate.utils import is_windows_platform
            if is_windows_platform():
                msg += ("\nThe above export script is for 'cmd' shell, "
                        "you can specify your shell via "
                        "RELATE_RUNPY_DOCKER_CONFIG['local_docker_machine']"
                        "['config']['shell'], see "
                        "https://docs.docker.com/machine/reference/env/.")

        return msg


Docker_client_config_ish = Union[
        ClientForDockerConfigure, ClientForDockerMachineConfigure,
        RunpyClientForDockerConfigure, RunpyClientForDockerMachineConfigure]


def get_docker_client_config(docker_config, for_runpy=True):
    # type: (Dict, bool, **Any) -> Optional[Docker_client_config_ish]

    """
    Get the client config from docker_config, with backward compatibility
    (i.e., original settings RELATE_DOCKER_RUNPY_IMAGE, RELATE_DOCKER_URL and
    RELATE_DOCKER_TLS_CONFIG)
    :param docker_config: Optional, a :class:`dict` instance. If not specified,
    RELATE_RUNPY_DOCKER_CONFIG will be used.
    :param for_runpy: Optional, a :class:`bool` instance, default to True,
    representing whether the client
    is used for runpy (code question)
    :return: a `Docker_client_config_ish` instance.
    """
    from copy import deepcopy
    configs = deepcopy(docker_config)
    docker_image = configs.pop("docker_image", None)
    client_config = configs.pop("client_config", {})
    use_local_docker_machine = False
    local_docker_machine_config = configs.pop("local_docker_machine_config", {})
    if local_docker_machine_config:
        from relate.utils import is_windows_platform, is_osx_platform
        if (local_docker_machine_config.get("enabled", False)
            and
                (is_windows_platform() or is_osx_platform())):
            use_local_docker_machine = True

    kwargs = {}
    kwargs.update(configs)
    if for_runpy:
        kwargs.update({"docker_image": docker_image})

    if use_local_docker_machine:
        docker_machine_config = local_docker_machine_config.get("config", {})
        kwargs.update({"docker_machine_config": docker_machine_config})

        if for_runpy:
            return RunpyClientForDockerMachineConfigure(client_config, **kwargs)
        else:
            return ClientForDockerMachineConfigure(client_config, **kwargs)

    if for_runpy:
        return RunpyClientForDockerConfigure(client_config, **kwargs)
    else:
        return ClientForDockerConfigure(client_config, **kwargs)
