from parsing.parser import *
from actions.conversation import *


def greeting() -> Parser:
    """
    :return: a parser for the player saying a greeting, e.g. hello, to the spy.
    """
    return word_meaning('hello').ignore_parsed(Greeting())


def what_name() -> Parser:
    """
    :return: a parser for the player asking what the spy's name is.
    """
    return word_meaning('name').ignore_parsed(WhatName())


def obscenity() -> Parser:
    """
    :return: a parser for recognising obscenity
    """
    def contains_asterisk(word: Word) -> Response:
        return float('*' in word)

    return predicate(contains_asterisk).ignore_parsed(Obscenity())


def repeat() -> Parser:
    """
    :return: a parser for recognising a repeat command.
    """
    repeat_after_me = phrase('repeat after me')
    repeat = strongest_word(['repeat', 'say'])
    return strongest([repeat_after_me, repeat]) \
          .ignore_then(rest()) \
          .map_parsed(lambda words: Repeat(words))


def conversation() -> Parser:
    """
    :return: a parser for all conversation.
    """
    default = produce(DefaultConversation(), response=0.0)
    parsers = [
        repeat(),
        greeting(),
        what_name(),
        obscenity(),
        default
    ]

    return strongest(parsers)
