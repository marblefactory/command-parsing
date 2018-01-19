import unittest
from parser import *
from descriptor import *


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


class NTLKFirsTaggedTestCase(unittest.TestCase):
    """
    Tests nltk first_tagged
    """

    def test_no_match(self):
        assert nltk_first_tagged('NN', ['go', 'dive']) == None

    def test_match(self):
        assert nltk_first_tagged('NN', ['car', 'go']) == 'car'

    def test_first_match(self):
        assert nltk_first_tagged('NN', ['boat', 'car']) == 'boat'


class ParseOneOfTestCase(unittest.TestCase):
    """
    Tests parse_one_of
    """

    def parse_fn(self, text: str) -> Optional[int]:
        possibilities = {
            'a': 1,
            'b': 2
        }
        return parse_one_of(possibilities, text.split())

    def test_no_match(self):
        assert self.parse_fn('c d') is None

    def test_match1(self):
        assert self.parse_fn('a d') == 1

    def test_match2(self):
        assert self.parse_fn('b d') == 2

    def test_matches_first_occurence_in_text(self):
        assert self.parse_fn('b a') == 2
