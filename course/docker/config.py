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
from django.core.checks import CheckMessage, Critical
import logging
import warnings
from typing import Union
from django.core.exceptions import ImproperlyConfigured
from relate.utils import RELATEDeprecateWarning
from .utils import (
    get_docker_program_version, run_cmd_line)
from distutils.version import LooseVersion as lv  # noqa
from course.checks import (
    GENERIC_ERROR_PATTERN, INSTANCE_ERROR_PATTERN,
    RelateCriticalCheckMessage)
import docker

# {{{ for mypy

if False:
    from typing import Any, Text, Optional, Any, List, Dict, Tuple  # noqa

# }}}

# {{{ Constants

DEFAULT_DOCKER_RUNPY_CONFIG_ALIAS = 'default'

LOCALHOST = '127.0.0.1'
DOCKER_MACHINE_RUNNING = 'Running'
DEFAULT_MACHINE_NAME = "default"
DOCKER_HOST = 'DOCKER_HOST'
DOCKER_CERT_PATH = 'DOCKER_CERT_PATH'
DOCKER_TLS_VERIFY = 'DOCKER_TLS_VERIFY'

# default values
REQUIRED_DOCKER_VERSION = '1.6.0'
REQUIRED_DOCKER_MACHINE_VERSION = '0.7.0'
DOCKER_RUNPY_CLIENT_VERSION_DEFAULT = "1.19"
DOCKER_RUNPY_CLIENT_TIMEOUT_DEFAULT = 15

# }}}

# {{{ Settings name

RELATE_RUNPY_DOCKER_ENABLED = "RELATE_RUNPY_DOCKER_ENABLED"
RELATE_DOCKERS = "RELATE_DOCKERS"
RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME = "RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME"

# Settings to be deprecated
RELATE_DOCKER_TLS_CONFIG = "RELATE_DOCKER_TLS_CONFIG"
RELATE_DOCKER_URL = "RELATE_DOCKER_URL"
RELATE_DOCKER_RUNPY_IMAGE = "RELATE_DOCKER_RUNPY_IMAGE"

# }}}

# {{{ String patterns

RUNPY_ATTR_NOT_CONFIGURED_PATTERN = (  # noqa
    '%(location)s not configured for docker runpy')
RUNPY_CONFIGURED_ERR_PATTERN = (  # noqa
    '"%(config_name)s" not configured for '
    'docker runpy in %(location)s')
RUNPY_DEPRECATED_SETTINGS_PATTERN = (
    "%(deprecated_location)s is deprecated, use %(location)s instead"
)
DOCKER_MACHINE_GENERIC_ERROR_PATTERN = (
    "%(error_type)s: %(error_str)s")

# }}}

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


class RunpyDockerClientConfigNameIsNoneWarning(Warning):
    pass


class RunpyDockerConfigNotSetError(ImproperlyConfigured):
    pass


def has_error(errors):
    # type: (list[CheckMessage]) -> bool
    from django.core.checks import WARNING
    for error in errors:
        if error.level > WARNING:
            return True
    return False


