import unittest
from utils import split_list, partial_class, compose


class SplitListTestCase(unittest.TestCase):
    def test_split_empty(self):
        assert split_list([], [1]) == []

    def test_split_single_elem(self):
        assert split_list([2], [2]) == []

    def test_split(self):
        assert split_list([1, 2, 3, 4, 2, 5, 2, 7], [2]) == [[1], [3, 4], [5], [7]]

    def test_split_first(self):
        assert split_list([1, 2, 3], [1]) == [[2, 3]]

    def test_split_last(self):
        assert split_list([1, 2, 3], [3]) == [[1, 2]]

    def test_split_next_to(self):
        assert split_list([1, 4, 2, 2, 3], [2]) == [[1, 4], [3]]

    def test_split_multiple_separators(self):
        assert split_list([1, 4, 2, 3, 1, 1], [4, 3]) == [[1], [2], [1, 1]]


class PartialClassTestCase(unittest.TestCase):
    class TestClass:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    def test_sets_properties(self):
        bound_x = partial_class(PartialClassTestCase.TestClass, x='X')
        obj = bound_x(y='Y')

        assert obj.x == 'X'
        assert obj.y == 'Y'
        assert isinstance(obj, PartialClassTestCase.TestClass)

    def test_isinstance(self):
        bound_x = partial_class(PartialClassTestCase.TestClass, x='X')
        obj = bound_x(y='Y')

        assert obj.x == 'X'
        assert obj.y == 'Y'
        assert isinstance(obj, PartialClassTestCase.TestClass)
