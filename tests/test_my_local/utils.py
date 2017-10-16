import os
import platform
from django.conf import settings
from tempfile import mkdtemp

TEST_NODES = ["Dzhuang-surface", "OfficeZD", "dzhuang-PC"]


def _skip_test():
    if not getattr(settings, "USING_LOCAL_TEST_SETTINGS", None):
        return True

    mongo_db_name =  getattr(settings, "RELATE_MONGODB_NAME", None)
    if not mongo_db_name:
        # Because this will use default name, DANGEROUS
        return True

    if not mongo_db_name.startswith("test_"):
        # Because this might use default name, DANGEROUS
        return True

    uri = getattr(settings, "RELATE_MONGO_URI", None)
    if uri is not None:
        return True

    if platform.node() in TEST_NODES:
        if os.path.split(settings.SENDFILE_ROOT)[-1] == "test_protected":
            return False
        else:
            print("To protected your production data for being deleted by "
                  "tests, you must configure the test SENDFILE_ROOT "
                  "with a directory named 'test_protected', otherwise the "
                  "tests will be skipped!")
    return True

skip_test = _skip_test()


SKIP_LOCAL_TEST_REASON = "These are tests for local test"


def get_test_folder(prefix="TEST"):
    return mkdtemp(prefix=prefix)


def get_test_media_folder():
    return get_test_folder("TEST_MEDIA")
