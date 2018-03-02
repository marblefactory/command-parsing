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


def _object_interaction(verb_parser: Parser, ParseType: Type) -> Parser:
    """
    :param verb_parser: a parser for the verb of the interaction, e.g. 'hack'
    :param parse_type: type which will be parsed. Also used as the marker used to identify where parsing failed
                       for partial parses.
    :return: a parser which parses a verb followed by the name of an object and an optional direction.
    """
    def combine_direction(make_type: Callable, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: make_type(dir))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Parses the name of the object and then the direction.
        data_parser = interaction_object_name() \
                     .map_parsed(lambda obj_name: partial_class(ParseType, obj_name)) \
                     .then(combine_direction)

        # If we only get the verb and no data, use the response from the verb parser.
        return partial_parser(data_parser, verb_response, ParseType)

    return verb_parser.then(combine)


def pick_up() -> Parser:
    """
    :return: a parser which parses an instruction to pick up an object relative to the player, e.g. pick up the rock on your left.
    """
    verb_parser = strongest_word(['pick', 'take'], parser_constructors=[word_meaning])
    return _object_interaction(verb_parser, PickUp)


def hack() -> Parser:
    """
    :return: a parser which parses hack instructions.
    """
    hack_verb = strongest_word(['hack'], parser_constructors=[word_spelling, word_meaning])
    text = word_match('text') # Because speech recognition mistakes 'hack' for 'text'.
    verb_parser = strongest([hack_verb, text])

    return _object_interaction(verb_parser, Hack)


def through_door() -> Parser:
    """
    :return: a parser which parses instructions to go through a door, e.g. 'go through'.
    """
    open = strongest_word(['open', 'through', 'enter', 'into']) # 'into' because Google thinks 'enter' is 'into'.
    parser = open.ignore_then(maybe(word_match('door')), mix) # Reduce the response if 'door' is missing.
    return parser.ignore_parsed(ThroughDoor())


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
