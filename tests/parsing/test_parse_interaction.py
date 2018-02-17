import unittest
from parsing.parse_interaction import interaction_object_name
from parsing.parse_action import action
from actions.interaction import *
from actions.location import *


class InteractionObjectTestCase(unittest.TestCase):
    def test_rope_as_rock(self):
        s = 'rope'.split()
        assert interaction_object_name().parse(s).parsed == 'rock'


class ThroughDoorTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'go through the door'.split()
        assert action().parse(s).parsed == ThroughDoor()

    def test_missing_door(self):
        s = 'go through'.split()
        assert action().parse(s).parsed == ThroughDoor()


class PickUpTestCase(unittest.TestCase):
    def test_parse_pick_up(self):
        s = 'pick up the rock on your left'.split()
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_parse_take(self):
        s = 'take the rock on your left'.split()
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_direction_defaults_to_vicinity(self):
        s = 'pick up the hammer'.split()
        assert action().parse(s).parsed == PickUp('hammer', ObjectRelativeDirection.VICINITY)

    def test_pick_up_fails_if_no_object(self):
        s = 'pick up'.split()
        assert action().parse(s) is None

    def test_take_fails_if_no_object1(self):
        s = 'take the on your left'.split()
        assert type(action().parse(s)) != PickUp


class ThrowTestCase(unittest.TestCase):
    def test_parse_directional(self):
        s = 'chuck to your left'.split()

        expected_loc = Directional(MoveDirection.LEFT)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_parse_positional(self):
        s = 'throw to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_throw_behind_object(self):
        s = 'throw behind the desk'.split()
        assert action().parse(s).parsed == Throw(Behind('desk'))

    def test_defaults_forwards(self):
        s = 'throw'.split()

        expected_loc = Directional(MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Throw(expected_loc)


class HackTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'hack the terminal on your left'.split()
        assert action().parse(s).parsed == Hack('terminal', ObjectRelativeDirection.LEFT)

    def test_direction_defaults_to_vicinity(self):
        s = 'hack the camera'.split()
        assert action().parse(s).parsed == Hack('camera', ObjectRelativeDirection.VICINITY)

    def test_hacked_as_hack(self):
        s = 'hacked the camera'.split()
        assert action().parse(s).parsed == Hack('camera', ObjectRelativeDirection.VICINITY)

    def test_have_as_hack(self):
        s = 'have the server'.split()
        assert action().parse(s).parsed == Hack('server', ObjectRelativeDirection.VICINITY)

    def test_fails_if_no_object1(self):
        s = 'hack'.split()
        assert action().parse(s) is None

    def test_fails_if_no_object2(self):
        s = 'hack something'.split()
        assert action().parse(s) is None
