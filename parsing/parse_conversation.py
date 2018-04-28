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


def conversation() -> Parser:
    """
    :return: a parser for all conversation.
    """
    default = produce(DefaultConversation(), response=0.0)
    parsers = [
        greeting(),
        what_name(),
        default
    ]

    return strongest(parsers)
