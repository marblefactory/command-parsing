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


def who_are_you() -> Parser:
    """
    :return: a parser for the player asking who the spy is.
    """
    return word_match('who') \
          .ignore_then(word_match('you')) \
          .ignore_parsed(WhoAreYou())


def obscenity() -> Parser:
    """
    :return: a parser for recognising obscenity
    """
    def contains_asterisk(word: Word) -> Response:
        return float('*' in word)

    starred = predicate(contains_asterisk)
    words = strongest_word(['fuck', 'shit'])

    return strongest([words, starred]).ignore_parsed(Obscenity())


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
    parsers = [
        greeting(),
        what_name(),
        who_are_you(),
        obscenity(),
        repeat()
    ]

    return strongest(parsers)
