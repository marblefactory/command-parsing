import unittest
from parsing.parser import *
from parsing.pre_processing import pre_process


class ParserTestCase(unittest.TestCase):
    def test_then(self):
        # Take a parser, keep the parse result, but set the response to zero.
        def f(parsed: str, response) -> Parser:
            return produce(parsed, 0.0)

        parser = produce('a', 1.0).then(f)
        s = pre_process('b')

        assert parser.parse(s) == SuccessParse(parsed='a', response=0.0, remaining=['b'])

    def test_then_ignore(self):
        # Ignore the parsed 'b', but average the responses.
        parser = produce('a', 0.0).then_ignore(produce('b', 1.0), mix)
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='a', response=0.5, remaining=[''])

    def test_then_ignore_default_response(self):
        parser = produce('a', 0.5).then_ignore(produce('b', 1.0))
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='a', response=0.5, remaining=[''])

    def test_ignore_then(self):
        # Ignore the parsed 'a', but average the responses.
        parser = produce('a', 1.0).ignore_then(produce('b', 0.0), mix)
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='b', response=0.5, remaining=[''])

    def test_ignore_then_default_response(self):
        parser = produce('a', 0.5).ignore_then(produce('b', 1.0))
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='b', response=1.0, remaining=[''])

    def test_map(self):
        parser = produce('a', 1.0).map(lambda p, r: (p + 'bc', r / 2))
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='abc', response=0.5, remaining=[''])

    def test_map_parsed(self):
        parser = produce('a', 0.8).map_parsed(lambda p: 'x' + p)
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='xa', response=0.8, remaining=[''])

    def test_map_response(self):
        parser = produce('a', 0.8).map_response(lambda r: r / 2)
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='a', response=0.4, remaining=[''])

    def test_ignore_parsed_captures_state(self):
        letter = 'b'
        parser = produce('a', 0.8).ignore_parsed(letter)
        # Change the letter to check that the letter returned by parser is still a 'b'
        letter = 'c'

        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='b', response=0.8, remaining=[''])


class WrapTestCase(unittest.TestCase):
    def test_wrap(self):
        def operation(parsed: str, response: Response) -> Parser:
            return produce('b', 1.0).map_parsed(lambda parsed2: parsed + parsed2)

        def wrapper(parser: Parser, response: Response) -> Parser:
            return parser.map(lambda parsed, response: (parsed + 'c', response / 2))

        parser = produce('a', 1.0).then(wrap(operation, wrapper))
        s = pre_process('')

        assert parser.parse(s) == SuccessParse(parsed='abc', response=0.5, remaining=[''])


class AppendTestCase(unittest.TestCase):
    def test_parse(self):
        p1 = word_match('hello')
        p2 = word_match('world')
        p3 = word_match('!')

        p = p1.then(append(p2)).then(append(p3))
        s = pre_process('hello world ! c')

        assert p.parse(s) == SuccessParse('hello world !', 1, ['c'])

    def test_parse_no_spaces(self):
        p1 = word_match('hello')
        p2 = word_match('world')
        p3 = word_match('!')

        p = p1.then(append(p2)).then(append(p3, spaces=False))
        s = pre_process('hello world ! c')

        assert p.parse(s) == SuccessParse('hello world!', 1, ['c'])

    def test_combine_responses(self):
        p1 = produce('x', 0.5)
        p2 = produce('y', 1.0)

        p = p1.then(append(p2, mix))

        s = pre_process('w')
        assert p.parse(s) == SuccessParse('x y', 0.75, ['w'])

    def test_response_default(self):
        p1 = produce('x', 0.5)
        p2 = produce('y', 1.0)

        p = p1.then(append(p2))

        s = pre_process('w')
        assert p.parse(s) == SuccessParse('x y', 0.5, ['w'])


class IndexArrayTestCase(unittest.TestCase):
    def test_in_bounds(self):
        s = pre_process('')
        array = ['a', 'b', 'c']
        p = produce(2, 0.5).then(index_array(array))

        assert p.parse(s) == SuccessParse('c', 0.5, [''])

    def test_out_of_bounds(self):
        s = pre_process('')
        array = ['a', 'b', 'c']
        p = produce(3, 0.5).then(index_array(array))

        assert p.parse(s).is_failure()


