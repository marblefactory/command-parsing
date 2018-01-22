from typing import List, Optional, Callable, Any, Tuple
from collections import namedtuple
import nltk


# Stores the object created from parsing, the response (how 'strongly' the parser matched), and the remaining tokens,
ParseResult = namedtuple('ParseResult', 'parsed response remaining')

# A word in the user's text.
Word = str

# A value from 0-1 indicating how strongly a parser 'matches' on some text. E.g. a parser for the semantic similarity
# to the word 'hello' would give a higher response for 'hi' than 'car'.
Response = float


class Parser:
    def __init__(self, parse: Callable[[List[Word]], ParseResult]):
        """
        :param parse: the function that takes a list of words and produces a parse result.
        """
        self.parse = parse


    def then(self, f: Callable[[Any, Response], 'Parser']) -> 'Parser':
        """
        :param f: used to construct a new parser from the parse result of this parser.
        :return: applies this parser, then uses the result of parsing and the response to return another parser over
                 the remaining tokens.
        """
        def new_parse(input: List[Word]) -> Optional[ParseResult]:
            parsed = self.parse(input)

            if parsed is None:
                return None

            result, response, remaining = parsed

            new_parser = f(result, response)
            return new_parser.parse(remaining)

        return Parser(new_parse)

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


def produce(parsed: Any, response: Response) -> Parser:
    """
    :return: a parser that matches on all input, returns the supplied parsed object and response from parsing, and
             consumes no input.
    """
    def parse(input: List[Word]) -> Optional[ParseResult]:
        return ParseResult(parsed, response, input)

    return Parser(parse)


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


s = 'hello world'.split()
print(word_match('hello').parse(s))

s = 'car'.split()
print(word_tagged(['NN']).parse(s))

s = '102'.split()
print(number().parse(s))

# p1 = WordMatch('hello')
# p2 = WordMatch('world')
# p3 = Produce('OUTPUT', 1.0)
#
# thresholded = Thresholded([p1, p2], p3, 0.5)
#
# print(thresholded.parse(['f']))

# strongest = StrongestOf([p1, p2])
#
# print(strongest.parse(['hello']))

# p1 = WordMatch('hello')
#
# def f(parsed: str, response: Response) -> Parser:
#     return WordMatch('world').map(lambda p, r: (parsed + p, 0))
#
# s = 'hello world'.split()
#
# print(p1.then(f).parse(s))

# def f(parsed: str, response: Response) -> Parser:
#     return Number() #.map(lambda num_str, r: (int(num_str), r))
#
# room_parser = WordMatch('room').then(f)
#
# s = '102'.split()
#
# print(room_parser.parse(s))
# print(Number().parse(s))