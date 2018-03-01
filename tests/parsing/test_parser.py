import unittest
from parsing.parser import *
from nltk.corpus import wordnet as wn


class ParserTestCase(unittest.TestCase):
    def test_then(self):
        # Take a parser, keep the parse result, but set the response to zero.
        def f(parsed: str, response) -> Parser:
            return produce(parsed, 0.0)

        parser = produce('a', 1.0).then(f)

        assert parser.parse(['b']) == SuccessParse(parsed='a', response=0.0, remaining=['b'])

    def test_then_ignore(self):
        # Ignore the parsed 'b', but average the responses.
        parser = produce('a', 0.0).then_ignore(produce('b', 1.0), mix)

        assert parser.parse([]) == SuccessParse(parsed='a', response=0.5, remaining=[])

    def test_then_ignore_default_response(self):
        parser = produce('a', 0.5).then_ignore(produce('b', 1.0))

        assert parser.parse([]) == SuccessParse(parsed='a', response=0.5, remaining=[])

    def test_ignore_then(self):
        # Ignore the parsed 'a', but average the responses.
        parser = produce('a', 1.0).ignore_then(produce('b', 0.0), mix)

        assert parser.parse([]) == SuccessParse(parsed='b', response=0.5, remaining=[])

    def test_ignore_then_default_response(self):
        parser = produce('a', 0.5).ignore_then(produce('b', 1.0))

        assert parser.parse([]) == SuccessParse(parsed='b', response=1.0, remaining=[])

    def test_map(self):
        parser = produce('a', 1.0).map(lambda p, r: (p + 'bc', r / 2))

        assert parser.parse([]) == SuccessParse(parsed='abc', response=0.5, remaining=[])

    def test_map_parsed(self):
        parser = produce('a', 0.8).map_parsed(lambda p: 'x' + p)

        assert parser.parse([]) == SuccessParse(parsed='xa', response=0.8, remaining=[])

    def test_map_response(self):
        parser = produce('a', 0.8).map_response(lambda r: r / 2)

        assert parser.parse([]) == SuccessParse(parsed='a', response=0.4, remaining=[])

    def test_ignore_parsed_captures_state(self):
        letter = 'b'
        parser = produce('a', 0.8).ignore_parsed(letter)
        letter = 'c'

        assert parser.parse([]) == SuccessParse(parsed='b', response=0.8, remaining=[])


class PredicateTestCase(unittest.TestCase):
    def test_none_if_all_zero(self):
        def condition(input_word: Word) -> Response:
            return 0.0

        assert predicate(condition).parse(['a']).is_failure()

    def test_none_if_empty(self):
        def condition(input_word: Word) -> Response:
            return 1.0

        assert predicate(condition).parse([]).is_failure()

    def test_matches_highest(self):
        def condition(input_word: Word) -> Response:
            if input_word == 'a':
                return 0.1
            elif input_word == 'b':
                return 0.8
            else:
                return 0.2

        assert predicate(condition).parse(['a', 'b', 'c']) == SuccessParse('b', 0.8, ['c'])


class WordEditDistTestCase(unittest.TestCase):
    def test_no_match1(self):
        """
        Tests None is returned if the words share no similarities.
        """
        assert word_spelling('aaa', dist_threshold=0).parse(['bbb', 'ccc']).is_failure()

    def test_no_match_not_same_first(self):
        """
        Tests None is returned if the words do not have the same first letter.
        """
        assert word_spelling('hello', dist_threshold=0).parse(['dello', 'mello']).is_failure()

    def test_match_some(self):
        """
        Tests the parser matches when some of the letters are correct.
        """
        assert word_spelling('aaaa', dist_threshold=0).parse(['abbb', 'cccc']) == SuccessParse('aaaa', 0.25, ['cccc'])

    def test_match_all(self):
        """
        Tests the parse matches when all of the letters are correct.
        """
        assert word_spelling('aaaa', dist_threshold=0).parse(['aaaa', 'cccc']) == SuccessParse('aaaa', 1.0, ['cccc'])

    def test_matches_strongest(self):
        """
        Tests the parse matches on the word with the lowest edit distance.
        """
        assert word_spelling('aaaa', dist_threshold=0).parse(['abbb', 'aacc']) == SuccessParse('aaaa', 0.5, [])


class WordMatchTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if the word is nowhere in the input text.
        """
        assert word_match('a').parse(['b', 'c']).is_failure()

    def test_match(self):
        """
        Tests the word is parsed if it is in the input text.
        """
        assert word_match('a').parse(['b', 'a', 'c']) == SuccessParse(parsed='a', response=1.0, remaining=['c'])

    def test_matches_plural_default(self):
        assert word_match('hack').parse(['hacks', 'hello']) == SuccessParse(parsed='hacks', response=1.0, remaining=['hello'])

    def test_does_not_match_plural(self):
        assert word_match('hack', match_plural=False).parse(['hacks', 'hello']).is_failure()


class WordMeaningTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if no similar words are found.
        """
        assert word_meaning('orange').parse(['boat', 'hello']).is_failure()

    def test_match(self):
        """
        Tests the similar word is parsed.
        """
        p = word_meaning('hi')
        assert p.parse(['boat', 'walk', 'hello']) == SuccessParse(parsed='hello', response=1.0, remaining=[])


class WordTaggedTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if no words with the tags are found.
        """
        parser = word_tagged(['CD', 'NN'])
        assert parser.parse(['go', 'listening']).is_failure()

    def test_match(self):
        """
        Tests the word is returned if it matches any of the tags.
        """
        parser = word_tagged(['NN'])
        assert parser.parse(['go', 'tree', 'listening']) == SuccessParse(parsed='tree', response=1.0, remaining=['listening'])


class CardinalNumberTestCase(unittest.TestCase):
    def test_match(self):
        assert cardinal_number().parse(['201', 'hello']) == SuccessParse(parsed='201', response=1.0, remaining=['hello'])


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
    def strongest_parser(self, parsers: List[Parser]) -> Parser:
        return strongest(parsers)

    def test_chooses_strongest_from_unique(self):
        p1 = produce('a', 0.1)
        p2 = produce('b', 0.8)
        p3 = produce('c', 0.4)
        parser = self.strongest_parser([p1, p2, p3])

        assert parser.parse([]) == SuccessParse(parsed='b', response=0.8, remaining=[])

    def test_chooses_first_strongest(self):
        p1 = produce('a', 0.8)
        p2 = produce('b', 0.8)
        p3 = produce('c', 0.4)
        parser = self.strongest_parser([p1, p2, p3])

        assert parser.parse([]) == SuccessParse(parsed='a', response=0.8, remaining=[])

    def test_no_parse(self):
        p1 = word_match('a')
        p2 = word_match('b')
        parser = self.strongest_parser([p1, p2])

        s = 'x y z'.split()
        assert parser.parse(s).is_failure()

    def test_prefers_success_to_partial_results(self):
        p1 = partial_parser(word_match('b'), response=1.0)
        p2 = word_match('a')
        parser = self.strongest_parser([p1, p2])

        s = 'a'.split()
        assert parser.parse(s).parsed == 'a'


class StrongestWordTestCase(unittest.TestCase):
    def test_match_strongest_word(self):
        s = 'a b c'.split()
        assert strongest_word(['b', 'x']).parse(s).parsed == 'b'

    def test_cartesian_product_of_parser_constructors1(self):
        """
        Tests that every parser constructor is combined with every word to match on.
        """
        s = 'orange hillo'.split()
        parser = strongest_word(['blue', 'hello'], parser_constructors=[word_spelling, word_meaning])
        assert parser.parse(s).parsed == 'hello'

    def test_cartesian_product_of_parser_constructors2(self):
        """
        Tests that every parser constructor is combined with every word to match on.
        """
        s = 'run whale'.split()
        parser = strongest_word(['go', 'hi'], parser_constructors=[word_spelling, word_meaning])
        assert parser.parse(s).parsed == 'run'


class AnywhereTestCase(unittest.TestCase):
    def test_input_is_unchanged(self):
        """
        Tests even if the input will be consumed by a parser, that by wrapping said parser in an `anywhere` parser
        none of the input text is consumed.
        """
        s = ['b', 'a', 'c']
        parser = anywhere(word_match('a'))

        assert parser.parse(s) == SuccessParse(parsed='a', response=1.0, remaining=s)


class MaybeTestCase(unittest.TestCase):
    def test_replaces_none_result(self):
        """
        Tests that if a parser returns None, that the result is replaced with an empty result with zero response.
        """
        parser = maybe(failure())
        assert parser.parse(['a', 'b']) == SuccessParse(parsed=None, response=0.0, remaining=['a', 'b'])


    def test_no_replace_result(self):
        """
        Tests the result of a parser is not replaced if it result is not None.
        """
        parser = maybe(produce('a', 0.5))
        assert parser.parse(['b', 'c']) == SuccessParse(parsed='a', response=0.5, remaining=['b', 'c'])


class ThresholdTestCase(unittest.TestCase):
    def test_below_threshold(self):
        parser = threshold(produce('a', 0.1), response_threshold=0.5)
        assert parser.parse([]).is_failure()

    def test_on_threshold(self):
        parser = threshold(produce('a', 0.5), response_threshold=0.5)
        assert parser.parse([]).is_failure()

    def test_above_threshold(self):
        parser = threshold(produce('a', 0.6), response_threshold=0.5)
        assert parser.parse(['a', 'b']) == SuccessParse('a', 0.6, ['a', 'b'])


class AppendTestCase(unittest.TestCase):
    def test_parse(self):
        p1 = word_match('hello')
        p2 = word_match('world')
        p3 = word_match('!')

        p = p1.then(append(p2)).then(append(p3))
        s = ['hello', 'world', '!', 'c']

        assert p.parse(s) == SuccessParse('hello world !', 1, ['c'])

    def test_parse_no_spaces(self):
        p1 = word_match('hello')
        p2 = word_match('world')
        p3 = word_match('!')

        p = p1.then(append(p2)).then(append(p3, spaces=False))
        s = ['hello', 'world', '!', 'c']

        assert p.parse(s) == SuccessParse('hello world!', 1, ['c'])

    def test_combine_responses(self):
        p1 = produce('x', 0.5)
        p2 = produce('y', 1.0)

        p = p1.then(append(p2, mix))

        assert p.parse([]) == SuccessParse('x y', 0.75, [])

    def test_response_default(self):
        p1 = produce('x', 0.5)
        p2 = produce('y', 1.0)

        p = p1.then(append(p2))

        assert p.parse([]) == SuccessParse('x y', 0.5, [])


class NoneTestCase(unittest.TestCase):
    def test_parse_causes_fail(self):
        s = 'b a c'.split()
        p = none(word_match('a'))

        assert p.parse(s).is_failure()

    def test_no_parse_causes_empty_parse(self):
        s = 'x y z'.split()
        p = none(word_match('a'), response=0.5)

        assert p.parse(s) == SuccessParse(None, 0.5, ['x', 'y', 'z'])


class IgnoreWordsTestCase(unittest.TestCase):
    def test_removes_from_input(self):
        s = 'a b c d b c a b'.split()
        p = ignore_words(['b', 'a'])

        assert p.parse(s).remaining == ['c', 'd', 'c']


class PartialTestCase(unittest.TestCase):
    def test_success_if_matches(self):
        p = partial_parser(word_match('a'), response=0.7)
        s = 'b c a x'.split()

        assert p.parse(s) == SuccessParse('a', 1.0, ['x'])

    def test_partial_if_no_match(self):
        a_matcher = word_match('a')
        p = partial_parser(a_matcher, response=0.7)
        s = 'b c x'.split()

        assert p.parse(s) == PartialParse(a_matcher, response=0.7)
