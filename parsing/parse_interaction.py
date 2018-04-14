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

    rock_correction = word_match('ra').ignore_parsed('rock')
    # Strongly recognises the names of actual objects in the game, and weakly matches on other nouns.
    objects = object_spelled(names, other_noun_response=0.25)

    return strongest([objects, rock_correction])


def guard_noun() -> Parser:
    """
    :return: a parser for the word guard, or similar words.
    """
    guard_words = ['guard', 'enemy']
    corrections = ['card', 'god', 'aids', 'jobs', 'dogs', 'car']
    return words_and_corrections(guard_words, corrections, make_word_parsers=[word_spelling, word_meaning_pos(POS.noun)])

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


def drop() -> Parser:
    """
    :return: a parser which parses an instruction for the spy to drop whatever they're holding.
    """
    put_down_verb = word_match('put').then_ignore(word_match('down'))
    drop_verb = word_meaning('drop', pos=POS.verb)

    return strongest([put_down_verb, drop_verb]).ignore_parsed(Drop())


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
    hack_verbs = ['hack', 'log', 'attack']
    corrections = ['text', 'taxi']  # 'hack' is sometimes misheard for 'text'.
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


def throw_verb() -> Parser:
    """
    :return: a parser for verbs that mean 'to throw'.
    """
    throw_verbs = ['chuck', 'throw']
    corrections = ['show', 'stoner', 'through', 'check', 'shut']
    return  words_and_corrections(throw_verbs, corrections)


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

    # The name of the object is not used, since the spy can only hold one object at once, however it is needed for a
    # successful parse.
    return throw_verb() \
          .ignore_then(pickupable_object_name(), lambda verb_r, obj_r: obj_r) \
          .ignore_then(target, mix) \
          .map_parsed(lambda loc: Throw(loc))


def throw_at_guard() -> Parser:
    """
    :return: a parser which parses instructions to throw an object at a guard.
    """
    return throw_verb() \
          .ignore_then(guard_noun()) \
          .ignore_then(object_relative_direction()) \
          .map_parsed(lambda dir: ThrowAtGuard(dir))


def take_out_guard() -> Parser:
    """
    :return: a parser which parsers instructions to kill a guard.
    """
    kill_words = ['kill', 'strangle', 'destroy', 'attack']
    kill_parser = strongest_word(kill_words, make_word_parsers=[word_meaning_pos(POS.verb)])

    knock_out = word_match('knock').ignore_then(word_match('out'))
    take_out = word_match('take').ignore_then(word_match('out'))

    verb_parser = strongest([kill_parser, knock_out, take_out])

    return non_consuming(verb_parser) \
          .ignore_then(guard_noun()) \
          .ignore_then(object_relative_direction()) \
          .map_parsed(lambda dir: TakeOutGuard(dir))


def pickpocket() -> Parser:
    """
    :return: a parser which parses instructions to pickpocket a guard.
    """
    pickpocket_words = ['pickpocket', 'steal']
    pickpocket = strongest_word(pickpocket_words, make_word_parsers=[word_match, word_meaning_pos(POS.verb)])
    take = word_match('take').ignore_then(guard_noun())
    verb_parser = strongest([pickpocket, take])

    return verb_parser \
          .ignore_then(object_relative_direction()) \
          .map_parsed(lambda dir: Pickpocket(dir))


def destroy_generator() -> Parser:
    """
    :return: a parser which parses instructions to destroy the generator.
    """
    destroy_verbs = ['destroy', 'break', 'kill', 'attack']
    destroy_verbs = strongest_word(destroy_verbs, make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])
    take_out = word_match('take').ignore_then(word_match('out'))
    verb_parser = strongest([destroy_verbs, take_out])

    generator_nouns = ['generator', 'engine']
    generator_parser = strongest_word(generator_nouns, make_word_parsers=[word_spelling, word_meaning_pos(POS.noun)])

    return non_consuming(verb_parser) \
          .ignore_then(generator_parser) \
          .ignore_parsed(DestroyGenerator())
