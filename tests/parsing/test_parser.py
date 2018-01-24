import unittest
from parsing.parser import *


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

    def test_ignore_parsed_captures_state(self):
        letter = 'b'
        parser = produce('a', 0.8).ignore_parsed(letter)
        letter = 'c'

        assert parser.parse([]) == ParseResult(parsed='b', response=0.8, remaining=[])


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


class WordMatchTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if the word is nowhere in the input text.
        """
        assert word_match('a').parse(['b', 'c']) is None

    def test_match(self):
        """
        Tests the word is parsed if it is in the input text.
        """
        assert word_match('a').parse(['b', 'a', 'c']) == ParseResult(parsed='a', response=1.0, remaining=['c'])


class WordMeaningTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if no similar words are found.
        """
        assert word_meaning('go').parse(['boat', 'hello']) is None

    def test_match(self):
        """
        Tests the similar word is parsed.
        """
        assert word_meaning('go').parse(['boat', 'walk', 'hello']) == ParseResult(parsed='walk', response=0.5, remaining=['hello'])


class WordTaggedTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if no words with the tags are found.
        """
        parser = word_tagged(['CD', 'NN'])
        assert parser.parse(['go', 'listening']) is None

    def test_match(self):
        """
        Tests the word is returned if it matches any of the tags.
        """
        parser = word_tagged(['NN'])
        assert parser.parse(['go', 'tree', 'listening']) == ParseResult(parsed='tree', response=1.0, remaining=['listening'])


class StrongestTestCase(unittest.TestCase):
    def test_chooses_strongest_from_unique(self):
        p1 = produce('a', 0.1)
        p2 = produce('b', 0.8)
        p3 = produce('c', 0.4)

        parser = strongest([p1, p2, p3])

        assert parser.parse([]) == ParseResult(parsed='b', response=0.8, remaining=[])

    def test_chooses_first_strongest(self):
        p1 = produce('a', 0.8)
        p2 = produce('b', 0.8)
        p3 = produce('c', 0.4)

        parser = strongest([p1, p2, p3])

        assert parser.parse([]) == ParseResult(parsed='a', response=0.8, remaining=[])


class AnywhereTestCase(unittest.TestCase):
    def test_input_is_unchanged(self):
        """
        Tests even if the input will be consumed by a parser, that by wrapping said parser in an `anywhere` parser
        none of the input text is consumed.
        """
        s = ['b', 'a', 'c']
        parser = anywhere(word_match('a'))

        assert parser.parse(s) == ParseResult(parsed='a', response=1.0, remaining=s)


class MaybeTestCase(unittest.TestCase):
    def test_replaces_none_result(self):
        """
        Tests that if a parser returns None, that the result is replaced with an empty result with zero response.
        """
        parser = maybe(failure())
        assert parser.parse(['a', 'b']) == ParseResult(parsed=None, response=0.0, remaining=['a', 'b'])


    def test_no_replace_result(self):
        """
        Tests the result of a parser is not replaced if it result is not None.
        """
        parser = maybe(produce('a', 0.5))
        assert parser.parse(['b', 'c']) == ParseResult(parsed='a', response=0.5, remaining=['b', 'c'])


class ManyTestCase(unittest.TestCase):
    def test_none_parsed(self):
        """
        Tests the base case of the many parser.
        """
        p = word_match('a')
        s = 'b c d'.split()

        assert many(p).parse(s) == ParseResult([], 1, ['b', 'c', 'd'])

    def test_single_parsed(self):
        p = word_match('a')
        s = 'a b c'.split()

        assert many(p).parse(s) == ParseResult(['a'], 1, ['b', 'c'])

    def test_multiple_parsed(self):
        p = word_match('a')
        s = 'a b a c a d'.split()

        assert many(p).parse(s) == ParseResult(['a', 'a', 'a'], 1, ['d'])

    def test_order(self):
        p = word_meaning('hello')
        s = 'hi x hello y'.split()

        assert many(p).parse(s) == ParseResult(['hi', 'hello'], 1, ['y'])


class SomeTestCase(unittest.TestCase):
    def test_failure(self):
        """
        Tests the parser fails if the parser doesn't match at least once.
        """
        p = word_match('a')
        s = 'b c'

        assert some(p).parse(s) is None

    def test_single_parsed(self):
        p = word_match('a')
        s = 'a b c'.split()

        assert some(p).parse(s) == ParseResult(['a'], 1, ['b', 'c'])

    def test_multiple_parsed(self):
        p = word_match('a')
        s = 'a b a c a d'.split()

        assert some(p).parse(s) == ParseResult(['a', 'a', 'a'], 1, ['d'])

    def test_order(self):
        p = word_meaning('hello')
        s = 'hi x hello y'.split()

        assert some(p).parse(s) == ParseResult(['hi', 'hello'], 1, ['y'])


class SepByTestCase(unittest.TestCase):
    def test_failure(self):
        p = word_match('a')
        sep = word_match(',')

        s = 'b c'.split()

        assert sep_by(p, sep).parse(s) is None

    def test_single(self):
        p = word_match('a')
        sep = word_match('X')

        s = 'a b c'.split()

        assert sep_by(p, sep).parse(s) == ParseResult(['a'], 1, ['b', 'c'])

    def test_multiple(self):
        p = word_match('a')
        sep = word_match('X')

        s = 'a X a b c'.split()

        assert sep_by(p, sep).parse(s) == ParseResult(['a', 'a'], 1, ['b', 'c'])

    def test_separator_at_end(self):
        p = word_match('a')
        sep = word_match('X')

        s = 'a X a X b c'.split()

        assert sep_by(p, sep).parse(s) == ParseResult(['a', 'a'], 1, ['X', 'b', 'c'])
