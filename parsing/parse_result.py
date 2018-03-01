from equatable import EquatableMixin
from typing import List, Any, Callable

# A word in the user's text.
Word = str

# A value from 0-1 indicating how strongly a parser 'matches' on some text. E.g. a parser for the semantic similarity
# to the word 'hello' would give a higher response for 'hi' than 'car'.
Response = float


class ParseResult(EquatableMixin):
    """
    The result of performing parsing.
    """
    def either(self,
               success: Callable[['SuccessParse'], Any] = lambda _: None,
               partial: Callable[['PartialParse'], Any] = lambda _: None,
               failure: Callable[['FailureParse'], Any] = lambda _: None):

        if isinstance(self, SuccessParse):
            return success(self)
        elif isinstance(self, PartialParse):
            return partial(self)
        elif isinstance(self, FailureParse):
            return failure(self)

        raise RuntimeError('unexpected ParseResult type')

    def is_failure(self) -> bool:
        return isinstance(self, FailureParse)


class SuccessParse(ParseResult):
    """
    Represents a successful parse.
    """
    def __init__(self, parsed: Any, response: Response, remaining: List[Word]):
        """
        :param parsed: the object the was parsed.
        :param response: how strongly the parser matched on the transcript.
        :param remaining: any words that were remaining un-parsed.
        """
        self.parsed = parsed
        self.response = response
        self.remaining = remaining


class PartialParse(ParseResult):
    """
    Represents a parse that was partially matched, but the player
    needs to be asked questions for the rest of the information.
    """

    def __init__(self, failed_parser, response: Response):
        """
        :param failed_parser: the parser that failed, but that can be reapplied once were have more  information.
        :param response: the response so far.
        :param remaining: any words that were remaining un-parsed.
        """
        self.failed_parser = failed_parser
        self.response = response


class FailureParse(ParseResult):
    """
    Represents a failed parse.
    """
    pass
