from parsing.parse_result import *
from parsing.parser import Parser, Word, word_match
from typing import  List


def partial(parser: Parser) -> Parser:
    def parse(input: List[Word]) -> ParseResult:
        parsed = parser.parse(input)

        if parsed.is_failure():
            return PartialParse(parser, 1.0)

        return parsed

    return Parser(parse)


if __name__ == '__main__':
    def combine(parsed: Any, response: Response) -> Parser:
        # Captures the currently parsed object inside the partial.
        return partial(word_match('world').map_parsed(lambda p: parsed + [p]))

    p = word_match('hello').map_parsed(lambda p: [p]).then(combine)

    s = 'hello'.split()
    result = p.parse(s)

    if isinstance(result, PartialParse):
        # Get some more input.
        s = 'world'.split()
        result2 = result.failed_parser.parse(s)

        print('Partial:', result2.parsed)

    elif isinstance(result, SuccessParse):
        print('Success:', result)

