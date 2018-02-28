from actions.move import *
from actions.location import Directional, MoveDirection
from parsing.parser import *
from parsing.parse_location import location, move_direction, move_object_name


def speed() -> Parser:
    """
    :return: a parser for different speeds, i.e. slow, normal, fast.
    """

    # The response to give if neither fast or slow is specified.
    normal_speed_response = 0.5

    fast_word_parsers = [
        word_meaning('quick', semantic_similarity_threshold=normal_speed_response),
        word_meaning('fast', semantic_similarity_threshold=normal_speed_response),
        word_meaning('sprint', semantic_similarity_threshold=normal_speed_response),
        word_spelling('run')]

    slow = strongest_word(['slow', 'quiet'], parser_constructors=[word_meaning]).ignore_parsed(Speed.SLOW)
    fast = strongest(fast_word_parsers).ignore_parsed(Speed.FAST)
    # Deduce that if the speed is neither slow nor fast, then it must be normal speed.
    normal = strongest([slow, fast, produce(Speed.NORMAL, normal_speed_response)])

    return strongest([slow, normal, fast])


def stance() -> Parser:
    """
    :return: a parser for different stances, i.e. crouched, standing.
    """
    crouched = strongest_word(['crouch'], parser_constructors=[word_spelling, word_meaning]).ignore_parsed(Stance.CROUCH)
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
    p = strongest([stance(), get_up, get_down])

    return p.map_parsed(lambda s: ChangeStance(s))


def move() -> Parser:
    """
    :return: a parser to recognise movement actions.
    """
    def combine_speed(acc: List, r: Response) -> Parser:
        # Passes though the response, ignoring the response of the speed parser.
        return anywhere(speed()).map(lambda parsed_speed, _: (acc + [parsed_speed], r))

    def combine_stance(acc: List, r: Response) -> Parser:
        # If no stance is found, default to None, meaning there is no change in the stance.
        stance_parser = maybe(anywhere(stance()))
        # Passes through the response, ignoring the response of the stance parser.
        return stance_parser.map(lambda parsed_stance, _: (acc + [parsed_stance], r))

    verbs = ['go', 'walk', 'run', 'take', 'sprint']
    move_verb = anywhere(strongest_word(verbs, parser_constructors=[word_spelling, word_meaning]))

    # Defaults the location to forwards, therefore if the user just says 'go', the spy moves forwards.
    #defaulted_loc = strongest([location(), produce(Directional(MoveDirection.FORWARDS), response=0.0)])
    loc_parser = location().map_parsed(lambda loc: [loc])

    return move_verb.ignore_then(loc_parser, mix) \
                    .then(combine_speed) \
                    .then(combine_stance) \
                    .map_parsed(lambda p: Move(p[1], p[0], p[2]))


def hide() -> Parser:
    """
    :return: a parser to recognise hide actions.
    """
    verb = word_meaning('hide')
    # If no object name is given, the spy hides behind the nearest object.
    obj_name = maybe(move_object_name(), response=1.0)

    return verb.ignore_then(obj_name) \
               .map_parsed(lambda obj_name: Hide(obj_name))