class PredicateTestCase(unittest.TestCase):
    def test_none_if_all_zero(self):
        def condition(input_word: Word) -> Response:
            return 0.0

        s = pre_process('a')
        assert predicate(condition).parse(s).is_failure()

    def test_none_if_empty(self):
        def condition(input_word: Word) -> Response:
            return 0.0 if input_word == 'a' else 1.0

        s = pre_process('a')
        assert predicate(condition).parse(s).is_failure()

    def test_matches_highest(self):
        def condition(input_word: Word) -> Response:
            if input_word == 'a':
                return 0.1
            elif input_word == 'b':
                return 0.8
            else:
                return 0.2

        s = pre_process('a b c')
        assert predicate(condition).parse(s) == SuccessParse('b', 0.8, ['c'])

    def test_matches_first_only(self):
        def condition(input_word: Word) -> Response:
            return 0.0 if input_word == 'a' else 1.0

        s = pre_process('a b')
        assert predicate(condition, first_only=False).parse(s).parsed == 'b'
        assert predicate(condition, first_only=True).parse(s).is_failure()

    def test_consume_word_only(self):
        def condition(input_word: Word) -> Response:
            return 1.0 if input_word == 'b' else 0.0

        s = pre_process('a b c')
        assert predicate(condition, consume=Consume.WORD_ONLY).parse(s) == SuccessParse('b', 1.0, ['a', 'c'])


class WordSpellingTestCase(unittest.TestCase):
    def test_no_match1(self):
        """
        Tests None is returned if the words share no similarities.
        """
        s = pre_process('bbb ccc')
        assert word_spelling('aaa', match_first_letter=True, dist_threshold=0, min_word_length=0).parse(s).is_failure()

    def test_no_match_not_same_first(self):
        """
        Tests None is returned if the words do not have the same first letter.
        """
        s = pre_process('dello mello')
        assert word_spelling('hello', match_first_letter=True, dist_threshold=0, min_word_length=0).parse(s).is_failure()

    def test_match_some(self):
        """
        Tests the parser matches when some of the letters are correct.
        """
        s = pre_process('abbb cccc')
        assert word_spelling('aaaa', match_first_letter=True, dist_threshold=0, min_word_length=0).parse(s) == SuccessParse('aaaa', 0.25, ['cccc'])

    def test_match_all(self):
        """
        Tests the parse matches when all of the letters are correct.
        """
        s = pre_process('aaaa cccc')
        assert word_spelling('aaaa', match_first_letter=True, dist_threshold=0, min_word_length=0).parse(s) == SuccessParse('aaaa', 1.0, ['cccc'])

    def test_matches_strongest(self):
        """
        Tests the parse matches on the word with the lowest edit distance.
        """
        s = pre_process('abbb aacc')
        assert word_spelling('aaaa', match_first_letter=True, dist_threshold=0, min_word_length=0).parse(s) == SuccessParse('aaaa', 0.5, [])

    def test_matches_first_only(self):
        s = pre_process('dello hello')
        assert word_spelling('hello', match_first_letter=True, dist_threshold=0, first_only=False, min_word_length=0).parse(s).parsed == 'hello'
        assert word_spelling('hello', match_first_letter=True, dist_threshold=0, first_only=True, min_word_length=0).parse(s).is_failure()

    def test_consume_word_only(self):
        s = pre_process('aa bb cc')
        assert word_spelling('bb', match_first_letter=True, consume=Consume.WORD_ONLY, min_word_length=0).parse(s) == SuccessParse('bb', 1.0, ['aa', 'cc'])

    def test_no_match_first_letter(self):
        s = pre_process('baaa')
        r = word_spelling('aaaa', match_first_letter=False, dist_threshold=0, min_word_length=0).parse(s)
        self.assertEqual(r, SuccessParse('aaaa', 0.75, []))

    def test_min_word_length(self):
        s = pre_process('up')
        r1 = word_spelling('cup', min_word_length=0).parse(s).parsed
        self.assertTrue(r1, 'cup')

        r2 = word_spelling('cup', min_word_length=3).parse(s)
        self.assertTrue(r2.is_failure())

    def test_plural(self):
        s = pre_process('clouds')
        r = word_spelling('cloud', match_plural=True).parse(s)

        self.assertEqual(r, SuccessParse('clouds', 1.0, []))


class WordMatchTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if the word is nowhere in the input text.
        """
        s = pre_process('b c')
        assert word_match('a').parse(s).is_failure()

    def test_match(self):
        """
        Tests the word is parsed if it is in the input text.
        """
        s = pre_process('b a c')
        assert word_match('a').parse(s) == SuccessParse(parsed='a', response=1.0, remaining=['c'])

    def test_matches_plural_default(self):
        s = pre_process('hacks hello')
        assert word_match('hack').parse(s) == SuccessParse(parsed='hack', response=1.0, remaining=['hello'])

    def test_does_not_match_plural(self):
        s = pre_process('hacks hello')
        assert word_match('hack', match_plural=False).parse(s).is_failure()

    def test_matches_word_with_numbers(self):
        s = pre_process('b o2 c')
        assert word_match('o2').parse(s) == SuccessParse(parsed='o2', response=1.0, remaining=['c'])

    def test_matches_first_only(self):
        s = pre_process('hello world')
        assert word_match('world', first_only=False).parse(s).parsed == 'world'
        assert word_match('world', first_only=True).parse(s).is_failure()

    def test_consume_word_only(self):
        s = pre_process('aa bb cc')
        assert word_match('bb', consume=Consume.WORD_ONLY).parse(s) == SuccessParse('bb', 1.0, ['aa', 'cc'])


class WordMeaningTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if no similar words are found.
        """
        s = pre_process('boat hello')
        assert word_meaning('orange').parse(s).is_failure()

    def test_match(self):
        """
        Tests the similar word is parsed.
        """
        p = word_meaning('hi')
        s = pre_process('boat walk hello')
        assert p.parse(s) == SuccessParse(parsed='hello', response=1.0, remaining=[])

    def test_filter_word_pos(self):
        """
        Tests that the supplied POS filters the considered words.
        """
        p1 = word_meaning('fly')
        p2 = word_meaning('fly', pos=POS.noun)

        s = pre_process('flying')

        assert p1.parse(s) == SuccessParse(parsed='flying', response=1.0, remaining=[])
        assert p2.parse(s).is_failure()

    def test_matches_first_only(self):
        s = pre_process('boat hello')
        assert word_meaning('hi', first_only=False).parse(s).parsed == 'hello'
        assert word_meaning('hi', first_only=True).parse(s).is_failure()

    def test_consume_word_only(self):
        p = word_meaning('hi', consume=Consume.WORD_ONLY)
        s = pre_process('boat hello walk')
        assert p.parse(s) == SuccessParse(parsed='hello', response=1.0, remaining=['boat', 'walk'])


class WordTaggedTestCase(unittest.TestCase):
    def test_no_match(self):
        """
        Tests None is returned if no words with the tags are found.
        """
        parser = word_tagged(['CD', 'NN'])
        s = pre_process('go listening')
        assert parser.parse(s).is_failure()

    def test_match(self):
        """
        Tests the word is returned if it matches any of the tags.
        """
        parser = word_tagged(['NN'])
        s = pre_process('go tree listening')
        assert parser.parse(s) == SuccessParse(parsed='tree', response=1.0, remaining=['listening'])

    def test_matches_first_only(self):
        s = pre_process('go tree')
        assert word_tagged(['NN'], first_only=False).parse(s).parsed == 'tree'
        assert word_tagged(['NN'], first_only=True).parse(s).is_failure()

    def test_consume_word_only(self):
        parser = word_tagged(['NN'], consume=Consume.WORD_ONLY)
        s = pre_process('go tree listening')
        assert parser.parse(s) == SuccessParse(parsed='tree', response=1.0, remaining=['go', 'listening'])


class PhraseTestCase(unittest.TestCase):
    def test_match(self):
        s = pre_process('a b')
        parser = phrase('a b')

        assert parser.parse(s).parsed == 'a b'

    def test_match_not_at_start(self):
        s = pre_process('c d a b c')
        parser = phrase('a b')

        assert parser.parse(s) == SuccessParse('a b', 1.0, ['c'])

    def test_fail_if_in_between(self):
        s = pre_process('a c b')
        parser = phrase('a b')

        assert parser.parse(s).is_failure()

class CardinalNumberTestCase(unittest.TestCase):
    def test_match(self):
        s = pre_process('201 hello')
        assert cardinal_number().parse(s) == SuccessParse(parsed=201, response=1.0, remaining=['hello'])


