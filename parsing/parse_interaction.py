from actions.interaction import *
from parsing.parser import *
from parsing.parse_location import object_relative_direction, positional, directional, behind
from actions.location import Directional, Distance


def pickupable_object_name() -> Parser:
    """
    :return: a parser for the names of objects which can be picked up and thrown.
    """
    # Objects the player can actually pick up.
    names = ['rock', 'hammer', 'bottle', 'cup', 'can']
    # Strongly recognises the names of actual objects in the game, and weakly matches on other nouns.
    return object_spelled(names, other_noun_response=0.25)


def pick_up() -> Parser:
    """
    :return: a parser which parses an instruction to pick up an object relative to the player, e.g. pick up the rock on your left.
    """
    verb_parser = strongest_word(['pick', 'take'], make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])

    def combine_direction(make_type: Callable, response: Response) -> Parser:
        return object_relative_direction().map(lambda dir, _: (make_type(dir), response))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Parses the name of the object and then the direction.
        data_parser = pickupable_object_name() \
                     .map(lambda obj_name, obj_name_resp: (partial(PickUp.partial_init(), obj_name), obj_name_resp)) \
                     .then(combine_direction)

        # If we only get the verb and no data, use the response from the verb parser.
        return partial_parser(data_parser, verb_response, PickUp)

    return verb_parser.then(combine)


def hackable_object_name() -> Parser:
    """
    :return: a parser for the names of objects which can be hacked. Returns a tuple containing the name of the
             hacked object (e.g. server) and the type of object it is (e.g. TERMINAL).
    """
    camera_words = ['camera', 'cctv']
    camera = strongest_word(camera_words, make_word_parsers=[word_spelling]) \
            .map_parsed(lambda obj_name: (obj_name, HackableType.CAMERA))

    terminal_words = ['terminal', 'computer', 'console', 'server', 'mainframe']
    terminal = strongest_word(terminal_words, make_word_parsers=[word_spelling]) \
              .map_parsed(lambda obj_name: (obj_name, HackableType.TERMINAL))

    return strongest([camera, terminal])


def hack() -> Parser:
    """
    :return: a parser which parses hack instructions.
    """
    hack_verbs = ['hack', 'log']
    corrections = ['text']  # 'hack' is sometimes misheard for 'text'.
    verb_parser = words_and_corrections(hack_verbs, corrections, make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])

    # Only want the spelling of the word 'break', not the meaning.
    break_parser = word_spelling('break')

    # Combine the break and verb parsers.
    parser = strongest([verb_parser, break_parser])

    def combine_direction(make_type: Callable, _: Response) -> Parser:
        return object_relative_direction().map_parsed(lambda dir: make_type(dir))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Parses the name of the object and then the direction.
        data_parser = hackable_object_name() \
                     .map_parsed(lambda obj_data: partial(Hack.partial_init(), obj_data[1], obj_data[0])) \
                     .then(combine_direction)

        # If we only get the verb and no data, use the response from the verb parser.
        return partial_parser(data_parser, verb_response, Hack)

    return parser.then(combine)


def throw() -> Parser:
    """
    :return: a parser which parses instructions to throw the object the spy is holding.
    """
    # Defaults to throwing forwards.
    default_target_parser = produce(Directional(ObjectRelativeDirection.FORWARDS, Distance.MEDIUM), 0.0)
    target_location_parsers = [
        positional(),
        behind(),
        directional(),
        default_target_parser
    ]
    target = strongest(target_location_parsers).map_response(lambda _: 1.0)

    throw_verbs = ['chuck', 'throw']
    corrections = ['show', 'stoner']
    verb_parser = words_and_corrections(throw_verbs, corrections)

    return verb_parser.ignore_then(target) \
                      .map_parsed(lambda loc: Throw(loc))
