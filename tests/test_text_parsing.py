import unittest
from text_parsing import *


class MockParser(Parser):
    """
    Returns the supplied response for every string.
    """
    def __init__(self, response: float):
        self.r = response

    def response(self, text: str) -> float:
        return self.r

    def max_response(self) -> float:
        return 1


class ThresholdTestCase(unittest.TestCase):

    def descriptor(self, value: float):
        return Threshold(MockParser(value), 0.5)

    def test_below_threshold(self):
        assert self.descriptor(0.1).response(' ') == 0

    def test_on_threshold(self):
        assert self.descriptor(0.5).response(' ') == 1

    def test_above_threshold(self):
        assert self.descriptor(0.7).response(' ') == 1

    def test_normalised_response(self):
        assert self.descriptor(0.7).normalised_response(' ') == 1


class WordMatchTestCase(unittest.TestCase):

    def descriptor(self):
        return WordMatch('hello')

    def test_no_response(self):
        assert self.descriptor().response('my sentence') == 0

    def test_single(self):
        assert self.descriptor().response('hello world') == 1

    def test_multiple(self):
        assert self.descriptor().response('hello world hello') == 1

    def test_normalised_response(self):
        assert self.descriptor().normalised_response('hello word') == 1


# class WordMeaningDistanceMeasureTestCase(unittest.TestCase):
#     """
#     Tests WordMeaning
#     """
#
#     def descriptor(self):
#         return WordMeaning('crouching')
#
#     def test_single_small(self):
#         assert self.descriptor().response('go') == 0.25
#
#     def test_single_large(self):
#         assert self.descriptor().response('crouching') == 1.0
#
#     def test_multiple(self):
#         assert self.descriptor().response('crouch crouching') == 1.0


class AndTestCase(unittest.TestCase):

    def descriptor(self):
        words = WordMatch.list_from_words(['hello', 'world'])
        return And(words)

    def test_no_response(self):
        print(self.descriptor().response('my sentence'))
        assert self.descriptor().response('my sentence') == 0

    def test_single(self):
        assert self.descriptor().response('hello sentence') == 1

    def test_single_order_invariant(self):
        assert self.descriptor().response('sentence hello') == 1

    def test_multiple(self):
        assert self.descriptor().response('hello world') == 2

    def test_multiple_order_invariant(self):
        assert self.descriptor().response('world hello') == 2

    def test_extra_word_invariant(self):
        assert self.descriptor().response('hello extra world extra') == 2

    def test_normalised_response(self):
        assert self.descriptor().normalised_response('hello sentence') == 0.5

    def test_normalised_response_extra_word_invariant(self):
        assert self.descriptor().normalised_response('hello extra world extra') == 1

    def test_normalised_response_nested(self):
        and1 = And(WordMatch.list_from_words(['a', 'b']))
        and2 = And([and1, WordMatch('c')])

        assert and2.normalised_response('a b c') == 1


class PositionalTestCase(unittest.TestCase):

    def descriptor(self):
        return Positional()

    def test_no_response(self):
        assert self.descriptor().response('take the door') == 0

    def test_single(self):
        assert self.descriptor().response('take the first door') == 1

    def test_multiple(self):
        assert self.descriptor().response('take the first second door') == 0

    def test_normalised_response(self):
        assert self.descriptor().normalised_response('take the first door') == 1


class WordTagTestCase(unittest.TestCase):

    def descriptor(self):
        """
        :return: a descriptor which matches on nouns.
        """
        return WordTag('NN')

    def test_no_response(self):
        assert self.descriptor().response('flying') == 0

    def test_single(self):
        assert self.descriptor().response('flying car') == 1

    def test_multiple(self):
        assert self.descriptor().response('flying car table') == 1

    def test_normalised_response(self):
        assert self.descriptor().normalised_response('flying car') == 1


class NumberTestCase(unittest.TestCase):

    def descriptor(self):
        return Number()

    def test_no_response(self):
        assert self.descriptor().response('number') == 0

    def test_single(self):
        assert self.descriptor().response('105') == 1

    def test_multiple(self):
        assert self.descriptor().response('Room 802 and 700') == 1

    def test_normalised_response(self):
        assert self.descriptor().normalised_response('105') == 1


class OneOfTestCase(unittest.TestCase):

    def descriptor(self):
        return OneOf([WordMatch('left'), WordMatch('right')])

    def test_no_response(self):
        assert self.descriptor().response('go forwards') == 0

    def test_single1(self):
        assert self.descriptor().response('go left') == 1

    def test_single2(self):
        assert self.descriptor().response('go right') == 1

    def test_multiple(self):
        assert self.descriptor().response('go left right') == 0

    def test_normalised_response(self):
        and_descriptor = And(WordMatch.list_from_words(['a', 'b'])) # Max Response = 2
        one_of = OneOf([and_descriptor, WordMatch('c')])            # Max Response = 1
        assert one_of.normalised_response('a') == 0.5


class NoneOfTestCase(unittest.TestCase):

    def descriptor(self):
        return NoneOf([WordMatch('hello'), WordMatch('world')])

    def test_no_response1(self):
        assert self.descriptor().response('hello') == 0

    def test_no_response2(self):
        assert self.descriptor().response('world') == 0

    def test_no_response3(self):
        assert self.descriptor().response('hello the world is blue') == 0

    def test_response(self):
        assert self.descriptor().response('no matched words in here') == 1

    def test_response_if_empty(self):
        assert self.descriptor().response('') == 1

    def test_normalised_response(self):
        assert self.descriptor().normalised_response('no matched words') == 1


class AllOfTestCase(unittest.TestCase):

    def descriptor(self):
        return AllOf(WordMatch.list_from_words(['hello', 'world']))

    def test_no_response1(self):
        assert self.descriptor().response('nothing') == 0

    def test_no_response2(self):
        assert self.descriptor().response('hello') == 0

    def test_no_response3(self):
        assert self.descriptor().response('word') == 0

    def test_response(self):
        assert self.descriptor().response('hello world') == 1
