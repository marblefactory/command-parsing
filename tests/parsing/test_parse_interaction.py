import unittest
from parsing.pre_processing import pre_process
from parsing.parse_action import action
from actions.interaction import *
from actions.location import *


class ThroughDoorTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('go through the door')
        assert action().parse(s).parsed == ThroughDoor(ObjectRelativeDirection.VICINITY)

    def test_missing_door(self):
        s = pre_process('go through')
        assert action().parse(s).parsed == ThroughDoor(ObjectRelativeDirection.VICINITY)

    def test_enter_room(self):
        s = pre_process('enter the room')
        assert action().parse(s).parsed == ThroughDoor(ObjectRelativeDirection.VICINITY)

    def test_enter(self):
        s = pre_process('enter')
        assert action().parse(s).parsed == ThroughDoor(ObjectRelativeDirection.VICINITY)

    def test_into(self):
        # Google mistakes 'enter' for 'into'.
        s = pre_process('into to the room')
        assert action().parse(s).parsed == ThroughDoor(ObjectRelativeDirection.VICINITY)

    def test_direction(self):
        s = pre_process('enter the room on your right')
        assert action().parse(s).parsed == ThroughDoor(ObjectRelativeDirection.RIGHT)


class PickUpTestCase(unittest.TestCase):
    def test_parse_pick_up(self):
        s = pre_process('pick up the rock on your left')
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_parse_take(self):
        s = pre_process('take the rock on your left')
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.LEFT)

    def test_tape_as_take(self):
        s = pre_process('tape the rock')
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)

    def test_direction_defaults_to_vicinity(self):
        s = pre_process('pick up the hammer')
        assert action().parse(s).parsed == PickUp('hammer', ObjectRelativeDirection.VICINITY)

    def test_take_fails_if_no_object1(self):
        s = pre_process('take the on your left')
        assert type(action().parse(s)) != PickUp

    def test_pick_up_partial_if_no_object1(self):
        # Tests that a partial is returned asking for more information if the object name is not given.
        s = pre_process('pick up')
        result = action().parse(s)
        assert result.marker == PickUp

    def test_pick_up_partial_if_no_object2(self):
        # Tests that a partial is returned asking for more information if the object name is not given.
        s = pre_process('pick up on your left')
        result = action().parse(s)
        assert result.marker == PickUp

    def test_take_is_partial(self):
        # Tests that a partial is returned if you say 'take'.
        s = pre_process('take')
        result = action().parse(s)
        assert result.marker == PickUp

    def test_rope_as_rock(self):
        s = pre_process('pick up the rope')
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)


class ThrowTestCase(unittest.TestCase):
    def test_parse_directional(self):
        s = pre_process('chuck to your left')

        expected_loc = Directional(MoveDirection.LEFT, Distance.MEDIUM)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_parse_positional(self):
        s = pre_process('throw to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_throw_behind_object(self):
        s = pre_process('throw behind the desk')
        assert action().parse(s).parsed == Throw(Behind('desk'))

    def test_defaults_forwards(self):
        s = pre_process('throw')

        expected_loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        assert action().parse(s).parsed == Throw(expected_loc)


class HackTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('hack the terminal on your left')
        assert action().parse(s).parsed == Hack(HackableType.TERMINAL, 'terminal', ObjectRelativeDirection.LEFT)

    def test_direction_defaults_to_vicinity(self):
        s = pre_process('hack the camera')
        assert action().parse(s).parsed == Hack(HackableType.CAMERA, 'camera', ObjectRelativeDirection.VICINITY)

    def test_hacked_as_hack(self):
        s = pre_process('hacked the computer')
        assert action().parse(s).parsed == Hack(HackableType.TERMINAL, 'computer', ObjectRelativeDirection.VICINITY)

    def test_have_as_hack(self):
        s = pre_process('have the console')
        assert action().parse(s).parsed == Hack(HackableType.TERMINAL, 'console', ObjectRelativeDirection.VICINITY)

    def test_text_as_hack(self):
        # Because speech recognition mistakes 'hack' as 'text'
        s = pre_process('text the server')
        assert action().parse(s).parsed == Hack(HackableType.TERMINAL, 'server', ObjectRelativeDirection.VICINITY)

    def test_partial_if_no_object1(self):
        s = pre_process('hack')
        result = action().parse(s)
        assert result.marker == Hack

    def test_partial_if_no_object2(self):
        s = pre_process('hack something')
        result = action().parse(s)
        assert result.marker == Hack
