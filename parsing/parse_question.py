from parsing.parser import *
from actions.question import InventoryContentsQuestion, LocationQuestion


def inventory_question() -> Parser:
    """
    :return: a parser for asking the spy what they're holding.
    """
    what = strongest_word(['what'], parser_constructors=[word_spelling, word_meaning])
    carrying = strongest_word(['hold', 'carry'], parser_constructors=[word_meaning])

    return what.ignore_then(carrying) \
          .ignore_parsed(InventoryContentsQuestion())


def location_question() -> Parser:
    """
    :return: a parser for asking the spy where they are.
    """
    where = strongest_word(['where'], parser_constructors=[word_spelling, word_meaning])
    return where.ignore_parsed(LocationQuestion())
