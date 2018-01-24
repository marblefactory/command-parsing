import unittest
from parsing.parse_location import *


class OrdinalNumberTestCase(unittest.TestCase):
    def test_parses_next(self):
        """
        Tests 'next' is considered as an ordinal number.
        """
        assert ordinal_number().parse(['next']).parsed == 0

    def test_parses_ordinal_numbers(self):
        """
        Tests 'first', 'second', 'third', etc are parsed to their respective integers.
        """
        words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']

        for num, word in enumerate(words):
            assert ordinal_number().parse([word]).parsed == num


class MoveDirectionTestCase(unittest.TestCase):
    def parser(self) -> Parser:
        return move_direction()

    def test_parses_forwards(self):
        assert self.parser().parse(['forwards']).parsed == MoveDirection.FORWARDS

    def test_parses_front(self):
        assert self.parser().parse(['front']).parsed == MoveDirection.FORWARDS

    def test_parses_backwards(self):
        assert self.parser().parse(['backwards']).parsed == MoveDirection.BACKWARDS

    def test_parses_behind(self):
        assert self.parser().parse(['behind']).parsed == MoveDirection.BACKWARDS

    def test_parses_left(self):
        assert self.parser().parse(['left']).parsed == MoveDirection.LEFT

    def test_parses_right(self):
        assert self.parser().parse(['right']).parsed == MoveDirection.RIGHT


class ObjectRelativeDirectionTestCase(MoveDirectionTestCase):
    def parser(self) -> Parser:
        return object_relative_direction()

    def test_parse_defaults_to_vicinity(self):
        assert self.parser().parse(['nan']).parsed == ObjectRelativeDirection.VICINITY


class AbsoluteTestCase(unittest.TestCase):
    def test_parses_room_and_number(self):
        s = 'go to room 201'.split()
        assert absolute().parse(s).parsed == Absolute('room 201')

    def test_parses_if_missing_room(self):
        s = 'go to 201'.split()
        assert absolute().parse(s).parsed == Absolute('room 201')

    def test_fails_if_missing_number(self):
        s = 'go to room'.split()
        assert absolute().parse(s) is None

    def test_lower_response_if_missing_room(self):
        s1 = 'go to room 201'.split()
        s2 = 'go to 201'.split()

        r1 = absolute().parse(s1).response
        r2 = absolute().parse(s2).response

        assert r1 > r2


class PositionalTestCase(unittest.TestCase):
    def test_parses(self):
        s = 'on your left take the second door'.split()
        assert positional().parse(s).parsed == Positional('door', 1, MoveDirection.LEFT)

    def test_direction_default_forwards(self):
        s = 'go to the third server'.split()
        assert positional().parse(s).parsed == Positional('server', 2, MoveDirection.FORWARDS)

    def test_ordinal_num_defaults_next(self):
        s = 'go to the server on your right'.split()
        assert positional().parse(s).parsed == Positional('server', 0, MoveDirection.RIGHT)

    def test_parses_with_all_missing(self):
        s = 'go to the door'.split()
        assert positional().parse(s).parsed == Positional('door', 0, MoveDirection.FORWARDS)

    def test_fails_if_missing_object(self):
        s = 'go to the next on your right'.split()
        assert positional().parse(s) is None

    def test_missing_direction_does_not_reduce_repsonse(self):
        s1 = 'take the second door in front of you'.split()
        s2 = 'take the second door'.split()

        r1 = positional().parse(s1).response
        r2 = positional().parse(s2).response

        assert r1 == r2

    def test_missing_ordinal_num_does_not_reduce_response(self):
        s1 = 'take the second door in front of you'.split()
        s2 = 'take the door in front of you'.split()

        r1 = positional().parse(s1).response
        r2 = positional().parse(s2).response

        assert r1 == r2