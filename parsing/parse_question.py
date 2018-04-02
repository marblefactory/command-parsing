from parsing.parser import *
from actions.question import *
from parsing.parse_interaction import pickupable_object_name

def see_verb() -> Parser:
    """
    :return: a parser for words that mean 'to see'.
    """
    verbs = ['see', 'around', 'near']
    return strongest_word(verbs, make_word_parsers=[word_match, word_meaning])


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
    return what \
          .ignore_then(see_verb()) \
          .ignore_parsed(SurroundingsQuestion())


def see_object_question() -> Parser:
    """
    :return: a parser for asking whether the spy can see a specific object.
    """
    there = word_match('there') # E.g. "are there any ... ?"
    verb = strongest([see_verb(), there])

    return anywhere(verb) \
          .ignore_then(pickupable_object_name(), combine_responses=mix) \
          .map_parsed(lambda obj: SeeObjectQuestion(obj))


def time_remaining_question() -> Parser:
    """
    :return: a parser for asking how much time is remaining.
    """
    left_words = ['left', 'remaining']
    time_words = ['time', 'longer', 'long', 'clock']

    left = strongest_word(left_words)
    time = strongest_word(time_words)

    return maybe(anywhere(left)) \
          .ignore_then(time, combine_responses=max) \
          .ignore_parsed(TimeRemainingQuestion())
