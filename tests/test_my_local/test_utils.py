import datetime
from collections import OrderedDict
import numpy as np

from unittest import TestCase
from image_upload.utils import (
    deep_np_to_string, deep_eq, deep_convert_ordereddict)
from tests.utils import mock


class DeepEqTest(TestCase):

    def test_dict(self):
        x1, y1 = ({'a': 'b'}, {'a': 'b'})
        self.assertTrue(deep_eq(x1, y1))

        x2, y2 = ({'a': 'b'}, {'b': 'a'})
        self.assertFalse(deep_eq(x2, y2))

    def test_embeded_dict(self):
        x3, y3 = ({'a': {'b': 'c'}}, {'a': {'b': 'c'}})
        self.assertTrue(deep_eq(x3, y3))
        x4, y4 = ({'c': 't', 'a': {'b': 'c'}}, {'a': {'b': 'n'}, 'c': 't'})
        self.assertFalse(deep_eq(x4, y4))

    def test_list_as_dict_value(self):
        x5, y5 = ({'a': [1, 2, 3]}, {'a': [1, 2, 3]})
        self.assertTrue(deep_eq(x5, y5))
        x6, y6 = ({'a': [1, 'b', 8]}, {'a': [2, 'b', 8]})
        self.assertFalse(deep_eq(x6, y6))

    def test_string(self):
        x7, y7 = ('a', 'a')
        self.assertTrue(deep_eq(x7, y7))

    def test_list(self):
        x8, y8 = (['p', 'n', ['asdf']], ['p', 'n', ['asdf']])
        self.assertTrue(deep_eq(x8, y8))

        x9, y9 = (['p', 'n', ['asdf', ['omg']]], ['p', 'n', ['asdf', ['nowai']]])
        self.assertFalse(deep_eq(x9, y9))

    def test_int(self):
        x10, y10 = (1, 2)
        self.assertFalse(deep_eq(x10, y10))

    def test_tuple_comprehension(self):
        self.assertTrue(
            deep_eq((str(p) for p in range(10)), (str(p) for p in range(10))))

    def test_range(self):
        self.assertEqual(str(deep_eq(range(4), range(4))), "True")
        self.assertTrue(deep_eq(range(100), range(100)))
        self.assertFalse(deep_eq(range(2), range(5)))

    def test_datatime(self):
        from datetime import datetime as dt

        d1, d2 = (dt.now(), dt.now() + datetime.timedelta(seconds=4))
        self.assertFalse(deep_eq(d1, d2))

        self.assertTrue(deep_eq(d1, d2,
                                datetime_fudge=datetime.timedelta(seconds=5)))

    def test_ordereddict(self):
        from collections import OrderedDict
        x11, y11 = ({'a': 'b', 'c': 'd'}, OrderedDict({'c': 'd', 'a': 'b'}))
        self.assertTrue(deep_eq(x11, y11))

        x12, y12 = ({'a': 'b', 'c': [{'a': 1, 'b': 2}]},
                    OrderedDict({'c': [{'b': 2, 'a': 1}], 'a': 'b'}))
        self.assertTrue(deep_eq(x12, y12))

        x13, y13 = ({'a': 'b', 'c': [{'a': 2, 'b': 2}]},
                    OrderedDict({'c': [{'b': 2, 'a': 1}], 'a': 'b'}))
        self.assertFalse(deep_eq(x13, y13))

    def test_numpy_array(self):
        x = np.array(
            [[1, 2, 3],
            [4, 5, 6]]
        )
        y = np.array(
            [[1, 2, 3],
            [4, 5, 6]]
        )
        self.assertTrue(deep_eq(x, y))

        y = np.array(
            [[4, 5, 6],
            [1, 2, 3]]
        )
        self.assertFalse(deep_eq(x, y))

        y = np.array(
            [[1, 2], [3, 4], [5, 6]]
        )
        self.assertFalse(deep_eq(x, y))

    def test_numpy_array_with_nan(self):
        x = np.array(
            [[1, 2, np.nan],
            [4, 5, 6]]
        )
        y = np.array(
            [[1, 2, np.nan],
            [4, 5, 6]]
        )
        self.assertTrue(deep_eq(x, y))

    def test_numpy_matrix(self):
        x = np.matrix(
             [[0,  95, 170],
              [0,   0,   0],
              [0,   0,   1]])
        y = np.matrix(
                [[0, 95, 170],
                 [0, 0, 0],
                 [0, 0, 1]])

        self.assertTrue(deep_eq(x, y))

        y = np.matrix(
                [[0, 95, 170],
                 [0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 1]])

        self.assertFalse(deep_eq(x, y))
        with self.assertRaises(AssertionError):
            deep_eq(x, y, _assert=True)

    def test_numpy_matrix_with_nan(self):
        x = np.matrix(
            [[0., 14., 17., np.nan, 27., 36.],
             [0., 18., 24., 25., 26., 37.],
             [0., 14., 26., np.nan, 33., np.nan]])
        y = np.matrix(
            [[0., 14., 17., np.nan, 27., 36.],
             [0., 18., 24., 25., 26., 37.],
             [0., 14., 26., np.nan, 33., np.nan]])

        self.assertTrue(deep_eq(x, y))

        y = np.matrix(
            [[0., 14., 17., np.nan, 27., 36.],
             [0., 18., 24., 25., 26., 37.],
             [0., 14., 26., np.nan, 33., 0]])
        self.assertFalse(deep_eq(x, y))

    def test_numpy_matrix_array(self):
        x = np.array(
            [[0., 14., 17., np.nan, 27., 36.],
             [0., 18., 24., 25., 26., 37.],
             [0., 14., 26., np.nan, 33., np.nan]])
        y = np.matrix(
            [[0., 14., 17., np.nan, 27., 36.],
             [0., 18., 24., 25., 26., 37.],
             [0., 14., 26., np.nan, 33., np.nan]])

        self.assertFalse(deep_eq(x, y))

    def test_np_allclose_raise(self):
        x = np.matrix(
            [[0., 14., 17., np.nan, 27., 36.],
             [0., 18., 24., 25., 26., 37.],
             [0., 14., 26., np.nan, 33., np.nan]])
        y = np.matrix(
            [[0., 14., 17., np.nan, 27., 36.],
             [0., 18., 24., 25., 26., 37.],
             [0., 14., 26., np.nan, 33., np.nan]])

        def allclose_side_effect(a, b, rtol=1.e-5, atol=1.e-8, equal_nan=False):
            raise RuntimeError()
        with mock.patch("numpy.allclose") as mock_all_close:
            mock_all_close.side_effect = allclose_side_effect
            with self.assertRaises(RuntimeError):
                deep_eq(x, y)


