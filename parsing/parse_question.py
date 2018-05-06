from parsing.parser import *
from actions.question import *
from parsing.parse_interaction import interactable_object_name, guard_noun


def see_verb() -> Parser:
    """
    :return: a parser for words that mean 'to see'. This only consumes the parsed words.
    """
    can_see = maybe(word_match('can', consume=Consume.WORD_ONLY)).ignore_then(word_meaning('see', consume=Consume.WORD_ONLY))
    near = word_meaning('near', consume=Consume.WORD_ONLY)
    look = word_spelling('look', match_first_letter=True, consume=Consume.WORD_ONLY)
    find = word_spelling('find', consume=Consume.WORD_ONLY)

    return strongest([can_see, near, look, find])


def inventory_question() -> Parser:
    """
    :return: a parser for asking the spy what they're holding.
    """
    what = strongest_word(['what'], make_word_parsers=[word_spelling, word_meaning])
    you = word_match('you')
    carrying = strongest_word(['hold', 'carry', 'doing'], make_word_parsers=[word_spelling, word_meaning])

    return maybe(what) \
          .ignore_then(you, mix) \
          .ignore_then(carrying, lambda what_r, carry_r: mix(what_r, carry_r, 0.24)) \
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
    return see_verb() \
          .ignore_then(guard_noun(), mix) \
          .ignore_parsed(GuardsQuestion())


def surroundings_question() -> Parser:
    """
    :return: a parser for asking questions about what the spy can see around them.
    """
    # E.g. what's can you see?
    what = strongest_word(['what'], make_word_parsers=[word_spelling, word_meaning])
    what_around = maybe(what) \
                 .ignore_then(see_verb(), combine_responses=mix)

    # E.g. what's in the room
    room = strongest_word(['room', 'corridor'], make_word_parsers=[word_spelling])
    what_in = maybe(what) \
             .ignore_then(room, combine_responses=mix)

    return strongest([what_around, what_in]) \
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


def question() -> Parser:
    """
    :return: a parser for all the types of question.
    """
    parsers = [
        inventory_question(),
        see_object_question(),
        location_question(),
        guards_question(),
        surroundings_question()
    ]
    return strongest(parsers)
