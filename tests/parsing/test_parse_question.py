import unittest
from actions.question import *
from parsing.pre_processing import pre_process
from parsing.parse_action import statement


class InventoryQuestionTestCase(unittest.TestCase):
    def test_parse_carry(self):
        s = pre_process('what are you carrying')
        assert statement().parse(s).parsed == InventoryContentsQuestion()

    def test_parse_hold(self):
        s = pre_process('what are you holding')
        assert statement().parse(s).parsed == InventoryContentsQuestion()

    def test_fails(self):
        s = pre_process('what')
        assert statement().parse(s).is_failure()

    def test_you_holding(self):
        s = pre_process('you holding')
        r = statement().parse(s).parsed
        self.assertEqual(r, InventoryContentsQuestion())


class LocationQuestionTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('where are you')
        assert statement().parse(s).parsed == LocationQuestion()

    def test_parse_i(self):
        s = pre_process('where am i')
        assert statement().parse(s).parsed == LocationQuestion()


class GuardsQuestionTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('can you see any guards')
        assert statement().parse(s).parsed == GuardsQuestion()

    def test_parses_god_as_guard(self):
        s = pre_process('can you see any gods')
        assert statement().parse(s).parsed == GuardsQuestion()

    def test_security(self):
        s = pre_process('can you see any security')
        assert statement().parse(s).parsed == GuardsQuestion()


class SurroundingsTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('what can you see around you')
        assert statement().parse(s).parsed == SurroundingsQuestion()

    def test_look(self):
        s = pre_process('look left')
        r = statement().parse(s).parsed
        self.assertEqual(r, SurroundingsQuestion())

    def test_whats_in_room(self):
        s = pre_process('whats in the room')
        r = statement().parse(s).parsed
        self.assertEqual(r, SurroundingsQuestion())


class SeeObjectTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('can you see a rock nearby')
        assert statement().parse(s).parsed == SeeObjectQuestion('rock')

    def test_are_there(self):
        s = pre_process('are there any rocks nearby')
        assert statement().parse(s).parsed == SeeObjectQuestion('rock')

    def test_you_see(self):
        s = pre_process('you see any rocks')
        assert statement().parse(s).parsed == SeeObjectQuestion('rock')

    def test_around_you(self):
        s = pre_process('are there any rocks around you')
        assert statement().parse(s).parsed == SeeObjectQuestion('rock')

    def test_other_nouns(self):
        s = pre_process('are there any submarines around you')
        r = statement().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('submarines'))

    def test_other_nouns_can_see1(self):
        s = pre_process('can you see any submarines')
        assert statement().parse(s).parsed == SeeObjectQuestion('submarines')

    def test_other_nouns_can_see2(self):
        s = pre_process('are there any submarines you can see')
        assert statement().parse(s).parsed == SeeObjectQuestion('submarines')

    def test_can_you_see(self):
        s = pre_process('can you see any rocks')
        assert statement().parse(s).parsed == SeeObjectQuestion('rock')

    def test_any_you_can_see(self):
        s = pre_process('are there any hammers you can see')
        r = statement().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('hammer'))

    def test_see_can(self):
        s = pre_process('can you see any cans')
        assert statement().parse(s).parsed == SeeObjectQuestion('can')

    def test_nan_is_nothing(self):
        s = pre_process('nan')
        assert statement().parse(s).is_failure()

    def test_terminal(self):
        s = pre_process('can you see a terminal')
        self.assertEqual(statement().parse(s).parsed, SeeObjectQuestion('terminal'))

    def test_where_are(self):
        s = pre_process('where are the rocks')
        r = statement().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('rock'))

    def test_singular(self):
        s = pre_process('where are the rock')
        r = statement().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('rock'))

    def test_find(self):
        s = pre_process('find a rock')
        r = statement().parse(s).parsed
        self.assertEqual(r, SeeObjectQuestion('rock'))
