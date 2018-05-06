from typing import Tuple, Optional
from parsing.parse_result import *
from parsing.pre_processing import pre_process
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset
import inflect
import editdistance
from itertools import product
import functools
import numpy as np
from functools import partial
from enum import Enum


class POS:
    """
    A category of words. This is used when creating a parser a word with a specific category.
    """
    noun = 'n'
    verb = 'v'


class Consume(Enum):
    """
    Tells the predicate parser the policy to use when generating the remaining words.
    """

    # Consume all the words up to and including the parsed word.
    UP_TO_WORD = 0
    # Consume only the parsed word.
    WORD_ONLY = 1


def mix(r1: Response, r2: Response, proportion: float = 0.5) -> Response:
    """
    :param proportion: the ratio of r1 to r2/
    :return: a mix response of r1 and r2  in the ratio 1-proportion:proportion.
    """
    return r1 * (1 - proportion) + r2 * proportion


@functools.lru_cache(maxsize=None)
def semantic_similarity(w1: Word, w2: Word, pos: str, similarity_measure: Callable[[Synset, Synset], Response]) -> Response:
    """
    :param similarity_measure: a word net function which give the semantic distance between two synsets.
    :return: the semantic similarity between the words using a `similarity` distance function defined by WordNet.
    """

    # If a category of words (POS) was supplied, fill that in.
    make_synsets = partial(wn.synsets, pos=pos) if pos else wn.synsets

    # Each synset contains different meanings of the word, e.g. fly is a noun and verb.
    # We'll find the maximum semantic similarity between any pairing of words from both synsets.
    w1_synsets: List[Synset] = make_synsets(w1)
    w2_synsets: List[Synset] = make_synsets(w2)

    if len(w1_synsets) == 0 or len(w2_synsets) == 0:
        return 0.0

    similarities = [similarity_measure(s1, s2) or 0.0 for s1 in w1_synsets for s2 in w2_synsets]
    return np.max(similarities)


class Parser:
    def __init__(self, parse: Callable[[List[Word]], ParseResult]):
        """
        :param parse: the function that takes a list of words and produces a parse result.
        """
        self.parse = parse

    def then(self, operation: Callable[[Any, Response], 'Parser']) -> 'Parser':
        """
        :param operation: used to construct a new parser from the parse result of this parser.
        :return: applies this parser, then uses the result of parsing and the response to return another parser over
                 the remaining tokens.
        """
        def new_parse(input: List[Word]) -> ParseResult:
            result = self.parse(input)

            if not isinstance(result, SuccessParse):
                return result

            new_parser = operation(result.parsed, result.response)
            return new_parser.parse(result.remaining)

        return Parser(new_parse)

    def then_ignore(self,
                    next_parser: 'Parser',
                    combine_responses: Callable[[Response, Response], Response] = None) -> 'Parser':
        """
        :param next_parser:       the parser to apply over the tokens after using this parser.
        :param combine_responses: a function used to combine the responses of both this parser and `next_parser`. If
                                  `combine_responses` is None then this will be equal to the response of this parser,
                                  i.e. ignoring `next_parser`.
        :return:                  a parser which parsers first with this parser, then with `next_parser`. The parsed
                                  object from `next_parser` is ignored, and the response of both parsers is combined
                                  using `combine_responses`.
        """

        if not combine_responses:
            combine_responses = lambda r1, r2: r1

        def op(parsed: Any, r1: Response) -> Parser:
            return next_parser.map(lambda ignored_parsed, r2: (parsed, combine_responses(r1, r2)))

        return self.then(op)

    def ignore_then(self,
                    next_parser: 'Parser',
                    combine_responses: Callable[[Response, Response], Response] = None) -> 'Parser':
        """
        :param next_parser:       the parser to apply over the tokens after using this parser.
        :param combine_responses: a function used to combine the responses of both this parser and `next_parser`. If
                                  `combine_responses` is None then this will be equal to the response of `next_parser`,
                                  i.e. ignoring this parser.
        :return:                  a parser which parsers first with this parser, then with `next_parser`. The parsed
                                  object from this parser is ignored, and the response of both parsers is combined
                                  using `combine_responses`.
        """
        if not combine_responses:
            combine_responses = lambda r1, r2: r2

        def op(ignored_parsed: Any, r1: Response) -> Parser:
            return next_parser.map(lambda parsed, r2: (parsed, combine_responses(r1, r2)))

        return self.then(op)


    def map(self, transformation: Callable[[Any, Response], Tuple[Any, Response]]) -> 'Parser':
        """
        :return: takes the parse result 'wrapped' in the parser and applies the transformation to create a new parser.
        """

        def transform(parsed: Any, response: Response) -> Parser:
            def new_parse(words: List[Word]) -> ParseResult:
                new_parsed, new_response = transformation(parsed, response)
                return SuccessParse(new_parsed, new_response, words)

            return Parser(new_parse)

        return self.then(transform)

    def map_response(self, transformation: Callable[[Response], Response]) -> 'Parser':
        """
        :return: maps the response of this parser to the value returned by the transformation.
        """

        def t(parsed: Any, response: Response) -> Tuple[Any, Response]:
            new_response = transformation(response)
            return (parsed, new_response)

        return self.map(t)

    def map_parsed(self, transformation: Callable[[Any], Any]) -> 'Parser':
        """
        :return: maps the parsed object of this parser to the value returned by the transformation.
        """

        def t(parsed: Any, response: Response) -> Tuple[Any, Response]:
            new_parsed = transformation(parsed)
            return (new_parsed, response)

        return self.map(t)

    def ignore_parsed(self, new_parsed: Any) -> 'Parser':
        """
        :return: a parser which ignores the parsed object from this parser and uses `new_parsed`.
        """
        return self.map_parsed(lambda _: new_parsed)


