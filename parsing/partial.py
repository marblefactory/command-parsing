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

# word_match('hello').then(partial(word_match('world'), 'where?'))

if __name__ == '__main__':
    p = partial(word_match('hello'))

    s1 = 'hello'.split()
    s2 = 'world'.split()

    success = lambda x: x.parsed
    partial = lambda x: x.failed_parser.parse('hello'.split())

    r1 = p.parse(s1)
    r2 = p.parse(s2).either(success, partial)

    print('r1:', r1)
    print('r2:', r2)
