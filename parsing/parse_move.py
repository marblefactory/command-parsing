from actions.move import *
from actions.location import MoveDirection
from parsing.parser import *
from parsing.parse_location import location, move_direction, move_object_name, object_relative_direction
from functools import partial


def fast_speed_verb() -> Parser:
    """
    :return: a parser for words that mean to move at a fast pace.
    """
    verbs = ['quick', 'fast', 'sprint', 'run', 'hurry']
    # S2T mistakes 'run' for the following words:
    corrections = ['randa', 'rhonda', 'rhondda']

    # Make a parser that recognises the meaning and spelling of the actual verbs, and matches on exact corrections.
    parser = words_and_corrections(verbs, corrections, make_word_parsers=[word_spelling, word_meaning_pos(POS.verb)])

    # Ignore the go verbs, because it *can* be parsed as to mean 'fast', but it does not necessarily.
    return ignore_words(go_verb_words()).ignore_then(parser)


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
    return ['go', 'to', 'take', 'move']


def go_verbs() -> Parser:
    """
    :return: parser for words that mean to go somewhere.
    """
    go_verbs = go_verb_words()
    # S2T can mistake 'to' for 'o2.
    corrections = ['o2']

    spelling = partial(word_spelling, dist_threshold=0.5)
    go_verb_parser = words_and_corrections(go_verbs, corrections, make_word_parsers=[spelling, word_meaning_pos(POS.verb)])

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


def stance() -> Parser:
    """
    :return: a parser for different stances, i.e. crouched, standing.
    """
    crouched = strongest_word(['crouch', 'quiet', 'sneak'], make_word_parsers=[word_spelling, word_meaning]).ignore_parsed(Stance.CROUCH)
    crouched_correction = word_match('grouch').ignore_parsed(Stance.CROUCH)
    lie_spelling = word_spelling('lie', 0.5).ignore_parsed(Stance.CROUCH)
    standing = word_meaning('stand').ignore_parsed(Stance.STAND)

    return strongest([crouched, crouched_correction, lie_spelling, standing])


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
    """
    def combine_speed(makeMove: Callable, r: Response) -> Parser:
        # The speed defaults to normal.
        speed_parser = strongest([speed(), produce(Speed.NORMAL, 0.5)])
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

    # Parses on the verb, then the location can not be specified, thereby creating a partial move.
    # This allows the user to just say they want to move. They can then be asked a question about where they want to go.
    make_partial = lambda parser, verb_response: partial_parser(parser, verb_response, marker=Move)
    partial_move = non_consuming(go_verbs()).then(wrap(combine, make_partial))

    # Parses moves which can optionally have a verb or not. This cannot be a partial parser otherwise everything will
    # be considered a partial move.
    move = maybe(non_consuming(go_verbs())).then(combine)

    return strongest([move, partial_move])


def hide() -> Parser:
    """
    :return: a parser to recognise hide actions.
    """
    verb = word_meaning('hide')
    # If no object name is given, the spy hides behind the nearest object.
    obj_name = maybe(move_object_name(), response=1.0)

    return verb.ignore_then(obj_name) \
               .map_parsed(lambda obj_name: Hide(obj_name))


def through_door() -> Parser:
    """
    :return: a parser which parses instructions to go through a door, e.g. 'go through'.
    """
    open = strongest_word(['open', 'through', 'enter', 'into'])  # 'into' because Google thinks 'enter' is 'into'.
    door_parser = open.ignore_then(maybe(word_match('door')), mix)  # Reduce the response if 'door' is missing.

    return door_parser \
          .ignore_then(object_relative_direction()) \
          .map_parsed(lambda dir: ThroughDoor(dir))


def leave_room() -> Parser:
    """
    :return: a parser which tells the spy to leave the room they're in, e.g. 'leave the room'.
    """
    leave_verbs = ['leave', 'out']
    return strongest_word(leave_verbs).ignore_parsed(LeaveRoom())
