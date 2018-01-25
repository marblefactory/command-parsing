import unittest
from parsing.parse_action import *
from actions.interaction import *
from actions.move import *
from actions.location import *


class CompositeTestCase(unittest.TestCase):
    def test_parses_then(self):
        s = 'go left then go right'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            Move(Speed.NORMAL, Directional(MoveDirection.RIGHT), None),
        ]

        assert composite().parse(s).parsed == Composite(expected_actions)

    def test_parses_and(self):
        s = 'go left and pick up the rock'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert composite().parse(s).parsed == Composite(expected_actions)

    def test_parses_and_then(self):
        s = 'go left and then pick up the rock'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert composite().parse(s).parsed == Composite(expected_actions)

    def test_removes_non_parses(self):
        """
        Tests that single action parses that fail are not included in the final composite action.
        """
        s = 'go left and NAN then pick up the rock'.split()

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert composite().parse(s).parsed == Composite(expected_actions)

    def test_failure(self):
        """
        Tests the composite parser fails if it couldn't find 'then' or 'and'.
        """
        s = 'nothing to see here'.split()
        assert composite().parse(s) is None