def print_result() -> Callable[[Any, Response], Parser]:
    """
    :return: a function to be used with `then` which prints out the parse and passes it on.
    """
    def _print(parsed: Any, response: Response) -> Parser:
        print('{}, {}'.format(parsed, response))
        return produce(parsed, response)

    return _print


def wrap(operation: Callable[[Any, Response], Parser], wrapper: Callable[[Parser, Response], Parser]) -> Callable[[Any, Response], Parser]:
    """
    :return: a function which wraps the operation in the wrapper, passing the result of one to the other.
    """
    def op(parsed: Any, response: Response) -> Parser:
        return wrapper(operation(parsed, response), response)

    return op


def append(parser: Parser, combine_responses: Callable[[Response, Response], Response] = None, spaces = True) -> Callable[[Any, Response], Parser]:
    """
    An operation to be used with `then`.
    :param parser: the parser to run after the current parser.
    :param combine_responses: the function uses to combine the results of the parsers. Defaults to use the response of the current parser.
    :param spaces: whether to put spaces between appended words.
    :return: a operation which can be given to `then` to append a parsed string to the parsed string of the next parser.
    """
    if not combine_responses:
        combine_responses = lambda r1, r2: r1

    def op(parsed_str: str, response: Response) -> Parser:
        sep = ' ' if spaces else ''
        return parser.map(lambda p, r: (parsed_str + sep + p, combine_responses(response, r)))

    return op


def index_array(array: List) -> Callable[[Any, Response], Parser]:
    """
    An operation to be used with `then`.
    :param array: the array to index based on the result of the previous parser.
    :return: an operation which can be given to `then` which will index the given array using the result of the a parser
             (which must be an integer). If the index is out of bounds then the parser will fail.
    """
    def op(parsed_index: int, response: Response) -> Parser:
        try:
            elem = array[parsed_index]
            return produce(elem, response)
        except IndexError:
            return failure()

    return op


def produce(parsed: Any, response: Response) -> Parser:
    """
    :return: a parser that matches on all input, returns the supplied parsed object and response from parsing, and
             consumes no input.
    """
    def parse(input: List[Word]) -> ParseResult:
        return SuccessParse(parsed, response, input)

    return Parser(parse)


