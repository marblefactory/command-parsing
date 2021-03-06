from actions.move import *
from actions.location import MoveDirection
from parsing.parser import *
from parsing.parse_location import location, move_direction, move_object_name, object_relative_direction
from functools import partial


def fast_speed_verb() -> Parser:
    """
    :return: a parser for words that mean to move at a fast pace.
    """
    verbs = ['quick', 'fast', 'sprint', 'run', 'hurry', 'ran']
    # S2T mistakes 'run' for the following words:
    corrections = ['rhonda', 'rhondda', 'done']

    # Make a parser that recognises the meaning and spelling of the actual verbs, and matches on exact corrections.
    spelling = word_spelling_threshold(dist_threshold=0.42, min_word_length=2, match_first_letter=True)
    verb_parser = words_and_corrections(verbs, corrections, make_word_parsers=[spelling, word_meaning_pos(POS.verb)])

    # Google mistakes 'run' for 'rent'.
    rental_correction = word_spelling('rent')

    parser = strongest([verb_parser, rental_correction])

    # Ignore the go verbs, because it *can* be parsed as to mean 'fast', but it does not necessarily.
    # Also, crouching an mutually exclusive. Therefore inhibit running when crouching is detected.
    return ignore_words(go_verb_words()) \
          .ignore_then(none(non_consuming(crouch_stance()), max_parser_response=0.85)) \
          .ignore_then(parser)

# .ignore_then(none(crouch_stance(), max_parser_response=1.1)) \


def normal_speed_verb() -> Parser:
    """
    :return: a parser for words that mean to move at a normal, i.e. walking, pace.
    """
    return strongest_word(['normal', 'normally', 'walk'], make_word_parsers=[word_meaning])


def slow_speed_verb() -> Parser:
    """
    :return: a parser for words that mean to move at a slow pace.
    """
    return word_meaning('slow')


def go_verb_words() -> List[Word]:
    """
    :return: a list of words which can mean 'go'.
    """
    return ['go', 'to', 'take', 'move', 'into']


def go_verbs() -> Parser:
    """
    :return: parser for words that mean to go somewhere.
    """
    go_verbs = go_verb_words()
    # S2T can mistake 'to' for 'o2.
    corrections = ['o2']

    go_verb_parser = words_and_corrections(go_verbs, corrections, make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])

    # All parsers which can be used to parse 'go' verbs.
    all_parsers = [
        go_verb_parser,
        fast_speed_verb(),
        normal_speed_verb(),
        slow_speed_verb()
    ]

    return strongest(all_parsers)


def speed() -> Parser:
    """
    :return: a parser for different speeds, i.e. slow, normal, fast.
    """
    fast = fast_speed_verb().ignore_parsed(Speed.FAST)
    normal = normal_speed_verb().ignore_parsed(Speed.NORMAL)
    slow = slow_speed_verb().ignore_parsed(Speed.SLOW)

    return strongest([fast, normal, slow])


def crouch_stance() -> Parser:
    """
    :return: a parser for recognising crouched stances.
    """
    crouch_words = ['crouch', 'quiet', 'sneak']
    crouch_corrections = ['close']
    crouched = words_and_corrections(crouch_words, crouch_corrections,
                                     make_word_parsers=[word_spelling, word_meaning]).ignore_parsed(Stance.CROUCH)
    crouched_correction = word_match('grouch').ignore_parsed(Stance.CROUCH)
    lie_spelling = word_match('lie').ignore_parsed(Stance.CROUCH)

    return strongest([crouched, crouched_correction, lie_spelling])


def stance() -> Parser:
    """
    :return: a parser for different stances, i.e. crouched, standing.
    """
    standing = word_meaning('stand').ignore_parsed(Stance.STAND)
    return strongest([crouch_stance(), standing])


def turn() -> Parser:
    """
    :return: a parser for turning instructions, e.g. turn around, defaults to turning around (i.e. backwards).
    """
    turn_verb = word_match('turn')
    direction = strongest([move_direction(), produce(MoveDirection.BACKWARDS, 1)])

    return turn_verb.ignore_then(direction) \
                    .map_parsed(lambda dir: Turn(dir))


