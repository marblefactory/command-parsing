import unittest
from actions.location import *
from actions.interaction import *
from encoders.encode_action import ActionEncoder
import json


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
        target_loc = Directional(MoveDirection.FORWARDS, Distance.SHORT)
        throw = Throw(target_loc)

        expected = {
            'type': 'throw',
            'location': {
                'type': 'directional',
                'direction': 'forwards',
                'distance': 'short'
            }
        }

        assert expected == json.loads(json.dumps(throw, cls=ActionEncoder))


class DropEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        drop = Drop()

        expected = {
            'type': 'drop'
        }

        assert expected == json.loads(json.dumps(drop, cls=ActionEncoder))


class HackEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        hack = Hack(HackableType.TERMINAL, 'computer', ObjectRelativeDirection.RIGHT)

        expected = {
            'type': 'hack',
            'hack_type': 'terminal',
            'direction': 'right'
        }

        assert expected == json.loads(json.dumps(hack, cls=ActionEncoder))


class PickpocketEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        pickpocket = Pickpocket(ObjectRelativeDirection.RIGHT)

        expected = {
            'type': 'pickpocket',
            'direction': 'right'
        }

        assert expected == json.loads(json.dumps(pickpocket, cls=ActionEncoder))
