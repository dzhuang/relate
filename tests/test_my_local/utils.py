from django.conf import settings
from tempfile import mkdtemp

def _skip_test():

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

    from plugins.latex.utils import get_mongo_db
    import mongomock
    if not isinstance(get_mongo_db(), mongomock.database.Database):
        print("To protected your production data for being deleted by "
              "tests, you must configure the test RELATE_MONGO_CLIENT_PATH "
              "with a directory named 'mongomock.MongoClient', otherwise the "
              "tests will be skipped!")

        return True

    return False

skip_test = _skip_test()


SKIP_LOCAL_TEST_REASON = "These are tests for local test"


def get_test_folder(prefix="TEST"):
    return mkdtemp(prefix=prefix)


def get_test_media_folder():
    return get_test_folder("TEST_MEDIA")
