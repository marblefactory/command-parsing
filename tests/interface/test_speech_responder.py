import unittest
from interface.speech_responder import SpeechResponder
from parsing.parser import *


class SpeechResponderTestCase(unittest.TestCase):
    def responder(self) -> SpeechResponder:
        """
        :return: a speech responder which parses the transcript 'hello world' partially.
                 'success' is the speech response returned for successful parsing, and 'failure' is the speech response
                 for failed parsing.
        """
        def combine(parsed: str, response: Response) -> Parser:
            return partial_parser(word_match('world').map_parsed(lambda x: parsed + x), 0.5, 'Type')

        # A parser which parses 'hello world', but where 'world' can be asked for after (i.e. partial parsing).
        parser = word_match('hello').then(combine)

        return SpeechResponder(parser, lambda game_resp, action: 'success', lambda t: 'partial' + t, lambda _: 'failure')

    def test_generates_success_speech(self):
        responder = self.responder()

        make_speech, parsed = responder.parse('hello world')
        game_response = {}
        assert make_speech(game_response) == 'success'

    def test_generates_parsed_object(self):
        responder = self.responder()

        make_speech, parsed = responder.parse('hello world')
        assert parsed == 'helloworld'

    def test_generates_partial_speech(self):
        responder = self.responder()

        make_speech, parsed = responder.parse('hello')
        game_response = {}
        assert make_speech(game_response) == 'partialType'

    def test_generates_no_partial_parsed_object(self):
        responder = self.responder()

        speech, parsed = responder.parse('hello')
        assert parsed is None

    def test_parses_partial_success_speech(self):
        # Tests that after a partial parse, the full object can be parsed after.
        responder = self.responder()
        _ = responder.parse('hello')
        make_speech, parsed = responder.parse('world')

        game_response = {}
        assert make_speech(game_response) == 'success'

    def test_parses_partial_success_object(self):
        # Tests that after a partial parse, the full object can be parsed after.
        responder = self.responder()
        _ = responder.parse('hello')
        speech, parsed = responder.parse('world')

        assert parsed == 'helloworld'

    def test_generates_failure_speech(self):
        responder = self.responder()

        make_speech, parsed = responder.parse('nothing here')
        game_response = {}
        assert make_speech(game_response) == 'failure'

    def test_generates_no_failure_parsed_object(self):
        responder = self.responder()

        speech, parsed = responder.parse('nothing here')
        assert parsed is None
