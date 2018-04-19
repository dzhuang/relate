from __future__ import absolute_import, unicode_literals


from django.test import TestCase

from tests.base_test_mixins import SingleCourseTestMixin
import traceback
from contextlib import contextmanager
import unittest

import pytest
#from case import Mock, call, patch, skip
from relate.celery import app

from tests.utils import mock
from celery import states, uuid
from celery.backends.base import SyncBackendMixin
from celery.exceptions import (CPendingDeprecationWarning,
                               ImproperlyConfigured, IncompleteStream,
                               TimeoutError)
from celery.result import (AsyncResult, EagerResult, GroupResult, ResultSet,
                           assert_will_not_block, result_from_tuple)
from celery.utils.serialization import pickle

PYTRACEBACK = """\
Traceback (most recent call last):
  File "foo.py", line 2, in foofunc
    don't matter
  File "bar.py", line 3, in barfunc
    don't matter
Doesn't matter: really!\
"""


def mock_task(name, state, result, traceback=None):
    return {
        'id': uuid(), 'name': name, 'state': state,
        'result': result, 'traceback': traceback,
    }


def save_result(app, task):
    traceback = task.get('traceback') or 'Some traceback'
    if task['state'] == states.SUCCESS:
        app.backend.mark_as_done(task['id'], task['result'])
    elif task['state'] == states.RETRY:
        app.backend.mark_as_retry(
            task['id'], task['result'], traceback=traceback,
        )
    else:
        app.backend.mark_as_failure(
            task['id'], task['result'], traceback=traceback,
        )


def make_mock_group(app, size=10):
    tasks = [mock_task('ts%d' % i, states.SUCCESS, i) for i in range(size)]
    [save_result(app, task) for task in tasks]
    return [app.AsyncResult(task['id']) for task in tasks]


class _MockBackend:
    def add_pending_result(self, *args, **kwargs):
        return True

    def wait_for_pending(self, *args, **kwargs):
        return True


