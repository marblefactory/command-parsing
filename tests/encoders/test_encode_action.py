import unittest
import json
from actions.interaction import *
from actions.move import *
from actions.location import *
from actions.action import *

from encoders.encode_action import *
from encoders.encode_move import *
from encoders.encode_interaction import *
from encoders.encode_location import *


class StopEncoderTestCase(unittest.TestCase):

    def test_stop(self):
        a = Stop()

        a_json = {'type': 'stop'}

        assert json.dumps(a_json) == str(json.dumps(a, cls=StopEncoder))