class StringNumberTestCase(unittest.TestCase):
    def test_match_zero(self):
        s = pre_process('zero')
        assert string_number().parse(s).parsed == 0

    def test_match_one(self):
        s = pre_process('one')
        assert string_number().parse(s).parsed == 1

    def test_match_two(self):
        s = pre_process('two')
        assert string_number().parse(s).parsed == 2

    def test_match_two_alt1(self):
        s = pre_process('to')
        assert string_number().parse(s).parsed == 2

    def test_match_two_alt2(self):
        s = pre_process('too')
        assert string_number().parse(s).parsed == 2

    def test_match_four(self):
        s = pre_process('four')
        assert string_number().parse(s).parsed == 4

    def test_match_four_alt1(self):
        s = pre_process('for')
        assert string_number().parse(s).parsed == 4


class NumberTestCase(unittest.TestCase):
    def test_match_cardinal(self):
        s = pre_process('201 hello')
        assert number().parse(s).parsed == 201

    def test_match_string(self):
        s = pre_process('three hello')
        assert number().parse(s).parsed == 3


class NumberStrTestCase(unittest.TestCase):
    def test_converts_to_string(self):
        s = pre_process('one')
        assert number_str().parse(s).parsed == '1'


class StrongestTestCase(unittest.TestCase):
    def strongest_parser(self, parsers: List[Parser]) -> Parser:
        return strongest(parsers)

    def test_chooses_strongest_from_unique(self):
        p1 = produce('a', 0.1)
        p2 = produce('b', 0.8)
        p3 = produce('c', 0.4)
        parser = self.strongest_parser([p1, p2, p3])

        s = pre_process('x')
        assert parser.parse(s) == SuccessParse(parsed='b', response=0.8, remaining=['x'])

    def test_chooses_first_strongest(self):
        p1 = produce('a', 0.8)
        p2 = produce('b', 0.8)
        p3 = produce('c', 0.4)
        parser = self.strongest_parser([p1, p2, p3])

        s = pre_process('x')
        assert parser.parse(s) == SuccessParse(parsed='a', response=0.8, remaining=['x'])

    def test_no_parse(self):
        p1 = word_match('a')
        p2 = word_match('b')
        parser = self.strongest_parser([p1, p2])

        s = pre_process('x y z')
        assert parser.parse(s).is_failure()

    def test_prefers_success_to_partial_results(self):
        p1 = partial_parser(word_match('b'), response=1.0, marker='Type')
        p2 = word_match('a')
        parser = self.strongest_parser([p1, p2])

        s = pre_process('a')
        assert parser.parse(s).parsed == 'a'

    def test_chooses_strongest_partial_from_unique(self):
        p1 = partial_parser(word_match('a'), 0.1, 'Type')
        p2 = partial_parser(word_match('b'), 0.8, 'Type')
        p3 = partial_parser(word_match('c'), 0.4, 'Type')
        parser = self.strongest_parser([p1, p2, p3])

        s = pre_process('x')
        assert parser.parse(s).response == 0.8


class StrongestWordTestCase(unittest.TestCase):
    def test_match_strongest_word(self):
        s = 'a b c'.split()
        s = pre_process('b x')
        assert strongest_word(s).parse(s).parsed == 'b'

    def test_cartesian_product_of_parser_constructors1(self):
        """
        Tests that every parser constructor is combined with every word to match on.
        """
        s = pre_process('orange hillo')
        parser = strongest_word(['blue', 'hello'], make_word_parsers=[word_spelling, word_meaning])
        assert parser.parse(s).parsed == 'hello'

    def test_cartesian_product_of_parser_constructors2(self):
        """
        Tests that every parser constructor is combined with every word to match on.
        """
        s = pre_process('run whale')
        parser = strongest_word(['go', 'hi'], make_word_parsers=[word_spelling, word_meaning])
        assert parser.parse(s).parsed == 'run'


class AnywhereTestCase(unittest.TestCase):
    def test_input_is_unchanged(self):
        """
        Tests even if the input will be consumed by a parser, that by wrapping said parser in an `anywhere` parser
        none of the input text is consumed.
        """
        s = pre_process('b a c')
        parser = non_consuming(word_match('a'))

        assert parser.parse(s) == SuccessParse(parsed='a', response=1.0, remaining=s)


