import unittest
from text_parsing import *


class MockInteraction(SpeechParsable):
    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return WordMatch('interaction')

    @classmethod
    def parse(cls, user_text: str) -> 'MockInteraction':
        return MockInteraction()


class MockMovement(SpeechParsable):
    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return WordMatch('move')

    @classmethod
    def parse(cls, user_text: str) -> 'MockMovement':
        return MockMovement()


class MockHack(SpeechParsable):
    @classmethod
    def text_descriptor(cls) -> Descriptor:
        return And([WordMatch('hack'), WordMatch('terminal')])

    @classmethod
    def parse(cls, user_text: str) -> 'MockHack':
        return MockHack()


class SpeechParsableTestCase(unittest.TestCase):

    def test_parse_unique(self):
        """
        Tests the correct class is parsed when the input text uniquely describes the type.
        """
        parsed = parse_user_speech('move', [MockInteraction, MockMovement, MockHack])

        assert type(parsed) == MockMovement

    def test_no_parse(self):
        """
        Tests None is returned if nothing could be parsed.
        """
        parsed = parse_user_speech('nothing', [MockInteraction, MockMovement, MockHack])

        assert parsed is None

    def test_below_threshold(self):
        """
        Tests None is returned if all responses are below the threshold.
        """
        parsed = parse_user_speech('hack', [MockInteraction, MockMovement, MockHack], response_threshold=0.51)

        assert parsed == None

    def test_above_threshold(self):
        """
        Tests the correct class is parsed if the response if above a threshold.
        """
        parsed = parse_user_speech('hack', [MockInteraction, MockMovement, MockHack], response_threshold=0.49)

        assert type(parsed) == MockHack

    def test_unsure(self):
        """
        Tests None is returned if two classes give the maximum response.
        """
        parsed = parse_user_speech('move interaction', [MockInteraction, MockMovement, MockHack])

        assert parsed == None