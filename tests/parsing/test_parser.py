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
        parser = produce('a', 0.0).then_ignore(produce('b', 1.0), mix)

        assert parser.parse([]) == ParseResult(parsed='a', response=0.5, remaining=[])

    def test_then_ignore_default_response(self):
        parser = produce('a', 0.5).then_ignore(produce('b', 1.0))

        assert parser.parse([]) == ParseResult(parsed='a', response=0.5, remaining=[])

    def test_ignore_then(self):
        # Ignore the parsed 'a', but average the responses.
        parser = produce('a', 1.0).ignore_then(produce('b', 0.0), mix)

        assert parser.parse([]) == ParseResult(parsed='b', response=0.5, remaining=[])

    def test_ignore_then_default_response(self):
        parser = produce('a', 0.5).ignore_then(produce('b', 1.0))

        assert parser.parse([]) == ParseResult(parsed='b', response=1.0, remaining=[])

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
    def test_none_if_all_zero(self):
        def condition(input_word: Word) -> Response:
            return 0.0

        assert predicate(condition).parse(['a']) is None

    def test_none_if_empty(self):
        def condition(input_word: Word) -> Response:
            return 1.0

        assert predicate(condition).parse([]) is None

    def test_matches_highest(self):
        def condition(input_word: Word) -> Response:
            if input_word == 'a':
                return 0.1
            elif input_word == 'b':
                return 0.8
            else:
                return 0.2

        assert predicate(condition).parse(['a', 'b', 'c']) == ParseResult('b', 0.8, ['c'])


class WordEditDistTestCase(unittest.TestCase):
    def test_no_match1(self):
        """
        Tests None is returned if the words share no similarities.
        """
        assert word_edit_dist('aaa').parse(['bbb', 'ccc']) is None

    def test_no_match_not_same_first(self):
        """
        Tests None is returned if the words do not have the same first letter.
        """
        assert word_edit_dist('hello').parse(['dello', 'mello']) is None

    def test_match_some(self):
        """
        Tests the parser matches when some of the letters are correct.
        """
        assert word_edit_dist('aaaa').parse(['abbb', 'cccc']) == ParseResult('aaaa', 0.25, ['cccc'])

    def test_match_all(self):
        """
        Tests the parse matches when all of the letters are correct.
        """
        assert word_edit_dist('aaaa').parse(['aaaa', 'cccc']) == ParseResult('aaaa', 1.0, ['cccc'])

    def test_matches_strongest(self):
        """
        Tests the parse matches on the word with the lowest edit distance.
        """
        assert word_edit_dist('aaaa').parse(['abbb', 'aacc']) == ParseResult('aaaa', 0.5, [])


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

    def test_matches_plural_default(self):
        assert word_match('hack').parse(['hacks', 'hello']) == ParseResult(parsed='hacks', response=1.0, remaining=['hello'])

    def test_does_not_match_plural(self):
        assert word_match('hack', match_plural=False).parse(['hacks', 'hello']) is None


class WordMeaningTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if no similar words are found.
        """
        assert word_meaning('orange').parse(['boat', 'hello']) is None

    def test_match(self):
        """
        Tests the similar word is parsed.
        """
        p = word_meaning('hi')
        assert p.parse(['boat', 'walk', 'hello']) == ParseResult(parsed='hello', response=1.0, remaining=[])


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


class CardinalNumberTestCase(unittest.TestCase):
    def test_match(self):
        assert cardinal_number().parse(['201', 'hello']) == ParseResult(parsed='201', response=1.0, remaining=['hello'])


class StringNumberTestCase(unittest.TestCase):
    def test_match_one(self):
        assert string_number().parse(['one']).parsed == '1'

    def test_match_two(self):
        assert string_number().parse(['two']).parsed == '2'

    def test_match_two_alt1(self):
        assert string_number().parse(['to']).parsed == '2'

    def test_match_two_alt2(self):
        assert string_number().parse(['too']).parsed == '2'

    def test_match_four(self):
        assert string_number().parse(['four']).parsed == '4'

    def test_match_four_alt1(self):
        assert string_number().parse(['for']).parsed == '4'


class NumberTestCase(unittest.TestCase):
    def test_match_cardinal(self):
        assert number().parse(['201', 'hello']).parsed == '201'

    def test_match_string(self):
        assert number().parse(['three', 'hello']).parsed == '3'


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


class StrongestWordTestCase(unittest.TestCase):
    def test_match_strongest_word(self):
        s = 'a b c'.split()
        assert strongest_word(['b', 'x']).parse(s).parsed == 'b'

    def test_cartesian_product_of_parser_constructors1(self):
        """
        Tests that every parser constructor is combined with every word to match on.
        """
        s = 'orange hillo'.split()
        parser = strongest_word(['blue', 'hello'], parser_constructors=[word_edit_dist, word_meaning])
        assert parser.parse(s).parsed == 'hello'

    def test_cartesian_product_of_parser_constructors2(self):
        """
        Tests that every parser constructor is combined with every word to match on.
        """
        s = 'run whale'.split()
        parser = strongest_word(['go', 'hi'], parser_constructors=[word_edit_dist, word_meaning])
        assert parser.parse(s).parsed == 'run'


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


class ThresholdTestCase(unittest.TestCase):
    def test_below_threshold(self):
        parser = threshold(produce('a', 0.1), response_threshold=0.5)
        assert parser.parse([]) is None

    def test_on_threshold(self):
        parser = threshold(produce('a', 0.5), response_threshold=0.5)
        assert parser.parse([]) is None

    def test_above_threshold(self):
        parser = threshold(produce('a', 0.6), response_threshold=0.5)
        assert parser.parse(['a', 'b']) == ParseResult('a', 0.6, ['a', 'b'])


class AppendTestCase(unittest.TestCase):
    def test_parse(self):
        p1 = word_match('hello')
        p2 = word_match('world')
        p3 = word_match('!')

        p = p1.then(append(p2)).then(append(p3))
        s = ['hello', 'world', '!', 'c']

        assert p.parse(s) == ParseResult('hello world !', 1, ['c'])

    def test_parse_no_spaces(self):
        p1 = word_match('hello')
        p2 = word_match('world')
        p3 = word_match('!')

        p = p1.then(append(p2)).then(append(p3, spaces=False))
        s = ['hello', 'world', '!', 'c']

        assert p.parse(s) == ParseResult('hello world!', 1, ['c'])

    def test_combine_responses(self):
        p1 = produce('x', 0.5)
        p2 = produce('y', 1.0)

        p = p1.then(append(p2, mix))

        assert p.parse([]) == ParseResult('x y', 0.75, [])

    def test_response_default(self):
        p1 = produce('x', 0.5)
        p2 = produce('y', 1.0)

        p = p1.then(append(p2))

        assert p.parse([]) == ParseResult('x y', 0.5, [])