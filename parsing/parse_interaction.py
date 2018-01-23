from actions.interaction import *
from parsing.parser import *
from parsing.parse_location import object_relative_direction, positional, directional
from actions.location import Directional, MoveDirection


def interaction_object_name() -> Parser:
    """
    :return: a parser for names of objects that can be interacted with.
    """
    return strongest_word(['rock', 'hammer'])


def through_door() -> Parser:
    """
    :return: a parser which parses instructions to go through a door.
    """
    open = strongest_word(['open', 'through'])
    return anywhere(word_match('door')).ignore_then(open).ignore_parsed(ThroughDoor())


def pick_up() -> Parser:
    """
    :return: a parser which parses an instruction to pick up an object relative to the player, e.g. pick up the rock on your left.
    """
    def combine_direction(acc: List, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: acc + [dir])

    pick_up_verb = anywhere(word_meaning('pick'))
    obj_name = anywhere(interaction_object_name()).map_parsed(lambda name: [name])

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
        produce(Directional(MoveDirection.FORWARDS), 1)
    ]
    target = strongest(target_location_parsers)
    throw_verb = word_meaning('throw')

    return throw_verb.ignore_then(target) \
                     .map_parsed(lambda loc: Throw(loc))
