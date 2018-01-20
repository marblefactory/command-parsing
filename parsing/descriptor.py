from typing import List
from functools import reduce
from parsing.parser import nltk_tagged


class Descriptor:
    """
    Produces a response when applied to a text.
    """

    def response(self, tokens: List[str]) -> float:
        """
        :param tokens: the words in the text.
        :return: the non-normalised response of the descriptor on the text. I.e. this does not need to be in the
                 range 0-1. However, it does need to be in the range 0-max_response
        """
        raise NotImplementedError

    def max_response(self) -> int:
        """
        :return: the maximum response which the descriptor can give.
        """
        raise NotImplementedError

    def normalised_response(self, tokens: List[str]) -> float:
        """
        :param tokens: the words in the text.
        :return: the response normalised to be in the range 0-1.
        """
        return self.response(tokens) / self.max_response()


class Threshold(Descriptor):
    """
    Produces a response when the given descriptor produces a response over or equal to a threshold.
    """
    def __init__(self, parser: Descriptor, threshold: float):
        self.parser = parser
        self.threshold = threshold

    def response(self, tokens: List[str]) -> float:
        """
        :param tokens: the words in the text.
        :return: the response of the descriptor if the response is over a threshold, otherwise 0.
        """
        return 1 if self.parser.response(tokens) >= self.threshold else 0

    def max_response(self) -> float:
        return 1


class Word(Descriptor):
    """
    Matches based on individual words in a text.
    """

    word: str

    def __init__(self, word: str):
        """
        :param word: the word to be matched over the text.
        """
        self.word = word

    @classmethod
    def list_from_words(cls, words: List[str]) -> List['Word']:
        """
        :return: a list of word descriptors from the list of words.
        """
        return [cls(word) for word in words]


class WordMatch(Word):
    """
    Matches on words in a text.
    """

    def __init__(self, word: str):
        super(WordMatch, self).__init__(word)

    def response(self, tokens: List[str]) -> float:
        """
        :param tokens: the words in the text.
        :return: 1 if the word is present in the text, otherwise 0.
        """
        matched_words = [w for w in tokens if w == self.word]
        return float(len(matched_words) >= 1)

    def max_response(self) -> float:
        return 1


# class WordMeaning(Word):
#     """
#     Generates a response based on semantic similarity between words.
#     """
#
#     def __init__(self, word: str):
#         super(WordMeaning, self).__init__(word)
#
#     def response(self, text: str) -> float:
#         def similarity(synset1, synset2) -> float:
#             """
#             :return: the maximum semantic similarity between the two synsets.
#             """
#             maximum = 0
#             for s1 in synset1:
#                 for s2 in synset2:
#                     sim = s1.wup_similarity(s2) or 0
#                     maximum = sim if sim > maximum else maximum
#
#             return maximum
#
#         word_synsets = wn.synsets(self.word)
#         sentence_synsets = [wn.synsets(w) for w in text.split()]
#         similarities = [similarity(word_synsets, synsets) for synsets in sentence_synsets]
#         return min(similarities)

class WordTag(Descriptor):
    """
    Matches on words with the given NLTK tag.
    """

    def __init__(self, tag: str):
        self.tag = tag

    def response(self, tokens: List[str]) -> float:
        """
        :param tokens: the words in the text.
        :return: the number of words matching the tag in the text.
        """
        num_tagged = len(nltk_tagged(self.tag, tokens))
        return float(num_tagged >= 1)

    def max_response(self) -> float:
        return 1


class Number(WordTag):
    """
    Matches on numbers (e.g. 102) in a text.
    """

    def __init__(self):
        super(Number, self).__init__('CD')  # Matches on Cardinal Numbers.


class Composite(Descriptor):
    """
    Matches using multiple descriptors.
    """

    def __init__(self, parsers: List[Descriptor]):
        self.ps = parsers

    def initial_response(self) -> float:
        """
        :return: the initial value of the accumulated response.
        """
        raise NotImplementedError

    def combine_responses(self, acc_response: float, new_response: float) -> float:
        """
        :param acc_response: the currently accumulated response.
        :param new_response: the new response.
        :return: the result of combining the accumulated response with the new response.
        """
        raise NotImplementedError

    def response(self, tokens: List[str]) -> float:
        curr_response = self.initial_response()
        for parser in self.ps:
            response = parser.response(tokens)
            curr_response = self.combine_responses(curr_response, response)

        return curr_response


class SomeOf(Composite):
    """
    Matches on text more strongly as more descriptors match on the text.
    """

    def __init__(self, parsers: List[Descriptor]):
        """
        :param parsers: the parsers for which the responses will be summed.
        """
        super(SomeOf, self).__init__(parsers)

    def initial_response(self) -> float:
        return 0

    def combine_responses(self, acc_response: float, new_response: float) -> float:
        return acc_response + new_response

    def max_response(self) -> float:
        """
        :return: the maximum response, i.e. the sum of all maximum responses of all descriptors.
        """
        return sum([parser.max_response() for parser in self.ps])


class AllOf(Composite):
    """
    Matches on text more strongly the more descriptors give a response. If any do not give a response then the final
    response will be 0.
    """

    def __init__(self, parsers: List[Descriptor]):
        super(AllOf, self).__init__(parsers)

    def initial_response(self) -> float:
        return 1

    def combine_responses(self, acc_response: float, new_response: float) -> float:
        return acc_response * new_response

    def max_response(self) -> float:
        return reduce((lambda p1, p2: p1.max_response() * p2.max_response()), self.ps)


class NoneOf(Composite):
    """
    Matches on text more strongly if the parsers supplied don't match on the text.
    """

    def __init__(self, parsers: List[Descriptor]):
        super(NoneOf, self).__init__(parsers)

    def initial_response(self) -> float:
        return 1

    def combine_responses(self, acc_response: float, new_response: float) -> float:
        return acc_response * (1 - new_response)

    def max_response(self) -> float:
        return 1


class OneOf(Descriptor):
    """
    Matches only if one descriptor matches.
    """

    def __init__(self, parsers: List[Descriptor]):
        """
        :param parsers: the list of parsers to match. There must be at least 2.
        """

        assert len(parsers) >= 2

        self.ps = parsers

    def response(self, tokens: List[str]) -> float:
        """
        :param tokens: the words in the text.
        :return: the value of descriptor D if D is the only descriptor to give a non-zero response, otherwise 0.
        """
        responses = sorted([parser.response(tokens) for parser in self.ps])

        # If the second to last element is zero, it means either there was a response from only one descriptor, or
        # no descriptors responded.
        if responses[-2] == 0:
            return responses[-1]

        return 0

    def max_response(self) -> float:
        """
        :return: a maximum response out of all descriptors, i.e. because only one descriptor can respond.
        """
        max_responses = [parser.max_response() for parser in self.ps]
        return max(max_responses)


class Contextual(OneOf):
    """
    Matches on positional words, e.g. next, first, second, etc.
    """

    def __init__(self):
        words = ['next', 'first', 'second', 'third', 'fourth']
        ds = WordMatch.list_from_words(words)

        super(Contextual, self).__init__(ds)