def failure() -> Parser:
    """
    :return: a parser which fails (i.e. gives a None result) to all input.
    """
    return Parser(lambda input: FailureParse())


def predicate(condition: Callable[[Word], Response], first_only = False, consume = Consume.UP_TO_WORD) -> Parser:
    """
    :param first_only: whether to only match the predicate on the first word in the remaining list of words.
    :param consume_to_word: whether to consume all the words on the input up and including to the parsed word, or
                            whether to just consume the parsed word and leave the rest of the input untouched.
    :return: a parser which matches on the word which gives the highest response to the condition.
    """

    # Returns the index of the word with the maximum response, that word, and its response.
    def generate_responses(input: List[Word]) -> (int, Word, Response):
        responses = [(i, word, condition(word)) for i, word in enumerate(input)]
        return max(responses, key=lambda r: r[2])

    # Returns the index of the first word, the first word, and its response to the predicate.
    def generate_response_first(input: List[Word]) -> (int, Word, Response):
        index = 0
        word = input[index]
        return index, word, condition(word)

    # Returns: the words to be in the remaining of this parser.
    def output_words(input: List[Word], word_match_idx: int) -> List[Word]:
        if consume == Consume.UP_TO_WORD:
            return input[word_match_idx + 1:]
        elif consume == Consume.WORD_ONLY:
            return input[:word_match_idx] + input[word_match_idx+1 :]

    def parse(input: List[Word]) -> ParseResult:
        if len(input) == 0:
            return FailureParse()

        i, word, max_response = generate_response_first(input) if first_only else generate_responses(input)
        if max_response == 0:
            return FailureParse()

        remaining = output_words(input, i)
        return SuccessParse(word, max_response, remaining)

    return Parser(parse)


def word_spelling(word: Word,
                  match_first_letter = False,
                  min_word_length = 3,
                  match_plural = False,
                  dist_threshold: Response = 0.5,
                  first_only = False,
                  consume = Consume.UP_TO_WORD) -> Parser:
    """
    :param match_first_letter: whether the parser should fail if the first letter does not match.
    :param min_word_length: the minimum word length, below, or equal, to which word spelling must exactly match.
    :param first_only: whether to only match the predicate on the first word in the remaining list of words.
    :return: a parser which matches words where the difference in spelling of the word and an input word determines the
             response. If matches then `word` is the parsed string, not the word from the input text.
    """
    def condition(match_word: Word) -> Callable[[Word], Response]:
        def _c(input_word: Word) -> Response:
            if len(input_word) <= min_word_length:
                return input_word == match_word

            if match_first_letter and input_word[0] != match_word[0]:
                return 0

            max_word_len = max(len(input_word), len(match_word))
            edit_dist = editdistance.eval(match_word, input_word)
            return ((max_word_len - edit_dist) / max_word_len)

        return _c

    if match_plural:
        plural = inflect.engine().plural(word)
        p_plural = predicate(condition(plural), first_only, consume).ignore_parsed(plural)
        p = predicate(condition(word), first_only, consume).ignore_parsed(word)
        return strongest([p, p_plural])

    else:
        p = predicate(condition(word), first_only, consume).ignore_parsed(word)
        return threshold_success(p, dist_threshold)


def word_spelling_threshold(dist_threshold: Response,
                            match_first_letter=False,
                            min_word_length=3,
                            match_plural=False,
                            first_only=False,
                            consume=Consume.UP_TO_WORD) -> Callable[[Word], Parser]:
    """
    :param first_only: whether to only match the predicate on the first word in the remaining list of words.
    :return: a parser which matches words where the difference in spelling of the word and an input word determines the
             response. If matches then `word` is the parsed string, not the word from the input text.
    """
    return partial(word_spelling,
                   match_first_letter=match_first_letter,
                   min_word_length=min_word_length,
                   dist_threshold=dist_threshold,
                   match_plural=match_plural,
                   first_only=first_only,
                   consume=consume)


