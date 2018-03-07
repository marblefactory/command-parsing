import unittest
from parsing.pre_processing import pre_process
from parsing.parse_location import location, ordinal_number, move_direction, object_relative_direction, Parser, distance
from actions.location import *


class DistanceTestCase(unittest.TestCase):
    def test_short(self):
        s = pre_process('little')
        assert distance().parse(s).parsed == Distance.SHORT

    def test_medium(self):
        s = pre_process('fair')
        assert distance().parse(s).parsed == Distance.MEDIUM

    def test_far(self):
        s = pre_process('long')
        assert distance().parse(s).parsed == Distance.FAR


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
        s = pre_process('go to storage room 5')
        assert location().parse(s).parsed == Absolute('storage room 5')

    def test_parses_storage_no_room(self):
        s = pre_process('go to storage 5')
        assert location().parse(s).parsed == Absolute('storage room 5')

    def test_parses_storage_same_response(self):
        s1 = pre_process('go to storage 5')
        s2 = pre_process('go to storage room 5')

        r1 = location().parse(s1).response
        r2 = location().parse(s2).response

        assert r1 == r2

    def test_parses_office(self):
        s = pre_process('go to office 10')
        assert location().parse(s).parsed == Absolute('office 10')

    def test_parses_computer_lab(self):
        s = pre_process('go to computer lab 6')
        assert location().parse(s).parsed == Absolute('computer lab 6')

    def test_parses_lab(self):
        s = pre_process('go to lab 3')
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_live_as_lab(self):
        s = pre_process('go to live 3')
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_love_as_lab(self):
        s = pre_process('go to love 3')
        assert location().parse(s).parsed == Absolute('lab 3')

    def test_parses_meeting_room(self):
        s = pre_process('go to meeting room 89')
        assert location().parse(s).parsed == Absolute('meeting room 89')

    def test_parses_workshop(self):
        s = pre_process('go to workshop 2')
        assert location().parse(s).parsed == Absolute('workshop 2')

    def test_parses_server_room(self):
        s = pre_process('go to server room 78')
        assert location().parse(s).parsed == Absolute('server room 78')

    def test_parses_reception(self):
        s = pre_process('go to reception')
        assert location().parse(s).parsed == Absolute('reception')

    def test_parses_kitchen(self):
        s = pre_process('go to the kitchen')
        assert location().parse(s).parsed == Absolute('kitchen')

    def test_parses_gun_range(self):
        s = pre_process('go to the gun range')
        assert location().parse(s).parsed == Absolute('range')

    def test_parses_gun_range_same_response(self):
        s1 = pre_process('go to the range')
        s2 = pre_process('go to the gun range')

        r1 = location().parse(s1).response
        r2 = location().parse(s2).response

        assert r1 == r2

    def test_parses_mortuary(self):
        s = pre_process('go to the mortuary')
        assert location().parse(s).parsed == Absolute('mortuary')

    def test_parses_security_office(self):
        s = pre_process('go to the security office')
        assert location().parse(s).parsed == Absolute('security office')


class PositionalTestCase(unittest.TestCase):
    def test_parses(self):
        s = pre_process('on your left take the second door')
        assert location().parse(s).parsed == Positional('door', 1, MoveDirection.LEFT)

    def test_direction_default_forwards(self):
        s = pre_process('go to the third server')
        assert location().parse(s).parsed == Positional('server', 2, MoveDirection.FORWARDS)

    def test_ordinal_num_defaults_next(self):
        s = pre_process('go to the server on your right')
        assert location().parse(s).parsed == Positional('server', 0, MoveDirection.RIGHT)

    def test_parses_with_all_missing(self):
        s = pre_process('go to the door')
        assert location().parse(s).parsed == Positional('door', 0, MoveDirection.FORWARDS)

    def test_fails_if_missing_object(self):
        s = pre_process('go to the next on your right')
        assert type(location().parse(s)) is not Positional


class DirectionalTestCase(unittest.TestCase):
    def test_parses_left(self):
        s = pre_process('go left')
        assert location().parse(s).parsed == Directional(MoveDirection.LEFT, Distance.MEDIUM)

    def test_parses_right(self):
        s = pre_process('go right')
        assert location().parse(s).parsed == Directional(MoveDirection.RIGHT, Distance.MEDIUM)

    def test_parses_forwards(self):
        s = pre_process('go forwards')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_backwards(self):
        s = pre_process('go backwards')
        assert location().parse(s).parsed == Directional(MoveDirection.BACKWARDS, Distance.MEDIUM)

    def test_parses_short(self):
        s = pre_process('go backwards a little bit')
        assert location().parse(s).parsed == Directional(MoveDirection.BACKWARDS, Distance.SHORT)

    def test_parses_medium(self):
        s = pre_process('go forwards a fair distance')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.MEDIUM)

    def test_parses_far(self):
        s = pre_process('go forwards a long way')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.FAR)

    def test_swapped_direction_and_distance(self):
        s = pre_process('go a long way forwards')
        assert location().parse(s).parsed == Directional(MoveDirection.FORWARDS, Distance.FAR)


class StairsTestCase(unittest.TestCase):
    def test_parses_up(self):
        s = pre_process('go up the stairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_upstairs(self):
        s = pre_process('go upstairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_down(self):
        s = pre_process('go down the stairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_downstairs(self):
        s = pre_process('go downstairs')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_just_up(self):
        s = pre_process('go up')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_just_down(self):
        s = pre_process('go down')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)

    def test_parses_up_floor(self):
        s = pre_process('go up a floor')
        assert location().parse(s).parsed == Stairs(FloorDirection.UP)

    def test_parses_down_floor(self):
        s = pre_process('go down a floor')
        assert location().parse(s).parsed == Stairs(FloorDirection.DOWN)


class BehindTestCase(unittest.TestCase):
    def test_behind(self):
        s = pre_process('go behind the desk')
        assert location().parse(s).parsed == Behind('desk')

    def test_around(self):
        s = pre_process('go around the server')
        assert location().parse(s).parsed == Behind('server')

    def test_fails_if_missing_object(self):
        s = pre_process('go around the')
        assert location().parse(s).is_failure()

    def test_other_side(self):
        s = pre_process('go to the other side of the table')
        assert location().parse(s).parsed == Behind('table')

    def test_fails_if_side_other_incorrect_order(self):
        s = pre_process('go to the side other of the table')
        assert type(location().parse(s).parsed) is not Behind


class EndOfTestCase(unittest.TestCase):
    def test_parse_room(self):
        s = pre_process('go to the end of the room')
        assert location().parse(s).parsed == EndOf('room')

    def test_parse_corridor(self):
        s = pre_process('go to the end of the corridor')
        assert location().parse(s).parsed == EndOf('corridor')

    def test_parse_absolute(self):
        s = pre_process('go to the end of the gun range')
        assert location().parse(s).parsed == EndOf('range')
