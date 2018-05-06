from parsing.parser import *
from actions.question import *
from parsing.parse_interaction import interactable_object_name, guard_noun


def see_verb() -> Parser:
    """
    :return: a parser for words that mean 'to see'. This only consumes the parsed words.
    """
    can_see = maybe(word_match('can', consume=Consume.WORD_ONLY)).ignore_then(word_meaning('see', consume=Consume.WORD_ONLY))
    around = word_meaning('around', consume=Consume.WORD_ONLY)
    near = word_meaning('near', consume=Consume.WORD_ONLY)
    look = word_meaning('look', consume=Consume.WORD_ONLY)

    return strongest([can_see, around, near, look])


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
    spelling = partial(word_spelling, match_first_letter=True)
    where = strongest_word(['where'], make_word_parsers=[spelling, word_meaning])
    you = strongest_word(['you', 'i'])
    return where.ignore_then(you, lambda r1, r2: mix(r1, r2, 0.1)).ignore_parsed(LocationQuestion())


def guards_question() -> Parser:
    """
    :return: a parser for asking questions about guards.
    """
    return guard_noun().ignore_parsed(GuardsQuestion())


def surroundings_question() -> Parser:
    """
    :return: a parser for asking questions about what the spy can see around them.
    """
    what = strongest_word(['what'], make_word_parsers=[word_spelling, word_meaning])
    return maybe(what) \
          .ignore_then(see_verb(), combine_responses=mix) \
          .ignore_parsed(SurroundingsQuestion())


def see_object_question() -> Parser:
    """
    :return: a parser for asking whether the spy can see a specific object.
    """
    there = strongest_word(['there', 'where']) # E.g. "are there any ... ?" or "where are the ...?"
    verb = strongest([see_verb(), there])

    return verb \
          .ignore_then(interactable_object_name(), mix) \
          .map_parsed(lambda obj: SeeObjectQuestion(obj))


def time_remaining_question() -> Parser:
    """
    :return: a parser for asking how much time is remaining.
    """
    how = strongest_word(['how', 'what'], make_word_parsers=[word_spelling])
    left_words = ['left', 'remaining']
    time_words = ['time', 'longer', 'long', 'clock']

    left = strongest_word(left_words)
    time = strongest_word(time_words)

    return non_consuming(how) \
          .ignore_then(maybe(non_consuming(left)), combine_responses=mix) \
          .ignore_then(time, combine_responses=mix) \
          .ignore_parsed(TimeRemainingQuestion())
