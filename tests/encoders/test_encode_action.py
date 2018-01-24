import unittest
from encoders.encode_action import *
from encoders.encode_location import *


class StopEncoderTestCase(unittest.TestCase):
    def test_encodes(self):
        expected = {
            'type': 'stop'
        }

        assert expected == json.loads(json.dumps(Stop(), cls=ActionEncoder))


class CompositeEncoderTestCase(unittest.TestCase):
    def test_encodes(self):
        actions = [Stop(), Stop()]
        composite = Composite(actions)

        expected = {
            'type': 'composite',
            'actions': [
                {
                    'type': 'stop'
                },
                {
                    'type': 'stop'
                }
            ]
        }

        assert expected == json.loads(json.dumps(composite, cls=ActionEncoder))
