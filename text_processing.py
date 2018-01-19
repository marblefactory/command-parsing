import nltk
from typing import List, Optional, Type
from nltk.corpus import wordnet as wn
import numpy as np
from abc import abstractclassmethod


def name_in(text: str):
    """
    :param text: the text the user spoke.
    :return: the name of the object the user is referring to.
    """
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    nouns = [(i, word) for i, (word, word_tag) in enumerate(tagged) if word_tag == 'NN']

    if nouns is None:
        raise Exception('No place name found')

    i, noun = nouns[0]

    # Find the name of the room.
    if noun == 'room' and i+1 < len(tokens):
        room_name = tokens[i+1]
        return 'room ' + room_name

    return noun


def nltk_tagged(tag: str, text: str) -> List[str]:
    """
    :return: a list of words with the NLTK tag `tag` in `text`.
    """
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    return [word for (word, word_tag) in tagged if word_tag == tag]


class Descriptor:
    """
    Produces a response when applied to a text.
    """

    def response(self, text: str) -> float:
        """
        :return: the non-normalised response of the descriptor on the text. I.e. this does not need to be in the
                 range 0-1. However, it does need to be in the range 0-max_response
        """
        raise NotImplementedError

    def max_response(self) -> int:
        """
        :return: the maximum response which the descriptor can give.
        """
        raise NotImplementedError

    def normalised_response(self, text: str) -> float:
        """
        :return: the response normalised to be in the range 0-1.
        """
        return self.response(text) / self.max_response()


class Threshold(Descriptor):
    """
    Produces a response when the given descriptor produces a response over or equal to a threshold.
    """
    def __init__(self, descriptor: Descriptor, threshold: float):
        self.descriptor = descriptor
        self.threshold = threshold

    def response(self, text: str) -> float:
        """
        :return: the response of the descriptor if the response is over a threshold, otherwise 0.
        """
        return 1 if self.descriptor.response(text) >= self.threshold else 0

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

    def response(self, text: str) -> float:
        """
        :return: 1 if the word is present in the text, otherwise 0.
        """
        matched_words = [w for w in text.split() if w == self.word]
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


class And(Descriptor):
    """
    Matches on multiple conditions in a text.
    """

    def __init__(self, descriptors: List[Descriptor]):
        """
        :param descriptors: the descriptors for which the responses will be summed.
        """
        self.ds = descriptors

    def response(self, text: str) -> float:
        """
        :return: the average response from all descriptors.
        """
        return sum([descriptor.response(text) for descriptor in self.ds])

    def max_response(self) -> float:
        """
        :return: the maximum response, i.e. the sum of all maximum responses of all descriptors.
        """
        return sum([descriptor.max_response() for descriptor in self.ds])


class AllOf(Descriptor):
    """
    Matches only if all descriptors match.
    """

    def __init__(self, descriptors: List[Descriptor]):
        self.ds = descriptors

    def response(self, text: str) -> float:
        """
        :return: 1 if **all** other descriptors give a response, otherwise 0.
        """
        responses = [descriptor.response(text) for descriptor in self.ds]
        was_response = [r != 0 for r in responses]
        return float(all(was_response))

    def max_response(self) -> float:
        return 1


class NoneOf(Descriptor):
    """
    Matches on the text if the other descriptors don't match, i.e. give a response of zero.
    """

    def __init__(self, descriptors: List[Descriptor]):
        self.ds = descriptors

    def response(self, text: str) -> float:
        """
        :return: 1 if **all** other descriptors give a response, otherwise 0.
        """
        responses = [descriptor.response(text) for descriptor in self.ds]
        was_response = [r != 0 for r in responses]
        return float(not any(was_response))

    def max_response(self) -> float:
        return 1


class OneOf(Descriptor):
    """
    Matches only if one descriptor matches.
    """

    def __init__(self, descriptors: List[Descriptor]):
        """
        :param descriptors: the list of descriptors to match. There must be at least 2.
        """

        assert len(descriptors) >= 2

        self.ds = descriptors

    def response(self, text: str) -> float:
        """
        :return: the value of descriptor D if D is the only descriptor to give a non-zero response, otherwise 0.
        """
        responses = sorted([descriptor.response(text) for descriptor in self.ds])

        # If the second to last element is zero, it means either there was a response from only one descriptor, or
        # no descriptors responded.
        if responses[-2] == 0:
            return responses[-1]

        return 0

    def max_response(self) -> float:
        """
        :return: a maximum response out of all descriptors, i.e. because only one descriptor can respond.
        """
        max_responses = [descriptor.max_response() for descriptor in self.ds]
        return max(max_responses)


class Positional(OneOf):
    """
    Matches on positional words, e.g. next, first, second, etc.
    """

    def __init__(self):
        words = ['next', 'first', 'second', 'third', 'fourth']
        ds = WordMatch.list_from_words(words)

        super(Positional, self).__init__(ds)


class WordTag(Descriptor):
    """
    Matches on words with the given NLTK tag.
    """

    def __init__(self, tag: str):
        self.tag = tag

    def response(self, text: str) -> float:
        """
        :return: the number of words matching the tag in the text.
        """
        num_tagged = len(nltk_tagged(self.tag, text))
        return float(num_tagged >= 1)

    def max_response(self) -> float:
        return 1


class Number(WordTag):
    """
    Matches on numbers (e.g. 102) in a text.
    """

    def __init__(self):
        super(Number, self).__init__('CD')  # Matches on Cardinal Numbers.


class SpeechParsable:
    """
    A type which can be created by parsing the transcript of speech from the player.
    """

    @abstractclassmethod
    def text_descriptor(cls) -> Descriptor:
        """
        :return: a descriptor used to recognise the type from the transcript of the player's speech.
        """
        raise NotImplementedError

    @abstractclassmethod
    def parse(cls, user_text: str) -> 'SpeechParsable':
        """
        :param user_text: the transcript of the player's speech.
        :return: the object parsed from the user's text.
        """
        raise NotImplementedError


def parse_user_speech(speech_text: str,
                      possible_classes: List[Type[SpeechParsable]],
                      response_threshold: float = 0.5) -> Optional[SpeechParsable]:
    """
    :param speech_text: the transcript of the player's speech.
    :param possible_classes: a list of possible classes to parse to, e.g. Interaction, Movement, etc.
    :response_threshold: the minimum response a class' text descriptor must give for that class to be considered.
    :return: the parsed object, or None if the parser was not sure to which class the text belonged.
    """

    responses = np.array([c.text_descriptor().normalised_response(speech_text) for c in possible_classes])

    # Remove any responses below a threshold.
    below_threshold_indices = responses < response_threshold
    responses[below_threshold_indices] = 0

    max_response = max(responses)

    # If all responses are zero, there was no parse.
    if max_response == 0:
        return None

    # If more than one response is the maximum, we can't tell which class it should actually be.
    if responses.tolist().count(max_response) > 1:
        return None

    # If the maximum response is unique, return that maximum.
    max_index = responses.argmax()
    return possible_classes[max_index].parse(speech_text)