def word_match(word: Word, match_plural = True, first_only = False, consume = Consume.UP_TO_WORD) -> Parser:
    """
    :param match_plural: whether to match on the plural of the word as well as the word.
    :param first_only: whether to only match the predicate on the first word in the remaining list of words.
    :return: a parser which matches on the first occurrence of the supplied word anywhere in the remaining words.
    """
    if match_plural:
        plural = inflect.engine().plural(word)

        def condition(input_word: Word) -> Response:
            return float(input_word == word or input_word == plural)

    else:
        def condition(input_word: Word) -> Response:
            return float(input_word == word)

    return predicate(condition, first_only, consume).map_parsed(lambda _: word)


def word_meaning(word: Word,
                 pos: Optional[str] = None,
                 semantic_similarity_threshold: Response = 0.5,
                 similarity_measure: Callable[[Synset, Synset], Response] = Synset.path_similarity,
                 first_only = False,
                 consume = Consume.UP_TO_WORD) -> Parser:
    """
    :param word: the word to find similar words to.
    :param pos: defines the category of words to compare (e.g. verbs). Words not in this category will have a similarity of 0.
    :param semantic_similarity_threshold: the minimum semantic distance for an input word to be from the supplied word.
    :param similarity_measure: used to compare the semantic similarity of two words.
    :param first_only: whether to only match the predicate on the first word in the remaining list of words.
    :return: a parser which matches on words which have a similar meaning to the supplied word.
    """
    def condition(input_word: Word) -> Response:
        return semantic_similarity(input_word, word, pos, similarity_measure)

    return threshold_success(predicate(condition, first_only, consume), semantic_similarity_threshold)


def word_meaning_pos(pos: POS,
                     semantic_similarity_threshold: Response = 0.5,
                     similarity_measure: Callable[[Synset, Synset], Response] = Synset.path_similarity,
                     first_only = False,
                     consume = Consume.UP_TO_WORD) -> Callable[[Word], Parser]:
    """
    :param pos: defines the category of words to compare (e.g. verbs). Words not in this category will have a similarity of 0.
    :param semantic_similarity_threshold: the minimum semantic distance for an input word to be from the supplied word.
    :param similarity_measure: used to compare the semantic similarity of two words.
    :param first_only: whether to only match the predicate on the first word in the remaining list of words.
    :return: a function which takes a word and returns a parser which matches on words which have a similar meaning to
             that word.
    """
    return partial(word_meaning,
                   pos=pos,
                   semantic_similarity_threshold=semantic_similarity_threshold,
                   similarity_measure=similarity_measure,
                   first_only=first_only,
                   consume=consume)


def word_tagged(tags: List[str], first_only = False, consume = Consume.UP_TO_WORD) -> Parser:
    """
    :param first_only: whether to only match the predicate on the first word in the remaining list of words.
    :return: a parser which matches on words with the given tags.
    """
    def condition(input_word: Word) -> Response:
        word, tag = nltk.pos_tag([input_word])[0]
        return float(tag in tags)

    return predicate(condition, first_only, consume)


def phrase(words_phrase: str) -> Parser:
    """
    :param words_phrase: a string of the phrase, e.g. "take out"
    :return: a parser that looks for the consecutive words in the phrase, without other words in between.
    """
    words = pre_process(words_phrase)

    acc = word_match(words[0])
    for word in words[1:]:
        acc = acc.then(append(word_match(word, first_only=True)))
    return acc


def cardinal_number() -> Parser:
    """
    :return: a parser which matches on string cardinal numbers, e.g. '102', and returns integers, e.g. 102.
    """
    return word_tagged(['CD']).map_parsed(lambda str_num: int(str_num))


