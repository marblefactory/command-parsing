from actions.action import Stop, Composite
from parsing.parser import *
from parsing.parse_move import move, change_stance


def stop() -> Parser:
    """
    :return: parses stop actions, i.e. saying the word 'stop'.
    """
    return word_match('stop').ignore_parsed(Stop())


def single_action() -> Parser:
    """
    :return: a parser which parses single actions, i.e. not composite actions.
    """
    return strongest([move(), change_stance(), stop()])


def composite() -> Parser:
    """
    :return: a parser which parses composite actions, e.g. actions connected with the word 'then'.
    """
    pass


if __name__ == '__main__':
    s = 'stand up and run to the next door in front of you'.split()

    result = single_action().parse(s)

    if result:
        print(result.parsed)
        print(result.response)
    else:
        print("None")