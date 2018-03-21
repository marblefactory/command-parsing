from actions.interaction import *
from parsing.parser import *
from parsing.parse_location import object_relative_direction, positional, directional, behind
from actions.location import Directional, Distance
from utils import partial_class


def pickupable_object_name() -> Parser:
    """
    :return: a parser for the names of objects which can be picked up and thrown.
    """
    words = ['rock', 'hammer']
    return strongest_word(words, parser_constructors=[word_spelling])


def pick_up() -> Parser:
    """
    :return: a parser which parses an instruction to pick up an object relative to the player, e.g. pick up the rock on your left.
    """
    verb_parser = strongest_word(['pick', 'take'], parser_constructors=[word_meaning, word_spelling])

    def combine_direction(make_type: Callable, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: make_type(dir))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Parses the name of the object and then the direction.
        data_parser = pickupable_object_name() \
                     .map_parsed(lambda obj_name: partial_class(PickUp, obj_name)) \
                     .then(combine_direction)

        # If we only get the verb and no data, use the response from the verb parser.
        return partial_parser(data_parser, verb_response, PickUp)

    return verb_parser.then(combine)


def hackable_object_name() -> Parser:
    """
    :return: a parser for the names of objects which can be hacked. Returns a tuple containing the name of the
             hacked object (e.g. server) and the type of object it is (e.g. TERMINAL).
    """
    camera = word_spelling('camera').map_parsed(lambda obj_name: (obj_name, HackableType.CAMERA))

    terminal_words = ['terminal', 'computer', 'console', 'server']
    terminal = strongest_word(terminal_words, parser_constructors=[word_spelling]) \
              .map_parsed(lambda obj_name: (obj_name, HackableType.TERMINAL))

    return strongest([camera, terminal])


def hack() -> Parser:
    """
    :return: a parser which parses hack instructions.
    """
    hack_verb = strongest_word(['hack'], parser_constructors=[word_spelling, word_meaning])
    text = word_match('text') # Because speech recognition mistakes 'hack' for 'text'.
    verb_parser = strongest([hack_verb, text])

    def combine_direction(make_type: Callable, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: make_type(dir))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Parses the name of the object and then the direction.
        data_parser = hackable_object_name() \
                     .map_parsed(lambda obj_data: partial_class(Hack, obj_data[1], obj_data[0])) \
                     .then(combine_direction)

        # If we only get the verb and no data, use the response from the verb parser.
        return partial_parser(data_parser, verb_response, Hack)

    return verb_parser.then(combine)


def throw() -> Parser:
    """
    :return: a parser which parses instructions to throw the object the spy is holding.
    """
    # Defaults to throwing forwards.
    target_location_parsers = [
        positional(),
        behind(),
        directional(),
        produce(Directional(ObjectRelativeDirection.FORWARDS, Distance.MEDIUM), 0.5)
    ]
    target = strongest(target_location_parsers).map_response(lambda _: 1.0)
    throw_verb = strongest_word(['chuck', 'throw'])

    return throw_verb.ignore_then(target) \
                     .map_parsed(lambda loc: Throw(loc))
