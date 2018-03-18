from actions.move import *
from actions.location import MoveDirection
from parsing.parser import *
from parsing.parse_location import location, move_direction, move_object_name
from functools import partial
from utils import partial_class


def fast_speed_verb() -> Parser:
    """
    :return: a parser for words that mean to move at a fast pace.
    """
    parsers = [
        word_meaning('quick'),
        word_meaning('fast'),
        word_meaning('sprint'),
        word_meaning('sprinting'),
        word_spelling('run'),
        word_spelling('running'),

        # A few words that 'run' are mistaken for.
        word_match('randa'),
        word_match('rhonda'),
        word_match('rhondda')
    ]

    return strongest(parsers)


def normal_speed_verb() -> Parser:
    """
    :return: a parser for words that mean to move at a normal, i.e. walking, pace.
    """
    return strongest_word(['normal', 'normally', 'walk'], parser_constructors=[word_meaning])


def slow_speed_verb() -> Parser:
    """
    :return: a parser for words that mean to move at a slow pace.
    """
    return word_meaning('slow')


def go_verbs() -> Parser:
    """
    :return: parser for words that mean to go somewhere.
    """
    go_words = [
        'go',   # e.g. go to the end of the corridor
        'to',   # e.g. to the end of the corridor
        'take'  # e.g. take the third door on your left
    ]

    go_parser = strongest_word(go_words, parser_constructors=[word_spelling, word_meaning])

    # Parsers required because voice recognition sometimes mistakes words.
    correction_parsers = [
        'o2'  # 'to' is mistaken for 'o2'
    ]

    correction_parser = strongest_word(correction_parsers)

    # All parsers which can be used to parse 'go' verbs.
    all_parsers = [
        go_parser,
        correction_parser,
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
    crouched = strongest_word(['crouch', 'quiet'], parser_constructors=[word_spelling, word_meaning]).ignore_parsed(Stance.CROUCH)
    crouched_correction = word_match('grouch').ignore_parsed(Stance.CROUCH)
    standing = word_meaning('stand').ignore_parsed(Stance.STAND)

    return strongest([crouched, crouched_correction, standing])


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

    return anywhere(go_verbs()).then(combine)


def hide() -> Parser:
    """
    :return: a parser to recognise hide actions.
    """
    verb = word_meaning('hide')
    # If no object name is given, the spy hides behind the nearest object.
    obj_name = maybe(move_object_name(), response=1.0)

    return verb.ignore_then(obj_name) \
               .map_parsed(lambda obj_name: Hide(obj_name))
