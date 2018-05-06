import unittest
from actions.question import *
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

    def test_parse_i(self):
        s = pre_process('where am i')
        assert action().parse(s).parsed == LocationQuestion()


class GuardsQuestionTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('can you see any guards')
        assert action().parse(s).parsed == GuardsQuestion()

    def test_parses_god_as_guard(self):
        s = pre_process('can you see any gods')
        assert action().parse(s).parsed == GuardsQuestion()

    def test_security(self):
        s = pre_process('can you see any security')
        assert action().parse(s).parsed == GuardsQuestion()


class SurroundingsTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('what can you see around you')
        assert action().parse(s).parsed == SurroundingsQuestion()


class SeeObjectTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('can you see a rock nearby')
        assert action().parse(s).parsed == SeeObjectQuestion('rock')

    def test_are_there(self):
        s = pre_process('are there any rocks nearby')
        assert action().parse(s).parsed == SeeObjectQuestion('rock')

    def test_you_see(self):
        s = pre_process('you see any rocks')
        assert action().parse(s).parsed == SeeObjectQuestion('rock')

    def test_around_you(self):
        s = pre_process('are there any rocks around you')
        assert action().parse(s).parsed == SeeObjectQuestion('rock')

    def test_other_nouns(self):
        s = pre_process('are there any submarines around you')
        r = action().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('submarines'))

    def test_other_nouns_can_see1(self):
        s = pre_process('can you see any submarines')
        assert action().parse(s).parsed == SeeObjectQuestion('submarines')

    def test_other_nouns_can_see2(self):
        s = pre_process('are there any submarines you can see')
        assert action().parse(s).parsed == SeeObjectQuestion('submarines')

    def test_can_you_see(self):
        s = pre_process('can you see any rocks')
        assert action().parse(s).parsed == SeeObjectQuestion('rock')

    def test_any_you_can_see(self):
        s = pre_process('are there any hammers you can see')
        r = action().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('hammer'))

    def test_see_can(self):
        s = pre_process('can you see any cans')
        assert action().parse(s).parsed == SeeObjectQuestion('can')

    def test_nan_is_nothing(self):
        s = pre_process('nan')
        assert action().parse(s).is_failure()

    def test_terminal(self):
        s = pre_process('can you see a terminal')
        self.assertEqual(action().parse(s).parsed, SeeObjectQuestion('terminal'))

    def test_where_are(self):
        s = pre_process('where are the rocks')
        r = action().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('rock'))

    def test_singular(self):
        s = pre_process('where are the rock')
        r = action().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('rock'))


class TimeRemainingTestCase(unittest.TestCase):
    def test_parse_longer(self):
        s = pre_process('how much longer is there')
        r = action().parse(s).parsed
        self.assertEqual(r, TimeRemainingQuestion())

    def test_parse_time_left(self):
        s = pre_process('how much time is left')
        assert action().parse(s).parsed == TimeRemainingQuestion()

    def test_parse_long_left(self):
        s = pre_process('how long have we got left')
        assert action().parse(s).parsed == TimeRemainingQuestion()

    def test_parse_left_clock(self):
        s = pre_process("what's left on the clock")
        assert action().parse(s).parsed == TimeRemainingQuestion()

    def test_parse_remaining(self):
        s = pre_process('how much time is remaining')
        assert action().parse(s).parsed == TimeRemainingQuestion()

    def test_parse_clock(self):
        s = pre_process('what does the clock say')
        assert action().parse(s).parsed == TimeRemainingQuestion()

    def test_more_time(self):
        s = pre_process('how much more time is there')
        assert action().parse(s).parsed == TimeRemainingQuestion()
