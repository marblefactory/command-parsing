from actions.action import Stop, Composite
from parsing.parse_move import move, change_stance, change_speed, turn, hide, through_door, leave_room, move_into
from parsing.parse_interaction import *
from parsing.parse_question import *
from parsing.parse_conversation import *
from utils import split_list


def ignored_words() -> List[str]:
    """
    :return: a list of words which should be removed from the input text.
    """
    return ['the']


def stop() -> Parser:
    """
    :return: parses stop actions, i.e. saying the word 'stop'.
    """
    stop_words = ['stop', 'freeze', 'halt', "don't", 'not']
    stop_corrections = ['star']
    parser = words_and_corrections(stop_words, stop_corrections, make_word_parsers=[word_spelling])

    return parser.ignore_parsed(Stop())


def single_action() -> Parser:
    """
    :return: a parser which parses single actions, i.e. not composite actions.
    """
    # The order these appear in here determine their precedence.
    parsers = [
        stop(),
        hack(),
        throw_at_guard(),
        throw(),
        change_stance().map_response(lambda r: r * 0.7),  # Because move also looks for stances, and this matches on less.
        change_speed().map_response(lambda r: r * 0.72),  # Because move also looks for speeds, and this matches on less.
        turn(),
        auto_take_out_guard(),
        strangle_guard(),
        pickpocket(),
        pick_up(),
        drop(),
        hide(),
        move_into(),
        through_door(),
        move(),
        destroy_generator(),
        leave_room(),
        inventory_question(),
        see_object_question(),
        location_question(),
        guards_question(),
        surroundings_question(),
        time_remaining_question(),
        conversation()
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
    return ignore_words(ignored_words()) \
          .ignore_then(act)
