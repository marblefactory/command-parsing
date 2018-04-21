import unittest
from actions.location import Absolute, Directional, MoveDirection, Distance
from actions.move import Move, Speed, ThroughDoor, ObjectRelativeDirection
from actions.action import Composite


class TestMovePostProcessing(unittest.TestCase):
    def test_post_process_no_change(self):
        loc = Directional(MoveDirection.FORWARDS, Distance.MEDIUM)
        move = Move(Speed.NORMAL, loc, None)

        self.assertEqual(move.post_processed(), move)

    def test_post_process_absolute_loc(self):
        loc = Absolute('room')
        move = Move(Speed.NORMAL, loc, None)

        expected = Composite([move, ThroughDoor(ObjectRelativeDirection.VICINITY)])
        self.assertEqual(move.post_processed(), expected)
