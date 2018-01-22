import unittest
from parser import *


class ParserTestCase(unittest.TestCase):
    def test_then(self):
        # Take a parser, keep the parse result, but set the response to zero.
        def f(parsed: str, response) -> Parser:
            return produce(parsed, 0.0)

        parser = produce('a', 1.0).then(f)

        assert parser.parse(['b']) == ParseResult(parsed='a', response=0.0, remaining=['b'])

    def test_then_ignore(self):
        # Ignore the parsed 'b', but average the responses.
        parser = produce('a', 0.0).then_ignore(produce('b', 1.0), mean)

        assert parser.parse([]) == ParseResult(parsed='a', response=0.5, remaining=[])

    def test_ignore_then(self):
        # Ignore the parsed 'a', but average the responses.
        parser = produce('a', 1.0).ignore_then(produce('b', 0.0), mean)

        assert parser.parse([]) == ParseResult(parsed='b', response=0.5, remaining=[])

    def test_map(self):
        parser = produce('a', 1.0).map(lambda p, r: (p + 'bc', r / 2))

        assert parser.parse([]) == ParseResult(parsed='abc', response=0.5, remaining=[])

    def test_map_parsed(self):
        parser = produce('a', 0.8).map_parsed(lambda p: 'x' + p)

        assert parser.parse([]) == ParseResult(parsed='xa', response=0.8, remaining=[])

    def test_map_response(self):
        parser = produce('a', 0.8).map_response(lambda r: r / 2)

        assert parser.parse([]) == ParseResult(parsed='a', response=0.4, remaining=[])


class PredicateTestCase(unittest.TestCase):
    def test_condition_below_threshold(self):
        """
        Tests None is returned if the condition is below the threshold.
        """
        def condition(input_word: Word) -> Response:
            return 0.1

        parser = predicate(condition, threshold=0.5)

        assert parser.parse([]) is None

    def test_condition_on_threshold(self):
        """
        Tests the parse result is returned if condition is on the threshold.
        """
        def condition(input_word: Word) -> Response:
            return 0.5

        parser = predicate(condition, threshold=0.5)

        assert parser.parse(['a', 'b']) == ParseResult(parsed='a', response=0.5, remaining=['b'])

    def test_condition_above_threshold(self):
        """
        Tests the parse result is returned if the condition is over the threshold.
        """
        def condition(input_word: Word) -> Response:
            return 0.51

        parser = predicate(condition, threshold=0.5)

        assert parser.parse(['a', 'b']) == ParseResult(parsed='a', response=0.51, remaining=['b'])