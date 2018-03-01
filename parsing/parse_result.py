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

    def __lt__(self, other) -> bool:
        """
        Assumes the responses are in the range 0-1.
        :return: Successes are ranked the highest, if two are compared the response is used.
                 Partials are ranked below success, if two are compared the response is used.
                 Failures are ranked lowest, and two are worth the same.
        """
        # Used for inter-class comparison.
        def rank(result: ParseResult) -> int:
            return result.either(lambda _: 2, lambda _: 1, lambda _: 0)

        # Used for intra-class comparison
        def response(result: ParseResult) -> int:
            success = lambda s: s.response
            partial = lambda p: p.response
            failure = lambda f: 0.0

            return result.either(success, partial, failure)

        if rank(self) > rank(other):
            return False

        if rank(self) == rank(other):
            return response(self) < response(other)

        # Only case left is rank(self) < rank(other)
        return True


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
        :param response: the response so far, until the failed parser.
        """
        self.failed_parser = failed_parser
        self.response = response


class FailureParse(ParseResult):
    """
    Represents a failed parse.
    """
    pass
