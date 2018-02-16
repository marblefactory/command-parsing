import unittest
from parsing.parse_action import action
from actions.action import *
from actions.interaction import *
from actions.move import *
from actions.location import *


class StopTestCase(unittest.TestCase):
    def test_parses_stop(self):
        s = 'stop'.split()
        assert action().parse(s).parsed == Stop()

    def test_parses_freeze(self):
        s = 'freeze'.split()
        assert action().parse(s).parsed == Stop()

    def test_parses_halt(self):
        s = 'halt'.split()
        assert action().parse(s).parsed == Stop()

    def test_does_not_parse(self):
        s = 'does the end of the corridor'.split()
        assert type(action().parse(s).parsed) != Stop


class CompositeTestCase(unittest.TestCase):
    def test_parses_then(self):
        s = 'go left then go right'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            Move(Speed.NORMAL, Directional(MoveDirection.RIGHT), None),
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_parses_and(self):
        s = 'go left and pick up the rock'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_parses_and_then(self):
        s = 'go left and then pick up the rock'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_removes_non_parses(self):
        """
        Tests that single action parses that fail are not included in the final composite action.
        """
        s = 'go left and NAN then pick up the rock'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_failure(self):
        """
        Tests the composite parser fails if it couldn't find 'then' or 'and'.
        """
        s = 'nothing to see here'.split()
        assert action().parse(s) is None


class DontTestCase(unittest.TestCase):
    def test_no_parse(self):
        """
        Tests that if the player says "don't" no action is performed.
        """
        s = "don't go forwards".split()
        assert action().parse(s) is None
