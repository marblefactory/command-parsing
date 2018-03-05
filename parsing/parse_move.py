from actions.move import *
from actions.location import MoveDirection, Distance
from parsing.parser import *
from parsing.parse_location import location, move_direction, move_object_name
from functools import partial
from utils import partial_class


def speed() -> Parser:
    """
    :return: a parser for different speeds, i.e. slow, normal, fast.
    """
    fast_word_parsers = [
        word_meaning('quick'),
        word_meaning('fast'),
        word_meaning('sprint'),
        word_meaning('sprinting'),
        word_spelling('run'),
        word_spelling('running')
    ]

    fast = strongest(fast_word_parsers).ignore_parsed(Speed.FAST)
    normal = strongest_word(['normal', 'normally', 'walk'], parser_constructors=[word_meaning]).ignore_parsed(Speed.NORMAL)
    slow = word_meaning('slow').ignore_parsed(Speed.SLOW)

    return strongest([slow, normal, fast])


def stance() -> Parser:
    """
    :return: a parser for different stances, i.e. crouched, standing.
    """
    crouched = strongest_word(['crouch', 'quiet'], parser_constructors=[word_spelling, word_meaning]).ignore_parsed(Stance.CROUCH)
    standing = word_meaning('stand').ignore_parsed(Stance.STAND)

    return strongest([crouched, standing])


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
    get_down = word_match('get').then_ignore(word_match('down')).ignore_parsed(Stance.CROUCH)
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
        return anywhere(speed_parser).map(lambda parsed_speed, _: (partial(makeMove, speed=parsed_speed), r))

    def combine_stance(makeMove: Callable, r: Response) -> Parser:
        # If no stance is found, default to None, meaning there is no change in the stance.
        stance_parser = maybe(anywhere(stance()))
        # Passes through the response, ignoring the response of the stance parser.
        # Applies the stance to the Move init.
        return stance_parser.map(lambda parsed_stance, _: (makeMove(stance=parsed_stance), r))

    def combine(_: Any, verb_response: Response) -> Parser:
        # Defaults the location to forwards, therefore if the user just says 'go', the spy moves forwards.
        # Partially applies the location to the Move init.
        loc_parser = anywhere(location()).map(lambda loc, loc_response: (partial_class(Move, location=loc), mix(verb_response, loc_response)))
        full_parser = loc_parser.then(combine_speed).then(combine_stance)

        # Allow the user to just say they want to move. They can then be asked a question about where they want to go.
        return partial_parser(full_parser, verb_response, Move)

    verbs = ['go', 'walk', 'run', 'take', 'sprint']
    move_verb = anywhere(strongest_word(verbs, parser_constructors=[word_spelling, word_meaning]))

    return move_verb.then(combine)


def hide() -> Parser:
    """
    :return: a parser to recognise hide actions.
    """
    verb = word_meaning('hide')
    # If no object name is given, the spy hides behind the nearest object.
    obj_name = maybe(move_object_name(), response=1.0)

    return verb.ignore_then(obj_name) \
               .map_parsed(lambda obj_name: Hide(obj_name))
