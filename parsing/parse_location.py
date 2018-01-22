from actions.location import *
from parsing.parser import *


def object_name() -> Parser:
    """
    :return: a parser which parses names of objects which can be moved to, i.e. table, door, desk.
    """
    object_names = ['table', 'door', 'desk']

    def condition(input_word: Word) -> Response:
        return float(input_word in object_names)

    return predicate(condition)


def ordinal_number() -> Parser:
    """
    :return: a parser for ordinal numbers, e.g. first, second, third.
    """
    #words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
    words = [('first', 0), ('second', 1)]

    #word_matchers = [word_match(word).map(lambda d, r: (d + str(num), r)) for (word, num) in words]

    word_matchers = []

    for word, num in words:
        print(word, num)
        parser = word_match(word).map_parsed(lambda p: p + str(num))

        word_matchers.append(parser)


    return strongest(word_matchers)


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
    num = anywhere(ordinal_number())

s = 'first'.split()
(x, response, remaining) = ordinal_number().parse(s)
print(x)