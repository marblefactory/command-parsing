from parsing.parser import *
from actions.question import *
from parsing.parse_interaction import pickupable_object_name

def see_verb() -> Parser:
    """
    :return: a parser for words that mean 'to see'. This only consumes the parsed words.
    """
    can_see = maybe(word_match('can', consume=Consume.WORD_ONLY)).ignore_then(word_meaning('see', consume=Consume.WORD_ONLY))
    around = word_meaning('around', consume=Consume.WORD_ONLY)
    near = word_meaning('near', consume=Consume.WORD_ONLY)

    return strongest([can_see, around, near])


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

    return verb \
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

    return maybe(non_consuming(left)) \
          .ignore_then(time, combine_responses=max) \
          .ignore_parsed(TimeRemainingQuestion())