class AsyncResultMixin(object):

    def setup(self):
        super(AsyncResultMixin, self).setUp()
        self.app.conf.result_cache_max = 100
        self.app.conf.result_serializer = 'pickle'
        self.task1 = mock_task('task1', states.SUCCESS, 'the')
        self.task2 = mock_task('task2', states.SUCCESS, 'quick')
        self.task3 = mock_task('task3', states.FAILURE, KeyError('brown'))
        self.task4 = mock_task('task3', states.RETRY, KeyError('red'))
        self.task5 = mock_task(
            'task3', states.FAILURE, KeyError('blue'), PYTRACEBACK,
        )
        for task in (self.task1, self.task2,
                     self.task3, self.task4, self.task5):
            save_result(self.app, task)

        @self.app.task(shared=False)
        def mytask():
            pass
        self.mytask = mytask

    def test_successful(self):
        ok_res = self.app.AsyncResult(self.task1['id'])
        nok_res = self.app.AsyncResult(self.task3['id'])
        nok_res2 = self.app.AsyncResult(self.task4['id'])

        assert ok_res.successful()
        assert not nok_res.successful()
        assert not nok_res2.successful()

        pending_res = self.app.AsyncResult(uuid())
        assert not pending_res.successful()

    def test_raising(self):
        notb = self.app.AsyncResult(self.task3['id'])
        withtb = self.app.AsyncResult(self.task5['id'])

        # with pytest.raises(KeyError):
        #     notb.get()
        # try:
        #     withtb.get()
        # except KeyError:
        #     tb = traceback.format_exc()
        #     assert '  File "foo.py", line 2, in foofunc' not in tb
        #     assert '  File "bar.py", line 3, in barfunc' not in tb
        #     assert 'KeyError:' in tb
        #     assert "'blue'" in tb
        # else:
        #     raise AssertionError('Did not raise KeyError.')

    def test_str(self):
        ok_res = self.app.AsyncResult(self.task1['id'])
        ok2_res = self.app.AsyncResult(self.task2['id'])
        nok_res = self.app.AsyncResult(self.task3['id'])
        assert str(ok_res) == self.task1['id']
        assert str(ok2_res) == self.task2['id']
        assert str(nok_res) == self.task3['id']

        pending_id = uuid()
        pending_res = self.app.AsyncResult(pending_id)
        assert str(pending_res) == pending_id

    def test_repr(self):
        ok_res = self.app.AsyncResult(self.task1['id'])
        ok2_res = self.app.AsyncResult(self.task2['id'])
        nok_res = self.app.AsyncResult(self.task3['id'])
        assert repr(ok_res) == '<AsyncResult: %s>' % (self.task1['id'],)
        assert repr(ok2_res) == '<AsyncResult: %s>' % (self.task2['id'],)
        assert repr(nok_res) == '<AsyncResult: %s>' % (self.task3['id'],)

        pending_id = uuid()
        pending_res = self.app.AsyncResult(pending_id)
        assert repr(pending_res) == '<AsyncResult: %s>' % (pending_id,)

    def test_hash(self):
        assert (hash(self.app.AsyncResult('x0w991')) ==
                hash(self.app.AsyncResult('x0w991')))
        assert (hash(self.app.AsyncResult('x0w991')) !=
                hash(self.app.AsyncResult('x1w991')))

    def test_get_traceback(self):
        ok_res = self.app.AsyncResult(self.task1['id'])
        nok_res = self.app.AsyncResult(self.task3['id'])
        nok_res2 = self.app.AsyncResult(self.task4['id'])
        assert not ok_res.traceback
        assert nok_res.traceback
        assert nok_res2.traceback

        pending_res = self.app.AsyncResult(uuid())
        assert not pending_res.traceback

    def test_get__backend_gives_None(self):
        res = self.app.AsyncResult(self.task1['id'])
        res.backend.wait_for = mock.Mock(name='wait_for')
        res.backend.wait_for.return_value = None
        assert res.get() is None

    def test_get(self):
        ok_res = self.app.AsyncResult(self.task1['id'])
        ok2_res = self.app.AsyncResult(self.task2['id'])
        nok_res = self.app.AsyncResult(self.task3['id'])
        nok2_res = self.app.AsyncResult(self.task4['id'])

        callback = mock.Mock(name='callback')

        assert ok_res.get(callback=callback) == 'the'
        callback.assert_called_with(ok_res.id, 'the')
        assert ok2_res.get() == 'quick'
        # with pytest.raises(KeyError):
        #     nok_res.get()
        assert nok_res.get(propagate=False)
        assert isinstance(nok2_res.result, KeyError)
        assert ok_res.info == 'the'

    def test_eq_ne(self):
        r1 = self.app.AsyncResult(self.task1['id'])
        r2 = self.app.AsyncResult(self.task1['id'])
        r3 = self.app.AsyncResult(self.task2['id'])
        assert r1 == r2
        assert r1 != r3
        assert r1 == r2.id
        assert r1 != r3.id

    def test_ready(self):
        oks = (self.app.AsyncResult(self.task1['id']),
               self.app.AsyncResult(self.task2['id']),
               self.app.AsyncResult(self.task3['id']))
        assert all(result.ready() for result in oks)
        assert not self.app.AsyncResult(self.task4['id']).ready()

        assert not self.app.AsyncResult(uuid()).ready()


class MonitorTaskTest(SingleCourseTestMixin, TestCase):
    def setUp(self):
        super(MonitorTaskTest, self).setUp()
        # self.app.conf.result_cache_max = 100
        # self.app.conf.result_serializer = 'pickle'
        self.task1 = mock_task('task1', states.SUCCESS, 'the')
        self.task2 = mock_task('task2', states.SUCCESS, 'quick')
        self.task3 = mock_task('task3', states.FAILURE, KeyError('brown'))
        self.task4 = mock_task('task3', states.RETRY, KeyError('red'))
        self.task5 = mock_task(
            'task3', states.FAILURE, KeyError('blue'), PYTRACEBACK,
        )
        for task in (self.task1, self.task2,
                     self.task3, self.task4, self.task5):
            save_result(app, task)

    def get_monitor_url(self, task_id):
        from django.urls import reverse
        return reverse("relate-monitor_task", kwargs={"task_id": task_id})

    def test(self):
        with self.temporarily_switch_to_user(self.instructor_participation.user):
            resp = self.c.get(self.get_monitor_url(self.task1['id']))
            self.assertEqual(resp.status_code, 200)