class TestDeepConvertOrdereddict(TestCase):
    def test_string(self):
        x = "abcd"
        y = "abcd"
        self.assertEqual(deep_convert_ordereddict(x), y)

    def test_bytes_string(self):
        x = b"abcd"
        y = b"abcd"
        self.assertEqual(deep_convert_ordereddict(x), y)

    def test_list(self):
        x = ["b", "a", "c", "d"]
        y = ["b", "a", "c", "d"]
        self.assertEqual(deep_convert_ordereddict(x), y)

    def test_dict(self):
        x = {"a": 1, "b": 2}
        y = {"b": 2, "a": 1}
        self.assertEqual(deep_convert_ordereddict(x), deep_convert_ordereddict(y))

        y = {"b": 3, "a": 1}
        self.assertNotEqual(
            deep_convert_ordereddict(x), deep_convert_ordereddict(y))

    def test_dict_embeded_in_dict(self):
        x = {"b": 1, "a": {"d": 3, "c": 4}}
        x_converted = deep_convert_ordereddict(x)

        y = OrderedDict([("a", OrderedDict([("c", 4), ("d", 3)])), ("b", 1)])
        self.assertEqual(x_converted, y)

        y = OrderedDict([("a", OrderedDict([("d", 3), ("c", 4)])), ("b", 1)])
        self.assertNotEqual(x_converted, y)

    def test_dict_embeded_in_list(self):
        x = [2, 1, {"b": 1, "a": {"d": 3, "c": 4}}]
        x_converted = deep_convert_ordereddict(x)

        y = [2, 1, OrderedDict([("a", OrderedDict(
            [("c", 4), ("d", 3)])), ("b", 1)])]
        self.assertEqual(x_converted, y)

        y = [2, 1, OrderedDict([("a", OrderedDict(
            [("d", 3), ("c", 4)])), ("b", 1)])]
        self.assertNotEqual(x_converted, y)

    def test_dict_embeded_in_tuple(self):
        x = (2, 1, {"b": 1, "a": {"d": 3, "c": 4}})
        x_converted = deep_convert_ordereddict(x)

        y = (2, 1, OrderedDict([("a", OrderedDict(
            [("c", 4), ("d", 3)])), ("b", 1)]))
        self.assertEqual(x_converted, y)

        y = (2, 1, OrderedDict([("a", OrderedDict(
            [("d", 3), ("c", 4)])), ("b", 1)]))
        self.assertNotEqual(x_converted, y)

    def test_not_deep_eq_raise(self):
        with mock.patch("image_upload.utils.deep_eq") as mock_deep_eq:
            mock_deep_eq.return_value = False
            x = b"abcd"
            with self.assertRaises(ValueError):
                deep_convert_ordereddict(x)


