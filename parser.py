from abc import abstractclassmethod
from descriptor import Descriptor
from typing import List, Type, Optional, Any, Dict
import numpy as np
import nltk


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
    def parse(cls, tokens: List[str]) -> 'SpeechParsable':
        """
        :param tokens: the transcript individual words of the player's speech.
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
    tokens = nltk.word_tokenize(speech_text)
    return possible_classes[max_index].parse(tokens)


def nltk_first_tagged(tag: str, tokens: List[str]) -> Optional[str]:
    """
    :param words: the word that the user said.
    :return: the first work tagged with the given tag, or None if no word has the tag.
    """
    tagged = nltk.pos_tag(tokens)
    matched = [word for (word, word_tag) in tagged if word_tag == tag]

    if len(matched) == 0:
        return None

    return matched[0]


def parse_one_of(possibilities: Dict[str, Any], tokens: List[str]) -> Optional[Any]:
    """
    :param possibilities: a mapping of tokens and their corresponding return value if matched.
    :param words: the words that user said.
    :return: the value of the first key to be present in the text, or None if no possibilities match.
    """
    for word in tokens:
        value = possibilities.get(word)
        if value is not None:
            return value

    return None


def parse_positional(tokens: List[str]) -> Optional[int]:
    """
    :param tokens: the words that the user said.
    :return: the number representing the position, e.g. first maps to 1. Or, returns None if no positions are found.
    """
    ps = {
        'next': 0,
        'first': 0,
        'second': 1,
        'third': 2,
        'fourth': 3,
        'fifth': 4
    }

    return parse_one_of(ps, tokens)