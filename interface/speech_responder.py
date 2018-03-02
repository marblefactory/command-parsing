from parsing.parser import Parser, strongest
from parsing.pre_processing import pre_process
from parsing.parse_result import SuccessParse, PartialParse, FailureParse
from actions.action import Action
from typing import Optional, Callable, Any


class SpeechResponder:
    """
    Parses the transcript and creates a speech response to send to the user.
    Depending on the **state** the response will be different, for example, if the last transcript gave a partial
    response, we will try and parse with the failed parser.
    """

    # Is a parser if the last transcript gave a partial parse. The parser will be tried on the next parse.
    _partial: Optional[Parser]

    def __init__(self, parser: Parser,
                 parsed_response: Callable[[Action], str],
                 partial_response: Callable[[Any], str],
                 no_parsed_response: Callable[[str], str]):
        """
        :param parser: the parser to be used when parsing the transcript.
        :param parsed_response: function used to create a response when an action was parsed from the transcript.
        :param partial_response: function used to create a response when a partial was parsed from the transcript.
                                 The marker given to the function is the marker supplied to the partial parser that failed.
        :param no_parsed_response: function used to create a response when nothing could be parsed from the transcript.
        """
        self.parser = parser
        self.parsed_response = parsed_response
        self.partial_response = partial_response
        self.no_parsed_response = no_parsed_response
        self._partial = None

    def parse(self, transcript: str) -> (str, Optional[Action]):
        """
        :param transcript: the transcript of the user's speech.
        :return: a speech response to be sent to the client to speak. An action for the spy to perform may optionally
                 be returned if one was parsed from the transcript.
        """

        # Create a parser containing the partial parser if there was a partial result last time.
        parser = strongest([self._partial, self.parser]) if self._partial else self.parser

        words = pre_process(transcript)
        result = parser.parse(words)

        if isinstance(result, SuccessParse):
            self._partial = None
            action = result.parsed
            return (self.parsed_response(action), action)

        elif isinstance(result, PartialParse):
            self._partial = result.failed_parser
            # We assume the marker is the class that failed to parse.
            return (self.partial_response(result.marker), None)

        elif isinstance(result, FailureParse):
            self._partial = None
            return (self.no_parsed_response(transcript), None)

        raise RuntimeError('unexpected ParseResult type')
