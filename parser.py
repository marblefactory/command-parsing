from typing import List, Optional, Callable, Any, Tuple
from collections import namedtuple
import nltk


# Stores the object created from parsing, the response (how 'strongly' the parser matched), and the remaining tokens,
ParseResult = namedtuple('ParseResult', 'result response remaining')

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

    def map(self, transform: Callable[[Any, Response], Tuple[Any, Response]]) -> 'Parser':
        """
        :return: takes the parse result 'wrapped' in the parser and applies the transformation to create a new parser.
        """
        def new_parse(input: List[Word]) -> Optional[ParseResult]:
            parsed = self.parse(input)

            if parsed is None:
                return None

            result, response, remaining = parsed
            new_result, new_response = transform(result, response)
            return ParseResult(new_result, new_response, remaining)

        return Parser(new_parse)


class Predicate(Parser):
    """
    Parses on words when a predicate is above or equal to a threshold.
    """

    def __init__(self, predicate: Callable[[Word], float], threshold: float):
        """
        :param predicate: the function that must give an output above the threshold for a parse to occur.
        :param threshold: the minimum response of the predicate.
        """
        def parse(input: List[Word]) -> Optional[ParseResult]:
            """
            Searches through the input until the predicate is true.
            :return: the parsed word and remaining tokens if the predicate is true. Or, None if the predicate is false.
            """
            for i, word in enumerate(input):
                response = predicate(word)
                if response >= threshold:
                    return ParseResult(word, response, input[i + 1:])

            return None

        super(Predicate, self).__init__(parse)


class WordMatch(Predicate):
    """
    Parses on words when a given word in the text matches.
    """

    def __init__(self, word: Word):
        """
        :param word: the word to match in the input.
        """
        def predicate(input_word: Word) -> float:
            return float(input_word == word)

        super(WordMatch, self).__init__(predicate, 1.0)


class WordTagged(Predicate):
    """
    Parses on words when a word has a NLTK tag from the given list.
    """

    def __init__(self, tags: List[str]):
        """
        :param tags: the tags to look for in the input.
        """
        def predicate(input_word: Word) -> float:
            tag = nltk.pos_tag([input_word])[0]
            return float(tag in tags)

        super(WordTagged, self).__init__(predicate, 1.0)


class Number(WordTagged):
    """
    Parses on cardinal numbers, e.g. 102.
    """

    def __init__(self):
        """
        :param input: the words to parse over.
        """
        super(Number, self).__init__(['CD'])


p1 = WordMatch('hello')

def f(parsed: str, response: Response) -> Parser:
    return WordMatch('world')

s = 'hello world'.split()

print(p1.then(f).parse(s))
