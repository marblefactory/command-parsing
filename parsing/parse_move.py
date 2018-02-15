from actions.move import *
from parsing.parser import *
from parsing.parse_location import location, move_direction, move_object_name


def speed() -> Parser:
    """
    :return: a parser for different speeds, i.e. slow, normal, fast.
    """
    normal_speed_response = 0.5
    fast_word_parsers = [word_meaning('quick', normal_speed_response), word_meaning('fast', normal_speed_response), word_edit_dist('run')]

    slow = strongest_word(['slow', 'slowly']).ignore_parsed(Speed.SLOW)
    fast = strongest(fast_word_parsers).ignore_parsed(Speed.FAST)
    # Deduce that if the speed is neither slow nor fast, then it must be normal speed.
    normal = strongest([slow, fast, produce(Speed.NORMAL, normal_speed_response)])

    return strongest([slow, normal, fast])


def stance() -> Parser:
    """
    :return: a parser for different stances, i.e. crouched, standing.
    """
    crouched = word_meaning('crouch').ignore_parsed(Stance.CROUCH)
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
    :return: a parser for stance changes, i.e. crouch, stand up.
    """
    # Half the response to give bias towards move actions since both use stances.
    return stance().map_parsed(lambda s: ChangeStance(s))


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

    verbs = ['go', 'walk', 'run', 'take']
    move_verb = anywhere(strongest_word(verbs, parser_constructors=[word_meaning, word_edit_dist]))
    loc_parser = anywhere(location()).map_parsed(lambda loc: [loc])

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
