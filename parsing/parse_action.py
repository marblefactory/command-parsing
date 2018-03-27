from actions.action import Stop, Composite
from parsing.parser import *
from parsing.parse_move import move, change_stance, change_speed, turn, hide, through_door, leave_room
from parsing.parse_interaction import pick_up, throw, hack, drop
from parsing.parse_question import inventory_question, location_question, guards_question, surroundings_question
from utils import split_list


def failure_words() -> Parser:
    """
    :return: a parser which parses words which will cause parsing to fail.
    """
    return strongest_word([ "not", "don't"])


def ignored_words() -> List[str]:
    """
    :return: a list of words which should be removed from the input text.
    """
    return ['the']


def stop() -> Parser:
    """
    :return: parses stop actions, i.e. saying the word 'stop'.
    """
    return strongest_word(['stop', 'freeze', 'halt']).ignore_parsed(Stop())


def single_action() -> Parser:
    """
    :return: a parser which parses single actions, i.e. not composite actions.
    """
    # The order these appear in here determine their precedence.
    parsers = [
        stop(),
        hack(),
        through_door(),
        change_stance().map_response(lambda r: r * 0.7),  # Because move also looks for stances, and this matches on less.
        change_speed().map_response(lambda r: r * 0.7), # Because move also looks for speeds, and this matches on less.
        turn(),
        pick_up(),
        throw(),
        drop(),
        hide(),
        move(),
        leave_room(),
        inventory_question(),
        location_question(),
        guards_question(),
        surroundings_question()
    ]

    # Removes successful parses which have below 0.3 response. This does not remove partial parses.
    min_response = 0.24
    thresholds = [threshold_success(p, min_response) for p in parsers]

    return strongest(thresholds)


def composite() -> Parser:
    """
    :return: a parser which parses composite actions, e.g. actions connected with the word 'then' or 'and'. The
             response is the mean of all parsed actions.
    """
    separators = ['then', 'and']

    def parse(full_input: List[Word]) -> Optional[ParseResult]:
        inputs = split_list(full_input, separators)

        if len(inputs) <= 1:
            # There were no occurrences of the separators.
            return FailureParse()

        results = [single_action().parse(words) for words in inputs]
        filtered = [result for result in results if result.is_success()] # Ignore partials
        actions = [r.parsed for r in filtered]

        return SuccessParse(Composite(actions), 1.0, [])

    return Parser(parse)


def action() -> Parser:
    """
    :return: a parser for single or composite actions. Nothing will be parsed if the text contains "not" or "don't".
    """
    act = strongest([composite(), single_action()])
    return none(failure_words()) \
          .ignore_then(ignore_words(ignored_words())) \
          .ignore_then(act)
