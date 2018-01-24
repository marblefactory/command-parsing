import unittest
from parsing.parse_interaction import *
from actions.location import *


class ThroughDoorTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'go through the door'.split()
        assert through_door().parse(s).parsed == ThroughDoor()

    def test_missing_door(self):
        s = 'go through'.split()
        assert through_door().parse(s).parsed == ThroughDoor()


class PickUpTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'pick up the rock on your left'.split()
        assert pick_up().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_direction_defaults_to_vicinity(self):
        s = 'pick up the hammer'.split()
        assert pick_up().parse(s).parsed == PickUp('hammer', ObjectRelativeDirection.VICINITY)


class ThrowTestCase(unittest.TestCase):
    def test_parse_directional(self):
        s = 'chuck to your left'.split()

        expected_loc = Directional(MoveDirection.LEFT)
        assert throw().parse(s).parsed == Throw(expected_loc)

    def test_parse_positional(self):
        s = 'throw to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert throw().parse(s).parsed == Throw(expected_loc)

    def test_defaults_forwards(self):
        s = 'throw'.split()

        expected_loc = Directional(MoveDirection.FORWARDS)
        assert throw().parse(s).parsed == Throw(expected_loc)

    def test_fails(self):
        s = 'what is going on'.split()

        assert throw().parse(s) is None
