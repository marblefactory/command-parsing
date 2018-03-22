import unittest
from actions.question import *
from encoders.encode_action import ActionEncoder
import json


class InventoryQuestionEncoderTestCase(unittest.TestCase):
    def test_encode(self):
        question = InventoryContentsQuestion()

        expected = {
            'type': 'inventory_question'
        }

        assert expected == json.loads(json.dumps(question, cls=ActionEncoder))


class LocationQuestionTestCase(unittest.TestCase):
    def test_encode(self):
        question = LocationQuestion()

        expected = {
            'type': 'location_question'
        }

        assert expected == json.loads(json.dumps(question, cls=ActionEncoder))


class GuardQuestionTestCase(unittest.TestCase):
    def test_encode(self):
        question = GuardsQuestion()

        expected = {
            'type': 'guards_question'
        }

        assert expected == json.loads(json.dumps(question, cls=ActionEncoder))
