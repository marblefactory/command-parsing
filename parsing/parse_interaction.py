from actions.interaction import *
from parsing.parser import *
from parsing.parse_location import object_relative_direction, positional, directional, behind, pickupable_object_name
from actions.location import Directional, Distance
from actions.location import MoveDirection


def guard_noun() -> Parser:
    """
    :return: a parser for the word guard, or similar words.
    """
    guard_words = ['guard', 'enemy', 'security', 'guy', 'him', 'man']
    corrections = ['card', 'god', 'aids', 'jobs', 'dogs', 'car', 'ga']
    return words_and_corrections(guard_words, corrections, make_word_parsers=[word_spelling, word_meaning_pos(POS.noun)])


def pick_up() -> Parser:
    """
    :return: a parser which parses an instruction to pick up an object relative to the player, e.g. pick up the rock on your left.
    """
    def combine_direction(make_type: Callable, response: Response) -> Parser:
        return object_relative_direction().map(lambda dir, _: (make_type(dir), response))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Parses the name of the object and then the direction.
        return pickupable_object_name() \
              .map(lambda obj_name, obj_name_resp: (partial(PickUp.partial_init(), obj_name), mix(verb_response, obj_name_resp))) \
              .then(combine_direction)

    verb_parser = strongest_word(['pick', 'take'], make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])
    return partial_or_maybe(verb_parser, combine, partial_marker=PickUp)


def drop() -> Parser:
    """
    :return: a parser which parses an instruction for the spy to drop whatever they're holding.
    """
    verbs = ['put', 'drop']
    verb_parsers = strongest_word(verbs, make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])
    place = word_spelling('place')
    parsers = strongest([place, verb_parsers])

    return parsers.ignore_parsed(Drop())


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
    hack_verbs = ['hack', 'attack']
    corrections = ['text', 'taxi', 'at']  # 'hack' is sometimes misheard for 'text'.
    spelling = word_spelling_threshold(dist_threshold=0.49)
    verb_parser = words_and_corrections(hack_verbs, corrections, make_word_parsers=[spelling, word_meaning_pos(POS.verb)])

    # Only want the spelling of the word 'break', not the meaning.
    break_parser = word_spelling('break')
    log_in = word_match('log').ignore_then(word_spelling('into'), combine_responses=mix)

    # Combine the break and verb parsers.
    parser = strongest([verb_parser, break_parser, log_in])

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
    corrections = ['show', 'stoner', 'through', 'check', 'shut', 'row', 'road', 'roller', 'roll', 'rover', 'role', 'rolling']
    match = partial(word_match, consume=Consume.WORD_ONLY)
    return words_and_corrections(throw_verbs, corrections, make_word_parsers=[match])


def throw() -> Parser:
    """
    :return: a parser which parses instructions to throw the object the spy is holding.
    """
    # Defaults to throwing forwards.
    default_target_parser = produce(Directional(ObjectRelativeDirection.FORWARDS, Distance.MEDIUM), 0.0)
    target_location_parsers = [
        positional(),
        behind(),
        directional(default=MoveDirection.FORWARDS),
        default_target_parser
    ]
    target = strongest(target_location_parsers).map_response(lambda _: 1.0)

    # The name of the object is not used, since the spy can only hold one object at once, however it is needed for a
    # successful parse.
    return throw_verb() \
          .ignore_then(pickupable_object_name(), lambda verb_r, obj_r: obj_r) \
          .ignore_then(target, mix) \
          .map_parsed(lambda loc: Throw(loc))


def _make_guard_parser(verb_parser: Parser, make_action: Callable[[ObjectRelativeDirection], Any]) -> Parser:
    """
    :param verb_parser: a parser for the verb indicating the action to take, e.g. throw.
    :param make_action: creates an action, using the direction of the guard from the spy.
    :return: a parser which parses a verb, a guard noun, and the direction of the guard from the spy.
    """
    return non_consuming(verb_parser) \
          .ignore_then(guard_noun()) \
          .ignore_then(object_relative_direction()) \
          .map_parsed(make_action)


def throw_at_guard() -> Parser:
    """
    :return: a parser which parses instructions to throw an object at a guard.
    """
    return _make_guard_parser(throw_verb(), ThrowAtGuard)


def strangle_guard() -> Parser:
    """
    :return: a parser which parses instruction to strangle a guard.
    """
    strangle_words = ['strangle']
    strangle = strongest_word(strangle_words, make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])

    return _make_guard_parser(strangle, StrangleGuard)


def auto_take_out_guard() -> Parser:
    """
    :return: a parser which parsers instructions to kill a guard.
    """
    kill_words = ['kill', 'destroy', 'attack', 'waste']
    kill_parser = strongest_word(kill_words, make_word_parsers=[word_spelling_threshold(0.49), word_meaning_pos(POS.verb)])

    knock_out = word_match('knock').ignore_then(word_match('out'))
    take_out = word_match('take').ignore_then(word_match('out'))

    verb_parser = strongest([kill_parser, knock_out, take_out])
    parser = _make_guard_parser(verb_parser, AutoTakeOutGuard)

    # 'Kill the guard' is often interpreted as 'hildegard'
    hildegard_correction = word_match('hildegard').ignore_parsed(AutoTakeOutGuard(ObjectRelativeDirection.VICINITY))

    return strongest([parser, hildegard_correction])


def pickpocket() -> Parser:
    """
    :return: a parser which parses instructions to pickpocket a guard.
    """
    pickpocket_words = ['pickpocket', 'steal']
    pickpocket = strongest_word(pickpocket_words, make_word_parsers=[word_match, word_meaning_pos(POS.verb)])
    take = word_match('take').ignore_then(guard_noun())
    verb_parser = strongest([pickpocket, take])

    return non_consuming(verb_parser) \
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
