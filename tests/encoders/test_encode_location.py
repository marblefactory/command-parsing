import unittest
from encoders.encode_location import *
import json


class AbsoluteEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        absolute = Absolute('room 302')

        expected = {
            'type': 'absolute',
            'name': 'room 302'
        }

        assert expected == json.loads(json.dumps(absolute, cls=LocationEncoder))


class PositionalEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        positional = Positional('door', 1, MoveDirection.BACKWARDS)

        expected = {
            'type': 'positional',
            'index': 1,
            'name': 'door',
            'direction': 'backwards'
        }

        assert expected == json.loads(json.dumps(positional, cls=LocationEncoder))


class DirectionalEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        directional = Directional(MoveDirection.RIGHT, Distance.FAR)

        expected = {
            'type': 'directional',
            'direction': 'right',
            'distance': 'far'
        }

        assert expected == json.loads(json.dumps(directional, cls=LocationEncoder))


class StairsEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        stairs = Stairs(FloorDirection.UP)

        expected = {
            'type': 'stairs',
            'direction': 'up'
        }

        assert expected == json.loads(json.dumps(stairs, cls=LocationEncoder))

    def test_encode_no_direction(self):
        stairs = Stairs(None)

        expected = {
            'type': 'stairs',
            'direction': 'none'
        }

        assert expected == json.loads(json.dumps(stairs, cls=LocationEncoder))


class BehindEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        behind = Behind('desk')

        expected = {
            'type': 'behind',
            'name': 'desk'
        }

        assert expected == json.loads(json.dumps(behind, cls=LocationEncoder))


class EndOfEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        end_of = EndOf('room')

        expected = {
            'type': 'end_of',
            'name': 'room'
        }

        assert expected == json.loads(json.dumps(end_of, cls=LocationEncoder))
