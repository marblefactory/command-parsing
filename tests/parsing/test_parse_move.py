import unittest
from parsing.parse_move import *
from actions.move import *
from actions.location import *


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


class ChangeStanceTestCase(unittest.TestCase):
    def test_stand_up(self):
        s = 'stand up'.split()
        assert change_stance().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_crouch(self):
        s = 'crouch down'.split()
        assert change_stance().parse(s).parsed == ChangeStance(Stance.CROUCH)


class MoveTestCase(unittest.TestCase):
    def test_parses_go(self):
        s = 'go left crouching'.split()
        assert move().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), Stance.CROUCH)

    def test_parses_walk(self):
        s = 'walk left crouching'.split()
        assert move().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), Stance.CROUCH)

    def test_stance_defaults_to_none(self):
        s = 'go left'.split()
        assert move().parse(s).parsed == Move(Speed.NORMAL, Directional(MoveDirection.LEFT), None)