class TestDeepNpToString(TestCase):
    m = np.matrix(
        [[0., 14., 17., np.nan, 27., 36.],
         [0., 18., 24., 25., 26., 37.],
         [0., 14., 26., np.nan, 33., np.nan]])
    result = (
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,@'
        b'\x00\x00\x00\x00\x00\x001@\x00\x00\x00\x00\x00\x00\xf8\x7f'
        b'\x00\x00\x00\x00\x00\x00;@\x00\x00\x00\x00\x00\x00B@'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x002@'
        b'\x00\x00\x00\x00\x00\x008@\x00\x00\x00\x00\x00\x009@\x00'
        b'\x00\x00\x00\x00\x00:@\x00\x00\x00\x00\x00\x80B@\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,@\x00\x00'
        b'\x00\x00\x00\x00:@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00'
        b'\x00\x00\x00\x80@@\x00\x00\x00\x00\x00\x00\xf8\x7f')

    large_x = np.arange(1, 10000, 1)
    large_z = np.arange(1, 10000, 1)
    large_y = np.arange(1, 10000, 1)
    large_y[20] = 1000

    def test_string(self):
        x = "abcd"
        self.assertEqual(deep_np_to_string(x), x)

    def test_bytes_string(self):
        x = b"abcd"
        self.assertEqual(deep_np_to_string(x), x)

    def test_list(self):
        x = ["b", "a", "c", "d"]
        self.assertEqual(deep_np_to_string(x), x)

    def test_np(self):
        self.assertEqual(deep_np_to_string(self.m), self.result)

    def test_np_embeded_in_dict(self):
        x = {"b": 1, "a": {"d": 3, "c": self.m}}
        x_converted = deep_np_to_string(x)
        y = {"b": 1, "a": {"d": 3, "c": self.result}}
        self.assertTrue(deep_eq(x_converted, y))

    def test_np_embeded_in_list_and_dict(self):
        x = [2, 1, {"b": 1, "a": {"d": 3, "c": self.m}}]
        x_converted = deep_np_to_string(x)
        self.assertEqual(x_converted[2]["a"]["c"], self.result)

    def test_np_embeded_in_tuple(self):
        x = (2, 1, self.m)
        x_converted = deep_np_to_string(x)
        y = (2, 1, self.result)
        self.assertEqual(x_converted, y)

    def test_large_np_array_not_partial(self):
        # make sure we are not using str(np.array) to get the string

        # Note: str(self.large_x) == str(self.large_y), which is not expected
        self.assertFalse(np.allclose(self.large_x, self.large_y))
        self.assertTrue(np.allclose(self.large_x, self.large_z))
        self.assertEqual(deep_np_to_string(self.large_x),
                         deep_np_to_string(self.large_z))
        self.assertNotEqual(deep_np_to_string(self.large_x),
                            deep_np_to_string(self.large_y))

    def test_large_np_array_embedded_in_dict_not_partial(self):
        x = {"b": 1, "a": {"d": 3, "c": self.large_x}}
        x_converted = deep_np_to_string(x)
        y = {"b": 1, "a": {"d": 3, "c": self.large_y}}
        z = {"b": 1, "a": {"d": 3, "c": self.large_z}}
        self.assertEqual(x_converted["a"]["c"], deep_np_to_string(self.large_x))
        self.assertFalse(deep_eq(x_converted, deep_np_to_string(y)))
        self.assertTrue(deep_eq(x_converted, deep_np_to_string(z)))

    def test_large_np_embeded_in_list_and_dict(self):
        x = [2, 1, {"b": 1, "a": {"d": 3, "c": self.large_x}}]
        x_converted = deep_np_to_string(x)
        self.assertEqual(x_converted[2]["a"]["c"], deep_np_to_string(self.large_x))
        self.assertEqual(x_converted[2]["a"]["c"], deep_np_to_string(self.large_z))
        self.assertNotEqual(x_converted[2]["a"]["c"],
                            deep_np_to_string(self.large_y))

    def test_large_np_embeded_in_tuple(self):
        x = (2, 1, self.large_x)
        x_converted = deep_np_to_string(x)
        y = (2, 1, self.large_y)
        z = (2, 1, self.large_z)

        self.assertEqual(x_converted[2], deep_np_to_string(self.large_x))
        self.assertEqual(x_converted, deep_np_to_string(z))
        self.assertNotEqual(x_converted, deep_np_to_string(y))

    def test_large_np_embeded_in_tuple_of_tuple(self):
        x = (2, 1, (3, self.large_x))
        x_converted = deep_np_to_string(x)
        y = (2, 1, (3, self.large_y))
        z = (2, 1, (3, self.large_z))

        self.assertIsInstance(x_converted[2], tuple)
        self.assertEqual(x_converted[2][1], deep_np_to_string(self.large_x))
        self.assertEqual(x_converted, deep_np_to_string(z))
        self.assertNotEqual(x_converted, deep_np_to_string(y))
