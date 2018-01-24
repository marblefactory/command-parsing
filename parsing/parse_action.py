from actions.action import Stop, Composite
from parsing.parser import *
from parsing.parse_move import move, change_stance
from parsing.parse_interaction import through_door, pick_up, throw


def stop() -> Parser:
    """
    :return: parses stop actions, i.e. saying the word 'stop'.
    """
    return word_match('stop').ignore_parsed(Stop())


def single_action() -> Parser:
    """
    :return: a parser which parses single actions, i.e. not composite actions.
    """
    parsers = [
        stop(),
        move(),
        change_stance().map_response(lambda r: r / 2), # Half because move also looks for stances.
        through_door(),
        pick_up(),
        throw()
    ]

    return strongest(parsers)


def composite() -> Parser:
    """
    :return: a parser which parses composite actions, e.g. actions connected with the word 'then' or 'and'. The
             response is the mean of all parsed actions.
    """
    separators = ['then', 'and']

    def parse(full_input: List[Word]) -> Optional[ParseResult]:
        inputs = split_list(full_input, separators)

        if len(inputs) == 1:
            # There were no occurrences of the separators.
            return None

        results = [single_action().parse(words) for words in inputs]
        filtered = [result for result in results if result is not None]

        actions = [r.parsed for r in filtered]
        mean_response = sum([r.response for r in filtered]) / len(filtered)

        return ParseResult(Composite(actions), mean_response, [])

    return Parser(parse)


def action() -> Parser:
    """
    :return: a parser for single or composite actions.
    """
    act = strongest([composite(), single_action()])
    return threshold(act, 0.5)


if __name__ == '__main__':
    #s = 'stand up and run to the door on your right'.split()
    s = 'throw the rock to the desk behind you'.split()
    #s = 'run upstairs'.split()

    result = action().parse(s)

    if result:
        print(result.parsed)
        print(result.response)
    else:
        print("None")
