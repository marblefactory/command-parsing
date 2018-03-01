from parsing.parser import *
from parsing.parser import Parser, Word, word_match
from typing import List


def partial(parser: Parser, response: Response) -> Parser:
    def parse(input: List[Word]) -> ParseResult:
        parsed = parser.parse(input)

        if parsed.is_failure():
            return PartialParse(parser, response)

        return parsed

    return Parser(parse)


if __name__ == '__main__':
    def combine(parsed: Any, response: Response) -> Parser:
        # Captures the currently parsed object inside the partial.
        p = strongest_word(['uk', 'world'])
        return partial(p.map_parsed(lambda p: parsed + [p]), response)

    parser = word_spelling('hello').map_parsed(lambda p: [p]).then(combine)

    s = 'hillo'.split()
    result = parser.parse(s)

    if isinstance(result, PartialParse):

        # Get some more input.
        s = 'uk'.split()
        result2 = result.failed_parser.parse(s)

        print('Response1:', result.response)
        print('Partial:', result2.parsed)
        print('Response2:', result2.response)

    elif isinstance(result, SuccessParse):
        print('Success:', result.parsed)
        print('Response:', result.response)

