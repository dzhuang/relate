from __future__ import division

__copyright__ = "Copyright (C) 2017 Dong Zhuang, Andreas Kloeckner, Zesheng Wang"

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
import stat
import time
import errno
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from course.models import Course, Participation, ParticipationRole
from course.constants import participation_status

CREATE_SUPERUSER_KWARGS = {
    "username": "test_admin",
    "password": "test_admin",
    "email": "test_admin@example.com",
    "first_name": "Test",
    "last_name": "Admin"}

SINGLE_COURSE_SETUP_LIST = [
    {
        "course": {
            "identifier": "test-course",
            "name": "Test Course",
            "number": "CS123",
            "time_period": "Fall 2016",
            "hidden": False,
            "listed": True,
            "accepts_enrollment": True,
            "git_source": "git://github.com/inducer/relate-sample",
            "course_file": "course.yml",
            "events_file": "events.yml",
            "enrollment_approval_required": False,
            "enrollment_required_email_suffix": None,
            "from_email": "inform@tiker.net",
            "notify_email": "inform@tiker.net"},
        "participations": [
            {
                "role_identifier": "instructor",
                "user": {
                    "username": "test_instructor",
                    "password": "test_instructor",
                    "email": "test_instructor@example.com",
                    "first_name": "Test",
                    "last_name": "Instructor"},
                "status": participation_status.active
            },
            {
                "role_identifier": "ta",
                "user": {
                    "username": "test_ta",
                    "password": "test",
                    "email": "test_ta@example.com",
                    "first_name": "Test",
                    "last_name": "TA"},
                "status": participation_status.active
            },
            {
                "role_identifier": "student",
                "user": {
                    "username": "test_student",
                    "password": "test",
                    "email": "test_student@example.com",
                    "first_name": "Test",
                    "last_name": "Student"},
                "status": participation_status.active
            }
        ]
    }
]


def _call_windows_retry(func, args=(), retry_max=5, retry_delay=0.5):
    """
    It's possible to see spurious errors on Windows due to various things
    keeping a handle to the directory open (explorer, virus scanners, etc)
    So we try a few times if it fails with a known error.
    retry_delay is multiplied by the number of failed attempts to increase
    the likelihood of success in subsequent attempts.
    """

    retry_count = 0
    while True:
        try:
            func(*args)
        except OSError as e:
            # Error codes are defined in:
            # http://docs.python.org/2/library/errno.html#module-errno
            if e.errno not in (errno.EACCES, errno.ENOTEMPTY):
                raise

            if retry_count == retry_max:
                raise

            retry_count += 1

            print ('%s() failed for "%s". Reason: %s (%s). Retrying...' % \
                (func.__name__, args, e.strerror, e.errno))
            time.sleep(retry_count * retry_delay)
        else:
            # If no exception has been thrown it should be done
            break


def remove(path):
    """Removes the specified file, link, or directory tree.
    This is a replacement for shutil.rmtree that works better under
    windows. It does the following things:
     - check path access for the current user before trying to remove
     - retry operations on some known errors due to various things keeping
       a handle on file paths - like explorer, virus scanners, etc. The
       known errors are errno.EACCES and errno.ENOTEMPTY, and it will
       retry up to 5 five times with a delay of (failed_attempts * 0.5) seconds
       between each attempt.
    Note that no error will be raised if the given path does not exists.
    :param path: path to be removed
    """

    import shutil

    def _call_with_windows_retry(*args, **kwargs):
        try:
            _call_windows_retry(*args, **kwargs)
        except OSError as e:
            # The file or directory to be removed doesn't exist anymore
            if e.errno != errno.ENOENT:
                raise

    def _update_permissions(path):
        """Sets specified pemissions depending on filetype"""
        if os.path.islink(path):
            # Path is a symlink which we don't have to modify
            # because it should already have all the needed permissions
            return

        stats = os.stat(path)

        if os.path.isfile(path):
            mode = stats.st_mode | stat.S_IWUSR
        elif os.path.isdir(path):
            mode = stats.st_mode | stat.S_IWUSR | stat.S_IXUSR
        else:
            # Not supported type
            return

        _call_with_windows_retry(os.chmod, (path, mode))

    if not os.path.exists(path):
        return

    if os.path.isfile(path) or os.path.islink(path):
        # Verify the file or link is read/write for the current user
        _update_permissions(path)
        _call_with_windows_retry(os.remove, (path,))

    elif os.path.isdir(path):
        # Verify the directory is read/write/execute for the current user
        _update_permissions(path)

        # We're ensuring that every nested item has writable permission.
        for root, dirs, files in os.walk(path):
            for entry in dirs + files:
                _update_permissions(os.path.join(root, entry))
        _call_with_windows_retry(shutil.rmtree, (path,))


def force_remove_path(path):
    # shutil.rmtree won't work when delete course repo folder, on Windows,
    # so it cause all testcases failed.
    # Though this work around (copied from http://bit.ly/2usqGxr) still fails
    # for some tests, this enables **some other** tests on Windows.
    import stat
    def remove_readonly(func, path, _):  # noqa
        os.chmod(path, stat.S_IWRITE)
        func(path)

    import shutil
    if os.path.isdir(path):
        #shutil.rmtree(path, onerror=remove_readonly)
        remove(path)


