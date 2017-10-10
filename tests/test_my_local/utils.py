from django.conf import settings
import platform
from tempfile import mkdtemp

TEST_NODES = ["Dzhuang-surface", "OfficeZD", "dzhuang-PC"]


def _skip_test():
    if not getattr(settings, "USING_LOCAL_TEST_SETTINGS"):
        return True
    if platform.node() in TEST_NODES:
        return False
    return True

skip_test = _skip_test()


SKIP_LOCAL_TEST_REASON = "These are tests for local test"


def get_test_folder(prefix="TEST"):
    return mkdtemp(prefix=prefix)


def get_test_media_folder():
    return get_test_folder("TEST_MEDIA")
