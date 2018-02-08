import unittest
from parsing.parse_action import action
from actions.interaction import *
from actions.location import *


class ThroughDoorTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'go through the door'.split()
        assert action().parse(s).parsed == ThroughDoor()

    def test_missing_door(self):
        s = 'go through'.split()
        assert action().parse(s).parsed == ThroughDoor()


class PickUpTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'pick up the rock on your left'.split()
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_direction_defaults_to_vicinity(self):
        s = 'pick up the hammer'.split()
        assert action().parse(s).parsed == PickUp('hammer', ObjectRelativeDirection.VICINITY)

    def test_fails_if_no_object(self):
        s = 'pick up'.split()
        assert action().parse(s) is None


class ThrowTestCase(unittest.TestCase):
    def test_parse_directional(self):
        s = 'chuck to your left'.split()

        expected_loc = Directional(MoveDirection.LEFT)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_parse_positional(self):
        s = 'throw to the next door'.split()

        print(action().parse(s).parsed)

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_defaults_forwards(self):
        s = 'throw'.split()

        expected_loc = Directional(MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_fails(self):
        s = 'what is going on'.split()
        assert action().parse(s) is None


class HackTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'hack the terminal on your left'.split()
        assert action().parse(s).parsed == Hack('terminal', ObjectRelativeDirection.LEFT)

    def test_direction_defaults_to_vicinity(self):
        s = 'hack the camera'.split()
        assert action().parse(s).parsed == Hack('camera', ObjectRelativeDirection.VICINITY)

    def test_fails_if_no_object(self):
        s = 'hack something'.split()
        assert action().parse(s) is None
