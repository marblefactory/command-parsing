import unittest
from parsing.parse_move import speed, stance
from parsing.parse_action import action
from actions.move import *
from actions.location import *

from parsing.parser import word_meaning


class SpeedTestCase(unittest.TestCase):
    def test_fast(self):
        words = ['run', 'quickly', 'fast']
        for word in words:
            assert speed().parse([word]).parsed == Speed.FAST

    def test_slow(self):
        assert speed().parse(['slow']).parsed == Speed.SLOW

    def test_default_normal(self):
        assert speed().parse(['nan']).parsed == Speed.NORMAL


class StanceTestCase(unittest.TestCase):
    def test_crouch(self):
        assert stance().parse(['crouch']).parsed == Stance.CROUCH

    def test_stand(self):
        assert stance().parse(['stand']).parsed == Stance.STAND


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

    def test_crouch(self):
        s = 'crouch down'.split()
        assert action().parse(s).parsed == ChangeStance(Stance.CROUCH)


class MoveTestCase(unittest.TestCase):
    def test_parses_go(self):
        s = 'go left standing'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), Stance.STAND)

    def test_parses_walk(self):
        s = 'walk left crouching'.split()
        assert action().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), Stance.CROUCH)

    def test_whats_as_walk(self):
        s = 'whats the next room'.split()
        expected_loc = Positional('room', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.NORMAL, expected_loc, None)

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

    def test_slow(self):
        s = 'slowly go to the next door'.split()

        expected_loc = Positional('door', 0, MoveDirection.FORWARDS)
        assert action().parse(s).parsed == Move(Speed.SLOW, expected_loc, None)

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


class HideTestCase(unittest.TestCase):
    def test_parses_object_named(self):
        s = 'hide behind the table'.split()
        assert action().parse(s).parsed == Hide('table')

    def test_parses_no_object(self):
        s = 'hide'.split()
        assert action().parse(s).parsed == Hide(None)
