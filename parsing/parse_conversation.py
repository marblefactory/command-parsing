from parsing.parser import *
from actions.conversation import *


def greeting() -> Parser:
    """
    :return: a parser for the player saying a greeting, e.g. hello, to the spy.
    """
    return word_meaning('hello').ignore_parsed(Greeting())


def default_conversation() -> Parser:
    """
    :return: a parser to be used as the default for if no other conversation was parsed.
    """
    return produce(DefaultConversation(), response=0.0)


def conversation() -> Parser:
    """
    :return: a parser for all conversation.
    """
    return strongest([greeting(), default_conversation()])
