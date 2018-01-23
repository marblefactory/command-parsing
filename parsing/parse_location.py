from actions.location import *
from parsing.parser import *


def object_name() -> Parser:
    """
    :return: a parser which parses names of objects which can be moved to, i.e. table, door, desk.
    """
    object_names = ['table', 'door', 'desk', 'server']

    def condition(input_word: Word) -> Response:
        return float(input_word in object_names)

    return predicate(condition)


def ordinal_number() -> Parser:
    """
    :return: a parser for ordinal numbers, e.g. next, first, second, third, which are converted to their numerical
             representation.
    """
    words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
    numeric_zipped = list(zip(words, range(len(words)))) + [('next', 0)]

    word_matchers = [word_match(word).ignore_parsed(num) for word, num in numeric_zipped]
    return strongest(word_matchers)


def move_direction() -> Parser:
    """
    :return: a parser for movement directions, e.g. left, right, forwards, backwards, which are converted to Direction enums.
    """
    forwards_matcher = strongest_word(['forward', 'front'], make_parser=word_meaning)
    backwards_matcher = strongest_word(['backward', 'behind'], make_parser=word_meaning)

    forwards = forwards_matcher.ignore_parsed(MoveDirection.FORWARDS)
    backwards = backwards_matcher.ignore_parsed(MoveDirection.BACKWARDS)

    left = word_match('left').ignore_parsed(MoveDirection.LEFT)
    right = word_match('right').ignore_parsed(MoveDirection.RIGHT)

    return strongest([left, right, forwards, backwards])


def object_relative_direction() -> Parser:
    """
    :return: a parser for object relative directions. This defaults to objects in the vicinity if no left, right, etc is found.
    """
    return strongest([move_direction(), produce(ObjectRelativeDirection.VICINITY, 1.0)])


def absolute() -> Parser:
    """
    :return: a parser for absolute locations, e.g. '[go to] room 201'.
             Can also parse just the number, e.g. '[go to] 201' but this gives a lower response.
    """
    return maybe(word_match('room')) \
          .ignore_then(number(), mean) \
          .map_parsed(lambda room_num: Absolute('room ' + room_num))


def positional() -> Parser:
    """
    :return: a parser for positional locations, e.g. 'third door on your left'
    """
    def combine_ordinal_num(acc: List, r1: Response) -> Parser:
        # Parses an ordinal number, or defaults to 0 if there is no ordinal number.
        default = produce(parsed=0, response=0)
        ord = strongest([anywhere(ordinal_number()), default])

        return ord.map(lambda parsed_num, r2: (acc + [parsed_num], mean(r1, r2)))

    def combine_direction(acc: List, r1: Response) -> Parser:
        dir = object_relative_direction()
        return dir.map(lambda parsed_dir, r2: (acc + [parsed_dir], mean(r1, r2)))

    obj = anywhere(object_name()).map_parsed(lambda parsed_name: [parsed_name])

    return obj.then(combine_ordinal_num) \
              .then(combine_direction) \
              .map_parsed(lambda p: Positional(p[0], p[1], p[2]))


def directional() -> Parser:
    """
    :return: a parser for directions, e.g. go left, right, forwards, backwards.
    """
    # Half the response to give bias towards positional locations since both use directions.
    return move_direction().map(lambda dir, r: (Directional(dir), r/2))


def stairs() -> Parser:
    """
    :return: a parser for stair directions, e.g. upstairs, downstairs.
    """
    up = strongest_word(['up', 'upstairs']).ignore_parsed(FloorDirection.UP)
    down = strongest_word(['down', 'downstairs']).ignore_parsed(FloorDirection.DOWN)

    return strongest([up, down])


def location() -> Parser:
    """
    :return: a parser which parses locations.
    """
    return strongest([absolute(), positional(), directional(), stairs()])
