import unittest
from utils import split_list, PartialClassMixin
from functools import partial


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
    class TestClass(PartialClassMixin):
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __str__(self):
            return "x = {}, y = {}".format(self.x, self.y)

    def test_sets_properties(self):
        p = PartialClassTestCase.TestClass.partial_init()
        bound_x = partial(p, x='X')
        bound_y = bound_x(y='Y')

        assert bound_y.x == 'X'
        assert bound_y.y == 'Y'
        assert isinstance(bound_y, PartialClassTestCase.TestClass)
