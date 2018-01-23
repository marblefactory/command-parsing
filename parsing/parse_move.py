from actions.move import *
from parsing.parser import *
from parsing.parse_location import location


def speed() -> Parser:
    """
    :return: a parser for different speeds, i.e. slow, normal, fast.
    """
    fast_word_parsers = [word_meaning('quick'), word_meaning('fast'), word_match('run')]

    slow = word_meaning('slow').ignore_parsed(Speed.SLOW)
    fast = strongest(fast_word_parsers).ignore_parsed(Speed.FAST)
    # Deduce that if the speed is neither slow nor fast, then it must be normal speed.
    normal = strongest([slow, fast, produce(Speed.NORMAL, 1.0)])

    return strongest([slow, normal, fast])


def stance() -> Parser:
    """
    :return: a parser for different stances, i.e. crouched, standing.
    """
    crouched = word_meaning('crouch').ignore_parsed(Stance.CROUCH)
    # Deduce that if the stance is not crouched then it must be standing.
    standing = strongest([crouched, produce(Stance.STAND, 1.0)])

    return strongest([crouched, standing])


def move() -> Parser:
    """
    :return: a parser to recognise movement actions.
    """
    def combine_speed(acc: List, r: Response) -> Parser:
        # Passes though the response, ignoring the response of the speed parser.
        return anywhere(speed()).map(lambda parsed_speed, _: (acc + [parsed_speed], r))

    def combine_stance(acc: List, r: Response) -> Parser:
        # Passes through the response, ignoring the response of the stance parser.
        return anywhere(stance()).map(lambda parsed_stance, _: (acc + [parsed_stance], r))

    move_verb = anywhere(word_meaning('go'))
    loc_parser = anywhere(location()).map_parsed(lambda loc: [loc])

    return move_verb.ignore_then(loc_parser, mean) \
                    .then(combine_speed) \
                    .then(combine_stance) \
                    .map_parsed(lambda p: Move(p[1], p[2], p[0]))