def change_stance() -> Parser:
    """
    :return: a parser for stance changes, e.g. crouch, stand up, etc
    """
    get_up = word_match('get').then_ignore(word_match('up')).ignore_parsed(Stance.STAND)
    get_down = word_match('get').then_ignore(strongest_word(['down', 'low'])).ignore_parsed(Stance.CROUCH)
    parser = strongest([stance(), get_up, get_down])

    return parser.map_parsed(lambda s: ChangeStance(s))


def change_speed() -> Parser:
    """
    :return: a parser for speed changes, e.g. run, walk normally, etc
    """
    return speed().map_parsed(lambda s: ChangeSpeed(s))


def move() -> Parser:
    """
    :return: a parser to recognise movement actions.

             Parses on a go verb, then the location can not be specified, thereby creating a partial move.
             This allows the user to just say they want to move. They can then be asked a question about where they
             want to go.

             Also, parses moves which can optionally have a verb or not. This cannot be a partial parser otherwise
             everything will be considered a partial move.
    """
    def combine_speed(makeMove: Callable, r: Response) -> Parser:
        # The speed defaults to normal.
        speed_parser = defaulted(speed(), produce(Speed.FAST, 0.5))
        # Partially applies the speed to the Move init.
        return non_consuming(speed_parser).map(lambda parsed_speed, _: (partial(makeMove, speed=parsed_speed), r))

    def combine_stance(makeMove: Callable, r: Response) -> Parser:
        # If no stance is found, default to None, meaning there is no change in the stance.
        stance_parser = maybe(non_consuming(stance()))
        # Passes through the response, ignoring the response of the stance parser.
        # Applies the stance to the Move init.
        return stance_parser.map(lambda parsed_stance, _: (makeMove(stance=parsed_stance), r))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Defaults the location to forwards, therefore if the user just says 'go', the spy moves forwards.
        # Partially applies the location to the Move init.
        loc_parser = non_consuming(location()).map(lambda loc, loc_response: (partial(Move.partial_init(), location=loc), mix(verb_response, loc_response)))
        return loc_parser.then(combine_speed).then(combine_stance)

    go = non_consuming(go_verbs())
    return partial_or_maybe(go, combine, partial_marker=Move)


def through_door() -> Parser:
    """
    :return: a parser which parses instructions to go through a door, e.g. 'go through'.
    """
    open_words = ['open', 'through', 'enter', 'into', 'inside']
    open_corrections = ['going']
    open = words_and_corrections(open_words, open_corrections)  # 'into' because Google thinks 'enter' is 'into'.
    door_parser = open.ignore_then(maybe(word_match('door')), mix)  # Reduce the response if 'door' is missing.
    corrections = word_match('coincide')

    # For if the player says 'go in'. Reduced response though as the word could appear in other phrases.
    in_parser = word_match('in').map_response(lambda _: 0.0)

    verb_parser = strongest([door_parser, corrections, in_parser])

    return verb_parser \
          .ignore_then(object_relative_direction(), lambda verb_r, dir_r: mix(verb_r, dir_r, 0.65)) \
          .map_parsed(lambda dir: ThroughDoor(dir))


def move_into() -> Parser:
    """
    :return: a parser that parses going to a location and then through the door, e.g. 'go into the second room'.
    """
    return non_consuming(move()) \
          .then_ignore(through_door()) \
          .map_parsed(lambda move: Composite([move, ThroughDoor(ObjectRelativeDirection.VICINITY)]))


def hide() -> Parser:
    """
    :return: a parser to recognise hide actions.
    """
    verb = strongest_word(['hide'], make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])
    # If no object name is given, the spy hides behind the nearest object.
    obj_name = maybe(move_object_name(), response=1.0)

    return verb.ignore_then(obj_name, lambda verb_r, obj_r: mix(verb_r, obj_r, 0.35)) \
               .map_parsed(lambda obj_name: Hide(obj_name))


def leave_room() -> Parser:
    """
    :return: a parser which tells the spy to leave the room they're in, e.g. 'leave the room'.
    """
    leave_verbs = ['leave', 'out', 'exit']
    return strongest_word(leave_verbs).ignore_parsed(ThroughDoor(ObjectRelativeDirection.VICINITY))
