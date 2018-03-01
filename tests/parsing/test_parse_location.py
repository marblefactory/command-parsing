import unittest
from parsing.parse_location import location, ordinal_number, move_direction, object_relative_direction, Parser
from actions.location import *


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
    def test_parses_storage(self):
        s = 'go to storage room 5'.split()
        assert location().parse(s).parsed == Absolute('storage room 5')

    def test_parses_storage_no_room(self):
        s = 'go to storage 5'.split()
        assert location().parse(s).parsed == Absolute('storage room 5')

    def test_parses_storage_same_response(self):
        s1 = 'go to storage 5'.split()
        s2 = 'go to storage room 5'.split()

        r1 = location().parse(s1).response
        r2 = location().parse(s2).response

        assert r1 == r2

    def test_parses_office(self):
        s = 'go to office 10'.split()
        assert location().parse(s).parsed == Absolute('office 10')

    def test_parses_computer_lab(self):
        s = 'go to computer lab 6'.split()
        assert location().parse(s).parsed == Absolute('computer lab 6')

    def test_parses_lab(self):
        s = 'go to lab 3'.split()
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_live_as_lab(self):
        s = 'go to live 3'.split()
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_love_as_lab(self):
        s = 'go to love 3'.split()
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_meeting_room(self):
        s = 'go to meeting room 89'.split()
        assert location().parse(s).parsed == Absolute('meeting room 89')

    def test_parses_workshop(self):
        s = 'go to workshop 2'.split()
        assert location().parse(s).parsed == Absolute('workshop 2')

    def test_parses_server_room(self):
        s = 'go to server room 78'.split()
        assert location().parse(s).parsed == Absolute('server room 78')

    def test_parses_reception(self):
        s = 'go to reception'.split()
        assert location().parse(s).parsed == Absolute('reception')

    def test_parses_kitchen(self):
        s = 'go to the kitchen'.split()
        assert location().parse(s).parsed == Absolute('kitchen')

    def test_parses_gun_range(self):
        s = 'go to the gun range'.split()
        assert location().parse(s).parsed == Absolute('range')

    def test_parses_gun_range_same_response(self):
        s1 = 'go to the range'.split()
        s2 = 'go to the gun range'.split()

        r1 = location().parse(s1).response
        r2 = location().parse(s2).response

        assert r1 == r2

    def test_parses_mortuary(self):
        s = 'go to the mortuary'.split()
        assert location().parse(s).parsed == Absolute('mortuary')

    def test_parses_security_office(self):
        s = 'go to the security office'.split()
        assert location().parse(s).parsed == Absolute('security office')


class PositionalTestCase(unittest.TestCase):
    def test_parses(self):
        s = 'on your left take the second door'.split()
        assert location().parse(s).parsed == Positional('door', 1, MoveDirection.LEFT)

    def test_direction_default_forwards(self):
        s = 'go to the third server'.split()
        assert location().parse(s).parsed == Positional('server', 2, MoveDirection.FORWARDS)

    def test_ordinal_num_defaults_next(self):
        s = 'go to the server on your right'.split()
        assert location().parse(s).parsed == Positional('server', 0, MoveDirection.RIGHT)

    def test_parses_with_all_missing(self):
        s = 'go to the door'.split()
        assert location().parse(s).parsed == Positional('door', 0, MoveDirection.FORWARDS)

    def test_fails_if_missing_object(self):
        s = 'go to the next on your right'.split()
        assert type(location().parse(s)) is not Positional


class DirectionalTestCase(unittest.TestCase):
    def test_parses_left(self):
        s = 'go left'.split()
        assert location().parse(s).parsed == Directional(MoveDirection.LEFT)

    def test_parses_right(self):
        s = 'go right'.split()
        assert location().parse(s).parsed == Directional(MoveDirection.RIGHT)

    def test_parses_forwards(self):
        s = 'go forwards'.split()
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS)

    def test_parses_backwards(self):
        s = 'go backwards'.split()
        assert location().parse(s).parsed == Directional(MoveDirection.BACKWARDS)


class StairsTestCase(unittest.TestCase):
    def test_parses_up(self):
        s = 'go up the stairs'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_upstairs(self):
        s = 'go upstairs'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_down(self):
        s = 'go down the stairs'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_downstairs(self):
        s = 'go downstairs'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_just_up(self):
        s = 'go up'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_just_down(self):
        s = 'go down'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_up_floor(self):
        s = 'go up a floor'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_down_floor(self):
        s = 'go down a floor'.split()
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)


class BehindTestCase(unittest.TestCase):
    def test_behind(self):
        s = 'go behind the desk'.split()
        assert location().parse(s).parsed == Behind('desk')

    def test_around(self):
        s = 'go around the server'.split()
        assert location().parse(s).parsed == Behind('server')

    def test_fails_if_missing_object(self):
        s = 'go around the'.split()
        assert location().parse(s) is None

    def test_other_side(self):
        s = 'go to the other side of the table'.split()
        assert location().parse(s).parsed == Behind('table')

    def test_fails_if_side_other_incorrect_order(self):
        s = 'go to the side other of the table'.split()
        assert type(location().parse(s)) is not Behind


class EndOfTestCase(unittest.TestCase):
    def test_parse_room(self):
        s = 'go to the end of the room'.split()
        assert location().parse(s).parsed == EndOf('room')

    def test_parse_corridor(self):
        s = 'go to the end of the corridor'.split()
        assert location().parse(s).parsed == EndOf('corridor')

    def test_parse_absolute(self):
        s = 'go to the end of the gun range'.split()
        assert location().parse(s).parsed == EndOf('range')