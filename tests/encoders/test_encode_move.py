import unittest
import json
from actions.move import *
from actions.location import *
from encoders.encode_action import ActionEncoder


class ConversionToCPPJSONTestCase(unittest.TestCase):
    """
    Tests converting location in a move to JSON the c++ game can handle.
    """
    def test_no_object_name(self):
        loc = Directional(MoveDirection.LEFT, Distance.MEDIUM)
        move = Move(Speed.NORMAL, loc, Stance.STAND)

        expected = {
            'type': 'move',
            'speed': 'normal',
            'stance': 'stand',
            'dest': {
                'name': 'no_object',
                'location': {
                    'type': 'directional',
                    'direction': 'left',
                    'distance': 'medium'
                }
            }
        }

        assert expected == json.loads(json.dumps(move, cls=ActionEncoder))


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

        assert expected == json.loads(json.dumps(move, cls=ActionEncoder))


class TurnEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        turn = Turn(MoveDirection.RIGHT)

        expected = {
            'type': 'turn',
            'direction': 'right'
        }

        assert expected == json.loads(json.dumps(turn, cls=ActionEncoder))


class ChangeStanceEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        change_stance = ChangeStance(Stance.CROUCH)

        expected = {
            'type': 'change_stance',
            'stance': 'crouch'
        }

        assert expected == json.loads(json.dumps(change_stance, cls=ActionEncoder))


class ChangeSpeedEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        change_speed = ChangeSpeed(Speed.NORMAL)

        expected = {
            'type': 'change_speed',
            'speed': 'normal'
        }

        assert expected == json.loads(json.dumps(change_speed, cls=ActionEncoder))


class MoveEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        loc = Stairs(FloorDirection.DOWN)
        move = Move(Speed.SLOW, loc, Stance.STAND)

        expected = {
            'type': 'move',
            'speed': 'slow',
            'stance': 'stand',
            'dest': {
                'name': 'no_object',
                'location': {
                    'type': 'stairs',
                    'direction': 'down'
                }
            }
        }

        assert expected == json.loads(json.dumps(move, cls=ActionEncoder))

    def test_encode_no_stance(self):
        loc = Absolute('room 3')
        move = Move(Speed.SLOW, loc, None)

        expected = {
            'type': 'move',
            'speed': 'slow',
            'stance': 'no_change',
            'dest': {
                'name': 'room 3',
                'location': {
                    'type': 'absolute'
                }
            }
        }

        assert expected == json.loads(json.dumps(move, cls=ActionEncoder))


class HideEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        hide = Hide('table')

        expected = {
            'type': 'hide',
            'name': 'table'
        }

        assert expected == json.loads(json.dumps(hide, cls=ActionEncoder))


class ThroughDoorEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        through_door = ThroughDoor(ObjectRelativeDirection.BACKWARDS)

        expected = {
            'type': 'opendoor',
            'direction': 'backwards'
        }

        assert expected == json.loads(json.dumps(through_door, cls=ActionEncoder))


class LeaveRoomEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        leave_room = LeaveRoom()

        expected = {
            'type': 'leave_room',
        }

        assert expected == json.loads(json.dumps(leave_room, cls=ActionEncoder))
