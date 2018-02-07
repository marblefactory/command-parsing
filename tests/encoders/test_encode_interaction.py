import unittest
from actions.interaction import *
from encoders.encode_interaction import *
from encoders.encode_action import ActionEncoder


class ThroughDoorEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        through_door = ThroughDoor()

        expected = {
            'type': 'opendoor'
        }

        assert expected == json.loads(json.dumps(through_door, cls=ActionEncoder))


class PickUpEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        pick_up = PickUp('rock', ObjectRelativeDirection.VICINITY)

        expected = {
            'type': 'pickup',
            'name': 'rock',
            'direction': 'vicinity'
        }

        assert expected == json.loads(json.dumps(pick_up, cls=ActionEncoder))


class ThrowEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        target_loc = Directional(MoveDirection.FORWARDS)
        throw = Throw(target_loc)

        expected = {
            'type': 'throw',
            'location': {
                'type': 'directional',
                'direction': 'forwards'
            }
        }

        assert expected == json.loads(json.dumps(throw, cls=ActionEncoder))


class HackEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        hack = Hack('computer', ObjectRelativeDirection.RIGHT)

        expected = {
            'type': 'hack',
            'name': 'computer',
            'direction': 'right'
        }

        assert expected == json.loads(json.dumps(hack, cls=ActionEncoder))