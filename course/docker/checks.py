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

from django.conf import settings
from django.core.checks import register, Critical

RELATE_STARTUP_DOCKER_CHECKS_TAG = "relate_startup_docker_checks"

DEBUG = False


def check_docker_client_config(app_configs, **kwargs):
    docker_client_config = settings.RELATE_RUNPY_DOCKER_CLIENT_CONFIG
    if docker_client_config is None:
        return []

    return docker_client_config.checks()


def register_docker_client_config_checks():
    if not getattr(settings, "RELATE_RUNPY_DOCKER_ENABLED", False):
        return
    register(check_docker_client_config, RELATE_STARTUP_DOCKER_CHECKS_TAG)
