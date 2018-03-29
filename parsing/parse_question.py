from parsing.parser import *
from actions.question import *


def inventory_question() -> Parser:
    """
    :return: a parser for asking the spy what they're holding.
    """
    what = strongest_word(['what'], make_word_parsers=[word_spelling, word_meaning])
    carrying = strongest_word(['hold', 'carry'], make_word_parsers=[word_meaning])

    return what.ignore_then(carrying) \
          .ignore_parsed(InventoryContentsQuestion())


def location_question() -> Parser:
    """
    :return: a parser for asking the spy where they are.
    """
    where = strongest_word(['where'], make_word_parsers=[word_spelling, word_meaning])
    return where.ignore_then(word_match('you')).ignore_parsed(LocationQuestion())


def guards_question() -> Parser:
    """
    :return: a parser for asking questions about guards.
    """
    guard_words = ['guard', 'enemy']
    corrections = ['card', 'god', 'aids', 'jobs', 'dogs']
    parser = words_and_corrections(guard_words, corrections, make_word_parsers=[word_spelling, word_meaning_pos(POS.noun)])

    return parser.ignore_parsed(GuardsQuestion())


def surroundings_question() -> Parser:
    """
    :return: a parser for asking questions about what the spy can see around them.
    """
    what = strongest_word(['what'], make_word_parsers=[word_spelling, word_meaning])
    see = strongest_word(['see', 'around', 'near'], make_word_parsers=[word_spelling, word_meaning])

    return what.ignore_then(see).ignore_parsed(SurroundingsQuestion())
