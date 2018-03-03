import unittest
from parsing.parse_move import speed, stance
from parsing.parse_action import action
from actions.move import *
from actions.location import *
from parsing.parse_result import PartialParse


class SpeedTestCase(unittest.TestCase):
    def test_fast(self):
        words = ['run', 'quickly', 'fast']
        for word in words:
            assert speed().parse([word]).parsed == Speed.FAST

    def test_slow(self):
        assert speed().parse(['slow']).parsed == Speed.SLOW

    def test_normal(self):
        assert speed().parse(['normal']).parsed == Speed.NORMAL

    def test_normally(self):
        assert speed().parse(['normally']).parsed == Speed.NORMAL


class StanceTestCase(unittest.TestCase):
    def test_crouch(self):
        s = 'crouch'.split()
        assert stance().parse(s).parsed == Stance.CROUCH

    def test_couch_as_crouch(self):
        s = 'couch'.split()
        assert stance().parse(s).parsed == Stance.CROUCH

    def test_stand(self):
        s = 'stand'.split()
        assert stance().parse(s).parsed == Stance.STAND


class TurnTestCase(unittest.TestCase):
    def test_parse(self):
        s = 'turn to your left'.split()
        assert action().parse(s).parsed == Turn(MoveDirection.LEFT)

    def test_defaults_backwards(self):
        s = 'turn around'.split()
        assert action().parse(s).parsed == Turn(MoveDirection.BACKWARDS)


class ChangeStanceTestCase(unittest.TestCase):
    def test_stand_up(self):
        s = 'stand up'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_stand(self):
        s = 'stand'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_standing_as_stand(self):
        s = 'standing'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_crouch(self):
        s = 'crouch down'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_crouching(self):
        s = 'crouching'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_quiet_as_crouch(self):
        s = 'be quiet'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_get_up(self):
        s = 'get up'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_get_down(self):
        s = 'get down'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)


class ChangeSpeedTestCase(unittest.TestCase):
    def test_run(self):
        s = 'run'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_fast(self):
        s = 'fast'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_running_as_fast(self):
        s = 'running'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_sprinting_as_fast(self):
        s = 'sprinting'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_go_fast(self):
        s = 'go fast'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_run_quick(self):
        s = 'run quick'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_slow(self):
        s = 'slow down'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.SLOW)

    def test_go_slow(self):
        s = 'go slow'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.SLOW)

    def test_go_normally(self):
        s = 'go normally'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.NORMAL)

    def test_walk(self):
        s = 'walk'.split()
        assert action().parse(s).parsed == ChangeSpeed(Speed.NORMAL)


class MoveTestCase(unittest.TestCase):
    def test_fails_if_just_location(self):
        s = 'next door'.split()
        assert action().parse(s).is_failure()

    def test_parses_standing(self):
        s = 'go left standing'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), Stance.STAND)

    def test_parses_crouching(self):
        s = 'walk left crouching'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), Stance.CROUCH)

    def test_parses_crouching_as_crouch(self):
        s = 'go left while crouching'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), Stance.CROUCH)

    def test_stance_defaults_to_none(self):
        s = 'go left'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None)

    def test_fast(self):
        s = 'run to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_ron_as_run(self):
        s = 'ron to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_sprint_as_fast(self):
        s = 'sprint to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_running_as_run(self):
        s = 'go running to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_slow(self):
        s = 'slowly go to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.SLOW, expected_loc, None)

    def test_quietly_as_crouch(self):
        s = 'quietly go to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.NORMAL, expected_loc, Stance.CROUCH)

    def test_parses_behind(self):
        s = 'go around the desk'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Behind('desk'), None)

    def test_parses_turn_backwards(self):
        s = 'turn around'.split()
        assert action().parse(s).parsed == Turn(MoveDirection.BACKWARDS)

    def test_parses_take_next_door(self):
        s = 'take the next door'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Positional('door', 0, MoveDirection.FORWARDS), None)

    def test_parses_take_the_stairs(self):
        s = 'take the stairs up'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Stairs(FloorDirection.UP), None)

    def test_corridor_does_not_crouch(self):
        """
        Tests that 'corridor' does not mean crouch
        """
        s = 'go to the end of the corridor'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, EndOf('corridor'), None)

    def test_normal(self):
        s = 'go normally to the next room'.split()

        expected_loc = Positional('room', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.NORMAL, expected_loc, None)

    def test_go_is_partial(self):
        s = 'go'.split()
        result = action().parse(s)
        assert result.marker == Move


class HideTestCase(unittest.TestCase):
    def test_parses_object_named(self):
        s = 'hide behind the wall'.split()
        assert action().parse(s).parsed == Hide('wall')

    def test_parses_no_object(self):
        s = 'hide'.split()
        assert action().parse(s).parsed == Hide(None)
