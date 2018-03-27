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

    def test_sneak_as_crouch(self):
        s = pre_process('sneak')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_get_up(self):
        s = pre_process('get up')
        assert action().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_get_down(self):
        s = pre_process('get down')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_grouch_as_crouch(self):
        s = pre_process('grouch')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_lie_down(self):
        s = pre_process('lie down')
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)

    def test_get_low(self):
        s = pre_process('get low')
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

    def test_hurry(self):
        s = pre_process('hurry up')
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
    def test_parses_just_location1(self):
        s = pre_process('next door')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Positional('door', 0, ObjectRelativeDirection.FORWARDS), None)

    def test_parses_just_location2(self):
        s = pre_process('forward')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.FORWARDS, Distance.MEDIUM), None)

    def test_parses_just_location_with_speed_stance(self):
        s = pre_process('running forward standing')
        assert action().parse(s).parsed == Move(Speed.FAST, Directional(MoveDirection.FORWARDS, Distance.MEDIUM), Stance.STAND)

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

    def test_to_as_go(self):
        s = pre_process('to lab 300')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Absolute('lab 300'), None)

    def test_randa_as_run(self):
        s = pre_process('randa to lab 25')
        assert action().parse(s).parsed == Move(Speed.FAST, Absolute('lab 25'), None)

    def test_rhonda_as_run(self):
        s = pre_process('rhonda to lab 300')
        assert action().parse(s).parsed == Move(Speed.FAST, Absolute('lab 300'), None)

    def test_rhondda_as_run(self):
        s = pre_process('rhondda to lab 300')
        assert action().parse(s).parsed == Move(Speed.FAST, Absolute('lab 300'), None)

    def test_fails(self):
        s = pre_process("good")
        assert action().parse(s).is_failure()

    def test_pick_up_is_not_move(self):
        s = pre_process('pick up the assault rifle')
        assert type(action().parse(s).parsed) != Move

    def test_move_forwards(self):
        s = pre_process('move forwards')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.FORWARDS, Distance.MEDIUM), None)

    def test_move_backwards(self):
        s = pre_process('move backwards')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.BACKWARDS, Distance.MEDIUM), None)

    def test_move_left(self):
        s = pre_process('move left')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT, Distance.MEDIUM), None)

    def test_move_right(self):
        s = pre_process('move right')
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.RIGHT, Distance.MEDIUM), None)


class HideTestCase(unittest.TestCase):
    def test_parses_object_named(self):
        s = pre_process('hide behind the wall')
        assert action().parse(s).parsed == Hide('wall')

    def test_parses_no_object(self):
        s = pre_process('hide')
        assert action().parse(s).parsed == Hide(None)

    def test_take_cover(self):
        s = pre_process('take cover')
        assert action().parse(s).parsed == Hide(None)


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


class LeaveRoomTestCase(unittest.TestCase):
    def test_parse(self):
        s = pre_process('leave the room')
        assert action().parse(s).parsed == LeaveRoom()