class ClientConfigBase(object):
    def __init__(self, docker_config_name, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        self.docker_config_name = docker_config_name
        self.client_config = client_config

        self.client_config_location = (
            "'client_config' of '%s' in %s"
            % (self.docker_config_name, RELATE_DOCKERS)
        )
        self.client_tls_location = "'tls' in %s" % self.client_config_location
        self.client_base_url_location = (
            "'base_url' in %s" % self.client_tls_location)

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
                    msg=(DOCKER_MACHINE_GENERIC_ERROR_PATTERN
                         % {
                             "error_type": type(e).__name__,
                             "error_str": str(e)
                         }),
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
        tls = self.client_config.get("tls", None)
        if not tls:
            from django.core.checks import Warning as CheckWarning
            errors.append(
                CheckWarning(
                    msg=("SecurityWarning: TLS is not enabled "
                         "for Docker client in %(location)s"
                         % {"location": self.client_tls_location}
                         ),
                    id="docker_config_client_tls.W001",
                    obj=self.__class__
                )
            )
        else:
            from docker.tls import TLSConfig
            if not isinstance(tls, TLSConfig):
                errors.append(
                    RelateCriticalCheckMessage(
                        msg=(
                            INSTANCE_ERROR_PATTERN
                            % {
                                "location": self.client_tls_location,
                                "types": TLSConfig.__name__}),
                        id="docker_config_client_tls.E001",
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
                    msg=(GENERIC_ERROR_PATTERN
                         % {"location": ("'client_config' of '%s' in %s"
                                         % (self.docker_config_name,
                                            RELATE_DOCKERS)),
                            "error_type": type(e).__name__,
                            "error_str": str(e)
                            }),
                    id="docker_config_client_create.E001"
                )
            )
        return errors


class ClientForDockerMixin(object):
    def __init__(self, docker_config_name, client_config, **kwargs):
        super(ClientForDockerMixin, self).__init__(  # type: ignore # noqa
                docker_config_name, client_config, **kwargs)

        # This is not needed for docker-machine
        base_url = self.client_config.get("base_url", None)
        if not base_url:
            from django.conf import settings
            deprecated_docker_url_setting = (
                getattr(settings, RELATE_DOCKER_URL, None))
            if not deprecated_docker_url_setting:
                raise ImproperlyConfigured(
                    RUNPY_ATTR_NOT_CONFIGURED_PATTERN
                    % {'location': self.client_base_url_location})
            else:
                warnings.warn(
                    RUNPY_DEPRECATED_SETTINGS_PATTERN
                    % {
                        'location': self.client_base_url_location,
                        'deprecated_location': RELATE_DOCKER_RUNPY_IMAGE
                    },
                    RELATEDeprecateWarning,
                    stacklevel=2
                )
            assert deprecated_docker_url_setting
            self.client_config["base_url"] = deprecated_docker_url_setting

        # This is not needed for docker-machine
        if not self.client_config.get("tls"):
            from django.conf import settings
            deprecated_tls_setting = (
                getattr(settings, RELATE_DOCKER_TLS_CONFIG, None))
            if deprecated_tls_setting:
                warnings.warn(
                    RUNPY_DEPRECATED_SETTINGS_PATTERN
                    % {
                        "location": self.client_tls_location,
                        'deprecated_location': RELATE_DOCKER_TLS_CONFIG},
                    RELATEDeprecateWarning,
                    stacklevel=2
                )
                self.client_config["tls"] = deprecated_tls_setting

    def update_client_creation_kwargs(self):
        # type: () -> None
        return


class ClientForDockerMachineMixin(object):
    def __init__(self, docker_config_name, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        docker_machine_config = kwargs.pop("docker_machine_config", None)
        super(ClientForDockerMachineMixin, self).__init__(  # type: ignore # noqa
                docker_config_name, client_config, **kwargs)
        self.docker_running_shell = (
                docker_machine_config.get("shell", None))
        self.docker_machine_name = (
                docker_machine_config.get("name", DEFAULT_MACHINE_NAME))

    def check_docker_installed_and_version_supported(self):
        # type: () -> list[CheckMessage]
        errors = super(ClientForDockerMachineMixin, self)\
            .check_docker_installed_and_version_supported()

        try:
            docker_machine_version = (
                get_docker_program_version("docker-machine", print_output=Debug))
        except Exception as e:
            return [
                RelateCriticalCheckMessage(
                    msg=(GENERIC_ERROR_PATTERN
                         % {"location": ("'%s' in %s"
                                         % (self.docker_config_name,
                                            RELATE_DOCKERS)
                                         ),
                            "error_type": type(e).__name__,
                            "error_str": str(e)}),
                    id="docker_machine_version_exception_unknown.E001"
                )]

        if (not docker_machine_version
                or lv(docker_machine_version) < lv(REQUIRED_DOCKER_MACHINE_VERSION)):
            errors.append(
                RelateCriticalCheckMessage(
                    msg=(
                        "You must install docker-machine with version >="
                        "%(machine_version)s, to enable RELATE Docker"
                        " functionalities."
                        % {"machine_version": REQUIRED_DOCKER_MACHINE_VERSION}),
                    id="docker_machine_version.E001",
                    obj=DockerMachineVersionNotSupportedError.__name__
                ))

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


class RunpyDockerMixinBase(object):
    def __init__(self, docker_config_name, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        image = kwargs.pop("docker_image", None)
        super(RunpyDockerMixinBase, self).__init__(
            docker_config_name, client_config, **kwargs)  # type: ignore # noqa

        self.docker_image_location = (
            "'docker_image' of '%s' in %s"
            % (self.docker_config_name, RELATE_DOCKERS)
        )

        if not image:
            from django.conf import settings
            deprecated_image_setting = (
                getattr(settings, RELATE_DOCKER_RUNPY_IMAGE, None))
            if not deprecated_image_setting:
                raise ImproperlyConfigured(
                    RUNPY_ATTR_NOT_CONFIGURED_PATTERN
                    % {'location': self.docker_image_location})
            else:
                warnings.warn(
                    RUNPY_DEPRECATED_SETTINGS_PATTERN
                    % {
                        'location': self.docker_image_location,
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

        self.private_public_ip_map_dict = (
            kwargs.get("private_public_ip_map_dict", {}))

        self.private_public_ip_map_dict_location = (
            "'private_public_ip_map_dict' of '%s' in %s"
            % (self.docker_config_name, RELATE_DOCKERS)
        )

    def check_config_validaty(self):
        # type: () -> list[CheckMessage]
        errors = (
            super(RunpyDockerMixinBase, self).check_config_validaty())

        if has_error(errors):
            return errors

        if self.private_public_ip_map_dict:
            if not isinstance(self.private_public_ip_map_dict, dict):
                errors.append(
                    RelateCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {'location':
                                    self.private_public_ip_map_dict_location,
                                "types": "str"}),
                        id="private_public_ip_map_dict.E001"))
            else:
                for private_ip, public_ip in (
                        six.iteritems(self.private_public_ip_map_dict)):
                    try:
                        get_ip_address(six.text_type(private_ip))
                        get_ip_address(six.text_type(public_ip))
                    except Exception as e:
                        errors.append(RelateCriticalCheckMessage(
                            msg=(
                                GENERIC_ERROR_PATTERN
                                % {'location':
                                       self.private_public_ip_map_dict_location,
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
        RELATE_DOCKERS['private_public_ip_map_dict'] need to be
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


class RunpyDockerMixin(RunpyDockerMixinBase):
    pass


class RunpyDockerMachineMixin(RunpyDockerMixinBase):
    def __init__(self, docker_config_name, client_config, **kwargs):
        # type: (Text, Dict, **Any) -> None
        super(RunpyDockerMachineMixin, self).__init__(
            docker_config_name, client_config, **kwargs)

        self.local_docker_machine = (
            "'local_docker_machine' of '%s' in %s"
            % (self.docker_config_name, RELATE_DOCKERS)
        )
        self.local_docker_machine_config_shell_location = (
            "'shell' in 'config' of %s" % self.local_docker_machine)

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
        # type: (dict[Any]) -> list[CheckMessage]
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

                def get_readable_error_msg(e):
                    # type: (Exception) -> Text
                    """Get a more readable error message for windows when
                     failing "docker-machine env", as its e.args is a tuple with
                     multiple elements.

                    Without this, the stdout of `str(e)` is, for example:

                        ('Exited with return code 1', 'Error checking TLS
                        connection: Error checking and/or regenerating the certs:
                        There was an error validating certificates for host
                        "192.168.99.101:2376": x509: certificate is valid for
                        192.168.99.100, not 192.168.99.101\nYou can attempt to
                        regenerate them using \'docker-machine regenerate-certs
                        [name]\'.\nBe advised that this will trigger a Docker
                        daemon restart which might stop running containers.\n\n', 1)

                    With this function, the stdout is:
                        Exited with return code 1

                        Error checking TLS connection: Error checking and/or
                        regenerating the certs: There was an error validating
                        certificates for host "192.168.99.101:2376": x509:
                        certificate is valid for 192.168.99.100,
                        not 192.168.99.101
                        You can attempt to regenerate them using 'docker-machine
                        regenerate-certs [name]'.
                        Be advised that this will trigger a Docker daemon restart
                        which might stop running containers
                        1
                    """
                    return "\n".join([str(s).rstrip("\n") for s in list(e.args)])

                errors.append(
                    RelateDockMachineCritical(
                        msg=(DOCKER_MACHINE_GENERIC_ERROR_PATTERN
                             % {
                                 "error_type": type(e).__name__,
                                 "error_str": get_readable_error_msg(e)
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
                        "you can specify your shell in %(location)s, see "
                        "https://docs.docker.com/machine/reference/env/."
                        % {"location":
                               self.local_docker_machine_config_shell_location}
                        )

        return msg


Docker_client_config_ish = Union[
        ClientForDockerConfigure, ClientForDockerMachineConfigure,
        RunpyClientForDockerConfigure, RunpyClientForDockerMachineConfigure]


def get_docker_client_config(docker_config_name, for_runpy=True):
    # type: (Text, bool, **Any) -> Optional[Docker_client_config_ish]

    """
    Get the client config from docker configurations with docker_config_name
    in RELATE_DOCKS, with backward compatibility (i.e., original
    settings RELATE_DOCKER_RUNPY_IMAGE, RELATE_DOCKER_URL and
    RELATE_DOCKER_TLS_CONFIG) if it is a runpy docker.
    :param docker_config: Optional, a :class:`dict` instance. If not specified,
    RELATE_DOCKERS will be used.
    :param for_runpy: Optional, a :class:`bool` instance, default to True,
    representing whether the client is used for runpy (code question)
    :return: a `Docker_client_config_ish` instance.
    """
    from copy import deepcopy
    configs = deepcopy(get_config_by_name(docker_config_name))
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
            return RunpyClientForDockerMachineConfigure(
                docker_config_name, client_config, **kwargs)
        else:
            return ClientForDockerMachineConfigure(
                docker_config_name, client_config, **kwargs)

    if for_runpy:
        return RunpyClientForDockerConfigure(
            docker_config_name, client_config, **kwargs)
    else:
        return ClientForDockerConfigure(
            docker_config_name, client_config, **kwargs)


def get_config_by_name(docker_config_name):
    from django.conf import settings
    relate_dockers_config = getattr(settings, RELATE_DOCKERS, None)
    if not relate_dockers_config:
        raise ImproperlyConfigured(
            "%s: '%s' is not configured in RELATE local settings."
            % (RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME, RELATE_DOCKERS)
        )
    if docker_config_name not in relate_dockers_config:
        raise ImproperlyConfigured(
            "%s: %s has no configuration named '%s'"
            % (RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME, RELATE_DOCKERS,
               docker_config_name)
        )
    return relate_dockers_config[docker_config_name]


def get_relate_runpy_docker_client_config(silence_for_none=True):  # noqa
    from django.conf import settings
    runpy_enabled = getattr(settings, RELATE_RUNPY_DOCKER_ENABLED, False)
    if not runpy_enabled:
        return None
    relate_runpy_docker_client_config_name = (
        getattr(settings, RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME,
                DEFAULT_DOCKER_RUNPY_CONFIG_ALIAS))

    if relate_runpy_docker_client_config_name is None:
        msg = ("%s can not be None when %s is True"
               % (RELATE_RUNPY_DOCKER_CLIENT_CONFIG_NAME,
                  RELATE_RUNPY_DOCKER_ENABLED))
        if not silence_for_none:
            raise RunpyDockerConfigNotSetError(msg)
        else:
            warnings.warn(
                msg,
                RunpyDockerClientConfigNameIsNoneWarning,
                stacklevel=2)
            return None
    return get_docker_client_config(
        relate_runpy_docker_client_config_name, for_runpy=True)

# vim: foldmethod=marker