def string_number() -> Parser:
    """
    :return: a parser which matches on string numbers and returns integers, e.g. three parses to the integer 3.
    """
    all_words = [
        ['zero'],
        ['one'],
        ['to', 'two', 'too'],
        ['three'],
        ['four', 'for'],
        ['five'],
        ['six'],
        ['seven'],
        ['eight'],
        ['nine'],
        ['ten']
    ]

    parsers: List[Parser]= []

    for num, words in enumerate(all_words):
        for word in words:
            parser = word_match(word).ignore_parsed(num)
            parsers.append(parser)

    return strongest(parsers)


def number() -> Parser:
    """
    :return: a parser which parses string numbers, e.g. 'one', up to 'ten'. Or, any cardinal number, e.g. '201'.
             Returns an integer representation of the number.
    """
    return strongest([string_number(), cardinal_number()])


def number_str() -> Parser:
    """
    :return: a parser which parses string number, e.g. 'one', and returns a string representation of the integer, e.g. '1'.
    """
    return number().map_parsed(lambda num: str(num))


def strongest(parsers: List[Parser], debug = False) -> Parser:
    """
    :return: the parser that gives the strongest response on the input text. If multiple parsers have the same maximum,
             then the parser to occur first in the list is returned.
    """
    def parse(input: List[Word]) -> ParseResult:
        best_result: Optional[ParseResult] = None

        # Not the prettiest code, but this is the fastest I could make it, which is more important considering
        # how often this is run.
        for parser in parsers:
            result = parser.parse(input)

            if debug:
                print(result)

            # The maximum value of a response is 1, therefore we can exit early.
            if isinstance(result, SuccessParse):
                if result.response == 1.0:
                    return result

            if not best_result or isinstance(best_result, FailureParse):
                best_result = result
            else:
                if best_result < result:
                    best_result = result

        return best_result

    return Parser(parse)


def strongest_word(words: List[Word], make_word_parsers: [Callable[[Word], Parser]] = None, debug = False) -> Parser:
    """
    :param words: the list of words to compare to the input.
    :param make_word_parsers: the functions used to create a parser from a word. For each word a parser will be
                              created using each parser in the list.
    :return: created parser which matches most strongly on the input.
    """
    if make_word_parsers is None:
        make_word_parsers = [word_match]

    # Each word matched with each type of parser (i.e. Cartesian product)
    constructors_and_words = product(make_word_parsers, words)
    parsers = [constructor(word) for (constructor, word) in constructors_and_words]
    return strongest(parsers, debug)


def non_consuming(parser: Parser) -> Parser:
    """
    :return: a parser which consumes none of the input, therefore any chained parsers can match anywhere in the text.
    """
    def parse(input: List[Word]) -> ParseResult:
        result = parser.parse(input)
        if isinstance(result, SuccessParse):
            return SuccessParse(result.parsed, result.response, input)
        return result

    return Parser(parse)


def maybe(parser: Parser, response: Response = 0.0) -> Parser:
    """
    :param response: the response of the parser if it fails and an empty parse result is created.
    :return: a parser which will produce an empty parse result if the parser returns no result.
             The empty parse result contains no parsed object, a response of 0, and the remaining full input to parser.
    """

    def parse(input: List[Word]) -> ParseResult:
        result = parser.parse(input)
        if not isinstance(result, SuccessParse):
            return SuccessParse(parsed=None, response=response, remaining=input)
        return result

    return Parser(parse)


def threshold_success(parser: Parser, response_threshold: Response) -> Parser:
    """
    :return: a parser which returns the result of `parser` if the response successful and is above the threshold,
             otherwise returns None.
    """
    def check_threshold(parsed: Any, response: Response) -> Parser:
        if response <= response_threshold:
            return failure()

        return produce(parsed, response)

    return parser.then(check_threshold)


def none(parser: Parser, response: Response = 1.0, max_parser_response: Response = 0.0) -> Parser:
    """
    :param response: the response of the returned parser if the supplied parser succeeds.
    :param max_parser_response: the response of the supplied parser, above which this parser will fail.
    :return: a parser which fails if the supplied parser parses. Otherwise returns the empty response.
    """
    def parse(input: List[Word]) -> ParseResult:
        result = parser.parse(input)
        if isinstance(result, SuccessParse):
            if result.response > max_parser_response:
                return FailureParse()
            else:
                return result

        return SuccessParse(parsed=None, response=response, remaining=input)

    return Parser(parse)


