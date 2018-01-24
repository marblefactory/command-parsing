from typing import List, Optional, Callable, Any, Tuple
from collections import namedtuple
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset
from utils import split_list


# Stores the object created from parsing, the response (how 'strongly' the parser matched), and the remaining tokens,
ParseResult = namedtuple('ParseResult', 'parsed response remaining')

# A word in the user's text.
Word = str

# A value from 0-1 indicating how strongly a parser 'matches' on some text. E.g. a parser for the semantic similarity
# to the word 'hello' would give a higher response for 'hi' than 'car'.
Response = float


def mean(r1: Response, r2: Response) -> Response:
    """
    :return: the mean response of r1 and r2.
    """
    return (r1 + r2) / 2.0


def semantic_similarity(w1: Word, w2: Word, similarity_measure: Callable[[Synset, Synset], Response]) -> Response:
    """
    :param similarity_measure: a word net function which give the semantic distance between two synsets.
    :return: the semantic similarity between the words using a `similarity` distance function defined by WordNet.
    """
    w1_synsets: List[Synset] = wn.synsets(w1)
    w2_synsets: List[Synset] = wn.synsets(w2)

    # Each synset contains different meanings of the word, e.g. fly is a noun and verb.
    # We'll find the maximum semantic similarity between any pairing of words from both synsets.
    maximum: Response = 0

    for s1 in w1_synsets:
        for s2 in w2_synsets:
            similarity_value = similarity_measure(s1, s2) or 0
            maximum = similarity_value if similarity_value > maximum else maximum

    return maximum


class Parser:
    def __init__(self, parse: Callable[[List[Word]], Optional[ParseResult]]):
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

        def new_parse(input: List[Word]) -> Optional[ParseResult]:
            parsed = self.parse(input)

            if not parsed:
                return None

            result, response, remaining = parsed

            new_parser = operation(result, response)
            return new_parser.parse(remaining)

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
            combine_responses = lambda r1, r2: r1

        def op(ignored_parsed: Any, r1: Response) -> Parser:
            return next_parser.map(lambda parsed, r2: (parsed, combine_responses(r1, r2)))

        return self.then(op)


    def map(self, transformation: Callable[[Any, Response], Tuple[Any, Response]]) -> 'Parser':
        """
        :return: takes the parse result 'wrapped' in the parser and applies the transformation to create a new parser.
        """

        def transform(parsed: Any, response: Response) -> Parser:
            def new_parse(words: List[Word]) -> Optional[ParseResult]:
                new_parsed, new_response = transformation(parsed, response)
                return ParseResult(new_parsed, new_response, words)

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


def produce(parsed: Any, response: Response) -> Parser:
    """
    :return: a parser that matches on all input, returns the supplied parsed object and response from parsing, and
             consumes no input.
    """
    def parse(input: List[Word]) -> Optional[ParseResult]:
        return ParseResult(parsed, response, input)

    return Parser(parse)


def failure() -> Parser:
    """
    :return: a parser which fails (i.e. gives a None result) to all input.
    """
    return Parser(lambda input: None)


def predicate(condition: Callable[[Word], Response], threshold: Response = 1.0) -> Parser:
    """
    :return: a parser which matches on the first word to give a value of condition higher than the threshold.
    """
    def parse(input: List[Word]) -> Optional[ParseResult]:
        for i, word in enumerate(input):
            response = condition(word)
            if response >= threshold:
                return ParseResult(word, response, input[i + 1:])

        return None

    return Parser(parse)


def word_match(word: Word) -> Parser:
    """
    :return: a parser which matches on the first occurrence of the supplied word.
    """

    def condition(input_word: Word) -> Response:
        return float(input_word == word)

    return predicate(condition)


def word_meaning(word: Word,
                 semantic_similarity_threshold: Response = 0.5,
                 similarity_measure: Callable[[Synset, Synset], Response] = Synset.path_similarity) -> Parser:
    """
    :param word: the word to find similar words to.
    :param semantic_similarity_threshold: the minimum semantic distance for an input word to be from the supplied word.
    :param similarity_measure: used to compare the semantic similarity of two words.
    :return: a parser which matches on words which have a similar meaning to the supplied word.
    """

    def condition(input_word: Word) -> Response:
        return semantic_similarity(input_word, word, similarity_measure)

    return predicate(condition, semantic_similarity_threshold)


def word_tagged(tags: List[str]) -> Parser:
    """
    :return: a parser which matches on words with the given tags.
    """

    def condition(input_word: Word) -> Response:
        word, tag = nltk.pos_tag([input_word])[0]
        return float(tag in tags)

    return predicate(condition)


def number() -> Parser:
    """
    :return: a parser which matches on cardinal numbers, e.g. 102. The parse result is a string of the number.
    """
    return word_tagged(['CD'])


def strongest(parsers: List[Parser]) -> Parser:
    """
    :return: the parser that gives the strongest response on the input text. If multiple parsers have the same maximum,
             then the parser to occur first in the list is returned.
    """
    def parse(input: List[Word]) -> Optional[ParseResult]:
        results = [parser.parse(input) for parser in parsers]
        filtered = [r for r in results if r is not None]

        if filtered == []:
            return None

        return max(filtered, key=lambda parse_result: parse_result.response)

    return Parser(parse)


def strongest_word(words: List[Word], make_parser: Callable[[Word], Parser] = word_match) -> Parser:
    """
    :param words: the list of words to compare to the input.
    :param make_parser: the function used to create a parser from a word.
    :return: created parser which matches most strongly on the input.
    """
    parsers = [make_parser(word) for word in words]
    return strongest(parsers)


def anywhere(parser: Parser) -> Parser:
    """
    :return: a parser which consumes none of the input, therefore any chained parsers can match anywhere in the text.
    """

    def parse(input: List[Word]) -> Optional[ParseResult]:
        result = parser.parse(input)
        if not result:
            return None

        return ParseResult(result.parsed, result.response, input)

    return Parser(parse)


def maybe(parser: Parser) -> Parser:
    """
    :return: a parser which will produce an empty parse result if the parser returns no result.
             The empty parse result contains no parsed object, a response of 0, and the remaining full input to parser.
    """

    def parse(input: List[Word]) -> Optional[ParseResult]:
        result = parser.parse(input)
        if not result:
            return ParseResult(parsed=None, response=0.0, remaining=input)

        return result

    return Parser(parse)


def inverse(parser: Parser) -> Parser:
    """
    :return: a parser with a response which is the inverse of the supplied parser, i.e. 1 - response.
    """
    return parser.map_response(lambda r: 1 - r)

