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
        assert absolute().parse(s).parsed.place_name == 'room 201'

    def test_parses_if_missing_room(self):
        s = 'go to 201'.split()
        assert absolute().parse(s).parsed.place_name == 'room 201'

    def test_fails_if_missing_number(self):
        s = 'go to room'.split()
        assert absolute().parse(s) is None