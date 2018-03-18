import unittest
from actions.question import InventoryContentsQuestion, LocationQuestion
from parsing.pre_processing import pre_process
from parsing.parse_action import action


class InventoryQuestionTestCase(unittest.TestCase):
    def test_parse_carry(self):
        s = pre_process('what are you carrying')
        assert action().parse(s).parsed == InventoryContentsQuestion()

    def test_parse_hold(self):
        s = pre_process('what are you holding')
        assert action().parse(s).parsed == InventoryContentsQuestion()

    def test_fails(self):
        s = pre_process('what')
        assert action().parse(s).is_failure()


class LocationQuestionTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('where are you')
        assert action().parse(s).parsed == LocationQuestion()