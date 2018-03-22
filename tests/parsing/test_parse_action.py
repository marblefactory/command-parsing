import unittest
from parsing.pre_processing import pre_process
from parsing.parse_action import action
from actions.action import *
from actions.interaction import *
from actions.move import *
from actions.location import *
from nltk.corpus import wordnet as wn


class StopTestCase(unittest.TestCase):
    def test_parses_stop(self):
        s = pre_process('stop')
        assert action().parse(s).parsed == Stop()

    def test_parses_freeze(self):
        s = pre_process('freeze')
        assert action().parse(s).parsed == Stop()

    def test_parses_halt(self):
        s = pre_process('halt')
        assert action().parse(s).parsed == Stop()


class CompositeTestCase(unittest.TestCase):
    def test_parses_then(self):
        s = pre_process('go left then go right')

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), None),
            Move(Speed.NORMAL, Directional(MoveDirection.RIGHT, Distance.MEDIUM), None),
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_parses_and(self):
        s = pre_process('go left and pick up the rock')

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_parses_and_then(self):
        s = pre_process('go left and then pick up the rock')

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_removes_non_parses(self):
        """
        Tests that single action parses that fail are not included in the final composite action.
        """
        s = pre_process('go left and NAN then pick up the rock')

        expected_actions = [
            Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), None),
            PickUp('rock', ObjectRelativeDirection.VICINITY)
        ]

        assert action().parse(s).parsed == Composite(expected_actions)

    def test_fails_if_only_then(self):
        s = pre_process('then')
        assert action().parse(s).is_failure()


class DontTestCase(unittest.TestCase):
    def test_no_parse(self):
        """
        Tests that if the player says "don't" no action is performed.
        """
        s = "don't go forwards".split()
        assert action().parse(s).is_failure()
