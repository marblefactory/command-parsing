from actions.interaction import *
from parsing.parser import *
from parsing.parse_location import object_relative_direction, positional, directional, behind
from actions.location import Directional


def interaction_object_name() -> Parser:
    """
    :return: a parser for names of objects that can be interacted with.
    """
    return strongest_word(['rock', 'hammer', 'terminal', 'computer', 'camera', 'console'])


def through_door() -> Parser:
    """
    :return: a parser which parses instructions to go through a door, e.g. 'go through'.
    """
    open = strongest_word(['open', 'through'])
    parser = open.ignore_then(maybe(word_match('door')), mix)
    return parser.ignore_parsed(ThroughDoor())


def pick_up() -> Parser:
    """
    :return: a parser which parses an instruction to pick up an object relative to the player, e.g. pick up the rock on your left.
    """
    def combine_direction(acc: List, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: acc + [dir])

    pick_up_verb = word_meaning('pick')
    obj_name = interaction_object_name().map_parsed(lambda name: [name])

    return pick_up_verb.ignore_then(obj_name) \
                       .then(combine_direction) \
                       .map_parsed(lambda p: PickUp(p[0], p[1]))


def throw() -> Parser:
    """
    :return: a parser which parses instructions to throw the object the spy is holding.
    """
    # Defaults to throwing forwards.
    target_location_parsers = [
        positional(),
        directional(),
        behind(),
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

    hack_verb = word_match('hack')
    obj_name = interaction_object_name().map_parsed(lambda name: [name])

    return hack_verb.ignore_then(obj_name) \
                       .then(combine_direction) \
                       .map_parsed(lambda p: Hack(p[0], p[1]))


def interaction() -> Parser:
    """
    :return: a parser which can parse any interaction, e.g. picking up an object.
    """
    return strongest([through_door(), pick_up(), throw(), hack()])
