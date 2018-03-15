import unittest
from parsing.pre_processing import pre_process
from parsing.parse_move import speed, stance
from parsing.parse_action import action
from actions.move import *
from actions.location import *


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
        s = pre_process('crouch')
        assert stance().parse(s).parsed == Stance.CROUCH

    def test_couch_as_crouch(self):
        s = pre_process('couch')
        assert stance().parse(s).parsed == Stance.CROUCH

    def test_stand(self):
        s = pre_process('stand')
        assert stance().parse(s).parsed == Stance.STAND


class TurnTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('turn to your left')
        assert action().parse(s).parsed == Turn(MoveDirection.LEFT)

    def test_defaults_backwards(self):
        s = pre_process('turn around')
        assert action().parse(s).parsed == Turn(MoveDirection.BACKWARDS)


class ChangeStanceTestCase(unittest.TestCase):
    def test_stand_up(self):
        s = pre_process('stand up')
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_stand(self):
        s = pre_process('stand')
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_standing_as_stand(self):
        s = pre_process('standing')
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_crouch(self):
        s = pre_process('crouch down')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_crouching(self):
        s = pre_process('crouching')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_quiet_as_crouch(self):
        s = pre_process('be quiet')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_get_up(self):
        s = pre_process('get up')
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_get_down(self):
        s = pre_process('get down')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)


class ChangeSpeedTestCase(unittest.TestCase):
    def test_run(self):
        s = pre_process('run')
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_fast(self):
        s = pre_process('fast')
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_running_as_fast(self):
        s = pre_process('running')
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_sprinting_as_fast(self):
        s = pre_process('sprinting')
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_go_fast(self):
        s = pre_process('go fast')
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_run_quick(self):
        s = pre_process('run quick')
        assert action().parse(s).parsed == ChangeSpeed(Speed.FAST)

    def test_slow(self):
        s = pre_process('slow down')
        assert action().parse(s).parsed == ChangeSpeed(Speed.SLOW)

    def test_go_slow(self):
        s = pre_process('go slow')
        assert action().parse(s).parsed == ChangeSpeed(Speed.SLOW)

    def test_go_normally(self):
        s = pre_process('go normally')
        assert action().parse(s).parsed == ChangeSpeed(Speed.NORMAL)

    def test_walk(self):
        s = pre_process('walk')
        assert action().parse(s).parsed == ChangeSpeed(Speed.NORMAL)


class MoveTestCase(unittest.TestCase):
    def test_fails_if_just_location(self):
        s = pre_process('next door')
        assert action().parse(s).is_failure()

    def test_parses_standing(self):
        s = pre_process('go left standing')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), Stance.STAND)

    def test_parses_crouching(self):
        s = pre_process('walk left crouching')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), Stance.CROUCH)

    def test_parses_crouching_as_crouch(self):
        s = pre_process('go left while crouching')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), Stance.CROUCH)

    def test_stance_defaults_to_none(self):
        s = pre_process('go left')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), None)

    def test_fast(self):
        s = pre_process('run to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_ron_as_run(self):
        s = pre_process('ron to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_sprint_as_fast(self):
        s = pre_process('sprint to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_running_as_run(self):
        s = pre_process('go running to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.FAST, expected_loc, None)

    def test_slow(self):
        s = pre_process('slowly go to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.SLOW, expected_loc, None)

    def test_quietly_as_crouch(self):
        s = pre_process('quietly go to the next door')

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.NORMAL, expected_loc, Stance.CROUCH)

    def test_parses_behind(self):
        s = pre_process('go around the desk')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Behind('desk'), None)

    def test_parses_turn_backwards(self):
        s = pre_process('turn around')
        assert action().parse(s).parsed == Turn(MoveDirection.BACKWARDS)

    def test_parses_take_next_door(self):
        s = pre_process('take the next door')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Positional('door', 0, MoveDirection.FORWARDS), None)

    def test_parses_take_the_stairs(self):
        s = pre_process('take the stairs up')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Stairs(FloorDirection.UP), None)

    def test_corridor_does_not_crouch(self):
        """
        Tests that 'corridor' does not mean crouch
        """
        s = pre_process('go to the end of the corridor')
        assert action().parse(s).parsed == Move(Speed.NORMAL, EndOf('corridor'), None)

    def test_normal(self):
        s = pre_process('go normally to the next room')

        expected_loc = Positional('room', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.NORMAL, expected_loc, None)

    def test_go_is_partial(self):
        s = pre_process('go')
        result = action().parse(s)
        assert result.marker == Move

    def test_o2_is_go(self):
        s = pre_process('o2 lab 300')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Absolute('lab 300'), None)


class HideTestCase(unittest.TestCase):
    def test_parses_object_named(self):
        s = pre_process('hide behind the wall')
        assert action().parse(s).parsed == Hide('wall')

    def test_parses_no_object(self):
        s = pre_process('hide')
        assert action().parse(s).parsed == Hide(None)
