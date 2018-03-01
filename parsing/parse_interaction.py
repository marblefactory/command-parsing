from actions.interaction import *
from parsing.parser import *
from parsing.parse_location import object_relative_direction, positional, directional, behind
from actions.location import Directional
from utils import partial_class


def interaction_object_name() -> Parser:
    """
    :return: a parser for names of objects that can be interacted with.
    """
    return strongest_word(['rock', 'hammer', 'terminal', 'computer', 'camera', 'console', 'server'], parser_constructors=[word_spelling])


def through_door() -> Parser:
    """
    :return: a parser which parses instructions to go through a door, e.g. 'go through'.
    """
    open = strongest_word(['open', 'through', 'enter', 'into']) # 'into' because Google thinks 'enter' is 'into'.
    parser = open.ignore_then(maybe(word_match('door')), mix) # Reduce the response if 'door' is missing.
    return parser.ignore_parsed(ThroughDoor())


def pick_up() -> Parser:
    """
    :return: a parser which parses an instruction to pick up an object relative to the player, e.g. pick up the rock on your left.
    """
    # Takes the partially applied init of PickUp and adds the last argument, i.e. the direction.
    def combine_direction(make_pickup: Callable, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: make_pickup(dir))

    def combine(make_pickup: Callable, verb_response: Response) -> Parser:
        # Parses all the information required to construct a pick-up.
        data_parser = interaction_object_name() \
                     .map_parsed(lambda obj_name: partial_class(PickUp, obj_name)) \
                     .then(combine_direction)

        # If we only get the verb and no data, use the response from the verb parser.
        return partial_parser(data_parser, verb_response, PickUp)

    # The verb to look for so we know it's a pick-up action.
    verb = strongest_word(['pick', 'take'], parser_constructors=[word_meaning])

    return verb.then(combine)


def throw() -> Parser:
    """
    :return: a parser which parses instructions to throw the object the spy is holding.
    """
    # Defaults to throwing forwards.
    target_location_parsers = [
        positional(),
        behind(),
        directional(),
        produce(Directional(ObjectRelativeDirection.FORWARDS), 0.5)
    ]
    target = strongest(target_location_parsers)
    throw_verb = strongest_word(['chuck', 'throw'])

    return throw_verb.ignore_then(target) \
                     .map_parsed(lambda loc: Throw(loc))


def hack() -> Parser:
    """
    :return: a parser which parses hack instructions.
    """
    def combine_direction(acc: List, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: acc + [dir])

    hack_verb = strongest_word(['hack'], parser_constructors=[word_spelling, word_meaning])
    text = word_match('text') # Because speech recognition mistakes 'hack' for 'text'.
    parser = strongest([hack_verb, text])
    obj_name = interaction_object_name().map_parsed(lambda name: [name])

    return parser.ignore_then(obj_name) \
                 .then(combine_direction) \
                 .map_parsed(lambda p: Hack(p[0], p[1]))