class SuperuserCreateMixin(object):
    create_superuser_kwargs = CREATE_SUPERUSER_KWARGS

    @classmethod
    def setUpTestData(cls):  # noqa
        # Create superuser, without this, we cannot
        # create user, course and participation.
        cls.superuser = cls.create_superuser()
        cls.c = Client()
        super(SuperuserCreateMixin, cls).setUpTestData()

    @classmethod
    def tearDownClass(cls):  # noqa
        super(SuperuserCreateMixin, cls).tearDownClass()

    @classmethod
    def create_superuser(cls):
        return get_user_model().objects.create_superuser(
                                                **cls.create_superuser_kwargs)


class CoursesTestMixinBase(SuperuserCreateMixin):

    # A list of Dicts, each of which contain a course dict and a list of
    # participations. See SINGLE_COURSE_SETUP_LIST for the setup for one course.
    courses_setup_list = []

    @classmethod
    def setUpTestData(cls):  # noqa
        super(CoursesTestMixinBase, cls).setUpTestData()
        cls.n_courses = 0
        for course_setup in cls.courses_setup_list:
            if "course" not in course_setup:
                continue

            cls.n_courses += 1
            course_identifier = course_setup["course"]["identifier"]
            cls.remove_exceptionally_undelete_course_repos(course_identifier)
            cls.create_course(**course_setup["course"])
            course = Course.objects.get(identifier=course_identifier)
            if "participations" in course_setup:
                for participation in course_setup["participations"]:
                    create_user_kwargs = participation.get("user")
                    if not create_user_kwargs:
                        continue
                    role_identifier = participation.get("role_identifier")
                    if not role_identifier:
                        continue
                    cls.create_participation(
                        course=course,
                        create_user_kwargs=create_user_kwargs,
                        role_identifier=role_identifier,
                        status=participation.get("status",
                                                 participation_status.active)
                    )

                    # Remove superuser from participation for further test
                    # such as impersonate in auth module
                    if role_identifier == "instructor":
                        try:
                            superuser_participation = (
                                Participation.objects.get(user=cls.superuser))
                            Participation.delete(superuser_participation)
                        except Participation.DoesNotExist:
                            pass
        cls.course_qset = Course.objects.all()

    @classmethod
    def remove_exceptionally_undelete_course_repos(cls, course_identifier):
        # Remove undelete course repo folders coursed by
        # unexpected exceptions in previous tests.
        try:
            force_remove_path(os.path.join(settings.GIT_ROOT, course_identifier))
        except OSError:
            raise

    @classmethod
    def remove_course_repo(cls, course):
        from course.content import get_course_repo_path
        repo_path = get_course_repo_path(course)
        try:
            force_remove_path(repo_path)
        except OSError:
            pass

    @classmethod
    def tearDownClass(cls):
        cls.c.logout()
        # Remove repo folder for all courses
        for course in Course.objects.all():
            identifier = course.identifier
            course.delete()
            cls.remove_exceptionally_undelete_course_repos(identifier)
            #cls.remove_course_repo(course)
        super(CoursesTestMixinBase, cls).tearDownClass()

    @classmethod
    def create_participation(
            cls, course, create_user_kwargs, role_identifier, status):
        try:
            # TODO: why pop failed here?
            password = create_user_kwargs["password"]
        except:
            raise
        user, created = get_user_model().objects.get_or_create(**create_user_kwargs)
        if created:
            user.set_password(password)
            user.save()
        participation, p_created = Participation.objects.get_or_create(
            user=user,
            course=course,
            status=status
        )
        if p_created:
            role = ParticipationRole.objects.filter(
                course=course, identifier=role_identifier)
            participation.roles.set(role)
        return participation

    @classmethod
    def create_course(cls, **create_course_kwargs):
        cls.c.force_login(cls.superuser)
        cls.c.post(reverse("relate-set_up_new_course"), create_course_kwargs)


class SingleCourseTestMixin(CoursesTestMixinBase):
    courses_setup_list = SINGLE_COURSE_SETUP_LIST

    @classmethod
    def setUpTestData(cls):  # noqa
        super(SingleCourseTestMixin, cls).setUpTestData()
        cls.course = cls.course_qset.first()
        cls.instructor_participation = Participation.objects.filter(
            course=cls.course,
            roles__identifier="instructor",
            status=participation_status.active
        ).first()
        assert cls.instructor_participation

        cls.student_participation = Participation.objects.filter(
            course=cls.course,
            roles__identifier="student",
            status=participation_status.active
        ).first()
        assert cls.student_participation

        cls.ta_participation = Participation.objects.filter(
            course=cls.course,
            roles__identifier="ta",
            status=participation_status.active
        ).first()
        assert cls.ta_participation
        cls.c.logout()

    @classmethod
    def tearDownClass(cls):
        super(SingleCourseTestMixin, cls).tearDownClass()
