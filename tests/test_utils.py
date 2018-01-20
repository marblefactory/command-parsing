import unittest
from utils import split_list


class SplitListTestCase(unittest.TestCase):

    def test_split_empty(self):
        assert split_list([], 1) == []

    def test_split_single_elem(self):
        assert split_list([2], 2) == []

    def test_split(self):
        assert split_list([1, 2, 3, 4, 2, 5], 2) == [[1], [3, 4], [5]]

    def test_split_first(self):
        assert split_list([1, 2, 3], 1) == [[2, 3]]

    def test_split_last(self):
        assert split_list([1, 2, 3], 3) == [[1, 2]]
