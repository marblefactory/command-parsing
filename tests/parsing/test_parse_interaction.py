import unittest
from parsing.pre_processing import pre_process
from parsing.parse_action import action
from actions.interaction import *
from actions.location import *


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

    def test_take_is_partial(self):
        # Tests that a partial is returned if you say 'take'.
        s = pre_process('take')
        result = action().parse(s)
        assert result.marker == PickUp

    def test_rope_as_rock(self):
        s = pre_process('pick up the rope')
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)

    def test_ra_as_rock(self):
        s = pre_process('pick up the ra')
        assert action().parse(s).parsed == PickUp('rock', ObjectRelativeDirection.VICINITY)

    def test_parses_noun(self):
        """
        Tests that other nouns that haven't been explicitly listed can also be recognised.
        """
        s = pre_process('pick up the phone')
        assert action().parse(s).parsed == PickUp('phone', ObjectRelativeDirection.VICINITY)

    def test_parses_noun_lower_response(self):
        """
        Tests that although other nouns can be recognised, they have a lower response than objects in the game.
        """
        real_obj_s = pre_process('pick up the rock')
        fake_obj_s = pre_process('pick up the phone')

        real_r = action().parse(real_obj_s)
        fake_r = action().parse(fake_obj_s)

        assert fake_r.response < real_r.response


class ThrowTestCase(unittest.TestCase):
    def test_parse_directional(self):
        s = pre_process('chuck the rock to your left')

        expected_loc = Directional(MoveDirection.LEFT, Distance.MEDIUM)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_parse_positional(self):
        s = pre_process('throw the rock to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_throw_behind_object(self):
        s = pre_process('throw the hammer behind the desk')
        assert action().parse(s).parsed == Throw(Behind('desk'))

    def test_defaults_forwards(self):
        s = pre_process('throw the rock')

        expected_loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_show_as_throw(self):
        s = pre_process('show the rock')

        expected_loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_through_as_throw(self):
        s = pre_process('through the rock')

        expected_loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        assert action().parse(s).parsed == Throw(expected_loc)

    def test_loc_first(self):
        pass

    def test_fails_if_no_object(self):
        s = pre_process('throw')
        assert type(action().parse(s)) != Throw


class DropTestCase(unittest.TestCase):
    def test_drop(self):
        s = pre_process('drop the rock')
        assert action().parse(s).parsed == Drop()

    def test_put_down(self):
        s = pre_process('put down the rock')
        assert action().parse(s).parsed == Drop()

    def test_fails_if_just_put(self):
        s = pre_process('put the rock')
        assert action().parse(s).is_failure()

    def test_fails_if_just_down(self):
        s = pre_process('down the rock')
        assert action().parse(s).is_failure()


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

    def test_hack_into(self):
        s = pre_process('hack into a camera')
        assert action().parse(s).parsed == Hack(HackableType.CAMERA, 'camera', ObjectRelativeDirection.VICINITY)

    def test_log_into(self):
        s = pre_process('log into the computer')
        assert action().parse(s).parsed == Hack(HackableType.TERMINAL, 'computer', ObjectRelativeDirection.VICINITY)

    def test_break_into(self):
        s = pre_process('break into the cctv')
        assert action().parse(s).parsed == Hack(HackableType.CAMERA, 'cctv', ObjectRelativeDirection.VICINITY)

    def test_breaking(self):
        s = pre_process('breaking the mainframe')
        assert action().parse(s).parsed == Hack(HackableType.TERMINAL, 'mainframe', ObjectRelativeDirection.VICINITY)

    def test_partial_if_no_object1(self):
        s = pre_process('hack')
        result = action().parse(s)
        assert result.marker == Hack

    def test_partial_if_no_object2(self):
        s = pre_process('hack something')
        result = action().parse(s)
        assert result.marker == Hack


class PickpocketTestCase(unittest.TestCase):
    def test_parse_pickpocket(self):
        s = pre_process('pickpocket the guard')
        assert action().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)

    def test_parse_direction(self):
        s = pre_process('steal from the guard behind you')
        assert action().parse(s).parsed == Pickpocket(ObjectRelativeDirection.BACKWARDS)

    def test_parse_take(self):
        s = pre_process('take from the guard')
        assert action().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)

    def test_parse_take_object(self):
        s = pre_process('take the rock from the guard')
        assert action().parse(s).parsed == Pickpocket(ObjectRelativeDirection.VICINITY)
