import unittest
from parsing.parse_action import *
from actions.action import *


class CompositeTestCase(unittest.TestCase):
    def test_parses_then(self):
        pass

    def test_parses_and(self):
        pass

    def test_parses_and_then(self):
        pass

    def test_removes_non_parses(self):
        """
        Tests that single action parses that fail are not included in the final composite action.
        """
        pass

    def test_failure(self):
        pass