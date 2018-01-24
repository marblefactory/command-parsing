import unittest
from parsing.parse_move import *
from actions.move import *


class ChangeStanceTestCase(unittest.TestCase):
    def test_stand_up(self):
        s = 'stand up'.split()
        assert change_stance().parse(s).parsed == ChangeStance(Stance.STAND)

    def test_crouch(self):
        s = 'crouch down'.split()
        assert change_stance().parse(s).parsed == ChangeStance(Stance.CROUCH)
