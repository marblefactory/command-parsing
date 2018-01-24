import unittest
from actions.move import *
from encoders.encode_move import *


class ConversionToCPPJSONTestCase(unittest.TestCase):
    """
    Tests converting location in a move to JSON the c++ game can handle.
    """
    def test_no_object_name(self):
        loc = Directional(MoveDirection.LEFT)
        move = Move(Speed.NORMAL, loc, Stance.STAND)

        expected = {
            'type': 'move',
            'speed': 'normal',
            'stance': 'stand',
            'dest': {
                'name': 'no_object',
                'location': {
                    'type': 'directional',
                    'direction': 'left'
                }
            }
        }

        assert expected == json.loads(json.dumps(move, cls=MoveEncoder))


    def test_object_name(self):
        loc = Absolute(place_name='room 201')
        move = Move(Speed.NORMAL, loc, Stance.STAND)

        expected = {
            'type': 'move',
            'speed': 'normal',
            'stance': 'stand',
            'dest': {
                'name': 'room 201',
                'location': {
                    'type': 'absolute'
                }
            }
        }

        assert expected == json.loads(json.dumps(move, cls=MoveEncoder))