def ignore_words(words: List[Word]) -> Parser:
    """
    :return: a parser which removes the given words from the input text. Gives None as the parsed object.
    """
    def parse(input: List[Word]) -> ParseResult:
        new_input = [word for word in input if word not in words]
        return SuccessParse(parsed=None, response=0.0, remaining=new_input)

    return Parser(parse)


def rest() -> Parser:
    """
    :return: a parser which parses the rest of input and gives it as output, provided there is input remaining.
             If there is no input, the parser fails.
    """
    def parse(input: List[Word]) -> ParseResult:
        if input == []:
            return FailureParse()
        return SuccessParse(parsed=input, response=1.0, remaining=[])

    return Parser(parse)


def partial_parser(parser: Parser, response: Response, marker: Any) -> Parser:
    """
    :param parser: the parser to try parsing with.
    :param response: the response of the partial parse if the parser fails.
    :param marker: used to tell where parsing failed.
    :return: a parser which if it fails, creates a partial response containing parser.
             This can be used in implementing asking the player for more information about an action.
    """
    def parse(input: List[Word]) -> ParseResult:
        parsed = parser.parse(input)

        if parsed.is_failure():
            return PartialParse(parser, response, marker)

        return parsed

    return Parser(parse)


def words_and_corrections(words: List[Word], corrections: List[Word], make_word_parsers: [Callable[[Word], Parser]] = None, debug = False, consume=Consume.WORD_ONLY) -> Parser:
    """
    :param words: the words the parser should recognise.
    :param corrections: the words the speech-to-text service mistakes for words in the list of words.
    :param make_word_parsers: the functions used to create a parser from a word. For each word a parser will be
                              created using each parser in the list.
    :return: a parser that is useful of if a speech-to-text service frequently mishears words. Parses the words and
             corrections.
    """
    words_parser = strongest_word(words, make_word_parsers=make_word_parsers)
    match = partial(word_match, consume=consume)
    corrections_parser = strongest_word(corrections, make_word_parsers=[match])
    return strongest([words_parser, corrections_parser], debug=debug)


def object_spelled(names: List[str], other_noun_response: Response, word_spelling_threshold=0.5) -> Parser:
    """
    :param names: the names of objects in the game. These give a response of 1.0.
    :param other_noun_response: the response for other nouns.
    :return: a parser which strongly recognises spelling of the given names, and can also recognise other nouns.
    """
    # Objects the player can actually pick up.
    spelling = partial(word_spelling, consume=Consume.WORD_ONLY, dist_threshold=word_spelling_threshold)
    objects = strongest_word(names, make_word_parsers=[partial(word_match, consume=Consume.WORD_ONLY), spelling])
    # Objects which are recognised, but the user cannot pickup. These have a lower response.
    nouns = ['NN', 'NNS']
    other_objects = word_tagged(nouns).map_response(lambda _: other_noun_response)

    return strongest([objects, other_objects])


def partial_or_maybe(initial_parser: Parser, combine: Callable[[Any, Response], Parser], partial_marker: Any):
    """
    :param initial_parser: the parser which can either be used to generate a partial response if combining fails,
                           or can not be present if combine succeeds.
    :param combine:        combines the optional result of the initial parser.
    :param partial_marker: the marker for the partial parse if combining fails.
    :return:               a parser which produces a partial parse if the combine fails, or can optionally not parse
                           the initial parser and just parse using the combine operation.
    """
    # If the combine fails, produce a partial parse.
    make_partial = lambda parser, response: partial_parser(parser, response, marker=partial_marker)
    partial_initial_parser = initial_parser.then(wrap(combine, make_partial))

    # Optionally parse the initial parser.
    maybe_initial_parser = maybe(initial_parser).then(combine)

    return strongest([maybe_initial_parser, partial_initial_parser])