class MaybeTestCase(unittest.TestCase):
    def test_replaces_none_result(self):
        """
        Tests that if a parser returns None, that the result is replaced with an empty result with zero response.
        """
        parser = maybe(failure())
        s = pre_process('a b')
        assert parser.parse(s) == SuccessParse(parsed=None, response=0.0, remaining=['a', 'b'])


    def test_no_replace_result(self):
        """
        Tests the result of a parser is not replaced if it result is not None.
        """
        parser = maybe(produce('a', 0.5))
        s = pre_process('b c')
        assert parser.parse(s) == SuccessParse(parsed='a', response=0.5, remaining=['b', 'c'])


class ThresholdTestCase(unittest.TestCase):
    def test_below_threshold(self):
        parser = threshold_success(produce('a', 0.1), response_threshold=0.5)
        s = pre_process('')
        assert parser.parse(s).is_failure()

    def test_on_threshold(self):
        parser = threshold_success(produce('a', 0.5), response_threshold=0.5)
        s = pre_process('')
        assert parser.parse(s).is_failure()

    def test_above_threshold(self):
        parser = threshold_success(produce('a', 0.6), response_threshold=0.5)
        s = pre_process('a b')
        assert parser.parse(s) == SuccessParse('a', 0.6, ['a', 'b'])


class NoneTestCase(unittest.TestCase):
    def test_parse_causes_fail(self):
        s = pre_process('b a c')
        p = none(word_match('a'))

        assert p.parse(s).is_failure()

    def test_no_parse_causes_empty_parse(self):
        s = pre_process('x y z')
        p = none(word_match('a'), response=0.5)

        assert p.parse(s) == SuccessParse(None, 0.5, ['x', 'y', 'z'])

    def test_parse_above_threshold(self):
        s = pre_process('')
        p = produce(parsed='DONE', response=0.5)
        n = none(p, max_parser_response=0.3)

        assert n.parse(s).is_failure()

    def test_parse_below_threshold(self):
        s = pre_process('')
        p = produce(parsed='DONE', response=0.2)
        n = none(p, max_parser_response=0.3)

        assert n.parse(s).parsed == 'DONE'


class IgnoreWordsTestCase(unittest.TestCase):
    def test_removes_from_input(self):
        s = pre_process('a b c d b c a b')
        p = ignore_words(['b', 'a'])

        assert p.parse(s).remaining == ['c', 'd', 'c']


class RestTestCase(unittest.TestCase):
    def test_rest(self):
        s = pre_process('a b c')
        r = rest().parse(s).parsed
        self.assertEqual(r, ['a', 'b', 'c'])

    def test_rest_fails(self):
        r = rest().parse([])
        self.assertTrue(r.is_failure())


class PartialTestCase(unittest.TestCase):
    def test_success_if_matches(self):
        p = partial_parser(word_match('a'), response=0.7, marker='MyType')
        s = pre_process('b c a x')

        assert p.parse(s) == SuccessParse('a', 1.0, ['x'])

    def test_partial_if_no_match(self):
        a_matcher = word_match('a')
        p = partial_parser(a_matcher, response=0.7, marker='MyType')
        s = pre_process('b c x')

        assert p.parse(s) == PartialParse(a_matcher, response=0.7, marker='MyType')


class ObjectSpelledTestCase(unittest.TestCase):
    def test_parses_object_name(self):
        s = pre_process('phone')
        p = object_spelled(['phone', 'car'], other_noun_response=0.2)

        assert p.parse(s).parsed == 'phone'

    def test_parses_object_response(self):
        s = pre_process('phone')
        p = object_spelled(['phone', 'car'], other_noun_response=0.2)

        assert p.parse(s).response == 1.0

    def test_parses_object_spelled_similar(self):
        s = pre_process('phon')
        p = object_spelled(['phone', 'car'], other_noun_response=0.2)

        assert p.parse(s).parsed == 'phone'

    def test_parses_object_spelled_similar_response(self):
        s = pre_process('phon')
        p = object_spelled(['phone', 'car'], other_noun_response=0.2)

        assert p.parse(s).response == 0.8

    def test_parses_other_nouns(self):
        s = pre_process('boat')
        p = object_spelled(['phone', 'car'], other_noun_response=0.2)

        assert p.parse(s).parsed == 'boat'

    def test_parses_other_nouns_response(self):
        s = pre_process('boat')
        p = object_spelled(['phone', 'car'], other_noun_response=0.2)

        assert p.parse(s).response == 0.2
